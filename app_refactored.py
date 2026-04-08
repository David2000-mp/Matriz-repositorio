"""
App refactorizado para CHAMPILEAKS.
Provee enrutamiento limpio a las vistas y asegura inyección de estilos.
"""
import streamlit as st
import pandas as pd
from components import (
    inject_custom_css,
    inject_layout_compact_css,
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
        inject_layout_compact_css(hide_streamlit_header=False)
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

    # Sidebar: El ÚNICO lugar para filtrar
    with st.sidebar:
        # Logo Marista
        logo_b64 = load_image("logo_maristas.png")
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-marista" alt="Logo Marista">', unsafe_allow_html=True)
        
        st.title("CHAMPILEAKS")

        st.subheader("Navegación")
        st.caption("Primero elige una vista; después usa los filtros globales para refinar la lectura.")
        
        # Navegación simplificada sin index calculado
        menu_options = ["🏠 Inicio", "📊 Dashboard Global", "📈 Comparativas", "💡 Calc. Engagement", "📝 Captura", "🔍 Auditoría de Respuestas", "⚙️ Configuración"]
        selected_display = st.radio(
            "Seleccionar página", 
            menu_options, 
            index=menu_options.index(st.session_state.get("page_selection", "🏠 Inicio")) if st.session_state.get("page_selection") in menu_options else 0,
            label_visibility="hidden"
        )
        
        # Mapear display a canonical
        display_to_canonical = {
            "🏠 Inicio": "Inicio",
            "📊 Dashboard Global": "Dashboard Global", 
            "📈 Comparativas": "Comparativas",
            "💡 Calc. Engagement": "Calc. Engagement",
            "📝 Captura": "Captura",
            "🔍 Auditoría de Respuestas": "Auditoría de Respuestas",
            "⚙️ Configuración": "Configuración",
        }
        
        selected = display_to_canonical.get(selected_display, "Inicio")
        st.session_state["page_selection"] = selected
        scroll_to_top_on_nav_change("page_selection")

        st.markdown("---")
        st.subheader("Filtros Globales")
        st.caption("Estos filtros impactan dashboards y comparativas para mantener el contexto.")

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
                    origin = st.session_state.get("data_origin", "cloud")
                    if origin == "cloud":
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
            
            # Métricas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                total_registros = len(df_forms)
                st.metric("Total de Registros", total_registros)
            
            with col2:
                promedio_engagement = df_forms['engagement_rate'].mean()
                st.metric("Promedio de Engagement", f"{promedio_engagement:.2f}%")
            
            with col3:
                ultima_fecha = df_forms['fecha'].max()
                st.metric("Última Fecha de Reporte", ultima_fecha.strftime('%Y-%m-%d') if pd.notna(ultima_fecha) else "N/A")
            
            # Data Editor para correcciones manuales
            st.subheader("Datos del Formulario")
            edited_df = st.data_editor(
                df_forms,
                use_container_width='100%',
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
            errores = df_forms[df_forms['error_validacion'] != '']
            if not errores.empty:
                st.error("Filas con errores de validación:")
                st.dataframe(errores[['entidad', 'plataforma', 'error_validacion']], use_container_width='100%')

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
