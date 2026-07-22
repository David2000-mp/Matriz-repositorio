"""
Vista de Captura Manual de Datos para CHAMPILEAKS.
Formulario para ingreso manual de métricas.
"""

import streamlit as st
import pandas as pd
from datetime import date
import logging
from components import ui
from utils.data_provider import data_provider
from utils.helpers import generate_social_url
from utils.data_manager import (
    save_comment,
    load_usernames_editados,
    save_username_editado,
    save_batch,
    invalidate_caches,
)
from utils.catalog import COLEGIOS_MARISTAS, PLATAFORMAS_REQUERIDAS
from utils.data_saver import get_id
from utils.analytics import calculate_likes_promedio, estimate_reach
from utils.validators import (
    validate_social_url,
    validate_followers,
    validate_engagement,
    validate_form,
    get_validation_icon,
    check_missing_data_per_institution,
    get_monthly_pending_institutions,
    normalize_report_date_to_month_start,
)
from utils.app_state import get_app_state
from components.toast_notifications import (
    toast_success,
    toast_info,
    toast_warning,
    toast_data_saved,
    toast_validation_error,
)


def check_registro_existente(entidad: str, plataforma: str, fecha: date) -> bool:
    """
    Verifica si ya existe un registro para [Institución + Plataforma + Período (mes)].
    
    Args:
        entidad: Nombre de la institución
        plataforma: Nombre de la plataforma social
        fecha: Fecha del registro (se busca por mes)
    
    Returns:
        bool: True si existe registro en ese período, False en caso contrario
    """
    try:
        # Obtener datos usando caché compartido; la vista invalida caché tras guardar
        df_metricas = data_provider.get_merged_data(force_reload=False)

        if df_metricas.empty:
            return False
        
        # Convertir fecha a timestamp para comparación
        fecha_ts = pd.to_datetime(fecha)
        periodo_busqueda = fecha_ts.to_period("M")  # Obtener periodo (mes)
        
        # Filtrar por institución y plataforma
        mask = (
            (df_metricas["entidad"] == entidad) & 
            (df_metricas["plataforma"] == plataforma)
        )
        
        if not mask.any():
            return False
        
        # Verificar si hay registro en el mismo mes
        df_filtrado = df_metricas[mask]
        df_filtrado["periodo"] = pd.to_datetime(df_filtrado["fecha"]).dt.to_period("M")
        
        existe_en_periodo = (df_filtrado["periodo"] == periodo_busqueda).any()
        return existe_en_periodo
        
    except Exception as e:
        logging.error(f"Error verificando registro existente: {e}")
        return False


def render(df=None):
    """
    Renderiza la vista de captura de datos priorizando Google Forms y verificación mensual.
    """
    # Configurar el sidebar
    st.sidebar.title("Opciones de Captura")
    opcion = st.sidebar.radio(
        "Selecciona una opción:", ["Formulario Externo", "Carga Masiva", "Captura Anual"]
    )

    st.title("📝 Captura de Datos")
    st.caption("Registro de Métricas por Cuenta")
    st.markdown("---")

    # Calcular datos faltantes
    try:
        df_full = data_provider.get_merged_data(force_reload=False)
        if not df_full.empty:
            pending_report = get_monthly_pending_institutions(df_full, min_platforms=2)
            summary = pending_report.get("summary", {})
            target_month = pending_report.get("target_month")
            pending_rows = pending_report.get("pending_rows", [])

            st.markdown("### Verificación de Captura Mensual")
            if target_month:
                st.caption(f"Mes objetivo de verificación: {target_month}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Instituciones activas", int(summary.get("total_activas", 0)))
            c2.metric("Instituciones completas", int(summary.get("completas", 0)))
            c3.metric("Instituciones pendientes", int(summary.get("pendientes", 0)))

            if pending_rows:
                st.markdown("### ⚠️ Pendientes del último mes capturado")

                pending_df = pd.DataFrame(pending_rows)
                pending_df = pending_df.sort_values(["plataformas_actuales", "institucion"], ascending=[True, True])
                st.dataframe(
                    pending_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "institucion": st.column_config.TextColumn("Institución"),
                        "plataformas_actuales": st.column_config.NumberColumn("Plataformas actuales"),
                        "estado": st.column_config.TextColumn("Estado"),
                    },
                )
            else:
                st.success("Cobertura completa: no hay instituciones pendientes en el último mes capturado.")

            st.markdown("### Formulario Externo de Captura")
            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdyENRU-OPiD9VTEMC_AQeCusksvK450UTQQFGcnKS9tQJINA/viewform"
            st.link_button("📝 Abrir Google Forms", form_url, width='stretch')
            st.components.v1.iframe(form_url, width=None, height=980, scrolling=True)

            # Mantener verificación histórica existente como diagnóstico secundario
            current_date = pd.Timestamp.now()
            date_range = (current_date.replace(day=1), current_date + pd.offsets.MonthEnd(1))
            missing_issues = check_missing_data_per_institution(df_full, date_range)
            if missing_issues:
                with st.expander("Diagnóstico detallado de campos faltantes", expanded=False):
                    issues_by_institution = {}
                    for issue in missing_issues:
                        inst = issue['institution']
                        if inst not in issues_by_institution:
                            issues_by_institution[inst] = []
                        issues_by_institution[inst].append(f"{issue['platform']}: {issue['issue_type']}")

                    for institution, issues in issues_by_institution.items():
                        st.markdown(f"**{institution}**")
                        for issue in issues:
                            st.warning(issue)
    except Exception as e:
        logging.warning(f"Error calculando datos faltantes: {e}")

    # Flujo Forms-only: no mostrar la captura manual individual.
    if opcion == "Formulario Externo":
        return

    # Obtener estado global
    state = get_app_state()
    
    # Persistencia: conservar institución y fecha seleccionadas entre envíos
    defaults = state.get_form_defaults()
    if not defaults.get("capture_entidad_default"):
        state.set_form_defaults({
            "capture_entidad_default": list(COLEGIOS_MARISTAS.keys())[0],
            "capture_fecha_default": date.today(),
            "capture_plataforma_default": PLATAFORMAS_REQUERIDAS[0],
        })

    if opcion == "Captura Manual":
        st.subheader("Registro Individual")
        toast_info("Selecciona la institución y plataforma, ingresa las métricas del período y guarda.", duration=2)

        # Contenedor de captura (usar formulario específico más abajo)
        with st.container():
            st.markdown("### Información de la Cuenta")

            col1, col2 = st.columns(2)

            with col1:
                instituciones = list(COLEGIOS_MARISTAS.keys())
                defaults = state.get_form_defaults()
                entidad_default = defaults.get("capture_entidad_default", instituciones[0])
                entidad_index = instituciones.index(entidad_default) if entidad_default in instituciones else 0
                entidad = st.selectbox(
                    "Institución Marista",
                    instituciones,
                    index=entidad_index,
                    key="selector_institucion",
                    help="Selecciona la institución educativa",
                )

            with col2:
                if entidad:
                    plataformas_disponibles = PLATAFORMAS_REQUERIDAS
                    plataforma_default = defaults.get("capture_plataforma_default", plataformas_disponibles[0])
                    plataforma_index = plataformas_disponibles.index(plataforma_default) if plataforma_default in plataformas_disponibles else 0
                    plataforma = st.selectbox(
                        "Plataforma Social",
                        plataformas_disponibles,
                        index=plataforma_index,
                        key="selector_plataforma",
                        help="Selecciona la red social",
                    )
                else:
                    plataforma = None

            # INDICADOR DINÁMICO: Mostrar si ya existe registro para este período
            if entidad and plataforma:
                defaults = state.get_form_defaults()
                fecha_temp = defaults.get("capture_fecha_default", date.today())
                existe_registro = check_registro_existente(entidad, plataforma, fecha_temp)
                
                if existe_registro:
                    st.success(
                        f"✅ **Dato registrado con éxito** para {entidad} - {plataforma} en {fecha_temp.strftime('%B %Y')}",
                        icon="✅"
                    )
                else:
                    st.info(
                        f"📝 Nuevo registro para {entidad} - {plataforma}",
                        icon="ℹ️"
                    )
            else:
                plataforma = None

            # DINÁMICO: Link se actualiza INMEDIATAMENTE con cada cambio de plataforma
            # Nota: usuario/URL se coloca en Opciones Avanzadas para simplificar la UI
            url_actual = ""
            if entidad and plataforma:
                url_actual = COLEGIOS_MARISTAS.get(entidad, {}).get(plataforma, "")

            usuario_red = ""  # valor por defecto; sobrescrito en el expander avanzado

            st.divider()
            # Agrupar toda la entrada manual en un formulario seguro
            with st.form("manual_entry_form", clear_on_submit=True):
                st.markdown("### Métricas del Período (Entrada Invertida)")
                st.caption("💡 Nueva lógica: Ingresa Seguidores + Engagement Rate → Likes se calcula automáticamente")

                # Identificadores: Fecha (principal), Entidad y Plataforma como contexto
                id_col1, id_col2, id_col3 = st.columns([2, 3, 3])
                with id_col1:
                    fecha_captura = st.date_input(
                        "📅 Fecha del Reporte",
                        value=date.today(),
                        key="input_fecha",
                        help="Fecha del período reportado (YYYY-MM-DD)",
                    )

                with id_col2:
                    st.markdown("**Institución**")
                    st.markdown(entidad if entidad else "— Selecciona institución —")

                with id_col3:
                    st.markdown("**Plataforma**")
                    st.markdown(plataforma if plataforma else "— Selecciona plataforma —")

                # ========================================================================
                # INPUTS PRINCIPALES (Obligatorios)
                # ========================================================================
                col1, col2 = st.columns(2)

                with col1:
                    seguidores = st.number_input(
                        "👥 Seguidores Totales *",
                        min_value=0,
                        value=0,
                        step=10,
                        key="input_seguidores",
                        help="Número total de seguidores al final del período",
                    )
                    # Validación reactiva de seguidores
                    seguidores_valid, seguidores_msg = validate_followers(seguidores)
                    if seguidores > 0 and not seguidores_valid:
                        st.error(f"{get_validation_icon(False)} {seguidores_msg}", icon="❌")
                    elif seguidores > 0:
                        st.caption(f"{get_validation_icon(True)} Seguidores válidos")

                with col2:
                    engagement_rate = st.number_input(
                        "📊 Engagement Rate (%) *",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0,
                        step=0.01,
                        format="%.2f",
                        key="input_engagement",
                        help="Porcentaje de engagement (interacciones / seguidores × 100)",
                    )
                    # Validación reactiva de engagement rate
                    engagement_valid, engagement_msg = validate_engagement(engagement_rate)
                    if engagement_rate > 0 and not engagement_valid:
                        st.error(f"{get_validation_icon(False)} {engagement_msg}", icon="❌")
                    elif engagement_rate > 0:
                        st.caption(f"{get_validation_icon(True)} Engagement válido")

                # ========================================================================
                # CÁLCULO EN TIEMPO REAL - Likes Promedio Inferido
                # ========================================================================
                st.divider()
                
                if seguidores > 0 and engagement_rate > 0:
                    likes_promedio_calculado = calculate_likes_promedio(engagement_rate, seguidores)
                    
                    # Mostrar en un box destacado
                    col_likes1, col_likes2 = st.columns([2, 1])
                    
                    with col_likes1:
                        st.success(
                            f"✅ **Likes Promedio Calculado:** {likes_promedio_calculado:.2f}",
                            icon="✔️"
                        )
                        st.caption(
                            f"Fórmula: Seguidores × (Engagement Rate / 100) = {seguidores} × ({engagement_rate}/100) = {likes_promedio_calculado:.2f}"
                        )
                    
                    with col_likes2:
                        st.metric(
                            "Likes",
                            f"{likes_promedio_calculado:.0f}",
                            delta=f"{engagement_rate:.1f}%",
                        )
                else:
                    st.caption("⚠️ Ingresa Seguidores y Engagement Rate para ver el cálculo")
                    likes_promedio_calculado = 0.0

                st.divider()

                # ========================================================================
                # Opciones Avanzadas: URL, Alcance, Interacciones, Comentarios
                # (La fecha ya se captura en el encabezado principal)
                # ========================================================================
                with st.expander("Opciones Avanzadas"):
                    col1, col2 = st.columns(2)
                    with col1:
                        manual_key = f"usuario_red_manual_{plataforma}" if plataforma else "usuario_red_manual"
                        usuario_red = st.text_input(
                            "Usuario o URL de la red",
                            value=(url_actual if url_actual else ""),
                            key=manual_key,
                            help="Ingresa la URL o el usuario si aún no está en el catálogo. Se reutilizará para el siguiente envío.",
                        )
                        # Validación reactiva de URL
                        if usuario_red and plataforma:
                            url_valid, url_msg = validate_social_url(usuario_red, plataforma)
                            if not url_valid:
                                st.error(f"{get_validation_icon(False)} {url_msg}", icon="❌")
                            else:
                                st.caption(f"{get_validation_icon(True)} URL válida para {plataforma}")

                    with col2:
                        defaults = state.get_form_defaults()
                        fecha_captura = st.date_input(
                            "📅 Fecha del Reporte",
                            value=defaults.get("capture_fecha_default", date.today()),
                            key="fecha_captura_selector",
                            help="Fecha del período reportado",
                        )

                    col3, col4 = st.columns(2)
                    with col3:
                        alcance = st.number_input(
                            "🌐 Alcance Total (Opcional)",
                            min_value=0,
                            value=0,
                            step=10,
                            key="input_alcance",
                            help="Número de personas únicas que vieron el contenido",
                        )

                    with col4:
                        interacciones = st.number_input(
                            "💬 Interacciones Totales (Opcional)",
                            min_value=0,
                            value=int(likes_promedio_calculado) if likes_promedio_calculado > 0 else 0,
                            step=1,
                            key="input_interacciones",
                            help="Suma de likes, comentarios, shares, etc.",
                        )

                comentarios = st.text_area(
                    "💭 Comentarios Contextuales",
                    help="Agrega cualquier información adicional relevante para este registro.",
                    key="capture_comments_input",
                )
                st.divider()

                submitted = st.form_submit_button("💾 Guardar Datos")

                if submitted:
                    # Validación completa del formulario
                    form_valid, form_errors = validate_form(
                        entidad=entidad,
                        plataforma=plataforma,
                        usuario_red=usuario_red,
                        seguidores=seguidores,
                        engagement_rate=engagement_rate,
                        interacciones=interacciones if interacciones > 0 else None,
                        me_gusta=None,
                    )

                    if not form_valid:
                        st.error("❌ Errores de validación:")
                        for error in form_errors:
                            st.error(f"   • {error}")
                        st.warning("No se guardó el registro. Completa todos los campos obligatorios.")
                        st.stop()
                    try:
                        # Preparar datos para guardar
                        cuentas_cache, metricas_cache = data_provider.get_data()

                        # Usar usuario_red (URL literal o vacío) para generar ID consistente
                        id_cuenta = get_id(
                            entidad,
                            plataforma,
                            usuario_red if usuario_red and usuario_red.strip() else "",
                            df_cuentas_cache=cuentas_cache,
                        )

                        # Validar campos obligatorios antes de guardar
                        required_fields = [entidad, plataforma, usuario_red, seguidores, engagement_rate, fecha_captura]
                        if not all(required_fields) or seguidores <= 0 or engagement_rate <= 0:
                            st.error("❌ No se guardó el registro. Todos los campos obligatorios deben estar completos y válidos.")
                            st.stop()

                        # Redondear engagement para guardado
                        engagement_rate_guardado = round(float(engagement_rate), 2)
                        likes_promedio_guardado = calculate_likes_promedio(engagement_rate_guardado, seguidores)
                        alcance_final = int(alcance) if ('alcance' in locals() and alcance > 0) else int(
                            estimate_reach(plataforma, seguidores, engagement_rate_guardado)
                        )
                        fecha_captura_normalizada = normalize_report_date_to_month_start(fecha_captura)
                        fecha_captura_guardado = fecha_captura_normalizada.strftime("%Y-%m-%d")

                        # Construir registro SOLO con campos indispensables
                        nuevo_registro = {
                            "id_cuenta": id_cuenta,
                            "entidad": entidad,
                            "plataforma": plataforma,
                            "usuario_red": usuario_red,
                            "fecha": fecha_captura_guardado,
                            "seguidores": int(seguidores),
                            "alcance": alcance_final,
                            "interacciones": int(interacciones) if interacciones > 0 else int(likes_promedio_guardado),
                            "likes_promedio": round(likes_promedio_guardado, 2),
                            "engagement_rate": engagement_rate_guardado,
                        }

                        # --- Validación de duplicado exacto (id_cuenta + fecha) ---
                        existe_duplicado = False
                        if metricas_cache is not None and not metricas_cache.empty:
                            metricas_cache["id_cuenta"] = metricas_cache["id_cuenta"].astype(str)
                            metricas_cache["fecha"] = pd.to_datetime(metricas_cache["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
                            existe_duplicado = (
                                (metricas_cache["id_cuenta"] == id_cuenta)
                                & (metricas_cache["fecha"] == nuevo_registro["fecha"])
                            ).any()

                        if existe_duplicado:
                            st.error(
                                f"❌ Ya existe un registro para esta cuenta ({entidad} - {plataforma} - {usuario_red}) en la fecha {nuevo_registro['fecha']}. "
                                "No se guardó el registro para evitar duplicados."
                            )
                            st.stop()

                        # --- DEFENSIVO: Bloquear si hay campos extra/no reconocidos ---
                        campos_permitidos = set([
                            "id_cuenta", "entidad", "plataforma", "usuario_red", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"
                        ])
                        if set(nuevo_registro.keys()) - campos_permitidos:
                            st.error("❌ El registro contiene campos no permitidos. Revisa la entrada.")
                            st.stop()

                        df_nuevo = pd.DataFrame([nuevo_registro])

                        with st.status("Guardando entrada..."):
                            success = save_batch(df_nuevo)

                            # Guardar comentarios contextuales si existen (no bloquear)
                            try:
                                if comentarios and comentarios.strip():
                                    mes_formato = fecha_captura_normalizada.strftime("%Y-%m")
                                    save_comment(entidad, mes_formato, comentarios.strip())
                            except Exception:
                                pass

                        # Feedback
                        if success:
                            toast_data_saved(f"{entidad} - {plataforma}")
                            toast_info(f"Alcance estimado: {alcance_final:,}", duration=2)
                            ui.render_status(
                                f"Datos guardados para {entidad} - {plataforma}",
                                tipo="success",
                            )
                            try:
                                st.balloons()
                            except Exception:
                                pass

                            # Invalida cachés centralmente
                            try:
                                invalidate_caches()
                            except Exception as e:
                                logging.warning(f"No se pudo invalidar cachés centralmente: {e}")

                            # Persistir valores para siguiente captura usando AppState
                            state.set_form_defaults({
                                "capture_entidad_default": entidad,
                                "capture_plataforma_default": plataforma,
                                "capture_fecha_default": fecha_captura_normalizada.date(),
                            })

                        else:
                            ui.render_status(
                                "Error al guardar el registro. Intenta nuevamente. Si el problema persiste, verifica tu conexión a Google Sheets.",
                                tipo="error",
                            )

                    except Exception as e:
                        ui.render_status(f"Error al guardar el registro: {e}", tipo="error")
                        logging.error(f"Error al guardar registro: {e}", exc_info=True)

        # ========================================================================
        # HERRAMIENTA AUXILIAR: CALCULADORA DE ENGAGEMENT (dentro de Captura Manual)
        # ========================================================================
        st.divider()
        with st.expander("🧮 Calculadora de Engagement - Herramienta Auxiliar", expanded=False):
            st.markdown("""
            Usa esta herramienta para calcular y analizar tu engagement en **Facebook** o **TikTok** 
            antes de registrarlo en el sistema. Ingresa tus últimas 15 publicaciones/videos y obtén 
            métricas detalladas con recomendaciones.
            """)
            
            # Crear dos columnas para las opciones
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                if st.button("📘 Calculadora Facebook", key="calc_fb_btn", width="stretch"):
                    st.session_state["calc_active_tab"] = "facebook"
                    st.rerun()
            
            with calc_col2:
                if st.button("🎵 Calculadora TikTok", key="calc_tk_btn", width="stretch"):
                    st.session_state["calc_active_tab"] = "tiktok"
                    st.rerun()
            
            # Mostrar calculadora seleccionada
            if st.session_state.get("calc_active_tab") == "facebook":
                st.markdown("---")
                from views import engagement_calculator
                engagement_calculator.render_facebook_tab()
            
            elif st.session_state.get("calc_active_tab") == "tiktok":
                st.markdown("---")
                from views import engagement_calculator
                engagement_calculator.render_tiktok_tab()

    elif opcion == "Carga Masiva":
        st.subheader("Carga Masiva de Datos")
        st.info("🚧 Esta funcionalidad está en desarrollo.")

    elif opcion == "Captura Anual":
        st.subheader("📅 Captura Anual de Datos")
        st.caption("Captura datos mensuales completos para una institución durante todo un año.")

        # Selector de institución y año
        col1, col2 = st.columns(2)
        with col1:
            entidad_anual = st.selectbox(
                "Institución Marista",
                list(COLEGIOS_MARISTAS.keys()),
                key="entidad_anual",
                help="Selecciona la institución para la captura anual",
            )

        with col2:
            año_captura = st.selectbox(
                "Año",
                list(range(2024, 2027)),
                index=1,  # 2025 por defecto
                key="año_anual",
                help="Selecciona el año para la captura",
            )

        if entidad_anual:
            st.markdown("---")
            st.markdown(f"### 📊 Captura Anual {año_captura} - {entidad_anual}")

            # Obtener plataformas disponibles para esta institución
            plataformas_disponibles = list(COLEGIOS_MARISTAS[entidad_anual].keys())

            # Crear formulario para cada mes y plataforma
            with st.form("captura_anual_form", clear_on_submit=False):
                st.markdown("#### 📝 Ingreso de Datos Mensuales")

                # Crear una tabla de entrada para todos los meses
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

                # Crear columnas para organizar mejor
                col_plat, col_data = st.columns([1, 4])

                with col_plat:
                    st.markdown("**Plataformas**")
                    for plataforma in plataformas_disponibles:
                        st.markdown(f"**{plataforma}**")

                with col_data:
                    st.markdown("**Datos por Mes**")
                    # Crear headers de meses
                    cols_meses = st.columns(len(meses))
                    for i, mes in enumerate(meses):
                        with cols_meses[i]:
                            st.markdown(f"**{mes[:3]}**")  # Mostrar solo primeras 3 letras

                # Crear inputs para cada plataforma y mes
                datos_anuales = {}
                for plataforma in plataformas_disponibles:
                    datos_anuales[plataforma] = {}

                    # Crear fila para esta plataforma
                    cols_plat_data = st.columns([1] + [1] * len(meses))

                    with cols_plat_data[0]:
                        st.markdown(f"**{plataforma}**")

                    for i, mes in enumerate(meses):
                        with cols_plat_data[i + 1]:
                            seguidores_key = f"{plataforma}_{mes}_seguidores"
                            datos_anuales[plataforma][mes] = st.number_input(
                                f"Seguidores {plataforma} {mes}",
                                min_value=0,
                                value=0,
                                step=10,
                                key=seguidores_key,
                                label_visibility="collapsed"
                            )

                st.markdown("---")

                # Botón de envío
                submitted_anual = st.form_submit_button(
                    "💾 Guardar Datos Anuales", type="primary", width="stretch"
                )

                if submitted_anual:
                    # Procesar y guardar los datos
                    registros_guardados = 0
                    errores = []

                    with st.status("Guardando datos anuales...") as status:
                        for plataforma in plataformas_disponibles:
                            usuario_plataforma = COLEGIOS_MARISTAS[entidad_anual][plataforma]

                            for i, mes in enumerate(meses):
                                seguidores_mes = datos_anuales[plataforma][mes]

                                # Solo guardar si hay datos (seguidores > 0)
                                if seguidores_mes > 0:
                                    try:
                                        # Crear fecha para este mes
                                        fecha_mes = pd.to_datetime(f"{año_captura}-{i+1:02d}-01")

                                        # Obtener datos de cache
                                        cuentas_cache, _ = data_provider.get_data()

                                        # Generar ID de cuenta
                                        id_cuenta = get_id(
                                            entidad_anual,
                                            plataforma,
                                            usuario_plataforma,
                                            df_cuentas_cache=cuentas_cache,
                                        )

                                        # Crear registro (usando valores estimados para otras métricas)
                                        # En una implementación completa, se pedirían todos los campos
                                        alcance_estimado = int(seguidores_mes * 2.5)  # Estimación
                                        interacciones_estimadas = int(alcance_estimado * 0.08)  # 8% engagement
                                        likes_promedio = max(5, int(interacciones_estimadas / 30))  # ~30 posts/mes
                                        engagement_rate = round((interacciones_estimadas / seguidores_mes * 100), 2)

                                        registro = pd.DataFrame([{
                                            "id_cuenta": id_cuenta,
                                            "entidad": entidad_anual,
                                            "plataforma": plataforma,
                                            "usuario_red": usuario_plataforma,
                                            "fecha": fecha_mes,
                                            "seguidores": int(seguidores_mes),
                                            "alcance": alcance_estimado,
                                            "interacciones": interacciones_estimadas,
                                            "likes_promedio": likes_promedio,
                                            "engagement_rate": engagement_rate,
                                        }])

                                        # Guardar usando save_batch
                                        success = save_batch(registro)
                                        if success:
                                            registros_guardados += 1
                                        else:
                                            errores.append(f"Error guardando {plataforma} - {mes}")

                                    except Exception as e:
                                        errores.append(f"Error en {plataforma} - {mes}: {str(e)}")
                                        logging.error(f"Error guardando registro anual: {e}")

                        # Mostrar resultados
                        if registros_guardados > 0:
                            status.update(label=f"✅ ¡Guardados {registros_guardados} registros exitosamente!")
                            toast_success(f"¡Captura anual completada! {registros_guardados} registros guardados")
                            ui.render_status(
                                f"Captura anual completada: {registros_guardados} registros guardados",
                                tipo="success",
                            )

                            # Mostrar resumen
                            st.info(f"📊 Resumen: {entidad_anual} - {año_captura}")
                            resumen_data = []
                            for plataforma in plataformas_disponibles:
                                meses_con_datos = sum(1 for mes in meses if datos_anuales[plataforma][mes] > 0)
                                resumen_data.append({
                                    "Plataforma": plataforma,
                                    "Meses con datos": meses_con_datos,
                                    "Usuario": COLEGIOS_MARISTAS[entidad_anual][plataforma]
                                })

                            if resumen_data:
                                st.dataframe(pd.DataFrame(resumen_data), width="stretch")

                        else:
                            status.update(label="❌ No se guardaron registros")
                            ui.render_status(
                                "No se encontraron datos para guardar. Ingresa al menos un valor de seguidores.",
                                tipo="error",
                            )

                        if errores:
                            ui.render_status(
                                f"La captura terminó con {len(errores)} errores",
                                tipo="error",
                            )
                            st.error("❌ Errores encontrados:")
                            for error in errores:
                                st.error(f"  • {error}")

                        # Limpiar cache para refrescar datos
                        st.cache_data.clear()
