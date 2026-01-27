"""
App refactorizado para CHAMPILEAKS.
Provee enrutamiento limpio a las vistas y asegura inyección de estilos.
"""
import streamlit as st
from components import inject_custom_css
from utils.helpers import load_image
from utils.logger import set_production_mode


def main():
    # Configurar logging para producción si estamos en la nube
    import os
    if os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true":
        set_production_mode()

    st.set_page_config(page_title="CHAMPILEAKS", layout="wide", page_icon="Ⓜ️")
    try:
        inject_custom_css()
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
        
        # Navegación simplificada sin index calculado
        menu_options = ["🏠 Inicio", "📊 Dashboard Global", "📈 Comparativas", "📝 Captura", "⚙️ Configuración"]
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
            "📝 Captura": "Captura",
            "⚙️ Configuración": "Configuración",
        }
        
        selected = display_to_canonical.get(selected_display, "Inicio")
        st.session_state["page_selection"] = selected

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

        st.divider()
        st.caption("v2.1.0 • Maristas")

    # --- Función de Carga Lazy ---
    def load_data_lazy():
        """Carga datos solo cuando se necesitan (lazy loading).

        Usa `utils.data_provider` como fuente canónica para filtros y datos.
        """
        if "app_data" not in st.session_state:
            with st.spinner("Cargando datos..."):
                try:
                    # Imports lazy para mejor rendimiento - solo cuando se necesitan
                    import pandas as pd
                    from utils.data_provider import get_data, get_merged_data

                    cuentas, metricas = get_data()

                    # Procesar datos
                    if not cuentas.empty and "id_cuenta" in cuentas.columns:
                        cuentas["id_cuenta"] = cuentas["id_cuenta"].astype(str)
                    if not metricas.empty and "id_cuenta" in metricas.columns:
                        metricas["id_cuenta"] = metricas["id_cuenta"].astype(str)

                    # Merge de datos
                    df_global = pd.DataFrame()
                    if not metricas.empty and not cuentas.empty:
                        df_global = pd.merge(metricas, cuentas, on="id_cuenta", how="left")

                        # Normalizar columnas
                        for logical in ("entidad", "plataforma", "usuario_red"):
                            if logical in df_global.columns:
                                continue
                            for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
                                if suff in df_global.columns:
                                    df_global.rename(columns={suff: logical}, inplace=True)
                                    break

                        if "fecha" in df_global.columns:
                            df_global["fecha"] = pd.to_datetime(df_global["fecha"], errors="coerce")

                    # Actualizar filtros globales disponibles usando data_provider
                    try:
                        merged = get_merged_data()
                        if merged is not None and not merged.empty and "entidad" in merged.columns:
                            st.session_state.global_entities = sorted(merged["entidad"].unique().tolist())
                        if merged is not None and not merged.empty and "fecha" in merged.columns:
                            meses = sorted(merged["fecha"].dt.strftime("%Y-%m").dropna().unique(), reverse=True)
                            st.session_state.global_months = meses
                    except Exception:
                        # Fallback a cuentas/metricas
                        if not cuentas.empty and "entidad" in cuentas.columns:
                            st.session_state.global_entities = sorted(cuentas["entidad"].unique().tolist())
                        if not metricas.empty and "fecha" in df_global.columns:
                            meses = sorted(df_global["fecha"].dt.strftime("%Y-%m").dropna().unique(), reverse=True)
                            st.session_state.global_months = meses

                    st.session_state.app_data = {
                        "cuentas": cuentas,
                        "metricas": metricas,
                        "df_global": df_global
                    }

                    # Toast de éxito
                    origin = st.session_state.get("data_origin", "local")
                    if origin == "cloud":
                        st.toast("🌐 Datos cargados desde la nube", icon="Ⓜ️")
                    else:
                        st.toast("💾 Datos locales cargados", icon="Ⓜ️")

                except Exception as e:
                    st.error("Error al cargar datos")
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
        data = load_data_lazy()
        if data:
            df_filtered = apply_filters(data["df_global"])
            from views import analytics
            analytics.render(df_filtered)
    elif selected == "Captura":
        data = load_data_lazy()
        if data:
            df_filtered = apply_filters(data["df_global"])
            from views import data_entry
            data_entry.render(df_filtered)
    elif selected == "Configuración":
        from views import settings
        settings.render()
    else:
        from views import landing
        landing.render()


if __name__ == "__main__":
    main()
