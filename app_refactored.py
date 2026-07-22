"""Entry point y router nativo de CHAMPILEAKS."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable

import streamlit as st

from components import (
    inject_clipboard_shortcut_guard,
    inject_custom_css,
    inject_layout_compact_css,
)
from utils.app_data import apply_global_filters, get_filter_options, load_app_dataframe
from utils.logger import get_logger, set_production_mode

logger = get_logger(__name__)


def _configure_app() -> None:
    """Configura la página y conserva el sistema visual existente."""
    if os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true":
        set_production_mode()

    st.set_page_config(
        page_title="CHAMPILEAKS",
        layout="wide",
        page_icon="Ⓜ️",
        initial_sidebar_state="expanded",
        menu_items={"Get Help": None, "Report a bug": None, "About": None},
    )

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
        return load_app_dataframe()
    except Exception as exc:
        logger.exception("No se pudieron cargar los datos de la aplicación")
        st.error("No se pudieron cargar los datos. Verifica la conexión configurada.")
        st.caption(str(exc))
        return None


def _render_sidebar_controls(df) -> None:
    """Renderiza identidad, filtros globales y controles operativos."""
    options = get_filter_options(df)

    with st.sidebar:
        st.divider()
        st.subheader("Filtros globales")

        entities = ["Todas", *options.entities]
        months = ["Todos", *options.months]

        if st.session_state.get("filtro_entidad", "Todas") not in entities:
            st.session_state["filtro_entidad"] = "Todas"
        if st.session_state.get("filtro_mes", "Todos") not in months:
            st.session_state["filtro_mes"] = "Todos"

        st.selectbox("Colegio", entities, key="filtro_entidad")
        st.selectbox("Periodo", months, key="filtro_mes")

        if st.button(
            "Reset filtros",
            help="Restablece colegio y periodo.",
            use_container_width=True,
        ):
            st.session_state["filtro_entidad"] = "Todas"
            st.session_state["filtro_mes"] = "Todos"
            st.rerun()

        if st.button(
            "Forzar recarga",
            help="Invalida el caché compartido y consulta nuevamente la fuente.",
            use_container_width=True,
        ):
            from utils.data_provider import data_provider

            data_provider.invalidate_cache()
            st.toast("Caché invalidado. Recargando datos…", icon="🔄")
            st.rerun()

        st.divider()
        st.caption("v2.1.0 • Maristas")


def _render_inicio() -> None:
    """Landing intacta: conserva video, glassmorphism y estilos propios."""
    from views import landing

    landing.render()


def _render_dashboard() -> None:
    from views import dashboard

    df = _load_data_for_ui()
    if df is None or df.empty:
        st.warning("No hay datos disponibles para el Dashboard Global.")
        return

    filtered = apply_global_filters(
        df,
        entity=st.session_state.get("filtro_entidad", "Todas"),
        month=st.session_state.get("filtro_mes", "Todos"),
    )
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


def _page(
    renderer: Callable[[], None],
    *,
    title: str,
    icon: str,
    url_path: str,
    default: bool = False,
) -> st.Page:
    """Construye una página con URL estable y sin estado de navegación manual."""
    return st.Page(
        renderer,
        title=title,
        icon=icon,
        url_path=url_path,
        default=default,
    )


def _build_navigation():
    pages = {
        "Resumen": [
            _page(
                _render_inicio,
                title="Inicio",
                icon=":material/home:",
                url_path="inicio",
                default=True,
            ),
            _page(
                _render_dashboard,
                title="Dashboard Global",
                icon=":material/dashboard:",
                url_path="dashboard",
            ),
        ],
        "Inteligencia": [
            _page(
                _render_audiencias,
                title="Audiencias y riesgo",
                icon=":material/groups:",
                url_path="audiencias",
            ),
            _page(
                _render_contenidos,
                title="Tipo de contenidos",
                icon=":material/article:",
                url_path="contenidos",
            ),
            _page(
                _render_textos,
                title="Análisis de textos",
                icon=":material/text_fields:",
                url_path="textos",
            ),
            _page(
                _render_demografia,
                title="Demografía y geografía",
                icon=":material/map:",
                url_path="demografia",
            ),
            _page(
                _render_cruzada,
                title="Inteligencia cruzada",
                icon=":material/hub:",
                url_path="inteligencia-cruzada",
            ),
        ],
        "Comparativas": [
            _page(
                _render_comparativas,
                title="Comparativas",
                icon=":material/compare_arrows:",
                url_path="comparativas",
            ),
            _page(
                _render_engagement,
                title="Engagement",
                icon=":material/monitoring:",
                url_path="engagement",
            ),
        ],
        "Datos": [
            _page(
                _render_registro,
                title="Registro estadístico",
                icon=":material/table_chart:",
                url_path="registro",
            ),
            _page(
                _render_captura,
                title="Captura",
                icon=":material/edit_note:",
                url_path="captura",
            ),
            _page(
                _render_auditoria,
                title="Auditoría",
                icon=":material/fact_check:",
                url_path="auditoria",
            ),
        ],
        "Sistema": [
            _page(
                _render_configuracion,
                title="Configuración",
                icon=":material/settings:",
                url_path="configuracion",
            ),
        ],
    }
    return st.navigation(pages, position="sidebar", expanded=True)


def main() -> None:
    _configure_app()
    current_page = _build_navigation()

    # La caché es global; session_state conserva únicamente filtros escalares.
    df = _load_data_for_ui()
    _render_sidebar_controls(df)

    current_page.run()


if __name__ == "__main__":
    main()
