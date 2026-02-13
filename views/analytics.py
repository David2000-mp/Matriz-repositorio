"""
Vista de Comparativas para CHAMPILEAKS.
Provee dos pestañas: 'Distribución' (pie por plataforma) y 'Rendimiento' (barras por institución).
"""

import streamlit as st
import pandas as pd
try:
    import plotly.express as px
except Exception:
    px = None
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

    tab_dist, tab_perf, tab_cuenta = st.tabs(["Distribución", "Rendimiento", "Vista por Cuenta"])

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

            if cuenta_seleccionada:
                # Obtener datos de la cuenta seleccionada
                cuenta_data = df[df["usuario_red"] == cuenta_seleccionada]
                if not cuenta_data.empty:
                    cuenta_row = cuenta_data.iloc[0]
                    cuenta_seguidores = cuenta_row["seguidores"]
                    cuenta_plataforma = cuenta_row["plataforma"]

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

    st.markdown("---")
    st.info("Usa los filtros globales en la barra lateral para ajustar institución y periodo.")
