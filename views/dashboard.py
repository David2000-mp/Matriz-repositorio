"""
Vista Dashboard Global para CHAMPILYTICS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import (
    load_data,
    simular,
    save_batch,
    reset_db,
    generar_reporte_html,
    COLEGIOS_MARISTAS,
)
from utils.data_manager import load_configs
from components import COLOR_MAP, inject_custom_css
from utils.analytics import calculate_growth_metrics, calculate_health_score, apply_moving_average


def render(df=None):
    # Inyectar estilos globales desde components
    inject_custom_css()

    st.title("Dashboard Global")

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

        # Aplicar suavizado (promedio móvil 3M) sobre seguidores e interacciones
        try:
            df_full = apply_moving_average(df_full, col="seguidores")
            if "interacciones" in df_full.columns:
                df_full = apply_moving_average(df_full, col="interacciones")
        except Exception as e:
            logging.warning(f"No se pudo aplicar moving average: {e}")

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

        # DataFrame reducido al mes seleccionado (para KPIs y ranking). NO se usa
        # para calcular la salud ni las series históricas.
        df_m_month = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes].copy()  # type: ignore

    # Botón de descarga del reporte HTML usando utils.generar_reporte_html
    try:
        report_html = generar_reporte_html(df_m_month, f"Reporte {mes}")
        st.download_button(
            "Descargar Reporte HTML",
            report_html,
            file_name=f"Reporte_{mes}.html",
            mime="text/html",
        )
    except Exception as e:
        logging.warning(f"No se pudo generar el reporte HTML: {e}")
        st.info("No se pudo generar el reporte HTML para descarga. Puedes intentar de nuevo más tarde.")

    # --- Resumen Ejecutivo ---
    st.subheader("Resumen Ejecutivo")

    # KPIs principales (migradas desde legacy)
    # Evitar duplicados por merges erróneos: desduplicar por `id_cuenta` cuando exista.
    try:
        if "id_cuenta" in df_m_month.columns:
            seg_series = df_m_month.drop_duplicates(subset=["id_cuenta"])['seguidores']
            int_series = df_m_month.drop_duplicates(subset=["id_cuenta"])['interacciones']
        else:
            # Fallback: desduplicar por entidad+plataforma+fecha
            seg_series = df_m_month.drop_duplicates(subset=["entidad", "plataforma", "fecha"])['seguidores']
            int_series = df_m_month.drop_duplicates(subset=["entidad", "plataforma", "fecha"])['interacciones']
        tot_seg = int(seg_series.sum())
        tot_int = int(int_series.sum())
    except Exception:
        tot_seg = int(df_m_month['seguidores'].sum()) if 'seguidores' in df_m_month.columns else 0
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
            seg_prev = df_prev.drop_duplicates(subset=["id_cuenta"])['seguidores'].sum()
            int_prev = df_prev.drop_duplicates(subset=["id_cuenta"])['interacciones'].sum()
        else:
            seg_prev = df_prev.drop_duplicates(subset=["entidad", "plataforma", "fecha"])['seguidores'].sum()
            int_prev = df_prev.drop_duplicates(subset=["entidad", "plataforma", "fecha"])['interacciones'].sum()
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
            df_prev_year = df[df["fecha"].dt.strftime("%Y-%m") == prev_year_str]
            seg_prev_year = df_prev_year["seguidores"].sum() if not df_prev_year.empty else 0
            if seg_prev_year > 0:
                yoy_seg = (tot_seg - seg_prev_year) / seg_prev_year * 100.0
            else:
                yoy_seg = None
        except Exception:
            yoy_seg = None
    else:
        delta_seg = 0.0
        delta_int = 0.0
        delta_er = 0.0

    # Health score (calculate before rendering KPIs) — usar el histórico completo
    health_score = calculate_health_score(df_full)

    k1, k2, k3, k4 = st.columns(4)
    # Mostrar MoM y YoY juntos cuando estén disponibles
    if mes_anterior:
        if yoy_seg is not None:
            delta_display = f"{delta_seg:+.1f}% (YoY {yoy_seg:+.1f}%)"
        else:
            delta_display = f"{delta_seg:+.1f}%"
    else:
        delta_display = "-"

    k1.metric(
        "Seguidores",
        f"{tot_seg:,.0f}",
        delta=delta_display,
    )
    k2.metric(
        "Interacciones",
        f"{tot_int:,.0f}",
        delta=f"{delta_int:+.1f}%" if mes_anterior else "-",
    )
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

        st.plotly_chart(
            fig_area,
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )

        # Línea adicional: interacciones con tendencia suavizada
        try:
            if "interacciones" in df_full.columns:
                df_int = (
                    df_full.groupby(["fecha", "plataforma"])["interacciones"].sum().reset_index()
                )
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
                fig_int.update_layout(autosize=True)
                st.plotly_chart(
                    fig_int,
                    width="stretch",
                    config={"displayModeBar": False, "responsive": True},
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
        fig_bar = px.bar(
            resumen,
            x="seguidores",
            y="entidad",
            color="plataforma",
            orientation="h",
            color_discrete_map=COLOR_MAP,
            title=f"Ranking de Seguidores ({mes})",
            barmode="group",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(autosize=True)
        st.plotly_chart(
            fig_bar,
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
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
            fig_health = px.line(x=labels, y=health_points, markers=True, labels={"x": "Mes", "y": "Salud"}, title="Evolución de la Salud Digital (últimos 6 meses)")
            fig_health.update_traces(line=dict(color="#2b6cb0"))
            fig_health.update_layout(autosize=True, yaxis=dict(range=[0,100]))
            st.plotly_chart(fig_health, width="stretch", config={"displayModeBar": False, "responsive": True})
    except Exception as e:
        logging.warning(f"No se pudo generar la serie histórica de salud: {e}")

    # Vista de datos plegable
    with st.expander("Ver datos fuente"):
        st.dataframe(
            df_full.sort_values(["entidad", "plataforma"]), width="stretch"
        )
