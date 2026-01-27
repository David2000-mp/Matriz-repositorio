"""
Vista Dashboard Global para CHAMPILEAKS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
try:
    import plotly.express as px
except Exception:
    px = None
import logging
from utils import (
    simular,
    save_batch,
    generar_reporte_html,
    COLEGIOS_MARISTAS,
)
from utils.data_provider import data_provider
from utils.data_manager import load_configs
from components import COLOR_MAP, inject_custom_css
from utils.analytics import (
    calculate_growth_metrics,
    calculate_health_score,
    apply_moving_average,
    detect_anomalies,
    normalize_monthly_latest,
    summarize_followers_growth,
)
from utils.reports import generate_pdf_report


# Configuración optimizada para gráficos Plotly (rendimiento en la nube)
PLOTLY_CONFIG = {
    "displayModeBar": False,  # Ocultar barra de herramientas
    "responsive": True,       # Responsive
    "displaylogo": False,     # Ocultar logo Plotly
    "modeBarButtonsToRemove": [
        "pan2d", "select2d", "lasso2d", "autoScale2d", "resetScale2d",
        "zoom2d", "zoomIn2d", "zoomOut2d", "toImage"
    ],  # Remover botones innecesarios
    "staticPlot": False,      # Mantener interactividad mínima
}

PLOTLY_LAYOUT_DEFAULTS = {
    "font": {"size": 10},      # Fuente más pequeña para mejor rendimiento
    "margin": {"l": 20, "r": 20, "t": 40, "b": 20},  # Márgenes reducidos
    "showlegend": True,
    "legend": {"orientation": "h", "y": -0.2},  # Leyenda horizontal abajo
}


def paginate_dataframe(df, page_size=1000, page_key="page"):
    """
    Implementa paginación para DataFrames grandes.
    Retorna el DataFrame paginado y controles de navegación.
    """
    if df is None or len(df) <= page_size:
        return df, None

    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size

    # Control de página
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("◀ Anterior", disabled=st.session_state.get(page_key, 1) == 1):
            if page_key in st.session_state:
                st.session_state[page_key] = max(1, st.session_state[page_key] - 1)
            st.rerun()

    with col2:
        current_page = st.session_state.get(page_key, 1)
        st.write(f"Página {current_page} de {total_pages} ({total_rows:,} filas)")

    with col3:
        if st.button("Siguiente ▶", disabled=current_page >= total_pages):
            st.session_state[page_key] = current_page + 1
            st.rerun()

    # Aplicar paginación
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size

    return df.iloc[start_idx:end_idx], total_pages


def render(df=None):
    # Inyectar estilos globales desde components
    inject_custom_css()

    st.title("Dashboard Global")

    # Cargar datos usando data provider si no se proporcionaron
    if df is None:
        # IMPORTANTE: Siempre forzar recarga en dashboard para ver datos frescos
        # después de guardar desde data_entry
        df = data_provider.get_merged_data(force_reload=True)
        
        # Debug visual temporal para confirmar cantidad de registros cargados
        if df is not None:
            try:
                st.sidebar.write(f"DEBUG: {len(df)} registros cargados")
            except Exception:
                pass

    # Selector temporal rápido
    col_time, col_space = st.columns([2, 3])
    with col_time:
        periodo_seleccionado = st.radio(
            "Periodo de análisis:",
            ["Último mes", "Últimos 3 meses", "Histórico"],
            horizontal=True,
            help="Selecciona el periodo para el análisis de datos"
        )

    # Micro-interacción: status mientras procesamos/normalizamos el DataFrame
    with st.status("Buscando datos en la nube..."):
        # quick check (df already validated above)
        pass

    with st.status("Procesando históricos..."):
        # Si recibimos un DataFrame filtrado desde el entrypoint, úsalo.
        if df is None or (hasattr(df, "empty") and df.empty):
            st.info("No hay datos para los filtros seleccionados. Ajusta los filtros o intenta otro periodo.")
            return

        # Trabajaremos con dos vistas internas:
        # - df_full: todo el histórico recibido (p. ej. filtrado por entidad si aplica)
        # - df_m_month: datos limitados al mes seleccionado (usado para KPIs y ranking)
        df_full = df.copy()

        # Asegurar tipos antes de cualquier cálculo
        if "fecha" in df_full.columns:
            df_full["fecha"] = pd.to_datetime(df_full["fecha"], errors="coerce")
            # Eliminar filas con fechas inválidas para evitar errores en .dt.strftime
            df_full = df_full.dropna(subset=['fecha'])
            # Consolidar: mantener solo último registro por cuenta y mes para evitar doble conteo
            df_full = normalize_monthly_latest(df_full)

        # Aplicar suavizado (promedio móvil 3M) sobre seguidores e interacciones
        try:
            df_full = apply_moving_average(df_full, col="seguidores")
            if "interacciones" in df_full.columns:
                df_full = apply_moving_average(df_full, col="interacciones")
        except Exception as e:
            logging.warning(f"No se pudo aplicar moving average: {e}")

        # Detectar anomalías
        try:
            df_full = detect_anomalies(df_full, threshold=0.20)
        except Exception as e:
            logging.warning(f"No se pudo detectar anomalías: {e}")

        # Normalizar nombres de columnas resultantes de merges: muchas vistas esperan
        # columnas como 'plataforma' o 'entidad' sin sufijos. Si el DataFrame tiene
        # versiones con sufijos (_x/_y), preferirlas. Si ninguna existe, rellenar
        # con un valor por defecto para evitar KeyError en agrupaciones.
        for logical in ("plataforma", "entidad", "usuario_red"):
            if logical in df_full.columns:
                continue
            for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
                if suff in df_full.columns:
                    ser = df_full.loc[:, suff]
                    if isinstance(ser, pd.DataFrame):
                        ser = ser.iloc[:, 0]
                    df_full[logical] = ser
                    break
            else:
                df_full[logical] = "Unknown"

        # Asegurar que las columnas numéricas estén en formato correcto para evitar errores
        for _col in ("seguidores", "interacciones"):
            if _col in df_full.columns:
                df_full[_col] = pd.to_numeric(df_full[_col], errors="coerce").fillna(0)

        # Determinar periodo (mes) a partir del histórico para etiquetas/títulos
        meses = sorted(df_full["fecha"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)  # type: ignore
        mes = meses[0] if meses else None

        if not mes:
            st.info("No hay meses válidos en los datos.")
            return

        # Aplicar filtro temporal según selección del usuario
        if periodo_seleccionado == "Últimos 3 meses" and len(meses) >= 3:
            meses_seleccionados = meses[:3]
            # Asegurar que fecha sea datetime antes de usar strftime
            if pd.api.types.is_datetime64_any_dtype(df_full["fecha"]):
                df_full_temp = df_full.copy()
                df_m_month = df_full_temp[df_full_temp["fecha"].dt.strftime("%Y-%m").isin(meses_seleccionados)].copy()  # type: ignore
            else:
                st.error("Error: La columna 'fecha' no es de tipo datetime válido.")
                return
            periodo_label = f"{meses[2]} - {meses[0]}"
        elif periodo_seleccionado == "Histórico":
            df_m_month = df_full.copy()  # Usar todos los datos históricos
            periodo_label = "Histórico completo"
        else:
            # DataFrame reducido al mes seleccionado (para KPIs y ranking). NO se usa
            # para calcular la salud ni las series históricas.
            df_m_month = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes].copy()  # type: ignore
            periodo_label = mes

    # ========================================================================
    # VALIDACIÓN DEFENSIVA: Si df_m_month está vacío, mostrar warning y salir
    # ========================================================================
    if df_m_month.empty:
        st.warning(
            f"⚠️ No hay datos disponibles para el período seleccionado: **{periodo_label}**\n\n"
            "Esto puede deberse a:\n"
            "- Filtros muy restrictivos aplicados\n"
            "- Período sin datos registrados\n"
            "- Problemas de sincronización con Google Sheets\n\n"
            "Intenta seleccionar otro período o ajustar los filtros."
        )
        return

    # Botón de descarga del reporte HTML usando utils.generar_reporte_html
    try:
        report_html = generar_reporte_html(df_m_month, f"Reporte {periodo_label}")
        st.download_button(
            "Descargar Reporte HTML",
            report_html,
            file_name=f"Reporte_{periodo_label}.html",
            mime="text/html",
        )
    except Exception as e:
        logging.warning(f"No se pudo generar el reporte HTML: {e}")
        st.info("No se pudo generar el reporte HTML para descarga. Puedes intentar de nuevo más tarde.")

    # Verificar anomalías en el mes actual
    anomalias_mes = df_m_month[
        (df_m_month.get("anomalia_seguidores", False)) | 
        (df_m_month.get("anomalia_interacciones", False))
    ]
    plataformas_anomalas = anomalias_mes["plataforma"].unique() if not anomalias_mes.empty else []

    # Alerta ejecutiva si hay anomalías (defensiva contra NaN)
    if len(plataformas_anomalas) > 0:
        # Filtrar NaN y convertir a string
        plataformas_limpia = [str(p) for p in plataformas_anomalas if pd.notna(p) and str(p).strip() != '']
        if plataformas_limpia:
            plataformas_str = ", ".join(plataformas_limpia)
            st.warning(f"⚠️ Nota: Se detectó un comportamiento inusual en {plataformas_str} durante este periodo.")

    # --- Resumen Ejecutivo ---
    st.subheader("Resumen Ejecutivo")

    # KPIs principales con snapshot consolidado por cuenta
    followers_resume = summarize_followers_growth(df_full)
    tot_seg = int(followers_resume.get("total", 0))
    seg_prev_total = int(followers_resume.get("total_prev", 0))

    try:
        if "id_cuenta" in df_m_month.columns:
            int_series = df_m_month.drop_duplicates(subset=["id_cuenta"])['interacciones']
        else:
            int_series = df_m_month.drop_duplicates(subset=["entidad", "plataforma", "fecha"])['interacciones']
        tot_int = int(int_series.sum())
    except Exception:
        tot_int = int(df_m_month['interacciones'].sum()) if 'interacciones' in df_m_month.columns else 0

    er_global = (tot_int / tot_seg * 100.0) if tot_seg > 0 else 0.0

    # Mes anterior para MoM
    meses_disponibles = sorted(df_full["fecha"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)  # type: ignore
    mes_anterior = meses_disponibles[1] if len(meses_disponibles) > 1 else None

    yoy_seg = None
    if mes_anterior:
        df_prev = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes_anterior]  # type: ignore
        # usar desduplicación consistente para comparar
        if "id_cuenta" in df_prev.columns:
            seg_prev = df_prev.drop_duplicates(subset=["id_cuenta"] )['seguidores'].sum()
            int_prev = df_prev.drop_duplicates(subset=["id_cuenta"] )['interacciones'].sum()
        else:
            seg_prev = df_prev.drop_duplicates(subset=["entidad", "plataforma", "fecha"] )['seguidores'].sum()
            int_prev = df_prev.drop_duplicates(subset=["entidad", "plataforma", "fecha"] )['interacciones'].sum()
        er_prev = (int_prev / seg_prev * 100.0) if seg_prev > 0 else 0.0
        delta_seg = ((tot_seg - seg_prev) / seg_prev * 100.0) if seg_prev > 0 else 0.0
        delta_int = ((tot_int - int_prev) / int_prev * 100.0) if int_prev > 0 else 0.0
        delta_er = er_global - er_prev
        # Detector de anomalías: alerta si el delta de seguidores es > +/-20%
        try:
            if abs(delta_seg) > 20:
                st.warning(
                    "⚠️ Se detectó un salto inusual en los datos. Verifica la consistencia de las capturas manuales."
                )
        except Exception:
            # Si delta_seg no está definido o hay error, no hacer nada
            pass
        # YoY: comparar mismo mes año anterior
        try:
            mes_dt = pd.to_datetime(mes + "-01")
            prev_year_dt = mes_dt - pd.DateOffset(years=1)
            prev_year_str = prev_year_dt.strftime("%Y-%m")
            # Asegurar que fecha sea datetime antes de usar strftime
            if pd.api.types.is_datetime64_any_dtype(df["fecha"]):
                df_temp = df.copy()
                df_prev_year = df_temp[df_temp["fecha"].dt.strftime("%Y-%m") == prev_year_str]  # type: ignore
            else:
                df_prev_year = pd.DataFrame()  # DataFrame vacío si fecha no es datetime
            seg_prev_year = df_prev_year["seguidores"].sum() if not df_prev_year.empty else 0
            if seg_prev_year > 0:
                yoy_seg = (tot_seg - seg_prev_year) / seg_prev_year * 100.0
            else:
                yoy_seg = None
        except Exception:
            yoy_seg = None
    else:
        delta_seg = ((tot_seg - seg_prev_total) / seg_prev_total * 100.0) if seg_prev_total > 0 else 0.0
        delta_int = 0.0
        delta_er = 0.0

    # Health score (calculate before rendering KPIs) — usar el histórico completo
    health_score = calculate_health_score(df_full)

    # Verificar si hay anomalías en el mes actual para badges
    anomalia_seguidores = df_m_month.get("anomalia_seguidores", pd.Series(False)).any()
    anomalia_interacciones = df_m_month.get("anomalia_interacciones", pd.Series(False)).any()

    k1, k2, k3, k4 = st.columns(4)
    # Mostrar MoM y YoY juntos cuando estén disponibles
    if mes_anterior:
        if yoy_seg is not None:
            delta_display = f"{delta_seg:+.1f}% (YoY {yoy_seg:+.1f}%)"
        else:
            delta_display = f"{delta_seg:+.1f}%"
    else:
        delta_display = "-"

    with k1:
        st.metric(
            label="Seguidores",
            value=f"{tot_seg:,.0f}",
            delta=delta_display,
        )
        if anomalia_seguidores:
            st.markdown("⚠️ **Anomalía detectada**", help="Variación >20% vs promedio móvil o mes anterior")

    with k2:
        st.metric(
            label="Interacciones",
            value=f"{tot_int:,.0f}",
            delta=f"{delta_int:+.1f}%" if mes_anterior else "-",
        )
        if anomalia_interacciones:
            st.markdown("⚠️ **Anomalía detectada**", help="Variación >20% vs promedio móvil o mes anterior")
    k3.metric(
        "Engagement",
        f"{er_global:.2f}%",
        delta=f"{delta_er:+.2f} pp" if mes_anterior else "-",
    )
    # Salud Digital: mostrar número y color
    score_label = f"{health_score:.0f}"
    if health_score > 80:
        color = "#2ecc71"  # green
    elif health_score > 60:
        color = "#f1c40f"  # yellow
    else:
        color = "#e74c3c"  # red
    # Badge Pro: tarjeta con borde dinámico y tooltip explicativo
    tooltip = (
        "Este score promedia tu Engagement (50%), Crecimiento Anual (30%) y Consistencia (20%)."
    )
    k4.markdown(
        f"<div title='{tooltip}' style='padding:8px;border-radius:8px;border:2px solid {color};background:#ffffff;text-align:center;'>"
        f"<div style='font-size:11px;color:#666;margin-bottom:6px;'>Salud Digital</div>"
        f"<div style='font-size:22px;font-weight:800;color:{color};'>{score_label}</div>"
        f"<div style='font-size:11px;color:#444;margin-top:6px;'>Score (0-100)</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Métricas de cobertura usando la tabla de cuentas
    st.markdown("### 📊 Cobertura de Plataformas")
    total_schools = len(COLEGIOS_MARISTAS)
    schools_with_data = df_m_month["entidad"].nunique() if not df_m_month.empty else 0
    coverage_percentage = (schools_with_data / total_schools * 100) if total_schools > 0 else 0

    # Cobertura por plataforma
    platform_coverage = {}
    for platform in ["Facebook", "Instagram", "TikTok"]:
        schools_with_platform = sum(1 for school in COLEGIOS_MARISTAS.values() if platform in school)
        platform_coverage[platform] = schools_with_platform / total_schools * 100 if total_schools > 0 else 0

    col_cov1, col_cov2, col_cov3, col_cov4 = st.columns(4)
    with col_cov1:
        st.metric(
            label="Instituciones con Datos",
            value=f"{schools_with_data}/{total_schools}",
            delta=f"{coverage_percentage:.1f}%"
        )
    with col_cov2:
        st.metric(
            label="Facebook",
            value=f"{platform_coverage.get('Facebook', 0):.1f}%"
        )
    with col_cov3:
        st.metric(
            label="Instagram",
            value=f"{platform_coverage.get('Instagram', 0):.1f}%"
        )
    with col_cov4:
        st.metric(
            label="TikTok",
            value=f"{platform_coverage.get('TikTok', 0):.1f}%"
        )

    # Alertas suaves basadas en análisis de crecimiento
    if mes_anterior and delta_seg < 0:
        st.info("💡 **Crecimiento mensual por debajo del promedio**: Considera revisar estrategias de engagement en las plataformas con menor rendimiento.")

    # Alerta de salud digital baja
    if health_score < 60:
        st.warning("⚠️ **Salud Digital baja**: El engagement general está por debajo del umbral recomendado. Revisa el contenido y la frecuencia de publicación.")

    # Microcopy contextual para lectura ejecutiva
    if delta_seg > 10:
        st.success("🚀 **Excelente crecimiento**: La red está expandiéndose a buen ritmo. Mantén las estrategias actuales.")
    elif delta_seg > 0:
        st.info("📈 **Crecimiento positivo**: La tendencia es favorable, pero hay oportunidad de acelerar el crecimiento.")

    # Botón de descarga PDF
    school_name = st.session_state.get('filtro_entidad', 'Todos')
    period = st.session_state.get('filtro_mes', periodo_label)
    kpis = {
        'seguidores': {'valor': tot_seg, 'delta': delta_display},
        'interacciones': {'valor': tot_int, 'delta': f"{delta_int:+.1f}%" if mes_anterior else "-"},
        'engagement': {'valor': f"{er_global:.2f}%", 'delta': f"{delta_er:+.2f} pp" if mes_anterior else "-"}
    }
    anomalies_list = []
    if not anomalias_mes.empty:
        for _, row in anomalias_mes.iterrows():
            if row.get('anomalia_seguidores', False):
                anomalies_list.append(f"Anomalía en seguidores de {row['plataforma']}")
            if row.get('anomalia_interacciones', False):
                anomalies_list.append(f"Anomalía en interacciones de {row['plataforma']}")

    # Preparar nombre de archivo seguro
    safe_school = str(school_name).replace(' ', '_').replace('/', '_')
    safe_period = str(periodo_label).replace(' ', '_')
    file_name = f"Reporte_{safe_school}_{safe_period}.pdf"

    col1, col2 = st.columns([3, 1])
    with col2:
        try:
            pdf_data = generate_pdf_report(school_name, period, kpis, anomalies_list, health_score)
        except Exception as e:
            logging.warning(f"No se pudo generar el PDF: {e}")
            pdf_data = None

        if pdf_data:
            clicked = st.download_button(
                "📥 Descargar Reporte PDF",
                data=pdf_data,
                file_name=file_name,
                mime='application/pdf',
                help="Genera y descarga un reporte PDF ejecutivo con los datos actuales"
            )
            if clicked:
                try:
                    # st.toast es reciente; intentar y fallback a st.success
                    if hasattr(st, 'toast'):
                        st.toast('PDF generado correctamente')
                    else:
                        st.success('PDF generado correctamente')
                except Exception:
                    st.success('PDF generado correctamente')
        else:
            st.info('No se pudo generar el PDF en este momento.')

    st.markdown("---")

    # --- Seguidores totales por red social ---
    st.subheader("Seguidores Totales por Red Social")

    # Calcular datos para el gráfico de barras
    platform_data = df_m_month.groupby("plataforma")["seguidores"].sum().reset_index()
    platform_data = platform_data.sort_values("seguidores", ascending=False)

    # Calcular porcentajes y tendencias vs mes anterior
    total_followers = platform_data["seguidores"].sum()
    platform_data["porcentaje"] = (platform_data["seguidores"] / total_followers * 100).round(1)

    # Inicializar tendencia como float para evitar conflictos de tipos
    platform_data["tendencia"] = 0.0

    # Calcular tendencia vs mes anterior usando merge vectorizado
    if mes_anterior:
        # Asegurar que fecha sea datetime antes de usar strftime
        if pd.api.types.is_datetime64_any_dtype(df_full["fecha"]):
            df_full_temp = df_full.copy()
            df_prev_month = df_full_temp[df_full_temp["fecha"].dt.strftime("%Y-%m") == mes_anterior].copy()  # type: ignore
        else:
            df_prev_month = pd.DataFrame()  # DataFrame vacío si fecha no es datetime
        prev_platform_data = df_prev_month.groupby("plataforma")["seguidores"].sum().reset_index()

        # Merge calculado para asignar tendencia vectorizada
        platform_data = platform_data.merge(prev_platform_data, on="plataforma", how="left", suffixes=("", "_prev"))
        platform_data["tendencia"] = (
            ((platform_data["seguidores"] - platform_data["seguidores_prev"]) / platform_data["seguidores_prev"] * 100)
            .round(1)
            .fillna(0.0)  # Asegurar float
        )
        # Limpiar columna temporal
        platform_data = platform_data.drop(columns=["seguidores_prev"])

    # Crear gráfico de barras
    if px is None:
        st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
    else:
        fig_platform = px.bar(
            platform_data,
            x="plataforma",
            y="seguidores",
            color="plataforma",
            color_discrete_map=COLOR_MAP,
            title="Distribución de Seguidores por Plataforma",
            labels={"seguidores": "Seguidores", "plataforma": "Red Social"}
        )

        # Personalizar tooltips y layout
        fig_platform.update_traces(
            hovertemplate="<b>%{x}</b><br>" +
                         "Seguidores: %{y:,.0f}<br>" +
                         "Porcentaje: %{customdata[0]}%<br>" +
                         "Tendencia vs mes anterior: %{customdata[1]}+%",
            customdata=platform_data[["porcentaje", "tendencia"]].values,
            showlegend=False
        )

        fig_platform.update_layout(
            xaxis_title="",
            yaxis_title="Seguidores",
            font={"size": 10},
            margin={"l": 20, "r": 20, "t": 40, "b": 20}
        )

        st.plotly_chart(fig_platform, config=PLOTLY_CONFIG)

    st.markdown("---")

    # --- Análisis Detallado ---
    st.subheader("Análisis Detallado")

    # --- Gráficos principales (area y barras) respetando COLOR_MAP ---
    # Usar pestañas para evitar scroll infinito y mejorar la jerarquía de información
    tab_evo, tab_rank = st.tabs(["Evolución", "Ranking"])

    with tab_evo:
        # Área: evolución de seguidores por plataforma (usar df_full para mostrar tendencia completa)
        df_evo = (
            df_full.groupby(["fecha", "plataforma"])["seguidores"].sum().reset_index()
        )
        if px is None:
            st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
            fig_area = None
        else:
            fig_area = px.area(
                df_evo,
                x="fecha",
                y="seguidores",
                color="plataforma",
                color_discrete_map=COLOR_MAP,
                title="Tendencia de Seguidores por Plataforma",
            )
            fig_area.update_layout(autosize=True)

        # Añadir línea de tendencia suavizada por plataforma
        try:
            if "seguidores_ma3" in df_full.columns:
                df_trend = (
                    df_full.groupby(["fecha", "plataforma"])["seguidores_ma3"].sum().reset_index()
                )
                import plotly.graph_objects as go

                for plat in df_trend["plataforma"].unique():
                    dfp = df_trend[df_trend["plataforma"] == plat].sort_values("fecha")
                    fig_area.add_trace(
                        go.Scatter(
                            x=dfp["fecha"],
                            y=dfp["seguidores_ma3"],
                            mode="lines",
                            name=f"{plat} - Tendencia Suavizada",
                            line=dict(width=2, dash="dash"),
                            hoverinfo="skip",
                        )
                    )
        except Exception as e:
            logging.warning(f"No se pudo agregar línea de tendencia: {e}")

        if fig_area is not None:
            st.plotly_chart(
                fig_area,
                width='stretch',
                config=PLOTLY_CONFIG,
            )

        # Línea adicional: interacciones con tendencia suavizada
        try:
            if "interacciones" in df_full.columns:
                df_int = (
                    df_full.groupby(["fecha", "plataforma"])["interacciones"].sum().reset_index()
                )
                if px is None:
                    st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
                    fig_int = None
                else:
                    fig_int = px.line(
                        df_int,
                        x="fecha",
                        y="interacciones",
                        color="plataforma",
                        color_discrete_map=COLOR_MAP,
                        title="Evolución de Interacciones (Real vs Tendencia)",
                    )
                if "interacciones_ma3" in df_full.columns:
                    df_int_tr = (
                        df_full.groupby(["fecha", "plataforma"])["interacciones_ma3"].sum().reset_index()
                    )
                    import plotly.graph_objects as go

                    for plat in df_int_tr["plataforma"].unique():
                        dfp = df_int_tr[df_int_tr["plataforma"] == plat].sort_values("fecha")
                        fig_int.add_trace(
                            go.Scatter(
                                x=dfp["fecha"],
                                y=dfp["interacciones_ma3"],
                                mode="lines",
                                name=f"{plat} - Tendencia Suavizada",
                                line=dict(width=2, dash="dash"),
                                hoverinfo="skip",
                            )
                        )
                if fig_int is not None:
                    fig_int.update_layout(autosize=True)
                    st.plotly_chart(
                        fig_int,
                        width='stretch',
                        config=PLOTLY_CONFIG,
                    )
        except Exception as e:
            logging.warning(f"No se pudo generar la tendencia de interacciones: {e}")

    with st.status("¡Listo!"):
        pass

    with tab_rank:
        # Barras: ranking por institución para el mes seleccionado
        resumen = (
            df_m_month.groupby(["entidad", "plataforma"])["seguidores"].sum().reset_index()
        )
        # Ordenar para mostrar mejores arriba
        resumen = resumen.sort_values("seguidores", ascending=False)
        if px is None:
            st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
        else:
            fig_bar = px.bar(
                resumen,
                x="seguidores",
                y="entidad",
                color="plataforma",
                orientation="h",
                color_discrete_map=COLOR_MAP,
                title=f"Ranking de Seguidores ({periodo_label})",
                barmode="group",
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(autosize=True)
            st.plotly_chart(
                fig_bar,
                width='stretch',
                config=PLOTLY_CONFIG,
            )

    # --- Evolución de la Salud Digital (últimos 6 meses) ---
    try:
        # Obtener meses únicos ordenados (ascendente) y tomar los últimos 6 — usar el histórico completo
        df_full_copy = df_full.copy()
        df_full_copy["Mes"] = pd.to_datetime(df_full_copy["fecha"]).dt.to_period("M").dt.to_timestamp()
        months = sorted(df_full_copy["Mes"].dropna().unique())
        recent_months = months[-6:]

        health_points = []
        labels = []
        for m in recent_months:
            # construir dataframe hasta ese mes para permitir cálculo histórico
            df_up_to = df_full_copy[df_full_copy["Mes"] <= m]
            score_m = calculate_health_score(df_up_to)
            labels.append(m.strftime("%Y-%m"))
            health_points.append(score_m)

        if labels and health_points:
            if px is None:
                st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
            else:
                fig_health = px.line(x=labels, y=health_points, markers=True, labels={"x": "Mes", "y": "Salud"}, title="Evolución de la Salud Digital (últimos 6 meses)")
                fig_health.update_traces(line=dict(color="#2b6cb0"))
                fig_health.update_layout(autosize=True, yaxis=dict(range=[0,100]))
                st.plotly_chart(fig_health, width='stretch', config=PLOTLY_CONFIG)
    except Exception as e:
        logging.warning(f"No se pudo generar la serie histórica de salud: {e}")

    # Vista de datos plegable con paginación
    with st.expander("Ver datos fuente"):
        df_paginated, total_pages = paginate_dataframe(
            df_full.sort_values(["entidad", "plataforma"]),
            page_size=500,  # 500 filas por página para buen rendimiento
            page_key="dashboard_data_page"
        )

        if total_pages and total_pages > 1:
            st.info(f"📄 Mostrando página de datos (total: {len(df_full):,} filas)")

        st.dataframe(df_paginated, width='stretch')
