"""Entry point y router nativo de CHAMPILEAKS."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st

from components import (
    FilterBar,
    PageHeader,
    configure_plotly_theme,
    filter_chip,
    inject_clipboard_shortcut_guard,
    inject_custom_css,
    inject_layout_compact_css,
    render_empty_state,
    render_friendly_error,
    status_chip,
)
from components.chart_downloads import install_global_chart_csv_downloads
from utils.app_data import (
    apply_global_filters,
    format_month_label,
    get_filter_options,
    load_app_dataframe,
    summarize_dataset,
)
from utils.logger import get_logger, set_production_mode

logger = get_logger(__name__)

APP_VERSION = "v2.2.0"
ENTITY_KEY = "filtro_entidad"
MONTH_KEY = "filtro_mes"
NAV_PAGES_KEY = "_nav_pages"


def _configure_app() -> None:
    """Configura la página y el sistema visual compartido."""
    if os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true":
        set_production_mode()

    st.set_page_config(
        page_title="CHAMPILEAKS · Inteligencia Digital Marista",
        layout="wide",
        page_icon="images/logo_maristas.png",
        initial_sidebar_state="auto",
        menu_items={"Get Help": None, "Report a bug": None, "About": None},
    )
    install_global_chart_csv_downloads()
    configure_plotly_theme()

    # El logo nativo ocupa la cabecera reservada del sidebar y queda siempre
    # por encima del menú generado por st.navigation.
    st.logo("utils/logo_maristas_sidebar.png")

    try:
        inject_custom_css()
        inject_layout_compact_css(hide_streamlit_header=True)
        inject_clipboard_shortcut_guard()
    except Exception as exc:
        logging.warning("No se pudo aplicar el CSS existente: %s", exc)


def _load_data_for_ui():
    """Carga datos compartidos; nunca escribe el DataFrame en session_state."""
    try:
        # El primer acceso consulta la fuente remota; las siguientes
        # ejecuciones usan el caché compartido de Streamlit.
        with st.spinner("Sincronizando datos…"):
            return load_app_dataframe()
    except Exception as exc:
        render_friendly_error("No pudimos cargar los datos.", exc, key="data-load")
        return None


def _reset_filters() -> None:
    """Restablece filtros antes de que Streamlit instancie sus widgets."""
    st.session_state[ENTITY_KEY] = "Todas"
    st.session_state[MONTH_KEY] = "Todos"


def _reload_data() -> None:
    """Invalida el caché compartido desde el callback del botón."""
    from utils.data_provider import data_provider

    data_provider.invalidate_cache()
    st.toast("Recargando datos desde la fuente…", icon=":material/sync:")


# ---------------------------------------------------------------------------
# Renderizadores (importación diferida: solo se carga la vista activa)
# ---------------------------------------------------------------------------


def _render_inicio() -> None:
    from views import landing

    landing.render()


def _render_dashboard() -> None:
    from views import dashboard

    df = load_app_dataframe()
    if df is None or df.empty:
        render_empty_state(
            "**Aún no hay datos para mostrar**  \n"
            "Carga o sincroniza registros y vuelve a consultar el Dashboard Global.",
        )
        return

    filtered = apply_global_filters(
        df,
        entity=st.session_state.get(ENTITY_KEY, "Todas"),
        month=st.session_state.get(MONTH_KEY, "Todos"),
    )
    if filtered.empty:
        render_empty_state(
            "**Los filtros no encontraron registros**  \n"
            "Prueba con otro colegio o periodo desde los filtros del panel lateral.",
        )
        return
    dashboard.render(filtered)


def _render_comparativas() -> None:
    from views import comparison

    comparison.render_comparison_view()


def _render_audiencias() -> None:
    from views import audience_risk_view

    audience_risk_view.render()


def _render_contenidos() -> None:
    from views import new_data_dashboard

    new_data_dashboard.render_new_data_dashboard()


def _render_textos() -> None:
    from views import text_analysis_dashboard

    text_analysis_dashboard.render_text_analysis_dashboard()


def _render_demografia() -> None:
    from views import demographic_geographic_analysis

    demographic_geographic_analysis.render_demographic_geographic_analysis()


def _render_cruzada() -> None:
    from views import cross_intelligence_view

    cross_intelligence_view.render_cross_intelligence_view()


def _render_satelite() -> None:
    from views import satellite_dashboard

    satellite_dashboard.render()


def _render_engagement() -> None:
    from views import engagement_calculator_v2

    engagement_calculator_v2.render()


def _render_registro() -> None:
    from views import statistical_registry_dashboard

    statistical_registry_dashboard.render_statistical_registry_dashboard()


def _render_captura() -> None:
    from views import data_entry

    data_entry.render()


def _render_auditoria() -> None:
    from views import audit_view

    audit_view.render_audit_view()


def _render_configuracion() -> None:
    from views import settings

    settings.render()


# ---------------------------------------------------------------------------
# Catálogo de páginas
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PageSpec:
    """Metadatos de una página: navegación, encabezado y filtros que usa."""

    renderer: Callable[[], None]
    title: str
    icon: str
    url_path: str
    subtitle: str = ""
    filters: tuple[str, ...] = ()
    show_header: bool = True
    default: bool = False


BOTH = (ENTITY_KEY, MONTH_KEY)

PAGE_GROUPS: dict[str, list[PageSpec]] = {
    "Resumen": [
        PageSpec(
            _render_inicio,
            "Inicio",
            ":material/home:",
            "inicio",
            show_header=False,
            default=True,
        ),
        PageSpec(
            _render_dashboard,
            "Dashboard global",
            ":material/dashboard:",
            "dashboard",
            "Seguidores, engagement y salud digital de la red Marista en un solo vistazo.",
            filters=BOTH,
        ),
    ],
    "Inteligencia": [
        PageSpec(
            _render_audiencias,
            "Audiencias y riesgo",
            ":material/groups:",
            "audiencias",
            "Segmenta audiencias por nivel educativo y ubica cada colegio en la matriz de riesgo.",
            filters=BOTH,
        ),
        PageSpec(
            _render_contenidos,
            "Contenidos",
            ":material/article:",
            "contenidos",
            "Desempeño, calidad y oportunidades por tipo de contenido y frecuencia de publicación.",
            filters=BOTH,
        ),
        PageSpec(
            _render_textos,
            "Análisis de textos",
            ":material/text_fields:",
            "textos",
            "Sentimiento, palabras clave y tendencia mensual de publicaciones y comentarios.",
            filters=BOTH,
        ),
        PageSpec(
            _render_demografia,
            "Demografía y geografía",
            ":material/map:",
            "demografia",
            "Distribución de audiencias por edad, género y ciudad.",
        ),
        PageSpec(
            _render_cruzada,
            "Inteligencia cruzada",
            ":material/hub:",
            "inteligencia-cruzada",
            "Quién compone la audiencia y cómo se relaciona con el rendimiento del contenido.",
        ),
        PageSpec(
            _render_satelite,
            "Satélite",
            ":material/satellite_alt:",
            "satelite",
            "Termómetro de comentarios clasificados y contexto oficial agregado.",
        ),
    ],
    "Rendimiento": [
        PageSpec(
            _render_comparativas,
            "Comparar colegios",
            ":material/compare_arrows:",
            "comparativas",
            "Contrasta dos colegios, plataformas o periodos lado a lado.",
            filters=(MONTH_KEY,),
        ),
        PageSpec(
            _render_engagement,
            "Calculadora de engagement",
            ":material/calculate:",
            "engagement",
            "Calcula el engagement de una cuenta en tres pasos y descarga el reporte.",
        ),
        PageSpec(
            _render_registro,
            "Registro estadístico",
            ":material/query_stats:",
            "registro",
            "Estadística descriptiva, inferencia y proyección de tendencia por cuenta.",
            filters=BOTH,
        ),
    ],
    "Datos": [
        PageSpec(
            _render_captura,
            "Captura",
            ":material/edit_note:",
            "captura",
            "Registra las métricas mensuales de cada cuenta y revisa pendientes.",
        ),
        PageSpec(
            _render_auditoria,
            "Auditoría",
            ":material/fact_check:",
            "auditoria",
            "Revisa las respuestas del formulario antes de consolidarlas.",
        ),
        PageSpec(
            _render_configuracion,
            "Configuración",
            ":material/settings:",
            "configuracion",
            "Simulador de datos, reportes PDF y administración del sistema.",
        ),
    ],
}

SPECS_BY_PATH = {
    spec.url_path: spec for specs in PAGE_GROUPS.values() for spec in specs
}


def _header_chips(spec: PageSpec, df) -> list[str]:
    """Estado del corte de datos y filtros globales activos de la página."""
    summary = summarize_dataset(df)
    chips: list[str] = []
    if summary.latest_month:
        chips.append(status_chip("Corte", format_month_label(summary.latest_month)))
    else:
        chips.append(status_chip("Sin datos", live=False))

    entity = st.session_state.get(ENTITY_KEY, "Todas")
    month = st.session_state.get(MONTH_KEY, "Todos")
    if ENTITY_KEY in spec.filters and entity != "Todas":
        chips.append(filter_chip("Colegio", entity))
    if MONTH_KEY in spec.filters and month != "Todos":
        chips.append(filter_chip("Periodo", format_month_label(month)))
    return chips


def _wrap(spec: PageSpec, eyebrow: str) -> Callable[[], None]:
    """Envuelve una vista con encabezado común y una frontera de errores."""

    def run() -> None:
        if spec.show_header:
            PageHeader(
                spec.title,
                spec.subtitle or None,
                eyebrow=eyebrow,
                chips=_header_chips(spec, _safe_df()),
            )
        try:
            spec.renderer()
        except (
            Exception
        ) as exc:  # Las excepciones de control de Streamlit no heredan de Exception.
            render_friendly_error(
                f"No pudimos mostrar «{spec.title}».",
                exc,
                key=f"page-error-{spec.url_path}",
            )

    run.__name__ = f"page_{spec.url_path.replace('-', '_')}"
    return run


def _safe_df():
    try:
        return load_app_dataframe()
    except Exception:
        return None


def _build_navigation():
    pages: dict[str, list] = {}
    by_path: dict[str, st.Page] = {}
    for group, specs in PAGE_GROUPS.items():
        pages[group] = []
        for spec in specs:
            page = st.Page(
                _wrap(spec, group),
                title=spec.title,
                icon=spec.icon,
                url_path=spec.url_path,
                default=spec.default,
            )
            pages[group].append(page)
            by_path[spec.url_path] = page
    # La landing enlaza a los módulos con st.page_link usando estos objetos.
    st.session_state[NAV_PAGES_KEY] = by_path
    return st.navigation(pages, position="sidebar", expanded=True)


def _render_sidebar_controls(spec: PageSpec | None, df) -> None:
    """Filtros globales solo en las páginas que los aplican."""
    filters = spec.filters if spec else ()
    options = get_filter_options(df)
    entities = ["Todas", *options.entities]
    months = ["Todos", *options.months]

    if st.session_state.get(ENTITY_KEY, "Todas") not in entities:
        st.session_state[ENTITY_KEY] = "Todas"
    if st.session_state.get(MONTH_KEY, "Todos") not in months:
        st.session_state[MONTH_KEY] = "Todos"

    with st.sidebar:
        FilterBar(
            entities=entities,
            months=months,
            show_entity=ENTITY_KEY in filters,
            show_month=MONTH_KEY in filters,
            show_reload=bool(filters)
            or (spec is not None and spec.url_path == "inicio"),
            on_reset=_reset_filters,
            on_reload=_reload_data,
        )


def _render_sidebar_status(df) -> None:
    """Pie del sidebar con el corte de datos; va al final, tras los controles de la vista."""
    summary = summarize_dataset(df)
    corte = format_month_label(summary.latest_month) if summary.latest_month else "—"
    st.sidebar.markdown(
        '<div class="cl-sidebar-status">'
        f"Corte <b>{corte}</b> · <b>{summary.entities}</b> colegios · "
        f"<b>{summary.accounts}</b> cuentas<br>{APP_VERSION} · Maristas"
        "</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    _configure_app()
    current_page = _build_navigation()
    # La página por defecto expone url_path "" (raíz); su spec es "inicio".
    spec = SPECS_BY_PATH.get(current_page.url_path or "inicio")

    # La caché es global; session_state conserva únicamente filtros escalares.
    df = _load_data_for_ui()
    _render_sidebar_controls(spec, df)

    current_page.run()
    _render_sidebar_status(df)


if __name__ == "__main__":
    main()
