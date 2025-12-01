"""
CHAMPILYTICS - Sistema de Análisis de Redes Sociales
Red Marista México

Aplicación principal refactorizada con arquitectura modular limpia.

Estructura:
- utils/: Gestión de datos y funciones utilitarias
- components/: Componentes UI y estilos
- views/: Páginas de la aplicación
"""

import streamlit as st
import logging
from pathlib import Path

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# ===========================
# CONFIGURACIÓN DE LA APP
# ===========================

st.set_page_config(
    page_title="Maristas Analytics", 
    layout="wide", 
    page_icon="Ⓜ️",
    initial_sidebar_state="expanded"
)

# ===========================
# IMPORTACIONES DE MÓDULOS
# ===========================

# Estilos y componentes UI
from components import inject_custom_css

# Utilidades de datos
from utils import load_data

# Páginas/Vistas
# (Las importaremos dinámicamente para optimizar carga)

# ===========================
# INYECCIÓN DE ESTILOS
# ===========================

inject_custom_css()

# ===========================
# NAVEGACIÓN Y ENRUTAMIENTO
# ===========================

def main():
    """Función principal con lógica de navegación."""
    
    # Inicializar estado de sesión
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    
    # Verificar si hay datos para mostrar el menú principal
    cuentas, metricas = load_data()
    tiene_datos = not cuentas.empty and not metricas.empty
    
    # ===========================
    # SIDEBAR - NAVEGACIÓN
    # ===========================
    
    with st.sidebar:
        st.markdown("### CHAMPILYTICS")
        st.caption("Red Marista México")
        st.divider()
        
        # Menú de navegación (siempre visible)
        menu_options = [
            "🏠 Inicio",
            "📊 Dashboard Global",
            "🔍 Análisis Individual",
            "📝 Captura Manual",
            "⚙️ Configuración"
        ]
        
        # Mapeo de opciones a keys internas
        page_mapping = {
            "🏠 Inicio": "landing",
            "📊 Dashboard Global": "dashboard",
            "🔍 Análisis Individual": "analisis",
            "📝 Captura Manual": "captura",
            "⚙️ Configuración": "config"
        }
        
        # Obtener índice actual
        current_key = st.session_state.page
        reverse_mapping = {v: k for k, v in page_mapping.items()}
        current_label = reverse_mapping.get(current_key, "🏠 Inicio")
        
        try:
            default_index = menu_options.index(current_label)
        except ValueError:
            default_index = 0
        
        selected = st.radio(
            "Navegación",
            menu_options,
            index=default_index,
            label_visibility="collapsed"
        )
        
        # Actualizar página si cambió la selección
        new_page = page_mapping[selected]
        if new_page != st.session_state.page:
            st.session_state.page = new_page
            st.rerun()
        
        # ===========================
        # CARGA MASIVA (siempre visible en sidebar)
        # ===========================
        st.divider()
        st.markdown("### 📂 Carga Masiva")
        archivo = st.file_uploader(
            "Sube CSV o Excel",
            type=["csv", "xlsx"],
            accept_multiple_files=False,
            key="sidebar_file_uploader"
        )
        if archivo is not None:
            import pandas as pd
            from utils.data_manager import save_batch
            try:
                if archivo.name.lower().endswith(".csv"):
                    df = pd.read_csv(archivo)
                elif archivo.name.lower().endswith(".xlsx"):
                    df = pd.read_excel(archivo)
                else:
                    st.error("Formato no soportado.")
                    df = None
            except Exception as e:
                st.error(f"Error: {e}")
                df = None
            if df is not None:
                df.columns = [str(col).strip().lower() for col in df.columns]
                columnas_requeridas = ['entidad', 'plataforma', 'fecha', 'seguidores']
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    st.error(f"❌ Faltan: {faltantes}")
                else:
                    st.success(f"✅ {len(df)} registros")
                    with st.expander("Vista previa"):
                        st.dataframe(df.head(5), width='stretch')
                    if st.button("🚀 PROCESAR", type="primary", use_container_width=True):
                        try:
                            if 'fecha' in df.columns:
                                df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
                            datos_masivos = df.to_dict('records')
                            with st.spinner(f"Procesando {len(datos_masivos)} registros..."):
                                save_batch(datos_masivos)
                            st.success(f"¡{len(datos_masivos)} guardados!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        st.divider()
        st.caption(f"v2.0 • Arquitectura Modular")
        st.caption(f"© 2024 Maristas México")
    
    # ===========================
    # RENDERIZADO DE PÁGINAS
    # ===========================
    
    # Importaciones dinámicas (lazy loading) para optimizar rendimiento
    page = st.session_state.page
    
    try:
        if page == "landing":
            from views.landing import render as render_landing
            render_landing()
        
        elif page == "dashboard":
            from views.dashboard import render as render_dashboard
            render_dashboard()
        
        elif page == "analisis":
            from views.analytics import render as render_analytics
            render_analytics()
        
        elif page == "captura":
            from views.data_entry import render as render_data_entry
            render_data_entry()
        
        elif page == "config":
            from views.settings import render as render_settings
            render_settings()
        
        else:
            st.error(f"Página no encontrada: {page}")
            st.session_state.page = "landing"
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error al cargar la página: {e}")
        logging.error(f"Error en página {page}: {e}", exc_info=True)
        
        if st.button("🔙 Volver al inicio"):
            st.session_state.page = "landing"
            st.rerun()


# ===========================
# PUNTO DE ENTRADA
# ===========================

if __name__ == "__main__":
    main()
