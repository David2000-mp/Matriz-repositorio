"""
Vista de Tipo de contenidos para CHAMPILEAKS.
Sección adicional para visualizar campos nuevos del formulario sin reemplazar vistas existentes.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

from components import PLOTLY_CONFIG, PLOTLY_LAYOUT_DEFAULTS
from utils.data_provider import data_provider


NEW_NUMERIC_COLS = [
    "media_visualizaciones",
    "engagement_contenido_imagenes",
    "engagement_contenido_links",
    "engagement_contenido_videos",
    "engagement_tema_mas_visto",
    "publicaciones_por_semana",
]

COLUMN_LABELS = {
    "fecha": "Fecha",
    "entidad": "Entidad",
    "plataforma": "Plataforma",
    "tema_mas_visto": "Tema mas visto",
    "tema_principal": "Tema principal",
    "tuvo_cambios_operacionales": "Hubo cambios operacionales",
    "publicacion_destacada": "Publicacion destacada",
    "top_5_publicaciones": "Top 5 publicaciones",
    "comentarios_consolidados": "Comentarios",
    "media_visualizaciones": "Media visualizaciones",
    "engagement_contenido_imagenes": "Engagement imagenes (%)",
    "engagement_contenido_links": "Engagement links (%)",
    "engagement_contenido_videos": "Engagement videos (%)",
    "engagement_tema_mas_visto": "Engagement tema mas visto (%)",
    "publicaciones_por_semana": "Publicaciones por semana",
}

KPI_SPECS = [
    ("media_visualizaciones", "Media visualizaciones", "number"),
    ("engagement_contenido_imagenes", "Engagement imagenes", "percent"),
    ("engagement_contenido_videos", "Engagement videos", "percent"),
    ("publicaciones_por_semana", "Publicaciones/semana", "number"),
]

METRIC_THRESHOLDS = {
    "media_visualizaciones": (500.0, 1000.0),
    "engagement_contenido_imagenes": (1.0, 3.0),
    "engagement_contenido_videos": (1.0, 3.0),
    "publicaciones_por_semana": (2.0, 5.0),
}

METRIC_COLOR_MAP = {
    "engagement_rate": "#003696",
    "engagement_contenido_imagenes": "#C13584",
    "engagement_contenido_links": "#0A66C2",
    "engagement_contenido_videos": "#FF0000",
    "engagement_tema_mas_visto": "#CC7000",
}

COMPARISON_METRICS = [
    "engagement_contenido_imagenes",
    "engagement_contenido_links",
    "engagement_contenido_videos",
    "engagement_tema_mas_visto",
]

MAPS_PLATFORM_ALIASES = {
    "googlemaps",
    "googlemap",
    "google maps",
    "maps",
}

MAPS_STOPWORDS = {
    "de",
    "la",
    "el",
    "los",
    "las",
    "y",
    "en",
    "que",
    "con",
    "para",
    "por",
    "del",
    "una",
    "un",
    "muy",
    "pero",
    "como",
    "mas",
    "esta",
    "este",
    "es",
    "se",
    "al",
}

URL_ONLY_PATTERN = re.compile(r"^(https?://|www\.)", re.IGNORECASE)


def _normalize_platform_name(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip().lower().replace("_", " ")
    return " ".join(text.split())


def _is_maps_platform(value: object) -> bool:
    normalized = _normalize_platform_name(value)
    if not normalized:
        return False
    compact = normalized.replace(" ", "")
    return normalized in MAPS_PLATFORM_ALIASES or compact in MAPS_PLATFORM_ALIASES


def _split_social_vs_maps(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "plataforma" not in df.columns or df.empty:
        return df.copy(), pd.DataFrame(columns=df.columns)

    is_maps = df["plataforma"].map(_is_maps_platform)
    return df[~is_maps].copy(), df[is_maps].copy()


def _render_google_maps_section(maps_df: pd.DataFrame) -> None:
    st.markdown("---")
    st.subheader("Analisis de Google Maps")
    st.caption("Google Maps se analiza por separado del rendimiento de redes sociales.")

    if maps_df.empty:
        st.info("No hay registros de Google Maps para los filtros seleccionados.")
        return

    c1, c2 = st.columns(2)
    with c1:
        if "calificacion_redes" in maps_df.columns:
            ratings = pd.to_numeric(maps_df["calificacion_redes"], errors="coerce").dropna()
            if not ratings.empty:
                st.metric("Calificacion promedio en Maps", f"{ratings.mean():.2f}/10")
            else:
                st.metric("Calificacion promedio en Maps", "N/A")
        else:
            st.metric("Calificacion promedio en Maps", "N/A")
    with c2:
        st.metric("Registros de Maps", f"{len(maps_df):,}")

    st.markdown("**Analisis de comentarios (Google Maps)**")
    if "comentarios_consolidados" not in maps_df.columns:
        st.info("No existe la columna comentarios_consolidados en los datos de Maps.")
        return

    comments_source = maps_df[[col for col in ["fecha", "entidad", "comentarios_consolidados"] if col in maps_df.columns]].copy()
    comments_source["comentarios_consolidados"] = comments_source["comentarios_consolidados"].fillna("").astype(str).str.strip()
    comments_source = comments_source[comments_source["comentarios_consolidados"] != ""]

    if comments_source.empty:
        st.info("No hay comentarios de Google Maps disponibles para analizar.")
        return

    comments_df = comments_source.rename(columns={"comentarios_consolidados": "comentario"})
    comments_df["comentario"] = comments_df["comentario"].astype(str).str.replace("\n", " ", regex=False).str.strip()
    comments_df = comments_df[comments_df["comentario"] != ""]
    comments_df = comments_df.drop_duplicates(subset=["comentario"]).reset_index(drop=True)

    # Excluir filas que son solo enlaces (común en cargas de evidencia/Drive).
    link_only_mask = comments_df["comentario"].str.match(URL_ONLY_PATTERN)
    link_only_count = int(link_only_mask.sum())
    comments_df = comments_df[~link_only_mask].copy()

    if comments_df.empty:
        if link_only_count > 0:
            st.info(
                "Los registros de comentarios en Google Maps son enlaces/URLs y no texto de reseñas. "
                "No se puede ejecutar análisis textual con ese formato."
            )
        else:
            st.info("Los comentarios de Google Maps no tienen texto util para analizar.")
        return

    words = (
        comments_df["comentario"]
        .str.lower()
        .str.replace(r"[^a-z0-9\s]", " ", regex=True)
        .str.split()
        .explode()
    )
    words = words.dropna().astype(str)
    words = words[(words.str.len() >= 4) & (~words.isin(MAPS_STOPWORDS))]
    top_terms = words.value_counts().head(10).reset_index()
    top_terms.columns = ["Termino", "Frecuencia"]

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Comentarios validos", f"{len(comments_df):,}")
    with m2:
        st.metric("Longitud promedio", f"{comments_df['comentario'].str.len().mean():.0f} caracteres")

    if not top_terms.empty:
        st.markdown("**Top terminos frecuentes**")
        st.dataframe(top_terms, width="stretch", hide_index=True)

    if "fecha" in comments_df.columns:
        comments_df["fecha"] = pd.to_datetime(comments_df["fecha"], errors="coerce")
        comments_df = comments_df.sort_values("fecha", ascending=False)

    preview_cols = [col for col in ["fecha", "entidad", "comentario"] if col in comments_df.columns]
    st.markdown("**Comentarios recientes**")
    st.dataframe(comments_df[preview_cols].head(20), width="stretch", hide_index=True)


def _render_institution_rankings(df: pd.DataFrame, plataforma_sel: str) -> None:
    if "entidad" not in df.columns:
        return

    ranking_df = df.copy()
    if plataforma_sel != "Todas" and "plataforma" in ranking_df.columns:
        ranking_df = ranking_df[ranking_df["plataforma"].astype(str) == str(plataforma_sel)]

    ranking_df = ranking_df.dropna(subset=["entidad"])
    ranking_df = ranking_df[ranking_df["entidad"].astype(str).str.strip() != ""]
    if ranking_df.empty:
        return

    st.subheader("Ranking de rendimiento por institución")
    top_n = st.selectbox(
        "Cantidad de instituciones en ranking",
        options=[10, 15, 20],
        index=1,
        key="tipo_rank_top_n",
    )

    # Ranking 1: score compuesto promedio de contenido por institución
    score_components = [col for col in COMPARISON_METRICS if col in ranking_df.columns]
    if score_components:
        score_source = ranking_df.copy()
        score_source["score_contenido"] = score_source[score_components].mean(axis=1, skipna=True)
        score_source = score_source.dropna(subset=["score_contenido"])

        if not score_source.empty:
            rank_general = (
                score_source.groupby("entidad", as_index=False)
                .agg(
                    score_promedio=("score_contenido", "mean"),
                    registros=("score_contenido", "count"),
                )
                .sort_values("score_promedio", ascending=False)
                .head(int(top_n))
            )

            fig_rank_general = px.bar(
                rank_general.sort_values("score_promedio", ascending=True),
                x="score_promedio",
                y="entidad",
                orientation="h",
                color="registros",
                title="Ranking general de contenido (score compuesto)",
                color_continuous_scale=[[0.0, "#CC7000"], [1.0, "#003696"]],
            )
            fig_rank_general.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
            _apply_dark_chart_text(fig_rank_general)
            st.plotly_chart(
                fig_rank_general,
                width="stretch",
                config=PLOTLY_CONFIG,
                key="tipo_rank_general_instituciones",
            )

            # Tabla de resumen con posicion, medalla y variacion mensual por institucion.
            if "fecha" in score_source.columns:
                score_source["fecha"] = pd.to_datetime(score_source["fecha"], errors="coerce")
                score_source = score_source.dropna(subset=["fecha"])

                if not score_source.empty:
                    score_source["mes"] = score_source["fecha"].dt.to_period("M").dt.to_timestamp()
                    monthly_entity_score = (
                        score_source.groupby(["entidad", "mes"], as_index=False)
                        .agg(score_mensual=("score_contenido", "mean"))
                    )

                    summary_rows = []
                    rank_general_with_pos = rank_general.reset_index(drop=True).copy()
                    rank_general_with_pos["posicion"] = rank_general_with_pos.index + 1

                    for _, row in rank_general_with_pos.iterrows():
                        entidad = row["entidad"]
                        entidad_monthly = monthly_entity_score[monthly_entity_score["entidad"] == entidad].sort_values("mes")

                        latest_score = None
                        prev_score = None
                        if not entidad_monthly.empty:
                            latest_score = float(entidad_monthly.iloc[-1]["score_mensual"])
                            if len(entidad_monthly) >= 2:
                                prev_score = float(entidad_monthly.iloc[-2]["score_mensual"])

                        mom_variation = None
                        if latest_score is not None and prev_score is not None and prev_score != 0.0:
                            mom_variation = ((latest_score - prev_score) / abs(prev_score)) * 100.0

                        trend = "→"
                        if mom_variation is not None:
                            if mom_variation > 1.0:
                                trend = "↑"
                            elif mom_variation < -1.0:
                                trend = "↓"

                        pos = int(row["posicion"])
                        medal = ""
                        if pos == 1:
                            medal = "🥇"
                        elif pos == 2:
                            medal = "🥈"
                        elif pos == 3:
                            medal = "🥉"

                        summary_rows.append(
                            {
                                "Posición": pos,
                                "Medalla": medal,
                                "Institución": entidad,
                                "Score promedio": round(float(row["score_promedio"]), 2),
                                "Registros": int(row["registros"]),
                                "Variación MoM (%)": round(float(mom_variation), 2) if mom_variation is not None else "N/A",
                                "Tendencia": trend,
                            }
                        )

                    if summary_rows:
                        st.markdown("**Tabla resumen del ranking institucional**")
                        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

    # Ranking 2: ranking por formato de contenido elegido
    available_formats = [col for col in COMPARISON_METRICS if col in ranking_df.columns]
    if available_formats:
        format_options = {COLUMN_LABELS.get(col, col): col for col in available_formats}
        selected_format_label = st.selectbox(
            "Formato para ranking específico",
            options=list(format_options.keys()),
            key="tipo_rank_formato_selector",
        )
        selected_format_col = format_options[selected_format_label]

        rank_format = (
            ranking_df.groupby("entidad", as_index=False)[selected_format_col]
            .mean(numeric_only=True)
            .dropna(subset=[selected_format_col])
            .sort_values(selected_format_col, ascending=False)
            .head(int(top_n))
        )

        if not rank_format.empty:
            fig_rank_format = px.bar(
                rank_format.sort_values(selected_format_col, ascending=True),
                x=selected_format_col,
                y="entidad",
                orientation="h",
                title=f"Ranking por institución - {selected_format_label}",
                color_discrete_sequence=["#003696"],
            )
            fig_rank_format.update_layout(**{**PLOTLY_LAYOUT_DEFAULTS, "showlegend": False})
            _apply_dark_chart_text(fig_rank_format)
            st.plotly_chart(
                fig_rank_format,
                width="stretch",
                config=PLOTLY_CONFIG,
                key=f"tipo_rank_formato_{selected_format_col}",
            )


def _to_numeric_safe(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    result = df.copy()
    for col in cols:
        if col in result.columns:
            result[col] = (
                result[col]
                .astype(str)
                .str.replace("%", "", regex=False)
                .str.replace("\u00a0", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            result[col] = pd.to_numeric(result[col], errors="coerce")
    return result


def _monthly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["fecha"] = pd.to_datetime(tmp["fecha"], errors="coerce")
    tmp = tmp.dropna(subset=["fecha"])
    if tmp.empty:
        return tmp

    tmp["mes"] = tmp["fecha"].dt.to_period("M").dt.to_timestamp()

    agg_cols = [col for col in ["engagement_rate", *NEW_NUMERIC_COLS] if col in tmp.columns]
    if not agg_cols:
        return pd.DataFrame()

    monthly = (
        tmp.groupby("mes", as_index=False)[agg_cols]
        .mean(numeric_only=True)
        .sort_values("mes")
    )
    return monthly


def _non_empty_ratio(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    if pd.api.types.is_numeric_dtype(series):
        return float(series.notna().mean())
    normalized = series.fillna("").astype(str).str.strip()
    return float((normalized != "").mean())


def _delta_percentage(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None:
        return None
    if pd.isna(current) or pd.isna(previous):
        return None
    if float(previous) == 0.0:
        return None
    return ((float(current) - float(previous)) / abs(float(previous))) * 100.0


def _health_emoji(metric_key: str, value: float | None) -> str:
    if value is None or pd.isna(value):
        return "⚪"
    yellow, green = METRIC_THRESHOLDS.get(metric_key, (0.0, 1.0))
    if value >= green:
        return "🟢"
    if value >= yellow:
        return "🟡"
    return "🔴"


def _format_metric(value: float | None, value_type: str) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if value_type == "percent":
        return f"{value:,.2f}%"
    return f"{value:,.2f}"


def _resolve_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    entidad_global = st.session_state.get("filtro_entidad", "Todas")
    mes_global = st.session_state.get("filtro_mes", "Todos")

    if entidad_global != "Todas" and "entidad" in result.columns:
        result = result[result["entidad"].astype(str) == str(entidad_global)]

    if mes_global != "Todos" and "fecha" in result.columns:
        fechas = pd.to_datetime(result["fecha"], errors="coerce")
        periodos = fechas.dt.strftime("%Y-%m")
        result = result[periodos == str(mes_global)]

    return result


def _render_data_quality_badge(df: pd.DataFrame) -> None:
    target_cols = [col for col in NEW_NUMERIC_COLS if col in df.columns]
    if not target_cols:
        st.info("Calidad de datos: no hay columnas nuevas disponibles para evaluar completitud.")
        return

    completeness = {col: _non_empty_ratio(df[col]) for col in target_cols}
    avg_ratio = sum(completeness.values()) / len(completeness)
    low_cols = [COLUMN_LABELS.get(col, col) for col, ratio in completeness.items() if ratio < 0.6]

    if avg_ratio >= 0.85:
        status = "✅ Alta"
    elif avg_ratio >= 0.6:
        status = "⚠️ Media"
    else:
        status = "❌ Baja"

    msg = f"Calidad de datos: {status} ({avg_ratio * 100:,.1f}% de completitud promedio)."
    if low_cols:
        msg += f" Campos con menor cobertura: {', '.join(low_cols[:3])}."
    st.caption(msg)


def _render_kpis_with_context(filtered: pd.DataFrame, monthly: pd.DataFrame, mode: str) -> None:
    cols = st.columns(4)
    if monthly.empty:
        for idx, (_, label, value_type) in enumerate(KPI_SPECS):
            with cols[idx]:
                st.metric(label, _format_metric(None, value_type), delta="Sin datos mensuales")
        return

    monthly_sorted = monthly.sort_values("mes").reset_index(drop=True)
    latest = monthly_sorted.iloc[-1]
    prev = monthly_sorted.iloc[-2] if len(monthly_sorted) >= 2 else None
    yoy_reference = None
    if len(monthly_sorted) >= 13:
        yoy_reference = monthly_sorted.iloc[-13]

    for idx, (metric_key, label, value_type) in enumerate(KPI_SPECS):
        with cols[idx]:
            current_val = float(latest[metric_key]) if metric_key in latest and pd.notna(latest[metric_key]) else None
            prev_val = float(prev[metric_key]) if prev is not None and metric_key in prev and pd.notna(prev[metric_key]) else None
            yoy_val = (
                float(yoy_reference[metric_key])
                if yoy_reference is not None and metric_key in yoy_reference and pd.notna(yoy_reference[metric_key])
                else None
            )

            mom_delta = _delta_percentage(current_val, prev_val)
            yoy_delta = _delta_percentage(current_val, yoy_val)

            if mode == "vs mes anterior" and mom_delta is not None:
                delta_text = f"MoM {mom_delta:+.1f}%"
            elif mode == "vs mismo mes anio anterior" and yoy_delta is not None:
                delta_text = f"YoY {yoy_delta:+.1f}%"
            elif mode == "periodo completo" and mom_delta is not None:
                delta_text = f"MoM {mom_delta:+.1f}%"
            else:
                delta_text = "Sin comparativo"

            st.metric(
                label=f"{_health_emoji(metric_key, current_val)} {label}",
                value=_format_metric(current_val, value_type),
                delta=delta_text,
            )
            if yoy_delta is not None:
                st.caption(f"YoY {yoy_delta:+.1f}%")


def _build_executive_insights(monthly: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    if monthly.empty:
        return insights

    monthly_sorted = monthly.sort_values("mes").reset_index(drop=True)
    latest = monthly_sorted.iloc[-1]
    prev = monthly_sorted.iloc[-2] if len(monthly_sorted) >= 2 else None

    if "engagement_contenido_videos" in monthly_sorted.columns and pd.notna(latest.get("engagement_contenido_videos")):
        insights.append(
            f"Videos lidera con {float(latest['engagement_contenido_videos']):.2f}% de engagement en el periodo mas reciente."
        )

    if "publicaciones_por_semana" in monthly_sorted.columns and prev is not None:
        mom_posts = _delta_percentage(
            float(latest.get("publicaciones_por_semana")) if pd.notna(latest.get("publicaciones_por_semana")) else None,
            float(prev.get("publicaciones_por_semana")) if pd.notna(prev.get("publicaciones_por_semana")) else None,
        )
        if mom_posts is not None:
            direction = "crece" if mom_posts >= 0 else "cae"
            insights.append(f"El volumen de publicacion {direction} {abs(mom_posts):.1f}% vs mes anterior.")

    tracked = [
        "engagement_contenido_imagenes",
        "engagement_contenido_links",
        "engagement_contenido_videos",
        "engagement_tema_mas_visto",
    ]
    available = [col for col in tracked if col in monthly_sorted.columns and pd.notna(latest.get(col))]
    if available:
        best = max(available, key=lambda col: float(latest[col]))
        worst = min(available, key=lambda col: float(latest[col]))
        insights.append(
            f"Mejor formato actual: {COLUMN_LABELS.get(best, best)}. Oportunidad principal: {COLUMN_LABELS.get(worst, worst)}."
        )

    return insights[:3]


def _render_paginated_table(df: pd.DataFrame, page_key: str = "tipo_contenidos_page") -> pd.DataFrame:
    if df.empty:
        return df

    c1, c2 = st.columns([1, 1])
    with c1:
        page_size = st.selectbox("Filas por pagina", [25, 50, 100, 250], index=1, key="tipo_contenidos_page_size")
    with c2:
        total_pages = max(1, (len(df) + page_size - 1) // page_size)
        current_page = st.number_input("Pagina", min_value=1, max_value=total_pages, value=1, step=1, key=page_key)

    start = (int(current_page) - 1) * int(page_size)
    end = start + int(page_size)
    st.caption(f"Mostrando filas {start + 1}-{min(end, len(df))} de {len(df)}")
    return df.iloc[start:end]


def _apply_dark_chart_text(fig):
    """Fuerza tipografía oscura para evitar textos blancos en temas oscuros."""
    fig.update_layout(
        font={"color": "#212529"},
        title={"font": {"color": "#212529"}},
        legend={"font": {"color": "#212529"}},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    fig.update_xaxes(
        title_font={"color": "#212529"},
        tickfont={"color": "#212529"},
        color="#212529",
        gridcolor="#E0E0E0",
    )
    fig.update_yaxes(
        title_font={"color": "#212529"},
        tickfont={"color": "#212529"},
        color="#212529",
        gridcolor="#E0E0E0",
    )
    # Eje secundario (cuando existe)
    fig.update_layout(
        yaxis2={
            "title": {"font": {"color": "#212529"}},
            "tickfont": {"color": "#212529"},
            "color": "#212529",
        }
    )


def _get_reference_row(monthly_sorted: pd.DataFrame, mode: str):
    if monthly_sorted.empty:
        return None, "Sin referencia"

    if mode == "vs mes anterior" and len(monthly_sorted) >= 2:
        return monthly_sorted.iloc[-2], "Mes anterior"

    if mode == "vs mismo mes anio anterior" and len(monthly_sorted) >= 13:
        return monthly_sorted.iloc[-13], "Mismo mes anio anterior"

    if mode == "periodo completo" and len(monthly_sorted) >= 2:
        return monthly_sorted.iloc[:-1].mean(numeric_only=True), "Promedio historico"

    return None, "Sin referencia"


def _render_side_by_side_comparison(monthly: pd.DataFrame, mode: str) -> None:
    monthly_sorted = monthly.sort_values("mes").reset_index(drop=True)
    latest = monthly_sorted.iloc[-1]
    reference, reference_label = _get_reference_row(monthly_sorted, mode)

    st.subheader("Comparativo ejecutivo")
    left, right = st.columns(2)

    with left:
        st.markdown("**Periodo actual**")
        latest_month = latest.get("mes")
        if pd.notna(latest_month):
            st.caption(f"Corte: {pd.to_datetime(latest_month).strftime('%Y-%m')}")
        st.metric(
            "Engagement rate",
            _format_metric(float(latest.get("engagement_rate")) if pd.notna(latest.get("engagement_rate")) else None, "percent"),
        )
        st.metric(
            "Publicaciones/semana",
            _format_metric(float(latest.get("publicaciones_por_semana")) if pd.notna(latest.get("publicaciones_por_semana")) else None, "number"),
        )

    with right:
        st.markdown(f"**{reference_label}**")
        if isinstance(reference, pd.Series):
            if "mes" in reference and pd.notna(reference.get("mes")):
                st.caption(f"Corte: {pd.to_datetime(reference.get('mes')).strftime('%Y-%m')}")
            st.metric(
                "Engagement rate",
                _format_metric(float(reference.get("engagement_rate")) if pd.notna(reference.get("engagement_rate")) else None, "percent"),
            )
            st.metric(
                "Publicaciones/semana",
                _format_metric(float(reference.get("publicaciones_por_semana")) if pd.notna(reference.get("publicaciones_por_semana")) else None, "number"),
            )
        else:
            st.info("No hay suficiente historico para este comparativo.")

    if not isinstance(reference, pd.Series):
        return

    metrics = [m for m in COMPARISON_METRICS if m in monthly_sorted.columns]
    if not metrics:
        return

    rows = []
    for metric in metrics:
        current_value = float(latest.get(metric)) if pd.notna(latest.get(metric)) else None
        reference_value = float(reference.get(metric)) if pd.notna(reference.get(metric)) else None
        rows.append({
            "metrica": COLUMN_LABELS.get(metric, metric),
            "Periodo actual": current_value,
            reference_label: reference_value,
        })

    comp_df = pd.DataFrame(rows)
    melt_df = comp_df.melt(id_vars=["metrica"], var_name="periodo", value_name="valor")

    fig_comp = px.bar(
        melt_df,
        x="metrica",
        y="valor",
        color="periodo",
        barmode="group",
        title="Comparativa por formato de contenido",
        color_discrete_sequence=["#003696", "#CC7000"],
    )
    fig_comp.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(fig_comp)
    st.plotly_chart(fig_comp, width="stretch", config=PLOTLY_CONFIG)


def _render_data_quality_details(df: pd.DataFrame) -> None:
    st.subheader("Diagnostico de calidad de datos")
    target_cols = [col for col in NEW_NUMERIC_COLS if col in df.columns]
    if not target_cols:
        st.info("No hay columnas suficientes para diagnostico de calidad.")
        return

    quality_rows = []
    for col in target_cols:
        ratio = _non_empty_ratio(df[col])
        quality_rows.append(
            {
                "Campo": COLUMN_LABELS.get(col, col),
                "Completitud": ratio * 100.0,
                "Nulos": int(df[col].isna().sum()) if pd.api.types.is_numeric_dtype(df[col]) else int((df[col].fillna("").astype(str).str.strip() == "").sum()),
            }
        )

    quality_df = pd.DataFrame(quality_rows).sort_values("Completitud", ascending=False)
    fig_quality = px.bar(
        quality_df,
        x="Campo",
        y="Completitud",
        title="Completitud por campo",
        color="Completitud",
        color_continuous_scale=[[0.0, "#B42318"], [0.6, "#CC7000"], [1.0, "#0A7D35"]],
    )
    fig_quality.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(fig_quality)
    st.plotly_chart(fig_quality, width="stretch", config=PLOTLY_CONFIG)
    st.dataframe(quality_df, width="stretch", hide_index=True)


def _render_format_diagnostic(monthly: pd.DataFrame) -> None:
    st.subheader("Diagnostico por formato")
    if monthly.empty:
        st.info("Sin datos mensuales para diagnostico por formato.")
        return

    monthly_sorted = monthly.sort_values("mes").reset_index(drop=True)
    latest = monthly_sorted.iloc[-1]
    available = [col for col in COMPARISON_METRICS if col in monthly_sorted.columns and pd.notna(latest.get(col))]
    if not available:
        st.info("No hay columnas de formato disponibles para diagnostico.")
        return

    diag_df = pd.DataFrame(
        {
            "Formato": [COLUMN_LABELS.get(col, col) for col in available],
            "Engagement (%)": [float(latest[col]) for col in available],
        }
    ).sort_values("Engagement (%)", ascending=False)

    fig_diag = px.bar(
        diag_df,
        x="Formato",
        y="Engagement (%)",
        title="Ranking de formatos en el ultimo periodo",
        color="Engagement (%)",
        color_continuous_scale=[[0.0, "#CC7000"], [1.0, "#003696"]],
    )
    fig_diag.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(fig_diag)
    st.plotly_chart(fig_diag, width="stretch", config=PLOTLY_CONFIG)

    best = diag_df.iloc[0]
    worst = diag_df.iloc[-1]
    st.caption(
        f"Mejor formato actual: {best['Formato']} ({best['Engagement (%)']:.2f}%). "
        f"Formato con mayor oportunidad: {worst['Formato']} ({worst['Engagement (%)']:.2f}%)."
    )


def render_new_data_dashboard() -> None:
    st.title("Tipo de contenidos")
    st.caption("Panel ejecutivo para evaluar desempeno, calidad y oportunidades por tipo de contenido.")

    analytical_family = st.radio(
        "Enfoque analitico",
        options=["Rendimiento", "Calidad de datos", "Diagnostico por formato"],
        horizontal=True,
    )

    compare_mode = st.radio(
        "Modo de comparacion temporal",
        options=["periodo completo", "vs mes anterior", "vs mismo mes anio anterior"],
        horizontal=True,
    )

    df = data_provider.get_merged_data(force_reload=False)
    if df is None or df.empty:
        st.warning("No hay datos disponibles para esta vista.")
        return

    required_for_view = ["fecha", "entidad", "plataforma"]
    missing_required = [col for col in required_for_view if col not in df.columns]
    if missing_required:
        st.error(f"Faltan columnas base para visualizar: {missing_required}")
        return

    df = _to_numeric_safe(df, ["engagement_rate", *NEW_NUMERIC_COLS])

    # Filtros locales de la vista (sincronizados con filtros globales)
    df = _resolve_global_filters(df)

    c1, c2 = st.columns(2)
    with c1:
        entidades = ["Todas"] + sorted([str(v) for v in df["entidad"].dropna().unique()])
        default_entidad = st.session_state.get("filtro_entidad", "Todas")
        default_entidad_idx = entidades.index(default_entidad) if default_entidad in entidades else 0
        entidad_sel = st.selectbox(
            "Entidad",
            entidades,
            index=default_entidad_idx,
            key="new_data_entidad",
        )

    entity_filtered = df.copy()
    if entidad_sel != "Todas":
        entity_filtered = entity_filtered[entity_filtered["entidad"] == entidad_sel]

    social_for_selector, maps_filtered = _split_social_vs_maps(entity_filtered)

    with c2:
        social_platforms = [
            str(v)
            for v in social_for_selector["plataforma"].dropna().unique()
            if str(v).strip()
        ]
        plataformas = ["Todas"] + sorted(social_platforms)
        plataforma_sel = st.selectbox(
            "Plataforma (red social)",
            plataformas,
            key="new_data_plataforma",
            help="Google Maps se analiza en una seccion separada al final.",
        )

    social_filtered = social_for_selector.copy()
    if plataforma_sel != "Todas":
        social_filtered = social_filtered[social_filtered["plataforma"] == plataforma_sel]

    if social_filtered.empty and maps_filtered.empty:
        st.warning("No hay filas para los filtros seleccionados.")
        return

    has_social_data = not social_filtered.empty

    if has_social_data:
        _render_data_quality_badge(social_filtered)

    monthly = _monthly_aggregation(social_filtered) if has_social_data else pd.DataFrame()
    if has_social_data:
        _render_kpis_with_context(social_filtered, monthly, compare_mode)
    else:
        st.info("No hay plataformas de redes sociales para los filtros actuales. Google Maps se muestra en la seccion final.")

    if has_social_data and monthly.empty:
        st.info("No se pudo construir serie mensual con los datos sociales actuales.")

    if has_social_data and not monthly.empty:
        if analytical_family == "Rendimiento":
            insights = _build_executive_insights(monthly)
            if insights:
                st.subheader("Insights ejecutivos")
                for insight in insights:
                    st.markdown(f"- {insight}")

            if "engagement_rate" in monthly.columns and "publicaciones_por_semana" in monthly.columns:
                fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
                fig_dual.add_trace(
                    go.Scatter(
                        x=monthly["mes"],
                        y=monthly["engagement_rate"],
                        mode="lines+markers",
                        name="Engagement rate",
                        line={"color": "#003696", "width": 2},
                    ),
                    secondary_y=False,
                )
                fig_dual.add_trace(
                    go.Bar(
                        x=monthly["mes"],
                        y=monthly["publicaciones_por_semana"],
                        name="Publicaciones/semana",
                        marker_color="#CC7000",
                        opacity=0.45,
                    ),
                    secondary_y=True,
                )
                fig_dual.update_layout(
                    title="Tendencia ejecutiva: engagement vs volumen de publicacion",
                    **PLOTLY_LAYOUT_DEFAULTS,
                )
                fig_dual.update_yaxes(title_text="Engagement (%)", secondary_y=False)
                fig_dual.update_yaxes(title_text="Publicaciones/semana", secondary_y=True)
                _apply_dark_chart_text(fig_dual)
                st.plotly_chart(fig_dual, width="stretch", config=PLOTLY_CONFIG)

            _render_side_by_side_comparison(monthly, compare_mode)

        elif analytical_family == "Calidad de datos":
            _render_data_quality_details(social_filtered)

        else:
            _render_format_diagnostic(monthly)

    # Comparación mensual: engagement histórico vs nuevos puntos de contenido
    engagement_compare_cols = [
        col
        for col in [
            "engagement_rate",
            "engagement_contenido_imagenes",
            "engagement_contenido_links",
            "engagement_contenido_videos",
            "engagement_tema_mas_visto",
        ]
        if col in monthly.columns
    ]

    if has_social_data and engagement_compare_cols:
        line_df = monthly[["mes", *engagement_compare_cols]].melt(
            id_vars=["mes"],
            value_vars=engagement_compare_cols,
            var_name="metrica",
            value_name="valor",
        )
        fig_line = px.line(
            line_df,
            x="mes",
            y="valor",
            color="metrica",
            markers=True,
            title="Comparativa mensual de engagement (histórico vs nuevos campos)",
            color_discrete_map=METRIC_COLOR_MAP,
        )
        fig_line.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        _apply_dark_chart_text(fig_line)
        st.plotly_chart(fig_line, width="stretch", config=PLOTLY_CONFIG)

    # Volumen mensual de publicaciones
    if has_social_data and "publicaciones_por_semana" in monthly.columns:
        fig_bar = px.bar(
            monthly,
            x="mes",
            y="publicaciones_por_semana",
            title="Evolución mensual de publicaciones por semana",
            color_discrete_sequence=["#003696"],
        )
        fig_bar.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        _apply_dark_chart_text(fig_bar)
        st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CONFIG)

    # Rankings comparativos de rendimiento por institución
    if has_social_data:
        _render_institution_rankings(social_filtered, plataforma_sel)

    # Cortes explicitos por tema principal y cambios operacionales
    if has_social_data and "tema_principal" in social_filtered.columns and "engagement_rate" in social_filtered.columns:
        tema_df = social_filtered.copy()
        tema_df["tema_principal"] = tema_df["tema_principal"].fillna("").astype(str).str.strip()
        tema_df = tema_df[tema_df["tema_principal"] != ""]
        if not tema_df.empty:
            st.subheader("Engagement por tema principal")
            tema_agg = (
                tema_df.groupby("tema_principal", as_index=False)
                .agg(
                    engagement_promedio=("engagement_rate", "mean"),
                    registros=("engagement_rate", "count"),
                )
                .sort_values("engagement_promedio", ascending=False)
            )
            fig_tema = px.bar(
                tema_agg,
                x="tema_principal",
                y="engagement_promedio",
                color="registros",
                title="Promedio de engagement por tema principal",
                color_continuous_scale=[[0.0, "#CC7000"], [1.0, "#003696"]],
            )
            fig_tema.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
            _apply_dark_chart_text(fig_tema)
            st.plotly_chart(fig_tema, width="stretch", config=PLOTLY_CONFIG)

    if has_social_data and "tuvo_cambios_operacionales" in social_filtered.columns and "engagement_rate" in social_filtered.columns:
        cambios_df = social_filtered.copy()
        cambios_df["tuvo_cambios_operacionales"] = (
            cambios_df["tuvo_cambios_operacionales"].fillna("").astype(str).str.strip().str.lower()
        )
        cambios_df = cambios_df[cambios_df["tuvo_cambios_operacionales"].isin(["si", "no"])]
        if not cambios_df.empty:
            st.subheader("Impacto de cambios operacionales")
            cambios_agg = (
                cambios_df.groupby("tuvo_cambios_operacionales", as_index=False)
                .agg(
                    engagement_promedio=("engagement_rate", "mean"),
                    registros=("engagement_rate", "count"),
                )
                .sort_values("tuvo_cambios_operacionales")
            )
            cambios_agg["tuvo_cambios_operacionales"] = cambios_agg["tuvo_cambios_operacionales"].replace(
                {"si": "Con cambios", "no": "Sin cambios"}
            )
            fig_cambios = px.bar(
                cambios_agg,
                x="tuvo_cambios_operacionales",
                y="engagement_promedio",
                color="tuvo_cambios_operacionales",
                title="Engagement promedio con/sin cambios operacionales",
                color_discrete_map={"Con cambios": "#003696", "Sin cambios": "#CC7000"},
            )
            fig_cambios.update_layout(**{**PLOTLY_LAYOUT_DEFAULTS, "showlegend": False})
            _apply_dark_chart_text(fig_cambios)
            st.plotly_chart(fig_cambios, width="stretch", config=PLOTLY_CONFIG)

    # Tabla de detalle para auditoría operativa
    show_cols = [
        col
        for col in [
            "fecha",
            "entidad",
            "plataforma",
            "tema_mas_visto",
            "tema_principal",
            "top_5_publicaciones",
            "publicacion_destacada",
            "comentarios_consolidados",
            "obs_engagement",
            "notas_operacionales",
            "alertas_riesgos",
            "tuvo_cambios_operacionales",
            "media_visualizaciones",
            "engagement_contenido_imagenes",
            "engagement_contenido_links",
            "engagement_contenido_videos",
            "engagement_tema_mas_visto",
            "publicaciones_por_semana",
        ]
        if col in social_filtered.columns
    ]

    if has_social_data and show_cols:
        st.subheader("Detalle de nuevos datos")
        relevant_cols = [col for col in show_cols if _non_empty_ratio(social_filtered[col]) >= 0.3]
        if not relevant_cols:
            relevant_cols = show_cols

        detail_df = social_filtered[relevant_cols].sort_values("fecha", ascending=False)
        detail_df = detail_df.rename(columns=COLUMN_LABELS)
        paged_df = _render_paginated_table(detail_df)
        st.dataframe(paged_df, width="stretch")

        csv_data = detail_df.to_csv(index=False).encode("utf-8-sig")
        file_suffix = f"{entidad_sel}_{plataforma_sel}".replace(" ", "_")
        st.download_button(
            label="Descargar detalle CSV",
            data=csv_data,
            file_name=f"tipo_contenidos_{file_suffix}.csv",
            mime="text/csv",
        )

    _render_google_maps_section(maps_filtered)
