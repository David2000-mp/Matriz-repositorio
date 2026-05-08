"""
Vista de analisis de textos para CHAMPILEAKS.

Analiza columnas de texto y muestra:
- Distribucion de sentimientos
- Palabras clave mas frecuentes
- Tendencia mensual de sentimiento
- Observaciones manuales detectadas en comentarios
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components import PLOTLY_CONFIG, PLOTLY_LAYOUT_DEFAULTS
from utils.comment_processor import (
    clean_raw_text,
    create_dataframe_from_comments,
    export_full_csv,
    export_manual_load_csv,
)
from utils.data_provider import data_provider
from utils.text_mining import (
    TEXT_COLUMNS_DEFAULT,
    build_manual_observations,
    keyword_frequency,
    sentiment_distribution,
    sentiment_monthly_trend,
)

COLUMN_LABELS = {
    "tema_mas_visto": "Tema mas visto",
    "top_5_publicaciones": "Top 5 publicaciones",
    "comentarios_consolidados": "Comentarios consolidados",
    "obs_engagement": "Observaciones de engagement",
    "notas_operacionales": "Notas operacionales",
    "alertas_riesgos": "Alertas y riesgos",
    "publicacion_destacada": "Publicacion destacada",
}

SENTIMENT_COLORS = {
    "positivo": "#0A7D35",
    "neutral": "#CC7000",
    "negativo": "#B42318",
}

IMPORTER_MASTER_HEADERS = {
    "fecha_carga": "fecha_carga",
    "fuente": "fuente",
    "comentario_original": "Comentarios de la seccion de opinion",
    "sentimiento_etiqueta": "sentimiento_etiqueta",
    "sentimiento_score": "sentimiento_score",
    "categoria": "categoria",
}

IMPORTER_MANUAL_HEADERS = {
    "comentario_original": "Comentarios de la seccion de opinion",
    "fuente": "fuente",
}

SENTIMENT_SCORE_COLORS = {
    1: "#B42318",
    2: "#F04438",
    3: "#9CA3AF",
    4: "#12B76A",
    5: "#039855",
}


def _apply_dark_chart_text(fig):
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


def _resolve_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    entidad_global = st.session_state.get("filtro_entidad", "Todas")
    mes_global = st.session_state.get("filtro_mes", "Todos")

    if entidad_global != "Todas" and "entidad" in filtered.columns:
        filtered = filtered[filtered["entidad"].astype(str) == str(entidad_global)]

    if mes_global != "Todos" and "fecha" in filtered.columns:
        fechas = pd.to_datetime(filtered["fecha"], errors="coerce")
        periodos = fechas.dt.strftime("%Y-%m")
        filtered = filtered[periodos == str(mes_global)]

    return filtered


def _safe_total_texts(df: pd.DataFrame, selected_cols: list[str]) -> int:
    total = 0
    for col in selected_cols:
        if col in df.columns:
            total += int((df[col].fillna("").astype(str).str.strip() != "").sum())
    return total


def _global_sentiment(df: pd.DataFrame, selected_cols: list[str]) -> pd.DataFrame:
    chunks = []
    for col in selected_cols:
        dist = sentiment_distribution(df, col)
        if not dist.empty:
            dist["origen"] = col
            chunks.append(dist)

    if not chunks:
        return pd.DataFrame(columns=["sentimiento", "total"])

    merged = pd.concat(chunks, ignore_index=True)
    return merged.groupby("sentimiento", as_index=False)["total"].sum()


def _score_to_stars(value: int) -> str:
    score = int(value) if pd.notna(value) else 0
    score = max(1, min(5, score))
    return "★" * score + "☆" * (5 - score)


def _render_comment_importer() -> None:
    st.subheader("Importador de comentarios")
    st.caption(
        "Pega todos los comentarios de una sola vez, procesa en lote y descarga CSV para carga manual."
    )

    source_col, info_col = st.columns([2, 3])
    with source_col:
        source = st.selectbox(
            "Fuente",
            options=["Google Maps", "Facebook", "Instagram", "TikTok", "Otra"],
            key="comment_import_source",
        )
    with info_col:
        st.info(
            "Flujo recomendado: pegar bloque completo -> procesar -> descargar archivo maestro y/o archivo de carga manual."
        )

    raw_text = st.text_area(
        "Pega aqui los comentarios (uno por linea)",
        key="comment_import_raw_text",
        height=180,
        placeholder="Excelente servicio\nMuy caro para lo que ofrecen\nEl lugar estaba limpio",
    )

    if st.button("Procesar comentarios", key="comment_import_process"):
        cleanup_result = clean_raw_text(raw_text)
        cleaned = cleanup_result["comentarios_validos"]
        if not cleaned:
            st.warning("No se detectaron comentarios validos despues de limpiar el texto.")
            st.info(
                f"Analisis: {cleanup_result['total_original']} lineas originales, "
                f"{cleanup_result['total_descartados']} descartadas por ruido/duplicados."
            )
            return

        processed_df = create_dataframe_from_comments(cleaned, source)
        st.session_state["comment_import_processed_df"] = processed_df
        st.session_state["comment_import_cleanup_result"] = cleanup_result
        
        # Mostrar metricas de limpieza
        st.success(
            f"Se procesaron {cleanup_result['total_original']} lineas: "
            f"{len(cleaned)} validas y {cleanup_result['total_descartados']} descartadas."
        )

    processed_df = st.session_state.get("comment_import_processed_df")
    if processed_df is None or processed_df.empty:
        return

    summary = (
        processed_df["sentimiento_etiqueta"]
        .value_counts()
        .reindex(["Muy Positivo", "Positivo", "Neutral", "Negativo", "Muy Negativo"], fill_value=0)
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Comentarios procesados", f"{len(processed_df):,}")
    c2.metric("Promedio sentimiento", f"{processed_df['sentimiento_score'].mean():.2f}/5")
    c3.metric("Alertas criticas", int(summary["Muy Negativo"]))

    st.caption(
        " | ".join(
            [
                f"Muy Positivo: {int(summary['Muy Positivo'])}",
                f"Positivo: {int(summary['Positivo'])}",
                f"Neutral: {int(summary['Neutral'])}",
                f"Negativo: {int(summary['Negativo'])}",
                f"Muy Negativo: {int(summary['Muy Negativo'])}",
            ]
        )
    )

    if int(summary["Muy Negativo"]) > 0:
        st.error(f"Se detectaron {int(summary['Muy Negativo'])} alertas criticas Muy Negativas.")

    st.markdown("**Opciones de exportacion manual**")
    option_col_1, option_col_2 = st.columns(2)
    with option_col_1:
        include_source_in_manual = st.toggle(
            "Incluir columna fuente en CSV manual",
            value=False,
            key="comment_import_include_source_manual",
            help="Si se activa, el archivo manual incluye comentario_original y fuente.",
        )
    with option_col_2:
        manual_comment_header = st.text_input(
            "Nombre de columna para comentarios (CSV manual)",
            value="Comentarios de la seccion de opinion",
            key="comment_import_manual_header_name",
        ).strip()
        if not manual_comment_header:
            manual_comment_header = "Comentarios de la seccion de opinion"

    preview_df = processed_df.copy()
    preview_df["sentimiento_estrellas"] = preview_df["sentimiento_score"].map(_score_to_stars)

    st.dataframe(
        preview_df[["comentario_original", "sentimiento_etiqueta", "sentimiento_score", "sentimiento_estrellas", "categoria"]],
        width="stretch",
        column_config={
            "comentario_original": st.column_config.TextColumn("Comentario", width="large"),
            "sentimiento_etiqueta": st.column_config.TextColumn("Sentimiento"),
            "sentimiento_score": st.column_config.NumberColumn("Score", min_value=1, max_value=5),
            "sentimiento_estrellas": st.column_config.TextColumn("Escala"),
            "categoria": st.column_config.TextColumn("Categoria"),
        },
        hide_index=True,
    )

    legend_html = "".join(
        [
            f"<span style='display:inline-block;margin-right:10px;color:{color};font-weight:700'>{score}</span>"
            for score, color in SENTIMENT_SCORE_COLORS.items()
        ]
    )
    st.markdown(f"Colores de severidad: {legend_html}", unsafe_allow_html=True)

    try:
        full_csv_bytes = export_full_csv(
            processed_df,
            header_mapping=IMPORTER_MASTER_HEADERS,
        )
        manual_headers = dict(IMPORTER_MANUAL_HEADERS)
        manual_headers["comentario_original"] = manual_comment_header

        manual_csv_bytes = export_manual_load_csv(
            processed_df,
            include_source=include_source_in_manual,
            header_mapping=manual_headers,
        )

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Descargar CSV completo",
                data=full_csv_bytes,
                file_name="comentarios_procesados_completo.csv",
                mime="text/csv",
                key="comment_import_download_full_csv",
            )
        with d2:
            st.download_button(
                "Descargar CSV solo carga manual",
                data=manual_csv_bytes,
                file_name="comentarios_carga_manual.csv",
                mime="text/csv",
                key="comment_import_download_manual_csv",
            )

        st.caption(
            "CSV completo: respaldo historico y analitica. "
            "CSV solo carga manual: listo para copiar/pegar en la hoja y columna que definas."
        )
    except ValueError as exc:
        st.error(f"No se pudo preparar el CSV: {exc}")


def render_text_analysis_dashboard() -> None:
    st.title("Analisis de textos")
    st.caption("Mineria de textos local y gratuita sobre columnas textuales del formulario.")
    _render_comment_importer()
    st.divider()

    df = data_provider.get_merged_data(force_reload=False)
    if df is None or df.empty:
        st.warning("No hay datos disponibles para analizar textos.")
        return

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    df = _resolve_global_filters(df)

    text_columns = [col for col in TEXT_COLUMNS_DEFAULT if col in df.columns]
    if not text_columns:
        st.error("No se encontraron columnas de texto para analizar.")
        return

    col_left, col_right = st.columns(2)
    with col_left:
        entidades = ["Todas"] + sorted([str(v) for v in df["entidad"].dropna().unique()]) if "entidad" in df.columns else ["Todas"]
        entidad_sel = st.selectbox("Entidad", entidades, key="text_mining_entidad")
    with col_right:
        plataformas = ["Todas"] + sorted([str(v) for v in df["plataforma"].dropna().unique()]) if "plataforma" in df.columns else ["Todas"]
        plataforma_sel = st.selectbox("Plataforma", plataformas, key="text_mining_plataforma")

    filtered = df.copy()
    if entidad_sel != "Todas" and "entidad" in filtered.columns:
        filtered = filtered[filtered["entidad"].astype(str) == str(entidad_sel)]
    if plataforma_sel != "Todas" and "plataforma" in filtered.columns:
        filtered = filtered[filtered["plataforma"].astype(str) == str(plataforma_sel)]

    c3, c4 = st.columns(2)
    with c3:
        if "tema_principal" in filtered.columns:
            temas = ["Todos"] + sorted([str(v) for v in filtered["tema_principal"].dropna().astype(str).str.strip().unique() if str(v).strip()])
            tema_sel = st.selectbox("Tema principal", temas, key="text_mining_tema_principal")
        else:
            tema_sel = "Todos"
    with c4:
        if "tuvo_cambios_operacionales" in filtered.columns:
            cambios = ["Todos", "si", "no"]
            cambio_sel = st.selectbox("Cambios operacionales", cambios, key="text_mining_cambios")
        else:
            cambio_sel = "Todos"

    if tema_sel != "Todos" and "tema_principal" in filtered.columns:
        filtered = filtered[filtered["tema_principal"].astype(str).str.strip() == str(tema_sel)]
    if cambio_sel != "Todos" and "tuvo_cambios_operacionales" in filtered.columns:
        normalized_changes = filtered["tuvo_cambios_operacionales"].astype(str).str.strip().str.lower()
        filtered = filtered[normalized_changes == cambio_sel]

    if filtered.empty:
        st.info("No hay datos para los filtros seleccionados.")
        return

    selected_cols = st.multiselect(
        "Columnas de texto a analizar",
        options=text_columns,
        default=text_columns,
        format_func=lambda name: COLUMN_LABELS.get(name, name),
    )

    if not selected_cols:
        st.info("Selecciona al menos una columna de texto.")
        return

    sentiment_global = _global_sentiment(filtered, selected_cols)
    total_texts = _safe_total_texts(filtered, selected_cols)
    unique_keywords = 0
    for col in selected_cols:
        unique_keywords += len(keyword_frequency(filtered, col, top_n=50))

    dominant_sentiment = "Sin datos"
    if not sentiment_global.empty:
        dominant_sentiment = str(sentiment_global.sort_values("total", ascending=False).iloc[0]["sentimiento"]).capitalize()

    k1, k2, k3 = st.columns(3)
    k1.metric("Textos analizados", f"{total_texts:,}")
    k2.metric("Sentimiento dominante", dominant_sentiment)
    k3.metric("Palabras clave detectadas", f"{unique_keywords:,}")

    if not sentiment_global.empty:
        fig_pie = px.pie(
            sentiment_global,
            names="sentimiento",
            values="total",
            title="Distribucion global de sentimiento",
            color="sentimiento",
            color_discrete_map=SENTIMENT_COLORS,
        )
        fig_pie.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        _apply_dark_chart_text(fig_pie)
        st.plotly_chart(fig_pie, width="stretch", config=PLOTLY_CONFIG, key="text_global_sentiment_pie")

    tabs = st.tabs([COLUMN_LABELS.get(col, col) for col in selected_cols])
    for tab, source_col in zip(tabs, selected_cols):
        with tab:
            dist = sentiment_distribution(filtered, source_col)
            trend = sentiment_monthly_trend(filtered, source_col)
            keywords = keyword_frequency(filtered, source_col, top_n=15)

            c1, c2 = st.columns(2)
            with c1:
                if dist.empty:
                    st.info("Sin sentimiento disponible para esta columna.")
                else:
                    fig_bar = px.bar(
                        dist,
                        x="sentimiento",
                        y="total",
                        color="sentimiento",
                        title=f"Sentimiento en {COLUMN_LABELS.get(source_col, source_col)}",
                        color_discrete_map=SENTIMENT_COLORS,
                    )
                    fig_bar.update_layout(**{**PLOTLY_LAYOUT_DEFAULTS, "showlegend": False})
                    _apply_dark_chart_text(fig_bar)
                    st.plotly_chart(
                        fig_bar,
                        width="stretch",
                        config=PLOTLY_CONFIG,
                        key=f"text_sentiment_bar_{source_col}",
                    )
            with c2:
                if keywords.empty:
                    st.info("Sin palabras clave para esta columna.")
                else:
                    fig_kw = px.bar(
                        keywords.sort_values("total", ascending=True),
                        x="total",
                        y="palabra",
                        orientation="h",
                        title="Top palabras clave",
                        color_discrete_sequence=["#003696"],
                    )
                    fig_kw.update_layout(**{**PLOTLY_LAYOUT_DEFAULTS, "showlegend": False})
                    _apply_dark_chart_text(fig_kw)
                    st.plotly_chart(
                        fig_kw,
                        width="stretch",
                        config=PLOTLY_CONFIG,
                        key=f"text_keywords_bar_{source_col}",
                    )

            if trend.empty:
                st.info("No hay tendencia mensual disponible.")
            else:
                fig_trend = px.line(
                    trend,
                    x="mes",
                    y="score_promedio",
                    markers=True,
                    title="Tendencia mensual de sentimiento (score promedio)",
                    color_discrete_sequence=["#CC7000"],
                )
                fig_trend.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
                _apply_dark_chart_text(fig_trend)
                st.plotly_chart(
                    fig_trend,
                    width="stretch",
                    config=PLOTLY_CONFIG,
                    key=f"text_trend_line_{source_col}",
                )

            detail_cols = [col for col in ["fecha", "entidad", "plataforma", source_col, f"{source_col}_sentiment", f"{source_col}_keywords"] if col in filtered.columns]
            detail_df = filtered[detail_cols].copy()
            if "fecha" in detail_df.columns:
                detail_df = detail_df.sort_values("fecha", ascending=False)
            st.dataframe(detail_df.head(100), width="stretch")

    if "comentarios_consolidados" in selected_cols:
        st.subheader("Observaciones manuales detectadas")
        manual_df = build_manual_observations(filtered, source_col="comentarios_consolidados")
        if manual_df.empty:
            st.caption("No se detectaron observaciones manuales en el periodo filtrado.")
        else:
            st.dataframe(manual_df, width="stretch", hide_index=True)

    # Panel separado para contexto operativo y alertas
    context_cols = [col for col in ["notas_operacionales", "alertas_riesgos"] if col in filtered.columns]
    if context_cols:
        st.subheader("Panel de contexto operacional")
        left, right = st.columns(2)

        if "notas_operacionales" in context_cols:
            notas_df = filtered[[c for c in ["fecha", "entidad", "plataforma", "notas_operacionales"] if c in filtered.columns]].copy()
            notas_df = notas_df[notas_df["notas_operacionales"].fillna("").astype(str).str.strip() != ""]
            if "fecha" in notas_df.columns:
                notas_df = notas_df.sort_values("fecha", ascending=False)
            with left:
                st.markdown("**Notas operacionales recientes**")
                if notas_df.empty:
                    st.caption("Sin notas operacionales para los filtros actuales.")
                else:
                    st.dataframe(notas_df.head(20), width="stretch", hide_index=True)

        if "alertas_riesgos" in context_cols:
            alertas_df = filtered[[c for c in ["fecha", "entidad", "plataforma", "alertas_riesgos"] if c in filtered.columns]].copy()
            alertas_df = alertas_df[alertas_df["alertas_riesgos"].fillna("").astype(str).str.strip() != ""]
            if "fecha" in alertas_df.columns:
                alertas_df = alertas_df.sort_values("fecha", ascending=False)
            with right:
                st.markdown("**Alertas y riesgos recientes**")
                if alertas_df.empty:
                    st.caption("Sin alertas para los filtros actuales.")
                else:
                    st.dataframe(alertas_df.head(20), width="stretch", hide_index=True)
