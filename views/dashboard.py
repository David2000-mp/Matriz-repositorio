"""
Vista Dashboard Global para CHAMPILYTICS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import load_data, simular, save_batch, reset_db, generar_reporte_html, COLEGIOS_MARISTAS
from components import COLOR_MAP

def render():
    """
    Renderiza el dashboard global con KPIs y visualizaciones agregadas.
    """
    st.title("DASHBOARD GLOBAL")
    st.caption("Red Marista • Análisis Consolidado")
    
    cuentas, metricas = load_data()
    logging.info(f"Dashboard - Cuentas: {len(cuentas)}, Métricas: {len(metricas)}")
    
    if not cuentas.empty and 'entidad' in cuentas.columns:
        entidades = cuentas['entidad'].dropna().unique().tolist()
        logging.info(f"Dashboard - Entidades en cuentas ({len(entidades)}): {sorted(entidades) if entidades else 'Ninguna'}")
    
    if metricas.empty:
        st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
        return

    # Merge con validación
    if cuentas.empty:
        st.error("❌ No hay información de cuentas.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resetear Base de Datos", use_container_width=True):
                with st.spinner('Reseteando...'):
                    reset_db()
                st.success("✅ Base de datos reseteada")
                st.rerun()
        with col2:
            if st.button("🎲 Generar Datos Demo (6 meses)", use_container_width=True):
                with st.spinner('Generando datos...'):
                    total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
                    save_batch(simular(n=total_cuentas * 6, colegios_maristas=COLEGIOS_MARISTAS))
                st.success("✅ Datos generados")
                st.rerun()
        return
    
    df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
    logging.info(f"Dashboard - Después del merge: {len(df)} registros, Entidades: {df['entidad'].nunique() if 'entidad' in df.columns else 'N/A'}")
    
    # Verificar que el merge fue exitoso
    if 'entidad' not in df.columns or df['entidad'].isna().all():
        st.error("❌ Error en la estructura de datos. Los datos están corruptos.")
        st.info("💡 Solución: Resetea la base de datos y genera nuevos datos.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Resetear y Limpiar Todo", use_container_width=True, type="primary"):
                with st.spinner('Reseteando...'):
                    reset_db()
                st.success("✅ Base de datos limpiada")
                st.rerun()
        with col2:
            if st.button("🎲 Generar Datos Nuevos", use_container_width=True):
                with st.spinner('Generando...'):
                    reset_db()
                    total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
                    save_batch(simular(n=total_cuentas * 6, colegios_maristas=COLEGIOS_MARISTAS))
                st.success("✅ Datos regenerados")
                st.rerun()
        return
    
    # --- FILTROS ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: 
        st.markdown("#### Periodo de Análisis")
    with c2: 
        fechas = df['fecha'].dropna().dt.strftime('%Y-%m').unique()
        mes = st.selectbox("Mes", sorted(fechas, reverse=True), label_visibility="collapsed")
    with c3:
        df_m = df[df['fecha'].dt.strftime('%Y-%m') == mes]
        st.download_button("Descargar Reporte", generar_reporte_html(df_m, mes), f"Reporte_{mes}.html", "text/html")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- KPIs con Crecimiento MoM ---
    tot_seg = df_m['seguidores'].sum()
    tot_int = df_m['interacciones'].sum()
    er_global = (tot_int / tot_seg * 100) if tot_seg > 0 else 0
    
    # Calcular mes anterior para MoM
    fechas_disponibles = sorted(df['fecha'].dropna().dt.strftime('%Y-%m').unique(), reverse=True)
    mes_anterior = fechas_disponibles[1] if len(fechas_disponibles) > 1 else None
    
    if mes_anterior:
        df_prev = df[df['fecha'].dt.strftime('%Y-%m') == mes_anterior]
        seg_prev = df_prev['seguidores'].sum()
        int_prev = df_prev['interacciones'].sum()
        delta_seg = ((tot_seg - seg_prev) / seg_prev * 100) if seg_prev > 0 else 0
        delta_int = ((tot_int - int_prev) / int_prev * 100) if int_prev > 0 else 0
    else:
        delta_seg, delta_int = 0, 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seguidores Totales", f"{tot_seg:,.0f}", delta=f"{delta_seg:+.1f}% vs mes anterior" if mes_anterior else "Red Marista")
    c2.metric("Interacciones Totales", f"{tot_int:,.0f}", delta=f"{delta_int:+.1f}%" if mes_anterior else None)
    c3.metric("Engagement Rate", f"{er_global:.2f}%")
    c4.metric("Colegios Reportando", df_m['entidad'].nunique())
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    t1, t2 = st.tabs(["Visión Global", "Ranking Institucional"])
    
    with t1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c_left, c_right = st.columns([1, 2])
        with c_left:
            st.markdown("#### Distribución por Plataforma")
            fig = px.pie(df_m, values='seguidores', names='plataforma', 
                         color='plataforma', color_discrete_map=COLOR_MAP, hole=0.7)
            
            fig.update_traces(
                textposition='outside',
                textinfo='percent+label',
                hoverinfo='label+percent+value',
                marker=dict(line=dict(color='#FFFFFF', width=2)),
                textfont=dict(color='#000000', size=14, family='Montserrat')
            )
            
            fig.update_layout(
                showlegend=True,
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(family="Montserrat", size=13, color='#000000'),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(color='#000000', size=12)
                ),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Montserrat",
                    font_color="#000000"
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with c_right:
            st.markdown("#### Tendencia de Crecimiento")
            df_evo = df.groupby(['fecha', 'plataforma'])['seguidores'].sum().reset_index()
            
            fig = px.area(df_evo, x='fecha', y='seguidores', color='plataforma', 
                          color_discrete_map=COLOR_MAP)
            
            fig.update_layout(
                plot_bgcolor='#FFFFFF', 
                paper_bgcolor='#FFFFFF',
                margin=dict(t=10, b=0, l=0, r=0), 
                template='plotly_white',
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#E5E7EB', 
                    side="right",
                    tickfont=dict(color='#000000', size=12)
                ),
                xaxis=dict(
                    tickformat="%b %d",
                    showgrid=False,
                    title=None,
                    tickfont=dict(color='#000000', size=12)
                ),
                legend=dict(
                    orientation="h", 
                    y=1.1, 
                    x=0,
                    font=dict(color='#000000', size=12),
                    title=dict(text="Plataformas:", font=dict(color='#000000', size=13, family='Montserrat'))
                ),
                hovermode='x unified',
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

    with t2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c_h1, c_h2 = st.columns([3, 1])
        with c_h1: st.markdown("#### Comparativa por Institución")
        with c_h2: metric_sort = st.selectbox("Ordenar por", ["seguidores", "engagement_rate"])
        
        fig = px.bar(df_m.sort_values(metric_sort, ascending=True),
                     x=metric_sort, 
                     y="entidad",
                     color="plataforma", 
                     orientation='h',
                     barmode="group", 
                     color_discrete_map=COLOR_MAP, 
                     text_auto='.2s')

        fig.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=0)),
            textfont=dict(color='#000000', size=11)
        )
        
        fig.update_layout(
            height=600,
            plot_bgcolor='#FFFFFF', 
            paper_bgcolor='#FFFFFF', 
            template='plotly_white', 
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis=dict(
                showgrid=True, 
                gridcolor='#E5E7EB', 
                title=None,
                tickfont=dict(color='#000000', size=12)
            ),
            yaxis=dict(
                title=None, 
                tickfont=dict(size=12, color='#000000')
            ),
            legend=dict(
                orientation="h", 
                y=1.02, 
                x=0, 
                title=dict(text="Plataformas:", font=dict(color='#000000', size=13, family='Montserrat')),
                font=dict(color='#000000', size=12)
            ),
            font=dict(family="Montserrat", size=12, color='#000000'),
            hovermode='y unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Montserrat",
                font_color="#000000"
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
