"""Vista de Analisis Demografico y Geografico para Chammpileaks."""

from __future__ import annotations

from io import BytesIO
from typing import Dict, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import PLOTLY_CONFIG, ui
from utils.analytics_repository import load_analytics_bases
from utils.chart_theme import aplicar_tema_champileaks
from utils.demographics_geo import (
    CITY_IMPACT_COLORS,
    CITY_IMPACT_MARKER_SIZES,
    CITY_IMPACT_ORDER,
    MEXICO_CENTER,
    AGE_ORDER,
    apply_demographic_filters,
    apply_performance_filters,
    build_city_metric_estimate,
    build_city_report,
    classify_city_impact,
    build_demography_base,
    build_network_comparison,
)


def load_data() -> Dict[str, pd.DataFrame]:
    """Obtiene el snapshot compartido del repositorio analítico."""
    base_maestra, base_demografica = load_analytics_bases()
    return {
        "base_maestra": base_maestra.copy(),
        "base_demografica": base_demografica.copy(),
    }


def _default_date_range(df: pd.DataFrame):
    fechas = pd.to_datetime(df.get("fecha_reporte"), errors="coerce")
    fechas = fechas.dropna()
    if fechas.empty:
        today = pd.Timestamp.today().normalize()
        return today, today
    return fechas.min().normalize(), fechas.max().normalize()


def render_sidebar(df_maestra: pd.DataFrame, df_demografica: pd.DataFrame):
    """Renderiza filtros del analisis en el sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("Analisis Demografico")

        colegios_maestra = []
        if not df_maestra.empty and "colegio" in df_maestra.columns:
            colegios_maestra = sorted(
                [str(c).strip() for c in df_maestra["colegio"].dropna().unique() if str(c).strip()]
            )

        colegios_demografica = []
        if not df_demografica.empty and "colegio" in df_demografica.columns:
            colegios_demografica = sorted(
                [str(c).strip() for c in df_demografica["colegio"].dropna().unique() if str(c).strip()]
            )

        # Unimos ambas fuentes para no perder colegios si una hoja llega parcial.
        colegios = sorted(set(colegios_maestra) | set(colegios_demografica))
        if not colegios:
            colegios = ["Sin datos"]

        colegio = st.selectbox(
            "Colegio",
            options=["Todos"] + colegios,
            key="demogeo_v2_colegio",
        )

        plataformas_df = df_demografica
        if "colegio" in plataformas_df.columns and colegio not in {"Todos", "Sin datos"}:
            plataformas_df = plataformas_df[plataformas_df["colegio"].astype(str) == str(colegio)]

        plataformas = ["Todas"]
        if not plataformas_df.empty and "plataforma" in plataformas_df.columns:
            plataformas += sorted(
                [str(p).strip() for p in plataformas_df["plataforma"].dropna().unique() if str(p).strip()]
            )

        plataforma = st.selectbox(
            "Plataforma",
            options=plataformas,
            key="demogeo_v2_plataforma",
        )

        min_date, max_date = _default_date_range(df_demografica)
        date_range = st.date_input(
            "Rango de fechas (Fecha de Reporte)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="demogeo_fechas",
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        elif isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

    return {
        "colegio": colegio,
        "plataforma": plataforma,
        "start_date": pd.to_datetime(start_date),
        "end_date": pd.to_datetime(end_date),
    }


def render_demography_block(df_filtered: pd.DataFrame):
    """Bloque 1: estructura de audiencia por edad y sexo."""
    st.subheader("Bloque 1 - Estructura de la audiencia")

    demo = build_demography_base(df_filtered)
    if demo.empty:
        st.info("No hay datos de Demografia base para los filtros seleccionados.")
        return

    fig = px.bar(
        demo,
        x="edad",
        y="valor",
        color="sexo",
        barmode="group",
        category_orders={"edad": AGE_ORDER},
        hover_data={"participacion_pct": ":.2f"},
        labels={
            "edad": "Rango de edad",
            "valor": "Valor",
            "sexo": "Sexo",
            "participacion_pct": "% participacion",
        },
        title="Distribucion de audiencia por Edad y Sexo",
    )
    fig.update_layout(
        xaxis_title="Edad",
        yaxis_title="Valor",
        legend_title="Sexo",
        hovermode="x unified",
    )

    st.plotly_chart(aplicar_tema_champileaks(fig), width="stretch", config=PLOTLY_CONFIG)


def _to_excel_bytes(df: pd.DataFrame) -> Tuple[Optional[bytes], Optional[str]]:
    """Exporta DataFrame a XLSX en memoria con fallback cuando falta openpyxl."""
    buffer = BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="reporte_ciudades")
    except ModuleNotFoundError as exc:
        if getattr(exc, "name", "") == "openpyxl":
            return None, "El exportador Excel no esta disponible (falta openpyxl en el entorno)."
        return None, f"No se pudo generar Excel: {exc}"
    except Exception as exc:
        return None, f"No se pudo generar Excel: {exc}"

    buffer.seek(0)
    return buffer.getvalue(), None


def _build_city_impact_map(
    mapped: pd.DataFrame, title: str = "Mapa de ciudades por impacto"
) -> go.Figure:
    """Construye capas de mapa con colores explícitos por nivel de impacto."""
    map_data = mapped.copy()
    map_data["nivel_impacto"] = classify_city_impact(map_data["valor_total"])
    fig = go.Figure()
    for impact_level in CITY_IMPACT_ORDER:
        level_data = map_data[map_data["nivel_impacto"] == impact_level]
        if level_data.empty:
            continue
        fig.add_trace(
            go.Scattermap(
                lat=level_data["lat"],
                lon=level_data["lon"],
                text=level_data["ubicacion"],
                customdata=level_data[
                    ["valor_total", "participacion_pct", "nivel_impacto"]
                ],
                mode="markers",
                name=impact_level,
                marker={
                    "size": CITY_IMPACT_MARKER_SIZES[impact_level],
                    "color": CITY_IMPACT_COLORS[impact_level],
                    "opacity": 0.9,
                },
                hovertemplate=(
                    "<b>%{text}</b><br>Nivel: %{customdata[2]}"
                    "<br>Valor: %{customdata[0]:,.0f}"
                    "<br>Participación: %{customdata[1]:.2f}%<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title=title,
        map={
            "style": "carto-positron",
            "zoom": 4.4,
            "center": MEXICO_CENTER,
        },
        legend_title_text="Nivel de impacto",
    )
    return fig


def _render_metric_city_map(
    df_demo: pd.DataFrame,
    df_performance: pd.DataFrame,
    metric_key: str,
) -> None:
    metric_title = "Interacciones" if metric_key == "interacciones" else "Visualizaciones"
    estimated = build_city_metric_estimate(df_demo, df_performance, metric_key)
    mapped, _ = build_city_report(estimated)
    if mapped.empty:
        st.info(f"No hay datos suficientes para estimar {metric_title.lower()} por ciudad.")
        return

    fig = _build_city_impact_map(
        mapped,
        title=f"Impacto estimado por {metric_title.lower()}",
    )
    st.plotly_chart(
        aplicar_tema_champileaks(fig), width="stretch", config=PLOTLY_CONFIG
    )


def render_map_block(
    df_filtered: pd.DataFrame,
    colegio: str,
    df_performance: Optional[pd.DataFrame] = None,
):
    """Bloque 2: mapa de ciudades y reporte tabular."""
    st.subheader("Bloque 2 - Geolocalizacion interactiva (Mexico)")

    mapped, unmapped = build_city_report(df_filtered)

    if mapped.empty and unmapped.empty:
        st.info("No hay datos de criterio Ciudad para los filtros seleccionados.")
        return

    if not mapped.empty:
        fig = _build_city_impact_map(mapped)
        st.plotly_chart(aplicar_tema_champileaks(fig), width="stretch", config=PLOTLY_CONFIG)
    else:
        st.warning("No hay ciudades con coordenadas disponibles en el diccionario interno.")

    if df_performance is not None and not df_performance.empty:
        st.markdown("#### Mapas de rendimiento estimado")
        st.caption(
            "Estimación: el rendimiento de cada colegio y plataforma se distribuye "
            "entre sus ciudades según la participación demográfica observada. "
            "Interacciones y visualizaciones se calculan por separado."
        )
        col_interactions, col_views = st.columns(2)
        with col_interactions:
            _render_metric_city_map(df_filtered, df_performance, "interacciones")
        with col_views:
            _render_metric_city_map(df_filtered, df_performance, "visualizaciones")

    st.markdown("#### Reporte numerico por ciudad")

    city_report = pd.concat([mapped, unmapped], ignore_index=True)
    city_report = city_report.sort_values("valor_total", ascending=False).reset_index(drop=True)
    city_report.insert(0, "ranking", city_report.index + 1)

    display_cols = ["ranking", "ubicacion", "valor_total", "participacion_pct"]
    st.dataframe(
        city_report[display_cols],
        width="stretch",
        hide_index=True,
        column_config={
            "ranking": st.column_config.NumberColumn("#", format="%d"),
            "ubicacion": st.column_config.TextColumn("Ciudad"),
            "valor_total": st.column_config.NumberColumn("Valor", format="%d"),
            "participacion_pct": st.column_config.NumberColumn("% Participacion", format="%.2f"),
        },
    )

    csv_bytes = city_report[display_cols].to_csv(index=False).encode("utf-8-sig")
    xlsx_bytes, xlsx_error = _to_excel_bytes(city_report[display_cols])

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "Descargar CSV",
            data=csv_bytes,
            file_name=f"reporte_ciudades_{colegio}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_dl2:
        if xlsx_bytes is not None:
            st.download_button(
                "Descargar Excel",
                data=xlsx_bytes,
                file_name=f"reporte_ciudades_{colegio}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.info("Descarga Excel no disponible en este entorno. Usa CSV.")
            if xlsx_error:
                st.caption(xlsx_error)

    if not unmapped.empty:
        st.caption("Ciudades sin coordenadas en diccionario interno: " + ", ".join(unmapped["ubicacion"].tolist()))


def render_comparison_block(df_for_network: pd.DataFrame, colegio: str):
    """Bloque 3: comparacion del colegio contra promedio de red (excluyendolo)."""
    st.subheader("Bloque 3 - Colegio vs Promedio General de la Red")

    comp = build_network_comparison(df_for_network, colegio)
    if comp.empty:
        st.info(
            "No hay suficiente informacion para comparar. "
            "Se requiere Demografia base tanto del colegio seleccionado como del resto de la red."
        )
        return

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=comp["segmento"],
            y=comp["colegio_pct"],
            name=f"{colegio} (%)",
        )
    )
    fig.add_trace(
        go.Bar(
            x=comp["segmento"],
            y=comp["red_pct"],
            name="Promedio red (%)",
        )
    )
    fig.update_layout(
        barmode="group",
        title="Comparacion de distribucion por segmento",
        xaxis_title="Segmento (Edad | Sexo)",
        yaxis_title="Distribucion (%)",
    )
    fig.update_xaxes(tickangle=-35)
    st.plotly_chart(aplicar_tema_champileaks(fig), width="stretch", config=PLOTLY_CONFIG)

    table = comp[["edad", "sexo", "colegio_pct", "red_pct", "delta_pp"]].copy()
    table = table.sort_values("delta_pp", key=lambda s: s.abs(), ascending=False)

    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "edad": st.column_config.TextColumn("Edad"),
            "sexo": st.column_config.TextColumn("Sexo"),
            "colegio_pct": st.column_config.NumberColumn("Colegio %", format="%.2f"),
            "red_pct": st.column_config.NumberColumn("Red %", format="%.2f"),
            "delta_pp": st.column_config.NumberColumn("Delta pp", format="%.2f"),
        },
    )


def render_demographic_geographic_analysis() -> None:
    """Render principal de la pestaña de analisis demografico y geografico."""
    st.title("Analisis Demografico y Geografico")
    st.caption("Fuente: Google Sheets - Base_Maestra_Colegios y Base_Demografica_Colegios")

    data = load_data()
    df_maestra = data["base_maestra"]
    df_demografica = data["base_demografica"]

    if df_demografica.empty:
        ui.render_empty_state(
            "**No hay información demográfica disponible**  \n"
            "Verifica la hoja Base_Demografica_Colegios y vuelve a sincronizar los datos.",
            tipo="geo",
        )
        return

    filters = render_sidebar(df_maestra, df_demografica)
    colegio = filters["colegio"]

    df_selected = apply_demographic_filters(
        df_demografica,
        colegio=colegio if colegio != "Sin datos" else None,
        plataforma=filters["plataforma"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
    )

    df_network_scope = apply_demographic_filters(
        df_demografica,
        colegio=None,
        plataforma=filters["plataforma"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
    )
    df_performance_network = apply_performance_filters(
        df_maestra,
        colegio="Todos",
        plataforma=filters["plataforma"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
    )

    if df_network_scope.empty:
        ui.render_empty_state(
            "**No hay datos en el rango seleccionado**  \n"
            "Cambia la plataforma o amplía el periodo para consultar la red.",
            tipo="geo",
        )
        return

    if df_selected.empty:
        ui.render_empty_state("No hay datos para esta selección", tipo="geo")
        return

    metrics_df = df_selected if not df_selected.empty else df_network_scope
    top_left, top_right = st.columns(2)
    with top_left:
        st.metric("Registros filtrados", f"{len(metrics_df):,}")
    with top_right:
        total_valor = pd.to_numeric(metrics_df["valor"], errors="coerce").fillna(0).sum()
        st.metric("Valor total", f"{total_valor:,.0f}")

    tab_demo, tab_geo, tab_comp = st.tabs(
        [
            "Estructura de audiencia",
            "Mapa y reporte de ciudades",
            "Comparacion con red",
        ]
    )

    with tab_demo:
        if df_selected.empty:
            st.info("No hay datos de demografia base para el colegio seleccionado en este rango.")
        else:
            render_demography_block(df_selected)

    with tab_geo:
        colegios_mapa = []
        if "colegio" in df_network_scope.columns:
            colegios_mapa = sorted(
                [str(c).strip() for c in df_network_scope["colegio"].dropna().unique() if str(c).strip()]
            )

        mapa_mode = st.radio(
            "Modo de mapa",
            options=["General", "Por colegio"],
            horizontal=True,
            key="demogeo_mapa_mode",
            help="Cambia rapido entre vista general de la red o vista por colegio.",
        )

        if mapa_mode == "General":
            df_map = df_network_scope
            df_performance_map = df_performance_network
            mapa_label = "General_Red"
        else:
            if not colegios_mapa:
                st.info("No hay colegios disponibles para vista por colegio con los filtros actuales.")
                df_map = pd.DataFrame()
                df_performance_map = pd.DataFrame()
                mapa_label = "Sin_datos"
            else:
                default_school_index = colegios_mapa.index(colegio) if colegio in colegios_mapa else 0
                mapa_scope = st.selectbox(
                    "Colegio para mapa",
                    options=colegios_mapa,
                    index=default_school_index,
                    key="demogeo_mapa_scope",
                    help="Selecciona un colegio especifico para ver solo sus ciudades en el mapa.",
                )
                df_map = df_network_scope[df_network_scope["colegio"].astype(str) == str(mapa_scope)].copy()
                df_performance_map = df_performance_network[
                    df_performance_network["colegio"].astype(str) == str(mapa_scope)
                ].copy()
                mapa_label = mapa_scope

        if df_map.empty:
            st.info("No hay datos de ciudad para la seleccion de mapa actual.")
        else:
            render_map_block(df_map, mapa_label, df_performance_map)

    with tab_comp:
        colegios_comp = []
        if not df_network_scope.empty and "colegio" in df_network_scope.columns:
            colegios_comp = sorted(
                [str(c).strip() for c in df_network_scope["colegio"].dropna().unique() if str(c).strip()]
            )

        if not colegios_comp:
            st.info("No hay colegios disponibles para comparar con la red en los filtros actuales.")
            return

        default_comp_index = colegios_comp.index(colegio) if colegio in colegios_comp else 0
        colegio_comp = st.selectbox(
            "Colegio para comparar con la red",
            options=colegios_comp,
            index=default_comp_index,
            key="demogeo_comp_colegio",
            help="Selecciona el colegio que quieres contrastar contra el promedio de la red.",
        )

        render_comparison_block(df_network_scope, colegio_comp)
