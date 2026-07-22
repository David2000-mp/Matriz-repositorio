"""Vista de Inteligencia Cruzada para Chammpileaks."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components import PLOTLY_CONFIG, ui
from utils.chart_theme import (
    AMARILLO_MARISTA,
    ESCALA_IMPACTO_AMARILLA,
    aplicar_tema_champileaks,
)
from utils.cross_intelligence import (
    build_cohort_series,
    build_city_performance_drilldown,
    build_demographic_vs_network,
    build_historical_performance_series,
    build_performance_vs_network,
    build_school_ranking,
    build_segment_distribution,
    build_segmented_performance,
    calculate_demographic_performance_correlation,
    calculate_metric_delta,
    calculate_metric_total,
    get_filter_catalogs,
    get_historical_slice,
    get_month_bounds,
    get_monthly_slice,
    get_top_city,
    month_key_to_label,
    HISTORICAL_KEY,
)
from utils.metric_catalog import metric_label


def _metric_value(value: float) -> str:
    return f"{value:,.0f}"


def _metric_delta_text(current: float, previous: float, delta_abs: float, delta_pct: float | None) -> str:
    if previous <= 0:
        return "Sin base previa"
    if delta_pct is None:
        return f"{delta_abs:+,.0f}"
    return f"{delta_abs:+,.0f} ({delta_pct:+.1f}%)"


def _render_filters() -> tuple[str, str, str, str, str, str]:
    catalogs = get_filter_catalogs()
    month_keys = catalogs.get("month_keys", [])

    if not month_keys:
        return "Todos", "Todas", "", "interacciones", "Todos", "Todos"

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

        metric_key = st.selectbox(
            "Métrica de rendimiento",
            options=catalogs.get("metric_keys", ["interacciones"]),
            format_func=metric_label,
            key="cross_metric",
        )

        sexo = st.selectbox(
            "Sexo",
            options=["Todos"] + catalogs.get("sexos", []),
            key="cross_sex",
        )

        edad = st.selectbox(
            "Rango de edad",
            options=["Todos"] + catalogs.get("edades", []),
            key="cross_age",
        )

        month_key = st.selectbox(
            "Mes/Ano",
            options=month_keys,
            format_func=month_key_to_label,
            key="cross_month_key",
        )

    return colegio, plataforma, month_key, metric_key, sexo, edad


def _render_block_1(
    maestra_current,
    maestra_previous,
    maestra_historical,
    demo_current,
    prev_month_key: str,
    metric_key: str,
    sexo: str,
    edad: str,
) -> None:
    st.subheader("Bloque 1 - Rendimiento y audiencia segmentada")

    selected_kpi = calculate_metric_delta(maestra_current, maestra_previous, metric_key)
    historical_total = calculate_metric_total(maestra_historical, metric_key)
    segmented = build_segmented_performance(
        maestra_current, demo_current, metric_key, sexo, edad
    )
    top_city = get_top_city(demo_current)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**Métrica seleccionada**")
            st.metric(
                metric_label(metric_key),
                _metric_value(selected_kpi.current),
                delta=_metric_delta_text(
                    selected_kpi.current,
                    selected_kpi.previous,
                    selected_kpi.delta_abs,
                    selected_kpi.delta_pct,
                ),
            )
            st.caption(f"Acumulado histórico: {_metric_value(historical_total)}")

            if prev_month_key:
                st.caption(f"Delta vs {month_key_to_label(prev_month_key)}")
            else:
                st.caption("Delta: sin mes previo disponible")

    with col2:
        with st.container(border=True):
            st.markdown("**Segmentación activa**")
            segment_name = f"{sexo} | {edad}"
            if segmented.empty:
                st.warning("No hay cruce entre rendimiento y demografía para el segmento.")
            else:
                segment_share = (
                    segmented["volumen_segmento"].sum()
                    / segmented["volumen_demografico_total"].sum()
                    * 100.0
                    if segmented["volumen_demografico_total"].sum() > 0
                    else 0.0
                )
                st.metric("Segmento", segment_name)
                st.caption(f"Participación demográfica: {segment_share:.1f}%")

    with col3:
        with st.container(border=True):
            st.markdown("**Ciudad Principal de Alcance**")
            if top_city is None:
                st.warning("No hay datos de ciudad para el mes seleccionado.")
            else:
                st.metric("Ciudad", str(top_city["ciudad"]))
                st.caption(f"Participacion: {top_city['pct']:.1f}%")


def _render_block_2(
    maestra_historical,
    demo_historical,
    month_key: str,
    metric_key: str,
    sexo: str,
    edad: str,
) -> None:
    st.subheader("Bloque 2 - Correlación estadística y cohortes")
    segment_name = f"{sexo} | {edad}"
    tab_correlation, tab_cohort, tab_trend = st.tabs(
        ["Correlación", "Cohorte mensual", "Tendencia de rendimiento"]
    )

    with tab_correlation:
        method = st.radio(
            "Método estadístico",
            options=["pearson", "spearman"],
            format_func=lambda value: value.capitalize(),
            horizontal=True,
            key="cross_correlation_method",
        )
        result = calculate_demographic_performance_correlation(
            maestra_historical,
            demo_historical,
            metric_key,
            sexo,
            edad,
            method,
        )

        col_coefficient, col_sample = st.columns(2)
        coefficient_text = (
            f"{result.coefficient:.3f}" if result.coefficient is not None else "N/D"
        )
        col_coefficient.metric(f"Coeficiente {method.capitalize()}", coefficient_text)
        col_sample.metric("Meses comparables (n)", result.sample_size)
        st.caption(result.interpretation)

        if result.series.empty:
            st.warning("No hay meses coincidentes entre demografía y rendimiento.")
        else:
            fig_correlation = go.Figure(
                go.Scatter(
                    x=result.series["volumen_demografico"],
                    y=result.series["rendimiento"],
                    text=result.series["month_key"],
                    mode="markers+text",
                    textposition="top center",
                    marker={
                        "size": 13,
                        "color": result.series["rendimiento"],
                        "colorscale": ESCALA_IMPACTO_AMARILLA,
                        "showscale": True,
                    },
                    name=metric_label(metric_key),
                )
            )
            fig_correlation.update_layout(
                title=f"{metric_label(metric_key)} vs volumen demográfico · {segment_name}",
                xaxis_title="Volumen demográfico del segmento",
                yaxis_title=metric_label(metric_key),
            )
            fig_correlation.update_xaxes(rangemode="tozero")
            fig_correlation.update_yaxes(rangemode="tozero")
            st.plotly_chart(
                aplicar_tema_champileaks(fig_correlation),
                width="stretch",
                config=PLOTLY_CONFIG,
            )

    with tab_cohort:
        cohort = build_cohort_series(demo_historical, sexo, edad)
        if cohort.empty:
            st.warning("No hay historial demográfico para esta cohorte.")
        else:
            fig_cohort = go.Figure(
                go.Scatter(
                    x=cohort["month_date"],
                    y=cohort["participacion_pct"],
                    mode="lines+markers",
                    line={"color": AMARILLO_MARISTA, "width": 4},
                    marker={"size": 9, "color": "#6B3F00"},
                    name=segment_name,
                )
            )
            fig_cohort.update_layout(
                title=f"Evolución mensual de la cohorte · {segment_name}",
                xaxis_title="Mes",
                yaxis_title="Participación demográfica (%)",
            )
            fig_cohort.update_yaxes(range=[0, 100], rangemode="tozero")
            st.plotly_chart(
                aplicar_tema_champileaks(fig_cohort),
                width="stretch",
                config=PLOTLY_CONFIG,
            )
            st.dataframe(cohort, width="stretch", hide_index=True)

    with tab_trend:
        performance = build_historical_performance_series(maestra_historical)
        if performance.empty:
            st.warning("No hay historial de rendimiento para la métrica seleccionada.")
        else:
            fig_trend = go.Figure(
                go.Scatter(
                    x=performance["month_date"],
                    y=performance[metric_key],
                    mode="lines+markers",
                    line={"color": AMARILLO_MARISTA, "width": 4},
                    marker={"size": 9, "color": "#6B3F00"},
                    name=metric_label(metric_key),
                )
            )
            month_start, month_end = get_month_bounds(month_key)
            if month_start is not None and month_end is not None:
                fig_trend.add_vrect(
                    x0=month_start,
                    x1=month_end,
                    fillcolor="#FFD91A",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    annotation_text=month_key_to_label(month_key),
                )
            fig_trend.update_layout(
                title=f"Tendencia mensual · {metric_label(metric_key)}",
                xaxis_title="Mes",
                yaxis_title=metric_label(metric_key),
            )
            fig_trend.update_yaxes(rangemode="tozero")
            st.plotly_chart(
                aplicar_tema_champileaks(fig_trend),
                width="stretch",
                config=PLOTLY_CONFIG,
            )


def _render_block_3_drilldown(
    maestra_current,
    demo_current,
    network_maestra,
    selected_college: str,
    metric_key: str,
    sexo: str,
    edad: str,
) -> None:
    st.subheader("Bloque 3 - Desglose Multidimensional")
    tab_city, tab_school, tab_segment, tab_cross = st.tabs(
        [
            "Desglose por Ciudad",
            "Desglose por Colegio",
            "Distribución demográfica",
            "Segmentación cruzada",
        ]
    )

    with tab_city:
        city_rank = build_city_performance_drilldown(
            maestra_current, demo_current, metric_key
        )
        if city_rank.empty:
            st.warning("No hay datos suficientes para construir el desglose por ciudad en este mes.")
        else:
            st.subheader("Grafica: rendimiento estimado por ciudad")
            show = city_rank.head(12).iloc[::-1]
            fig_city = go.Figure(
                go.Bar(
                    y=show["ciudad"],
                    x=show["rendimiento_estimado"],
                    name=f"{metric_label(metric_key)} est.",
                    orientation="h",
                    marker={
                        "color": show["rendimiento_estimado"],
                        "colorscale": ESCALA_IMPACTO_AMARILLA,
                    },
                )
            )
            fig_city.update_layout(
                title=f"Impacto estimado por ciudad · {metric_label(metric_key)}"
            )
            fig_city.update_xaxes(rangemode="tozero")
            st.plotly_chart(aplicar_tema_champileaks(fig_city), width="stretch", config=PLOTLY_CONFIG)

            table_city = city_rank.copy()
            table_city["city_pct"] = table_city["city_pct"] * 100.0
            st.dataframe(table_city, width="stretch", hide_index=True)

    with tab_school:
        school_rank = build_school_ranking(network_maestra, metric_key)
        if school_rank.empty:
            st.warning("No hay datos suficientes para construir el ranking por colegio en este mes.")
        else:
            if selected_college != "Todos":
                st.info(
                    "Filtro de colegio especifico activo. Se muestra ranking de red del mes como contexto comparativo."
                )

            st.subheader(f"Gráfica: ranking por {metric_label(metric_key).lower()}")
            show = school_rank.head(12).iloc[::-1]
            fig_school = go.Figure()
            fig_school.add_trace(
                go.Bar(
                    y=show["colegio"],
                    x=show["rendimiento"],
                    orientation="h",
                    name=metric_label(metric_key),
                    marker_color=AMARILLO_MARISTA,
                )
            )
            fig_school.update_layout(
                title=f"Ranking de colegios · {metric_label(metric_key)}",
            )
            fig_school.update_xaxes(rangemode="tozero")
            st.plotly_chart(aplicar_tema_champileaks(fig_school), width="stretch", config=PLOTLY_CONFIG)
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
                yaxis_title="Participacion (%)",
                xaxis_title="Rango de edad",
            )
            fig_segment.update_yaxes(rangemode="tozero")
            st.plotly_chart(aplicar_tema_champileaks(fig_segment), width="stretch", config=PLOTLY_CONFIG)
            st.dataframe(segment_dist, width="stretch", hide_index=True)

    with tab_cross:
        segmented = build_segmented_performance(
            maestra_current, demo_current, metric_key, sexo, edad
        )
        st.caption(
            "Estimación = rendimiento observado × participación demográfica del "
            "segmento en el mismo mes, colegio y plataforma."
        )
        if segmented.empty:
            st.warning("No hay datos coincidentes para la segmentación seleccionada.")
        else:
            fig_cross = go.Figure(
                go.Bar(
                    x=segmented["plataforma"],
                    y=segmented["rendimiento_segmentado_estimado"],
                    marker={
                        "color": segmented["rendimiento_segmentado_estimado"],
                        "colorscale": ESCALA_IMPACTO_AMARILLA,
                    },
                    name=f"{metric_label(metric_key)} estimadas",
                )
            )
            fig_cross.update_layout(
                title=f"{metric_label(metric_key)} · {sexo} | {edad}",
                xaxis_title="Plataforma",
                yaxis_title="Rendimiento segmentado estimado",
            )
            fig_cross.update_yaxes(rangemode="tozero")
            st.plotly_chart(
                aplicar_tema_champileaks(fig_cross),
                width="stretch",
                config=PLOTLY_CONFIG,
            )
            st.dataframe(segmented, width="stretch", hide_index=True)


def _render_block_4_strict_comparison(
    network_maestra, network_demo, colegio: str, metric_key: str
) -> None:
    st.subheader("Bloque 4 - Cuenta vs Promedio de la Red (Regla Estricta)")

    if not colegio or colegio == "Todos":
        st.info("Selecciona un colegio especifico para habilitar la comparacion estricta contra la red.")
        return

    perf_comp = build_performance_vs_network(network_maestra, colegio, metric_key)
    demo_comp = build_demographic_vs_network(network_demo, colegio)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            f"**{metric_label(metric_key)}: Cuenta vs Red (promedio)**"
        )
        if perf_comp.empty:
            st.warning("No hay base suficiente para comparar rendimiento contra la red.")
        else:
            st.subheader("Grafica comparativa de rendimiento: cuenta vs red promedio")
            fig_perf = go.Figure()
            fig_perf.add_trace(
                go.Bar(x=perf_comp["metrica"], y=perf_comp["cuenta"], name="Cuenta")
            )
            fig_perf.add_trace(
                go.Bar(
                    x=perf_comp["metrica"],
                    y=perf_comp["red_promedio"],
                    name="Red promedio",
                )
            )
            fig_perf.update_layout(
                title="Comparacion de rendimiento: cuenta vs red promedio",
                barmode="group",
            )
            fig_perf.update_yaxes(rangemode="tozero")
            st.plotly_chart(aplicar_tema_champileaks(fig_perf), width="stretch", config=PLOTLY_CONFIG)
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
                go.Bar(x=plot_demo["segmento"], y=plot_demo["cuenta_pct"], name="Cuenta %")
            )
            fig_demo.add_trace(
                go.Bar(x=plot_demo["segmento"], y=plot_demo["red_pct"], name="Red %")
            )
            fig_demo.update_layout(
                title="Comparacion de perfil demografico: cuenta vs red",
                barmode="group",
            )
            fig_demo.update_xaxes(tickangle=-35)
            fig_demo.update_yaxes(rangemode="tozero")
            st.plotly_chart(aplicar_tema_champileaks(fig_demo), width="stretch", config=PLOTLY_CONFIG)
            st.dataframe(demo_comp, width="stretch", hide_index=True)


def render_cross_intelligence_view() -> None:
    st.title("Vista de Inteligencia Cruzada")
    st.caption("Cruce entre rendimiento historico de contenido y perfil de audiencia")

    colegio, plataforma, month_key, metric_key, sexo, edad = _render_filters()
    if not month_key:
        ui.render_empty_state(
            "**No hay periodos disponibles**  \n"
            "Sincroniza Base_Maestra_Colegios o Base_Demografica_Colegios para activar esta vista.",
            tipo="search",
        )
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
        ui.render_empty_state("No hay datos para esta selección", tipo="search")
        return

    if not historical_mode:
        if not maestra_current.empty and demo_current.empty:
            st.warning("Hay datos de rendimiento en el mes seleccionado, pero no hay datos demograficos para ese corte.")

        if maestra_current.empty and not demo_current.empty:
            st.warning("Hay datos demograficos en el mes seleccionado, pero no hay datos de rendimiento para ese corte.")

    st.markdown(f"**Periodo activo:** {month_key_to_label(month_key)}")
    st.caption(
        f"Métrica: {metric_label(metric_key)} · Plataforma: {plataforma} · "
        f"Segmento: {sexo} | {edad}"
    )

    _render_block_1(
        maestra_current,
        maestra_previous,
        maestra_historical,
        demo_current,
        prev_month_key,
        metric_key,
        sexo,
        edad,
    )
    st.markdown("---")
    _render_block_2(
        maestra_historical,
        demo_historical,
        month_key,
        metric_key,
        sexo,
        edad,
    )
    st.markdown("---")
    _render_block_3_drilldown(
        maestra_current,
        demo_current,
        network_maestra,
        colegio,
        metric_key,
        sexo,
        edad,
    )
    st.markdown("---")
    _render_block_4_strict_comparison(
        network_maestra, network_demo, colegio, metric_key
    )
