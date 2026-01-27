"""
Sistema de Estilos Móviles para CHAMPILEAKS.
Optimización responsive para dispositivos móviles y tablets.
Complementa global_styles.py con media queries específicas.
"""


def get_mobile_css() -> str:
    """
    Retorna CSS optimizado para dispositivos móviles.
    
    Optimizaciones incluidas:
    - Padding lateral reducido en móviles
    - Hero banner adaptable por breakpoint
    - KPI cards en columna única
    - Tablas con scroll touch optimizado
    - Tap targets ≥ 44px (iOS standard)
    - Inputs con altura mínima para evitar zoom
    - Tipografía escalable por dispositivo
    
    Breakpoints:
    - Desktop: > 1024px
    - Tablet: 768px - 1024px
    - Mobile Large: 481px - 767px
    - Mobile Small: 320px - 480px
    
    Returns:
        String con CSS móvil listo para st.markdown(unsafe_allow_html=True)
    """
    
    return """
    <style>
    /* ============================================
       CHAMPILEAKS - OPTIMIZACIÓN MÓVIL
       Responsive Design para todos los dispositivos
       ============================================ */
    
    /* === TABLETS (768px - 1024px) === */
    
    @media (max-width: 1024px) {
        /* Reducir padding lateral para aprovechar espacio */
        .block-container {
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
        
        /* Hero banner más compacto */
        .hero-banner {
            height: 350px !important;
        }
        
        /* Métricas ligeramente más pequeñas */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }
        
        /* Gráficas a ancho completo */
        .stPlotlyChart {
            width: 100% !important;
        }
    }
    
    /* === MÓVILES GRANDES (481px - 767px) === */
    
    @media (max-width: 767px) {
        /* ===== LAYOUT Y ESPACIADO ===== */
        
        /* Reducir padding lateral agresivamente - ganar espacio */
        .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Hero banner compacto para móvil */
        .hero-banner {
            height: 250px !important;
        }
        
        .hero-banner h1 {
            font-size: 1.75rem !important;
            line-height: 1.3 !important;
        }
        
        .hero-banner p {
            font-size: 0.95rem !important;
        }
        
        /* ===== KPI CARDS Y MÉTRICAS ===== */
        
        /* KPI Cards en columna única - mejor legibilidad */
        .kpi-cards {
            flex-direction: column !important;
        }
        
        .kpi-card {
            flex: 1 1 100% !important;
            margin-bottom: 12px !important;
            padding: 14px 18px !important;
        }
        
        .kpi-card .kpi-value {
            font-size: 1.6rem !important;
        }
        
        .kpi-card .kpi-title {
            font-size: 0.9rem !important;
        }
        
        /* Métricas Streamlit más compactas */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 0.9rem !important;
        }
        
        /* ===== GRÁFICAS Y VISUALIZACIONES ===== */
        
        /* Gráficas Plotly a 100% ancho */
        .stPlotlyChart {
            width: 100% !important;
            margin: 0 !important;
        }
        
        /* Contenedor de gráfica sin padding extra */
        [data-testid="stPlotlyChart"] {
            padding: 0 !important;
        }
        
        /* ===== TABLAS ===== */
        
        /* Tablas con scroll horizontal suave (touch-optimized) */
        .responsive-table {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            margin: 0 -1.5rem !important; /* Expandir a bordes */
            padding: 0 1.5rem !important;
        }
        
        .responsive-table table {
            min-width: 500px !important;
            font-size: 14px !important;
        }
        
        .responsive-table th,
        .responsive-table td {
            padding: 10px 12px !important;
        }
        
        /* DataFrames de Streamlit */
        .dataframe {
            font-size: 14px !important;
        }
        
        /* ===== BOTONES Y WIDGETS TÁCTILES ===== */
        
        /* Botones más grandes para dedos (iOS tap target: 44x44px) */
        .stButton button {
            padding: 14px 24px !important;
            font-size: 16px !important;
            min-height: 48px !important;
            width: 100% !important; /* Botones a ancho completo en móvil */
        }
        
        /* Inputs táctiles cómodos */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stTimeInput input,
        input,
        textarea,
        select {
            min-height: 44px !important;
            font-size: 16px !important; /* Evita zoom automático en iOS */
            padding: 12px !important;
        }
        
        /* Selectboxes táctiles */
        .stSelectbox > div > div {
            min-height: 44px !important;
        }
        
        /* ===== TABS Y NAVEGACIÓN ===== */
        
        /* Tabs más espaciadas para touch */
        button[data-baseweb="tab"],
        button[data-testid="stTab"] {
            padding: 12px 16px !important;
            font-size: 15px !important;
            min-height: 44px !important;
        }
        
        /* ===== SIDEBAR MÓVIL ===== */
        
        /* Sidebar no debe cubrir toda la pantalla */
        section[data-testid="stSidebar"] {
            max-width: 85% !important;
        }
        
        /* Labels de sidebar más compactos */
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            font-size: 15px !important;
        }
        
        /* ===== TIPOGRAFÍA MÓVIL ===== */
        
        /* Títulos escalables */
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.3 !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
            line-height: 1.3 !important;
        }
        
        h4 {
            font-size: 1.1rem !important;
        }
        
        /* Párrafos legibles */
        p {
            font-size: 16px !important;
            line-height: 1.6 !important;
        }
        
        /* ===== COLUMNAS RESPONSIVE ===== */
        
        /* Forzar columnas en stack vertical */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        
        .stColumn {
            width: 100% !important;
            min-width: 100% !important;
            margin-bottom: 1rem !important;
        }
        
        /* ===== EXPANDERS ===== */
        
        .streamlit-expanderHeader {
            font-size: 15px !important;
            padding: 12px 16px !important;
        }
        
        /* ===== ALERTAS Y MENSAJES ===== */
        
        .stAlert {
            font-size: 15px !important;
            padding: 12px 16px !important;
        }
    }
    
    /* === MÓVILES PEQUEÑOS (320px - 480px) === */
    
    @media (max-width: 480px) {
        /* Padding mínimo - maximizar espacio */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0.75rem !important;
        }
        
        /* Hero ultra-compacto */
        .hero-banner {
            height: 200px !important;
        }
        
        .hero-banner h1 {
            font-size: 1.5rem !important;
        }
        
        .hero-banner p {
            font-size: 0.875rem !important;
        }
        
        /* Tipografía aún más compacta */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.15rem !important;
        }
        
        /* KPI Values más pequeños pero legibles */
        .kpi-card .kpi-value {
            font-size: 1.4rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        
        /* Botones a ancho completo con padding reducido */
        .stButton button {
            padding: 12px 20px !important;
            font-size: 15px !important;
        }
        
        /* Tablas con fuente más pequeña */
        .responsive-table table {
            font-size: 13px !important;
        }
        
        .responsive-table th,
        .responsive-table td {
            padding: 8px 10px !important;
        }
    }
    
    /* === ORIENTACIÓN LANDSCAPE EN MÓVILES === */
    
    @media (max-width: 767px) and (orientation: landscape) {
        /* Hero mínimo en landscape - priorizar contenido */
        .hero-banner {
            height: 180px !important;
        }
        
        /* Reducir padding vertical */
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }
        
        /* Sidebar más estrecho */
        section[data-testid="stSidebar"] {
            max-width: 70% !important;
        }
        
        /* Métricas en fila si hay espacio */
        [data-testid="stMetric"] {
            margin-bottom: 0.5rem !important;
        }
    }
    
    /* === MEJORAS TÁCTILES (solo dispositivos touch) === */
    
    /* Detectar dispositivos táctiles sin hover */
    @media (hover: none) and (pointer: coarse) {
        /* Eliminar efectos hover - no aplican en táctil */
        .kpi-card:hover,
        .stButton button:hover,
        .dataframe tr:hover,
        button[data-baseweb="tab"]:hover {
            transform: none !important;
            box-shadow: initial !important;
            background-color: initial !important;
        }
        
        /* Feedback táctil con :active */
        .stButton button:active {
            transform: scale(0.98) !important;
            opacity: 0.8 !important;
        }
        
        button[data-baseweb="tab"]:active {
            opacity: 0.7 !important;
        }
        
        /* Tap highlight personalizado (color institucional) */
        * {
            -webkit-tap-highlight-color: rgba(0, 54, 150, 0.2) !important;
        }
        
        /* Links más grandes para touch */
        a {
            padding: 4px 8px !important;
            margin: -4px -8px !important;
        }
    }
    
    /* === ACCESIBILIDAD MÓVIL === */
    
    @media (max-width: 767px) {
        /* Asegurar contraste mínimo en pantallas pequeñas */
        p, span, label, li {
            color: #212529 !important;
            text-shadow: 0 0 1px rgba(0, 0, 0, 0.05); /* Sutil mejora de legibilidad */
        }
        
        /* Focus visible para navegación por teclado (tablets con teclado) */
        *:focus-visible {
            outline: 3px solid #FFB81C !important;
            outline-offset: 2px !important;
        }
    }
    
    /* === SCROLL SUAVE === */
    
    /* Scroll suave en iOS Safari */
    html {
        -webkit-overflow-scrolling: touch !important;
    }
    
    /* Scroll horizontal suave en tablas */
    .responsive-table,
    [data-testid="stDataFrame"] {
        -webkit-overflow-scrolling: touch !important;
    }
    
    /* === FIX PARA TECLADO VIRTUAL === */
    
    @media (max-width: 767px) {
        /* Evitar que inputs queden ocultos tras el teclado virtual */
        input:focus,
        textarea:focus,
        select:focus {
            position: relative !important;
            z-index: 9999 !important;
        }
        
        /* Asegurar que el viewport no se mueva al enfocar inputs */
        body.keyboard-visible {
            position: fixed !important;
            width: 100% !important;
        }
    }
    
    /* === OPTIMIZACIÓN DE CARGA EN MÓVILES === */
    
    @media (max-width: 767px) {
        /* Imágenes responsive */
        img {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* Logo sidebar proporcional */
        .logo-marista {
            max-width: 150px !important;
        }
    }
    
    /* === MODO OSCURO (si el usuario lo prefiere) === */
    
    @media (prefers-color-scheme: dark) and (max-width: 767px) {
        /* Aquí se pueden agregar ajustes para modo oscuro en el futuro */
        /* Por ahora, mantener diseño claro institucional */
    }
    
    </style>
    """
