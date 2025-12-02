"""
Vista de Análisis de Tendencias (MoM) para CHAMPILYTICS.
Incluye análisis individual y resumen mensual con deltas.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data
from utils.analytics import calculate_growth_metrics
from components import COLOR_MAP

def render():
    """Renderiza análisis individual y resumen mensual (MoM)."""
    st.title("ANÁLISIS DE TENDENCIAS")
    st.caption("Vista de evolución mensual y deltas MoM")

    st.markdown("""
    <span style='font-size:1.1em;'>
    <b>¿Cómo funcionan estas gráficas?</b><br>
    Las gráficas muestran la evolución mensual de las métricas clave de la red Marista. <br>
    <ul>
    <li><b>Volumen:</b> Seguidores e interacciones totales por mes. Permite identificar el crecimiento y la actividad general.</li>
    <li><b>Engagement Rate:</b> Mide la calidad de la interacción, mostrando el porcentaje de usuarios que interactúan respecto al total de seguidores.</li>
    </ul>
    Utiliza las pestañas para alternar entre volumen y calidad. Las tendencias ayudan a detectar meses destacados, caídas o picos de actividad.
    </span>
    """, unsafe_allow_html=True)

    cuentas, metricas = load_data()

    if cuentas.empty or metricas.empty:
        st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
        return

    df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
    # Si existe 'entidad_x', renombrar a 'entidad'
    if 'entidad_x' in df.columns:
        df = df.rename(columns={'entidad_x': 'entidad'})
    elif 'entidad_y' in df.columns:
        df = df.rename(columns={'entidad_y': 'entidad'})
    # Si existe 'plataforma_x', renombrar a 'plataforma'
    if 'plataforma_x' in df.columns:
        df = df.rename(columns={'plataforma_x': 'plataforma'})
    elif 'plataforma_y' in df.columns:
        df = df.rename(columns={'plataforma_y': 'plataforma'})

    if 'entidad' not in df.columns or df['entidad'].isna().all():
        st.error("❌ Error en la estructura de datos.")
        return

    # --- SECCIÓN GLOBAL ---
    resumen = calculate_growth_metrics(metricas)

    if resumen.empty:
        st.info("Aún no hay suficientes datos para calcular tendencias mensuales.")
    else:
        # Gráficas primero
        tab_vol, tab_qual = st.tabs(["Volumen (Seguidores/Interacciones)", "Calidad (Engagement)"])
        with tab_vol:
            fig_vol = px.line(
                resumen,
                x="Mes",
                y=["Seguidores", "Interacciones"],
                markers=True,
                title="Tendencia de Volumen"
            )
            fig_vol.update_layout(
                template='plotly_white', 
                margin=dict(t=40, b=10, l=0, r=0),
                hovermode='x unified',
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig_vol, config={'displayModeBar': False})
        with tab_qual:
            fig_qual = px.line(
                resumen,
                x="Mes",
                y=["Engagement"],
                markers=True,
                title="Tendencia de Engagement Rate",
                color_discrete_sequence=["#FF5733"]
            )
            fig_qual.update_layout(
                template='plotly_white', 
                margin=dict(t=40, b=10, l=0, r=0),
                hovermode='x unified',
                legend=dict(orientation="h", y=1.1),
                yaxis=dict(ticksuffix="%")
            )
            st.plotly_chart(fig_qual, config={'displayModeBar': False})
        # Tabla resumen después de las gráficas
        st.markdown("### Resumen Mensual de Datos")
        st.dataframe(resumen, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # --- SECCIÓN INDIVIDUAL ---
    st.markdown("### Análisis Individual")

    lista_colegios = sorted(df['entidad'].dropna().astype(str).unique())
    estado_global = st.session_state.get("institucion_activa", "Todas las Instituciones")
    if estado_global != "Todas las Instituciones" and estado_global in lista_colegios:
        default_index = lista_colegios.index(estado_global)
    else:
        default_index = 0
    entidad = st.selectbox("Seleccionar Institución", lista_colegios, index=default_index)

    # 1. Filtrado y Copia
    df_e = df[df['entidad'] == entidad].copy()
    
    # 2. Parsing y Ordenamiento Seguro
    df_e['fecha'] = pd.to_datetime(df_e['fecha'])
    df_e = df_e.sort_values(by=['fecha', 'plataforma'])
    
    if df_e.empty:
        st.warning("Esta institución no tiene datos registrados aún.")
        return

    last_date = df_e['fecha'].max()
    df_last = df_e[df_e['fecha'] == last_date]
    
    # Calcular benchmarks de red (promedios globales)
    df_network_last = df[df['fecha'] == last_date]
    avg_seg_network = df_network_last.groupby('entidad')['seguidores'].sum().mean()
    avg_int_network = df_network_last.groupby('entidad')['interacciones'].sum().mean()
    
    # Métricas institucionales
    seg_inst = df_last['seguidores'].sum()
    int_inst = df_last['interacciones'].sum()
    seg_sum = df_last['seguidores'].sum()
    er_e = (df_last['interacciones'].sum() / seg_sum * 100) if seg_sum > 0 else 0
    
    # Calcular engagement promedio de red
    er_network = (df_network_last['interacciones'].sum() / df_network_last['seguidores'].sum() * 100) if df_network_last['seguidores'].sum() > 0 else 0
    
    # Deltas vs red
    delta_seg = ((seg_inst - avg_seg_network) / avg_seg_network * 100) if avg_seg_network > 0 else 0
    delta_int = ((int_inst - avg_int_network) / avg_int_network * 100) if avg_int_network > 0 else 0
    delta_er = er_e - er_network
    
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Seguidores Totales", 
        f"{seg_inst:,.0f}",
        delta=f"{delta_seg:+.1f}% vs red",
        delta_color="normal"
    )
    col2.metric(
        "Interacciones (Mes)", 
        f"{int_inst:,.0f}",
        delta=f"{delta_int:+.1f}% vs red",
        delta_color="normal"
    )
    col3.metric(
        "Engagement Promedio", 
        f"{er_e:.2f}%",
        delta=f"{delta_er:+.2f}pp vs red",
        delta_color="normal"
    )

    tab_a, tab_b = st.tabs(["Evolución de Seguidores", "Evolución de Engagement"])
    
    with tab_a:
        # Calcular promedio de red por fecha y plataforma
        df_network_avg = df.groupby(['fecha', 'plataforma']).agg({
            'seguidores': lambda x: x.groupby(df.loc[x.index, 'entidad']).max().mean()
        }).reset_index()
        df_network_avg['tipo'] = 'Promedio Red'
        
        fig_a = px.line(
            df_e,
            x="fecha",
            y="seguidores",
            color="plataforma",
            color_discrete_map=COLOR_MAP,
            markers=True,
            title="Crecimiento de Audiencia (vs Promedio de Red)",
            hover_data={"fecha": True, "plataforma": True, "seguidores": ":,.0f"},
        )
        
        # Añadir líneas de promedio de red
        for plat in df_network_avg['plataforma'].unique():
            df_plat_avg = df_network_avg[df_network_avg['plataforma'] == plat]
            fig_a.add_scatter(
                x=df_plat_avg['fecha'],
                y=df_plat_avg['seguidores'],
                mode='lines',
                line=dict(dash='dash', color=COLOR_MAP.get(plat, '#999999'), width=2),
                name=f'{plat} (Promedio)',
                hovertemplate='<b>Promedio Red</b><br>%{y:,.0f}<extra></extra>',
                showlegend=True
            )
        
        fig_a.update_layout(
            template='plotly_white',
            margin=dict(t=40, b=60, l=0, r=0),
            xaxis=dict(title=None),
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified"
        )
        st.plotly_chart(fig_a, config={'displayModeBar': False})

    with tab_b:
        # Calcular promem dio de engagement de red por fecha y plataforma
        df_network_er = df.groupby(['fecha', 'plataforma'])['engagement_rate'].mean().reset_index()
        df_network_er['tipo'] = 'Promedio Red'
        
        fig_b = px.line(
            df_e,
            x="fecha",
            y="engagement_rate",
            color="plataforma",
            color_discrete_map=COLOR_MAP,
            markers=True,
            title="Evolución de Engagement Rate (vs Promedio de Red)",
            hover_data={"fecha": True, "plataforma": True, "engagement_rate": ":.2f"},
        )
        
        # Añadir líneas de promedio de red
        for plat in df_network_er['plataforma'].unique():
            df_plat_er = df_network_er[df_network_er['plataforma'] == plat]
            fig_b.add_scatter(
                x=df_plat_er['fecha'],
                y=df_plat_er['engagement_rate'],
                mode='lines',
                line=dict(dash='dash', color=COLOR_MAP.get(plat, '#999999'), width=2),
                name=f'{plat} (Promedio)',
                hovertemplate='<b>Promedio Red</b><br>%{y:.2f}%<extra></extra>',
                showlegend=True
            )
        
        fig_b.update_layout(
            template='plotly_white',
            margin=dict(t=40, b=60, l=0, r=0),
            xaxis=dict(title=None),
            yaxis=dict(ticksuffix="%"),
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified"
        )
        st.plotly_chart(fig_b, config={'displayModeBar': False})

    st.markdown("#### Datos Detallados")
    df_display = df_e[['fecha', 'plataforma', 'seguidores', 'alcance', 'interacciones', 'engagement_rate']].copy()
    df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d')
    # Eliminado width='stretch'
    st.dataframe(df_display.sort_values('fecha', ascending=False), use_container_width=True, hide_index=True)