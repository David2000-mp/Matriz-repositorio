from collections.abc import Iterable

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from components import COLOR_MAP, PLOTLY_CONFIG


def _coerce_numeric_series(series: pd.Series, *, strip_percent: bool = False) -> pd.Series:
    """Convierte series a numérico aceptando `%`, coma decimal y texto suelto."""
    if series is None:
        return pd.Series(dtype=float)

    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = series.astype(str).str.strip()
    if strip_percent:
        cleaned = cleaned.str.replace("%", "", regex=False)

    cleaned = cleaned.str.replace(",", ".", regex=False)
    cleaned = cleaned.replace({"nan": None, "None": None, "": None})
    cleaned = cleaned.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def sanitize_chart_dataframe(
    df: pd.DataFrame,
    *,
    date_cols: Iterable[str] | None = None,
    numeric_cols: Iterable[str] | None = None,
    percent_cols: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Normaliza columnas de fecha y métricas antes de renderizar gráficas."""
    if df is None:
        return pd.DataFrame()

    safe_df = df.copy()

    for col in date_cols or []:
        if col in safe_df.columns:
            safe_df[col] = pd.to_datetime(safe_df[col], errors="coerce")

    for col in percent_cols or []:
        if col in safe_df.columns:
            safe_df[col] = _coerce_numeric_series(safe_df[col], strip_percent=True).fillna(0)

    for col in numeric_cols or []:
        if col in safe_df.columns and col not in set(percent_cols or []):
            safe_df[col] = _coerce_numeric_series(safe_df[col]).fillna(0)

    return safe_df


def plot_engagement_evolution(df, platform_filter):
    """
    Crea una gráfica de evolución de engagement por red social.

    Args:
        df: DataFrame con columnas 'fecha', 'plataforma', 'engagement_rate'
        platform_filter: Filtro de plataforma seleccionado

    Returns:
        None: Muestra la gráfica en Streamlit
    """
    if df is None or df.empty or 'engagement_rate' not in df.columns:
        st.warning("No hay datos de engagement disponibles para la gráfica.")
        return

    df = sanitize_chart_dataframe(
        df,
        date_cols=["fecha"],
        numeric_cols=["seguidores", "interacciones", "alcance", "likes_promedio"],
        percent_cols=["engagement_rate"],
    )

    # Filtrar por plataforma si se selecciona
    if platform_filter != "Todas" and "plataforma" in df.columns:
        df = df[df["plataforma"].fillna("").str.casefold() == str(platform_filter).casefold()]

    # Agrupar por fecha y plataforma, promediar engagement
    df_agg = df.groupby(['fecha', 'plataforma'], dropna=False)['engagement_rate'].mean().reset_index()

    # Asegurar que fecha sea datetime
    df_agg["fecha"] = pd.to_datetime(df_agg["fecha"], errors="coerce")
    df_agg = df_agg.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])

    if df_agg.empty:
        st.warning("No hay datos suficientes para mostrar la evolución de engagement.")
        return

    df_agg["engagement_ma3"] = df_agg.groupby("plataforma")["engagement_rate"].transform(
        lambda values: values.rolling(window=3, min_periods=1).mean()
    )

    title = "Evolución de Engagement por Red Social"
    if platform_filter != "Todas":
        title = f"Evolución de Engagement · {platform_filter}"

    # Crear gráfica
    fig = px.line(
        df_agg,
        x="fecha",
        y="engagement_rate",
        color="plataforma",
        color_discrete_map=COLOR_MAP,
        title=title,
        markers=True,
    )

    for plataforma in df_agg["plataforma"].dropna().unique():
        trend_df = df_agg[df_agg["plataforma"] == plataforma]
        if len(trend_df) > 1:
            fig.add_trace(
                go.Scatter(
                    x=trend_df["fecha"],
                    y=trend_df["engagement_ma3"],
                    mode="lines",
                    name=f"{plataforma} · Tendencia",
                    line=dict(width=2, dash="dot"),
                    hovertemplate="<b>%{fullData.name}</b><br>%{x|%Y-%m}<br>%{y:.2f}%<extra></extra>",
                )
            )

    fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x|%Y-%m}<br>%{y:.2f}%<extra></extra>")
    fig.update_xaxes(type="date")
    fig.update_yaxes(title="Engagement (%)", ticksuffix="%")

    fig.update_layout(
        autosize=True,
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        font={"color": "#000000"},
        title_font={"color": "#000000"},
        legend={"font": {"color": "#000000"}, "title": {"text": "Plataforma"}},
        hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
        xaxis={
            "color": "#000000",
            "gridcolor": "#E0E0E0",
            "title": {"font": {"color": "#000000"}},
            "tickfont": {"color": "#000000"},
        },
        yaxis={
            "color": "#000000",
            "gridcolor": "#E0E0E0",
            "title": {"font": {"color": "#000000"}},
            "tickfont": {"color": "#000000"},
        },
    )

    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG)