import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from components import COLOR_MAP, PLOTLY_CONFIG

def plot_engagement_evolution(df, platform_filter):
    """
    Crea una gráfica de evolución de engagement por red social.
    
    Args:
        df: DataFrame con columnas 'fecha', 'plataforma', 'engagement_rate'
        platform_filter: Filtro de plataforma seleccionado
    
    Returns:
        None: Muestra la gráfica en Streamlit
    """
    if df.empty or 'engagement_rate' not in df.columns:
        st.warning("No hay datos de engagement disponibles para la gráfica.")
        return
    
    # Filtrar por plataforma si se selecciona
    if platform_filter != "Todas":
        df = df[df['plataforma'] == platform_filter]
    
    # Agrupar por fecha y plataforma, promediar engagement
    df_agg = df.groupby(['fecha', 'plataforma'])['engagement_rate'].mean().reset_index()
    
    # Asegurar que fecha sea datetime
    df_agg["fecha"] = pd.to_datetime(df_agg["fecha"], errors="coerce")
    df_agg = df_agg.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])
    
    if df_agg.empty:
        st.warning("No hay datos suficientes para mostrar la evolución de engagement.")
        return
    
    # Crear gráfica
    fig = px.line(
        df_agg,
        x="fecha",
        y="engagement_rate",
        color="plataforma",
        color_discrete_map=COLOR_MAP,
        title="Evolución de Engagement por Red Social",
        markers=True,
    )
    fig.update_xaxes(type="date")
    fig.update_yaxes(title="Engagement (%)")
    
    fig.update_layout(
        autosize=True,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"color": "#000000"},
        title_font={"color": "#000000"},
        legend={"font": {"color": "#000000"}},
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