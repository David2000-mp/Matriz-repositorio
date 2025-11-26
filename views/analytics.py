"""
Vista de Análisis Individual para CHAMPILYTICS.
Análisis detallado por institución.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import load_data
from components import COLOR_MAP

def render():
    """
    Renderiza el análisis detallado por institución con métricas individuales.
    """
    st.title("ANÁLISIS INDIVIDUAL")
    st.caption("Vista Detallada por Institución")
    
    cuentas, metricas = load_data()
    
    if cuentas.empty or metricas.empty:
        st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
        return
        
    df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
    
    # Verificar que el merge fue exitoso
    if 'entidad' not in df.columns or df['entidad'].isna().all():
        st.error("❌ Error en la estructura de datos. Los datos están corruptos.")
        st.info("💡 Ve a **Configuración** → **Simulador de Datos** para resetear y generar datos nuevos.")
        if st.button("🔧 Ir a Configuración", use_container_width=True, type="primary"):
            st.session_state.page = "config"
            st.rerun()
        return
    
    # Selector de Colegio
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1: 
        lista_colegios = sorted(df['entidad'].dropna().astype(str).unique())
        entidad = st.selectbox("Seleccionar Institución", lista_colegios)
    with c2:
        st.info("Visualizando histórico completo")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrar datos del colegio
    df_e = df[df['entidad'] == entidad].sort_values("fecha")
    
    if df_e.empty:
        st.warning("Este colegio no tiene datos registrados aún.")
        return

    # KPIs del último mes disponible
    last_date = df_e['fecha'].max()
    
    if pd.isna(last_date):
        st.error("No hay fechas válidas para esta institución.")
        return
    
    df_last = df_e[df_e['fecha'] == last_date]
    
    st.markdown(f"### Resultados al cierre de {last_date.strftime('%Y-%m')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Seguidores Totales", f"{df_last['seguidores'].sum():,.0f}")
    col2.metric("Interacciones (Mes)", f"{df_last['interacciones'].sum():,.0f}")
    
    er_e = (df_last['interacciones'].sum() / df_last['seguidores'].sum() * 100) if df_last['seguidores'].sum() > 0 else 0
    col3.metric("Engagement Promedio", f"{er_e:.2f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficas Individuales
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    tab_a, tab_b = st.tabs(["Evolución de Seguidores", "Evolución de Engagement"])
    
    with tab_a:
        fig = px.line(df_e, x="fecha", y="seguidores", color="plataforma", 
                      color_discrete_map=COLOR_MAP, markers=True, title="Crecimiento de Audiencia")
        
        fig.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            template='plotly_white',
            margin=dict(t=40, b=0, l=0, r=0),
            yaxis=dict(
                showgrid=True,
                gridcolor='#E5E7EB',
                tickfont=dict(color='#000000', size=12)
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color='#000000', size=12)
            ),
            legend=dict(
                orientation="h",
                y=1.15,
                x=0,
                font=dict(color='#000000', size=12)
            ),
            font=dict(family="Montserrat", size=12, color='#000000'),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab_b:
        fig = px.line(df_e, x="fecha", y="engagement_rate", color="plataforma",
                      color_discrete_map=COLOR_MAP, markers=True, title="Evolución de Engagement Rate (%)")
        
        fig.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            template='plotly_white',
            margin=dict(t=40, b=0, l=0, r=0),
            yaxis=dict(
                showgrid=True,
                gridcolor='#E5E7EB',
                tickfont=dict(color='#000000', size=12)
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color='#000000', size=12)
            ),
            legend=dict(
                orientation="h",
                y=1.15,
                x=0,
                font=dict(color='#000000', size=12)
            ),
            font=dict(family="Montserrat", size=12, color='#000000'),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabla de datos detallados
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("#### Datos Detallados")
    
    # Preparar tabla para mostrar
    df_display = df_e[['fecha', 'plataforma', 'seguidores', 'alcance', 'interacciones', 'engagement_rate']].copy()
    df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d')
    df_display = df_display.sort_values('fecha', ascending=False)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
