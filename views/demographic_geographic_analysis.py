"""Vista de Analisis Demografico y Geografico para Chammpileaks."""

from __future__ import annotations

from io import BytesIO
from typing import Dict, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import PLOTLY_CONFIG, render_empty_state
from utils.chart_theme import aplicar_tema_champileaks
from utils.demographics_geo import (
    MEXICO_CENTER,
    AGE_ORDER,
    apply_demographic_filters,
    build_city_report,
    build_demography_base,
    build_network_comparison,
    normalize_text,
)


# Salvaguarda en vista para ciudades reportadas frecuentemente sin coordenadas.
CITY_COORDS_RECOVERY = {
    # Estado de Mexico y CDMX
    "Toluca de Lerdo": (19.2925, -99.6569),
    "Nezahualcóyotl": (19.4081, -99.0186),
    "Ecatepec de Morelos": (19.6097, -99.0600),
    "Metepec": (19.2511, -99.6047),
    "Chimalhuacán": (19.4375, -98.9542),
    "Naucalpan de Juárez": (19.4753, -99.2378),
    "Tlalnepantla de Baz": (19.5400, -99.1900),
    "Cuautitlán Izcalli": (19.6439, -99.2161),
    "Atizapán de Zaragoza": (19.5558, -99.2492),
    "San Miguel Zinacantepec": (19.2908, -99.7389),
    "San Andrés Ocotlán": (19.1869, -99.5801),
    "San Mateo Atenco": (19.2673, -99.5327),

    # Resto del pais
    "Puebla de Zaragoza": (19.0453, -98.1975),
    "Zapopan": (20.7203, -103.3919),
    "Uruapan": (19.3967, -102.0392),
    "Ciudad Juárez": (31.7450, -106.4850),
    "Oaxaca de Juárez": (17.0678, -96.7200),
    "Santiago de Querétaro": (20.5888, -100.3899),
    "León de los Aldama": (21.1220, -101.6805),
    "San Luis Potosí": (22.1565, -100.9855),
    "Victoria de Durango": (24.0277, -104.6532),
    "San Francisco de Campeche": (19.8301, -90.5349),
    "San Cristóbal de las Casas": (16.7370, -92.6375),
    "Potoichán": (17.4470, -98.6650),
    "Las Margaritas": (16.3158, -91.9817),
    "Comonfort": (20.7189, -100.7606),
    "Apaseo el Grande": (20.5469, -100.6867),
    "Cortazar": (20.4828, -100.9611),
    "Santa Cruz de Juventino Rosas": (20.6433, -100.9942),
    "Juventino Rosas": (20.6433, -100.9942),
    "Monasterio de Yuste": (40.1142, -5.7389),
}


def load_data() -> Dict[str, pd.DataFrame]:
    """Carga ambas hojas necesarias para la vista."""
    base_maestra = _load_sheet_base_maestra()
    base_demografica = _load_sheet_base_demografica()
    return {
        "base_maestra": base_maestra,
        "base_demografica": base_demografica,
    }


@st.cache_data(ttl=300)
def _load_sheet_base_maestra() -> pd.DataFrame:
    """Carga Base_Maestra_Colegios directo desde Google Sheets."""
    from utils.sheets_connector import get_sheets_connection

    expected = ["fecha", "colegio", "plataforma", "metrica", "valor"]
    aliases = {
        "métrica": "metrica",
    }

    ss = get_sheets_connection()
    if not ss:
        return pd.DataFrame(columns=expected)

    try:
        ws = ss.worksheet("Base_Maestra_Colegios")
        records = ws.get_all_records()
    except Exception:
        return pd.DataFrame(columns=expected)

    if not records:
        return pd.DataFrame(columns=expected)

    df = pd.DataFrame(records).fillna("")
    df.columns = [aliases.get(str(c).strip().lower(), str(c).strip().lower()) for c in df.columns]

    for col in expected:
        if col not in df.columns:
            df[col] = ""

    df = df[expected].copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=300)
def _load_sheet_base_demografica() -> pd.DataFrame:
    """Carga Base_Demografica_Colegios directo desde Google Sheets."""
    from utils.sheets_connector import get_sheets_connection

    expected = [
        "fecha_reporte",
        "colegio",
        "plataforma",
        "criterio",
        "sexo",
        "edad",
        "ubicacion",
        "valor",
    ]
    aliases = {
        "fecha de reporte": "fecha_reporte",
        "ubicación": "ubicacion",
    }

    ss = get_sheets_connection()
    if not ss:
        return pd.DataFrame(columns=expected)

    try:
        ws = ss.worksheet("Base_Demografica_Colegios")
        records = ws.get_all_records()
    except Exception:
        return pd.DataFrame(columns=expected)

    if not records:
        return pd.DataFrame(columns=expected)

    df = pd.DataFrame(records).fillna("")
    df.columns = [aliases.get(str(c).strip().lower(), str(c).strip().lower()) for c in df.columns]

    for col in expected:
        if col not in df.columns:
            df[col] = ""

    df = df[expected].copy()
    df["fecha_reporte"] = pd.to_datetime(df["fecha_reporte"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    return df


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
            options=colegios,
            key="demogeo_colegio",
        )

        plataformas_df = df_demografica
        if "colegio" in plataformas_df.columns and colegio != "Sin datos":
            plataformas_df = plataformas_df[plataformas_df["colegio"].astype(str) == str(colegio)]

        plataformas = ["Todas"]
        if not plataformas_df.empty and "plataforma" in plataformas_df.columns:
            plataformas += sorted(
                [str(p).strip() for p in plataformas_df["plataforma"].dropna().unique() if str(p).strip()]
            )

        plataforma = st.selectbox(
            "Plataforma",
            options=plataformas,
            key="demogeo_plataforma",
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


def render_map_block(df_filtered: pd.DataFrame, colegio: str):
    """Bloque 2: mapa de ciudades y reporte tabular."""
    st.subheader("Bloque 2 - Geolocalizacion interactiva (Mexico)")

    mapped, unmapped = build_city_report(df_filtered)
    city_source = df_filtered.copy()
    city_source["criterio_norm"] = city_source["criterio"].apply(normalize_text)
    city_source = city_source[city_source["criterio_norm"] == "ciudad"]
    city_source = city_source[city_source["ubicacion"].astype(str).str.strip() != ""]

    city_totals = pd.DataFrame(columns=["ubicacion", "valor_total", "participacion_pct"])
    if not city_source.empty:
        city_totals = (
            city_source.groupby("ubicacion", as_index=False)["valor"]
            .sum()
            .rename(columns={"valor": "valor_total"})
            .sort_values("valor_total", ascending=False)
        )
        total_val = float(city_totals["valor_total"].sum())
        city_totals["participacion_pct"] = (city_totals["valor_total"] / total_val * 100.0) if total_val else 0.0

    # Recupera ciudades conocidas cuando llegan en unmapped por inconsistencias de parsing.
    if not unmapped.empty:
        recovery_norm = {normalize_text(name): coords for name, coords in CITY_COORDS_RECOVERY.items()}
        unmapped["_recovery_key"] = unmapped["ubicacion"].astype(str).apply(normalize_text)
        recover_mask = unmapped["_recovery_key"].isin(recovery_norm.keys())
        if recover_mask.any():
            recovered = unmapped.loc[recover_mask].copy()
            recovered["lat"] = recovered["_recovery_key"].map(
                lambda key: recovery_norm[key][0]
            )
            recovered["lon"] = recovered["_recovery_key"].map(
                lambda key: recovery_norm[key][1]
            )
            recovered = recovered.drop(columns=["_recovery_key"], errors="ignore")
            mapped = pd.concat([mapped, recovered], ignore_index=True)
            unmapped = unmapped.loc[~recover_mask].copy()
        unmapped = unmapped.drop(columns=["_recovery_key"], errors="ignore")

    # Refuerzo: si una ciudad conocida existe en datos crudos y no quedó en mapped, se inyecta.
    if not city_totals.empty:
        recovery_norm = {normalize_text(name): coords for name, coords in CITY_COORDS_RECOVERY.items()}
        city_totals["_recovery_key"] = city_totals["ubicacion"].astype(str).apply(normalize_text)
        known_rows = city_totals[city_totals["_recovery_key"].isin(recovery_norm.keys())].copy()
        mapped_keys = set(mapped["ubicacion"].astype(str).apply(normalize_text).tolist()) if not mapped.empty else set()
        missing_known = known_rows[~known_rows["_recovery_key"].isin(mapped_keys)].copy()
        if not missing_known.empty:
            missing_known["lat"] = missing_known["_recovery_key"].map(lambda key: recovery_norm[key][0])
            missing_known["lon"] = missing_known["_recovery_key"].map(lambda key: recovery_norm[key][1])
            missing_known = missing_known[["ubicacion", "valor_total", "participacion_pct", "lat", "lon"]]
            mapped = pd.concat([mapped, missing_known], ignore_index=True)

        if not unmapped.empty:
            known_norm_keys = set(recovery_norm.keys())
            unmapped_norm = unmapped["ubicacion"].astype(str).apply(normalize_text)
            unmapped = unmapped.loc[~unmapped_norm.isin(known_norm_keys)].copy()

    if mapped.empty and unmapped.empty:
        st.info("No hay datos de criterio Ciudad para los filtros seleccionados.")
        return

    if not mapped.empty:
        fig = px.scatter_mapbox(
            mapped,
            lat="lat",
            lon="lon",
            size="valor_total",
            color="valor_total",
            hover_name="ubicacion",
            hover_data={
                "valor_total": ":,.0f",
                "participacion_pct": ":.2f",
                "lat": False,
                "lon": False,
            },
            zoom=4.4,
            center=MEXICO_CENTER,
            mapbox_style="carto-positron",
            title="Mapa de ciudades por impacto",
        )
        st.plotly_chart(aplicar_tema_champileaks(fig), width="stretch", config=PLOTLY_CONFIG)
    else:
        st.warning("No hay ciudades con coordenadas disponibles en el diccionario interno.")

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
        render_empty_state(
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

    if df_network_scope.empty:
        render_empty_state(
            "**No hay datos en el rango seleccionado**  \n"
            "Cambia la plataforma o amplía el periodo para consultar la red.",
            tipo="geo",
        )
        return

    if df_selected.empty:
        st.info(
            "El colegio seleccionado no tiene datos en el rango actual. "
            "Puedes usar el mapa en modo General o cambiar de colegio."
        )

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
            mapa_label = "General_Red"
        else:
            if not colegios_mapa:
                st.info("No hay colegios disponibles para vista por colegio con los filtros actuales.")
                df_map = pd.DataFrame()
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
                mapa_label = mapa_scope

        if df_map.empty:
            st.info("No hay datos de ciudad para la seleccion de mapa actual.")
        else:
            render_map_block(df_map, mapa_label)

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
