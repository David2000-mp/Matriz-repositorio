"""
Vista Dashboard Global para CHAMPILEAKS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import os
try:
    import plotly.express as px
except Exception:
    px = None
import logging
from typing import Tuple
from utils import (
    simular,
    save_batch,
    generar_reporte_html,
    COLEGIOS_MARISTAS,
)
from utils.data_provider import data_provider
from utils.visualizations import plot_engagement_evolution, sanitize_chart_dataframe
from utils.data_manager import load_configs
from components import COLOR_MAP, inject_custom_css, configure_plotly_theme
from utils.analytics import (
    calculate_growth_metrics,
    calculate_health_score,
    apply_moving_average,
    detect_anomalies,
    normalize_monthly_latest,
    summarize_followers_growth,
    build_followers_growth_ranking,
)
from utils.reports import generate_pdf_report
from utils.app_state import get_app_state
from components.toast_notifications import (
    toast_success,
    toast_info,
    toast_warning,
    toast_error,
)

# Importar configuración Plotly centralizada
from components import PLOTLY_CONFIG, PLOTLY_LAYOUT_DEFAULTS, show_kpi_skeleton, show_chart_skeleton, COLOR_MAP


def get_traffic_light_indicator(metric, value):
    """
    Retorna indicador visual de confiabilidad basado en umbrales por métrica.
    🟢 Verde: Valores óptimos
    🟡 Amarillo: Valores aceptables pero requieren atención
    🔴 Rojo: Valores problemáticos que requieren acción inmediata
    """
    if metric == 'engagement':
        # Engagement realista: 1-15% óptimo, hasta 20% aceptable
        if value <= 15:
            return "🟢"
        elif value <= 20:
            return "🟡"
        else:
            return "🔴"
    elif metric == 'growth':
        # Crecimiento: positivo óptimo, ligeramente negativo aceptable
        if value >= 0:
            return "🟢"
        elif value >= -5:
            return "🟡"
        else:
            return "🔴"
    elif metric == 'coverage':
        # Cobertura: óptima >=80%, aceptable >=50%, baja <50%
        if value >= 80:
            return "🟢"
        elif value >= 50:
            return "🟡"
        else:
            return "🔴"


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


def get_engagement_status(engagement_rate=None):
    """
    Determina el estado del engagement basado en datos disponibles.
    Retorna un mensaje explicativo si no se puede calcular o es de referencia.
    
    Args:
        engagement_rate: Tasa de engagement (opcional) para validar si hay datos reales
    
    Returns:
        str o None: Mensaje si hay limitaciones de datos, None si los datos son suficientes
    """
    # Si hay un engagement_rate válido (>0), considerar que tenemos datos suficientes
    has_engagement = engagement_rate is not None and engagement_rate > 0
    
    if not has_engagement:
        return "No hay datos de engagement registrados. Este es un dato de referencia provisional."
    
    return None  # Datos suficientes


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
        # Progress bar con pasos (usa caché compartido; sin recarga forzada)
        progress_bar = st.progress(0)
        status = st.empty()

        status.text("📥 1/3: Recuperando datos cacheados...")
        progress_bar.progress(35)

        status.text("🔄 2/3: Consolidando métricas...")
        progress_bar.progress(70)
        df = data_provider.get_merged_data(force_reload=False)

        status.text("✅ 3/3: Aplicando filtros...")
        progress_bar.progress(100)

        # Limpiar progress bar
        progress_bar.empty()
        status.empty()
        
        # Debug visual temporal para confirmar cantidad de registros cargados
        if df is not None:
            try:
                if os.getenv("APP_DEBUG", "0") == "1":
                    st.sidebar.write(f"DEBUG: {len(df)} registros cargados")
            except Exception:
                pass

    # Periodo fijo por decisión de negocio: Histórico completo.
    periodo_label = "Histórico completo"

    # Micro-interacción: status mientras procesamos/normalizamos el DataFrame
    # OCULTO: Solo visible como pop-up en depuración
    # with st.status("Buscando datos en la nube..."):
    #     pass
    # with st.status("Procesando históricos..."):
    #     pass

    # Si recibimos un DataFrame filtrado desde el entrypoint, úsalo.
    if df is None or (hasattr(df, "empty") and df.empty):
        st.warning("⚠️ No hay datos para los filtros seleccionados.")
        st.caption("💡 Ajusta los filtros o intenta otro periodo.")
        return

    # Trabajaremos con dos vistas internas:
    # - df_full: todo el histórico recibido (p. ej. filtrado por entidad si aplica)
    # - df_m_month: histórico completo (anclado por decisión de negocio)
    df_full = sanitize_chart_dataframe(
        df.copy(),
        date_cols=["fecha"],
        numeric_cols=["seguidores", "alcance", "interacciones", "likes_promedio"],
        percent_cols=["engagement_rate"],
    )

    # Asegurar tipos antes de cualquier cálculo
    if "fecha" in df_full.columns:
        # Eliminar filas con fechas inválidas para evitar errores en .dt.strftime
        df_full = df_full.dropna(subset=['fecha'])
        # Consolidar: mantener solo último registro por cuenta y mes para evitar doble conteo
        df_full = normalize_monthly_latest(df_full)

    # Aplicar suavizado (promedio móvil 3M) sobre seguidores
    try:
        df_full = apply_moving_average(df_full, col="seguidores")
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
    for _col in ("seguidores", "engagement_rate"):
        if _col in df_full.columns:
            df_full[_col] = pd.to_numeric(df_full[_col], errors="coerce").fillna(0)

    # Dashboard anclado a histórico completo.
    df_m_month = df_full.copy()

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

    # ========================================================================
    # VALIDACIONES DE CALIDAD DE DATOS
    # ========================================================================
    data_quality_issues = []
    if 'seguidores' in df_m_month.columns and (df_m_month['seguidores'] < 0).any():
        data_quality_issues.append("Valores negativos detectados en seguidores")
    if 'seguidores' in df_m_month.columns and df_m_month['seguidores'].isna().any():
        data_quality_issues.append("Datos faltantes en seguidores")
    if 'engagement_rate' in df_m_month.columns and (df_m_month['engagement_rate'] < 0).any():
        data_quality_issues.append("Valores negativos detectados en engagement")
    if 'engagement_rate' in df_m_month.columns and df_m_month['engagement_rate'].isna().any():
        data_quality_issues.append("Datos faltantes en engagement")
    if 'fecha' in df_m_month.columns and df_m_month['fecha'].isna().any():
        data_quality_issues.append("Fechas inválidas o faltantes")

    if data_quality_issues:
        st.warning("⚠️ **Problemas de calidad de datos detectados:**\n" + "\n".join(f"- {issue}" for issue in data_quality_issues))

    # Crear df_unique para cálculos consistentes
    df_unique = (
        df_m_month.sort_values(['entidad', 'plataforma', 'fecha'])
        .drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
    )

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
        st.caption("📊 No se pudo generar el reporte HTML para descarga.")

    # Verificar anomalías en el mes actual
    anomalias_mes = df_unique[
        (df_unique.get("anomalia_seguidores", False))
    ]
    plataformas_anomalas = anomalias_mes["plataforma"].unique() if not anomalias_mes.empty else []

    # Alerta ejecutiva si hay anomalías (defensiva contra NaN)
    if len(plataformas_anomalas) > 0:
        # Filtrar NaN y convertir a string
        plataformas_limpia = [str(p) for p in plataformas_anomalas if pd.notna(p) and str(p).strip() != '']
        if plataformas_limpia:
            plataformas_str = ", ".join(plataformas_limpia)
            st.toast(f"⚠️ Se detectó comportamiento inusual en {plataformas_str}", icon="⚠️")

    # --- Resumen Ejecutivo ---
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.subheader("Resumen Ejecutivo")
    with col_refresh:
        if st.button("↻", help="Actualizar datos desde Google Sheets", key="refresh_btn"):
            st.cache_data.clear()
            st.session_state.force_data_refresh = True
            st.rerun()

    # Mostrar skeleton mientras se calculan métricas
    kpi_placeholder = st.empty()
    with kpi_placeholder.container():
        show_kpi_skeleton(count=4)

    # KPIs principales con snapshot consolidado por cuenta DEL MES ACTUAL
    tot_seg = df_unique['seguidores'].sum() if 'seguidores' in df_unique.columns else 0
    seg_prev_total = 0

    try:
        # CÁLCULO DE ENGAGEMENT GLOBAL (Promedio de los valores de engagement_rate por plataforma)
        # Normalizar engagement_rate a numérico
        df_unique_calc = df_unique.copy()
        df_unique_calc['engagement_rate'] = pd.to_numeric(
            df_unique_calc['engagement_rate'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0)
        
        # Agrupar por plataforma y promediar los engagement_rate del formulario
        platform_er = df_unique_calc.groupby('plataforma').agg({
            'engagement_rate': 'mean'
        }).reset_index()
        
        # Filtrar valores infinitos y extremos
        platform_er['engagement_rate'] = platform_er['engagement_rate'].replace([float('inf'), -float('inf')], 0)
        platform_er.loc[platform_er['engagement_rate'] > 100, 'engagement_rate'] = 100
        
        # Promedio simple de los ER por plataforma (del formulario)
        er_global = platform_er['engagement_rate'].mean() if len(platform_er) > 0 else 0.0
    except Exception as e:
        logging.warning(f"Error en cálculo de engagement: {e}")
        tot_seg_for_calc = df_unique['seguidores'].sum() if 'seguidores' in df_unique.columns else 0
        er_global = df_unique['engagement_rate'].mean() if not df_unique.empty else 0.0
    meses_disponibles = sorted(df_full["fecha"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)  # type: ignore
    mes_anterior = meses_disponibles[1] if len(meses_disponibles) > 1 else None

    yoy_seg = None
    if mes_anterior:
        df_prev = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes_anterior]  # type: ignore
        df_prev_unique = df_prev.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
        
        # Calcular engagement del mes anterior usando el mismo método que el mes actual
        try:
            # Normalizar engagement_rate a numérico
            df_prev_calc = df_prev_unique.copy()
            df_prev_calc['engagement_rate'] = pd.to_numeric(
                df_prev_calc['engagement_rate'].astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            ).fillna(0)
            
            # Agrupar por plataforma y promediar los engagement_rate del formulario
            platform_er_prev = df_prev_calc.groupby('plataforma').agg({
                'engagement_rate': 'mean'
            }).reset_index()
            
            # Filtrar valores infinitos y extremos
            platform_er_prev['engagement_rate'] = platform_er_prev['engagement_rate'].replace([float('inf'), -float('inf')], 0)
            platform_er_prev.loc[platform_er_prev['engagement_rate'] > 100, 'engagement_rate'] = 100
            
            # Promedio simple de los ER por plataforma (del formulario)
            er_prev = platform_er_prev['engagement_rate'].mean() if len(platform_er_prev) > 0 else 0.0
        except Exception as e:
            logging.warning(f"Error en cálculo de engagement anterior: {e}")
            seg_prev_calc = df_prev_unique['seguidores'].sum()
            er_prev = df_prev_unique['engagement_rate'].mean() if not df_prev_unique.empty else 0.0
        
        # usar suma total para comparar seguidores
        seg_prev = df_prev_unique['seguidores'].sum()
        seg_prev_total = seg_prev
        delta_seg = ((tot_seg - seg_prev) / seg_prev * 100.0) if seg_prev > 0 else 0.0
        delta_er = er_global - er_prev
        # Detector de anomalías: alerta si el delta de seguidores es > +/-20%
        try:
            if abs(delta_seg) > 20:
                st.warning("⚠️ Salto inusual detectado. Verifica la consistencia de las capturas.")
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
            df_prev_year_unique = df_prev_year.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
            seg_prev_year = df_prev_year_unique["seguidores"].sum() if not df_prev_year_unique.empty else 0  # Último valor del año anterior
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
    anomalia_seguidores = df_unique.get("anomalia_seguidores", pd.Series(False)).any()

    # Calcular estado del engagement global
    status_global = get_engagement_status(engagement_rate=er_global)

    # Limpiar skeleton y mostrar KPIs reales
    kpi_placeholder.empty()
    
    # CSS para cards de KPIs
    st.markdown("""
    <style>
    .kpi-card {
        background: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 16px;
        margin: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .kpi-card h4 {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #495057;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #212529;
        margin: 8px 0;
    }
    .kpi-delta {
        font-size: 12px;
        margin: 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        with st.container():
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Seguidores {get_traffic_light_indicator('growth', delta_seg)}</h4>
                <div class="kpi-value">{tot_seg:,.0f}</div>
                <div class="kpi-delta">{delta_display}</div>
            </div>
            """, unsafe_allow_html=True)
        if anomalia_seguidores:
            st.markdown("⚠️ **Anomalía detectada**", help="Variación >20% vs promedio móvil o mes anterior")

    with k2:
        with st.container():
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Engagement Promedio {get_traffic_light_indicator('engagement', er_global)}</h4>
                <div class="kpi-value">{er_global:.2f}%</div>
                <div class="kpi-delta">{f"{delta_er:+.2f} pp" if mes_anterior else "-"}</div>
            </div>
            """, unsafe_allow_html=True)
        if status_global:
            st.caption(f"💡 Nota sobre Engagement: {status_global}")
    
    # Coverage KPI (assuming k3 is for coverage)
    with k3:
        # Calculate coverage - number of institutions with data
        instituciones_con_datos = df_unique['entidad'].nunique()
        total_instituciones = len(COLEGIOS_MARISTAS)
        coverage_pct = (instituciones_con_datos / total_instituciones * 100) if total_instituciones > 0 else 0
        
        with st.container():
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Cobertura Institucional</h4>
                <div class="kpi-value">{instituciones_con_datos}/{total_instituciones}</div>
                <div class="kpi-delta">{coverage_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Health score KPI (k4)
    with k4:
        score_label = f"{health_score:.0f}"
        if health_score > 80:
            color = "#1E7E34"  # Verde oscuro
        elif health_score > 60:
            color = "#CC7000"  # Naranja oscuro
        else:
            color = "#C82333"  # Rojo oscuro
        
        tooltip = (
            "Salud Digital: Score que mide la salud general de tus redes sociales. Se calcula promediando Engagement (50%), Crecimiento Anual (30%) y Consistencia (20%). Un score alto indica cuentas saludables con buen engagement y crecimiento sostenido. "
            f"Indicador de confiabilidad: {get_traffic_light_indicator('health', health_score)} (🟢 >80 óptimo, 🟡 >60 aceptable, 🔴 ≤60 requiere atención)"
        )
        
        with st.container():
            st.markdown(f"""
            <div class="kpi-card" title="{tooltip}">
                <h4>Salud Digital {get_traffic_light_indicator('health', health_score)}</h4>
                <div class="kpi-value" style="color: {color};">{score_label}</div>
                <div class="kpi-delta">Score (0-100)</div>
            </div>
            """, unsafe_allow_html=True)

    school_name = st.session_state.get('filtro_entidad', 'Todos')
    meta_seguidores = 0.0
    meta_engagement = 0.0
    df_configs = pd.DataFrame()
    config_inst = pd.DataFrame()

    try:
        df_configs = load_configs()
        if school_name != 'Todas' and df_configs is not None and not df_configs.empty and 'entidad' in df_configs.columns:
            config_inst = df_configs[
                df_configs['entidad'].astype(str).str.strip().str.casefold() == str(school_name).strip().casefold()
            ]
            if not config_inst.empty:
                meta_seguidores = float(pd.to_numeric(config_inst.iloc[0].get('meta_seguidores', 0), errors='coerce') or 0)
                meta_engagement = float(pd.to_numeric(config_inst.iloc[0].get('meta_engagement', 0), errors='coerce') or 0)
    except Exception as e:
        logging.warning(f"No se pudieron cargar metas del dashboard: {e}")

    if school_name != 'Todas' and (meta_seguidores > 0 or meta_engagement > 0):
        st.markdown("### 🎯 Avance contra Metas")
        goal_col1, goal_col2 = st.columns(2)

        with goal_col1:
            progreso_seg = (tot_seg / meta_seguidores) if meta_seguidores > 0 else 0.0
            st.caption(f"🎯 Meta: {meta_seguidores:,.0f} seguidores")
            st.progress(min(float(progreso_seg), 1.0))
            if progreso_seg >= 1.0:
                st.success(f"¡Meta cumplida! 🎉 Seguidores al {progreso_seg:.0%}")
            elif meta_seguidores > 0:
                st.caption(f"Actual: {tot_seg:,.0f} ({progreso_seg:.0%})")

        with goal_col2:
            progreso_eng = (er_global / meta_engagement) if meta_engagement > 0 else 0.0
            st.caption(f"🎯 Meta: {meta_engagement:.2f}% engagement")
            st.progress(min(float(progreso_eng), 1.0))
            if progreso_eng >= 1.0:
                st.success(f"¡Meta cumplida! 🎉 Engagement al {progreso_eng:.0%}")
            elif meta_engagement > 0:
                st.caption(f"Actual: {er_global:.2f}% ({progreso_eng:.0%})")
    elif school_name != 'Todas':
        st.caption("🎯 Configura metas para esta institución y así visualizar el avance contra objetivo.")

    # Desglose por Red Social
    st.subheader("Desglose por Red Social")
    
    # Normalizar engagement_rate a numérico
    df_unique_display = df_unique.copy()
    df_unique_display['engagement_rate'] = pd.to_numeric(
        df_unique_display['engagement_rate'].astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)
    
    # Agrupar por plataforma usando valores del formulario
    platform_summary = df_unique_display.groupby('plataforma').agg({
        'seguidores': 'sum',
        'engagement_rate': 'mean'  # Promedio de valores del formulario
    }).reset_index()
    
    # Usar engagement_rate del formulario
    platform_summary['engagement_promedio'] = platform_summary['engagement_rate']
    
    for _, row in platform_summary.iterrows():
        status = get_engagement_status(engagement_rate=row['engagement_promedio'])
        engagement_display = status if status else f"{row['engagement_promedio']:.2f}%"
        st.write(f"**{row['plataforma']}**: Seguidores totales: {row['seguidores']:,.0f}, Engagement promedio: {engagement_display}")

    # Pulse Ejecutivo por Plataforma
    st.markdown("### 🧭 Pulse Ejecutivo por Plataforma")
    if not platform_summary.empty:
        platform_summary = platform_summary.sort_values('engagement_promedio', ascending=False).reset_index(drop=True)
        leader_row = platform_summary.iloc[0]
        watch_row = platform_summary.iloc[-1]

        if health_score < 60:
            priority_text = "Reforzar contenido y frecuencia en las plataformas con ER bajo."
            priority_delta = "Atención inmediata"
        elif delta_seg < 0:
            priority_text = "Recuperar crecimiento antes de aumentar volumen de publicaciones."
            priority_delta = "Vigilar tendencia"
        else:
            priority_text = "Escalar el formato ganador y mantener consistencia semanal."
            priority_delta = "Momentum positivo"

        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric(
                "🏆 Plataforma líder",
                str(leader_row['plataforma']),
                f"ER {float(leader_row['engagement_promedio']):.2f}%"
            )
        with p2:
            st.metric(
                "👀 Plataforma a vigilar",
                str(watch_row['plataforma']),
                f"ER {float(watch_row['engagement_promedio']):.2f}%"
            )
        with p3:
            st.metric(
                "🎯 Prioridad inmediata",
                priority_delta,
                f"Salud {health_score:.0f}/100"
            )

        pulse_rows = []
        for _, row in platform_summary.iterrows():
            health_status, emoji = _get_engagement_health(str(row['plataforma']), float(row['engagement_promedio']))
            if health_status == 'Bajo':
                action = 'Optimizar contenido y revisar frecuencia'
            elif health_status == 'Correcto':
                action = 'Probar formatos de mayor interacción'
            else:
                action = 'Escalar el formato ganador'

            pulse_rows.append({
                'Plataforma': row['plataforma'],
                'Seguidores': int(row['seguidores']),
                'ER promedio': f"{float(row['engagement_promedio']):.2f}%",
                'Estado': f"{emoji} {health_status}",
                'Acción sugerida': action,
            })

        st.dataframe(pd.DataFrame(pulse_rows), width='stretch', hide_index=True)
        st.info(f"**Lectura ejecutiva:** {priority_text}")

    # Desglose detallado por plataforma
    st.markdown("### 📱 Desglose Detallado por Plataforma")
    
    for _, row in platform_summary.iterrows():
        platform_name = row['plataforma']
        platform_followers = row['seguidores']
        platform_engagement = row['engagement_promedio']
        
        with st.expander(f"📱 {platform_name}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Seguidores Totales", f"{platform_followers:,.0f}")
            
            with col2:
                status = get_engagement_status(engagement_rate=platform_engagement)
                if status:
                    st.metric("Engagement Promedio", "Datos insuficientes")
                    st.caption(f"💡 {status}")
                else:
                    health_status, emoji = _get_engagement_health(platform_name, platform_engagement)
                    st.metric("Engagement Promedio", f"{platform_engagement:.2f}%", delta=f"{emoji} {health_status}")

    # Métricas de cobertura usando la tabla de cuentas
    st.markdown("### 📊 Cobertura de Plataformas")
    total_schools = len(COLEGIOS_MARISTAS)
    schools_with_data = df_unique["entidad"].nunique() if not df_unique.empty else 0
    coverage_percentage = (schools_with_data / total_schools * 100) if total_schools > 0 else 0

    # Cobertura por plataforma
    platform_coverage = {}
    for platform in ["Facebook", "Instagram", "TikTok"]:
        schools_with_platform = sum(1 for school in COLEGIOS_MARISTAS.values() if platform in school)
        platform_coverage[platform] = schools_with_platform / total_schools * 100 if total_schools > 0 else 0

    col_cov1, col_cov2, col_cov3, col_cov4 = st.columns(4)
    with col_cov1:
        st.metric(
            label=f"Instituciones con Datos {get_traffic_light_indicator('coverage', coverage_percentage)}",
            value=f"{schools_with_data}/{total_schools}",
            delta=f"{coverage_percentage:.1f}%"
        )
    with col_cov2:
        fb_cov = platform_coverage.get('Facebook', 0)
        st.metric(
            label=f"Facebook {get_traffic_light_indicator('coverage', fb_cov)}",
            value=f"{fb_cov:.1f}%"
        )
    with col_cov3:
        ig_cov = platform_coverage.get('Instagram', 0)
        st.metric(
            label=f"Instagram {get_traffic_light_indicator('coverage', ig_cov)}",
            value=f"{ig_cov:.1f}%"
        )
    with col_cov4:
        tt_cov = platform_coverage.get('TikTok', 0)
        st.metric(
            label=f"TikTok {get_traffic_light_indicator('coverage', tt_cov)}",
            value=f"{tt_cov:.1f}%"
        )

    st.markdown("### 🚨 Alertas automáticas")
    alert_messages = []
    if mes_anterior and delta_seg < -5:
        alert_messages.append(("error", f"Caída de seguidores detectada: {delta_seg:+.1f}% vs mes anterior."))
    elif mes_anterior and delta_seg < 0:
        alert_messages.append(("warning", f"Crecimiento mensual por debajo del promedio: {delta_seg:+.1f}% vs mes anterior."))

    if mes_anterior and delta_er < -0.5:
        alert_messages.append(("warning", f"El engagement bajó {delta_er:+.2f} pp respecto al corte anterior."))

    if health_score < 60:
        alert_messages.append(("error", "Salud Digital baja. El engagement está por debajo del umbral recomendado."))
    elif health_score < 80:
        alert_messages.append(("info", "Salud Digital estable, con margen claro de mejora para llegar a nivel óptimo."))

    if len(plataformas_anomalas) > 0:
        plataformas_alerta = ", ".join(str(p) for p in plataformas_anomalas if pd.notna(p))
        alert_messages.append(("warning", f"Se detectaron anomalías recientes en: {plataformas_alerta}."))

    if not alert_messages:
        st.success("✅ Sin alertas críticas. La red mantiene una tendencia saludable.")
    else:
        for level, message in alert_messages[:3]:
            if level == "error":
                st.error(message)
            elif level == "warning":
                st.warning(message)
            else:
                st.info(message)

    # Microcopy contextual para lectura ejecutiva
    if delta_seg > 10:
        st.caption("🚀 Excelente crecimiento: La red está expandiéndose a buen ritmo.")
    elif delta_seg > 0:
        st.caption("📈 Crecimiento positivo: La tendencia es favorable.")

    # Botón de descarga PDF
    period = st.session_state.get('filtro_mes', periodo_label)
    kpis = {
        'seguidores': {'valor': tot_seg, 'delta': delta_display},
        'engagement': {'valor': f"{er_global:.2f}%", 'delta': f"{delta_er:+.2f} pp" if mes_anterior else "-"}
    }
    anomalies_list = []
    if not anomalias_mes.empty:
        for _, row in anomalias_mes.iterrows():
            if row.get('anomalia_seguidores', False):
                anomalies_list.append(f"Anomalía en seguidores de {row['plataforma']}")

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
                toast_success("PDF generado correctamente")
        else:
            st.caption("📄 No se pudo generar el PDF en este momento.")

    st.markdown("---")

    # --- Seguidores totales por red social ---
    st.subheader("Seguidores Totales por Red Social")

    # Mostrar skeleton mientras se genera gráfico
    chart_placeholder = st.empty()
    
    try:
        # Calcular datos para el gráfico de barras
        platform_data = df_unique.groupby("plataforma")["seguidores"].sum().reset_index()
        
        if platform_data.empty:
            chart_placeholder.empty()
            st.warning("No hay datos de seguidores por plataforma disponibles.")
        else:
            with chart_placeholder.container():
                show_chart_skeleton(height=400)
            
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
                df_prev_month_unique = df_prev_month.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
                prev_platform_data = df_prev_month_unique.groupby("plataforma")["seguidores"].sum().reset_index()

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
                chart_placeholder.empty()
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
                                 "Tendencia vs mes anterior: %{customdata[1]:+.1f}%<extra></extra>",
                    customdata=platform_data[["porcentaje", "tendencia"]].values,
                    showlegend=False
                )

                fig_platform.update_layout(
                    xaxis_title="",
                    yaxis_title="Seguidores",
                    font={"size": 10, "color": "#000000"},
                    title_font={"color": "#000000"},
                    margin={"l": 20, "r": 20, "t": 40, "b": 20},
                    paper_bgcolor="white",
                    plot_bgcolor="white",
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

                # Limpiar skeleton y mostrar gráfico real
                chart_placeholder.empty()
                st.plotly_chart(fig_platform, config=PLOTLY_CONFIG, width='stretch')
                
    except Exception as e:
        chart_placeholder.empty()
        logging.error(f"Error al generar gráfica de plataformas: {e}")
        st.error(f"Error en gráfica de plataformas: {str(e)}")

    st.markdown("---")

    # --- Análisis Detallado ---
    st.subheader("Análisis Detallado")

    # --- Gráficos principales (area y barras) respetando COLOR_MAP ---
    # Usar pestañas para evitar scroll infinito y mejorar la jerarquía de información
    tab_evo, tab_rank = st.tabs(["Evolución", "Ranking"])

    with tab_evo:
        st.markdown("#### ⏱️ Comparativa temporal rápida")
        evo_col1, evo_col2, evo_col3 = st.columns(3)
        with evo_col1:
            st.metric("Seguidores vs mes anterior", f"{tot_seg:,.0f}", f"{delta_seg:+.1f}%")
        with evo_col2:
            st.metric("Engagement vs mes anterior", f"{er_global:.2f}%", f"{delta_er:+.2f} pp")
        with evo_col3:
            status_label = "Óptimo" if health_score >= 80 else "Atención" if health_score < 60 else "Estable"
            st.metric("Salud digital", f"{health_score:.0f}/100", status_label)

        # Área: evolución de seguidores por plataforma (usar df_full para mostrar tendencia completa)
        fig_area = None
        evolution_placeholder = st.empty()
        
        try:
            if df_full.empty:
                evolution_placeholder.empty()
                st.warning("No hay datos disponibles para gráficar evolución.")
            else:
                with evolution_placeholder.container():
                    show_chart_skeleton(height=400)
                
                if px is None:
                    evolution_placeholder.empty()
                    st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
                else:
                    df_evo = (
                        df_full.groupby(["fecha", "plataforma"])["seguidores"].sum().reset_index()
                    )
                    
                    # Asegurar que fecha sea datetime para Plotly
                    df_evo["fecha"] = pd.to_datetime(df_evo["fecha"], errors="coerce")
                    df_evo = df_evo.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])
                    
                    # DEBUG: Mostrar información de datos
                    logging.info(f"DEBUG df_evo: registros={len(df_evo)}, fechas_unicas={df_evo['fecha'].nunique()}, plataformas={df_evo['plataforma'].unique().tolist()}")
                    for plat in df_evo['plataforma'].unique():
                        dfp = df_evo[df_evo['plataforma'] == plat]
                        logging.info(f"  {plat}: {len(dfp)} puntos, fechas={dfp['fecha'].dt.strftime('%Y-%m').tolist()}")
                    
                    if df_evo.empty:
                        evolution_placeholder.empty()
                        st.warning("No hay datos después de agrupar (seguidores).")
                    else:
                        fig_area = px.area(
                            df_evo,
                            x="fecha",
                            y="seguidores",
                            color="plataforma",
                            color_discrete_map=COLOR_MAP,
                            title="Tendencia de Seguidores por Plataforma",
                            markers=True,
                        )
                        fig_area.update_layout(
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
                        fig_area.update_xaxes(type="date")
                        
                        # DEBUG: Verificar traces de Plotly
                        logging.info(f"DEBUG fig_area: traces={len(fig_area.data)}, traces_names={[t.name for t in fig_area.data]}")
                        for i, trace in enumerate(fig_area.data):
                            logging.info(f"  trace {i} ({trace.name}): {len(trace.x)} puntos")

                        # Añadir línea de tendencia suavizada por plataforma
                        if "seguidores_ma3" in df_full.columns:
                            df_trend = (
                                df_full.groupby(["fecha", "plataforma"])["seguidores_ma3"].max().reset_index()
                            )
                            # Asegurar que fecha sea datetime
                            df_trend["fecha"] = pd.to_datetime(df_trend["fecha"], errors="coerce")
                            df_trend = df_trend.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])
                            
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

                        for plat in df_evo["plataforma"].dropna().unique():
                            dfp = df_evo[df_evo["plataforma"] == plat].sort_values("fecha")
                            if dfp.empty:
                                continue
                            latest_point = dfp.iloc[-1]
                            prev_value = dfp.iloc[-2]["seguidores"] if len(dfp) > 1 else 0
                            delta_pct = ((latest_point["seguidores"] - prev_value) / prev_value * 100.0) if prev_value else 0.0
                            is_anomaly = False
                            if "anomalia_seguidores" in df_full.columns:
                                latest_matches = df_full[
                                    (df_full["plataforma"] == plat) & (df_full["fecha"] == latest_point["fecha"])
                                ]
                                is_anomaly = bool(latest_matches.get("anomalia_seguidores", pd.Series(False)).any())

                            badge = "⚠️" if is_anomaly else ""
                            fig_area.add_annotation(
                                x=latest_point["fecha"],
                                y=latest_point["seguidores"],
                                text=f"{badge}{plat} {delta_pct:+.1f}%",
                                showarrow=True,
                                arrowhead=2,
                                ax=35,
                                ay=-25,
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor="#D0D5DD",
                                font={"size": 10, "color": "#101828"},
                            )

                        evolution_placeholder.empty()  # Remover skeleton
                        st.plotly_chart(
                            fig_area,
                            width='stretch',
                            config=PLOTLY_CONFIG,
                        )
        except Exception as e:
            evolution_placeholder.empty()
            logging.error(f"Error al generar gráfica de evolución: {e}")
            st.error(f"Error al gráfica de evolución: {str(e)}")

        # Gráfica de evolución de engagement
        st.markdown("### 📈 Evolución de Engagement por Red Social")
        platform_filter = st.selectbox(
            "Filtrar por red social:",
            ["Todas", "Facebook", "Instagram", "TikTok", "Twitter"],
            key="engagement_platform_filter"
        )
        plot_engagement_evolution(df_full, platform_filter)

    with tab_rank:
        # Skeleton loader para ranking
        ranking_placeholder = st.empty()
        
        try:
            if df_unique.empty:
                ranking_placeholder.empty()
                st.warning("No hay datos para mostrar ranking.")
            else:
                with ranking_placeholder.container():
                    show_chart_skeleton(height=450)
                
                # Barras: ranking por institución para el mes seleccionado
                resumen = (
                    df_unique.groupby(["entidad", "plataforma"])["seguidores"].sum().reset_index()
                )
                
                if resumen.empty:
                    ranking_placeholder.empty()
                    st.warning("No hay datos después de agrupar (ranking).")
                else:
                    # Ordenar para mostrar mejores arriba
                    resumen = resumen.sort_values("seguidores", ascending=False)
                    if px is None:
                        ranking_placeholder.empty()
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
                        fig_bar.update_layout(
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
                        ranking_placeholder.empty()  # Remover skeleton
                        st.plotly_chart(
                            fig_bar,
                            width='stretch',
                            config=PLOTLY_CONFIG,
                        )
                
                # Nueva gráfica: Ranking de Engagement por Institución y Red Social
                st.markdown("---")
                st.subheader("📊 Ranking de Engagement por Institución")
                
                engagement_placeholder = st.empty()
                with engagement_placeholder.container():
                    show_chart_skeleton(height=450)
                
                try:
                    # Preparar datos: asegurar que engagement_rate sea numérico
                    df_engagement = df_unique.copy()
                    
                    # Debug: verificar si existe la columna engagement_rate
                    if 'engagement_rate' not in df_engagement.columns:
                        engagement_placeholder.empty()
                        st.warning("⚠️ La columna 'engagement_rate' no existe en los datos. Ingresa valores de engagement en Google Sheets.")
                    else:
                        df_engagement['engagement_rate'] = pd.to_numeric(
                            df_engagement['engagement_rate'].astype(str).str.replace(',', '.', regex=False),
                            errors='coerce'
                        ).fillna(0)
                        
                        # Agrupar por institución y plataforma
                        resumen_engagement = df_engagement.groupby(['entidad', 'plataforma']).agg({
                            'engagement_rate': 'mean'  # Promedio de engagement por institución-plataforma
                        }).reset_index()
                        
                        # Ordenar por engagement ascendente
                        resumen_engagement = resumen_engagement.sort_values('engagement_rate', ascending=True)
                        
                        if resumen_engagement.empty or resumen_engagement['engagement_rate'].sum() == 0:
                            engagement_placeholder.empty()
                            st.info("ℹ️ No hay datos de engagement disponibles para el ranking.")
                        else:
                            # Crear gráfica de barras horizontales
                            fig_engagement = px.bar(
                                resumen_engagement,
                                x='engagement_rate',
                                y='entidad',
                                color='plataforma',
                                orientation='h',
                                color_discrete_map=COLOR_MAP,
                                title=f"Ranking de Engagement Rate ({periodo_label})",
                                barmode='group',
                                labels={'engagement_rate': 'Engagement Rate (%)', 'entidad': 'Institución'},
                            )

                            benchmark_map = (
                                resumen_engagement.groupby('plataforma')['engagement_rate']
                                .mean()
                                .sort_values(ascending=False)
                                .to_dict()
                            )
                            for plataforma, benchmark in benchmark_map.items():
                                fig_engagement.add_vline(
                                    x=float(benchmark),
                                    line_dash='dot',
                                    line_width=2,
                                    line_color=COLOR_MAP.get(plataforma, '#98A2B3'),
                                    opacity=0.7,
                                    annotation_text=f"Bench {plataforma}: {benchmark:.2f}%",
                                    annotation_position='top',
                                )
                            
                            fig_engagement.update_traces(
                                texttemplate='%{x:.2f}%',
                                textposition='outside',
                                hovertemplate='<b>%{y}</b><br>%{fullData.name}<br>ER: %{x:.2f}%<extra></extra>'
                            )
                            
                            fig_engagement.update_layout(
                                autosize=True,
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                font={'color': '#000000'},
                                title_font={'color': '#000000'},
                                legend={'font': {'color': '#000000'}},
                                hoverlabel={'font': {'color': '#000000'}, 'bgcolor': '#FFFFFF', 'bordercolor': '#003696'},
                                xaxis={
                                    'color': '#000000',
                                    'gridcolor': '#E0E0E0',
                                    'title': {'font': {'color': '#000000'}},
                                    'tickfont': {'color': '#000000'},
                                },
                                yaxis={
                                    'color': '#000000',
                                    'gridcolor': '#E0E0E0',
                                    'title': {'font': {'color': '#000000'}},
                                    'tickfont': {'color': '#000000'},
                                },
                            )
                            
                            engagement_placeholder.empty()
                            st.plotly_chart(
                                fig_engagement,
                                width='stretch',
                                config=PLOTLY_CONFIG,
                            )
                            st.caption(
                                "Benchmarks por plataforma: " + ", ".join(
                                    f"{plataforma} {benchmark:.2f}%" for plataforma, benchmark in benchmark_map.items()
                                )
                            )
                except Exception as e:
                    engagement_placeholder.empty()
                    logging.error(f"Error al generar gráfica de engagement: {e}")
                    st.error(f"Error en gráfica de engagement: {str(e)}")
        except Exception as e:
            ranking_placeholder.empty()
            logging.error(f"Error al generar gráfica de ranking: {e}")
            st.error(f"Error en gráfica de ranking: {str(e)}")

    # --- Ranking de Crecimiento de Seguidores ---
    st.markdown("### 🚀 Crecimiento de Seguidores por Institución")
    growth_mode_label = st.radio(
        "Modo de comparación temporal",
        options=[
            "Mensual (último mes vs mes anterior)",
            "Últimas 2 mediciones",
        ],
        horizontal=True,
        key="dashboard_growth_mode",
    )

    growth_mode = "monthly" if growth_mode_label.startswith("Mensual") else "latest_two"
    st.caption("Ranking híbrido: combina crecimiento absoluto y porcentual para mayor precisión.")

    def render_growth_ranking_section(section_title: str, ranking_df: pd.DataFrame, subtitle: str):
        st.markdown(f"#### {section_title}")

        if ranking_df.empty:
            st.info(f"No hay datos de crecimiento disponibles para {section_title.lower()}.")
            return

        if px is None:
            st.warning("Plotly no disponible - no se puede mostrar la gráfica")
            return

        ranking_abs_df = ranking_df.sort_values(
            "crecimiento_abs",
            ascending=False,
        ).head(15).reset_index(drop=True)

        if ranking_abs_df.empty:
            st.info(f"No hay datos de crecimiento disponibles para {section_title.lower()}.")
            return

        show_platform_legend = ranking_df["plataforma"].nunique() > 1
        fig_growth = px.bar(
            ranking_abs_df,
            x="entidad",
            y="crecimiento_abs",
            color="plataforma",
            title=f"🚀 {section_title}<br><sup style=\"font-size:12px;\">{subtitle}</sup>",
            labels={
                "crecimiento_abs": "📈 Crecimiento de Seguidores",
                "entidad": "🏫 Institución",
                "plataforma": "📱 Plataforma",
            },
            color_discrete_map=COLOR_MAP,
            text="crecimiento_abs",
            custom_data=["crecimiento_pct", "seguidores_anterior", "seguidores_mas_reciente", "score_hibrido"],
        )

        fig_growth.update_layout(
            height=600,
            xaxis_title="",
            yaxis_title="Crecimiento de Seguidores",
            legend_title="Plataforma Social",
            showlegend=show_platform_legend,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#2c3e50"),
            title_font=dict(size=20, color="#2c3e50", family="Arial Black"),
            title_x=0.5,
            title_y=0.95,
        )

        fig_growth.update_traces(
            texttemplate="<b>%{text:,}</b>",
            textposition="outside",
            textfont_size=11,
            textfont_color="#2c3e50",
            marker_line_width=1,
            marker_line_color="rgba(0,0,0,0.3)",
            hovertemplate="<b>%{x}</b><br>"
            + "📱 %{fullData.name}<br>"
            + "📈 Crecimiento abs: <b>%{y:,}</b> seguidores<br>"
            + "📊 Crecimiento %: <b>%{customdata[0]:.2f}%</b><br>"
            + "👥 Seguidores previos: %{customdata[1]:,.0f}<br>"
            + "👥 Seguidores actuales: %{customdata[2]:,.0f}<br>"
            + "🎯 Score híbrido: %{customdata[3]:.2f}<br>"
            + "<extra></extra>",
        )

        fig_growth.update_xaxes(
            tickangle=45,
            tickfont=dict(size=10, color="#34495e"),
            showgrid=False,
        )

        fig_growth.update_yaxes(
            tickfont=dict(size=10, color="#34495e"),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
        )

        st.plotly_chart(
            fig_growth,
            width="stretch",
            config=PLOTLY_CONFIG,
        )

        st.markdown("##### 📊 Ranking por % de crecimiento")
        try:
            ranking_pct_df = ranking_df.copy()
            ranking_pct_df["crecimiento_pct_plot"] = pd.to_numeric(
                ranking_pct_df["crecimiento_pct"],
                errors="coerce",
            ).fillna(0)
            ranking_pct_df = ranking_pct_df.sort_values(
                "crecimiento_pct_plot",
                ascending=False,
            ).head(15).reset_index(drop=True)

            fig_growth_pct = px.bar(
                ranking_pct_df,
                x="entidad",
                y="crecimiento_pct_plot",
                color="plataforma",
                title=f"📊 % de Crecimiento por Institución<br><sup style=\"font-size:12px;\">{subtitle}</sup>",
                labels={
                    "crecimiento_pct_plot": "% Crecimiento",
                    "entidad": "🏫 Institución",
                    "plataforma": "📱 Plataforma",
                },
                color_discrete_map=COLOR_MAP,
                text="crecimiento_pct_plot",
                custom_data=["crecimiento_abs", "seguidores_anterior", "seguidores_mas_reciente", "score_hibrido"],
            )

            fig_growth_pct.update_layout(
                height=600,
                xaxis_title="",
                yaxis_title="Crecimiento porcentual (%)",
                legend_title="Plataforma Social",
                showlegend=show_platform_legend,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=12, color="#2c3e50"),
                title_font=dict(size=20, color="#2c3e50", family="Arial Black"),
                title_x=0.5,
                title_y=0.95,
            )

            fig_growth_pct.update_traces(
                texttemplate="<b>%{text:.2f}%</b>",
                textposition="outside",
                textfont_size=11,
                textfont_color="#2c3e50",
                marker_line_width=1,
                marker_line_color="rgba(0,0,0,0.3)",
                hovertemplate="<b>%{x}</b><br>"
                + "📱 %{fullData.name}<br>"
                + "📊 Crecimiento %: <b>%{y:.2f}%</b><br>"
                + "📈 Crecimiento abs: <b>%{customdata[0]:,}</b> seguidores<br>"
                + "👥 Seguidores previos: %{customdata[1]:,.0f}<br>"
                + "👥 Seguidores actuales: %{customdata[2]:,.0f}<br>"
                + "🎯 Score híbrido: %{customdata[3]:.2f}<br>"
                + "<extra></extra>",
            )

            fig_growth_pct.update_xaxes(
                tickangle=45,
                tickfont=dict(size=10, color="#34495e"),
                showgrid=False,
            )

            fig_growth_pct.update_yaxes(
                tickfont=dict(size=10, color="#34495e"),
                showgrid=True,
                gridcolor="rgba(0,0,0,0.1)",
            )

            st.plotly_chart(
                fig_growth_pct,
                width="stretch",
                config=PLOTLY_CONFIG,
            )
        except Exception as pct_error:
            st.error(f"No se pudo renderizar la gráfica de % crecimiento: {pct_error}")

        leader_row = ranking_abs_df.iloc[0]
        total_growth = ranking_abs_df["crecimiento_abs"].sum()
        avg_pct = ranking_abs_df["crecimiento_pct"].fillna(0).mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🏆 Mayor Crecimiento",
                leader_row["entidad"],
                f"+{leader_row['crecimiento_abs']:,}",
            )
        with col2:
            if show_platform_legend:
                platform_totals = ranking_abs_df.groupby("plataforma")["crecimiento_abs"].sum()
                st.metric(
                    "📱 Plataforma Líder",
                    platform_totals.idxmax(),
                    f"{platform_totals.max():,}",
                )
            else:
                st.metric(
                    "📱 Plataforma",
                    ranking_abs_df.iloc[0]["plataforma"],
                    f"{len(ranking_abs_df)} instituciones",
                )
        with col3:
            st.metric(
                "📊 Total Crecimiento",
                f"{total_growth:,}",
                f"Promedio {avg_pct:.2f}%",
            )

    try:
        full_top_n = max(15, int(len(df_full)))
        growth_df = build_followers_growth_ranking(
            df_full,
            mode=growth_mode,
            top_n=full_top_n,
        )

        platform_names = sorted(
            {
                str(platform).strip()
                for platform in df_full.get("plataforma", pd.Series(dtype="object")).dropna().unique()
                if str(platform).strip()
            }
        )
        platform_rankings = []

        for platform_name in platform_names:
            platform_source_df = df_full[df_full["plataforma"].astype(str).str.strip() == platform_name]
            platform_top_n = max(15, int(len(platform_source_df)))
            platform_growth_df = build_followers_growth_ranking(
                platform_source_df,
                mode=growth_mode,
                top_n=platform_top_n,
            )
            if not platform_growth_df.empty:
                platform_rankings.append((platform_name, platform_growth_df))

        if platform_rankings or not growth_df.empty:
            subtitle = (
                "Último mes vs mes anterior"
                if growth_mode == "monthly"
                else "Entre las últimas 2 mediciones"
            )

            tab_labels = [f"{platform_name} Top 15" for platform_name, _ in platform_rankings]
            if not growth_df.empty:
                tab_labels.append("General")

            if len(tab_labels) == 1:
                if platform_rankings:
                    platform_name, platform_growth_df = platform_rankings[0]
                    render_growth_ranking_section(
                        f"Top 15 {platform_name}",
                        platform_growth_df,
                        subtitle,
                    )
                else:
                    render_growth_ranking_section(
                        "Top 15 General",
                        growth_df,
                        subtitle,
                    )
            else:
                growth_tabs = st.tabs(tab_labels)

                for tab, (platform_name, platform_growth_df) in zip(growth_tabs, platform_rankings):
                    with tab:
                        render_growth_ranking_section(
                            f"Top 15 {platform_name}",
                            platform_growth_df,
                            subtitle,
                        )

                if not growth_df.empty:
                    with growth_tabs[-1]:
                        render_growth_ranking_section(
                            "Top 15 General",
                            growth_df,
                            subtitle,
                        )

            st.caption("Se excluyen incrementos extremos con base previa muy baja para reducir falsos positivos.")
        else:
            st.info("No hay datos de crecimiento de seguidores disponibles.")

    except Exception as e:
        st.error(f"Error al calcular ranking de crecimiento: {str(e)}")
        logging.error(f"Error en ranking de crecimiento: {e}")

    # --- Evolución de la Salud Digital (últimos 6 meses) ---
    health_placeholder = st.empty()
    
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

        if not labels or not health_points:
            health_placeholder.empty()
            st.warning("No hay datos suficientes para gráfica de salud digital.")
        else:
            with health_placeholder.container():
                show_chart_skeleton(height=300)
            
            if px is None:
                health_placeholder.empty()
                st.error("Plotly no está disponible. Instala `plotly` para ver gráficos.")
            else:
                fig_health = px.line(x=labels, y=health_points, markers=True, labels={"x": "Mes", "y": "Salud"}, title="Evolución de la Salud Digital (últimos 6 meses)")
                fig_health.update_traces(line=dict(color="#0056B3", width=3))  # Azul info WCAG AA
                fig_health.update_layout(
                    autosize=True,
                    font={"color": "#000000"},
                    title_font={"color": "#000000"},
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    hoverlabel={"font": {"color": "#000000"}, "bgcolor": "#FFFFFF", "bordercolor": "#003696"},
                    xaxis={
                        "color": "#000000",
                        "gridcolor": "#E0E0E0",
                        "title": {"font": {"color": "#000000"}},
                        "tickfont": {"color": "#000000"},
                    },
                    yaxis={
                        "range": [0, 100],
                        "color": "#000000",
                        "gridcolor": "#E0E0E0",
                        "title": {"font": {"color": "#000000"}},
                        "tickfont": {"color": "#000000"},
                    },
                )
                health_placeholder.empty()  # Remover skeleton
                st.plotly_chart(fig_health, width='stretch', config=PLOTLY_CONFIG)
    except Exception as e:
        health_placeholder.empty()
        logging.error(f"Error al generar gráfica de salud digital: {e}")
        st.warning(f"No se pudo generar la serie histórica de salud: {str(e)}")

    # Vista de datos plegable con paginación
    with st.expander("Ver datos fuente"):
        df_paginated, total_pages = paginate_dataframe(
            df_full.sort_values(["entidad", "plataforma"]),
            page_size=500,  # 500 filas por página para buen rendimiento
            page_key="dashboard_data_page"
        )

        if total_pages and total_pages > 1:
            st.caption(f"📄 Mostrando página de datos (total: {len(df_full):,} filas)")

        st.dataframe(df_paginated, width='stretch')
    
    # Debug merge al final como menú desplegable
    if 'debug_merge_info' in st.session_state and st.session_state.debug_merge_info:
        with st.expander("🔍 DEBUG MERGE - Diagnóstico de Fusión de Datos"):
            info = st.session_state.debug_merge_info
            st.write(f"**IDs en Métricas:** {info['ids_metricas']}")
            st.write(f"**IDs en Cuentas:** {info['ids_cuentas']}")
            st.write(f"**IDs que coinciden:** {info['coinciden']}")
            st.write(f"**IDs solo en Métricas:** {info['solo_metricas']}")
            st.write(f"**IDs solo en Cuentas:** {info['solo_cuentas']}")
            if info['ejemplos_huerfanos']:
                st.write(f"**Ejemplos de IDs huérfanos en Métricas:** {info['ejemplos_huerfanos']}")

    # Detectar duplicados para transparencia al final del dashboard
    duplicados = df_m_month[df_m_month.duplicated(subset=['entidad', 'plataforma'], keep=False)]

    if not duplicados.empty:
        num_dupes = duplicados['entidad'].nunique()
        st.warning(
            f"⚠️ **Atención:** Se detectaron registros duplicados para {num_dupes} cuentas en este periodo.\n"
            "El Dashboard está usando automáticamente el dato más reciente para evitar sumas incorrectas."
        )
        with st.expander("Ver cuentas duplicadas (Causa de discrepancia con Excel)"):
            st.dataframe(
                duplicados.sort_values(['entidad', 'plataforma', 'fecha'])
                [['fecha', 'entidad', 'plataforma', 'seguidores']]
            )

