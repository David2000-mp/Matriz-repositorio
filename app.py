import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, timedelta, datetime
import uuid
import random
import base64
import os

# -------------------------
# 1. CONFIGURACIÓN DEL SISTEMA
# -------------------------
st.set_page_config(
    page_title="Maristas Analytics", 
    layout="wide", 
    page_icon="Ⓜ️",
    initial_sidebar_state="expanded"
)

# Colores Institucionales
COLOR_PRIMARY = "#003696"  # Azul Marista
COLOR_BG = "#F4F6F9"       # Gris muy suave para fondo
COLOR_CARD = "#FFFFFF"     # Blanco puro para tarjetas
COLOR_TEXT = "#212529"     # Gris muy oscuro para texto (casi negro)

# Rutas
DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = Path(__file__).parent / "images"  # Nueva carpeta para imágenes
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CUENTAS_CSV = DATA_DIR / "cuentas.csv"
METRICAS_CSV = DATA_DIR / "metricas.csv"

# Rutas de imágenes (puedes cambiarlas por tus archivos)
LOGO_PATH = IMAGES_DIR / "logo_maristas.png"
BANNER_PATH = IMAGES_DIR / "banner_landing.jpg"
ICON_PATH = IMAGES_DIR / "icon_maristas.png"

# -------------------------
# 2. FUNCIONES HELPER PARA IMÁGENES
# -------------------------
def get_image_base64(image_path: Path) -> str:
    """Convierte una imagen local a base64 para usar en HTML."""
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def load_image(image_path: Path, fallback_url: str = None):
    """Carga una imagen local o usa fallback de URL."""
    if image_path.exists():
        return st.image(str(image_path))
    elif fallback_url:
        return st.image(fallback_url)
    else:
        return None

def get_banner_css(image_path: Path, fallback_url: str = None) -> str:
    """Genera CSS para imagen de fondo."""
    if image_path.exists():
        img_b64 = get_image_base64(image_path)
        return f"background-image: url(data:image/png;base64,{img_b64});"
    elif fallback_url:
        return f"background-image: url('{fallback_url}');"
    return "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"

# -------------------------
# 3. ESTILOS CSS (UI HIGH CONTRAST & BUTTON FIX)
# -------------------------
def inject_custom_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        
        /* --- FORZAR MODO CLARO Y CONTRASTE --- */
        [data-testid="stAppViewContainer"] {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
        }}
        /* Header minimalista - Evitar selectores agresivos */
        [data-testid="stHeader"] {{
            background-color: {COLOR_BG};
        }}
        /* NOTA: Para colores base, usa .streamlit/config.toml:
           [theme]
           primaryColor="#003696"
           backgroundColor="#F4F6F9"
           secondaryBackgroundColor="#FFFFFF"
           textColor="#212529"
        */
        .stApp {{
            font-family: 'Futura', 'Montserrat', 'Century Gothic', -apple-system, sans-serif;
            padding-top: 0 !important;
        }}
        /* Eliminar padding superior del contenedor principal */
        .main .block-container {{
            padding-top: 2rem !important;
        }}
        
        /* --- SIDEBAR MINIMALISTA --- */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_PRIMARY};
            padding-top: 1rem !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem !important;
            margin-top: 0 !important;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        /* Botón colapsar sidebar visible */
        [data-testid="collapsedControl"] {{
            display: block !important;
            visibility: visible !important;
        }}
        button[kind="header"] {{
            display: block !important;
            visibility: visible !important;
        }}
        /* Radio buttons minimalistas en sidebar */
        [data-testid="stSidebar"] .stRadio > label {{
            background-color: transparent !important;
            padding: 10px 15px !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
        }}
        [data-testid="stSidebar"] .stRadio > label:hover {{
            background-color: rgba(255,255,255,0.1) !important;
        }}
        
        /* --- TARJETAS MINIMALISTAS --- */
        .css-card {{
            background-color: {COLOR_CARD};
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 24px;
            border: none;
            color: {COLOR_TEXT} !important;
        }}
        
        /* Forzar texto negro en todos los elementos dentro de tarjetas */
        .css-card * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Excepciones: mantener colores específicos */
        .css-card h1, .css-card h2, .css-card h3 {{
            color: {COLOR_PRIMARY} !important;
        }}
        .css-card button, .css-card button * {{
            color: #FFFFFF !important;
        }}
        
        /* --- BOTONES MINIMALISTAS --- */
        button, 
        .stButton button,
        .stButton > button,
        .stDownloadButton button,
        .stDownloadButton > button,
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-minimal"],
        [data-testid="stFormSubmitButton"] button,
        button[kind="primary"],
        button[kind="secondary"],
        button[kind="tertiary"],
        input[type="button"],
        input[type="submit"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
            padding: 0.65rem 1.5rem !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
            text-transform: uppercase !important;
        }}
        
        /* Hover minimalista */
        button:hover,
        .stButton button:hover,
        .stButton > button:hover,
        .stDownloadButton button:hover,
        .stDownloadButton > button:hover,
        [data-testid="baseButton-primary"]:hover,
        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-minimal"]:hover,
        [data-testid="stFormSubmitButton"] button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        button[kind="tertiary"]:hover {{
            background-color: #002566 !important;
            color: #FFFFFF !important;
            opacity: 0.9 !important;
        }}
        
        /* Estado activo/presionado */
        button:active,
        .stButton button:active,
        .stDownloadButton button:active {{
            background-color: #001a4d !important;
            color: #FFFFFF !important;
            transform: translateY(0) !important;
        }}
        
        /* Texto dentro de botones - forzar blanco */
        button span,
        button p,
        button div,
        .stButton span,
        .stDownloadButton span {{
            color: #FFFFFF !important;
        }}
        
        /* Botón de submit en formularios (extra refuerzo) */
        [data-testid="stFormSubmitButton"] > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            width: 100% !important;
            padding: 0.75rem !important;
            font-size: 16px !important;
            font-weight: 700 !important;
        }}
        [data-testid="stFormSubmitButton"] > button:hover {{
            background-color: #002566 !important;
            color: #FFFFFF !important;
        }}
        
        /* --- KPIs MINIMALISTAS --- */
        [data-testid="stMetric"] {{
            background-color: transparent !important;
            border-radius: 0;
            padding: 20px 10px;
            border: none;
            border-bottom: 2px solid #E5E7EB;
            text-align: center;
            box-shadow: none;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 11px !important;
            color: #6B7280 !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARY} !important;
            font-size: 32px !important;
            font-weight: 300 !important;
            letter-spacing: -1px !important;
        }}
        [data-testid="stMetricDelta"] {{
            color: {COLOR_TEXT} !important;
            font-weight: 600 !important;
        }}
        
        /* --- INPUTS Y SELECTBOX (FIX CONTRASTE) --- */
        .stSelectbox label, .stNumberInput label, .stDateInput label, .stTextInput label {{
            color: {COLOR_TEXT} !important;
            font-weight: 600 !important;
        }}
        .stSelectbox > div > div, .stNumberInput > div > div, .stDateInput > div > div, .stTextInput > div > div {{
            background-color: white !important;
            color: {COLOR_TEXT} !important;
            border: 1px solid #D1D5DB !important;
        }}
        /* Texto dentro de selectbox */
        .stSelectbox [data-baseweb="select"] {{
            background-color: white !important;
        }}
        .stSelectbox [data-baseweb="select"] > div {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        .stSelectbox [data-baseweb="select"] span {{
            color: {COLOR_TEXT} !important;
        }}
        /* Opciones del dropdown */
        [role="listbox"] {{
            background-color: white !important;
        }}
        [role="option"] {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        [role="option"]:hover {{
            background-color: #F3F4F6 !important;
            color: {COLOR_TEXT} !important;
        }}
        
        /* --- FORZAR TEXTO NEGRO EN TODOS LOS INPUTS --- */
        input, textarea, select {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        
        /* Sliders y otros controles */
        .stSlider label {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Date picker */
        .stDateInput input {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Number input */
        .stNumberInput input {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Text input */
        .stTextInput input {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* --- JERARQUÍA TIPOGRÁFICA PROFESIONAL --- */
        /* H1: ExtraBold (800) - Títulos Principales */
        h1 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 800 !important; 
            font-size: 2.5rem !important;
            letter-spacing: 2px !important;
            margin-bottom: 0.5rem !important;
            text-transform: uppercase !important;
        }}
        
        /* H2: Bold (700) - Subtítulos de Sección */
        h2 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 700 !important; 
            font-size: 2rem !important;
            letter-spacing: 1.5px !important;
            margin-bottom: 1rem !important;
        }}
        
        /* H3: SemiBold (600) - Subtítulos de Subsección */
        h3 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 600 !important; 
            font-size: 1.5rem !important;
            letter-spacing: 1px !important;
            margin-bottom: 0.75rem !important;
        }}
        
        /* H4: Medium (500) - Títulos de Tarjetas */
        h4 {{
            color: {COLOR_TEXT} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
        }}
        
        /* Body Text: Regular (400) */
        p, li, span, div, label {{ 
            color: {COLOR_TEXT} !important;
            font-weight: 400 !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }}
        
        /* Captions: Light (300) */
        .stCaption {{
            color: #6B7280 !important;
            font-size: 0.875rem !important;
            font-weight: 300 !important;
            letter-spacing: 0.5px !important;
        }}
        
        /* --- REGLAS GLOBALES DE CONTRASTE --- */
        /* Forzar texto negro en TODOS los componentes de Streamlit */
        [data-testid*="st"] {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Mensajes de info, warning, success, error */
        .stAlert {{
            background-color: white !important;
        }}
        .stAlert * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Expandir/Colapsar */
        .streamlit-expanderHeader {{
            background-color: white !important;
            color: {COLOR_TEXT} !important;
        }}
        
        /* Markdown content */
        .stMarkdown {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* --- TABLAS --- */
        [data-testid="stDataFrame"] {{
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            background-color: white;
        }}
        [data-testid="stDataFrame"] * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* Data Editor */
        [data-testid="data-grid-canvas"] {{
            background-color: white !important;
        }}
        [data-testid="data-grid-canvas"] * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* --- TABS MINIMALISTAS --- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: white !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: white !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            padding: 12px 20px !important;
        }}
        
        /* CORRECCIÓN: Forzar color de texto específico dentro de los tabs */
        .stTabs [data-baseweb="tab"] p, 
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div {{
            color: #6B7280 !important; /* Gris para tabs inactivos */
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            font-size: 0.85rem !important;
        }}

        .stTabs [data-baseweb="tab"]:hover p,
        .stTabs [data-baseweb="tab"]:hover span {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(0, 54, 150, 0.05) !important;
        }}

        /* CORRECCIÓN: Tab activo con texto azul */
        .stTabs [aria-selected="true"] {{
            border-bottom-color: {COLOR_PRIMARY} !important;
            background-color: white !important;
        }}
        
        .stTabs [aria-selected="true"] p, 
        .stTabs [aria-selected="true"] span,
        .stTabs [aria-selected="true"] div {{
            color: {COLOR_PRIMARY} !important; /* Azul para tab activo */
        }}
        
        /* Contenido de tabs */
        [data-testid="stTabContent"] {{
            background-color: white !important;
        }}
        [data-testid="stTabContent"] * {{
            color: {COLOR_TEXT} !important;
        }}
        [data-testid="stTabContent"] h1, 
        [data-testid="stTabContent"] h2, 
        [data-testid="stTabContent"] h3 {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        /* --- LANDING PAGE MINIMALISTA --- */
        .hero-banner {{
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            margin: -2rem -6rem 0 -6rem;
            padding: 0;
            width: calc(100% + 12rem);
            min-height: 100vh;
            text-align: center;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hero-banner::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(0, 54, 150, 0.7) 0%, rgba(0, 0, 0, 0.5) 100%);
            z-index: 1;
        }}
        .hero-content {{
            position: relative;
            z-index: 2;
            color: white !important;
            padding: 40px;
        }}
        .hero-content h1, .hero-content p {{
            color: white !important;
            font-weight: 300 !important;
            letter-spacing: 2px !important;
        }}
        
        /* Contador animado de seguidores */
        .followers-counter {{
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            color: white !important;
            text-shadow: 2px 2px 20px rgba(0,0,0,0.4);
            letter-spacing: 3px !important;
            margin-top: 20px;
            animation: fadeInUp 1s ease-out;
        }}
        .followers-label {{
            font-size: 1rem !important;
            font-weight: 300 !important;
            color: rgba(255,255,255,0.9) !important;
            letter-spacing: 3px !important;
            text-transform: uppercase;
        }}
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Ocultar elementos nativos */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# -------------------------
# 3. LÓGICA DE NEGOCIO Y DATOS
# -------------------------

COLS_CUENTAS = ["id_cuenta", "entidad", "plataforma", "usuario_red"]
COLS_METRICAS = ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]

COLOR_MAP = {
    "Facebook": "#1877F2", "Instagram": "#E1306C", "TikTok": "#000000",
    "Twitter/X": "#1DA1F2", "LinkedIn": "#0A66C2", "YouTube": "#FF0000"
}

# Catálogo Maestro
COLEGIOS_MARISTAS = {
    "Centro Universitario México": {"Facebook": "maristascum", "Instagram": "@maristas_cum", "TikTok": "@maristascum"},
    "Colegio México Bachillerato": {"Facebook": "colegio.mexico.bachillerato", "Instagram": "@cmbacoxpa", "TikTok": "@cmbacoxpa"},
    "Instituto México Secundaria": {"Facebook": "InstitutoMexicoSecundaria", "Instagram": "@institutomexicosecundaria"},
    "Instituto México Primaria": {"Facebook": "imprimaria", "Instagram": "@institutomexicoprimaria"},
    "Colegio México (Roma)": {"Facebook": "ColegioMexicoRoma", "Instagram": "@institutomexicosecundaria"},
    "Instituto México Toluca": {"Facebook": "InstitutoMexicodeToluca", "Instagram": "@imt.secuprepa"},
    "Instituto Hidalguense": {"Facebook": "MaristasIH", "Instagram": "@maristas_ih"},
    "Colegio México Orizaba": {"Facebook": "cmoriedu", "Instagram": "@cmoriedu"},
    "Instituto Potosino": {"Facebook": "Oficialpotosino", "Instagram": "@institutopotosino"},
    "Instituto Queretano San Javier": {"Facebook": "MaristaSanJavier", "Instagram": "@iqm_qro"},
    "Colegio Lic. Manuel Concha": {"Facebook": "ColegioManuelConcha", "Instagram": "@marista_celaya"},
    "Colegio Pedro Martínez Vázquez": {"Facebook": "maristasirapuato", "Instagram": "@maristasirapuato"},
    "Colegio Jacona": {"Facebook": "CJMarista", "Instagram": "@maristas_jacona"},
    "Instituto Sahuayense": {"Instagram": "@sahuayensemarista"},
    "Universidad Marista de México": {"Facebook": "umaristamx", "Instagram": "@umarista_mx", "TikTok": "@umarista"},
    "Universidad Marista de Querétaro": {"Instagram": "@umaristaqro", "Facebook": "umqro"},
    "Universidad Marista SLP": {"Instagram": "@universidadmaristaslp", "Facebook": "umaslp"}
}

def init_files():
    if not CUENTAS_CSV.exists(): pd.DataFrame(columns=COLS_CUENTAS).to_csv(CUENTAS_CSV, index=False)
    if not METRICAS_CSV.exists(): pd.DataFrame(columns=COLS_METRICAS).to_csv(METRICAS_CSV, index=False)

def load_data():
    init_files()
    try:
        c = pd.read_csv(CUENTAS_CSV, dtype=str)
        m = pd.read_csv(METRICAS_CSV)
        if not m.empty:
            m['fecha'] = pd.to_datetime(m['fecha'], errors='coerce')
            for col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']:
                m[col] = pd.to_numeric(m[col], errors='coerce').fillna(0)
        return c, m
    except:
        return pd.DataFrame(columns=COLS_CUENTAS), pd.DataFrame(columns=COLS_METRICAS)

def save_batch(datos):
    with st.spinner('Guardando datos...'):
        _, df_m = load_data()
        new = pd.DataFrame(datos)
        new['engagement_rate'] = new.apply(lambda x: round((x['interacciones']/x['seguidores']*100), 2) if x['seguidores']>0 else 0, axis=1)
        
        if not df_m.empty and not new.empty:
            df_m['k'] = df_m['id_cuenta'] + df_m['fecha'].dt.strftime('%Y-%m-%d')
            new['k'] = new['id_cuenta'] + pd.to_datetime(new['fecha']).dt.strftime('%Y-%m-%d')
            df_m = df_m[~df_m['k'].isin(new['k'])].drop(columns=['k'])
            new = new.drop(columns=['k'])
            
        pd.concat([df_m, new], ignore_index=True).to_csv(METRICAS_CSV, index=False)
        st.cache_data.clear()

def get_id(entidad, plat, user):
    c, _ = load_data()
    exist = c[(c['entidad'] == entidad) & (c['plataforma'] == plat)]
    if not exist.empty: return exist.iloc[0]['id_cuenta']
    nid = uuid.uuid4().hex
    pd.concat([c, pd.DataFrame([{"id_cuenta": nid, "entidad": entidad, "plataforma": plat, "usuario_red": user}])]).to_csv(CUENTAS_CSV, index=False)
    return nid

def simular(meses=6):
    with st.spinner(f'Generando {meses} meses de datos de prueba...'):
        d = []
        fechas = [date.today() - timedelta(days=30*i) for i in range(meses)][::-1]
        
    for e, redes in COLEGIOS_MARISTAS.items():
        for p, u in redes.items():
            cid = get_id(e, p, u)
            if p == "TikTok": base, growth, er_rng = 5000, 0.15, (0.05, 0.15)
            elif p == "Instagram": base, growth, er_rng = 2000, 0.05, (0.02, 0.07)
            else: base, growth, er_rng = 8000, 0.01, (0.005, 0.03)
            curr = base
            for f in fechas:
                curr = int(curr * (1 + random.uniform(0, growth)))
                er = random.uniform(*er_rng)
                inter = int(curr * er)
                alc = int(inter * random.uniform(3, 8))
                d.append({"id_cuenta": cid, "fecha": f, "seguidores": curr, "alcance": alc, "interacciones": inter, "likes_promedio": int(inter/20)})
    
    # CORRECCIÓN: El return está ahora fuera de los bucles for
    return d

def reset_db():
    if CUENTAS_CSV.exists(): os.remove(CUENTAS_CSV)
    if METRICAS_CSV.exists(): os.remove(METRICAS_CSV)
    st.cache_data.clear()

# -------------------------
# 4. REPORTES HTML
# -------------------------
def generar_reporte_html(df_mes, mes):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica', sans-serif; padding: 40px; color: #333; }}
            h1 {{ color: #003696; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #003696; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .kpi-box {{ display: inline-block; width: 30%; background: #eee; padding: 20px; margin: 1%; text-align: center; border-radius: 8px; }}
            .kpi-val {{ font-size: 24px; font-weight: bold; color: #003696; }}
        </style>
    </head>
    <body>
        <div style="text-align:center;">
            <h1>Reporte Mensual Maristas Analytics</h1>
            <h3>Periodo: {mes}</h3>
        </div>
        <hr>
        <div style="margin: 30px 0;">
            <div class="kpi-box">Seguidores Totales<br><span class="kpi-val">{df_mes['seguidores'].sum():,.0f}</span></div>
            <div class="kpi-box">Interacciones<br><span class="kpi-val">{df_mes['interacciones'].sum():,.0f}</span></div>
            <div class="kpi-box">Instituciones<br><span class="kpi-val">{df_mes['entidad'].nunique()}</span></div>
        </div>
        
        <h2>Detalle por Institución y Plataforma</h2>
        {df_mes[['entidad', 'plataforma', 'seguidores', 'interacciones', 'engagement_rate']].sort_values(['entidad', 'seguidores'], ascending=False).to_html(index=False)}
        
        <br>
        <p><i>Generado automáticamente por Maristas Analytics</i></p>
    </body>
    </html>
    """
    return html.encode('utf-8')

# -------------------------
# 5. PÁGINAS UI
# -------------------------

def page_dashboard():
    st.title("DASHBOARD GLOBAL")
    st.caption("Red Marista • Análisis Consolidado")
    
    cuentas, metricas = load_data()
    if metricas.empty:
        st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
        return

    df = pd.merge(metricas, cuentas, on="id_cuenta")
    
    # --- FILTROS ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: 
        st.markdown("#### Periodo de Análisis")
    with c2: 
        fechas = df['fecha'].dropna().dt.strftime('%Y-%m').unique()
        mes = st.selectbox("Mes", sorted(fechas, reverse=True), label_visibility="collapsed")
    with c3:
        df_m = df[df['fecha'].dt.strftime('%Y-%m') == mes]
        st.download_button("Descargar Reporte", generar_reporte_html(df_m, mes), f"Reporte_{mes}.html", "text/html")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- KPIs con Crecimiento MoM ---
    tot_seg = df_m['seguidores'].sum()
    tot_int = df_m['interacciones'].sum()
    er_global = (tot_int / tot_seg * 100) if tot_seg > 0 else 0
    
    # Calcular mes anterior para MoM
    fechas_disponibles = sorted(df['fecha'].dropna().dt.strftime('%Y-%m').unique(), reverse=True)
    mes_anterior = fechas_disponibles[1] if len(fechas_disponibles) > 1 else None
    
    if mes_anterior:
        df_prev = df[df['fecha'].dt.strftime('%Y-%m') == mes_anterior]
        seg_prev = df_prev['seguidores'].sum()
        int_prev = df_prev['interacciones'].sum()
        delta_seg = ((tot_seg - seg_prev) / seg_prev * 100) if seg_prev > 0 else 0
        delta_int = ((tot_int - int_prev) / int_prev * 100) if int_prev > 0 else 0
    else:
        delta_seg, delta_int = 0, 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seguidores Totales", f"{tot_seg:,.0f}", delta=f"{delta_seg:+.1f}% vs mes anterior" if mes_anterior else "Red Marista")
    c2.metric("Interacciones Totales", f"{tot_int:,.0f}", delta=f"{delta_int:+.1f}%" if mes_anterior else None)
    c3.metric("Engagement Rate", f"{er_global:.2f}%")
    c4.metric("Colegios Reportando", df_m['entidad'].nunique())
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    t1, t2 = st.tabs(["Visión Global", "Ranking Institucional"])
    
    with t1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c_left, c_right = st.columns([1, 2])
        with c_left:
            st.markdown("#### Distribución por Plataforma")
            fig = px.pie(df_m, values='seguidores', names='plataforma', 
                         color='plataforma', color_discrete_map=COLOR_MAP, hole=0.7) # Agujero más grande = más moderno
            
            fig.update_traces(
                textposition='outside', # Etiquetas por fuera para no ensuciar el color
                textinfo='percent+label', # Mostrar qué es y el %
                hoverinfo='label+percent+value',
                marker=dict(line=dict(color='#FFFFFF', width=2)), # Borde blanco para separar rebanadas
                textfont=dict(color='#000000', size=14, family='Montserrat') # Texto negro
            )
            
            fig.update_layout(
                showlegend=True, # Mostrar leyenda para explicar colores
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(family="Montserrat", size=13, color='#000000'),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(color='#000000', size=12)
                ),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Montserrat",
                    font_color="#000000"
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with c_right:
            st.markdown("#### Tendencia de Crecimiento")
            df_evo = df.groupby(['fecha', 'plataforma'])['seguidores'].sum().reset_index()
            
            fig = px.area(df_evo, x='fecha', y='seguidores', color='plataforma', 
                          color_discrete_map=COLOR_MAP)
            
            fig.update_layout(
                plot_bgcolor='#FFFFFF', 
                paper_bgcolor='#FFFFFF',
                margin=dict(t=10, b=0, l=0, r=0), 
                template='plotly_white',
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#E5E7EB', 
                    side="right",
                    tickfont=dict(color='#000000', size=12)
                ),
                xaxis=dict(
                    tickformat="%b %d",
                    showgrid=False,
                    title=None,
                    tickfont=dict(color='#000000', size=12)
                ),
                legend=dict(
                    orientation="h", 
                    y=1.1, 
                    x=0,
                    font=dict(color='#000000', size=12),
                    title=dict(text="Plataformas:", font=dict(color='#000000', size=13, family='Montserrat'))
                ),
                hovermode='x unified',
                font=dict(family="Montserrat", size=12, color='#000000'),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Montserrat",
                    font_color="#000000"
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c_h1, c_h2 = st.columns([3, 1])
        with c_h1: st.markdown("#### Comparativa por Institución")
        with c_h2: metric_sort = st.selectbox("Ordenar por", ["seguidores", "engagement_rate"])
        
        # CAMBIO: Barras horizontales para evitar textos encimados en el eje X
        fig = px.bar(df_m.sort_values(metric_sort, ascending=True), # Ordenamos para que el mejor quede arriba
                     x=metric_sort, 
                     y="entidad", # Nombres en el eje Y
                     color="plataforma", 
                     orientation='h', # <--- CLAVE: Orientación Horizontal
                     barmode="group", 
                     color_discrete_map=COLOR_MAP, 
                     text_auto='.2s') # Formato corto (ej: 1.5k en vez de 1500)

        fig.update_traces(
            textposition='outside', # Saca los números de las barras para que se lean mejor
            marker=dict(line=dict(width=0)),
            textfont=dict(color='#000000', size=11)
        )
        
        fig.update_layout(
            height=600, # <--- CLAVE: Dar más altura fija para que respiren las barras
            plot_bgcolor='#FFFFFF', 
            paper_bgcolor='#FFFFFF', 
            template='plotly_white', 
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis=dict(
                showgrid=True, 
                gridcolor='#E5E7EB', 
                title=None,
                tickfont=dict(color='#000000', size=12)
            ),
            yaxis=dict(
                title=None, 
                tickfont=dict(size=12, color='#000000')
            ),
            legend=dict(
                orientation="h", 
                y=1.02, 
                x=0, 
                title=dict(text="Plataformas:", font=dict(color='#000000', size=13, family='Montserrat')),
                font=dict(color='#000000', size=12)
            ),
            font=dict(family="Montserrat", size=12, color='#000000'),
            hovermode='y unified', # Muestra todos los datos de esa fila al pasar el mouse
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

def page_analisis_detalle():
    st.title("ANÁLISIS INDIVIDUAL")
    st.caption("Vista Detallada por Institución")
    
    cuentas, metricas = load_data()
    if cuentas.empty or metricas.empty:
        st.warning("No hay datos disponibles.")
        return
        
    df = pd.merge(metricas, cuentas, on="id_cuenta")
    
    # Selector de Colegio
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1: 
        lista_colegios = sorted(df['entidad'].unique())
        entidad = st.selectbox("Seleccionar Institución", lista_colegios)
    with c2:
        st.info("Visualizando histórico completo")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrar datos del colegio
    df_e = df[df['entidad'] == entidad].sort_values("fecha")
    
    if df_e.empty:
        st.warning("Este colegio no tiene datos registrados aún.")
        return

    # KPIs del último mes disponible
    last_date = df_e['fecha'].max()
    df_last = df_e[df_e['fecha'] == last_date]
    
    st.markdown(f"### Resultados al cierre de {last_date.strftime('%Y-%m')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Seguidores Totales", f"{df_last['seguidores'].sum():,.0f}")
    col2.metric("Interacciones (Mes)", f"{df_last['interacciones'].sum():,.0f}")
    
    er_e = (df_last['interacciones'].sum() / df_last['seguidores'].sum() * 100) if df_last['seguidores'].sum() > 0 else 0
    col3.metric("Engagement Promedio", f"{er_e:.2f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficas Individuales
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    tab_a, tab_b = st.tabs(["Evolución de Seguidores", "Evolución de Engagement"])
    
    with tab_a:
        fig = px.line(df_e, x="fecha", y="seguidores", color="plataforma", 
                      color_discrete_map=COLOR_MAP, markers=True, title="Crecimiento de Audiencia")
        fig.update_traces(line=dict(width=3), marker=dict(size=10, line=dict(width=2, color='white')))
        fig.update_layout(
            plot_bgcolor='#FFFFFF', 
            paper_bgcolor='#FFFFFF',
            template='plotly_white', 
            font=dict(size=13, color='#000000'),
            title=dict(font=dict(color='#000000', size=16)),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#E5E7EB',
                tickfont=dict(color='#000000')
            ),
            xaxis=dict(tickfont=dict(color='#000000')),
            hovermode='x unified', 
            legend=dict(
                orientation='h', 
                y=1.15,
                title=dict(text="Plataformas:", font=dict(color='#000000', size=13)),
                font=dict(color='#000000', size=12)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    with tab_b:
        fig = px.line(df_e, x="fecha", y="engagement_rate", color="plataforma", 
                      color_discrete_map=COLOR_MAP, markers=True, title="Calidad de Interacción (%)")
        fig.update_traces(line=dict(width=3, dash='dot'), marker=dict(size=10, symbol='diamond', line=dict(width=2, color='white')))
        fig.update_layout(
            plot_bgcolor='#FFFFFF', 
            paper_bgcolor='#FFFFFF',
            template='plotly_white', 
            font=dict(size=13, color='#000000'),
            title=dict(font=dict(color='#000000', size=16)),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#E5E7EB', 
                range=[0, 20],
                tickfont=dict(color='#000000')
            ),
            xaxis=dict(tickfont=dict(color='#000000')),
            hovermode='x unified', 
            legend=dict(
                orientation='h', 
                y=1.15,
                title=dict(text="Plataformas:", font=dict(color='#000000', size=13)),
                font=dict(color='#000000', size=12)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabla de Datos
    with st.expander("Ver Datos Crudos"):
        st.dataframe(df_e[['fecha', 'plataforma', 'seguidores', 'interacciones', 'engagement_rate']].sort_values('fecha', ascending=False), use_container_width=True)

def page_captura():
    st.title("CAPTURA DE DATOS")
    st.caption("Registro de Métricas")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    entidad = c1.selectbox("Seleccionar Colegio", sorted(COLEGIOS_MARISTAS.keys()))
    fecha = c2.date_input("Fecha de Cierre", date.today())
    st.markdown('</div>', unsafe_allow_html=True)
    
    redes = COLEGIOS_MARISTAS[entidad]
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.info("✏️ Edita la tabla directamente. Puedes copiar y pegar desde Excel.")
    
    # Crear DataFrame para edición
    data_template = pd.DataFrame([
        {"Plataforma": plat, "Usuario": user, "Seguidores": 0, "Alcance": 0, "Interacciones": 0, "Posts del Mes": 1}
        for plat, user in redes.items()
    ])
    
    # Editor interactivo
    edited_data = st.data_editor(
        data_template,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Plataforma": st.column_config.TextColumn("Plataforma", disabled=True),
            "Usuario": st.column_config.TextColumn("Usuario", disabled=True),
            "Seguidores": st.column_config.NumberColumn("Seguidores", min_value=0, format="%d"),
            "Alcance": st.column_config.NumberColumn("Alcance", min_value=0, format="%d"),
            "Interacciones": st.column_config.NumberColumn("Interacciones", min_value=0, format="%d"),
            "Posts del Mes": st.column_config.NumberColumn("Posts", min_value=1, format="%d", help="Número de publicaciones en el mes")
        },
        hide_index=True
    )
    
    if st.button("Guardar Datos", type="primary", use_container_width=True):
        batch = []
        for _, row in edited_data.iterrows():
            if row['Seguidores'] > 0:
                batch.append({
                    "id_cuenta": get_id(entidad, row['Plataforma'], row['Usuario']),
                    "fecha": fecha,
                    "seguidores": int(row['Seguidores']),
                    "alcance": int(row['Alcance']),
                    "interacciones": int(row['Interacciones']),
                    "likes_promedio": int(row['Interacciones'] / row['Posts del Mes']) if row['Posts del Mes'] > 0 else 0
                })
        
        if batch:
            save_batch(batch)
            st.success("✓ Datos guardados correctamente.")
        else:
            st.warning("⚠ No hay datos para guardar. Asegúrate de ingresar al menos seguidores.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_settings():
    st.title("CONFIGURACIÓN")
    st.caption("Herramientas y Ajustes")
    
    tab1, tab2 = st.tabs(["Simulador de Datos", "Administrar Colegios"])
    
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("#### Generador de Datos de Prueba")
        sl = st.slider("Meses a generar", 1, 12, 6)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Generar Datos Demo", use_container_width=True):
                save_batch(simular(sl))
                st.success("✓ Datos de prueba generados correctamente.")
        with c2:
            if st.button("Resetear Base de Datos", use_container_width=True):
                reset_db()
                st.warning("⚠ Base de datos reseteada.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("#### Catálogo de Instituciones")
        st.caption("Vista de colegios configurados en el sistema")
        
        # Convertir diccionario a DataFrame para visualización
        colegios_data = []
        for colegio, redes in COLEGIOS_MARISTAS.items():
            colegios_data.append({
                "Institución": colegio,
                "Facebook": redes.get("Facebook", "-"),
                "Instagram": redes.get("Instagram", "-"),
                "TikTok": redes.get("TikTok", "-")
            })
        
        df_colegios = pd.DataFrame(colegios_data)
        st.dataframe(df_colegios, use_container_width=True, hide_index=True)
        
        st.info("💡 Próxima versión: Podrás agregar y editar colegios directamente desde aquí.")
        st.markdown('</div>', unsafe_allow_html=True)

def page_landing():
    # Hero Banner Minimalista Full-Screen
    banner_css = get_banner_css(
        BANNER_PATH, 
        "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1920"
    )
    
    # Calcular total de seguidores actuales
    cuentas, metricas = load_data()
    total_seguidores = 0
    if not metricas.empty:
        df = pd.merge(metricas, cuentas, on="id_cuenta")
        # Obtener la fecha más reciente
        ultima_fecha = df['fecha'].max()
        df_actual = df[df['fecha'] == ultima_fecha]
        total_seguidores = int(df_actual['seguidores'].sum())
    
    st.markdown(f'''
        <div class="hero-banner" style="{banner_css}">
            <div class="hero-content" style="max-width: 900px;">
                <h1 style="font-size: 7rem; margin-bottom: 30px; letter-spacing: 10px; text-shadow: 2px 2px 20px rgba(0,0,0,0.4); font-weight: 900;">
                    CHAMPILYTICS
                </h1>
                <p style="font-size: 1.2rem; margin-bottom: 20px; opacity: 0.9; text-shadow: 1px 1px 10px rgba(0,0,0,0.3); letter-spacing: 4px; font-weight: 300;">
                    INTELIGENCIA DIGITAL MARISTA
                </p>
                <div class="followers-counter">
                    {total_seguidores:,}
                </div>
                <div class="followers-label" style="margin-bottom: 60px;">
                    Seguidores Totales
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Sección de botones minimalista
    st.markdown("<div style='margin-top: -80px; position: relative; z-index: 10; max-width: 900px; margin-left: auto; margin-right: auto;'>", unsafe_allow_html=True)
    st.markdown('''
        <div style="background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); border-radius: 0; padding: 50px 60px; box-shadow: 0 4px 30px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; margin-bottom: 40px; color: #003696; font-size: 1.1rem; font-weight: 400; letter-spacing: 3px; text-transform: uppercase;">Navegar</h2>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: -30px;'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Dashboard", key="btn_dash", use_container_width=True):
            st.session_state.page = "Dashboard Global"
            st.rerun()
    
    with col2:
        if st.button("Captura", key="btn_cap", use_container_width=True):
            st.session_state.page = "Captura de Datos"
            st.rerun()
    
    with col3:
        if st.button("Análisis", key="btn_ana", use_container_width=True):
            st.session_state.page = "Análisis Individual"
            st.rerun()
    
    with col4:
        if st.button("Configuración", key="btn_cfg", use_container_width=True):
            st.session_state.page = "Configuración"
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPIs minimalistas (removidos - usar landing page para stats)

# -------------------------
# 6. MAIN
# -------------------------
def main():
    inject_custom_css()
    with st.sidebar:
        # Logo minimalista solo texto
        st.markdown("""
            <div style='text-align: center; padding: 25px 20px; border-bottom: 1px solid rgba(255,255,255,0.2);'>
                <h1 style='margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 3px;'>CHAMPILYTICS</h1>
                <p style='margin: 5px 0 0 0; font-size: 0.75rem; opacity: 0.7; letter-spacing: 2px;'>MARISTAS</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Sincronizar navegación con session_state
        if "page" not in st.session_state:
            st.session_state.page = "Inicio"
        
        st.markdown("<h3 style='text-align:center; color:white; margin-top: 10px;'>MENÚ PRINCIPAL</h3>", unsafe_allow_html=True)
        page = st.radio("Navegación", ["Inicio", "Dashboard Global", "Análisis Individual", "Captura de Datos", "Configuración"], 
                       index=["Inicio", "Dashboard Global", "Análisis Individual", "Captura de Datos", "Configuración"].index(st.session_state.page),
                       label_visibility="collapsed")
        
        # Actualizar session_state si el usuario cambió la página desde el radio
        if page != st.session_state.page:
            st.session_state.page = page
            st.rerun()
        
        st.markdown("---")
        st.caption("v12.0 • UX Enhanced")

    # Usar session_state.page para renderizar
    if st.session_state.page == "Inicio": page_landing()
    elif st.session_state.page == "Dashboard Global": page_dashboard()
    elif st.session_state.page == "Análisis Individual": page_analisis_detalle()
    elif st.session_state.page == "Captura de Datos": page_captura()
    elif st.session_state.page == "Configuración": page_settings()

if __name__ == "__main__":
    main()