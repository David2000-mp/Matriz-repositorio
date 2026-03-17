"""
Header personalizado institucional con funcionalidad de sidebar toggle.
Combina branding Marista con UX nativa de Streamlit.
"""

import streamlit as st


def render_custom_header():
    """
    Renderiza header personalizado con:
    - Título CHAMPILEAKS
    - Botón de toggle sidebar (mantiene funcionalidad nativa)
    - Oculta botones innecesarios (Share, Settings, Menu)
    """
    
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
        
        /* Header RECTANGULAR - deja que styles.py maneje el fondo */
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 70px !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            width: 100% !important;
        }
        
        /* Botón de toggle sidebar - visible y encima */
        button[data-testid="stExpandSidebarButton"] {
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            transition: all 0.2s ease !important;
            z-index: 99999 !important;
            position: relative !important;
        }

        button[data-testid="stExpandSidebarButton"]:hover {
            background: rgba(255, 255, 255, 0.25) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Ajustar padding del contenido principal - espacio para barra fija */
        .main .block-container {
            padding-top: 5rem !important;
        }
        
        /* ========================================
           BOTONES SECONDARY (Navegación Landing)
           ======================================== */
        
        /* Botones secondary con diseño institucional - Selectores ultra específicos */
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"],
        .stButton button[kind="secondary"],
        div[data-testid="stButton"] button[kind="secondary"] {
            background-color: #003696 !important;
            color: #FFFFFF !important;
            border: 2px solid #003696 !important;
            border-radius: 10px !important;
            padding: 18px 16px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 12px rgba(0, 54, 150, 0.25) !important;
        }
        
        button[kind="secondary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        .stButton button[kind="secondary"]:hover,
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: #00235A !important;
            color: #FFFFFF !important;
            border-color: #FFB81C !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(255, 184, 28, 0.4) !important;
        }
        
        button[kind="secondary"]:active,
        button[data-testid="stBaseButton-secondary"]:active {
            transform: translateY(-1px) !important;
        }
        
        /* Texto dentro de botones secondary - FORZAR BLANCO EN TODOS LOS NIVELES */
        button[kind="secondary"] *,
        button[data-testid="stBaseButton-secondary"] *,
        .stButton button[kind="secondary"] *,
        div[data-testid="stButton"] button[kind="secondary"] * {
            color: #FFFFFF !important;
        }
        
        /* Específicamente el párrafo dentro del markdown */
        button[kind="secondary"] p,
        button[data-testid="stBaseButton-secondary"] p,
        button[kind="secondary"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            margin: 0 !important;
        }
        
        /* Botones secondary con tooltip */
        div[data-testid="stTooltipHoverTarget"] button[kind="secondary"],
        div.stTooltipHoverTarget button[kind="secondary"] {
            background-color: #003696 !important;
            color: #FFFFFF !important;
        }
        
        /* Texto en botones con tooltip */
        div[data-testid="stTooltipHoverTarget"] button[kind="secondary"] *,
        div[data-testid="stTooltipHoverTarget"] button[kind="secondary"] p,
        div.stTooltipHoverTarget button[kind="secondary"] *,
        div.stTooltipHoverTarget button[kind="secondary"] p {
            color: #FFFFFF !important;
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
        
        /* Ocultar títulos duplicados generados por st.title() o st.header() */
        div[data-testid="stHeadingWithActionElements"] h1#champileaks {
            display: none !important;
        }
        
        /* Ocultar cualquier h1 que contenga "CHAMPILEAKS" */
        h1:not(.custom-header-title) {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Renderizar header personalizado
    st.markdown("""
        <div class="custom-header-container">
            <h1 class="custom-header-title">CHAMPILEAKS</h1>
        </div>
    """, unsafe_allow_html=True)
