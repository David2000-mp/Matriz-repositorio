"""
Header personalizado institucional con funcionalidad de sidebar toggle.
Combina branding Marista con UX nativa de Streamlit.
"""

import streamlit as st
from utils.helpers import load_image


def render_custom_header():
    """
    Renderiza header personalizado con:
    - Logo institucional
    - Título CHAMPILEAKS
    - Botón de toggle sidebar (mantiene funcionalidad nativa)
    - Oculta botones innecesarios (Share, Settings, Menu)
    """
    
    # Cargar logo
    logo_b64 = load_image("logo_maristas.png")
    
    # CSS para ocultar elementos nativos pero mantener toggle sidebar
    st.markdown("""
        <style>
        /* ============================================
           HEADER PERSONALIZADO CHAMPILEAKS
           Diseño: Institucional Marista profesional
           ============================================ */
        
        /* Ocultar toolbar de Streamlit (Share, Settings, Menu) */
        .stToolbarActions {
            display: none !important;
        }
        
        #MainMenu {
            display: none !important;
        }
        
        /* Mantener SOLO el botón de toggle sidebar */
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #003696 0%, #00235A 100%) !important;
            height: 70px !important;
            padding: 0 2rem !important;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Contenedor del header personalizado */
        .custom-header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 70px;
            padding: 0 2rem;
            background: transparent;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999998;
            pointer-events: none;
        }
        
        /* Logo institucional */
        .custom-header-logo {
            height: 45px;
            width: auto;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
            pointer-events: auto;
        }
        
        /* Título CHAMPILEAKS */
        .custom-header-title {
            color: #FFFFFF;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            pointer-events: auto;
        }
        
        /* Ajustar posición del botón nativo de sidebar */
        button[data-testid="stExpandSidebarButton"] {
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            padding: 8px !important;
            transition: all 0.2s ease !important;
        }
        
        button[data-testid="stExpandSidebarButton"]:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            transform: scale(1.05) !important;
        }
        
        /* Icono del botón sidebar en blanco */
        button[data-testid="stExpandSidebarButton"] span {
            color: #FFFFFF !important;
        }
        
        /* Ocultar completamente el texto del icono Material */
        button[data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"] {
            font-size: 0 !important;
            text-indent: -9999px !important;
            overflow: hidden !important;
            display: inline-block !important;
            width: 24px !important;
            height: 24px !important;
        }
        
        /* Reemplazar con símbolo de flecha personalizado */
        button[data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"]::after {
            content: "☰" !important;
            font-size: 20px !important;
            text-indent: 0 !important;
            display: block !important;
            color: #FFFFFF !important;
        }
        
        /* Ajustar padding del contenido principal */
        .main .block-container {
            padding-top: 5rem !important;
        }
        
        /* Responsive - Mobile */
        @media (max-width: 768px) {
            .custom-header-container {
                padding: 0 1rem;
            }
            
            .custom-header-logo {
                height: 35px;
            }
            
            .custom-header-title {
                font-size: 1.25rem;
                letter-spacing: 2px;
            }
            
            header[data-testid="stHeader"] {
                height: 60px !important;
            }
            
            .main .block-container {
                padding-top: 4rem !important;
            }
        }
        
        /* Ocultar footer de Streamlit */
        footer {
            display: none !important;
        }
        
        /* Marca de agua "Made with Streamlit" */
        .viewerBadge_container__r5tak {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Renderizar header personalizado
    st.markdown(f"""
        <div class="custom-header-container">
            <img src="data:image/png;base64,{logo_b64}" 
                 class="custom-header-logo" 
                 alt="Logo Maristas">
            <h1 class="custom-header-title">CHAMPILEAKS</h1>
        </div>
    """, unsafe_allow_html=True)
