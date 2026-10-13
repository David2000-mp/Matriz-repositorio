"""
Vista de Landing Page para CHAMPILEAKS.

Portada tipo "centro de mando": hero con el corte de datos vigente, KPIs de la
red y accesos directos a los módulos principales.
"""

from __future__ import annotations

import html
import logging

import pandas as pd
import streamlit as st

from utils.analytics import summarize_followers_growth
from utils.app_data import format_month_label
from utils.data_provider import data_provider

# Servidos por Streamlit desde /static (server.enableStaticServing).
HERO_VIDEO_URL = "app/static/banner_video.mp4"
HERO_POSTER_URL = "app/static/hero_poster.jpg"

# Tonos legibles sobre el fondo oscuro del hero.
_PLATFORM_COLORS = {
    "facebook": "#4C8DFF",
    "instagram": "#E1306C",
    "tiktok": "#25F4EE",
    "youtube": "#FF4D4D",
    "linkedin": "#3A8DDE",
    "twitter": "#A0AEC0",
    "x": "#A0AEC0",
}

# (url_path, título, descripción, icono) de los accesos directos.
_MODULES = (
    (
        "dashboard",
        "Dashboard global",
        "KPIs de seguidores, engagement y salud digital por red.",
        ":material/dashboard:",
    ),
    (
        "audiencias",
        "Audiencias y riesgo",
        "Segmentos educativos y matriz de riesgo institucional.",
        ":material/groups:",
    ),
    (
        "contenidos",
        "Contenidos",
        "Qué formatos funcionan y con qué frecuencia publicar.",
        ":material/article:",
    ),
    (
        "comparativas",
        "Comparar colegios",
        "Dos colegios o periodos, lado a lado.",
        ":material/compare_arrows:",
    ),
    (
        "registro",
        "Registro estadístico",
        "Descriptiva, inferencia y proyección por cuenta.",
        ":material/query_stats:",
    ),
    (
        "captura",
        "Captura",
        "Registra las métricas del mes y revisa pendientes.",
        ":material/edit_note:",
    ),
)


def _network_snapshot() -> dict | None:
    """Calcula seguidores totales, variación y desglose por red del último corte."""
    cuentas, metricas = data_provider.get_data()
    if metricas.empty or cuentas.empty:
        return None
    try:
        df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
        for logical in ("entidad", "plataforma", "usuario_red"):
            if logical in df.columns:
                continue
            for suff in (f"{logical}_y", f"{logical}_x"):
                if suff in df.columns:
                    df[logical] = df.loc[:, suff]
                    break
            else:
                df[logical] = "Unknown"
        if "fecha" not in df.columns or df["entidad"].isna().all():
            return None

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        resumen = summarize_followers_growth(df)
        snapshot = resumen["snapshot"]
        total = int(resumen["total"])
        if total <= 0:
            return None

        by_platform = (
            snapshot.groupby("plataforma")["seguidores"]
            .sum()
            .sort_values(ascending=False)
        )
        latest = df["fecha"].dropna().max()
        return {
            "total": total,
            "delta_pct": float(resumen["delta_pct"]),
            "platforms": [(str(p), int(v)) for p, v in by_platform.items() if v > 0],
            "entities": int(snapshot["entidad"].nunique()),
            "accounts": int(len(snapshot)),
            "cutoff": format_month_label(latest.strftime("%Y-%m"))
            if pd.notna(latest)
            else "—",
        }
    except Exception as exc:
        logging.warning("Error calculando el resumen de la landing: %s", exc)
        return None


def _hero_html(snap: dict | None) -> str:
    """Construye el HTML del hero; todo texto dinámico se escapa."""
    if snap:
        delta = snap["delta_pct"]
        delta_class = "up" if delta >= 0 else "down"
        delta_html = (
            f'<span class="cl-hero-delta {delta_class}">{delta:+.1f}% vs mes anterior</span>'
            if delta
            else ""
        )
        stats = f"""
            <div class="cl-hero-stats">
              <div><span class="v">{snap['total']:,}</span><span class="k">Seguidores totales</span>{delta_html}</div>
              <div><span class="v">{snap['entities']}</span><span class="k">Colegios</span></div>
              <div><span class="v">{snap['accounts']}</span><span class="k">Cuentas activas</span></div>
              <div><span class="v">{len(snap['platforms'])}</span><span class="k">Redes</span></div>
            </div>"""
        total = max(snap["total"], 1)
        rows = []
        for name, value in snap["platforms"]:
            color = _PLATFORM_COLORS.get(name.lower(), "#94A3B8")
            share = value / total * 100
            rows.append(
                f'<li><span class="n">{html.escape(name)}</span>'
                f'<span class="bar"><i style="width:{share:.1f}%;background:{color}"></i></span>'
                f'<span class="p">{share:.0f}%</span></li>'
            )
        panel = (
            '<aside class="cl-hero-panel"><p class="cl-hero-panel-title">Audiencia por red</p>'
            f'<ul>{"".join(rows)}</ul></aside>'
        )
        eyebrow = f'<span class="cl-dot"></span>Red Marista · corte {html.escape(snap["cutoff"])}'
    else:
        stats = (
            '<p class="cl-hero-empty">Aún no hay métricas cargadas. Empieza en '
            "<b>Captura</b> o sincroniza la fuente desde el panel lateral.</p>"
        )
        panel = ""
        eyebrow = '<span class="cl-dot cl-dot--idle"></span>Red Marista · sin datos'

    return f"""
    <section class="cl-hero">
      <video class="cl-hero-video" autoplay loop muted playsinline preload="metadata"
             poster="{HERO_POSTER_URL}" aria-hidden="true">
        <source src="{HERO_VIDEO_URL}" type="video/mp4" />
      </video>
      <div class="cl-hero-main">
        <p class="cl-hero-eyebrow">{eyebrow}</p>
        <h1 class="cl-hero-title">CHAMPI<span class="accent">LEAKS</span></h1>
        <p class="cl-hero-lead">Inteligencia digital para la red de colegios Maristas:
        audiencias, contenido y engagement en un solo lugar.</p>
        {stats}
      </div>
      {panel}
    </section>
    """


_LANDING_CSS = """
<style>
.cl-hero {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(240px, 1fr);
    gap: clamp(1.25rem, 3vw, 2.5rem);
    align-items: end;
    padding: clamp(1.5rem, 4vw, 3rem);
    min-height: 380px;
    border-radius: 20px;
    background: #071433 url("app/static/hero_poster.jpg") center / cover;
    color: #FFFFFF;
    box-shadow: 0 20px 50px rgba(7, 20, 51, 0.25);
}
.cl-hero-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -3;
}
/* Velo de tinta + retícula técnica sobre el video. */
.cl-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: -2;
    background:
        linear-gradient(100deg, rgba(7, 20, 51, 0.96) 0%, rgba(7, 20, 51, 0.86) 45%, rgba(7, 20, 51, 0.55) 100%);
}
.cl-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    z-index: -1;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
    background-size: 36px 36px;
    -webkit-mask-image: radial-gradient(120% 90% at 0% 100%, #000 30%, transparent 75%);
    mask-image: radial-gradient(120% 90% at 0% 100%, #000 30%, transparent 75%);
}
section[data-testid="stMain"] .cl-hero-panel li { color: #E6ECF8; }
section[data-testid="stMain"] .cl-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin: 0 0 1rem;
    padding: 0.3rem 0.7rem;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    font-family: var(--champi-mono);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #C9D4EE;
}
section[data-testid="stMain"] h1.cl-hero-title {
    margin: 0;
    padding: 0;
    font-size: clamp(2.4rem, 6vw, 4.25rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.035em;
    color: #FFFFFF;
}
section[data-testid="stMain"] .cl-hero-title span { color: #FFFFFF; }
section[data-testid="stMain"] .cl-hero-title span.accent { color: var(--champi-accent); }
section[data-testid="stMain"] p.cl-hero-lead {
    max-width: 52ch;
    margin: 0.9rem 0 1.75rem;
    font-size: clamp(0.95rem, 1.4vw, 1.1rem);
    line-height: 1.5;
    color: #C9D4EE;
}
.cl-hero-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, auto));
    justify-content: start;
    gap: 0.75rem 2.25rem;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
}
.cl-hero-stats > div { display: flex; flex-direction: column; gap: 0.2rem; }
.cl-hero-stats .v {
    font-family: var(--champi-mono);
    font-size: clamp(1.35rem, 2.4vw, 1.85rem);
    font-weight: 600;
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
    color: #FFFFFF;
}
.cl-hero-stats .k {
    font-family: var(--champi-mono);
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8A9AC0;
}
.cl-hero-delta {
    font-family: var(--champi-mono);
    font-size: 0.72rem;
}
.cl-hero-delta.up { color: #4ADE80; }
.cl-hero-delta.down { color: #F87171; }
section[data-testid="stMain"] p.cl-hero-empty { color: #C9D4EE; max-width: 46ch; }
.cl-hero-panel {
    align-self: end;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 1.1rem 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    background: rgba(7, 20, 51, 0.55);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
}
section[data-testid="stMain"] p.cl-hero-panel-title {
    margin: 0 0 0.85rem;
    font-family: var(--champi-mono);
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8A9AC0;
}
.cl-hero-panel ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.6rem; }
.cl-hero-panel li {
    display: grid;
    grid-template-columns: 5.5rem 1fr 2.6rem;
    align-items: center;
    gap: 0.6rem;
    margin: 0;
    font-size: 0.82rem;
}
.cl-hero-panel .bar {
    height: 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    overflow: hidden;
}
.cl-hero-panel .bar i { display: block; height: 100%; border-radius: inherit; }
.cl-hero-panel .p {
    text-align: right;
    font-family: var(--champi-mono);
    font-variant-numeric: tabular-nums;
    color: #C9D4EE;
}
/* Tarjetas de módulo: el page_link ocupa la fila de título. */
.st-key-landing-modules [data-testid="stPageLink"] a {
    padding: 0;
    font-weight: 600;
}
.st-key-landing-modules [data-testid="stPageLink"] a p {
    font-size: 1rem;
    color: var(--champi-ink);
}
.st-key-landing-modules [data-testid="stPageLink"] [data-testid="stIconMaterial"] {
    color: var(--champi-primary);
}
@media (max-width: 900px) {
    .cl-hero { grid-template-columns: 1fr; min-height: 0; }
    /* La capa responsive global centra y reduce los h1; el wordmark no. */
    section[data-testid="stMain"] h1.cl-hero-title {
        font-size: clamp(2.4rem, 12vw, 3.25rem) !important;
        text-align: left !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    .cl-hero-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (prefers-reduced-motion: reduce) {
    .cl-hero-video { display: none; }
    .cl-dot { animation: none; }
}
</style>
"""


def render(df=None):
    """Renderiza la portada. Acepta ``df`` por compatibilidad con el enrutador."""
    del df
    st.markdown(_LANDING_CSS, unsafe_allow_html=True)
    # Markdown interpreta líneas con sangría como bloque de código: se aplana.
    hero = " ".join(
        line.strip() for line in _hero_html(_network_snapshot()).splitlines()
    )
    st.markdown(hero, unsafe_allow_html=True)

    st.markdown('<p class="cl-section-label">Módulos</p>', unsafe_allow_html=True)
    pages = st.session_state.get("_nav_pages", {})
    with st.container(key="landing-modules"):
        for row_start in range(0, len(_MODULES), 3):
            cols = st.columns(3)
            for col, (path, title, description, icon) in zip(
                cols, _MODULES[row_start : row_start + 3]
            ):
                with col, st.container(border=True):
                    page = pages.get(path)
                    if page is not None:
                        st.page_link(page, label=title, icon=icon)
                    else:
                        st.markdown(f"{icon} **{title}**")
                    st.caption(description)
