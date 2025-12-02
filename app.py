import streamlit as st
from utils.data_manager import COLEGIOS_MARISTAS
from components import styles
from views import dashboard, analytics, data_entry, settings, landing, changelog
import pandas as pd

# 1. Configuración de Página
st.set_page_config(
    page_title="Maristas Analytics",
    layout="wide",
    page_icon="Ⓜ️",
    initial_sidebar_state="expanded"
)

# 2. Inyectar CSS
styles.inject_custom_css()

def main():
    # --- SIDEBAR GLOBAL ---
    with st.sidebar:
        st.markdown("## CHAMPILYTICS")
        opciones_institucion = ["Todas las Instituciones"] + list(COLEGIOS_MARISTAS.keys())
        idx_actual = 0
        if "global_institution_filter" in st.session_state:
            if st.session_state.global_institution_filter in opciones_institucion:
                idx_actual = opciones_institucion.index(st.session_state.global_institution_filter)

        st.selectbox(
            "🏛️ Vista Institucional",
            options=opciones_institucion,
            index=idx_actual,
            key="global_institution_filter"
        )
        st.divider()

        # Menú adaptativo según filtro
        menu_options = [
            "🏠 Inicio",
            "📊 Dashboard Global",
            "🔍 Comparativas Globales",
            "📝 Captura Manual",
            "⚙️ Configuración",
            "📋 Historial de Versiones"
        ]

        idx_menu = 0
        if "page_selection" in st.session_state:
            if st.session_state.page_selection in menu_options:
                idx_menu = menu_options.index(st.session_state.page_selection)

        selected = st.radio(
            "Navegación", 
            menu_options, 
            index=idx_menu,
            key="page_selection"
        )
        st.divider()
        st.caption("v2.1.0 • Sprint 5")

    # --- ENRUTADOR DE VISTAS ---
    filtro = st.session_state.get("global_institution_filter", "Todas las Instituciones")
    if selected == "🏠 Inicio":
        landing.render()
    elif selected == "📊 Dashboard Global":
        dashboard.render()
    elif selected == "🔍 Comparativas Globales":
        analytics.render()
    elif selected == "📝 Captura Manual":
        data_entry.render()
    elif selected == "⚙️ Configuración":
        settings.render()
    elif selected == "📋 Historial de Versiones":
        changelog.render()
    else:
        landing.render()

if __name__ == "__main__":
    main()