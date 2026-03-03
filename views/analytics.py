"""
Vista de Comparativas para CHAMPILEAKS.
Provee dos pestañas: 'Distribución' (pie por plataforma) y 'Rendimiento' (barras por institución).
"""

import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    px = None
    go = None
from utils.data_provider import data_provider
from components import COLOR_MAP, PLOTLY_CONFIG
from components.skeleton_loaders import show_chart_skeleton
from utils.data_manager import get_reverse_lookup
from utils.helpers import generate_social_url


def render(df=None):
    """Renderiza la vista de Comparativas.

    - Si `df` no se provee, se cargan datos con data_provider.
    - Normaliza columnas básicas generadas por merges.
    """
    st.title("Comparativas")

    # Cargar datos usando data provider con force_reload para datos frescos
    if df is None:
        # Progress bar con pasos para analytics
        progress_bar = st.progress(0)
        status = st.empty()
        
        status.text("📥 1/3: Cargando datos comparativos...")
        progress_bar.progress(33)
        import time
        time.sleep(0.2)
        
        status.text("🔄 2/3: Procesando métricas...")
        progress_bar.progress(66)
        df = data_provider.get_merged_data(force_reload=True)
        
        status.text("✅ 3/3: Aplicando normalización...")
        progress_bar.progress(100)
        time.sleep(0.2)
        
        # Limpiar progress bar
        progress_bar.empty()
        status.empty()

    if df.empty:
        st.warning("⚠️ No hay registros después de la normalización. Verifica los filtros o la conexión a datos.")
        return

    # Limpieza defensiva CRÍTICA antes de procesamiento
    # 1. Eliminar filas donde columnas críticas son NaN
    df = df.dropna(subset=['plataforma', 'entidad'], how='all')
    
    # 2. Eliminar filas con strings vacíos en entidad (fix para merge failures)
    df = df[df['entidad'] != '']
    
    if df.empty:
        st.warning("⚠️ Todos los registros fueron eliminados al limpiar datos vacíos. Intenta con otros filtros.")
        return

    tab_dist, tab_perf, tab_cuenta, tab_avanzadas = st.tabs(["Distribución", "Rendimiento", "Vista por Cuenta", "Visualizaciones Avanzadas"])

    with tab_dist:
        st.subheader("Distribución de Seguidores por Plataforma")
        # Limpiar NaN en plataforma antes de agrupar
        df_plat_clean = df[df['plataforma'].notna() & (df['plataforma'] != '')].copy()
        if df_plat_clean.empty:
            st.info("ℹ️ No hay datos de plataformas válidas para mostrar distribución.")
        else:
            df_plat = df_plat_clean.groupby("plataforma", dropna=False)["seguidores"].sum().reset_index()
            if df_plat.empty:
                st.info("ℹ️ No hay datos para la distribución.")
            else:
                # Skeleton loader para pie chart
                pie_placeholder = st.empty()
                with pie_placeholder.container():
                    show_chart_skeleton(height=400)
                
                try:
                    if px is None:
                        pie_placeholder.empty()
                        st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
                    else:
                        fig = px.pie(df_plat, names="plataforma", values="seguidores", color="plataforma", color_discrete_map=COLOR_MAP)
                        fig.update_traces(
                            textposition="inside",
                            textinfo="percent+label",
                            textfont={"color": "#000000"},
                        )
                        fig.update_layout(
                            margin=dict(t=30, b=10),
                            paper_bgcolor="white",
                            plot_bgcolor="white",
                            font={"color": "#000000"},
                            title_font={"color": "#000000"},
                            legend={"font": {"color": "#000000"}},
                            hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
                        )
                        pie_placeholder.empty()  # Remover skeleton
                        st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG)
                        
                        # Botones de exportación
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📊 Exportar Gráfico (PNG)",
                                data=fig.to_image(format="png"),
                                file_name="distribucion_plataformas.png",
                                mime="image/png",
                                help="Descarga el gráfico de distribución como imagen PNG"
                            )
                        with col2:
                            csv_data = df_plat.to_csv(index=False)
                            st.download_button(
                                "📋 Exportar Datos (CSV)",
                                data=csv_data,
                                file_name="distribucion_plataformas.csv",
                                mime="text/csv",
                                help="Descarga los datos de distribución como archivo CSV"
                            )
                except Exception as e:
                    pie_placeholder.empty()
                    st.error(f"Error al generar el gráfico de distribución: {e}")
                    st.info("Datos disponibles para debug:")
                    st.dataframe(df_plat)

    with tab_perf:
        st.subheader("Rendimiento por Institución (Seguidores)")
        # Limpiar NaN en entidad antes de agrupar
        df_ent_clean = df[df['entidad'].notna() & (df['entidad'] != '')].copy()
        if df_ent_clean.empty:
            st.info("ℹ️ No hay datos de instituciones válidas para mostrar ranking.")
        else:
            df_ent = df_ent_clean.groupby("entidad", dropna=False)["seguidores"].sum().reset_index()
            if df_ent.empty:
                st.info("ℹ️ No hay datos para el ranking de instituciones.")
            else:
                df_ent = df_ent.sort_values("seguidores", ascending=False)
                # Skeleton loader para bar chart
                bar_placeholder = st.empty()
                with bar_placeholder.container():
                    show_chart_skeleton(height=450)
                
                try:
                    if px is None:
                        bar_placeholder.empty()
                        st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
                    else:
                        fig2 = px.bar(df_ent, x="seguidores", y="entidad", orientation="h", text="seguidores")
                        fig2.update_traces(textfont={"color": "#000000"})
                        fig2.update_layout(
                            margin=dict(t=30, b=10),
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
                        bar_placeholder.empty()  # Remover skeleton
                        st.plotly_chart(fig2, width='stretch', config=PLOTLY_CONFIG)
                        
                        # Botones de exportación
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📊 Exportar Gráfico (PNG)",
                                data=fig2.to_image(format="png"),
                                file_name="rendimiento_instituciones.png",
                                mime="image/png",
                                help="Descarga el gráfico de rendimiento como imagen PNG"
                            )
                        with col2:
                            csv_data = df_ent.to_csv(index=False)
                            st.download_button(
                                "📋 Exportar Datos (CSV)",
                                data=csv_data,
                                file_name="rendimiento_instituciones.csv",
                                mime="text/csv",
                                help="Descarga los datos de rendimiento como archivo CSV"
                            )
                except Exception as e:
                    bar_placeholder.empty()
                    st.error(f"Error al generar el gráfico de rendimiento: {e}")
                    st.info("Datos disponibles para debug:")
                    st.dataframe(df_ent.head(10))

    with tab_cuenta:
        st.subheader("Vista por Cuenta - Análisis Comparativo")

        # Obtener lookup inverso para enriquecer información
        reverse_lookup = get_reverse_lookup()

        # Obtener instituciones que tienen cuentas con datos (con validación robusta)
        instituciones_con_datos = []
        for usuario in df["usuario_red"].unique():
            # Validar que usuario no sea NaN o string vacío
            if pd.notna(usuario) and str(usuario).strip() and usuario in reverse_lookup:
                institucion = reverse_lookup[usuario]['school']
                if institucion and institucion not in instituciones_con_datos:
                    instituciones_con_datos.append(institucion)
        instituciones_con_datos.sort()

        if not instituciones_con_datos:
            st.info("💡 No hay instituciones con datos disponibles. Por favor, captura datos o verifica la conexión a Google Sheets.")
            st.markdown("""**Sugerencias:**
            - Ve a la sección 'Captura' para agregar datos manualmente
            - Verifica que los datos en Google Sheets estén sincronizados
            - Asegúrate de que las URLs en los registros coincidan con el diccionario COLEGIOS_MARISTAS
            """)
            return

        # Selector de institución
        institucion_seleccionada = st.selectbox(
            "Seleccionar institución para análisis comparativo:",
            options=instituciones_con_datos,
            help="Elige una institución Marista para ver sus cuentas disponibles"
        )

        if institucion_seleccionada:
            # Obtener cuentas disponibles para esta institución
            cuentas_institucion = []
            for usuario in df["usuario_red"].unique():
                if usuario in reverse_lookup and reverse_lookup[usuario]['school'] == institucion_seleccionada:
                    cuentas_institucion.append((usuario, reverse_lookup[usuario]['platform']))

            if not cuentas_institucion:
                st.info(f"No hay cuentas con datos para {institucion_seleccionada}.")
                return

            # Selector de cuenta
            opciones_cuentas = [f"{usuario} ({platform})" for usuario, platform in cuentas_institucion]
            cuenta_seleccionada_display = st.selectbox(
                "Seleccionar cuenta específica:",
                options=opciones_cuentas,
                help="Elige una cuenta específica de la institución para comparar su rendimiento"
            )

            # Extraer el usuario real de la selección
            cuenta_seleccionada = cuenta_seleccionada_display.split(" (")[0] if cuenta_seleccionada_display else None

            # Selector de segunda cuenta para comparación (solo si hay más de una cuenta disponible)
            if len(opciones_cuentas) > 1:
                opciones_cuentas_sin_primera = [opt for opt in opciones_cuentas if opt != cuenta_seleccionada_display]
                segunda_cuenta_display = st.selectbox(
                    "Seleccionar segunda cuenta para comparar:",
                    options=opciones_cuentas_sin_primera,
                    help="Elige otra cuenta de la institución para comparar métricas directamente"
                )
                segunda_cuenta = segunda_cuenta_display.split(" (")[0] if segunda_cuenta_display else None
            else:
                segunda_cuenta = None

            if cuenta_seleccionada:
                # Obtener datos de la cuenta seleccionada
                cuenta_data = df[df["usuario_red"] == cuenta_seleccionada]
                if not cuenta_data.empty:
                    cuenta_row = cuenta_data.iloc[0]
                    cuenta_seguidores = cuenta_row["seguidores"]
                    cuenta_plataforma = cuenta_row["plataforma"]

                    # Mostrar comparación lado a lado si hay segunda cuenta
                    if segunda_cuenta:
                        # Obtener datos de la segunda cuenta
                        segunda_data = df[df["usuario_red"] == segunda_cuenta]
                        if not segunda_data.empty:
                            segunda_row = segunda_data.iloc[0]
                            segunda_seguidores = segunda_row["seguidores"]
                            segunda_plataforma = segunda_row["plataforma"]
                            
                            st.markdown("### 🔄 Comparación Directa entre Cuentas")
                            
                            # Tabla de comparación side-by-side
                            metrics = ["Seguidores"]
                            cuenta1_vals = [cuenta_seguidores]
                            cuenta2_vals = [segunda_seguidores]
                            diff_abs = [cuenta_seguidores - segunda_seguidores]
                            diff_pct = [(diff_abs[0] / segunda_seguidores * 100) if segunda_seguidores != 0 else 0]
                            
                            comp_df = pd.DataFrame({
                                "Métrica": metrics,
                                f"{cuenta_seleccionada} ({cuenta_plataforma})": cuenta1_vals,
                                f"{segunda_cuenta} ({segunda_plataforma})": cuenta2_vals,
                                "Diferencia Absoluta": diff_abs,
                                "Diferencia %": [f"{pct:.1f}%" for pct in diff_pct]
                            })
                            
                            st.table(comp_df)
                            
                            # Visualización gráfica de las diferencias
                            if px is not None:
                                # Preparar datos para gráfico
                                plot_df = pd.DataFrame({
                                    "Cuenta": [f"{cuenta_seleccionada} ({cuenta_plataforma})", f"{segunda_cuenta} ({segunda_plataforma})"],
                                    "Seguidores": [cuenta_seguidores, segunda_seguidores]
                                })
                                
                                fig_comp = px.bar(
                                    plot_df,
                                    x="Cuenta",
                                    y="Seguidores",
                                    color="Cuenta",
                                    text="Seguidores",
                                    title="Comparación de Seguidores"
                                )
                                fig_comp.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                                fig_comp.update_layout(
                                    margin=dict(t=30, b=10),
                                    paper_bgcolor="white",
                                    plot_bgcolor="white",
                                    font={"color": "#000000"},
                                    title_font={"color": "#000000"},
                                    xaxis={"color": "#000000", "tickfont": {"color": "#000000"}},
                                    yaxis={"color": "#000000", "gridcolor": "#E0E0E0", "title": {"font": {"color": "#000000"}}, "tickfont": {"color": "#000000"}},
                                    showlegend=False
                                )
                                st.plotly_chart(fig_comp, width='stretch', config=PLOTLY_CONFIG)
                            else:
                                st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
                            
                            st.divider()

                    # Mostrar información enriquecida de la cuenta
                    st.markdown("### 📊 Información de la Cuenta")
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        # Defensivo: asegurar que todas las variables son strings (no NaN)
                        inst_str = str(institucion_seleccionada).strip() if pd.notna(institucion_seleccionada) else "N/A"
                        cuenta_str = str(cuenta_seleccionada).strip() if pd.notna(cuenta_seleccionada) else "N/A"
                        plat_str = str(cuenta_plataforma).strip() if pd.notna(cuenta_plataforma) else "N/A"
                        st.info(f"**Institución:** {inst_str}\n\n**Cuenta:** {cuenta_str}\n\n**Plataforma:** {plat_str}")

                with col2:
                    # Asegurar que seguidores es número válido
                    seg_val = int(cuenta_seguidores) if pd.notna(cuenta_seguidores) and cuenta_seguidores != '' else 0
                    st.metric(
                        label="Seguidores",
                        value=f"{seg_val:,.0f}"
                    )

                with col3:
                    # Enlace directo si está en la tabla
                    if cuenta_seleccionada in reverse_lookup:
                        # Asegurar que plataforma es string válido
                        plat_link = str(cuenta_plataforma).strip() if pd.notna(cuenta_plataforma) else "Plataforma"
                        social_url = generate_social_url(plat_link, cuenta_seleccionada)
                        if social_url:
                            st.markdown(f"[🔗 Ver en {plat_link}]({social_url})")
                        else:
                            st.info("Enlace no disponible")
                    else:
                        st.info("Cuenta externa")

                st.divider()

                # Opción adicional: comparación vs promedio de todas las plataformas
                with st.expander("📊 Comparación vs Promedio de Todas las Plataformas", expanded=False):
                    st.markdown("**Comparación de la cuenta seleccionada contra el promedio de cada red social:**")

                    # Obtener todas las plataformas disponibles
                    plataformas_disponibles = df["plataforma"].unique()

                    # Crear métricas para cada plataforma
                    cols = st.columns(min(len(plataformas_disponibles), 3))  # Máximo 3 columnas

                    for i, plataforma in enumerate(plataformas_disponibles):
                        with cols[i % len(cols)]:
                            # Calcular promedio de la plataforma
                            promedio_plataforma = df[df["plataforma"] == plataforma]["seguidores"].mean()

                            # Calcular delta porcentual de la cuenta vs promedio de esta plataforma
                            if promedio_plataforma > 0:
                                delta_plataforma = ((cuenta_seguidores - promedio_plataforma) / promedio_plataforma) * 100
                            else:
                                delta_plataforma = 0

                            # Resaltar la plataforma de la cuenta seleccionada
                            titulo_plataforma = f"📍 {plataforma}" if plataforma == cuenta_plataforma else plataforma

                            st.metric(
                                titulo_plataforma,
                                f"{promedio_plataforma:,.0f} seguidores",
                                f"{delta_plataforma:+.1f}%",
                                help=f"Promedio de cuentas en {plataforma}"
                            )

                    # Microcopy contextual específico para la plataforma de la cuenta
                    promedio_actual = df[df["plataforma"] == cuenta_plataforma]["seguidores"].mean()
                    if promedio_actual > 0:
                        delta_porcentual_actual = ((cuenta_seguidores - promedio_actual) / promedio_actual) * 100
                    else:
                        delta_porcentual_actual = 0

                    st.markdown("---")
                    if delta_porcentual_actual > 0:
                        st.success(f"📈 **{cuenta_seleccionada}** supera el promedio de {cuenta_plataforma} en {abs(delta_porcentual_actual):.1f}%")
                    elif delta_porcentual_actual < 0:
                        st.warning(f"📉 **{cuenta_seleccionada}** está por debajo del promedio de {cuenta_plataforma} en {abs(delta_porcentual_actual):.1f}%")
                    else:
                        st.info(f"⚖️ **{cuenta_seleccionada}** está exactamente en el promedio de {cuenta_plataforma}")

    with tab_avanzadas:
        st.subheader("Visualizaciones Avanzadas")
        
        # Scatter Plot: Engagement vs Seguidores
        if 'engagement_rate' in df.columns and 'seguidores' in df.columns:
            st.markdown("### 📊 Scatter Plot: Engagement vs Seguidores")
            fig_scatter = px.scatter(df, x='seguidores', y='engagement_rate', color='plataforma', hover_data=['entidad', 'usuario_red'])
            st.plotly_chart(fig_scatter, config=PLOTLY_CONFIG)
        else:
            st.warning("Datos insuficientes para scatter plot.")
        
        # Heatmap de correlación
        numeric_cols = ['seguidores', 'engagement_rate', 'alcance', 'interacciones', 'likes_promedio']
        available_cols = [col for col in numeric_cols if col in df.columns]
        if len(available_cols) > 1:
            st.markdown("### 🔥 Heatmap: Matriz de Correlación")
            corr_matrix = df[available_cols].corr()
            fig_heatmap = px.imshow(corr_matrix, text_auto=True, aspect="auto")
            st.plotly_chart(fig_heatmap, config=PLOTLY_CONFIG)
        else:
            st.warning("Datos insuficientes para heatmap.")
        
        # Radar Chart: Promedios por Plataforma
        st.markdown("### 🕸️ Radar Chart: Promedios por Plataforma")
        if go is not None and not df.empty:
            # Calcular promedios por plataforma para métricas disponibles
            radar_data = {}
            for col in available_cols:
                platform_avg = df.groupby('plataforma')[col].mean()
                radar_data[col] = platform_avg
            
            # Crear radar chart
            fig_radar = go.Figure()
            for platform in df['plataforma'].unique():
                values = []
                for col in available_cols:
                    if platform in radar_data[col].index:
                        values.append(radar_data[col][platform])
                    else:
                        values.append(0)
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=available_cols,
                    fill='toself',
                    name=platform
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, None])
                ),
                showlegend=True
            )
            st.plotly_chart(fig_radar, config=PLOTLY_CONFIG)
        else:
            st.warning("Datos insuficientes para radar chart.")

    st.markdown("---")
    st.info("Usa los filtros globales en la barra lateral para ajustar institución y periodo.")
