"""
App refactorizado para CHAMPILEAKS.
Provee enrutamiento limpio a las vistas y asegura inyección de estilos.
"""
import streamlit as st
import pandas as pd
from components import (
    inject_custom_css,
    inject_layout_compact_css,
    inject_clipboard_shortcut_guard,
    scroll_to_top_on_nav_change,
    render_custom_header,
)
from utils.helpers import load_image
from utils.logger import set_production_mode, get_logger
from utils.sheets_connector import cargar_respuestas_forms

logger = get_logger(__name__)


def main():
    # Configurar logging para producción si estamos en la nube
    import os
    if os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true":
        set_production_mode()

    st.set_page_config(
        page_title="CHAMPILEAKS",
        layout="wide",
        page_icon="Ⓜ️",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Renderizar header personalizado (antes de cualquier contenido)
    try:
        render_custom_header()
    except Exception as e:
        import logging
        logging.warning(f"No se pudo renderizar header personalizado: {e}")
    
    # Aplicar estilos CSS globales
    try:
        inject_custom_css()
        inject_layout_compact_css(hide_streamlit_header=True)
        inject_clipboard_shortcut_guard()
    except Exception as e:
        try:
            st.warning(f"No se pudo aplicar CSS personalizado: {e}")
        except Exception:
            # En entornos no interactivos, registrar en la consola
            import logging

            logging.warning(f"No se pudo mostrar warning de CSS: {e}")

    # Sincronizar navegación desde la landing (permite botones que escriben `st.session_state['page']`)
    if "page" in st.session_state:
        st.session_state["page_selection"] = st.session_state.page
        del st.session_state["page"]

    # Asegurar sidebar desplegado por defecto una vez por sesión.
    # Evita forzarlo en cada rerun para no romper la preferencia manual del usuario.
    if not st.session_state.get("_sidebar_default_expanded_applied", False):
        st.html(
            """
            <script>
            const ensureExpanded = () => {
              const expandBtn = parent.document.querySelector('button[data-testid="stExpandSidebarButton"]');
              if (expandBtn) {
                expandBtn.click();
              }
            };
            setTimeout(ensureExpanded, 30);
            setTimeout(ensureExpanded, 180);
            </script>
            """,
            unsafe_allow_javascript=True,
        )
        st.session_state["_sidebar_default_expanded_applied"] = True

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary span,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
        [data-testid="stSidebar"] [data-testid="stRadio"] label p,
        [data-testid="stSidebar"] [data-testid="stRadio"] label span,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #f5f7fa !important;
            fill: #f5f7fa !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 0.35rem;
            padding-bottom: 0.35rem;
            gap: 0.25rem;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {
            margin-bottom: 0.15rem;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            margin-top: 0.1rem;
            margin-bottom: 0.15rem;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] details {
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            padding-top: 0.2rem;
            padding-bottom: 0.2rem;
        }

        [data-testid="stSidebar"] [data-testid="stSelectbox"],
        [data-testid="stSidebar"] [data-testid="stButton"],
        [data-testid="stSidebar"] [data-testid="stRadio"] {
            margin-bottom: 0.15rem;
        }

        [data-testid="stSidebar"] {
            padding-top: 0.35rem;
            padding-bottom: 0.35rem;
        }

        [data-testid="stSidebarUserContent"] {
            padding-top: 0rem !important;
        }

        [data-testid="stSidebarHeader"] {
            padding: 0rem !important;
            min-height: 0px !important;
        }

        [data-testid="stSidebar"] .element-container:has(.logo-marista) {
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.logo-marista) {
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.logo-marista) > * {
            margin: 0 !important;
            padding: 0 !important;
        }

        .logo-marista {
            margin: 0 auto 0 auto !important;
            padding: 0 !important;
            display: block !important;
            line-height: 0 !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.logo-marista) p {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar: El ÚNICO lugar para filtrar
    with st.sidebar:
        # Logo Marista
        logo_b64 = load_image("logo_maristas.png")
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-marista" alt="Logo Marista">', unsafe_allow_html=True)
        
        st.title("CHAMPILEAKS")

        st.subheader("Navegación")
        # Navegación agrupada con sincronización global de estado.
        navigation_groups = {
            "metrics_analysis": [
                "Inicio",
                "Dashboard Global",
                "Comparativas",
                "Tipo de contenidos",
                "Analisis de textos",
                "Calc. Engagement",
            ],
            "data_management": [
                "Registro Estadistico",
                "Captura",
                "Auditoría de Respuestas",
            ],
            "settings": [
                "Configuración",
            ],
        }

        # Compatibilidad con valores legacy (con emoji) para evitar navegación inválida.
        legacy_display_to_canonical = {
            "🏠 Inicio": "Inicio",
            "📊 Dashboard Global": "Dashboard Global",
            "📈 Comparativas": "Comparativas",
            "🆕 Tipo de contenidos": "Tipo de contenidos",
            "🧠 Analisis de textos": "Analisis de textos",
            "📐 Registro Estadistico": "Registro Estadistico",
            "💡 Calc. Engagement": "Calc. Engagement",
            "📝 Captura": "Captura",
            "🔍 Auditoría de Respuestas": "Auditoría de Respuestas",
            "⚙️ Configuración": "Configuración",
        }

        valid_canonical_options = {
            option for options in navigation_groups.values() for option in options
        }
        label_to_canonical = {
            option: option for option in valid_canonical_options
        }
        canonical_to_label = {
            option: option for option in valid_canonical_options
        }
        canonical_to_group = {}
        for group_name, group_options in navigation_groups.items():
            for option in group_options:
                canonical_to_group[option] = group_name

        radio_keys = {
            "metrics_analysis": "nav_radio_metrics_analysis",
            "data_management": "nav_radio_data_management",
            "settings": "nav_radio_settings",
        }

        current_selection = st.session_state.get("page_selection")
        if current_selection in legacy_display_to_canonical:
            current_selection = legacy_display_to_canonical[current_selection]
        if current_selection not in valid_canonical_options:
            current_selection = "Inicio"
        st.session_state["page_selection"] = current_selection

        def _sync_navigation(changed_radio_key: str):
            if st.session_state.get("_nav_sync_in_progress", False):
                return

            st.session_state["_nav_sync_in_progress"] = True
            try:
                selected_label = st.session_state.get(changed_radio_key)
                selected_canonical = label_to_canonical.get(selected_label)
                if selected_canonical in valid_canonical_options:
                    st.session_state["page_selection"] = selected_canonical

                active_canonical = st.session_state.get("page_selection", "Inicio")
                active_group = canonical_to_group.get(active_canonical, "metrics_analysis")

                for group_name, state_key in radio_keys.items():
                    if group_name == active_group:
                        st.session_state[state_key] = canonical_to_label.get(active_canonical)
                    else:
                        st.session_state[state_key] = None
            finally:
                st.session_state["_nav_sync_in_progress"] = False

        active_group = canonical_to_group.get(st.session_state["page_selection"], "metrics_analysis")
        for group_name, state_key in radio_keys.items():
            if group_name == active_group:
                st.session_state[state_key] = canonical_to_label[st.session_state["page_selection"]]
            elif state_key not in st.session_state:
                st.session_state[state_key] = None

        with st.expander("Métricas y Análisis", expanded=True):
            st.radio(
                "Métricas y Análisis",
                navigation_groups["metrics_analysis"],
                key=radio_keys["metrics_analysis"],
                index=None,
                label_visibility="collapsed",
                on_change=_sync_navigation,
                args=(radio_keys["metrics_analysis"],),
            )

        with st.expander("Gestión de Datos", expanded=False):
            st.radio(
                "Gestión de Datos",
                navigation_groups["data_management"],
                key=radio_keys["data_management"],
                index=None,
                label_visibility="collapsed",
                on_change=_sync_navigation,
                args=(radio_keys["data_management"],),
            )

        with st.expander("Ajustes", expanded=False):
            st.radio(
                "Ajustes",
                navigation_groups["settings"],
                key=radio_keys["settings"],
                index=None,
                label_visibility="collapsed",
                on_change=_sync_navigation,
                args=(radio_keys["settings"],),
            )

        selected = st.session_state["page_selection"]
        st.session_state["page_selection"] = selected
        scroll_to_top_on_nav_change("page_selection")

        st.markdown("---")
        st.subheader("Filtros Globales")

        # Filtros globales (sin cargar datos aquí - lazy loading)
        entidades = ["Todas"]  # Placeholder, se actualizará cuando se carguen datos
        if "global_entities" in st.session_state:
            entidades = ["Todas"] + st.session_state.global_entities

        # Determinar el índice por defecto (siempre "Todas" si no hay filtro guardado)
        filtro_actual = st.session_state.get("filtro_entidad", "Todas")
        if filtro_actual in entidades:
            index_default = entidades.index(filtro_actual)
        else:
            index_default = 0  # "Todas"
            # Asegurar que el filtro esté inicializado en "Todas"
            st.session_state["filtro_entidad"] = "Todas"

        entidad_sel = st.selectbox("Colegio", entidades, index=index_default, key="filtro_entidad")

        # Meses disponibles (se actualizarán cuando se carguen datos)
        meses = ["Todos"]
        if "global_months" in st.session_state:
            meses = ["Todos"] + st.session_state.global_months

        # Determinar el índice por defecto para mes (siempre "Todos" si no hay filtro guardado)
        filtro_mes_actual = st.session_state.get("filtro_mes", "Todos")
        if filtro_mes_actual in meses:
            index_mes_default = meses.index(filtro_mes_actual)
        else:
            index_mes_default = 0  # "Todos"
            # Asegurar que el filtro esté inicializado en "Todos"
            st.session_state["filtro_mes"] = "Todos"

        mes_sel = st.selectbox("Periodo", meses, index=index_mes_default, key="filtro_mes")

        # Botón de Reset Filtros
        if st.button("Reset Filtros", help="Limpia los filtros y devuelve a 'Todos los Colegios'"):
            if "filtro_entidad" in st.session_state:
                del st.session_state["filtro_entidad"]
            if "filtro_mes" in st.session_state:
                del st.session_state["filtro_mes"]
            st.rerun()

        if st.button("Forzar recarga", help="Limpia caché y vuelve a cargar datos desde Google Sheets"):
            from utils.data_provider import data_provider

            data_provider.invalidate_cache()
            st.session_state.force_data_refresh = True
            st.toast("Recarga forzada activada", icon="🔄")
            st.rerun()

        st.divider()
        st.caption("v2.1.0 • Maristas")

    # --- Función de Carga Lazy ---
    def load_data_lazy():
        """Carga datos solo cuando se necesitan (lazy loading).

        Usa `utils.data_provider` como fuente canónica para filtros y datos.
        El data_provider incluye el importador de formularios con cálculo de interacciones.
        """
        refresh_data = st.session_state.get("force_data_refresh", False)
        
        if "app_data" not in st.session_state or refresh_data:
            with st.spinner("Cargando datos desde Google Sheets..."):
                try:
                    # PRIORIDAD 1: Usar data_provider que tiene el importador de formulario
                    from utils.data_provider import data_provider
                    
                    # Cargar datos fusionados con force_reload si se solicita refresh
                    df_global = data_provider.get_merged_data(force_reload=refresh_data)
                    
                    if df_global is None or df_global.empty:
                        st.warning("No se pudieron cargar datos. Verifica tu conexión a Google Sheets.")
                        return None
                    
                    # Asegurar columnas estándar
                    expected_columns = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red', 'fecha', 'seguidores', 'engagement_rate', 'alcance', 'interacciones', 'likes_promedio']
                    
                    # Agregar columnas faltantes
                    for col in expected_columns:
                        if col not in df_global.columns:
                            df_global[col] = ''
                    
                    # Usar id_cuenta como id
                    if 'id_cuenta' in df_global.columns:
                        df_global['id'] = df_global['id_cuenta'].astype(str)
                    else:
                        df_global['id'] = range(len(df_global))
                    
                    # Procesar fecha si no es datetime
                    if 'fecha' in df_global.columns:
                        df_global['fecha'] = pd.to_datetime(df_global['fecha'], errors='coerce')

                    # Actualizar filtros globales disponibles
                    try:
                        if not df_global.empty and "entidad" in df_global.columns:
                            st.session_state.global_entities = sorted([str(e) for e in df_global["entidad"].dropna().unique()])
                        if not df_global.empty and "fecha" in df_global.columns:
                            meses = sorted(df_global["fecha"].dt.strftime("%Y-%m").dropna().unique(), reverse=True)
                            st.session_state.global_months = meses
                    except Exception as e:
                        logger.warning(f"No se pudieron actualizar filtros globales: {e}")

                    st.session_state.app_data = {
                        "cuentas": pd.DataFrame(),
                        "metricas": pd.DataFrame(),
                        "df_global": df_global
                    }
                    
                    # Limpiar flag de refresh
                    if "force_data_refresh" in st.session_state:
                        st.session_state.force_data_refresh = False
                    
                    # Toast de éxito
                    origin = st.session_state.get("data_origin", "unknown")
                    if origin in {"sheets", "sheets_form"}:
                        st.toast("🌐 Datos cargados desde Google Sheets", icon="✅")
                    else:
                        st.toast("💾 Datos cargados correctamente", icon="✅")
                    
                    return st.session_state.app_data

                except Exception as e:
                    st.error("❌ Error al cargar datos")
                    st.exception(e)
                    return None

        return st.session_state.app_data

    # --- Función para aplicar filtros ---
    def apply_filters(df_global):
        """Aplica filtros globales al dataframe"""
        if df_global is None or df_global.empty:
            return df_global

        df_filtered = df_global.copy()

        # Filtro por entidad
        entidad_sel = st.session_state.get("filtro_entidad", "Todas")
        if entidad_sel != "Todas" and entidad_sel in df_filtered["entidad"].values:
            df_filtered = df_filtered[df_filtered["entidad"] == entidad_sel]

        return df_filtered

    # Router con Lazy Loading
    if selected == "Inicio":
        from views import landing
        landing.render()
    elif selected == "Dashboard Global":
        data = load_data_lazy()
        if data:
            df_filtered = apply_filters(data["df_global"])
            from views import dashboard
            dashboard.render(df_filtered)
    elif selected == "Comparativas":
        # Sprint 2 Week 3: Nueva vista de comparación lado a lado
        from views import comparison
        comparison.render_comparison_view()
    elif selected == "Tipo de contenidos":
        from views import new_data_dashboard

        new_data_dashboard.render_new_data_dashboard()
    elif selected == "Analisis de textos":
        from views import text_analysis_dashboard

        text_analysis_dashboard.render_text_analysis_dashboard()
    elif selected == "Registro Estadistico":
        from views import statistical_registry_dashboard

        statistical_registry_dashboard.render_statistical_registry_dashboard()
    elif selected == "Calc. Engagement":
        # Calculadora de Engagement para Facebook y TikTok
        from views import engagement_calculator_v2 as engagement_calculator
        engagement_calculator.render()
    elif selected == "Captura":
        # Captura interna con validaciones y monitor mensual de pendientes.
        from views import data_entry

        data_entry.render()
    elif selected == "Auditoría de Respuestas":
        # Nueva sección: Auditoría de Respuestas
        st.header("🔍 Auditoría de Respuestas")

        try:
            df_forms = cargar_respuestas_forms()
            
            if df_forms.empty:
                st.warning("No hay datos nuevos del formulario")
                st.stop()

            df_forms = df_forms.reset_index(drop=True)
            
            # Métricas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                total_registros = len(df_forms)
                st.metric("Total de Registros", total_registros)
            
            with col2:
                promedio_engagement = df_forms['engagement_rate'].mean() if 'engagement_rate' in df_forms.columns else 0.0
                st.metric("Promedio de Engagement", f"{promedio_engagement:.2f}%")
            
            with col3:
                ultima_fecha = df_forms['fecha'].max() if 'fecha' in df_forms.columns else pd.NaT
                st.metric("Última Fecha de Reporte", ultima_fecha.strftime('%Y-%m-%d') if pd.notna(ultima_fecha) else "N/A")
            
            # Data Editor para correcciones manuales
            st.subheader("Datos del Formulario")
            edited_df = st.data_editor(
                df_forms,
                width="stretch",
                num_rows="dynamic",
                column_config={
                    "fecha": st.column_config.DateColumn("Fecha del Reporte"),
                    "seguidores": st.column_config.NumberColumn("Seguidores Totales", min_value=0),
                    "engagement_rate": st.column_config.NumberColumn("Engagement Rate (%)", min_value=0.0, max_value=100.0, step=0.01),
                    "alcance": st.column_config.NumberColumn("Alcance Total", min_value=0),
                    "interacciones": st.column_config.NumberColumn("Interacciones Totales", min_value=0),
                }
            )
            
            # Mostrar filas con errores
            if 'error_validacion' not in df_forms.columns:
                df_forms['error_validacion'] = ''

            errores = df_forms[df_forms['error_validacion'] != '']
            if not errores.empty:
                st.error("Filas con errores de validación:")
                error_cols = [col for col in ['entidad', 'plataforma', 'error_validacion'] if col in errores.columns]
                st.dataframe(errores[error_cols], width="stretch")

        except Exception as e:
            st.error(f"Error cargando datos del formulario: {e}")
            import logging
            logging.error(f"Error en auditoría de respuestas: {e}")
    elif selected == "Configuración":
        from views import settings
        settings.render()
    else:
        from views import landing
        landing.render()


if __name__ == "__main__":
    main()
