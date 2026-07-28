"""Vista aislada del Módulo Satélite y su Contexto Oficial agregado."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from pandas.errors import MergeError

from utils.account_normalization import normalize_platform_name
from utils.analytics_repository import load_analytics_bases
from utils.form_response_importer import normalize_institution_name
from utils.logger import get_logger
from utils.satellite_analytics import (
    aggregate_publication_performance,
    filter_satellite_data,
    get_publication_trace,
)
from utils.satellite_context import (
    FORM_STRATEGIC_LABELS,
    OfficialContext,
    OfficialCoverageComparison,
    build_coverage_comparison,
    build_satellite_official_context,
)
from utils.satellite_repository import load_satellite_data
from utils.sheets_connector import (
    load_form_responses,
    load_consolidated_comments,
    load_viral_videos_comments,
)


logger = get_logger(__name__)

SATELLITE_WARNING = (
    "Los filtros globales de ChampiLeaks no aplican a este módulo. "
    "Utiliza los controles locales. Los datos aquí mostrados son una muestra "
    "a detalle y no reemplazan los totales oficiales."
)
ALL_OPTION = "__satellite_all__"
NO_SATELLITE_SCHOOL = "__satellite_official_only__"


@dataclass(frozen=True)
class _SchoolOption:
    """Opción local que puede venir del satélite, de Sheets o de ambos."""

    option_id: str
    label: str
    colegio_id: str | None
    official_colegio: str | None


def _reset_stale_widget(key: str, options: Sequence[str]) -> None:
    """Evita conservar selecciones que ya no existen en las fuentes."""
    current_value = st.session_state.get(key)
    if current_value is not None and current_value not in options:
        del st.session_state[key]


def _non_empty_strings(series: pd.Series | None) -> list[str]:
    if series is None:
        return []
    values = series.dropna().astype("string").str.strip()
    return [str(value) for value in values.loc[values.ne("")].tolist()]


def _canonical_school(value: object) -> str | None:
    if pd.isna(value):
        return None
    canonical = normalize_institution_name(str(value)).strip()
    return canonical or None


def _school_options(
    df_cuentas: pd.DataFrame,
    df_base_maestra: pd.DataFrame,
    df_base_demografica: pd.DataFrame,
    df_comments: pd.DataFrame,
    df_formulario: pd.DataFrame,
) -> tuple[list[str], dict[str, _SchoolOption]]:
    """Une catálogos sin hacer joins entre filas oficiales y satélite."""
    choices: dict[str, _SchoolOption] = {}
    accounts = df_cuentas.copy()
    if {"colegio_id", "colegio_nombre"}.issubset(accounts.columns):
        for row in accounts.loc[:, ["colegio_id", "colegio_nombre"]].drop_duplicates().itertuples(index=False):
            colegio_id = None if pd.isna(row.colegio_id) else str(row.colegio_id).strip()
            canonical = _canonical_school(row.colegio_nombre)
            if not colegio_id:
                continue
            option_id = f"sat:{colegio_id}"
            display_name = canonical or str(row.colegio_nombre).strip() or colegio_id
            choices[option_id] = _SchoolOption(
                option_id=option_id,
                label=f"{display_name} · {colegio_id}",
                colegio_id=colegio_id,
                official_colegio=canonical,
            )

    official_names: list[str] = []
    for frame, column in (
        (df_base_maestra, "colegio"),
        (df_base_demografica, "colegio"),
        (df_comments, "institucion_nombre"),
        (df_comments, "institucion"),
        (df_formulario, "entidad"),
        (df_formulario, "institucion"),
    ):
        if column in frame.columns:
            official_names.extend(_non_empty_strings(frame[column]))

    satellite_names = {
        option.official_colegio for option in choices.values() if option.official_colegio
    }
    for raw_name in official_names:
        canonical = _canonical_school(raw_name)
        if not canonical or canonical in satellite_names:
            continue
        option_id = f"off:{canonical.casefold()}"
        choices.setdefault(
            option_id,
            _SchoolOption(
                option_id=option_id,
                label=f"{canonical} · Solo contexto oficial",
                colegio_id=None,
                official_colegio=canonical,
            ),
        )

    ordered = sorted(choices.values(), key=lambda choice: choice.label.casefold())
    return [ALL_OPTION, *(choice.option_id for choice in ordered)], {
        choice.option_id: choice for choice in ordered
    }


def _official_platform_values(
    df_base_maestra: pd.DataFrame,
    df_base_demografica: pd.DataFrame,
    df_comments: pd.DataFrame,
    df_formulario: pd.DataFrame,
) -> list[str]:
    values: list[str] = []
    for frame, column in (
        (df_base_maestra, "plataforma"),
        (df_base_demografica, "plataforma"),
        (df_comments, "fuente"),
        (df_formulario, "plataforma"),
    ):
        if column in frame.columns:
            values.extend(_non_empty_strings(frame[column]))
    return values


def _month_values(frame: pd.DataFrame, column: str, *, already_month: bool = False) -> list[str]:
    if column not in frame.columns:
        return []
    if already_month:
        return _non_empty_strings(frame[column])
    parsed = pd.to_datetime(frame[column], errors="coerce")
    return _non_empty_strings(parsed.dt.strftime("%Y-%m"))


def _render_local_filters(
    df_cuentas: pd.DataFrame,
    df_publicaciones: pd.DataFrame,
    df_base_maestra: pd.DataFrame,
    df_base_demografica: pd.DataFrame,
    df_comments: pd.DataFrame,
    df_formulario: pd.DataFrame,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Construye filtros locales con la unión de catálogos oficiales/satélite."""
    school_options, school_lookup = _school_options(
        df_cuentas,
        df_base_maestra,
        df_base_demografica,
        df_comments,
        df_formulario,
    )
    raw_platforms = _non_empty_strings(df_cuentas.get("plataforma"))
    raw_platforms.extend(
        _official_platform_values(
            df_base_maestra,
            df_base_demografica,
            df_comments,
            df_formulario,
        )
    )
    platforms = sorted({normalize_platform_name(value) for value in raw_platforms if value}, key=str.casefold)
    platform_options = [ALL_OPTION, *platforms]

    months = set(_month_values(df_publicaciones, "mes_clave", already_month=True))
    months.update(_month_values(df_base_maestra, "fecha"))
    months.update(_month_values(df_base_demografica, "fecha_reporte"))
    months.update(_month_values(df_comments, "fecha_carga"))
    months.update(_month_values(df_formulario, "fecha"))
    month_options = [ALL_OPTION, *sorted(months, reverse=True)]

    _reset_stale_widget("sat_filtro_colegio", school_options)
    _reset_stale_widget("sat_filtro_plataforma", platform_options)
    _reset_stale_widget("sat_filtro_mes", month_options)

    filter_columns = st.columns(3)
    with filter_columns[0]:
        selected_school = st.selectbox(
            "Colegio",
            options=school_options,
            format_func=lambda value: "Todos los colegios" if value == ALL_OPTION else school_lookup[value].label,
            key="sat_filtro_colegio",
        )
    with filter_columns[1]:
        selected_platform = st.selectbox(
            "Plataforma",
            options=platform_options,
            format_func=lambda value: "Todas las plataformas" if value == ALL_OPTION else value,
            key="sat_filtro_plataforma",
        )
    with filter_columns[2]:
        selected_month = st.selectbox(
            "Mes",
            options=month_options,
            format_func=lambda value: "Todos los meses" if value == ALL_OPTION else value,
            key="sat_filtro_mes",
        )

    selected = school_lookup.get(selected_school)
    return (
        None if selected is None else selected.colegio_id,
        None if selected is None else selected.official_colegio,
        None if selected_platform == ALL_OPTION else selected_platform,
        None if selected_month == ALL_OPTION else selected_month,
    )


def _display_number(value: object) -> str:
    if pd.isna(value):
        return "N/D"
    return f"{float(value):,.0f}"


def _display_percentage(value: object) -> str:
    if pd.isna(value):
        return "N/D"
    return f"{float(value):.2f}%"


def _render_strategic_form(context: OfficialContext) -> None:
    """Presenta métricas del formulario sin mezclar sus filas con el satélite."""
    with st.expander("Ficha Estratégica Oficial", expanded=False):
        ficha = context.ficha_estrategica
        if not ficha:
            st.info("No hay ficha estratégica oficial para el corte seleccionado.")
            return
        groups = (
            ("Engagement y frecuencia", ("engagement_rate", "publicaciones_por_semana", "media_visualizaciones", "media_interaccion")),
            ("Rendimiento de contenido", ("engagement_contenido_videos", "engagement_contenido_imagenes", "engagement_contenido_links", "tema_mas_visto", "engagement_tema_mas_visto", "tipo_contenido_mas_viral")),
            ("Viralidad y percepción", ("publicacion_mas_interacciones", "se_considera_viral_280", "calificacion_redes", "calificacion_contenido", "novedoso_video_viral")),
        )
        columns = st.columns(len(groups))
        for column, (title, fields) in zip(columns, groups):
            with column:
                st.markdown(f"**{title}**")
                for field in fields:
                    if field in ficha:
                        st.markdown(f"{FORM_STRATEGIC_LABELS[field]}: {ficha[field]}")


def _render_official_context(context: OfficialContext) -> None:
    """Muestra primero el panel agregado; nunca contiene filas satélite."""
    st.subheader("Contexto Oficial")
    st.caption("Totales y señales agregadas de las hojas históricas de ChampiLeaks.")
    performance = context.performance
    metrics = st.columns(4)
    metrics[0].metric("Interacciones oficiales", _display_number(performance.interacciones))
    metrics[1].metric("Visualizaciones oficiales", _display_number(performance.visualizaciones))

    audience = context.audience_top
    if audience.empty:
        metrics[2].metric("Audiencia Top (Sexo/Edad)", "N/D")
    else:
        segment = audience.iloc[0]
        metrics[2].metric(
            "Audiencia Top (Sexo/Edad)",
            f"{segment['sexo']} · {segment['edad']}",
            help=f"Valor agregado: {_display_number(segment['valor'])}",
        )
    metrics[3].metric("Ubicación Top", "N/D" if pd.isna(context.ubicacion_top) else str(context.ubicacion_top))

    _render_strategic_form(context)

    text_columns = st.columns(2)
    top_words = context.text.top_words
    if top_words.empty:
        text_columns[0].caption("Palabras clave oficiales: N/D")
    else:
        text_columns[0].caption(
            "Palabras clave oficiales: "
            + ", ".join(
                f"{row.palabra} ({int(row.total)})" for row in top_words.itertuples(index=False)
            )
        )
    sentiment = context.text.sentiment_distribution
    if sentiment.empty:
        text_columns[1].caption("Sentimiento oficial: N/D")
    else:
        text_columns[1].dataframe(
            sentiment.rename(columns={"sentimiento": "Sentimiento", "total": "Comentarios"}),
            hide_index=True,
            width="stretch",
            key="sat_tabla_sentimiento_oficial",
        )

    for warning in context.warnings:
        st.warning(warning, icon="⚠️")


def _sample_total(publications: pd.DataFrame, column: str) -> object:
    if publications.empty or column not in publications.columns:
        return pd.NA
    values = pd.to_numeric(publications[column], errors="coerce").dropna()
    return pd.NA if values.empty else float(values.sum())


def _render_coverage_metric(
    title: str,
    comparison: OfficialCoverageComparison,
) -> None:
    st.metric(
        title,
        _display_percentage(comparison.coverage_pct),
        delta=comparison.message,
        delta_color="inverse" if comparison.is_critical else "off",
    )


def _render_comparison_cards(
    context: OfficialContext,
    filtered_publications: pd.DataFrame,
) -> None:
    st.subheader("Cobertura de la muestra granular")
    interactions = build_coverage_comparison(
        context.performance.interacciones,
        _sample_total(filtered_publications, "interacciones"),
        metric_label="Interacciones",
    )
    views = build_coverage_comparison(
        context.performance.visualizaciones,
        _sample_total(filtered_publications, "visualizaciones"),
        metric_label="Visualizaciones",
    )
    cards = st.columns(2)
    with cards[0]:
        _render_coverage_metric("Cobertura de interacciones", interactions)
    with cards[1]:
        _render_coverage_metric("Cobertura de visualizaciones", views)
    for comparison in (interactions, views):
        if comparison.is_critical:
            st.error(comparison.message)


def _render_performance_table(performance: pd.DataFrame) -> None:
    st.subheader("Rendimiento por formato")
    if performance.empty:
        st.info("No hay publicaciones para la combinación de filtros seleccionada.")
        return

    display = performance.rename(
        columns={
            "plataforma": "Plataforma",
            "tipo_contenido": "Formato",
            "publicaciones_totales": "Publicaciones",
            "visualizaciones_totales": "Visualizaciones",
            "alcance_total": "Alcance",
            "interacciones_totales": "Interacciones",
            "interacciones_promedio": "Interacciones promedio",
            "interacciones_mediana": "Interacciones mediana",
            "cobertura_visualizaciones_pct": "Cobertura de vistas",
            "cobertura_alcance_pct": "Cobertura de alcance",
            "tasa_interacciones_1k_vistas": "Interacciones / 1k vistas",
            "tasa_interacciones_1k_alcance": "Interacciones / 1k alcance",
        }
    ).copy()
    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        placeholder="N/D",
        key="sat_tabla_rendimiento",
        column_config={
            "Cobertura de vistas": st.column_config.NumberColumn(format="%.2f%%"),
            "Cobertura de alcance": st.column_config.NumberColumn(format="%.2f%%"),
            "Interacciones / 1k vistas": st.column_config.NumberColumn(format="%.2f"),
            "Interacciones / 1k alcance": st.column_config.NumberColumn(format="%.2f"),
            "Interacciones promedio": st.column_config.NumberColumn(format="%.2f"),
            "Interacciones mediana": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    st.caption("N/D indica que el denominador es cero o que la métrica no fue informada.")


def _publication_label(row: pd.Series) -> str:
    date_value = pd.to_datetime(row.get("fecha_publicacion"), errors="coerce")
    date_label = date_value.strftime("%d/%m/%Y") if pd.notna(date_value) else "Sin fecha"
    raw_title = row.get("titulo_o_extracto")
    title = "" if pd.isna(raw_title) else str(raw_title).strip()
    if not title:
        title = "Sin título o extracto"
    if len(title) > 90:
        title = f"{title[:87]}..."
    platform = row.get("plataforma")
    platform_label = "Sin plataforma" if pd.isna(platform) else str(platform)
    return f"{date_label} · {platform_label} · {title}"


def _render_publication_detail(publication: pd.Series) -> None:
    title = publication.get("titulo_o_extracto")
    st.markdown(f"**{title if pd.notna(title) and str(title).strip() else 'Sin título'}**")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Formato", str(publication.get("tipo_contenido", "N/D")))
    for metric_column, name, source_column in (
        (metric_columns[1], "Visualizaciones", "visualizaciones"),
        (metric_columns[2], "Alcance", "alcance"),
        (metric_columns[3], "Interacciones", "interacciones"),
    ):
        value = publication.get(source_column)
        metric_column.metric(name, _display_number(value))
    url = publication.get("url_publicacion")
    if pd.notna(url) and str(url).strip():
        st.markdown(f"[Abrir publicación original]({str(url).strip()})")


def _render_comment_table(trace: pd.DataFrame) -> None:
    comments = trace.loc[
        trace["id_comentario"].notna(),
        ["texto", "sentimiento", "tema_alerta", "metodo_clasificacion"],
    ].copy()
    if comments.empty:
        st.info("No hay conversación registrada para este post.")
        return
    comments["tema_alerta"] = comments["tema_alerta"].astype("string").fillna("Sin alerta")
    comments = comments.rename(
        columns={
            "texto": "Comentario",
            "sentimiento": "Sentimiento",
            "tema_alerta": "Tema de alerta",
            "metodo_clasificacion": "Método de clasificación",
        }
    ).copy()
    st.dataframe(
        comments,
        width="stretch",
        hide_index=True,
        placeholder="N/D",
        key="sat_tabla_comentarios",
    )


def _render_trace_explorer(
    filtered_publications: pd.DataFrame,
    filtered_comments: pd.DataFrame,
) -> None:
    st.subheader("Explorador de trazabilidad")
    if filtered_publications.empty:
        st.info("No hay publicaciones disponibles para explorar con estos filtros.")
        return
    publications = (
        filtered_publications.sort_values(
            ["fecha_publicacion", "id_publicacion"],
            ascending=[False, True],
            kind="stable",
        )
        .reset_index(drop=True)
        .copy()
    )
    publication_ids = publications["id_publicacion"].astype(str).tolist()
    labels = {str(row["id_publicacion"]): _publication_label(row) for _, row in publications.iterrows()}
    _reset_stale_widget("sat_publicacion_selector", publication_ids)
    target_pub_id = st.selectbox(
        "Publicación",
        options=publication_ids,
        format_func=lambda value: labels.get(value, value),
        key="sat_publicacion_selector",
    )
    try:
        trace = get_publication_trace(filtered_publications, filtered_comments, target_pub_id)
    except MergeError:
        logger.exception("Cardinalidad inválida al explorar id_publicacion=%s", target_pub_id)
        st.error("La publicación seleccionada está duplicada. Revisa la llave primaria en la fuente satélite.")
        return
    selected_publication = publications.loc[publications["id_publicacion"].eq(target_pub_id)].iloc[0]
    _render_publication_detail(selected_publication)
    st.markdown("#### Comentarios clasificados")
    _render_comment_table(trace)


def render() -> None:
    """Renderiza contexto oficial primero y análisis granular sólo si existe."""
    st.warning(SATELLITE_WARNING, icon="⚠️")
    st.title("Módulo Satélite")
    st.caption("Análisis granular acompañado por el contexto histórico oficial.")

    data = load_satellite_data()
    base_maestra, base_demografica = load_analytics_bases()
    formulario = load_form_responses()
    consolidated = load_consolidated_comments()
    viral = load_viral_videos_comments()
    all_official_comments = pd.concat([consolidated.copy(), viral.copy()], ignore_index=True, sort=False).copy()

    colegio_id, official_colegio, plataforma, mes_clave = _render_local_filters(
        data.cuentas,
        data.publicaciones,
        base_maestra,
        base_demografica,
        all_official_comments,
        formulario,
    )
    context = build_satellite_official_context(
        data.cuentas,
        base_maestra,
        base_demografica,
        consolidated,
        viral,
        formulario,
        colegio_id=colegio_id,
        official_colegio=official_colegio,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    _render_official_context(context)

    if data.publicaciones.empty or data.cuentas.empty:
        st.info("Sin muestra granular: no hay CSVs satélite válidos para el análisis transaccional.")
        return

    satellite_school_filter = colegio_id if colegio_id is not None else (
        NO_SATELLITE_SCHOOL if official_colegio is not None else None
    )
    filtered_publications, filtered_comments = filter_satellite_data(
        data.cuentas,
        data.publicaciones,
        data.comentarios,
        colegio_id=satellite_school_filter,
        plataforma=plataforma,
        mes_clave=mes_clave,
    )
    _render_comparison_cards(context, filtered_publications)
    if filtered_publications.empty:
        st.info("Sin muestra granular para la combinación de filtros seleccionada.")
    performance = aggregate_publication_performance(filtered_publications)
    _render_performance_table(performance)
    _render_trace_explorer(filtered_publications, filtered_comments)
