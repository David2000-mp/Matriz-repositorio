"""
Vista de Landing Page para CHAMPILEAKS.
Página de inicio con hero banner y navegación rápida.
"""

import streamlit as st
import pandas as pd
import logging
from pathlib import Path
from utils.data_provider import data_provider
from utils import simular, save_batch
from utils.helpers import get_banner_css
from utils.analytics import summarize_followers_growth


def render(df=None):
    """
    Renderiza la página de inicio con banner hero y navegación rápida.

    Acepta un parámetro `df` por compatibilidad con el enrutador.
    """

    # Hero Banner Institucional con altura responsiva y overlay optimizado
    banner_css = get_banner_css("banner_landing.jpg")

    # Video de fondo para el hero
    import base64
    base_dir = Path(__file__).resolve().parent.parent
    video_path = base_dir / "images" / "banner_video.mp4"

    def get_video_base64(video_path):
        if video_path.exists():
            with open(video_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        logging.warning(f"Video de banner no encontrado: {video_path}")
        return None
    video_b64 = get_video_base64(video_path)

    # Calcular total de seguidores actuales y delta vs mes anterior
    cuentas, metricas = data_provider.get_data()
    total_seguidores = 0
    delta_pct = 0.0
    breakdown_text = ""

    # Verificar si hay datos válidos
    datos_validos = False
    if not metricas.empty and not cuentas.empty:
        try:
            df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
            for logical in ("entidad", "plataforma", "usuario_red"):
                if logical in df.columns:
                    continue
                for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
                    if suff in df.columns:
                        ser = df.loc[:, suff]
                        if isinstance(ser, pd.DataFrame):
                            ser = ser.squeeze()
                        df[logical] = ser
                        break
                else:
                    df[logical] = "Unknown"
            if "entidad" in df.columns and not df["entidad"].isna().all():
                if "fecha" in df.columns:
                    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                    resumen = summarize_followers_growth(df)
                    total_seguidores = resumen["total"]
                    delta_pct = resumen["delta_pct"]
                    snapshot = resumen["snapshot"]
                    platform_breakdown = snapshot.groupby("plataforma")["seguidores"].sum()
                    breakdown_parts = []
                    for platform, followers in platform_breakdown.items():
                        breakdown_parts.append(f"{platform}: {int(followers):,}")
                    breakdown_text = " | ".join(breakdown_parts)
                    datos_validos = total_seguidores > 0
                    logging.info(f"Landing - Seguidores totales: {total_seguidores:,}, Delta: {delta_pct:.1f}%")
        except Exception as e:
            logging.warning(f"Error calculando seguidores en landing: {e}")

    # Colores institucionales Marista
    PRIMARY_BLUE = "#003696"
    PRIMARY_BLUE_DARK = "#00235A"
    ACCENT_YELLOW = "#FFB81C"
    TEXT_ON_DARK = "#FFFFFF"
    TEXT_ON_LIGHT = "#212529"
    DELTA_POSITIVE = "#0A7D35"
    DELTA_NEGATIVE = "#B42318"

    try:
        theme = st.get_option("theme.base") or "light"
        is_dark = theme == "dark"
    except:
        is_dark = False

    card_bg = f"rgba(0, 54, 150, 0.85)" if is_dark else f"rgba(0, 54, 150, 0.9)"
    card_hover_bg = f"rgba(255, 184, 28, 0.95)"
    metrics_bg = "rgba(255, 255, 255, 0.95)" if is_dark else "rgba(255, 255, 255, 0.98)"

    # BLOQUE DE ESTILOS UNIFICADO
   # ------------------------------------------------------------------------
    # BLOQUE DE ESTILOS DEFINITIVO (Video 50% + Fix Barra Superior)
    # ------------------------------------------------------------------------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Tipografía de la landing, aislada del sidebar y sus Material Symbols. */
    section[data-testid="stMain"],
    section[data-testid="stMain"] .stMarkdown,
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4,
    section[data-testid="stMain"] h5,
    section[data-testid="stMain"] h6,
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] span:not([data-testid="stIconMaterial"]) {
        font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
    }

    /* -------------------------------------------
       1. ESTILOS DE VIDEO Y CONTENIDO (50% IZQUIERDA)
       ------------------------------------------- */
    
    /* ANIMACIONES PERSONALIZADAS PARA GLASS-BOX */
    @keyframes glassBoxEnter {
        0% {
            opacity: 0;
            transform: translateY(40px);
        }
        100% {
            opacity: 1;
            transform: translateY(0px);
        }
    }
    
    @keyframes glassBoxFloat {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-15px);
        }
    }
    
    @keyframes glassBoxGlow {
        0%, 100% {
            box-shadow: 0 8px 32px 0 rgba(31,38,135,0.18),
                        inset 0 0 20px rgba(255,184,28,0);
            border-color: rgba(255,255,255,0.28);
        }
        50% {
            box-shadow: 0 12px 42px 0 rgba(31,38,135,0.25),
                        inset 0 0 30px rgba(255,184,28,0.08),
                        0 0 30px rgba(255,184,28,0.2);
            border-color: rgba(255,184,28,0.4);
        }
    }
    
    .hero-bg-video {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;           /* Forzamos 50% para que sea pantalla dividida */
        height: 100vh;
        object-fit: cover;
        z-index: 0;
        pointer-events: none;
        margin-left: 0 !important;
    }

    .hero-overlay {
        position: relative;
        z-index: 2;
        width: 50%;           /* El texto también ocupa solo el 50% */
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-left: 0;
        padding-left: 0;
        perspective: 1200px;
    }

    .glass-box {
        position: relative;
        z-index: 3;
        background: rgba(7, 27, 51, 0.4) !important;
        backdrop-filter: blur(16px) saturate(120%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        border-radius: 20px !important;
        width: fit-content !important;
        max-width: calc(100vw - 2rem) !important;
        padding: clamp(1.5rem, 3vw, 2.5rem) !important;
        color: #FFFFFF !important;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        animation: glassBoxEnter 0.8s ease-out 0.3s both,
                   glassBoxFloat 4s ease-in-out 1.1s infinite,
                   glassBoxGlow 5s ease-in-out 1.1s infinite;
        transition: transform 0.1s ease-out, box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
        overflow: hidden;
        cursor: grab;
        touch-action: none;
        user-select: none;
    }

    .glass-box.is-dragging {
        animation: none !important;
        cursor: grabbing;
        box-shadow: 0 20px 52px rgba(0, 0, 0, 0.58),
                    0 0 36px rgba(255, 184, 28, 0.36) !important;
        border-color: rgba(255, 184, 28, 0.7) !important;
    }

    .glass-box h1,
    .glass-box h2,
    .glass-box h3,
    .glass-box p,
    .glass-box span {
        color: #FFFFFF !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }

    /* Jerarquía tipográfica de la consola de inteligencia. */
    .glass-box .hero-title {
        font-size: clamp(2rem, 4vw, 3.25rem) !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        letter-spacing: 0.16rem !important;
        margin: 0 0 0.65rem !important;
        white-space: nowrap !important;
        text-shadow: 0 4px 10px rgba(0,0,0,0.6) !important;
        text-transform: uppercase !important;
    }

    .glass-box .hero-subtitle {
        font-size: clamp(0.9rem, 1.8vw, 1.15rem) !important;
        font-weight: 400 !important;
        line-height: 1.35 !important;
        letter-spacing: 0.08rem !important;
        opacity: 0.88 !important;
        margin: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    .glass-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,184,28,0.4) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease-out;
        pointer-events: none;
        z-index: 1;
    }
    
    .glass-box:hover {
        background: rgba(255,255,255,0.25);
        border-color: rgba(255,184,28,0.6);
        box-shadow: 0 16px 48px 0 rgba(31,38,135,0.35),
                    0 0 40px rgba(255,184,28,0.3);
    }
    
    .glass-box:hover::before {
        opacity: 1;
    }

    .hero-title {
        color: #FFB81C;
        font-size: clamp(3rem, 5vw, 6rem); /* Ajustado un poco para que no rompa */
        font-weight: 900;
        letter-spacing: 8px;
        text-shadow: 2px 3px 18px rgba(0,0,0,0.95);
        margin-bottom: 0.7rem;
        text-transform: uppercase;
        line-height: 1.1;
    }

    .hero-subtitle {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 400;
        letter-spacing: 2px;
        margin-top: 0.2rem;
        margin-bottom: 0;
        text-shadow: 1px 2px 8px rgba(0,0,0,0.3);
    }

    /* -------------------------------------------
       2. ELIMINACIÓN DE BORDES Y FRANJA SUPERIOR
       ------------------------------------------- */
    
    /* Header Transparente */
    header[data-testid="stHeader"], .stAppHeader.st-emotion-cache-1s6ol36 {
        background: #001840 !important;
        background-color: #001840 !important;
        background-image: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* La escena de video debe quedar visible bajo el contenido de la landing. */
    .stApp,
    [data-testid="stAppViewContainer"],
    section[data-testid="stMain"],
    section[data-testid="stMain"] > div,
    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    section[data-testid="stMain"] {
        position: relative;
        z-index: 1;
    }

    /* Eliminar Padding del Contenedor Principal */
    [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100vw !important;
        overflow: hidden !important;
    }

    /* EL TRUCO FINAL: Margen negativo para subir todo y tapar el hueco del header */
    .main .block-container {
        margin-top: -65px !important; 
        padding-top: 0 !important;
    }

    /* Ocultar decoración superior (linea de colores) */
    div[data-testid="stDecoration"] {
        display: none;
    }
    
    /* Sidebar siempre visible encima del video */
    section[data-testid="stSidebar"] {
        z-index: 100 !important;
    }

    /* Móviles */
    @media (max-width: 768px) {
        .hero-bg-video, .hero-overlay {
            width: 100% !important;
        }
        .hero-title {
            font-size: clamp(1.65rem, 9vw, 2.25rem) !important;
            letter-spacing: 0.1rem !important;
        }
        /* Streamlit columns: fuerza 100% ancho y stack vertical */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            align-items: stretch !important;
        }
        [data-testid="stVerticalBlock"] {
            width: 100% !important;
            min-width: 0 !important;
        }
        /* Tablas y grids */
        table {
            width: 100% !important;
            font-size: 0.95rem !important;
            overflow-x: auto !important;
            display: block !important;
        }
        th, td {
            word-break: break-word !important;
            padding: 0.5em !important;
        }
    }
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const glassBox = document.querySelector('.glass-box');
        const heroOverlay = document.querySelector('.hero-overlay');
        
        if (!glassBox || !heroOverlay) return;
        
        heroOverlay.addEventListener('mousemove', function(e) {
            const rect = glassBox.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calcular ángulo de inclinación (max 15° en cada dirección)
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateY = ((x - centerX) / centerX) * 15;
            const rotateX = -((y - centerY) / centerY) * 15;
            
            // Aplicar rotación 3D
            glassBox.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            
            // Mover el spotlight (pseudo-elemento ::before)
            const spotX = (x / rect.width) * 100;
            const spotY = (y / rect.height) * 100;
            glassBox.style.setProperty('--spotX', spotX + '%');
            glassBox.style.setProperty('--spotY', spotY + '%');
            const beforeElement = glassBox.querySelector('::before');
            if (beforeElement) {
                beforeElement.style.backgroundPosition = spotX + '% ' + spotY + '%';
            }
        });
        
        heroOverlay.addEventListener('mouseleave', function() {
            glassBox.style.transform = 'rotateX(0deg) rotateY(0deg)';
        });
    });
    </script>
    """, unsafe_allow_html=True)
    if video_b64:
        html_code = f'''
        <video class="hero-bg-video" autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4" />
        </video>
        <div class="hero-overlay">
            <div class="glass-box">
                <h1 class="hero-title">CHAMPILEAKS</h1>
                <p class="hero-subtitle">Inteligencia Digital Marista</p>
            </div>
        </div>
        '''
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.markdown('<div class="hero-overlay"><div class="glass-box"><h1 class="hero-title">CHAMPILEAKS</h1><p class="hero-subtitle">Inteligencia Digital Marista</p></div></div>', unsafe_allow_html=True)

    st.html("""
    <script>
    (() => {
      const installDrag = () => {
        const card = document.querySelector('.glass-box');
        const overlay = document.querySelector('.hero-overlay');
        if (!card || !overlay) {
          window.setTimeout(installDrag, 100);
          return;
        }
        if (card.dataset.champiDragReady === 'true') return;
        card.dataset.champiDragReady = 'true';
        card.title = 'Arrástrame para mover la consola · doble clic para centrar';

        let dragging = false;
        let offsetX = 0;
        let offsetY = 0;
        const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

        const centre = () => {
          card.style.position = '';
          card.style.left = '';
          card.style.top = '';
          card.classList.remove('is-dragging');
        };

        card.addEventListener('pointerdown', (event) => {
          if (event.button !== 0) return;
          const cardRect = card.getBoundingClientRect();
          const overlayRect = overlay.getBoundingClientRect();
          card.style.position = 'absolute';
          card.style.left = `${cardRect.left - overlayRect.left}px`;
          card.style.top = `${cardRect.top - overlayRect.top}px`;
          offsetX = event.clientX - cardRect.left;
          offsetY = event.clientY - cardRect.top;
          dragging = true;
          card.classList.add('is-dragging');
          card.setPointerCapture(event.pointerId);
          event.preventDefault();
        });

        card.addEventListener('pointermove', (event) => {
          if (!dragging) return;
          const overlayRect = overlay.getBoundingClientRect();
          const maxLeft = Math.max(0, overlayRect.width - card.offsetWidth);
          const maxTop = Math.max(0, overlayRect.height - card.offsetHeight);
          card.style.left = `${clamp(event.clientX - overlayRect.left - offsetX, 0, maxLeft)}px`;
          card.style.top = `${clamp(event.clientY - overlayRect.top - offsetY, 0, maxTop)}px`;
        });

        const release = (event) => {
          if (!dragging) return;
          dragging = false;
          card.classList.remove('is-dragging');
          if (card.hasPointerCapture(event.pointerId)) card.releasePointerCapture(event.pointerId);
        };
        card.addEventListener('pointerup', release);
        card.addEventListener('pointercancel', release);
        card.addEventListener('dblclick', centre);
      };
      installDrag();
    })();
    </script>
    """)

    if datos_validos and total_seguidores > 0:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            delta_val = f"{delta_pct:+.1f}%" if delta_pct != 0 else None
            st.metric(
                label="Seguidores Totales Red Marista",
                value=f"{total_seguidores:,}",
                delta=delta_val if delta_val else None,
                help=breakdown_text if breakdown_text else None
            )
    else:
        st.info("🚀 Bienvenido a tu Inteligencia Digital - Carga datos para comenzar", icon="ℹ️")
