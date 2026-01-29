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
from datetime import datetime, timedelta
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


def render_comparison_view():
    """
    Renderiza vista de comparación lado a lado.
    
    Permite comparar:
    - Entidad A vs Entidad B
    - Plataforma A vs Plataforma B
    - Período A vs Período B
    """
    
    # Header
    st.title("📊 Comparación Lado a Lado")
    st.markdown("""
    Compara métricas, rendimiento y evolución entre dos entidades, plataformas o períodos.
    """)
    
    st.divider()
    
    # Estado global
    state = get_app_state()
    
    # Selector de tipo de comparación
    comparison_type = st.radio(
        "Tipo de Comparación:",
        options=["Entidades", "Plataformas", "Períodos"],
        horizontal=True,
        help="Selecciona qué deseas comparar",
    )
    
    st.divider()
    
    # Renderizar comparación según tipo seleccionado
    if comparison_type == "Entidades":
        _render_entity_comparison(state)
    elif comparison_type == "Plataformas":
        _render_platform_comparison(state)
    else:  # Períodos
        _render_period_comparison(state)


# ============================================
# COMPARACIÓN DE ENTIDADES
# ============================================

def _render_entity_comparison(state):
    """
    Comparación lado a lado de dos entidades.
    
    Args:
        state: AppState global
    """
    
    # Selectores en dos columnas
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔵 Entidad A")
        # Obtener lista de entidades disponibles
        entities = _get_available_entities()
        
        entity_a = st.selectbox(
            "Selecciona Entidad A:",
            options=entities,
            index=0 if entities else 0,
            key="comparison_entity_a",
        )
    
    with col_b:
        st.subheader("🟠 Entidad B")
        entity_b = st.selectbox(
            "Selecciona Entidad B:",
            options=entities,
            index=min(1, len(entities) - 1) if entities else 0,
            key="comparison_entity_b",
        )
    
    # Validar selección
    if not entity_a or not entity_b:
        st.warning("⚠️ Selecciona dos entidades para comparar.")
        return
    
    if entity_a == entity_b:
        st.warning("⚠️ Selecciona entidades diferentes para comparar.")
        return
    
    # Rango de fechas común
    st.markdown("### 📅 Rango de Fechas")
    date_col1, date_col2 = st.columns(2)
    
    with date_col1:
        start_date = st.date_input(
            "Fecha Inicio:",
            value=datetime.now() - timedelta(days=30),
            key="comparison_start_date",
        )
    
    with date_col2:
        end_date = st.date_input(
            "Fecha Fin:",
            value=datetime.now(),
            key="comparison_end_date",
        )
    
    # Validar rango de fechas
    if start_date >= end_date:
        st.error("❌ La fecha de inicio debe ser anterior a la fecha fin.")
        return
    
    toast_filter_applied(f"Comparando {entity_a} vs {entity_b}")
    
    st.divider()
    
    # Obtener datos filtrados para cada entidad
    with st.spinner("Cargando datos de comparación..."):
        data_a = _get_entity_data(entity_a, start_date, end_date)
        data_b = _get_entity_data(entity_b, start_date, end_date)
    
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
    
    # Calcular métricas agregadas
    total_followers = data["seguidores"].sum() if "seguidores" in data.columns else 0
    avg_engagement = data["engagement_rate"].mean() if "engagement_rate" in data.columns else 0
    
    # Calcular interacciones: usar columna interacciones si existe, sino estimar
    if "interacciones" in data.columns:
        total_interactions = data["interacciones"].sum()
    elif "engagement_rate" in data.columns and "seguidores" in data.columns:
        # Estimar: interacciones ≈ (engagement_rate / 100) * seguidores
        data_copy = data.copy()
        data_copy["interacciones_estimadas"] = (data_copy["engagement_rate"] / 100) * data_copy["seguidores"]
        total_interactions = data_copy["interacciones_estimadas"].sum()
    else:
        total_interactions = 0
    
    # Mostrar KPIs
    st.metric(
        "Total Seguidores",
        f"{total_followers:,.0f}",
        delta=None,
    )
    
    # Determinar estado de engagement (usar primera plataforma si hay datos)
    engagement_status = ""
    if not data.empty and "plataforma" in data.columns and avg_engagement > 0:
        first_platform = data["plataforma"].iloc[0]
        status, emoji = _get_engagement_health(first_platform, avg_engagement)
        engagement_status = f"{emoji} {status}"
    
    st.metric(
        "Engagement Promedio",
        f"{avg_engagement:.2f}%",
        delta=engagement_status if engagement_status else None,
    )
    
    st.metric(
        "Total Interacciones",
        f"{total_interactions:,.0f}",
        delta=None,
    )


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
    
    # Línea para entidad A - agrupar por fecha
    if not data_a.empty and "fecha" in data_a.columns and "seguidores" in data_a.columns:
        # Agrupar por fecha y sumar seguidores (todas las plataformas)
        data_a_grouped = data_a.groupby("fecha")["seguidores"].sum().reset_index()
        data_a_grouped = data_a_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_a_grouped["fecha"],
            y=data_a_grouped["seguidores"],
            mode="lines+markers",
            name=entity_a,
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        ))
    
    # Línea para entidad B - agrupar por fecha
    if not data_b.empty and "fecha" in data_b.columns and "seguidores" in data_b.columns:
        # Agrupar por fecha y sumar seguidores (todas las plataformas)
        data_b_grouped = data_b.groupby("fecha")["seguidores"].sum().reset_index()
        data_b_grouped = data_b_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_b_grouped["fecha"],
            y=data_b_grouped["seguidores"],
            mode="lines+markers",
            name=entity_b,
            line=dict(color="#ff7f0e", width=3),
            marker=dict(size=8),
        ))
    
    # Layout con formato de fechas en eje X
    fig.update_layout(
        title="Evolución de Seguidores",
        xaxis_title="Fecha",
        yaxis_title="Seguidores",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        xaxis=dict(
            type="date",
            tickformat="%d/%m/%Y",
            tickangle=-45,
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)


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
    
    # Línea para entidad A - agrupar por fecha
    if not data_a.empty and "fecha" in data_a.columns and "engagement_rate" in data_a.columns:
        # Agrupar por fecha y promediar engagement (todas las plataformas)
        data_a_grouped = data_a.groupby("fecha")["engagement_rate"].mean().reset_index()
        data_a_grouped = data_a_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_a_grouped["fecha"],
            y=data_a_grouped["engagement_rate"],
            mode="lines+markers",
            name=entity_a,
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        ))
    
    # Línea para entidad B - agrupar por fecha
    if not data_b.empty and "fecha" in data_b.columns and "engagement_rate" in data_b.columns:
        # Agrupar por fecha y promediar engagement (todas las plataformas)
        data_b_grouped = data_b.groupby("fecha")["engagement_rate"].mean().reset_index()
        data_b_grouped = data_b_grouped.sort_values("fecha")
        
        fig.add_trace(go.Scatter(
            x=data_b_grouped["fecha"],
            y=data_b_grouped["engagement_rate"],
            mode="lines+markers",
            name=entity_b,
            line=dict(color="#ff7f0e", width=3),
            marker=dict(size=8),
        ))
    
    # Layout con formato de fechas en eje X
    fig.update_layout(
        title="Evolución de Engagement (%)",
        xaxis_title="Fecha",
        yaxis_title="Engagement (%)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        xaxis=dict(
            type="date",
            tickformat="%d/%m/%Y",
            tickangle=-45,
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)


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
    
    # Agrupar por plataforma
    platform_data = data.groupby("plataforma")["seguidores"].sum().reset_index()
    platform_data = platform_data.sort_values("seguidores", ascending=False)
    
    # Gráfica de barras
    fig = go.Figure(data=[
        go.Bar(
            x=platform_data["plataforma"],
            y=platform_data["seguidores"],
            marker_color=color,
            text=platform_data["seguidores"],
            texttemplate='%{text:,.0f}',
            textposition='outside',
        )
    ])
    
    fig.update_layout(
        title="Seguidores por Plataforma",
        xaxis_title="Plataforma",
        yaxis_title="Seguidores",
        template="plotly_white",
        height=300,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)


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

def _get_available_entities() -> list:
    """
    Obtiene lista de entidades disponibles en los datos.
    
    Returns:
        Lista de nombres de entidades
    """
    state = get_app_state()
    entities = state.get_available_entities()
    
    if entities:
        return sorted(entities)
    
    # Fallback: obtener de datos frescos
    try:
        from utils.data_provider import DataProvider
        
        provider = DataProvider()
        all_data = provider.get_merged_data()
        
        if all_data is not None and not all_data.empty and "entidad" in all_data.columns:
            return sorted(all_data["entidad"].unique().tolist())
    except Exception as e:
        logger.error(f"Error al obtener entidades: {e}")
        toast_warning("No se pudieron cargar las entidades disponibles")
    
    return []


def _get_entity_data(
    entity: str,
    start_date: datetime,
    end_date: datetime,
) -> pd.DataFrame:
    """
    Obtiene datos filtrados para una entidad en un rango de fechas.
    
    Args:
        entity: Nombre de la entidad
        start_date: Fecha de inicio
        end_date: Fecha de fin
    
    Returns:
        DataFrame con datos filtrados
    """
    try:
        from utils.data_provider import DataProvider
        
        provider = DataProvider()
        all_data = provider.get_merged_data()
        
        if all_data is None or all_data.empty:
            return pd.DataFrame()
        
        # Filtrar por entidad
        data = filtrar_por_entidad(all_data, entity)
        
        # Filtrar por rango de fechas
        data = filtrar_por_rango_fechas(data, start_date, end_date)
        
        return data
    
    except Exception as e:
        logger.error(f"Error al obtener datos de {entity}: {e}")
        return pd.DataFrame()


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
