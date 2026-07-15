"""Vista de Inteligencia Cruzada para Chammpileaks."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

from components import PLOTLY_CONFIG
from utils.cross_intelligence import (
    build_city_performance_drilldown,
    build_daily_performance_series,
    build_demographic_time_share,
    build_historical_performance_series,
    build_demographic_vs_network,
    build_performance_vs_network,
    build_school_ranking,
    build_segment_distribution,
    calculate_historical_totals,
    calculate_performance_kpis,
    get_dominant_demographic,
    get_filter_catalogs,
    get_historical_slice,
    get_month_bounds,
    get_monthly_slice,
    get_top_city,
    month_key_to_label,
    HISTORICAL_KEY,
)


def _metric_value(value: float) -> str:
    return f"{value:,.0f}"


def _metric_delta_text(current: float, previous: float, delta_abs: float, delta_pct: float | None) -> str:
    if previous <= 0:
        return "Sin base previa"
    if delta_pct is None:
        return f"{delta_abs:+,.0f}"
    return f"{delta_abs:+,.0f} ({delta_pct:+.1f}%)"


def _apply_plotly_accessibility_theme(fig) -> None:
    """Asegura contraste suficiente para textos, ejes y leyendas."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"color": "#111827", "size": 13},
        title_font={"color": "#111827", "size": 18},
        legend={
            "font": {"color": "#111827", "size": 12},
            "title": {"font": {"color": "#111827", "size": 12}},
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font": {"color": "#111827", "size": 12},
            "bordercolor": "#9CA3AF",
        },
    )
    fig.update_xaxes(
        title_font={"color": "#111827"},
        tickfont={"color": "#111827"},
        gridcolor="#E5E7EB",
        zeroline=False,
        automargin=True,
    )
    fig.update_yaxes(
        title_font={"color": "#111827"},
        tickfont={"color": "#111827"},
        gridcolor="#E5E7EB",
        zeroline=False,
        automargin=True,
    )


def _force_plotly_text_contrast() -> None:
    """Inyecta CSS global para mantener alto contraste en los textos de Plotly."""
    if st.session_state.get("_plotly_text_contrast_css_injected"):
        return

    st.html(
        """
        <style>
        .js-plotly-plot svg.main-svg text,
        .js-plotly-plot .xtick text,
        .js-plotly-plot .ytick text,
        .js-plotly-plot .gtitle,
        .js-plotly-plot .legendtext,
        .js-plotly-plot .annotation text {
            fill: #111827 !important;
            color: #111827 !important;
        }
        </style>
        """
    )
    st.session_state["_plotly_text_contrast_css_injected"] = True


def _render_filters() -> tuple[str, str, str]:
    catalogs = get_filter_catalogs()
    month_keys = catalogs.get("month_keys", [])

    if not month_keys:
        return "Todos", "Todas", ""

    with st.sidebar:
        st.markdown("---")
        st.subheader("Inteligencia Cruzada")

        colegio = st.selectbox(
            "Colegio",
            options=["Todos"] + catalogs.get("colegios", []),
            key="cross_college",
        )

        plataforma = st.selectbox(
            "Plataforma",
            options=["Todas"] + catalogs.get("plataformas", []),
            key="cross_platform",
        )

        month_key = st.selectbox(
            "Mes/Ano",
            options=month_keys,
            format_func=month_key_to_label,
            key="cross_month_key",
        )

    return colegio, plataforma, month_key


def _render_block_1(
    maestra_current,
    maestra_previous,
    maestra_historical,
    demo_current,
    prev_month_key: str,
) -> None:
    st.subheader("Bloque 1 - Correlacion Rendimiento-Audiencia")

    kpis = calculate_performance_kpis(maestra_current, maestra_previous)
    historical_totals = calculate_historical_totals(maestra_historical)
    dominant = get_dominant_demographic(demo_current)
    top_city = get_top_city(demo_current)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**Interacciones y Visualizaciones**")

            inter = kpis["interacciones"]
            vis = kpis["visualizaciones"]

            st.metric(
                "Interacciones",
                _metric_value(inter.current),
                delta=_metric_delta_text(inter.current, inter.previous, inter.delta_abs, inter.delta_pct),
            )
            st.metric(
                "Visualizaciones",
                _metric_value(vis.current),
                delta=_metric_delta_text(vis.current, vis.previous, vis.delta_abs, vis.delta_pct),
            )
            st.caption(
                "Acumulado historico: "
                f"Interacciones {_metric_value(historical_totals['interacciones_total'])} | "
                f"Visualizaciones {_metric_value(historical_totals['visualizaciones_total'])}"
            )

            if prev_month_key:
                st.caption(f"Delta vs {month_key_to_label(prev_month_key)}")
            else:
                st.caption("Delta: sin mes previo disponible")

    with col2:
        with st.container(border=True):
            st.markdown("**Perfil Demografico Dominante**")
            if dominant is None:
                st.warning("No hay datos de demografia base para el mes seleccionado.")
            else:
                st.metric("Segmento", f"{dominant['sexo']} | {dominant['edad']}")
                st.caption(f"Participacion: {dominant['pct']:.1f}%")

    with col3:
        with st.container(border=True):
            st.markdown("**Ciudad Principal de Alcance**")
            if top_city is None:
                st.warning("No hay datos de ciudad para el mes seleccionado.")
            else:
                st.metric("Ciudad", str(top_city["ciudad"]))
                st.caption(f"Participacion: {top_city['pct']:.1f}%")


def _render_block_2(maestra_historical, demo_historical, month_key: str) -> None:
    st.subheader("Bloque 2 - Panorama Historico y Microscopio del Mes")

    perf = build_historical_performance_series(maestra_historical)
    if perf.empty:
        st.warning("No hay datos de rendimiento historico para construir la tendencia.")
        return

    demo_share, top_segments = build_demographic_time_share(demo_historical, top_n=2)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=perf["month_date"],
            y=perf["visualizaciones"],
            name="Visualizaciones",
            mode="lines+markers",
            line={"color": "#1f77b4", "width": 3},
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=perf["month_date"],
            y=perf["interacciones"],
            name="Interacciones",
            mode="lines+markers",
            line={"color": "#ff7f0e", "width": 2},
        ),
        secondary_y=False,
    )

    if demo_share.empty:
        st.warning("No hay datos demograficos en este mes. Se muestra solo rendimiento.")
    else:
        def _resolve_time_axis(part):
            if "month_date" in part.columns:
                return part["month_date"]
            if "fecha_reporte" in part.columns:
                return part["fecha_reporte"]
            if "month_key" in part.columns:
                return pd.to_datetime(part["month_key"].astype(str) + "-01", errors="coerce")
            return None

        has_any_trace = False
        for segment in top_segments:
            part = demo_share[demo_share["segmento"] == segment]
            x_axis = _resolve_time_axis(part)
            if x_axis is None:
                continue

            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=part["pct"],
                    name=f"% {segment}",
                    mode="lines+markers",
                    line={"dash": "dot", "width": 2},
                    opacity=0.9,
                ),
                secondary_y=True,
            )
            has_any_trace = True

        if not has_any_trace:
            st.warning("No se pudo construir el overlay demografico por falta de fecha valida en el cruce historico.")

    month_start, month_end = get_month_bounds(month_key)
    if month_start is not None and month_end is not None:
        fig.add_vrect(
            x0=month_start,
            x1=month_end,
            fillcolor="#dbeafe",
            opacity=0.28,
            layer="below",
            line_width=0,
            annotation_text=f"Mes analizado: {month_key_to_label(month_key)}",
            annotation_position="top left",
        )

    fig.update_layout(
        title="Tendencia historica con resaltado del mes seleccionado",
        hovermode="x unified",
        margin={"l": 10, "r": 10, "t": 60, "b": 10},
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend={"orientation": "h", "y": 1.08},
    )

    # Ambos ejes inician en 0 para evitar correlaciones visuales falsas por baseline flotante.
    fig.update_yaxes(title_text="Rendimiento (volumen)", rangemode="tozero", secondary_y=False, zeroline=True)
    fig.update_yaxes(
        title_text="Participacion demografica (%)",
        rangemode="tozero",
        range=[0, 100],
        secondary_y=True,
        zeroline=True,
    )
    fig.update_xaxes(title_text="Fecha")
    _apply_plotly_accessibility_theme(fig)

    st.subheader("Grafica historica: rendimiento mensual y participacion demografica")
    components.html(
        fig.to_html(include_plotlyjs="cdn", full_html=False, config=PLOTLY_CONFIG),
        height=520,
        scrolling=False,
    )

    if top_segments:
        st.caption("Segmentos dominantes monitoreados: " + ", ".join(top_segments))


def _render_block_3_drilldown(maestra_current, demo_current, network_maestra, selected_college: str) -> None:
    st.subheader("Bloque 3 - Desglose Multidimensional")
    tab_city, tab_school, tab_segment = st.tabs([
        "Desglose por Ciudad",
        "Desglose por Colegio",
        "Desglose por Segmento",
    ])

    with tab_city:
        city_rank = build_city_performance_drilldown(maestra_current, demo_current)
        if city_rank.empty:
            st.warning("No hay datos suficientes para construir el desglose por ciudad en este mes.")
        else:
            st.subheader("Grafica: rendimiento estimado por ciudad")
            show = city_rank.head(12).iloc[::-1]
            fig_city = go.Figure()
            fig_city.add_trace(
                go.Bar(
                    y=show["ciudad"],
                    x=show["visualizaciones_estimadas"],
                    name="Visualizaciones est.",
                    orientation="h",
                    marker_color="#1f77b4",
                )
            )
            fig_city.add_trace(
                go.Bar(
                    y=show["ciudad"],
                    x=show["interacciones_estimadas"],
                    name="Interacciones est.",
                    orientation="h",
                    marker_color="#ff7f0e",
                )
            )
            fig_city.update_layout(
                title="Desglose por ciudad: visualizaciones e interacciones estimadas",
                barmode="group",
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
            )
            fig_city.update_xaxes(rangemode="tozero")
            _apply_plotly_accessibility_theme(fig_city)
            st.plotly_chart(fig_city, width="stretch", config=PLOTLY_CONFIG, theme=None)
            _force_plotly_text_contrast()

            table_city = city_rank.copy()
            table_city["city_pct"] = table_city["city_pct"] * 100.0
            st.dataframe(table_city, width="stretch", hide_index=True)

    with tab_school:
        school_rank = build_school_ranking(network_maestra)
        if school_rank.empty:
            st.warning("No hay datos suficientes para construir el ranking por colegio en este mes.")
        else:
            if selected_college != "Todos":
                st.info(
                    "Filtro de colegio especifico activo. Se muestra ranking de red del mes como contexto comparativo."
                )

            st.subheader("Grafica: ranking de colegios por volumen total")
            show = school_rank.head(12).iloc[::-1]
            fig_school = go.Figure()
            fig_school.add_trace(
                go.Bar(
                    y=show["colegio"],
                    x=show["volumen_total"],
                    orientation="h",
                    marker_color="#2ca02c",
                    name="Volumen total",
                )
            )
            fig_school.update_layout(
                title="Ranking de colegios por volumen total del periodo",
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
            )
            fig_school.update_xaxes(rangemode="tozero")
            _apply_plotly_accessibility_theme(fig_school)
            st.plotly_chart(fig_school, width="stretch", config=PLOTLY_CONFIG, theme=None)
            _force_plotly_text_contrast()
            st.dataframe(school_rank, width="stretch", hide_index=True)

    with tab_segment:
        segment_dist = build_segment_distribution(demo_current)
        if segment_dist.empty:
            st.warning("No hay datos de Demografia base para este mes en el desglose por segmento.")
        else:
            st.subheader("Grafica: participacion por segmento demografico")
            fig_segment = go.Figure()
            for sexo in segment_dist["sexo"].dropna().unique():
                sub = segment_dist[segment_dist["sexo"] == sexo]
                fig_segment.add_trace(
                    go.Bar(
                        x=sub["edad"],
                        y=sub["pct"],
                        name=str(sexo),
                    )
                )
            fig_segment.update_layout(
                title="Distribucion demografica por edad y sexo",
                barmode="group",
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
                yaxis_title="Participacion (%)",
                xaxis_title="Rango de edad",
            )
            fig_segment.update_yaxes(rangemode="tozero")
            _apply_plotly_accessibility_theme(fig_segment)
            st.plotly_chart(fig_segment, width="stretch", config=PLOTLY_CONFIG, theme=None)
            _force_plotly_text_contrast()
            st.dataframe(segment_dist, width="stretch", hide_index=True)


def _render_block_4_strict_comparison(network_maestra, network_demo, colegio: str) -> None:
    st.subheader("Bloque 4 - Cuenta vs Promedio de la Red (Regla Estricta)")

    if not colegio or colegio == "Todos":
        st.info("Selecciona un colegio especifico para habilitar la comparacion estricta contra la red.")
        return

    perf_comp = build_performance_vs_network(network_maestra, colegio)
    demo_comp = build_demographic_vs_network(network_demo, colegio)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Rendimiento: Cuenta vs Red (promedio)**")
        if perf_comp.empty:
            st.warning("No hay base suficiente para comparar rendimiento contra la red.")
        else:
            st.subheader("Grafica comparativa de rendimiento: cuenta vs red promedio")
            fig_perf = go.Figure()
            fig_perf.add_trace(
                go.Bar(x=perf_comp["metrica"], y=perf_comp["cuenta"], name="Cuenta", marker_color="#1f77b4")
            )
            fig_perf.add_trace(
                go.Bar(
                    x=perf_comp["metrica"],
                    y=perf_comp["red_promedio"],
                    name="Red promedio",
                    marker_color="#7f7f7f",
                )
            )
            fig_perf.update_layout(
                title="Comparacion de rendimiento: cuenta vs red promedio",
                barmode="group",
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
            )
            fig_perf.update_yaxes(rangemode="tozero")
            _apply_plotly_accessibility_theme(fig_perf)
            st.plotly_chart(fig_perf, width="stretch", config=PLOTLY_CONFIG, theme=None)
            _force_plotly_text_contrast()
            st.dataframe(perf_comp, width="stretch", hide_index=True)

    with col_right:
        st.markdown("**Perfil: Cuenta vs Red (demografia base)**")
        if demo_comp.empty:
            st.warning("No hay base suficiente para comparar perfil demografico contra la red.")
        else:
            st.subheader("Grafica comparativa de perfil demografico: cuenta vs red")
            plot_demo = demo_comp.head(8).copy()
            fig_demo = go.Figure()
            fig_demo.add_trace(
                go.Bar(x=plot_demo["segmento"], y=plot_demo["cuenta_pct"], name="Cuenta %", marker_color="#2ca02c")
            )
            fig_demo.add_trace(
                go.Bar(x=plot_demo["segmento"], y=plot_demo["red_pct"], name="Red %", marker_color="#bcbd22")
            )
            fig_demo.update_layout(
                title="Comparacion de perfil demografico: cuenta vs red",
                barmode="group",
                margin={"l": 10, "r": 10, "t": 50, "b": 100},
            )
            fig_demo.update_xaxes(tickangle=-35)
            fig_demo.update_yaxes(rangemode="tozero")
            _apply_plotly_accessibility_theme(fig_demo)
            st.plotly_chart(fig_demo, width="stretch", config=PLOTLY_CONFIG, theme=None)
            _force_plotly_text_contrast()
            st.dataframe(demo_comp, width="stretch", hide_index=True)


def render_cross_intelligence_view() -> None:
    st.title("Vista de Inteligencia Cruzada")
    st.caption("Cruce entre rendimiento historico de contenido y perfil de audiencia")

    colegio, plataforma, month_key = _render_filters()
    if not month_key:
        st.warning("No hay periodos disponibles en Base_Maestra_Colegios ni Base_Demografica_Colegios.")
        return

    historical_mode = str(month_key) == HISTORICAL_KEY
    monthly = None if historical_mode else get_monthly_slice(colegio, plataforma, month_key)
    historical = get_historical_slice(colegio, plataforma)

    if historical_mode:
        maestra_current = historical["maestra_historical"]
        demo_current = historical["demo_historical"]
        maestra_previous = pd.DataFrame(columns=maestra_current.columns)
        maestra_historical = historical["maestra_historical"]
        demo_historical = historical["demo_historical"]
        network_maestra = historical["network_maestra"]
        network_demo = historical["network_demo"]
        prev_month_key = ""
    else:
        maestra_current = monthly["maestra_current"]
        demo_current = monthly["demo_current"]
        maestra_previous = monthly["maestra_previous"]
        maestra_historical = historical["maestra_historical"]
        demo_historical = historical["demo_historical"]
        network_maestra = monthly["network_maestra"]
        network_demo = monthly["network_demo"]
        prev_month_key = monthly.get("prev_month_key", "")

    if maestra_current.empty and demo_current.empty:
        st.warning("No hay datos en el periodo seleccionado para los filtros actuales.")
        return

    if not historical_mode:
        if not maestra_current.empty and demo_current.empty:
            st.warning("Hay datos de rendimiento en el mes seleccionado, pero no hay datos demograficos para ese corte.")

        if maestra_current.empty and not demo_current.empty:
            st.warning("Hay datos demograficos en el mes seleccionado, pero no hay datos de rendimiento para ese corte.")

    st.markdown(f"**Periodo activo:** {month_key_to_label(month_key)}")

    _render_block_1(
        maestra_current,
        maestra_previous,
        maestra_historical,
        demo_current,
        prev_month_key,
    )
    st.markdown("---")
    _render_block_2(maestra_historical, demo_historical, month_key)
    st.markdown("---")
    _render_block_3_drilldown(maestra_current, demo_current, network_maestra, colegio)
    st.markdown("---")
    _render_block_4_strict_comparison(network_maestra, network_demo, colegio)
