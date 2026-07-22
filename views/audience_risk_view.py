"""
Vista de Segmentacion de Audiencias y Riesgo.

Incluye:
- Segmentacion por segmento educativo
- Matriz de riesgo institucional
- Dispersion opcional de crecimiento vs engagement
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import unicodedata
try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    px = None
    go = None

from components import MetricCard, PLOTLY_CONFIG, render_empty_state
from utils.chart_theme import aplicar_tema_champileaks
from utils.data_provider import data_provider
from utils.analytics import calculate_health_score
from views.dashboard import calcular_kpi_engagement_global

# Umbrales fijos aprobados para matriz de riesgo.
CRITICAL_THRESHOLD = 45.0
HEALTHY_THRESHOLD = 70.0

# Mapeo explicito de instituciones a segmento educativo.
INSTITUTION_SEGMENT_MAP = {
    "Instituto Mexico Primaria": "Educacion Basica",
    "Instituto Mexico Toluca Primaria": "Educacion Basica",
    "Colegio Montejo": "Educacion Basica",
    "Instituto Mexico Secundaria": "Educacion Basica",
    "Colegio Mexico Roma": "Educacion Basica",
    "Instituto Hidalguense": "Educacion Basica",
    "Centro Universitario Mexico (CUM)": "Educacion Media Superior",
    "Centro Universitario Mexico": "Educacion Media Superior",
    "Colegio Mexico Bachillerato": "Educacion Media Superior",
    "Instituto Mexico Toluca": "Colegios Multinivel",
    "Colegio Mexico Orizaba": "Colegios Multinivel",
    "Instituto Potosino": "Colegios Multinivel",
    "Instituto Queretano San Javier": "Colegios Multinivel",
    "Colegio Lic. Manuel Concha": "Colegios Multinivel",
    "Colegio Pedro Martinez Vazquez": "Colegios Multinivel",
    "Colegio Jacona": "Colegios Multinivel",
    "Instituto Sahuayense": "Colegios Multinivel",
    "Universidad Marista de Mexico": "Educacion Superior",
    "Universidad Marista de Queretaro": "Educacion Superior",
    "Universidad Marista SLP": "Educacion Superior",
    "Universidad Marista de Guadalajara": "Educacion Superior",
    "Maristas Mexico Central": "Instancias Organizacionales",
    "Maristas Mexico Occidental": "Instancias Organizacionales",
    "Pastoral Juvenil Mexico Central": "Instancias Organizacionales",
    "Juventudes Maristas": "Instancias Organizacionales",
    "Convocatoria Marista": "Instancias Organizacionales",
    "Laicado Marista": "Instancias Organizacionales",
}

# Mapa secundario explicito para cobertura descriptiva visible en tabla de riesgo.
INSTITUTION_COVERAGE_MAP = {
    "Instituto Mexico Primaria": "Primaria",
    "Instituto Mexico Toluca Primaria": "Primaria",
    "Colegio Montejo": "Preescolar y Primaria",
    "Instituto Mexico Secundaria": "Secundaria",
    "Colegio Mexico Roma": "Preescolar, Primaria y Secundaria",
    "Instituto Hidalguense": "Primaria y Secundaria",
    "Centro Universitario Mexico (CUM)": "Bachillerato",
    "Centro Universitario Mexico": "Bachillerato",
    "Colegio Mexico Bachillerato": "Bachillerato",
    "Instituto Mexico Toluca": "Preescolar, Primaria, Secundaria y Preparatoria",
    "Colegio Mexico Orizaba": "Primaria, Secundaria y Bachillerato",
    "Instituto Potosino": "Primaria, Secundaria y Preparatoria",
    "Instituto Queretano San Javier": "Primaria, Secundaria y Preparatoria",
    "Colegio Lic. Manuel Concha": "Secundaria y Preparatoria",
    "Colegio Pedro Martinez Vazquez": "Primaria, Secundaria y Bachillerato",
    "Colegio Jacona": "Primaria, Secundaria y Preparatoria",
    "Instituto Sahuayense": "Primaria, Secundaria y Preparatoria",
    "Universidad Marista de Mexico": "Universidad",
    "Universidad Marista de Queretaro": "Universidad",
    "Universidad Marista SLP": "Universidad",
    "Universidad Marista de Guadalajara": "Universidad",
    "Maristas Mexico Central": "Coordinacion institucional",
    "Maristas Mexico Occidental": "Coordinacion institucional",
    "Pastoral Juvenil Mexico Central": "Pastoral y acompanamiento",
    "Juventudes Maristas": "Participacion juvenil",
    "Convocatoria Marista": "Comunicacion institucional",
    "Laicado Marista": "Comunidad laical",
}

SEGMENT_ORDER = [
    "Educacion Basica",
    "Educacion Media Superior",
    "Colegios Multinivel",
    "Educacion Superior",
    "Instancias Organizacionales",
]

RISK_PRIORITY = {
    "Riesgo Critico": 0,
    "Desempeno Regular": 1,
    "Saludable": 2,
}


def load_base_data(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Carga datos de forma defensiva desde el data provider."""
    if df is not None:
        return df.copy()

    try:
        loaded = data_provider.get_merged_data(force_reload=False)
        if loaded is None:
            return pd.DataFrame()
        return loaded.copy()
    except Exception:
        return pd.DataFrame()


def _apply_sidebar_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Aplica filtros globales del sidebar para entidad y periodo."""
    if data.empty:
        return data

    filtered = data.copy()

    mes_sel = st.session_state.get("filtro_mes", "Todos")
    if mes_sel != "Todos" and "fecha" in filtered.columns:
        fechas = pd.to_datetime(filtered["fecha"], errors="coerce")
        filtered = filtered[fechas.dt.strftime("%Y-%m") == str(mes_sel)]

    entidad_sel = st.session_state.get("filtro_entidad", "Todas")
    if entidad_sel != "Todas" and "entidad" in filtered.columns:
        filtered = filtered[filtered["entidad"] == entidad_sel]

    return filtered


def _prepare_core_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos de columnas clave usadas en agregaciones."""
    out = data.copy()

    if "fecha" in out.columns:
        out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")

    for col in ["seguidores", "interacciones", "engagement_rate"]:
        if col not in out.columns:
            out[col] = 0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    if "plataforma" not in out.columns:
        out["plataforma"] = ""
    if "entidad" not in out.columns:
        out["entidad"] = ""

    out["entidad"] = out["entidad"].fillna("").astype(str).str.strip()
    out["plataforma"] = out["plataforma"].fillna("").astype(str).str.strip()
    return out


def _normalize_text_value(text: str) -> str:
    """Normaliza texto para matching estable, tolerando acentos/no acentos."""
    base = unicodedata.normalize("NFKD", str(text))
    no_accents = "".join(ch for ch in base if not unicodedata.combining(ch))
    return " ".join(no_accents.strip().lower().split())


def _normalize_text(series: pd.Series) -> pd.Series:
    """Normaliza series de texto para matching estable con y sin acentos."""
    return series.fillna("").astype(str).apply(_normalize_text_value)


def _normalized_segment_map() -> dict[str, str]:
    """Retorna mapeo explicito normalizado para segmento educativo."""
    return {
        _normalize_text_value(name): segment
        for name, segment in INSTITUTION_SEGMENT_MAP.items()
    }


def _normalized_coverage_map() -> dict[str, str]:
    """Retorna mapeo explicito normalizado para cobertura institucional."""
    return {
        _normalize_text_value(name): coverage
        for name, coverage in INSTITUTION_COVERAGE_MAP.items()
    }


def _is_explicit_mapping(entidad_series: pd.Series) -> pd.Series:
    """Indica si la entidad existe en el mapeo explicito de taxonomia."""
    normalized = _normalize_text(entidad_series)
    return normalized.isin(set(_normalized_segment_map().keys()))


def classify_educational_segment(entidad_series: pd.Series) -> pd.Series:
    """
    Clasifica entidades en segmento educativo usando mapeo explicito.

    Estrategia:
    1) Diccionario explicito de instituciones validadas por usuario.
    2) Fallback heuristico para entidades no mapeadas explicitamente.
    """
    entidades_normalized = _normalize_text(entidad_series)

    segment = entidades_normalized.map(_normalized_segment_map())

    mask_superior = entidades_normalized.str.contains(r"\buniversidad\b", na=False)
    mask_media = entidades_normalized.str.contains(r"\b(bachillerato|prepa|cum)\b", na=False)
    mask_org = entidades_normalized.str.contains(
        r"\b(maristas mexico|pastoral|juventud|juventudes|convocatoria|laicado)\b",
        na=False,
    )
    mask_basica = entidades_normalized.str.contains(r"\b(primaria|secundaria)\b", na=False)
    mask_multinivel = entidades_normalized.str.contains(r"\b(colegio|instituto)\b", na=False)

    segment = np.where(pd.isna(segment) & mask_superior, "Educacion Superior", segment)
    segment = np.where(pd.isna(segment) & mask_media, "Educacion Media Superior", segment)
    segment = np.where(pd.isna(segment) & mask_org, "Instancias Organizacionales", segment)
    segment = np.where(pd.isna(segment) & mask_basica, "Educacion Basica", segment)
    segment = np.where(pd.isna(segment) & mask_multinivel, "Colegios Multinivel", segment)

    # Fallback final para asegurar categoria valida.
    return pd.Series(segment, index=entidad_series.index).fillna("Instancias Organizacionales")


def classify_coverage_description(entidad_series: pd.Series) -> pd.Series:
    """Clasifica cobertura descriptiva por institucion para tabla de riesgo."""
    entidades_normalized = _normalize_text(entidad_series)
    coverage = entidades_normalized.map(_normalized_coverage_map())

    mask_superior = entidades_normalized.str.contains(r"\buniversidad\b", na=False)
    mask_media = entidades_normalized.str.contains(r"\b(bachillerato|prepa|cum)\b", na=False)
    mask_primaria = entidades_normalized.str.contains(r"\bprimaria\b", na=False)
    mask_secundaria = entidades_normalized.str.contains(r"\bsecundaria\b", na=False)
    mask_org = entidades_normalized.str.contains(
        r"\b(maristas mexico|pastoral|juventud|juventudes|convocatoria|laicado)\b",
        na=False,
    )

    coverage = np.where(pd.isna(coverage) & mask_superior, "Universidad", coverage)
    coverage = np.where(pd.isna(coverage) & mask_media, "Bachillerato", coverage)
    coverage = np.where(pd.isna(coverage) & mask_primaria & mask_secundaria, "Primaria y Secundaria", coverage)
    coverage = np.where(pd.isna(coverage) & mask_primaria, "Primaria", coverage)
    coverage = np.where(pd.isna(coverage) & mask_secundaria, "Secundaria", coverage)
    coverage = np.where(pd.isna(coverage) & mask_org, "Coordinacion institucional", coverage)

    return pd.Series(coverage, index=entidad_series.index).fillna("Cobertura no especificada")


def _build_latest_snapshot(data: pd.DataFrame) -> pd.DataFrame:
    """
    Construye snapshot con el ultimo registro por cuenta/plataforma.

    Incluye columna de crecimiento de seguidores contra el periodo previo
    para habilitar visualizacion de dispersión.
    """
    if data.empty:
        return data

    df = data.copy()
    key_col = "id_cuenta" if "id_cuenta" in df.columns else None

    if key_col is not None:
        account_key = key_col
    else:
        account_key = "account_key"
        df[account_key] = (
            df["entidad"].fillna("").astype(str)
            + "||"
            + df["plataforma"].fillna("").astype(str)
        )

    if "fecha" in df.columns and df["fecha"].notna().any():
        df = df.sort_values([account_key, "fecha"]).copy()
        df["seguidores_prev"] = df.groupby(account_key)["seguidores"].shift(1)
        latest_idx = df.groupby(account_key)["fecha"].idxmax()
        snapshot = df.loc[latest_idx].copy()
    else:
        snapshot = df.drop_duplicates(subset=[account_key], keep="last").copy()
        snapshot["seguidores_prev"] = np.nan

    snapshot["seguidores_prev"] = pd.to_numeric(snapshot["seguidores_prev"], errors="coerce").fillna(0)
    snapshot["crecimiento_seguidores"] = snapshot["seguidores"] - snapshot["seguidores_prev"]
    snapshot["segmento_educativo"] = classify_educational_segment(snapshot["entidad"])
    snapshot["cobertura_institucional"] = classify_coverage_description(snapshot["entidad"])
    snapshot["mapeo_explicito"] = _is_explicit_mapping(snapshot["entidad"])
    return snapshot


def _build_level_summary(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Agrega seguidores y engagement ponderado por segmento educativo."""
    if snapshot.empty:
        return pd.DataFrame(columns=["segmento_educativo", "seguidores", "engagement_ponderado", "entidades"])

    grouped = (
        snapshot.groupby("segmento_educativo", as_index=False)
        .agg(
            seguidores=("seguidores", "sum"),
            entidades=("entidad", "nunique"),
        )
    )

    engagement_by_level = (
        snapshot.groupby("segmento_educativo")
        .apply(calcular_kpi_engagement_global)
        .rename("engagement_ponderado")
        .reset_index()
    )

    out = grouped.merge(engagement_by_level, on="segmento_educativo", how="left")
    out["engagement_ponderado"] = pd.to_numeric(out["engagement_ponderado"], errors="coerce").fillna(0)
    out["segmento_educativo"] = pd.Categorical(
        out["segmento_educativo"],
        categories=SEGMENT_ORDER,
        ordered=True,
    )
    out = out.sort_values("segmento_educativo").reset_index(drop=True)
    return out


def _classify_risk(score: pd.Series) -> pd.Series:
    """Clasifica riesgo institucional con umbrales fijos aprobados."""
    return pd.Series(
        np.select(
            [
                score < CRITICAL_THRESHOLD,
                (score >= CRITICAL_THRESHOLD) & (score < HEALTHY_THRESHOLD),
                score >= HEALTHY_THRESHOLD,
            ],
            ["Riesgo Critico", "Desempeno Regular", "Saludable"],
            default="Desempeno Regular",
        ),
        index=score.index,
    )


def _build_risk_table(full_data: pd.DataFrame, snapshot: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla de riesgo por entidad usando health_score + engagement ponderado."""
    if full_data.empty or snapshot.empty:
        return pd.DataFrame()

    entity_base = (
        snapshot.groupby(["entidad", "segmento_educativo", "cobertura_institucional"], as_index=False)
        .agg(
            seguidores=("seguidores", "sum"),
            crecimiento_seguidores=("crecimiento_seguidores", "sum"),
            mapeo_explicito=("mapeo_explicito", "all"),
        )
    )

    engagement_entity = (
        snapshot.groupby("entidad")
        .apply(calcular_kpi_engagement_global)
        .rename("engagement_ponderado")
        .reset_index()
    )

    health_entity = (
        full_data.groupby("entidad")
        .apply(calculate_health_score)
        .rename("health_score")
        .reset_index()
    )

    risk_df = entity_base.merge(engagement_entity, on="entidad", how="left")
    risk_df = risk_df.merge(health_entity, on="entidad", how="left")

    risk_df["engagement_ponderado"] = pd.to_numeric(risk_df["engagement_ponderado"], errors="coerce").fillna(0)
    risk_df["health_score"] = pd.to_numeric(risk_df["health_score"], errors="coerce").fillna(0)
    risk_df["categoria_riesgo"] = _classify_risk(risk_df["health_score"])

    recommendation_map = {
        "Riesgo Critico": "Priorizar plan de rescate de contenido y frecuencia semanal.",
        "Desempeno Regular": "Optimizar consistencia editorial y formatos de alto alcance.",
        "Saludable": "Mantener estrategia y escalar mejores practicas.",
    }
    risk_df["recomendacion"] = risk_df["categoria_riesgo"].map(recommendation_map)
    risk_df["prioridad"] = risk_df["categoria_riesgo"].map(RISK_PRIORITY).fillna(9).astype(int)

    risk_df = risk_df.sort_values(["prioridad", "health_score", "engagement_ponderado"], ascending=[True, True, False])
    risk_df = risk_df.drop(columns=["prioridad"])
    return risk_df.reset_index(drop=True)


def _attach_taxonomy_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Anexa columnas de taxonomia a nivel fila para analitica temporal."""
    out = data.copy()
    out["segmento_educativo"] = classify_educational_segment(out["entidad"])
    out["cobertura_institucional"] = classify_coverage_description(out["entidad"])
    out["mapeo_explicito"] = _is_explicit_mapping(out["entidad"])
    return out


def _build_monthly_segment_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula series mensuales por segmento educativo."""
    if data.empty or "fecha" not in data.columns:
        return pd.DataFrame()

    df = data.copy()
    df = df[df["fecha"].notna()].copy()
    if df.empty:
        return pd.DataFrame()

    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby(["mes", "segmento_educativo"], as_index=False)
        .agg(
            seguidores=("seguidores", "sum"),
            interacciones=("interacciones", "sum"),
            entidades=("entidad", "nunique"),
        )
    )
    monthly["engagement_ponderado"] = np.where(
        monthly["seguidores"] > 0,
        (monthly["interacciones"] / monthly["seguidores"]) * 100.0,
        0.0,
    )

    monthly["segmento_educativo"] = pd.Categorical(
        monthly["segmento_educativo"], categories=SEGMENT_ORDER, ordered=True
    )
    monthly = monthly.sort_values(["segmento_educativo", "mes"]).reset_index(drop=True)
    monthly["crecimiento_mensual_seguidores"] = (
        monthly.groupby("segmento_educativo")["seguidores"].diff().fillna(0)
    )
    return monthly


def _build_monthly_platform_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula series mensuales por segmento y red social."""
    if data.empty or "fecha" not in data.columns or "plataforma" not in data.columns:
        return pd.DataFrame()

    df = data.copy()
    df = df[df["fecha"].notna()].copy()
    df = df[df["plataforma"].astype(str).str.strip().ne("")]
    if df.empty:
        return pd.DataFrame()

    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby(["mes", "segmento_educativo", "plataforma"], as_index=False)
        .agg(
            seguidores=("seguidores", "sum"),
            interacciones=("interacciones", "sum"),
        )
    )
    monthly["engagement_ponderado"] = np.where(
        monthly["seguidores"] > 0,
        (monthly["interacciones"] / monthly["seguidores"]) * 100.0,
        0.0,
    )
    return monthly


def _build_topic_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Resume temas por segmento si existe `tema_mas_visto`."""
    if data.empty or "tema_mas_visto" not in data.columns:
        return pd.DataFrame()

    df = data.copy()
    df["tema_mas_visto"] = df["tema_mas_visto"].fillna("").astype(str).str.strip()
    df = df[df["tema_mas_visto"].ne("")]
    if df.empty:
        return pd.DataFrame()

    out = (
        df.groupby(["segmento_educativo", "tema_mas_visto"], as_index=False)
        .agg(
            registros=("tema_mas_visto", "count"),
            interacciones=("interacciones", "sum"),
        )
        .sort_values(["interacciones", "registros"], ascending=False)
        .reset_index(drop=True)
    )
    return out


def _build_content_type_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Resume preferencias de tipo de contenido por segmento educativo."""
    if data.empty:
        return pd.DataFrame()

    content_cols = [
        "engagement_contenido_imagenes",
        "engagement_contenido_links",
        "engagement_contenido_videos",
    ]
    present_cols = [col for col in content_cols if col in data.columns]
    if not present_cols:
        return pd.DataFrame()

    df = data.copy()
    for col in present_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    summary = (
        df.groupby("segmento_educativo", as_index=False)[present_cols]
        .mean()
        .melt(
            id_vars=["segmento_educativo"],
            value_vars=present_cols,
            var_name="tipo_contenido",
            value_name="engagement_promedio",
        )
    )

    label_map = {
        "engagement_contenido_imagenes": "Imagenes",
        "engagement_contenido_links": "Links",
        "engagement_contenido_videos": "Videos",
    }
    summary["tipo_contenido"] = summary["tipo_contenido"].map(label_map).fillna(summary["tipo_contenido"])
    return summary


def _risk_row_style(row: pd.Series) -> list[str]:
    """Resalta filas segun categoria para priorizacion visual en tabla."""
    category = row.get("categoria_riesgo", "")
    if category == "Riesgo Critico":
        return ["background-color: #FFE5E5"] * len(row)
    if category == "Desempeno Regular":
        return ["background-color: #FFF4DB"] * len(row)
    return [""] * len(row)


def render(df: pd.DataFrame | None = None) -> None:
    """Render de la vista Segmentacion de Audiencias y Riesgo."""
    st.title("Segmentacion de Audiencias y Riesgo")
    st.caption("Segmentacion por segmento educativo y matriz de riesgo institucional.")

    data = load_base_data(df)
    data = _apply_sidebar_filters(data)

    if data.empty:
        render_empty_state(
            "**Sin audiencias para los filtros actuales**  \n"
            "Cambia el colegio o el periodo global para explorar otros registros.",
        )
        return

    required_cols = {"entidad", "seguidores", "interacciones"}
    missing_cols = sorted(required_cols - set(data.columns))
    if missing_cols:
        st.error(f"Faltan columnas requeridas para esta vista: {', '.join(missing_cols)}")
        return

    data = _prepare_core_columns(data)
    data_taxonomy = _attach_taxonomy_columns(data)
    snapshot = _build_latest_snapshot(data)
    level_summary = _build_level_summary(snapshot)
    risk_table = _build_risk_table(data, snapshot)
    monthly_segment = _build_monthly_segment_metrics(data_taxonomy)
    monthly_platform = _build_monthly_platform_metrics(data_taxonomy)
    topic_summary = _build_topic_summary(data_taxonomy)
    content_summary = _build_content_type_summary(data_taxonomy)

    unmapped_entities = (
        snapshot.loc[~snapshot["mapeo_explicito"], "entidad"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    unmapped_entities = sorted([name for name in unmapped_entities.unique().tolist() if name])

    if snapshot.empty or level_summary.empty:
        render_empty_state(
            "**No hay base suficiente para el análisis de riesgo**  \n"
            "Se necesitan registros con seguidores e interacciones para construir la segmentación.",
        )
        return

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        MetricCard("Entidades analizadas", int(snapshot["entidad"].nunique()))
    with kpi_col2:
        MetricCard("Seguidores totales", f"{int(snapshot['seguidores'].sum()):,}")
    with kpi_col3:
        MetricCard("Engagement ponderado red", f"{calcular_kpi_engagement_global(snapshot):.2f}%")

    # Resumen ejecutivo para lectura rapida por usuarios no tecnicos.
    latest_month = None
    best_segment_text = "Sin datos suficientes"
    growth_segment_text = "Sin datos suficientes"
    risk_text = "Sin datos suficientes"
    content_text = "Sin datos de contenido"

    if not monthly_segment.empty:
        latest_month = monthly_segment["mes"].max()
        latest_slice = monthly_segment[monthly_segment["mes"] == latest_month]

        if not latest_slice.empty:
            best_segment_row = latest_slice.sort_values("engagement_ponderado", ascending=False).iloc[0]
            best_segment = str(best_segment_row["segmento_educativo"])
            best_segment_text = (
                f"{best_segment} lidera engagement con {best_segment_row['engagement_ponderado']:.2f}% "
                f"en {latest_month}."
            )

            growth_row = latest_slice.sort_values("crecimiento_mensual_seguidores", ascending=False).iloc[0]
            growth_segment_text = (
                f"{growth_row['segmento_educativo']} aporta mayor crecimiento mensual "
                f"({growth_row['crecimiento_mensual_seguidores']:,.0f} seguidores)."
            )

    if not risk_table.empty:
        critical_count = int((risk_table["categoria_riesgo"] == "Riesgo Critico").sum())
        risk_text = (
            f"Hay {critical_count} entidades en riesgo critico. "
            f"Priorizar este grupo acelera recuperacion de la red."
        )

    if not content_summary.empty and not monthly_segment.empty and latest_month is not None:
        latest_slice = monthly_segment[monthly_segment["mes"] == latest_month]
        if not latest_slice.empty:
            best_segment = str(
                latest_slice.sort_values("engagement_ponderado", ascending=False).iloc[0]["segmento_educativo"]
            )
            best_content = content_summary[
                content_summary["segmento_educativo"].astype(str) == best_segment
            ].sort_values("engagement_promedio", ascending=False)
            if not best_content.empty:
                row = best_content.iloc[0]
                content_text = (
                    f"En {best_segment}, el formato mas fuerte es {row['tipo_contenido']} "
                    f"({row['engagement_promedio']:.2f}% promedio)."
                )

    if not topic_summary.empty and not monthly_segment.empty and latest_month is not None:
        latest_slice = monthly_segment[monthly_segment["mes"] == latest_month]
        if not latest_slice.empty:
            best_segment = str(
                latest_slice.sort_values("engagement_ponderado", ascending=False).iloc[0]["segmento_educativo"]
            )
            best_topic = topic_summary[
                topic_summary["segmento_educativo"].astype(str) == best_segment
            ].sort_values("interacciones", ascending=False)
            if not best_topic.empty:
                content_text = content_text + " " + (
                    f"Tema dominante: {best_topic.iloc[0]['tema_mas_visto']} "
                    f"({best_topic.iloc[0]['interacciones']:,.0f} interacciones)."
                )

    st.markdown("### Insights Ejecutivos")
    i1, i2 = st.columns(2)
    with i1:
        st.info(best_segment_text)
        st.info(growth_segment_text)
    with i2:
        st.info(risk_text)
        st.info(content_text)

    tab_seg, tab_trend, tab_risk, tab_content, tab_scatter = st.tabs([
        "Segmentacion por Segmento",
        "Tendencia Mensual",
        "Matriz de Riesgo",
        "Contenido y Temas",
        "Dispersion de Crecimiento",
    ])

    with tab_seg:
        st.subheader("Comparativo por segmento educativo")
        st.dataframe(
            level_summary.rename(
                columns={
                    "segmento_educativo": "Segmento educativo",
                    "seguidores": "Seguidores",
                    "engagement_ponderado": "Engagement ponderado (%)",
                    "entidades": "Entidades",
                }
            ),
            width="stretch",
            hide_index=True,
        )

        if px is None or go is None:
            st.info("Plotly no esta disponible; se muestra solo tabla de segmentacion.")
        else:
            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(
                    x=level_summary["segmento_educativo"],
                    y=level_summary["seguidores"],
                    name="Seguidores",
                    yaxis="y",
                )
            )
            fig_bar.add_trace(
                go.Scatter(
                    x=level_summary["segmento_educativo"],
                    y=level_summary["engagement_ponderado"],
                    name="Engagement ponderado (%)",
                    mode="lines+markers",
                    yaxis="y2",
                )
            )
            fig_bar.update_layout(
                title="Seguidores y engagement ponderado por segmento educativo",
                xaxis_title="Segmento educativo",
                yaxis=dict(title="Seguidores"),
                yaxis2=dict(title="Engagement (%)", overlaying="y", side="right"),
            )
            st.plotly_chart(aplicar_tema_champileaks(fig_bar), width="stretch", config=PLOTLY_CONFIG)

            fig_donut = px.pie(
                level_summary,
                names="segmento_educativo",
                values="seguidores",
                hole=0.45,
                title="Participacion de seguidores por segmento educativo",
            )
            st.plotly_chart(aplicar_tema_champileaks(fig_donut), width="stretch", config=PLOTLY_CONFIG)

    with tab_trend:
        st.subheader("Tendencia mensual por segmento educativo")

        if monthly_segment.empty:
            st.info("No hay datos temporales suficientes para tendencia mensual.")
        else:
            latest_month = monthly_segment["mes"].max()
            latest_slice = monthly_segment[monthly_segment["mes"] == latest_month]

            if not latest_slice.empty:
                best_row = latest_slice.sort_values("engagement_ponderado", ascending=False).iloc[0]
                st.metric(
                    "Mejor engagement del ultimo mes",
                    f"{best_row['segmento_educativo']} ({best_row['engagement_ponderado']:.2f}%)",
                )

            if px is not None:
                fig_eng_month = px.line(
                    monthly_segment,
                    x="mes",
                    y="engagement_ponderado",
                    color="segmento_educativo",
                    markers=True,
                    title="Evolucion mensual de engagement ponderado por segmento",
                    labels={
                        "mes": "Mes",
                        "engagement_ponderado": "Engagement ponderado (%)",
                        "segmento_educativo": "Segmento educativo",
                    },
                )
                st.plotly_chart(aplicar_tema_champileaks(fig_eng_month), width="stretch", config=PLOTLY_CONFIG)

                fig_growth_month = px.bar(
                    monthly_segment,
                    x="mes",
                    y="crecimiento_mensual_seguidores",
                    color="segmento_educativo",
                    barmode="group",
                    title="Crecimiento mensual de seguidores por segmento",
                    labels={
                        "mes": "Mes",
                        "crecimiento_mensual_seguidores": "Crecimiento mensual",
                        "segmento_educativo": "Segmento educativo",
                    },
                )
                st.plotly_chart(aplicar_tema_champileaks(fig_growth_month), width="stretch", config=PLOTLY_CONFIG)

        st.subheader("Tendencia por red social dentro de cada segmento")
        if monthly_platform.empty:
            st.info("No hay datos de plataformas suficientes para tendencia por red social.")
        else:
            segments_available = [
                seg for seg in SEGMENT_ORDER
                if seg in monthly_platform["segmento_educativo"].astype(str).unique()
            ]
            selected_segment = st.selectbox(
                "Selecciona segmento educativo",
                options=segments_available if segments_available else sorted(monthly_platform["segmento_educativo"].astype(str).unique()),
                key="audience_risk_segment_platform",
            )
            platform_slice = monthly_platform[
                monthly_platform["segmento_educativo"].astype(str) == str(selected_segment)
            ]

            if px is not None and not platform_slice.empty:
                fig_platform_eng = px.line(
                    platform_slice,
                    x="mes",
                    y="engagement_ponderado",
                    color="plataforma",
                    markers=True,
                    title=f"Engagement mensual por red social - {selected_segment}",
                    labels={
                        "mes": "Mes",
                        "engagement_ponderado": "Engagement ponderado (%)",
                        "plataforma": "Red social",
                    },
                )
                st.plotly_chart(aplicar_tema_champileaks(fig_platform_eng), width="stretch", config=PLOTLY_CONFIG)

    with tab_risk:
        st.subheader("Matriz de riesgo institucional")

        if unmapped_entities:
            st.warning(
                "Instituciones fuera del mapeo explicito detectadas: "
                + ", ".join(unmapped_entities)
                + ". Se clasificaron con fallback heuristico."
            )

        if risk_table.empty:
            st.info("No hay datos suficientes para construir la matriz de riesgo.")
        else:
            critical_count = int((risk_table["categoria_riesgo"] == "Riesgo Critico").sum())
            regular_count = int((risk_table["categoria_riesgo"] == "Desempeno Regular").sum())
            healthy_count = int((risk_table["categoria_riesgo"] == "Saludable").sum())

            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("Riesgo Critico", critical_count)
            with r2:
                st.metric("Desempeno Regular", regular_count)
            with r3:
                st.metric("Saludable", healthy_count)

            risk_display = risk_table[
                [
                    "entidad",
                    "segmento_educativo",
                    "cobertura_institucional",
                    "mapeo_explicito",
                    "seguidores",
                    "crecimiento_seguidores",
                    "engagement_ponderado",
                    "health_score",
                    "categoria_riesgo",
                    "recomendacion",
                ]
            ].rename(
                columns={
                    "entidad": "Entidad",
                    "segmento_educativo": "Segmento educativo",
                    "cobertura_institucional": "Cobertura institucional",
                    "mapeo_explicito": "Mapeo institucional",
                    "seguidores": "Seguidores",
                    "crecimiento_seguidores": "Crecimiento seguidores",
                    "engagement_ponderado": "Engagement ponderado (%)",
                    "health_score": "Health score",
                    "categoria_riesgo": "Categoria riesgo",
                    "recomendacion": "Recomendacion",
                }
            )

            styled = risk_display.style.format(
                {
                    "Mapeo institucional": lambda value: "Explicito" if bool(value) else "Fallback",
                    "Seguidores": "{:,.0f}",
                    "Crecimiento seguidores": "{:,.0f}",
                    "Engagement ponderado (%)": "{:.2f}",
                    "Health score": "{:.2f}",
                }
            ).apply(_risk_row_style, axis=1)

            st.dataframe(styled, width="stretch", hide_index=True)

            critical_only = risk_display[risk_display["Categoria riesgo"] == "Riesgo Critico"]
            if not critical_only.empty:
                st.markdown("**Entidades prioritarias (Riesgo Critico)**")
                st.dataframe(critical_only, width="stretch", hide_index=True)

    with tab_content:
        st.subheader("Tipos de contenido con mejor engagement por segmento")
        if content_summary.empty:
            st.info("No hay columnas de contenido suficientes para este analisis.")
        else:
            if px is not None:
                fig_content = px.bar(
                    content_summary,
                    x="segmento_educativo",
                    y="engagement_promedio",
                    color="tipo_contenido",
                    barmode="group",
                    title="Engagement promedio por tipo de contenido y segmento",
                    labels={
                        "segmento_educativo": "Segmento educativo",
                        "engagement_promedio": "Engagement promedio (%)",
                        "tipo_contenido": "Tipo de contenido",
                    },
                )
                st.plotly_chart(aplicar_tema_champileaks(fig_content), width="stretch", config=PLOTLY_CONFIG)

            top_content = (
                content_summary.sort_values("engagement_promedio", ascending=False)
                .groupby("segmento_educativo", as_index=False)
                .first()
            )
            st.dataframe(
                top_content.rename(
                    columns={
                        "segmento_educativo": "Segmento educativo",
                        "tipo_contenido": "Tipo de contenido lider",
                        "engagement_promedio": "Engagement promedio (%)",
                    }
                ),
                width="stretch",
                hide_index=True,
            )

        st.subheader("Temas con mayor consumo por segmento")
        if topic_summary.empty:
            st.info("No hay columna `tema_mas_visto` disponible en el dataset actual.")
        else:
            top_topics = topic_summary.head(20).copy()
            if px is not None:
                fig_topics = px.bar(
                    top_topics,
                    x="interacciones",
                    y="tema_mas_visto",
                    color="segmento_educativo",
                    orientation="h",
                    title="Top temas por interacciones (segmentado)",
                    labels={
                        "interacciones": "Interacciones",
                        "tema_mas_visto": "Tema",
                        "segmento_educativo": "Segmento educativo",
                    },
                )
                st.plotly_chart(aplicar_tema_champileaks(fig_topics), width="stretch", config=PLOTLY_CONFIG)

            st.dataframe(
                top_topics.rename(
                    columns={
                        "segmento_educativo": "Segmento educativo",
                        "tema_mas_visto": "Tema",
                        "registros": "Registros",
                        "interacciones": "Interacciones",
                    }
                ),
                width="stretch",
                hide_index=True,
            )

    with tab_scatter:
        st.subheader("Crecimiento de seguidores vs engagement por segmento")

        scatter_data = (
            snapshot.groupby("segmento_educativo", as_index=False)
            .agg(
                seguidores=("seguidores", "sum"),
                crecimiento_seguidores=("crecimiento_seguidores", "sum"),
            )
        )
        engagement_scatter = (
            snapshot.groupby("segmento_educativo")
            .apply(calcular_kpi_engagement_global)
            .rename("engagement_ponderado")
            .reset_index()
        )
        scatter_data = scatter_data.merge(engagement_scatter, on="segmento_educativo", how="left")

        if px is None:
            st.info("Plotly no esta disponible; se omite la visualizacion de dispersion.")
        else:
            fig_scatter = px.scatter(
                scatter_data,
                x="crecimiento_seguidores",
                y="engagement_ponderado",
                size="seguidores",
                color="segmento_educativo",
                hover_name="segmento_educativo",
                title="Relacion crecimiento vs engagement por segmento educativo",
                labels={
                    "crecimiento_seguidores": "Crecimiento de seguidores",
                    "engagement_ponderado": "Engagement ponderado (%)",
                    "segmento_educativo": "Segmento educativo",
                },
            )
            st.plotly_chart(aplicar_tema_champileaks(fig_scatter), width="stretch", config=PLOTLY_CONFIG)

            if "plataforma" in snapshot.columns:
                platform_strength = (
                    snapshot[snapshot["plataforma"].astype(str).str.strip().ne("")]
                    .groupby(["segmento_educativo", "plataforma"], as_index=False)["seguidores"]
                    .sum()
                )
                if not platform_strength.empty:
                    fig_strength = px.bar(
                        platform_strength,
                        x="segmento_educativo",
                        y="seguidores",
                        color="plataforma",
                        barmode="group",
                        title="Fortaleza por red social y segmento educativo",
                        labels={
                            "segmento_educativo": "Segmento educativo",
                            "seguidores": "Seguidores",
                            "plataforma": "Red social",
                        },
                    )
                    st.plotly_chart(aplicar_tema_champileaks(fig_strength), width="stretch", config=PLOTLY_CONFIG)
