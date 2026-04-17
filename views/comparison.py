"""
Comparison View - Comparación Lado a Lado de Entidades
Sprint 2 - Semana 3: Vista de Comparación

Vista de comparación interactiva para contrastar métricas entre dos entidades,
plataformas o períodos de tiempo.

Integración:
    - utils.app_state para filtros de comparación
    - components.toast_notifications para feedback
    - utils.data_processor para cálculos
    - components.chart_components para gráficas
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.app_state import get_app_state
from components.toast_notifications import toast_info, toast_warning, toast_filter_applied
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# HELPERS DE FILTRADO (Sprint 2 Week 3)
# ============================================

def filtrar_por_entidad(df: pd.DataFrame, entidad: str) -> pd.DataFrame:
    """Filtra DataFrame por entidad"""
    if df.empty or "entidad" not in df.columns:
        return df
    return df[df["entidad"] == entidad].copy()


def filtrar_por_plataforma(df: pd.DataFrame, plataforma: str) -> pd.DataFrame:
    """Filtra DataFrame por plataforma"""
    if df.empty or "plataforma" not in df.columns:
        return df
    return df[df["plataforma"] == plataforma].copy()


def filtrar_por_rango_fechas(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """Filtra DataFrame por rango de fechas"""
    if df.empty or "fecha" not in df.columns:
        return df
    
    # Asegurar que fecha está en formato datetime
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    
    # Filtrar por rango
    mask = (df["fecha"] >= pd.to_datetime(start_date)) & (df["fecha"] <= pd.to_datetime(end_date))
    return df[mask].copy()


def _get_engagement_health(plataforma: str, engagement_rate: float) -> Tuple[str, str]:
    """
    Determina el estado de salud del engagement según la plataforma.
    
    Args:
        plataforma: Nombre de la plataforma social
        engagement_rate: Tasa de engagement en porcentaje
    
    Returns:
        Tuple[estado, emoji] donde estado es "Bajo", "Correcto", "Bueno", "Excelente"
    """
    # Rangos específicos por plataforma (basado en estándares de la industria)
    platform_ranges = {
        "Instagram": {"bajo": 1.5, "correcto": 3.0, "bueno": 6.0},
        "Facebook": {"bajo": 0.5, "correcto": 1.0, "bueno": 2.0},
        "TikTok": {"bajo": 5.0, "correcto": 10.0, "bueno": 15.0},
        "LinkedIn": {"bajo": 2.0, "correcto": 4.0, "bueno": 7.0},
        "Twitter": {"bajo": 0.05, "correcto": 0.2, "bueno": 0.5},
        "X": {"bajo": 0.05, "correcto": 0.2, "bueno": 0.5},
        "YouTube": {"bajo": 2.0, "correcto": 4.0, "bueno": 8.0},
    }
    
    # Obtener rangos para la plataforma (default genérico si no existe)
    ranges = platform_ranges.get(plataforma, {"bajo": 1.0, "correcto": 2.5, "bueno": 5.0})
    
    # Determinar estado
    if engagement_rate < ranges["bajo"]:
        return "Bajo", "🔴"
    elif engagement_rate < ranges["correcto"]:
        return "Correcto", "🟡"
    elif engagement_rate < ranges["bueno"]:
        return "Bueno", "🟢"
    else:
        return "Excelente", "🟢"


def get_engagement_status(interacciones, seguidores):
    """
    Determina el estado del engagement basado en datos disponibles.
    Retorna un mensaje explicativo si no se puede calcular o es de referencia.
    """
    if seguidores == 0 and interacciones == 0:
        return "No hay datos registrados (seguidores e interacciones ausentes). Este es un dato de referencia provisional."
    elif seguidores == 0:
        return "No hay seguidores registrados para calcular engagement. Este es un dato de referencia provisional."
    elif interacciones == 0:
        return "No hay interacciones registradas en este período. Este es un dato de referencia provisional."
    elif seguidores < 10:  # Umbral mínimo para "datos insuficientes"
        return "Datos insuficientes: audiencia muy pequeña para referencia precisa. Este es un dato de referencia provisional."
    else:
        return None  # Datos suficientes


def render_comparison_view():
    """
    Renderiza vista de comparación lado a lado.

    Permite comparar:
    - Entidad A vs Entidad B
    - Cuenta vs Promedio Red Marista (benchmark interno)
    - Plataforma A vs Plataforma B (próximamente)
    - Período A vs Período B (próximamente)
    """

    # Header
    st.title("📊 Comparación Lado a Lado")
    st.markdown("""
    Compara métricas entre dos entidades, o analiza una cuenta frente al promedio de la red Marista.
    """)

    st.divider()

    # Estado global
    state = get_app_state()

    # Cargar datos desde data_provider (fuente canónica con caché compartido)
    from utils.data_provider import data_provider
    with st.spinner("Cargando datos..."):
        df_full = data_provider.get_merged_data()

    if df_full is None or df_full.empty:
        st.warning("⚠️ No hay datos disponibles. Verifica la conexión a Google Sheets.")
        return

    # Aplicar filtro de mes del sidebar
    filtro_mes = st.session_state.get("filtro_mes", "Todos")
    if filtro_mes != "Todos" and "fecha" in df_full.columns:
        df_full = df_full.copy()
        df_full["fecha"] = pd.to_datetime(df_full["fecha"], errors="coerce")
        df_full = df_full[df_full["fecha"].dt.strftime("%Y-%m") == filtro_mes]
        if df_full.empty:
            st.warning(f"⚠️ No hay datos para el período {filtro_mes}. Cambia el filtro en el sidebar.")
            return

    # Selector global de red social para toda la vista de comparativas
    platform_options = ["Todas"]
    if "plataforma" in df_full.columns:
        platform_options += sorted([
            str(p)
            for p in df_full["plataforma"].dropna().unique()
            if str(p).strip() and str(p) != "nan"
        ])

    selected_platform = st.selectbox(
        "Red social:",
        options=platform_options,
        key="comparison_global_platform",
        help="Aplica a todos los modos de comparación",
    )

    df_for_comparison = df_full
    if selected_platform != "Todas":
        df_for_comparison = filtrar_por_plataforma(df_full, selected_platform)
        if df_for_comparison.empty:
            st.warning(f"⚠️ No hay datos para la red social {selected_platform} en el período seleccionado.")
            return

    # Selector de tipo de comparación
    comparison_type = st.radio(
        "Tipo de Comparación:",
        options=["Entidades", "Cuenta vs Promedio Red", "Plataformas", "Períodos"],
        horizontal=True,
        help="Selecciona qué deseas comparar",
    )

    st.divider()

    # Renderizar comparación según tipo seleccionado
    if comparison_type == "Entidades":
        _render_entity_comparison(state, df_for_comparison, selected_platform)
    elif comparison_type == "Cuenta vs Promedio Red":
        _render_benchmark_comparison(state, df_for_comparison, selected_platform)
    elif comparison_type == "Plataformas":
        _render_platform_comparison(state)
    else:  # Períodos
        _render_period_comparison(state)


# ============================================
# COMPARACIÓN DE ENTIDADES
# ============================================

def _render_entity_comparison(state, df: pd.DataFrame, selected_platform: str = "Todas"):
    """
    Comparación lado a lado de dos entidades.

    Args:
        state: AppState global
        df: DataFrame pre-filtrado con datos de la red
    """

    entities = _get_available_entities(df)

    if not entities:
        st.warning("⚠️ No hay entidades disponibles en los datos actuales.")
        return

    # Selectores en dos columnas
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🔵 Entidad A")
        entity_a = st.selectbox(
            "Selecciona Entidad A:",
            options=entities,
            index=0,
            key="comparison_entity_a",
        )

    with col_b:
        st.subheader("🟠 Entidad B")
        entity_b = st.selectbox(
            "Selecciona Entidad B:",
            options=entities,
            index=min(1, len(entities) - 1),
            key="comparison_entity_b",
        )

    # Validar selección
    if not entity_a or not entity_b:
        st.warning("⚠️ Selecciona dos entidades para comparar.")
        return

    if entity_a == entity_b:
        st.warning("⚠️ Selecciona entidades diferentes para comparar.")
        return

    platform_label = f" en {selected_platform}" if selected_platform != "Todas" else ""
    toast_filter_applied(f"Comparando {entity_a} vs {entity_b}{platform_label}")

    st.divider()

    # Filtrar directamente desde el DataFrame pre-cargado (sin llamadas extra a Sheets)
    data_a = _get_entity_data(entity_a, df)
    data_b = _get_entity_data(entity_b, df)

    # Validar datos
    if data_a.empty and data_b.empty:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado.")
        return

    # Renderizar comparación
    _render_entity_comparison_charts(entity_a, data_a, entity_b, data_b)


def _render_entity_comparison_charts(
    entity_a: str, 
    data_a: pd.DataFrame,
    entity_b: str, 
    data_b: pd.DataFrame
):
    """
    Renderiza gráficas comparativas entre dos entidades.
    
    Args:
        entity_a: Nombre de entidad A
        data_a: DataFrame con datos de entidad A
        entity_b: Nombre de entidad B
        data_b: DataFrame con datos de entidad B
    """
    
    # KPIs Comparativos
    st.markdown("### 📈 Métricas Clave")
    
    kpi_col1, kpi_col2 = st.columns(2)
    
    with kpi_col1:
        st.markdown(f"**🔵 {entity_a}**")
        _render_entity_kpis(data_a, color="#1f77b4")
    
    with kpi_col2:
        st.markdown(f"**🟠 {entity_b}**")
        _render_entity_kpis(data_b, color="#ff7f0e")
    
    st.divider()
    
    # Gráfica de evolución comparativa
    st.markdown("### 📊 Evolución Temporal")
    
    with st.expander("Evolución de Seguidores", expanded=True):
        if not data_a.empty or not data_b.empty:
            _render_followers_evolution_comparison(entity_a, data_a, entity_b, data_b)
        else:
            st.info("No hay datos suficientes para mostrar evolución.")
    
    with st.expander("Evolución de Engagement", expanded=False):
        if not data_a.empty or not data_b.empty:
            _render_engagement_evolution_comparison(entity_a, data_a, entity_b, data_b)
        else:
            st.info("No hay datos suficientes para mostrar evolución.")
    
    st.divider()
    
    # Distribución por plataforma
    st.markdown("### 🎯 Distribución por Plataforma")
    
    platform_col1, platform_col2 = st.columns(2)
    
    with platform_col1:
        st.markdown(f"**🔵 {entity_a}**")
        if not data_a.empty:
            _render_platform_distribution(data_a, "#1f77b4")
        else:
            st.info("Sin datos")
    
    with platform_col2:
        st.markdown(f"**🟠 {entity_b}**")
        if not data_b.empty:
            _render_platform_distribution(data_b, "#ff7f0e")
        else:
            st.info("Sin datos")

    st.divider()
    _render_export_comparison_button(data_a, data_b)


def _render_entity_kpis(data: pd.DataFrame, color: str = "#1f77b4"):
    """
    Renderiza KPIs de una entidad.
    
    Args:
        data: DataFrame con datos de la entidad
        color: Color para destacar métricas
    """
    
    if data.empty:
        st.metric("Total Seguidores", "0", delta=None)
        st.metric("Engagement Promedio", "0%", delta=None)
        st.metric("Total Interacciones", "0", delta=None)
        return
    
    # Seguidores totales: sumar todas las plataformas en su valor más reciente
    total_followers = 0
    if "seguidores" in data.columns and not data.empty:
        followers_df = data.copy()
        if "fecha" in followers_df.columns:
            followers_df["fecha"] = pd.to_datetime(followers_df["fecha"], errors="coerce")
        if "id_cuenta" in followers_df.columns and "fecha" in followers_df.columns:
            latest_rows = (
                followers_df.sort_values("fecha")
                .dropna(subset=["seguidores"])
                .groupby("id_cuenta", as_index=False)
                .tail(1)
            )
            total_followers = float(latest_rows["seguidores"].sum()) if not latest_rows.empty else 0
        elif "plataforma" in followers_df.columns and "fecha" in followers_df.columns:
            latest_rows = (
                followers_df.sort_values("fecha")
                .dropna(subset=["seguidores"])
                .groupby("plataforma", as_index=False)
                .tail(1)
            )
            total_followers = float(latest_rows["seguidores"].sum()) if not latest_rows.empty else 0
        elif "plataforma" in followers_df.columns:
            total_followers = float(followers_df.groupby("plataforma")["seguidores"].max().sum())
        else:
            total_followers = float(followers_df["seguidores"].max())
    
    # Calcular interacciones: usar columna interacciones si existe, sino estimar
    if "interacciones" in data.columns:
        total_interactions = data["interacciones"].sum()
        avg_interactions = data["interacciones"].mean() if not data.empty else 0
    elif "engagement_rate" in data.columns and "seguidores" in data.columns:
        # Estimar: interacciones ≈ (engagement_rate / 100) * alcance_estimado (seguidores * 2.5)
        data_copy = data.copy()
        data_copy["interacciones_estimadas"] = (data_copy["engagement_rate"] / 100) * (data_copy["seguidores"] * 2.5)
        total_interactions = data_copy["interacciones_estimadas"].sum()
        avg_interactions = data_copy["interacciones_estimadas"].mean() if not data_copy.empty else 0
    else:
        total_interactions = 0
        avg_interactions = 0
    
    # Calcular engagement promedio agrupando por plataforma primero
    # (consistente con Dashboard Global para evitar sesgo por conteo desigual de registros)
    if "engagement_rate" in data.columns and "plataforma" in data.columns and not data.empty:
        platform_er = data.groupby('plataforma')['engagement_rate'].mean()
        weighted_engagement = platform_er.mean() if not platform_er.empty else 0
    else:
        weighted_engagement = 0
    
    # Verificar estado del engagement con get_engagement_status
    status = get_engagement_status(total_interactions, total_followers)
    
    # Mostrar KPIs
    st.metric(
        "Total Seguidores",
        f"{total_followers:,.0f}",
        delta=None,
    )
    
    # Engagement metric: mostrar valor si existe, con nota si hay datos insuficientes
    has_engagement = "engagement_rate" in data.columns and not data.empty
    if has_engagement:
        # Determinar estado de engagement (usar primera plataforma si hay datos)
        engagement_status = ""
        if "plataforma" in data.columns:
            first_platform = data["plataforma"].iloc[0]
            status_health, emoji = _get_engagement_health(first_platform, weighted_engagement)
            engagement_status = f"{emoji} {status_health}"
        
        st.metric(
            "Engagement Promedio",
            f"{weighted_engagement:.2f}%",
            delta=engagement_status if engagement_status else None,
        )
        if status:
            st.caption(f"💡 Nota sobre Engagement: {status}")
    else:
        st.metric(
            "Engagement Promedio",
            "Datos insuficientes",
            delta=None,
        )
        if status:
            st.caption(f"💡 Nota sobre Engagement: {status}")
    
    st.metric(
        "Promedio Interacciones",
        f"{avg_interactions:,.1f}",
        delta=None,
    )
    
    # Desglose por plataforma
    if not data.empty and "plataforma" in data.columns:
        st.markdown("### 📊 Desglose por Plataforma")
        
        # Agrupar por plataforma solo con columnas disponibles para evitar errores
        agg_dict = {"seguidores": "max"}
        if "interacciones" in data.columns:
            agg_dict["interacciones"] = "mean"
        if "engagement_rate" in data.columns:
            agg_dict["engagement_rate"] = "mean"

        platform_summary = data.groupby("plataforma").agg(agg_dict).reset_index()
        
        # Calcular métricas por plataforma
        for _, row in platform_summary.iterrows():
            platform_name = row["plataforma"]
            platform_followers = row["seguidores"]
            
            # Calcular interacciones por plataforma
            if "interacciones" in data.columns:
                platform_interactions = row["interacciones"]
            else:
                # Estimar usando engagement_rate promedio de la plataforma
                platform_engagement = row.get("engagement_rate", 0)
                platform_interactions = (platform_engagement / 100) * platform_followers
            
            # Engagement por plataforma: siempre promedio (no suma)
            platform_engagement_weighted = row.get("engagement_rate", 0)
            if pd.isna(platform_engagement_weighted):
                platform_engagement_weighted = 0
            
            # Verificar estado por plataforma
            platform_status = get_engagement_status(platform_interactions, platform_followers)
            
            with st.expander(f"📱 {platform_name}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Seguidores", f"{platform_followers:,.0f}")
                
                with col2:
                    # Mostrar engagement aunque haya estado de advertencia
                    health_status, emoji = _get_engagement_health(platform_name, platform_engagement_weighted)
                    st.metric("Engagement", f"{platform_engagement_weighted:.2f}%", delta=f"{emoji} {health_status}")
                    if platform_status:
                        st.caption(f"💡 {platform_status}")
                
                with col3:
                    st.metric("Interacciones Promedio", f"{platform_interactions/platform_followers if platform_followers > 0 else 0:,.1f}")


def _render_followers_evolution_comparison(
    entity_a: str,
    data_a: pd.DataFrame,
    entity_b: str,
    data_b: pd.DataFrame,
):
    """
    Gráfica comparativa de evolución de seguidores.
    
    Args:
        entity_a: Nombre entidad A
        data_a: Datos entidad A
        entity_b: Nombre entidad B
        data_b: Datos entidad B
    """
    
    fig = go.Figure()
    
    # Línea para entidad A - sumar seguidores de todas las plataformas por fecha
    if not data_a.empty and "fecha" in data_a.columns and "seguidores" in data_a.columns:
        work_a = data_a.copy()
        work_a["fecha"] = pd.to_datetime(work_a["fecha"], errors="coerce")
        work_a = work_a.dropna(subset=["fecha"])

        # Normalmente data_provider ya entrega 1 registro por cuenta/mes.
        # Aquí sumamos por fecha para reflejar el total de la entidad.
        data_a_grouped = work_a.groupby("fecha")["seguidores"].sum().reset_index()
        data_a_grouped = data_a_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_a_grouped["fecha"],
            y=data_a_grouped["seguidores"],
            mode="lines+markers",
            name=entity_a,
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        ))
    
    # Línea para entidad B - sumar seguidores de todas las plataformas por fecha
    if not data_b.empty and "fecha" in data_b.columns and "seguidores" in data_b.columns:
        work_b = data_b.copy()
        work_b["fecha"] = pd.to_datetime(work_b["fecha"], errors="coerce")
        work_b = work_b.dropna(subset=["fecha"])

        data_b_grouped = work_b.groupby("fecha")["seguidores"].sum().reset_index()
        data_b_grouped = data_b_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_b_grouped["fecha"],
            y=data_b_grouped["seguidores"],
            mode="lines+markers",
            name=entity_b,
            line=dict(color="#ff7f0e", width=3),
            marker=dict(size=8),
        ))

    summary_cols = st.columns(2)
    if 'data_a_grouped' in locals() and not data_a_grouped.empty:
        start_a = float(data_a_grouped.iloc[0]["seguidores"])
        end_a = float(data_a_grouped.iloc[-1]["seguidores"])
        delta_a = ((end_a - start_a) / start_a * 100.0) if start_a else 0.0
        summary_cols[0].metric(f"🔵 {entity_a}", f"{end_a:,.0f}", f"{delta_a:+.1f}%")
        fig.add_annotation(x=data_a_grouped.iloc[-1]["fecha"], y=end_a, text=f"{end_a:,.0f}", showarrow=False, yshift=12, font={"color": "#1f77b4"})
    if 'data_b_grouped' in locals() and not data_b_grouped.empty:
        start_b = float(data_b_grouped.iloc[0]["seguidores"])
        end_b = float(data_b_grouped.iloc[-1]["seguidores"])
        delta_b = ((end_b - start_b) / start_b * 100.0) if start_b else 0.0
        summary_cols[1].metric(f"🟠 {entity_b}", f"{end_b:,.0f}", f"{delta_b:+.1f}%")
        fig.add_annotation(x=data_b_grouped.iloc[-1]["fecha"], y=end_b, text=f"{end_b:,.0f}", showarrow=False, yshift=-14, font={"color": "#ff7f0e"})
    
    # Layout con formato de fechas en eje X
    fig.update_layout(
        font={"color": "#000000"},
        title="Evolución de Seguidores",
        title_font={"color": "#000000"},
        xaxis_title="Fecha",
        yaxis_title="Seguidores",
        hovermode="x unified",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=400,
        hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
        legend={"font": {"color": "#000000"}},
        xaxis={
            "type": "date",
            "tickformat": "%d/%m/%Y",
            "tickangle": -45,
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.1)",
            "color": "#000000",
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
    fig.update_traces(hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": "#000000"}, "bordercolor": "#003696"})
    
    st.plotly_chart(fig, width='stretch')


def _render_engagement_evolution_comparison(
    entity_a: str,
    data_a: pd.DataFrame,
    entity_b: str,
    data_b: pd.DataFrame,
):
    """
    Gráfica comparativa de evolución de engagement.
    
    Args:
        entity_a: Nombre entidad A
        data_a: Datos entidad A
        entity_b: Nombre entidad B
        data_b: Datos entidad B
    """
    
    fig = go.Figure()
    
    # Línea para entidad A - agrupar por plataforma y fecha, luego promediar
    if not data_a.empty and "fecha" in data_a.columns and "engagement_rate" in data_a.columns:
        work_a = data_a.copy()
        work_a["fecha"] = pd.to_datetime(work_a["fecha"], errors="coerce")
        work_a["engagement_rate"] = pd.to_numeric(work_a["engagement_rate"], errors="coerce")
        work_a = work_a.dropna(subset=["fecha", "engagement_rate"])

        # Primero agrupar por fecha y plataforma, luego promediar entre plataformas
        # (consistente con Dashboard Global)
        if "plataforma" in work_a.columns:
            data_a_temp = work_a.groupby(["fecha", "plataforma"])["engagement_rate"].mean().reset_index()
            data_a_grouped = data_a_temp.groupby("fecha")["engagement_rate"].mean().reset_index()
        else:
            data_a_grouped = work_a.groupby("fecha")["engagement_rate"].mean().reset_index()
        data_a_grouped = data_a_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_a_grouped["fecha"],
            y=data_a_grouped["engagement_rate"],
            mode="lines+markers",
            name=entity_a,
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        ))
    
    # Línea para entidad B - agrupar por plataforma y fecha, luego promediar
    if not data_b.empty and "fecha" in data_b.columns and "engagement_rate" in data_b.columns:
        work_b = data_b.copy()
        work_b["fecha"] = pd.to_datetime(work_b["fecha"], errors="coerce")
        work_b["engagement_rate"] = pd.to_numeric(work_b["engagement_rate"], errors="coerce")
        work_b = work_b.dropna(subset=["fecha", "engagement_rate"])

        # Primero agrupar por fecha y plataforma, luego promediar entre plataformas
        # (consistente con Dashboard Global)
        if "plataforma" in work_b.columns:
            data_b_temp = work_b.groupby(["fecha", "plataforma"])["engagement_rate"].mean().reset_index()
            data_b_grouped = data_b_temp.groupby("fecha")["engagement_rate"].mean().reset_index()
        else:
            data_b_grouped = work_b.groupby("fecha")["engagement_rate"].mean().reset_index()
        data_b_grouped = data_b_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_b_grouped["fecha"],
            y=data_b_grouped["engagement_rate"],
            mode="lines+markers",
            name=entity_b,
            line=dict(color="#ff7f0e", width=3),
            marker=dict(size=8),
        ))

    summary_cols = st.columns(2)
    if 'data_a_grouped' in locals() and not data_a_grouped.empty:
        start_a = float(data_a_grouped.iloc[0]["engagement_rate"])
        end_a = float(data_a_grouped.iloc[-1]["engagement_rate"])
        delta_a = end_a - start_a
        summary_cols[0].metric(f"🔵 {entity_a}", f"{end_a:.2f}%", f"{delta_a:+.2f} pp")
        fig.add_annotation(x=data_a_grouped.iloc[-1]["fecha"], y=end_a, text=f"{end_a:.2f}%", showarrow=False, yshift=12, font={"color": "#1f77b4"})
    if 'data_b_grouped' in locals() and not data_b_grouped.empty:
        start_b = float(data_b_grouped.iloc[0]["engagement_rate"])
        end_b = float(data_b_grouped.iloc[-1]["engagement_rate"])
        delta_b = end_b - start_b
        summary_cols[1].metric(f"🟠 {entity_b}", f"{end_b:.2f}%", f"{delta_b:+.2f} pp")
        fig.add_annotation(x=data_b_grouped.iloc[-1]["fecha"], y=end_b, text=f"{end_b:.2f}%", showarrow=False, yshift=-14, font={"color": "#ff7f0e"})
    
    # Layout con formato de fechas en eje X
    fig.update_layout(
        font={"color": "#000000"},
        title="Evolución de Engagement (%)",
        title_font={"color": "#000000"},
        xaxis_title="Fecha",
        yaxis_title="Engagement (%)",
        hovermode="x unified",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=400,
        hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
        legend={"font": {"color": "#000000"}},
        xaxis={
            "type": "date",
            "tickformat": "%d/%m/%Y",
            "tickangle": -45,
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.1)",
            "color": "#000000",
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
    fig.update_traces(hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": "#000000"}, "bordercolor": "#003696"})
    
    st.plotly_chart(fig, width='stretch')


def _render_platform_distribution(data: pd.DataFrame, color: str = "#1f77b4"):
    """
    Gráfica de distribución por plataforma.
    
    Args:
        data: DataFrame con datos
        color: Color principal
    """
    
    if "plataforma" not in data.columns or "seguidores" not in data.columns:
        st.info("Datos insuficientes para distribución por plataforma")
        return
    
    try:
        # Agrupar por plataforma
        platform_data = data.groupby("plataforma")["seguidores"].max().reset_index()
        platform_data = platform_data.sort_values("seguidores", ascending=False)
        
        if platform_data.empty:
            st.info("No hay datos suficientes para generar la gráfica")
            return
        
        # Gráfica de barras
        fig = go.Figure(data=[
            go.Bar(
                x=platform_data["plataforma"],
                y=platform_data["seguidores"],
                marker_color=color,
                text=platform_data["seguidores"],
                texttemplate='%{text:,.0f}',
                textposition='outside',
                textfont={"color": "#000000"},
            )
        ])
        
        fig.update_layout(
            font={"color": "#000000"},
            title="Seguidores por Plataforma",
            title_font={"color": "#000000"},
            xaxis_title="Plataforma",
            yaxis_title="Seguidores",
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            height=300,
            showlegend=False,
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
        fig.update_traces(hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": "#000000"}, "bordercolor": "#003696"})
        
        st.plotly_chart(fig, width='stretch')
        
    except Exception as e:
        st.error(f"Error al generar la gráfica de distribución: {e}")
        st.info("Datos disponibles para debug:")
        if "plataforma" in data.columns and "seguidores" in data.columns:
            st.dataframe(data[["plataforma", "seguidores"]].head())


# ============================================
# COMPARACIÓN DE PLATAFORMAS
# ============================================

def _render_platform_comparison(state):
    """
    Comparación lado a lado de dos plataformas.
    
    Args:
        state: AppState global
    """
    
    st.info("🚧 Comparación de plataformas - Próximamente en Sprint 2 Semana 4")
    
    # TODO: Implementar en Semana 4
    # Similar a _render_entity_comparison pero filtrando por plataforma


# ============================================
# COMPARACIÓN DE PERÍODOS
# ============================================

def _render_period_comparison(state):
    """
    Comparación de dos períodos temporales.
    
    Args:
        state: AppState global
    """
    
    st.info("🚧 Comparación de períodos - Próximamente en Sprint 2 Semana 4")
    
    # TODO: Implementar en Semana 4
    # Comparar mismo período en años diferentes (ej: enero 2023 vs enero 2024)


# ============================================
# HELPERS DE DATOS
# ============================================

def _get_available_entities(df: pd.DataFrame = None) -> list:
    """
    Obtiene lista de entidades disponibles en los datos.

    Args:
        df: DataFrame con datos (preferido). Si es None, usa data_provider.

    Returns:
        Lista de nombres de entidades
    """
    if df is not None and not df.empty and "entidad" in df.columns:
        return sorted([str(e) for e in df["entidad"].dropna().unique() if str(e).strip() and str(e) != "nan"])

    # Fallback: data_provider (caché compartido, NO llama a Sheets directamente)
    try:
        from utils.data_provider import data_provider
        df_fallback = data_provider.get_merged_data()
        if df_fallback is not None and not df_fallback.empty and "entidad" in df_fallback.columns:
            return sorted([str(e) for e in df_fallback["entidad"].dropna().unique() if str(e).strip() and str(e) != "nan"])
    except Exception as e:
        logger.error(f"Error al obtener entidades: {e}")
        toast_warning("No se pudieron cargar las entidades disponibles")

    return []


def _get_entity_data(
    entity: str,
    df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Obtiene historial completo de datos para una entidad.

    Args:
        entity: Nombre de la entidad
        df: DataFrame pre-cargado (preferido). Si es None, usa data_provider.
            No se eliminan duplicados — normalize_monthly_latest en data_provider
            ya garantiza 1 registro por (cuenta, mes), preservando el historial.

    Returns:
        DataFrame con historial completo de la entidad
    """
    try:
        if df is not None and not df.empty:
            return filtrar_por_entidad(df, entity)

        # Fallback: data_provider (caché compartido)
        from utils.data_provider import data_provider
        all_data = data_provider.get_merged_data()

        if all_data is None or all_data.empty:
            logger.warning("No hay datos disponibles")
            return pd.DataFrame()

        return filtrar_por_entidad(all_data, entity)

    except Exception as e:
        logger.error(f"Error al obtener datos de {entity}: {e}")
        return pd.DataFrame()


# ============================================
# BENCHMARK: CUENTA VS PROMEDIO RED
# ============================================

def _calculate_network_benchmark(df: pd.DataFrame, plataforma: str = None) -> pd.DataFrame:
    """
    Calcula el promedio de la red Marista agrupado por (fecha, plataforma).

    Args:
        df: DataFrame completo de la red
        plataforma: Si se especifica, filtra solo esa plataforma antes de calcular.

    Returns:
        DataFrame con columnas [fecha, plataforma, seguidores_avg,
        engagement_rate_avg, interacciones_avg]
    """
    if df is None or df.empty or "fecha" not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    work["fecha"] = pd.to_datetime(work["fecha"], errors="coerce")
    work = work.dropna(subset=["fecha"])

    if plataforma and plataforma != "Todas" and "plataforma" in work.columns:
        work = work[work["plataforma"] == plataforma]

    if work.empty:
        return pd.DataFrame()

    group_cols = ["fecha", "plataforma"] if "plataforma" in work.columns else ["fecha"]

    agg_dict = {}
    if "seguidores" in work.columns:
        agg_dict["seguidores"] = "mean"
    if "engagement_rate" in work.columns:
        agg_dict["engagement_rate"] = "mean"
    if "interacciones" in work.columns:
        agg_dict["interacciones"] = "mean"

    if not agg_dict:
        return pd.DataFrame()

    benchmark = work.groupby(group_cols).agg(agg_dict).reset_index()
    benchmark = benchmark.rename(columns={
        "seguidores": "seguidores_avg",
        "engagement_rate": "engagement_rate_avg",
        "interacciones": "interacciones_avg",
    })
    benchmark = benchmark.sort_values("fecha")
    return benchmark


def _render_benchmark_comparison(state, df: pd.DataFrame, selected_platform: str = "Todas"):
    """
    Modo: Cuenta vs Promedio Red.
    Muestra una institución frente al benchmark interno de toda la red Marista.
    """
    st.markdown("#### Selecciona la cuenta a analizar")

    entities = _get_available_entities(df)
    if not entities:
        st.warning("⚠️ No hay entidades disponibles.")
        return

    entity = st.selectbox(
        "Institución:",
        options=entities,
        key="benchmark_entity",
    )

    if not entity:
        return

    st.divider()

    # Datos de la entidad seleccionada
    data_entity = filtrar_por_entidad(df, entity)
    plataforma_sel = selected_platform

    # Benchmark de la red
    benchmark = _calculate_network_benchmark(
        df,
        plataforma=plataforma_sel if plataforma_sel != "Todas" else None,
    )

    if data_entity.empty:
        plat_msg = f" en {plataforma_sel}" if plataforma_sel != "Todas" else ""
        st.warning(f"⚠️ No hay datos para {entity}{plat_msg}.")
        return

    if benchmark.empty:
        st.warning("⚠️ No se pudo calcular el benchmark de la red.")
        return

    plat_label = f" ({plataforma_sel})" if plataforma_sel != "Todas" else ""
    toast_filter_applied(f"{entity} vs Promedio Red{plat_label}")

    # ---- KPIs comparativos ----
    st.markdown("### 📈 Métricas Clave vs Promedio Red")

    # Valores actuales de la entidad (consolidando todas las plataformas)
    entity_followers = 0.0
    if "seguidores" in data_entity.columns and not data_entity.empty:
        entity_work = data_entity.copy()
        if "fecha" in entity_work.columns:
            entity_work["fecha"] = pd.to_datetime(entity_work["fecha"], errors="coerce")
        if "id_cuenta" in entity_work.columns and "fecha" in entity_work.columns:
            latest_entity_rows = (
                entity_work.sort_values("fecha")
                .dropna(subset=["seguidores"])
                .groupby("id_cuenta", as_index=False)
                .tail(1)
            )
            entity_followers = float(latest_entity_rows["seguidores"].sum()) if not latest_entity_rows.empty else 0.0
        elif "plataforma" in entity_work.columns and "fecha" in entity_work.columns:
            latest_entity_rows = (
                entity_work.sort_values("fecha")
                .dropna(subset=["seguidores"])
                .groupby("plataforma", as_index=False)
                .tail(1)
            )
            entity_followers = float(latest_entity_rows["seguidores"].sum()) if not latest_entity_rows.empty else 0.0
        elif "plataforma" in entity_work.columns:
            entity_followers = float(entity_work.groupby("plataforma")["seguidores"].max().sum())
        else:
            entity_followers = float(entity_work["seguidores"].max())

    if "engagement_rate" in data_entity.columns and not data_entity.empty:
        entity_er_work = data_entity.copy()
        if "fecha" in entity_er_work.columns:
            entity_er_work["fecha"] = pd.to_datetime(entity_er_work["fecha"], errors="coerce")
            latest_date_entity = entity_er_work["fecha"].max()
            if pd.notna(latest_date_entity):
                entity_er_work = entity_er_work[entity_er_work["fecha"] == latest_date_entity]

        if "plataforma" in entity_er_work.columns:
            per_plat_er = entity_er_work.groupby("plataforma")["engagement_rate"].mean()
            entity_engagement = float(per_plat_er.mean()) if not per_plat_er.empty else 0.0
        else:
            entity_engagement = float(entity_er_work["engagement_rate"].mean())
    else:
        entity_engagement = 0.0

    entity_interactions = float(data_entity["interacciones"].mean()) if "interacciones" in data_entity.columns else 0.0

    # Promedios de la red (último periodo disponible)
    net_followers = 0.0
    net_engagement = 0.0
    net_interactions = 0.0
    if not benchmark.empty and "fecha" in benchmark.columns:
        benchmark_work = benchmark.copy()
        benchmark_work["fecha"] = pd.to_datetime(benchmark_work["fecha"], errors="coerce")
        latest_benchmark_date = benchmark_work["fecha"].max()
        latest_benchmark = benchmark_work[benchmark_work["fecha"] == latest_benchmark_date] if pd.notna(latest_benchmark_date) else benchmark_work

        if "seguidores_avg" in latest_benchmark.columns:
            net_followers = float(latest_benchmark["seguidores_avg"].sum())
        if "engagement_rate_avg" in latest_benchmark.columns:
            net_engagement = float(latest_benchmark["engagement_rate_avg"].mean())
        if "interacciones_avg" in latest_benchmark.columns:
            net_interactions = float(latest_benchmark["interacciones_avg"].mean())

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    with kpi_col1:
        delta_pct_followers = ((entity_followers - net_followers) / net_followers * 100) if net_followers > 0 else 0.0
        sign = "+" if delta_pct_followers >= 0 else ""
        st.metric(
            "Seguidores",
            f"{entity_followers:,.0f}",
            delta=f"{sign}{delta_pct_followers:.1f}% vs red ({net_followers:,.0f})",
        )

    with kpi_col2:
        delta_eng = entity_engagement - net_engagement
        sign = "+" if delta_eng >= 0 else ""
        st.metric(
            "Engagement",
            f"{entity_engagement:.2f}%",
            delta=f"{sign}{delta_eng:.2f}pp vs red ({net_engagement:.2f}%)",
        )

    with kpi_col3:
        delta_int = entity_interactions - net_interactions
        sign = "+" if delta_int >= 0 else ""
        st.metric(
            "Interacciones (prom.)",
            f"{entity_interactions:,.1f}",
            delta=f"{sign}{delta_int:,.1f} vs red ({net_interactions:,.1f})",
        )

    st.divider()

    # ---- Gráfica de líneas doble ----
    st.markdown("### 📊 Evolución Temporal: Entidad vs Promedio Red")

    tab_seg, tab_eng = st.tabs(["Seguidores", "Engagement"])

    with tab_seg:
        _render_benchmark_chart(
            entity=entity,
            data_entity=data_entity,
            benchmark=benchmark,
            metric_entity="seguidores",
            metric_bench="seguidores_avg",
            ylabel="Seguidores",
            plataforma_sel=plataforma_sel,
        )

    with tab_eng:
        _render_benchmark_chart(
            entity=entity,
            data_entity=data_entity,
            benchmark=benchmark,
            metric_entity="engagement_rate",
            metric_bench="engagement_rate_avg",
            ylabel="Engagement (%)",
            plataforma_sel=plataforma_sel,
        )

    st.divider()

    # ---- Tabla de variación ----
    st.markdown("### 📋 Tabla de Variación vs Promedio Red")
    _render_delta_table(entity, data_entity, benchmark, plataforma_sel)


def _render_benchmark_chart(
    entity: str,
    data_entity: pd.DataFrame,
    benchmark: pd.DataFrame,
    metric_entity: str,
    metric_bench: str,
    ylabel: str,
    plataforma_sel: str = "Todas",
):
    """Gráfica de doble línea: entidad (sólida azul) vs promedio red (punteada gris)."""

    if metric_entity not in data_entity.columns and metric_bench not in benchmark.columns:
        st.info(f"No hay datos de {ylabel} disponibles.")
        return

    fig = go.Figure()

    # Línea entidad
    if not data_entity.empty and "fecha" in data_entity.columns and metric_entity in data_entity.columns:
        entity_work = data_entity.copy()
        entity_work["fecha"] = pd.to_datetime(entity_work["fecha"], errors="coerce")
        entity_work[metric_entity] = pd.to_numeric(entity_work[metric_entity], errors="coerce")
        entity_work = entity_work.dropna(subset=["fecha", metric_entity])

        if "plataforma" in entity_work.columns and plataforma_sel == "Todas":
            agg_fn = "sum" if metric_entity == "seguidores" else "mean"
            grp = entity_work.groupby(["fecha", "plataforma"])[metric_entity].agg(agg_fn).reset_index()
            entity_series = grp.groupby("fecha")[metric_entity].agg(agg_fn).reset_index()
        else:
            agg_fn = "sum" if metric_entity == "seguidores" else "mean"
            entity_series = entity_work.groupby("fecha")[metric_entity].agg(agg_fn).reset_index()
        entity_series = entity_series.sort_values("fecha")

        fig.add_trace(go.Scatter(
            x=entity_series["fecha"],
            y=entity_series[metric_entity],
            mode="lines+markers",
            name=entity,
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        ))

    # Línea benchmark (punteada gris)
    if not benchmark.empty and "fecha" in benchmark.columns and metric_bench in benchmark.columns:
        benchmark_work = benchmark.copy()
        benchmark_work["fecha"] = pd.to_datetime(benchmark_work["fecha"], errors="coerce")
        benchmark_work[metric_bench] = pd.to_numeric(benchmark_work[metric_bench], errors="coerce")
        benchmark_work = benchmark_work.dropna(subset=["fecha", metric_bench])

        if "plataforma" in benchmark_work.columns and plataforma_sel == "Todas":
            agg_fn = "sum" if metric_bench == "seguidores_avg" else "mean"
            bench_series = benchmark_work.groupby("fecha")[metric_bench].agg(agg_fn).reset_index()
        else:
            bench_series = benchmark_work[["fecha", metric_bench]].copy()
        bench_series = bench_series.sort_values("fecha")

        fig.add_trace(go.Scatter(
            x=bench_series["fecha"],
            y=bench_series[metric_bench],
            mode="lines+markers",
            name="Promedio Red Marista",
            line=dict(color="#888888", width=2, dash="dash"),
            marker=dict(size=6, symbol="diamond"),
        ))

    fig.update_layout(
        font={"color": "#000000"},
        title=f"{ylabel}: {entity} vs Promedio Red",
        title_font={"color": "#000000"},
        xaxis_title="Fecha",
        yaxis_title=ylabel,
        hovermode="x unified",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=400,
        hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
        legend={"font": {"color": "#000000"}},
        xaxis={
            "type": "date",
            "tickformat": "%d/%m/%Y",
            "tickangle": -45,
            "showgrid": True,
            "gridcolor": "rgba(0,0,0,0.1)",
            "color": "#000000",
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
    fig.update_traces(hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": "#000000"}, "bordercolor": "#003696"})
    st.plotly_chart(fig, width='stretch')


def _render_delta_table(
    entity: str,
    data_entity: pd.DataFrame,
    benchmark: pd.DataFrame,
    plataforma_sel: str = "Todas",
):
    """Tabla: Métrica | Valor Cuenta | Promedio Red | Δ% (verde si por encima, rojo si por debajo)."""

    rows = []

    # Seguidores
    if "seguidores" in data_entity.columns and "seguidores_avg" in benchmark.columns:
        val_cuenta = float(data_entity["seguidores"].max())
        val_red = float(benchmark["seguidores_avg"].mean())
        diff_pct = ((val_cuenta - val_red) / val_red * 100) if val_red > 0 else 0.0
        rows.append({"Métrica": "Seguidores", "Valor Cuenta": f"{val_cuenta:,.0f}", "Promedio Red": f"{val_red:,.0f}", "_delta": diff_pct})

    # Engagement
    if "engagement_rate" in data_entity.columns and "engagement_rate_avg" in benchmark.columns:
        if "plataforma" in data_entity.columns:
            per_plat = data_entity.groupby("plataforma")["engagement_rate"].mean()
            val_cuenta = float(per_plat.mean()) if not per_plat.empty else 0.0
        else:
            val_cuenta = float(data_entity["engagement_rate"].mean())
        val_red = float(benchmark["engagement_rate_avg"].mean())
        diff_pct = ((val_cuenta - val_red) / val_red * 100) if val_red > 0 else 0.0
        rows.append({"Métrica": "Engagement (%)", "Valor Cuenta": f"{val_cuenta:.2f}%", "Promedio Red": f"{val_red:.2f}%", "_delta": diff_pct})

    # Interacciones
    if "interacciones" in data_entity.columns and "interacciones_avg" in benchmark.columns:
        val_cuenta = float(data_entity["interacciones"].mean())
        val_red = float(benchmark["interacciones_avg"].mean())
        diff_pct = ((val_cuenta - val_red) / val_red * 100) if val_red > 0 else 0.0
        rows.append({"Métrica": "Interacciones (prom.)", "Valor Cuenta": f"{val_cuenta:,.1f}", "Promedio Red": f"{val_red:,.1f}", "_delta": diff_pct})

    if not rows:
        st.info("No hay suficientes datos para calcular la tabla de variación.")
        return

    # Construir HTML con colores
    header = "<tr><th>Métrica</th><th>Valor Cuenta</th><th>Promedio Red</th><th>Δ%</th></tr>"
    body_rows = []
    for r in rows:
        d = r["_delta"]
        sign = "+" if d >= 0 else ""
        color = "#27ae60" if d >= 0 else "#e74c3c"
        delta_html = f'<span style="color:{color};font-weight:bold">{sign}{d:.1f}%</span>'
        body_rows.append(f"<tr><td>{r['Métrica']}</td><td>{r['Valor Cuenta']}</td><td>{r['Promedio Red']}</td><td>{delta_html}</td></tr>")

    table_html = f"""
    <style>
    .cmp-delta-tbl {{width:100%;border-collapse:collapse;font-size:0.95rem;margin-bottom:1rem;}}
    .cmp-delta-tbl th {{background-color:#003696;color:white;padding:8px 12px;text-align:left;}}
    .cmp-delta-tbl td {{padding:8px 12px;border-bottom:1px solid #e0e0e0;color:#111111;}}
    .cmp-delta-tbl tr:hover td {{background-color:#f5f8ff;}}
    </style>
    <table class="cmp-delta-tbl"><thead>{header}</thead><tbody>{''.join(body_rows)}</tbody></table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ============================================
# EXPORTACIÓN DE COMPARACIÓN
# ============================================

def _render_export_comparison_button(data_a: pd.DataFrame, data_b: pd.DataFrame):
    """
    Botón para exportar datos de comparación a Excel/CSV.
    
    Args:
        data_a: Datos de entidad A
        data_b: Datos de entidad B
    """
    
    if st.button("📥 Exportar Comparación", use_container_width=True):
        try:
            # Combinar datos
            combined = pd.concat([
                data_a.assign(grupo="A"),
                data_b.assign(grupo="B"),
            ], ignore_index=True)
            
            # Convertir a CSV
            csv = combined.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"comparacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            
            toast_info("Comparación lista para descargar")
        
        except Exception as e:
            logger.error(f"Error al exportar comparación: {e}")
            toast_warning("No se pudo exportar la comparación")
