"""Contexto oficial agregado para el Módulo Satélite.

Este módulo es deliberadamente puro: recibe DataFrames ya cargados, no accede
a Google Sheets, no usa Streamlit y nunca cruza filas oficiales con filas
transaccionales del satélite.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Final

import pandas as pd

from utils.account_normalization import normalize_platform_name
from utils.form_response_importer import normalize_institution_name
from utils.logger import get_logger
from utils.metric_catalog import INTERACTION_ALIASES, VISUALIZATION_ALIASES
from utils.text_mining import keyword_frequency


logger = get_logger(__name__)


MAESTRA_COLUMNS: Final[tuple[str, ...]] = (
    "fecha",
    "colegio",
    "plataforma",
    "metrica",
    "valor",
)
DEMOGRAPHIC_COLUMNS: Final[tuple[str, ...]] = (
    "fecha_reporte",
    "colegio",
    "plataforma",
    "criterio",
    "sexo",
    "edad",
    "ubicacion",
    "valor",
)
COMMENT_COLUMNS: Final[tuple[str, ...]] = (
    "institucion",
    "institucion_nombre",
    "fecha_carga",
    "fuente",
    "comentario",
    "sentimiento_etiqueta",
    "sentimiento_score",
    "categoria",
)
AUDIENCE_COLUMNS: Final[tuple[str, ...]] = ("sexo", "edad", "valor")
WORD_COLUMNS: Final[tuple[str, ...]] = ("palabra", "total")
SENTIMENT_COLUMNS: Final[tuple[str, ...]] = ("sentimiento", "total")
FORM_STRATEGIC_FIELDS: Final[tuple[str, ...]] = (
    "engagement_rate",
    "publicaciones_por_semana",
    "engagement_contenido_videos",
    "engagement_contenido_imagenes",
    "engagement_contenido_links",
    "tema_mas_visto",
    "engagement_tema_mas_visto",
    "publicacion_mas_interacciones",
    "se_considera_viral_280",
    "media_visualizaciones",
    "media_interaccion",
    "calificacion_redes",
    "tipo_contenido_mas_viral",
    "novedoso_video_viral",
    "calificacion_contenido",
)
FORM_STRATEGIC_LABELS: Final[dict[str, str]] = {
    "engagement_rate": "Engagement Rate (%)",
    "publicaciones_por_semana": "Publicaciones x semana",
    "engagement_contenido_videos": "Engagement por contenido: Videos",
    "engagement_contenido_imagenes": "Engagement por contenido: Imágenes",
    "engagement_contenido_links": "Engagement por contenido: Links",
    "tema_mas_visto": "Tema más visto",
    "engagement_tema_mas_visto": "Engagement del tema más visto",
    "publicacion_mas_interacciones": "Publicación con más interacciones",
    "se_considera_viral_280": "Se considera viral (+280 interacciones)",
    "media_visualizaciones": "Media de visualizaciones",
    "media_interaccion": "Media de interacción",
    "calificacion_redes": "Calificación en redes",
    "tipo_contenido_mas_viral": "Tipo de contenido más viral",
    "novedoso_video_viral": "Novedad del video viral",
    "calificacion_contenido": "Calificación del contenido (1-10)",
}
FORM_HEADER_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "marca_temporal": ("marca temporal", "marca_temporal", "timestamp"),
    "fecha": ("fecha", "fecha del reporte", "fecha reporte"),
    "institucion": ("institucion", "institucion marista", "entidad", "colegio"),
    "plataforma": ("plataforma", "plataforma social", "fuente"),
    "engagement_rate": ("engagement rate", "engagement rate (%)", "engagment rate"),
    "publicaciones_por_semana": ("publicaciones por semana", "publicaciones x semana", "publicaciones/semana"),
    "engagement_contenido_videos": ("engagement por contenido: videos", "engagment por contenido: videos"),
    "engagement_contenido_imagenes": ("engagement por contenido: imagenes", "engagment por contenido: imagenes"),
    "engagement_contenido_links": ("engagement por contenido: links", "engagment por contenido: links"),
    "tema_mas_visto": ("tema mas visto",),
    "engagement_tema_mas_visto": ("engagement del tema mas visto", "engagment del tema mas visto"),
    "publicacion_mas_interacciones": ("publicacion con mas interacciones", "publicacion mas interacciones"),
    "se_considera_viral_280": ("se considera viral ( + 280 interacciones )", "se considera viral (+ 280 interacciones)", "se considera viral 280 interacciones"),
    "media_visualizaciones": ("media de visualizaciones",),
    "media_interaccion": ("media de interaccion", "media de interacciones"),
    "calificacion_redes": ("calificacion en redes",),
    "tipo_contenido_mas_viral": ("que tipo de contenido fue el mas viral",),
    "novedoso_video_viral": ("que es lo mas novedoso del video viral",),
    "calificacion_contenido": ("del 1 al 10 que calificacion le pones al contenido de la pagina",),
}


@dataclass(frozen=True)
class OfficialPerformanceContext:
    """Totales oficiales de métricas de flujo para el corte elegido."""

    interacciones: object
    visualizaciones: object
    rows_used: int
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfficialTextContext:
    """Resultado textual agregado y auditable de las hojas oficiales."""

    comentarios: pd.DataFrame
    top_words: pd.DataFrame
    sentiment_distribution: pd.DataFrame
    warnings: tuple[str, ...] = ()
    total_fuente: int = 0
    total_original: int = 0
    deduplicados: int = 0
    total_final: int = 0


@dataclass(frozen=True)
class OfficialDemographicContext:
    """Segmentos oficiales dominantes, sin relación fila-a-fila con el satélite."""

    sexo_edad_top: pd.DataFrame
    ubicacion_top: object
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfficialFormContext:
    """Ficha estratégica de la última respuesta oficial del periodo."""

    ficha_estrategica: dict[str, object]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfficialCoverageComparison:
    """Comparación explícita entre total oficial y muestra granular."""

    official_total: object
    sample_total: object
    coverage_pct: object
    undisaggregated: object
    message: str
    is_critical: bool


@dataclass(frozen=True)
class OfficialContext:
    """Respuesta estable del Puente de Contexto Oficial."""

    colegio_id: str | None
    colegio_nombre_canonico: str | None
    plataforma: str | None
    mes_clave: str | None
    performance: OfficialPerformanceContext
    demografia_top: pd.DataFrame
    ubicacion_top: object
    text: OfficialTextContext
    ficha_estrategica: dict[str, object]
    warnings: tuple[str, ...] = ()

    @property
    def audience_top(self) -> pd.DataFrame:
        """Alias retrocompatible para la audiencia dominante sexo × edad."""
        return self.demografia_top


def _empty_frame(columns: tuple[str, ...]) -> pd.DataFrame:
    return pd.DataFrame(columns=list(columns))


def _copy_with_columns(frame: pd.DataFrame | None, columns: tuple[str, ...]) -> pd.DataFrame:
    """Copia una fuente y agrega columnas ausentes para evitar KeyError."""
    local = frame.copy() if frame is not None else pd.DataFrame()
    for column in columns:
        if column not in local.columns:
            local[column] = pd.NA
    return local


def _identity_key(value: object) -> str:
    """Crea una llave de comparación resistente a acentos y puntuación."""
    canonical = normalize_institution_name("" if pd.isna(value) else str(value))
    folded = unicodedata.normalize("NFKD", canonical)
    return "".join(
        character.lower()
        for character in folded
        if not unicodedata.combining(character) and character.isalnum()
    )


def _metric_key(value: object) -> str:
    raw = "" if pd.isna(value) else str(value)
    folded = unicodedata.normalize("NFKD", raw)
    return " ".join(
        "".join(
            character.lower()
            for character in folded
            if not unicodedata.combining(character)
            and (character.isalnum() or character.isspace())
        ).split()
    )


def _platform_key(value: object) -> str:
    """Genera la misma llave normalizada para fuente y filtro seleccionado."""
    raw = "" if pd.isna(value) else str(value).strip()
    return normalize_platform_name(raw).strip().casefold()


def _as_number_or_na(value: object) -> object:
    parsed = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return pd.NA if pd.isna(parsed) else float(parsed)


def _sum_or_na(series: pd.Series) -> object:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    return pd.NA if numeric.empty else float(numeric.sum())


def resolve_official_school_name(
    df_cuentas_satellite: pd.DataFrame,
    colegio_id: str | None,
    *,
    official_colegio: str | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    """Resuelve colegio_id satélite a nombre institucional canónico.

    ``official_colegio`` sólo cubre el modo sin muestra satélite: el usuario
    selecciona un colegio que existe únicamente en las hojas oficiales.
    """
    if colegio_id is None:
        if official_colegio:
            canonical = normalize_institution_name(official_colegio).strip()
            return (canonical or None, ())
        return None, ()

    accounts = _copy_with_columns(
        df_cuentas_satellite,
        ("id_cuenta", "colegio_id", "colegio_nombre"),
    )
    selected = accounts.loc[accounts["colegio_id"].astype("string").eq(colegio_id)].copy()
    if selected.empty:
        return (
            None,
            (f"No existe colegio_id={colegio_id!r} en la dimensión satélite.",),
        )

    names = selected["colegio_nombre"].dropna().astype("string").str.strip()
    names = names.loc[names.ne("")].drop_duplicates()
    if names.empty:
        return (
            None,
            (f"colegio_id={colegio_id!r} no tiene colegio_nombre para mapear a Sheets.",),
        )

    canonical = normalize_institution_name(str(names.iloc[0])).strip()
    if not canonical:
        return (
            None,
            (f"No se pudo canonizar el colegio asociado a colegio_id={colegio_id!r}.",),
        )
    return canonical, ()


def _filter_maestra(
    df_base_maestra: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> pd.DataFrame:
    local = _copy_with_columns(df_base_maestra, MAESTRA_COLUMNS)
    local = local.loc[:, list(MAESTRA_COLUMNS)].copy()
    local["fecha"] = pd.to_datetime(local["fecha"], errors="coerce")
    local["valor"] = pd.to_numeric(local["valor"], errors="coerce")
    local["colegio_key"] = local["colegio"].map(_identity_key)
    local["plataforma_key"] = local["plataforma"].map(_platform_key)
    local["metrica_key"] = local["metrica"].map(_metric_key)
    local["mes_clave"] = local["fecha"].dt.strftime("%Y-%m")
    local = local.loc[local["fecha"].notna() & local["valor"].notna() & local["valor"].ge(0)].copy()

    if colegio_nombre_canonico:
        local = local.loc[local["colegio_key"].eq(_identity_key(colegio_nombre_canonico))].copy()
    if plataforma:
        local = local.loc[local["plataforma_key"].eq(_platform_key(plataforma))].copy()
    if mes_clave:
        local = local.loc[local["mes_clave"].eq(mes_clave)].copy()
    return local


def build_official_performance_context(
    df_base_maestra: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> OfficialPerformanceContext:
    """Suma flujos oficiales diarios de interacciones y visualizaciones."""
    filtered = _filter_maestra(
        df_base_maestra,
        colegio_nombre_canonico=colegio_nombre_canonico,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    interaction_rows = filtered.loc[
        filtered["metrica_key"].isin(INTERACTION_ALIASES)
    ].copy()
    visualization_rows = filtered.loc[
        filtered["metrica_key"].isin(VISUALIZATION_ALIASES)
    ].copy()

    warnings: list[str] = []
    interacciones = _sum_or_na(interaction_rows["valor"])
    visualizaciones = _sum_or_na(visualization_rows["valor"])
    if pd.isna(interacciones):
        warnings.append("No hay interacciones oficiales para el corte seleccionado.")
    if pd.isna(visualizaciones):
        warnings.append("No hay visualizaciones oficiales para el corte seleccionado.")

    return OfficialPerformanceContext(
        interacciones=interacciones,
        visualizaciones=visualizaciones,
        rows_used=len(filtered),
        warnings=tuple(warnings),
    )


def _filter_demographic(
    df_base_demografica: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
    criterio_key: str = "demografia base",
) -> pd.DataFrame:
    local = _copy_with_columns(df_base_demografica, DEMOGRAPHIC_COLUMNS)
    local = local.loc[:, list(DEMOGRAPHIC_COLUMNS)].copy()
    local["fecha_reporte"] = pd.to_datetime(local["fecha_reporte"], errors="coerce")
    local["valor"] = pd.to_numeric(local["valor"], errors="coerce")
    local["colegio_key"] = local["colegio"].map(_identity_key)
    local["plataforma_key"] = local["plataforma"].map(_platform_key)
    local["criterio_key"] = local["criterio"].map(_metric_key)
    local["mes_clave"] = local["fecha_reporte"].dt.strftime("%Y-%m")
    local = local.loc[
        local["fecha_reporte"].notna()
        & local["valor"].notna()
        & local["valor"].ge(0)
        & local["criterio_key"].eq(criterio_key)
    ].copy()

    if colegio_nombre_canonico:
        local = local.loc[local["colegio_key"].eq(_identity_key(colegio_nombre_canonico))].copy()
    if plataforma:
        local = local.loc[local["plataforma_key"].eq(_platform_key(plataforma))].copy()
    if mes_clave:
        local = local.loc[local["mes_clave"].eq(mes_clave)].copy()
    return local


def build_audience_context(
    df_base_demografica: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Devuelve el segmento sexo × edad dominante del corte oficial."""
    filtered = _filter_demographic(
        df_base_demografica,
        colegio_nombre_canonico=colegio_nombre_canonico,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    segments_source = filtered.loc[
        filtered["sexo"].astype("string").str.strip().ne("")
        & filtered["edad"].astype("string").str.strip().ne("")
    ].copy()
    if segments_source.empty:
        return _empty_frame(AUDIENCE_COLUMNS), (
            "No hay segmentos demográficos oficiales para el corte seleccionado.",
        )

    segments = (
        segments_source.groupby(["sexo", "edad"], as_index=False, dropna=False)["valor"]
        .sum(min_count=1)
        .sort_values(["valor", "sexo", "edad"], ascending=[False, True, True], kind="stable")
        .head(1)
        .reset_index(drop=True)
        .copy()
    )
    return segments.loc[:, list(AUDIENCE_COLUMNS)].copy(), ()


def build_demographic_context(
    df_base_demografica: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> OfficialDemographicContext:
    """Calcula sexo × edad y ubicación dominantes desde la fuente oficial."""
    geographic_rows = _filter_demographic(
        df_base_demografica,
        colegio_nombre_canonico=colegio_nombre_canonico,
        plataforma=plataforma,
        mes_clave=mes_clave,
        criterio_key="ciudad",
    )
    sexo_edad_top, audience_warnings = build_audience_context(
        df_base_demografica,
        colegio_nombre_canonico=colegio_nombre_canonico,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    locations = geographic_rows.loc[
        geographic_rows["ubicacion"].astype("string").str.strip().ne("")
    ].copy()
    if locations.empty:
        return OfficialDemographicContext(
            sexo_edad_top=sexo_edad_top.copy(),
            ubicacion_top=pd.NA,
            warnings=tuple((*audience_warnings, "No hay ubicación oficial para el corte seleccionado.")),
        )
    top_location = (
        locations.groupby("ubicacion", as_index=False, dropna=False)["valor"]
        .sum(min_count=1)
        .sort_values(["valor", "ubicacion"], ascending=[False, True], kind="stable")
        .iloc[0]
    )
    return OfficialDemographicContext(
        sexo_edad_top=sexo_edad_top.copy(),
        ubicacion_top=top_location["ubicacion"],
        warnings=audience_warnings,
    )


def _prepare_official_comments(
    frame: pd.DataFrame,
    *,
    origin: str,
) -> pd.DataFrame:
    local = _copy_with_columns(frame, COMMENT_COLUMNS)
    local = local.loc[:, list(COMMENT_COLUMNS)].copy()
    local["institucion_nombre"] = local["institucion_nombre"].where(
        local["institucion_nombre"].notna() & local["institucion_nombre"].astype("string").str.strip().ne(""),
        local["institucion"],
    )
    local["fecha_carga"] = pd.to_datetime(local["fecha_carga"], errors="coerce")
    local["comentario"] = local["comentario"].fillna("").astype("string").str.strip()
    local["sentimiento_etiqueta"] = (
        local["sentimiento_etiqueta"].fillna("Sin clasificar").astype("string").str.strip()
    )
    local["institucion_key"] = local["institucion_nombre"].map(_identity_key)
    local["plataforma_key"] = local["fuente"].map(_platform_key)
    local["mes_clave"] = local["fecha_carga"].dt.strftime("%Y-%m")
    local["fecha_dia"] = local["fecha_carga"].dt.strftime("%Y-%m-%d")
    local["origen_hoja"] = origin
    return local.loc[local["fecha_carga"].notna() & local["comentario"].ne("")].copy()


def build_text_context(
    df_comentarios_consolidados: pd.DataFrame,
    df_videos_virales: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> OfficialTextContext:
    """Une, deduplica y agrega el contexto textual oficial sin usar merges."""
    consolidated = _prepare_official_comments(
        df_comentarios_consolidados,
        origin="Comentarios Consolidados",
    )
    viral = _prepare_official_comments(df_videos_virales, origin="Videos Virales")
    total_fuente = len(consolidated) + len(viral)
    combined = pd.concat([consolidated, viral], ignore_index=True, sort=False).copy()

    if colegio_nombre_canonico:
        combined = combined.loc[
            combined["institucion_key"].eq(_identity_key(colegio_nombre_canonico))
        ].copy()
    if plataforma:
        combined = combined.loc[combined["plataforma_key"].eq(_platform_key(plataforma))].copy()
    if mes_clave:
        combined = combined.loc[combined["mes_clave"].eq(mes_clave)].copy()

    total_original = len(combined)
    combined = combined.drop_duplicates(
        subset=["institucion_key", "fecha_dia", "plataforma_key", "comentario"],
        keep="last",
    ).reset_index(drop=True).copy()
    total_final = len(combined)
    deduplicados = total_original - total_final
    if combined.empty:
        return OfficialTextContext(
            comentarios=combined,
            top_words=_empty_frame(WORD_COLUMNS),
            sentiment_distribution=_empty_frame(SENTIMENT_COLUMNS),
            warnings=("No hay comentarios oficiales para el corte seleccionado.",),
            total_fuente=total_fuente,
            total_original=total_original,
            deduplicados=deduplicados,
            total_final=total_final,
        )

    top_words = keyword_frequency(combined, "comentario", top_n=3).copy()
    sentiment_distribution = (
        combined["sentimiento_etiqueta"]
        .replace("", "Sin clasificar")
        .value_counts(dropna=False)
        .rename_axis("sentimiento")
        .reset_index(name="total")
        .copy()
    )
    return OfficialTextContext(
        comentarios=combined.copy(),
        top_words=top_words.loc[:, list(WORD_COLUMNS)].copy(),
        sentiment_distribution=sentiment_distribution.loc[:, list(SENTIMENT_COLUMNS)].copy(),
        total_fuente=total_fuente,
        total_original=total_original,
        deduplicados=deduplicados,
        total_final=total_final,
    )


def _form_header_key(value: object) -> str:
    raw = "" if pd.isna(value) else str(value)
    folded = unicodedata.normalize("NFKD", raw)
    characters = (
        character.lower()
        for character in folded
        if not unicodedata.combining(character)
    )
    normalized = "".join(
        character if character.isalnum() else " " for character in characters
    )
    return " ".join(normalized.split())


def _normalize_form_context_frame(df_formulario: pd.DataFrame) -> pd.DataFrame:
    """Canoniza encabezados del formulario sin depender de espacios o acentos."""
    source = df_formulario.copy()
    aliases = {
        canonical: {_form_header_key(canonical), *(_form_header_key(alias) for alias in values)}
        for canonical, values in FORM_HEADER_ALIASES.items()
    }
    normalized = pd.DataFrame(index=source.index)
    for canonical, accepted_keys in aliases.items():
        candidates = [column for column in source.columns if _form_header_key(column) in accepted_keys]
        if not candidates:
            normalized[canonical] = pd.NA
            continue
        candidate_values = source.loc[:, candidates].copy()
        candidate_values = candidate_values.replace(r"^\s*$", pd.NA, regex=True)
        normalized[canonical] = candidate_values.bfill(axis=1).iloc[:, 0]
    normalized["fecha"] = pd.to_datetime(normalized["fecha"], errors="coerce", format="mixed")
    normalized["marca_temporal"] = pd.to_datetime(
        normalized["marca_temporal"],
        errors="coerce",
        format="mixed",
    )
    normalized["institucion_key"] = normalized["institucion"].map(_identity_key)
    normalized["plataforma_key"] = normalized["plataforma"].map(_platform_key)
    normalized["mes_clave"] = normalized["fecha"].dt.strftime("%Y-%m")
    return normalized.copy()


def _form_value_or_na(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str):
        clean = value.strip()
        return pd.NA if not clean else clean
    return value


def build_form_context(
    df_formulario: pd.DataFrame,
    *,
    colegio_nombre_canonico: str | None,
    plataforma: str | None,
    mes_clave: str | None,
) -> OfficialFormContext:
    """Extrae una ficha estratégica oficial; duplicados se resuelven por fecha."""
    normalized = _normalize_form_context_frame(df_formulario)
    filtered = normalized.loc[normalized["fecha"].notna()].copy()
    if colegio_nombre_canonico:
        filtered = filtered.loc[
            filtered["institucion_key"].eq(_identity_key(colegio_nombre_canonico))
        ].copy()
    if plataforma:
        filtered = filtered.loc[filtered["plataforma_key"].eq(_platform_key(plataforma))].copy()
    if mes_clave:
        filtered = filtered.loc[filtered["mes_clave"].eq(mes_clave)].copy()
    if filtered.empty:
        return OfficialFormContext(
            ficha_estrategica={},
            warnings=("No hay ficha estratégica oficial para el corte seleccionado.",),
        )

    filtered = filtered.sort_values(
        ["fecha", "marca_temporal"],
        ascending=[False, False],
        na_position="last",
        kind="stable",
    ).copy()
    selected = filtered.iloc[0]
    warnings: tuple[str, ...] = ()
    if len(filtered) > 1:
        logger.warning(
            "Ficha estratégica: %s duplicados para colegio=%r plataforma=%r mes=%r; "
            "se usó fecha=%s y marca_temporal=%s.",
            len(filtered),
            colegio_nombre_canonico,
            plataforma,
            mes_clave,
            selected["fecha"],
            selected["marca_temporal"],
        )
        warnings = (
            f"Se detectaron {len(filtered)} respuestas de formulario para el corte; se usó la fecha más reciente.",
        )
    ficha = {
        field: value
        for field in FORM_STRATEGIC_FIELDS
        if not pd.isna(value := _form_value_or_na(selected.get(field)))
    }
    return OfficialFormContext(ficha_estrategica=ficha, warnings=warnings)


def build_coverage_comparison(
    official_total: object,
    sample_total: object,
    *,
    metric_label: str,
) -> OfficialCoverageComparison:
    """Construye cobertura y brecha sin confundir la muestra con una caída."""
    official = _as_number_or_na(official_total)
    sample = _as_number_or_na(sample_total)
    if pd.isna(official) or pd.isna(sample):
        return OfficialCoverageComparison(
            official_total=official,
            sample_total=sample,
            coverage_pct=pd.NA,
            undisaggregated=pd.NA,
            message=f"Sin datos suficientes para comparar {metric_label.lower()}.",
            is_critical=False,
        )
    if official <= 0:
        return OfficialCoverageComparison(
            official_total=official,
            sample_total=sample,
            coverage_pct=pd.NA,
            undisaggregated=pd.NA,
            message=f"El total oficial de {metric_label.lower()} es cero; cobertura no disponible.",
            is_critical=sample > 0,
        )

    coverage = (sample / official) * 100.0
    difference = official - sample
    if difference >= 0:
        return OfficialCoverageComparison(
            official_total=official,
            sample_total=sample,
            coverage_pct=coverage,
            undisaggregated=difference,
            message=f"No desglosadas en la muestra: {difference:,.0f}",
            is_critical=False,
        )
    return OfficialCoverageComparison(
        official_total=official,
        sample_total=sample,
        coverage_pct=coverage,
        undisaggregated=abs(difference),
        message=f"La muestra excede el total oficial por {abs(difference):,.0f}",
        is_critical=True,
    )


def build_satellite_official_context(
    df_cuentas_satellite: pd.DataFrame,
    df_base_maestra: pd.DataFrame,
    df_base_demografica: pd.DataFrame,
    df_comentarios_consolidados: pd.DataFrame,
    df_videos_virales: pd.DataFrame,
    df_formulario: pd.DataFrame | None = None,
    *,
    colegio_id: str | None,
    plataforma: str | None,
    mes_clave: str | None,
    official_colegio: str | None = None,
) -> OfficialContext:
    """Orquesta los agregados oficiales sin cruzarlos con filas satélite."""
    colegio_nombre, identity_warnings = resolve_official_school_name(
        df_cuentas_satellite,
        colegio_id,
        official_colegio=official_colegio,
    )
    if colegio_id is not None and colegio_nombre is None:
        unavailable = "No se puede consultar el contexto oficial sin una equivalencia institucional."
        return OfficialContext(
            colegio_id=colegio_id,
            colegio_nombre_canonico=None,
            plataforma=plataforma,
            mes_clave=mes_clave,
            performance=OfficialPerformanceContext(
                interacciones=pd.NA,
                visualizaciones=pd.NA,
                rows_used=0,
                warnings=(unavailable,),
            ),
            demografia_top=_empty_frame(AUDIENCE_COLUMNS),
            ubicacion_top=pd.NA,
            text=OfficialTextContext(
                comentarios=_empty_frame((*COMMENT_COLUMNS, "origen_hoja")),
                top_words=_empty_frame(WORD_COLUMNS),
                sentiment_distribution=_empty_frame(SENTIMENT_COLUMNS),
                warnings=(unavailable,),
            ),
            ficha_estrategica={},
            warnings=tuple(dict.fromkeys((*identity_warnings, unavailable))),
        )
    performance = build_official_performance_context(
        df_base_maestra,
        colegio_nombre_canonico=colegio_nombre,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    demographic = build_demographic_context(
        df_base_demografica,
        colegio_nombre_canonico=colegio_nombre,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    text = build_text_context(
        df_comentarios_consolidados,
        df_videos_virales,
        colegio_nombre_canonico=colegio_nombre,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    form = build_form_context(
        df_formulario if df_formulario is not None else pd.DataFrame(),
        colegio_nombre_canonico=colegio_nombre,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    warnings = (
        *identity_warnings,
        *performance.warnings,
        *demographic.warnings,
        *text.warnings,
        *form.warnings,
    )
    return OfficialContext(
        colegio_id=colegio_id,
        colegio_nombre_canonico=colegio_nombre,
        plataforma=plataforma,
        mes_clave=mes_clave,
        performance=performance,
        demografia_top=demographic.sexo_edad_top.copy(),
        ubicacion_top=demographic.ubicacion_top,
        text=OfficialTextContext(
            comentarios=text.comentarios.copy(),
            top_words=text.top_words.copy(),
            sentiment_distribution=text.sentiment_distribution.copy(),
            warnings=text.warnings,
            total_fuente=text.total_fuente,
            total_original=text.total_original,
            deduplicados=text.deduplicados,
            total_final=text.total_final,
        ),
        ficha_estrategica=dict(form.ficha_estrategica),
        warnings=tuple(dict.fromkeys(warnings)),
    )
