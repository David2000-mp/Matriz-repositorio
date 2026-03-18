"""
Calculadora de Engagement v2 - Herramienta Interactiva con Flujo Asistente
Arquitectura: Paso 1 (Datos Base) → Paso 2 (Publicaciones) → Paso 3 (Resultados + Reporte)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import logging
from utils.report_generator import generate_engagement_report_html
from utils.rules_engine import calculate_engagement_engine
from utils.content_analyzer import classify_school_content, identify_top_performer
from utils.smart_diagnosis import (
    build_recommendation_text,
    category_effectiveness,
    compute_volatility_guardrail,
)


# ============================================================================
# FUNCIONES AUXILIARES - VALIDACIÓN EN TIEMPO REAL
# ============================================================================

def get_engagement_thresholds(platform: str, metric_type: str = "comunidad") -> dict:
    """
    Retorna thresholds fijos de engagement según plataforma y tipo de métrica.
    Reglas oficiales actualizadas - Thresholds fijos, no dinámicos.
    
    Args:
        platform: 'facebook' o 'tiktok'
        metric_type: 'comunidad' (engagement general/por post) o 'vistas' (solo TikTok)
    """
    if platform == "facebook":
        return {
            "bajo": 0.5,
            "aceptable": 1.0,
            "bueno": 2.0,
            "labels": {
                "bajo": "< 0.5% → Bajo",
                "aceptable": "0.5% - 1% → Aceptable",
                "bueno": "1% - 2% → Bueno",
                "alto": "> 2% → Alto"
            }
        }
    elif platform == "instagram":
        return {
            "bajo": 1.0,
            "aceptable": 3.0,
            "bueno": 6.0,
            "labels": {
                "bajo": "< 1% → Bajo",
                "aceptable": "1% - 3% → Aceptable",
                "bueno": "3% - 6% → Bueno",
                "alto": "> 6% → Alto"
            }
        }
    elif platform == "tiktok":
        if metric_type == "vistas":
            return {
                "bajo": 1.0,
                "aceptable": 3.0,
                "bueno": 6.0,
                "labels": {
                    "bajo": "< 1% → Bajo",
                    "aceptable": "1% - 3% → Aceptable",
                    "bueno": "3% - 6% → Bueno",
                    "alto": "> 6% → Alto"
                }
            }
        else:  # comunidad
            return {
                "bajo": 3.0,
                "promedio": 6.0,
                "bueno": 10.0,
                "labels": {
                    "bajo": "< 3% → Bajo",
                    "promedio": "3% - 6% → Promedio",
                    "bueno": "6% - 10% → Bueno",
                    "alto": "> 10% → Alto"
                }
            }
    return {}


def calculate_expected_engagement(followers: int) -> dict:
    """
    Calcula el engagement esperado para una cantidad de seguidores.
    Basado en benchmarks de industria (promedios reales).
    
    Retorna dict con:
    - typical: engagement típico en %
    - min: mínimo esperado
    - max: máximo esperado
    """
    if followers < 1000:
        return {"typical": 8.0, "min": 5.0, "max": 15.0}
    elif followers < 5000:
        return {"typical": 6.0, "min": 3.0, "max": 12.0}
    elif followers < 10000:
        return {"typical": 4.5, "min": 2.0, "max": 10.0}
    elif followers < 50000:
        return {"typical": 3.5, "min": 1.5, "max": 8.0}
    elif followers < 100000:
        return {"typical": 2.5, "min": 1.0, "max": 6.0}
    elif followers < 500000:
        return {"typical": 1.8, "min": 0.8, "max": 4.0}
    else:
        return {"typical": 1.0, "min": 0.4, "max": 2.5}


def validate_post_engagement(reactions: int, comments: int, shares: int, followers: int) -> dict:
    """
    Valida engagement de un post individual.
    Retorna estado (green/yellow/red) y mensaje explicativo.
    """
    total = reactions + comments + shares
    
    if total == 0:
        return {
            "status": "empty",
            "color": "#95A5A6",
            "icon": "⚪",
            "message": "Sin datos aún",
            "engagement_pct": 0
        }
    
    engagement_pct = (total / followers * 100) if followers > 0 else 0
    expected = calculate_expected_engagement(followers)
    
    # Sanity check: engagement no puede ser > 100% de seguidores
    if total > followers * 5:
        return {
            "status": "red",
            "color": "#B42318",
            "icon": "🔴",
            "message": f"⚠️ Datos sospechosos: {engagement_pct:.1f}% es muy alto",
            "engagement_pct": engagement_pct
        }
    
    # Comparar con expected
    if engagement_pct >= expected["typical"] * 1.5:
        return {
            "status": "green",
            "color": "#0A7D35",
            "icon": "🟢",
            "message": f"Excelente: {engagement_pct:.1f}% (esperado: {expected['typical']:.1f}%)",
            "engagement_pct": engagement_pct
        }
    elif engagement_pct >= expected["typical"] * 0.7:
        return {
            "status": "yellow",
            "color": "#CC7000",
            "icon": "🟡",
            "message": f"Normal: {engagement_pct:.1f}% (esperado: {expected['typical']:.1f}%)",
            "engagement_pct": engagement_pct
        }
    else:
        return {
            "status": "red",
            "color": "#B42318",
            "icon": "🔴",
            "message": f"Bajo: {engagement_pct:.1f}% (esperado: {expected['typical']:.1f}%)",
            "engagement_pct": engagement_pct
        }


def calculate_growth_potential(current_engagement: float, current_followers: int, platform: str) -> dict:
    """
    Calcula potencial de crecimiento si se mejora engagement.
    Basado en relación engagement-seguidores.
    """
    # Factor de conversión: cuántos nuevos seguidores por punto de engagement
    conversion_factors = {
        "facebook": 50,  # 1% de engagement = ~50 nuevos seguidores/mes
        "tiktok": 75,    # TikTok tiene más viralidad
    }
    
    factor = conversion_factors.get(platform.lower(), 40)
    
    scenarios = {}
    for improvement in [10, 20, 30]:  # Mejorar 10%, 20%, 30%
        new_engagement = current_engagement + improvement
        monthly_growth = (new_engagement / 100) * current_followers * factor / 100
        growth_3months = monthly_growth * 3
        
        scenarios[improvement] = {
            "new_engagement": new_engagement,
            "monthly_followers": int(monthly_growth),
            "followers_3m": int(current_followers + growth_3months),
            "growth_pct": (growth_3months / current_followers * 100) if current_followers > 0 else 0
        }
    
    return scenarios


def _build_default_posts_grid(platform: str) -> pd.DataFrame:
    """Construye la rejilla inicial de 15 posts para captura agil."""
    content_types = ["📸 Imagen", "🎥 Video", "📝 Texto", "🔗 Link"]
    categories = [
        "Admisiones",
        "Eventos",
        "Vida Estudiantil",
        "Academico",
        "Pastoral",
        "Deportes",
        "Institucional",
        "Venta",
        "Otro",
    ]

    default_type = "🎥 Video" if platform == "tiktok" else "📸 Imagen"
    rows = []
    for i in range(1, 16):
        rows.append(
            {
                "Post #": i,
                "Fecha Publicacion": None,
                "Categoria": categories[0],
                "Tipo": default_type if default_type in content_types else content_types[0],
                "URL/Link": "",
                "Comentario": "",
                "Reacciones": 0,
                "Me gusta": 0,
                "Comentarios": 0,
                "Compartidos": 0,
                "Vistas": 0,
                "Interacciones": 0,
                "Estado": "⚪ Sin datos",
            }
        )

    return pd.DataFrame(rows)


def _ensure_posts_grid(platform: str) -> pd.DataFrame:
    """Inicializa o reutiliza la rejilla en session_state segun plataforma."""
    key = "wizard_posts_grid"
    platform_key = "wizard_posts_grid_platform"

    if key not in st.session_state or st.session_state.get(platform_key) != platform:
        st.session_state[key] = _build_default_posts_grid(platform)
        st.session_state[platform_key] = platform

    return st.session_state[key].copy()


def _post_total_from_row(row: pd.Series, platform: str) -> int:
    """Calcula interacciones por fila segun plataforma."""
    result = calculate_engagement_engine(
        platform,
        {
            "Reacciones": row.get("Reacciones", 0),
            "Me gusta": row.get("Me gusta", 0),
            "Comentarios": row.get("Comentarios", 0),
            "Compartidos": row.get("Compartidos", 0),
            "Interacciones": row.get("Interacciones", 0),
        },
    )
    return int(result.total_interactions)


def _row_validation(row: pd.Series, platform: str, followers: int) -> dict:
    """Valida el rendimiento de una fila usando reglas actuales."""
    result = calculate_engagement_engine(
        platform,
        {
            "Reacciones": row.get("Reacciones", 0),
            "Me gusta": row.get("Me gusta", 0),
            "Comentarios": row.get("Comentarios", 0),
            "Compartidos": row.get("Compartidos", 0),
            "Interacciones": row.get("Interacciones", 0),
            "followers": followers,
        },
    )
    return validate_post_engagement(result.total_interactions, 0, 0, followers)


def _sanitize_and_score_posts_df(posts_df: pd.DataFrame, platform: str, followers: int) -> tuple[pd.DataFrame, list[dict]]:
    """Normaliza la rejilla y calcula interacciones/estado por fila."""
    work_df = posts_df.copy()

    text_columns = ["Categoria", "Tipo", "URL/Link", "Comentario"]
    for col in text_columns:
        if col in work_df.columns:
            work_df[col] = work_df[col].fillna("").astype(str)

    numeric_columns = ["Reacciones", "Me gusta", "Comentarios", "Compartidos", "Vistas", "Interacciones"]
    for col in numeric_columns:
        if col in work_df.columns:
            work_df[col] = pd.to_numeric(work_df[col], errors="coerce").fillna(0).astype(int)

    posts_data = []
    for idx in work_df.index:
        row = work_df.loc[idx]
        row_result = calculate_engagement_engine(
            platform,
            {
                "Reacciones": row.get("Reacciones", 0),
                "Me gusta": row.get("Me gusta", 0),
                "Comentarios": row.get("Comentarios", 0),
                "Compartidos": row.get("Compartidos", 0),
                "Interacciones": row.get("Interacciones", 0),
                "followers": followers,
                "views": row.get("Vistas", 0),
            },
        )
        total = int(row_result.total_interactions)
        validation = validate_post_engagement(total, 0, 0, followers)
        work_df.at[idx, "Interacciones"] = int(total)
        if row_result.analysis_mode == "views_only":
            work_df.at[idx, "Estado"] = "📺 reach"
            status = "reach"
        else:
            work_df.at[idx, "Estado"] = f"{validation['icon']} {validation['status']}"
            status = validation["status"]

        posts_data.append(
            {
                "post_num": int(row.get("Post #", 0) or 0),
                "type": row.get("Tipo", "📸 Imagen"),
                "total": int(total),
                "status": status,
                "analysis_mode": row_result.analysis_mode,
                "views": int(row.get("Vistas", 0) or 0),
                "fecha": row.get("Fecha Publicacion"),
            }
        )

    return work_df, posts_data


def _sync_grid_to_legacy_state(posts_df: pd.DataFrame, platform: str):
    """Mantiene compatibilidad con llaves wizard_post_* del flujo anterior."""
    for _, row in posts_df.iterrows():
        post_num = int(row["Post #"])
        st.session_state[f"wizard_post_{post_num}_type"] = row.get("Tipo", "📸 Imagen")
        st.session_state[f"wizard_post_{post_num}_interactions"] = int(row.get("Interacciones", 0) or 0)
        st.session_state[f"wizard_post_{post_num}_comments"] = int(row.get("Comentarios", 0) or 0)
        st.session_state[f"wizard_post_{post_num}_shares"] = int(row.get("Compartidos", 0) or 0)
        if platform == "facebook":
            st.session_state[f"wizard_post_{post_num}_reactions"] = int(row.get("Reacciones", 0) or 0)
        elif platform == "instagram":
            st.session_state[f"wizard_post_{post_num}_likes"] = int(row.get("Me gusta", 0) or 0)
            st.session_state[f"wizard_post_{post_num}_shares"] = int(row.get("Compartidos", 0) or 0)
        else:
            st.session_state[f"wizard_post_{post_num}_likes"] = int(row.get("Me gusta", 0) or 0)
            st.session_state[f"wizard_post_{post_num}_views"] = int(row.get("Vistas", 0) or 0)


# ============================================================================
# PASO 1: DATOS BASE
# ============================================================================

def render_step_1_basic_data():
    """Paso 1 del asistente: Recopilar datos básicos."""
    
    st.divider()
    st.markdown("## Paso 1: Datos Básicos")
    st.markdown("Cuéntanos sobre tu cuenta para comenzar el análisis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        platform_options = ["facebook", "instagram", "tiktok"]
        platform_display = ["📘 Facebook", "📸 Instagram", "🎵 TikTok"]
        
        platform_index = st.selectbox(
            "¿Qué plataforma analizarás?",
            range(len(platform_options)),
            format_func=lambda x: platform_display[x],
            key="wizard_platform_idx",
            help="Selecciona la red social donde deseas analizar engagement"
        )
        platform_clean = platform_options[platform_index]
        st.session_state["wizard_platform"] = platform_clean
    
    with col2:
        st.markdown("### Información de tu cuenta")
        followers = st.number_input(
            "¿Cuántas personas te siguen?",
            min_value=1,
            value=st.session_state.get("wizard_followers", 2500),
            step=100,
            key="wizard_followers",
            help="Número total de seguidores actuales. Ejemplo: 2.500"
        )
        
        days = st.number_input(
            "Período de análisis (días)",
            min_value=1,
            max_value=365,
            value=st.session_state.get("wizard_days", 30),
            key="wizard_days",
            help="¿Cuántos días de publicaciones vas a analizar? Recomendado: 30"
        )
    
    # Mostrar estimación de publicaciones
    expected_posts = int((st.session_state.get("wizard_posts_count", 15)))
    platform_label_map = {
        "facebook": "Facebook",
        "instagram": "Instagram",
        "tiktok": "TikTok",
    }
    platform_label = platform_label_map.get(platform_clean, platform_clean.title())
    st.info(
        f"📊 **Resumen:** Analizarás **{expected_posts} publicaciones** de **{platform_label}** "
        f"en los últimos **{days} días** con **{followers:,} seguidores**.",
        icon="📋"
    )
    
    if st.button("Continuar al Paso 2 →", use_container_width=True, type="primary"):
        st.session_state["wizard_step"] = 2
        st.rerun()


# ============================================================================
# PASO 2: INGRESO DE PUBLICACIONES
# ============================================================================

def render_step_2_posts():
    """Paso 2 del asistente: Captura agil en rejilla editable con dimension temporal."""
    
    st.divider()
    st.markdown("## Paso 2: Tus Publicaciones")
    st.markdown(f"Ingresa datos de tus últimas **15 publicaciones** en {st.session_state.get('wizard_platform', 'Facebook').upper()}")
    
    platform = st.session_state.get("wizard_platform", "facebook")
    followers = st.session_state.get("wizard_followers", 2500)
    
    # Instrucciones
    with st.expander("💡 ¿Cómo llenar esto?", expanded=True):
        if platform == "facebook":
            st.markdown("""
            **Para cada publicación:**
            - **Reacciones:** Número de reacciones (Me gusta, Me encanta, etc.)
            - **Comentarios:** Comentarios en el post
            - **Compartidos:** Veces que fue compartido
            - **Tipo:** Qué tipo de contenido (Imagen, Video, etc.)
            
            **Dónde encontrar esto en Facebook:**
            1. Abre tu página → Insights → Posts
            2. Haz clic en cada post para ver reacciones, comentarios, shares
            3. Llena los datos aquí
            """)
        elif platform == "instagram":
            st.markdown("""
            **Para cada publicación de Instagram:**
            - **Me gusta:** Número de likes
            - **Comentarios:** Comentarios del post
            - **Compartidos:** Opcional (si se dispone)
            - **Tipo:** Qué tipo de contenido
            """)
        else:  # tiktok
            st.markdown("""
            **Para cada video:**
            - **Vistas:** Número total de vistas
            - **Me gusta:** Número de likes
            - **Comentarios:** Comentarios en el video
            - **Compartidos:** Veces que fue compartido
            - **Guardados:** Números de guardados en favoritos
            - **Tipo:** Qué tipo de contenido
            
            **Dónde encontrar esto en TikTok:**
            1. Abre tu perfil → Videos
            2. Haz clic en cada video (los números aparecen debajo)
            3. Llena los datos aquí
            """)
    
    content_types = ["📸 Imagen", "🎥 Video", "📝 Texto", "🔗 Link"]
    categories = [
        "Admisiones",
        "Eventos",
        "Vida Estudiantil",
        "Academico",
        "Pastoral",
        "Deportes",
        "Institucional",
        "Venta",
        "Otro",
    ]

    st.caption("Tip: Puedes navegar celda por celda con Tab y pegar datos desde Excel.")

    posts_df = _ensure_posts_grid(platform)

    if platform == "facebook":
        visible_columns = [
            "Post #",
            "Comentarios",
            "Compartidos",
            "Reacciones",
            "Interacciones",
            "Estado",
            "Fecha Publicacion",
            "Categoria",
            "Tipo",
            "URL/Link",
            "Comentario",
        ]
    elif platform == "instagram":
        visible_columns = [
            "Post #",
            "Comentarios",
            "Me gusta",
            "Compartidos",
            "Interacciones",
            "Estado",
            "Fecha Publicacion",
            "Categoria",
            "Tipo",
            "URL/Link",
            "Comentario",
        ]
    else:
        visible_columns = [
            "Post #",
            "Comentarios",
            "Compartidos",
            "Me gusta",
            "Vistas",
            "Interacciones",
            "Estado",
            "Fecha Publicacion",
            "Categoria",
            "Tipo",
            "URL/Link",
            "Comentario",
        ]

    # El formulario agrupa la rejilla y el botón "Calcular".
    # Al usar st.form, los cambios de celda NO disparan re-runs intermedios,
    # evitando el hash-reset del data_editor que borraba los datos ingresados.
    with st.form("wizard_posts_form", clear_on_submit=False):
        edited_df = st.data_editor(
            posts_df[visible_columns],
            use_container_width=True,
            hide_index=True,
            height=520,
            num_rows="fixed",
            key="wizard_posts_grid_editor",
            column_config={
                "Post #": st.column_config.NumberColumn("Post #", min_value=1, step=1, disabled=True),
                "Fecha Publicacion": st.column_config.DateColumn("Fecha Publicacion", format="YYYY-MM-DD"),
                "Categoria": st.column_config.SelectboxColumn("Categoria", options=categories),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=content_types),
                "URL/Link": st.column_config.TextColumn("URL/Link", width="medium"),
                "Comentario": st.column_config.TextColumn("Comentario", width="large"),
                "Reacciones": st.column_config.NumberColumn("Reacciones", min_value=0, step=1),
                "Me gusta": st.column_config.NumberColumn("Me gusta", min_value=0, step=1),
                "Comentarios": st.column_config.NumberColumn("Comentarios", min_value=0, step=1),
                "Compartidos": st.column_config.NumberColumn("Compartidos", min_value=0, step=1),
                "Vistas": st.column_config.NumberColumn("Vistas", min_value=0, step=1),
                "Interacciones": st.column_config.NumberColumn("Interacciones", min_value=0, step=1),
                "Estado": st.column_config.TextColumn("Estado", disabled=True),
            },
            disabled=["Post #", "Estado"],
        )
        st.markdown("")
        _, _, submit_col = st.columns([1, 1, 1])
        with submit_col:
            submitted = st.form_submit_button(
                "Calcular Resultados →",
                use_container_width=True,
                type="primary",
            )

    if submitted:
        posts_df.loc[:, visible_columns] = edited_df
        posts_df, posts_data = _sanitize_and_score_posts_df(posts_df, platform, followers)
        st.session_state["wizard_posts_grid"] = posts_df
        _sync_grid_to_legacy_state(posts_df, platform)

        if platform == "tiktok":
            captured_posts = len(
                [p for p in posts_data if p["total"] > 0 or (p.get("analysis_mode") == "views_only" and p.get("views", 0) > 0)]
            )
        else:
            captured_posts = len([p for p in posts_data if p["total"] > 0])

        valid_dates = pd.to_datetime(posts_df["Fecha Publicacion"], errors="coerce").dropna()
        if not valid_dates.empty:
            period_start = valid_dates.min().date()
            period_end = valid_dates.max().date()
            period_days = max((period_end - period_start).days + 1, 1)
        else:
            period_days = int(st.session_state.get("wizard_days", 30))
            period_end = datetime.now().date()
            period_start = period_end - pd.Timedelta(days=max(period_days - 1, 0))

        st.session_state["wizard_period_start"] = str(period_start)
        st.session_state["wizard_period_end"] = str(period_end)
        st.session_state["wizard_days"] = int(period_days)
        st.session_state["wizard_posts_count"] = int(captured_posts)

        if captured_posts <= 0:
            if platform == "tiktok":
                st.warning("Captura al menos un post con interacciones o vistas antes de calcular.")
            else:
                st.warning("Captura al menos un post con interacciones antes de calcular.")
        else:
            st.session_state["wizard_step"] = 3
            st.rerun()

    st.divider()

    # Resumen basado en los datos del último guardado (session_state)
    saved_grid = st.session_state.get("wizard_posts_grid", posts_df)
    _, posts_data = _sanitize_and_score_posts_df(saved_grid.copy(), platform, followers)
    green_posts = len([p for p in posts_data if p["status"] == "green"])
    yellow_posts = len([p for p in posts_data if p["status"] == "yellow"])
    red_posts = len([p for p in posts_data if p["status"] == "red"])

    summary_col1, summary_col2, summary_col3 = st.columns(3)
    with summary_col1:
        st.metric("🟢 Excelentes", green_posts)
    with summary_col2:
        st.metric("🟡 Normales", yellow_posts)
    with summary_col3:
        st.metric("🔴 Bajos", red_posts)

    if platform == "tiktok":
        reach_posts = len([p for p in posts_data if p.get("analysis_mode") == "views_only"])
        if reach_posts > 0:
            st.caption(f"📺 {reach_posts} post(s) en modo reach (vistas sin interacciones).")

    period_start_disp = st.session_state.get("wizard_period_start", str(datetime.now().date()))
    period_end_disp = st.session_state.get("wizard_period_end", str(datetime.now().date()))
    period_days_disp = int(st.session_state.get("wizard_days", 30))
    captured_posts_disp = int(st.session_state.get("wizard_posts_count", 0))
    posting_frequency_disp = (captured_posts_disp / period_days_disp) * 7 if period_days_disp > 0 else 0
    if captured_posts_disp > 0:
        st.info(
            f"Periodo analizado: **{period_start_disp}** al **{period_end_disp}** "
            f"(**{period_days_disp} dias**) - Total capturado: **{captured_posts_disp} posts** "
            f"- Frecuencia: **{posting_frequency_disp:.2f} posts/semana**",
            icon="📅",
        )

    if st.button("← Volver al Paso 1", use_container_width=True):
        st.session_state["wizard_step"] = 1
        st.rerun()


# ============================================================================
# PASO 3: RESULTADOS Y ANÁLISIS
# ============================================================================

def calculate_and_render_results():
    """Paso 3: Calcular y mostrar resultados con análisis completo."""
    
    platform = st.session_state.get("wizard_platform", "facebook")
    followers = st.session_state.get("wizard_followers", 2500)
    days = int(st.session_state.get("wizard_days", 30))
    
    # Recopilar datos de publicaciones
    posts_list = []
    total_interactions = 0
    total_views = 0
    period_start = st.session_state.get("wizard_period_start")
    period_end = st.session_state.get("wizard_period_end")

    grid_df = st.session_state.get("wizard_posts_grid")
    if isinstance(grid_df, pd.DataFrame) and not grid_df.empty:
        for _, row in grid_df.sort_values("Post #").iterrows():
            post = {
                "num": int(row.get("Post #", 0)),
                "type": row.get("Tipo", "📸 Imagen"),
                "fecha": str(row.get("Fecha Publicacion") or ""),
                "categoria": row.get("Categoria", ""),
                "url": row.get("URL/Link", ""),
                "comentario": row.get("Comentario", ""),
            }

            comments = int(row.get("Comentarios", 0) or 0)
            shares = int(row.get("Compartidos", 0) or 0)

            if platform == "facebook":
                reactions = int(row.get("Reacciones", 0) or 0)
                post["reactions"] = reactions
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Reacciones": reactions,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": int(row.get("Interacciones", 0) or 0),
                        "followers": followers,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
            elif platform == "instagram":
                likes = int(row.get("Me gusta", 0) or 0)
                post["likes"] = likes
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Me gusta": likes,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": int(row.get("Interacciones", 0) or 0),
                        "followers": followers,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
            else:
                views = int(row.get("Vistas", 0) or 0)
                likes = int(row.get("Me gusta", 0) or 0)
                post["views"] = views
                post["likes"] = likes
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Me gusta": likes,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": int(row.get("Interacciones", 0) or 0),
                        "followers": followers,
                        "views": views,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
                total_views += views

            post["analysis_mode"] = post_result.analysis_mode
            post["analysis_mode_label"] = "Alcance" if post_result.analysis_mode == "views_only" else "Comunidad"
            total_interactions += post["total"]
            posts_list.append(post)
    else:
        for i in range(1, 16):
            post = {
                "num": i,
                "type": st.session_state.get(f"wizard_post_{i}_type", "📸 Imagen"),
            }

            if platform == "facebook":
                reactions = st.session_state.get(f"wizard_post_{i}_reactions", 0)
                comments = st.session_state.get(f"wizard_post_{i}_comments", 0)
                shares = st.session_state.get(f"wizard_post_{i}_shares", 0)
                post["reactions"] = reactions
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Reacciones": reactions,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": st.session_state.get(f"wizard_post_{i}_interactions", 0),
                        "followers": followers,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
            elif platform == "instagram":
                likes = st.session_state.get(f"wizard_post_{i}_likes", 0)
                comments = st.session_state.get(f"wizard_post_{i}_comments", 0)
                shares = st.session_state.get(f"wizard_post_{i}_shares", 0)
                post["likes"] = likes
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Me gusta": likes,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": st.session_state.get(f"wizard_post_{i}_interactions", 0),
                        "followers": followers,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
            else:
                views = st.session_state.get(f"wizard_post_{i}_views", 0)
                likes = st.session_state.get(f"wizard_post_{i}_likes", 0)
                comments = st.session_state.get(f"wizard_post_{i}_comments", 0)
                shares = st.session_state.get(f"wizard_post_{i}_shares", 0)
                post["views"] = views
                post["likes"] = likes
                post["comments"] = comments
                post["shares"] = shares
                post_result = calculate_engagement_engine(
                    platform,
                    {
                        "Me gusta": likes,
                        "Comentarios": comments,
                        "Compartidos": shares,
                        "Interacciones": st.session_state.get(f"wizard_post_{i}_interactions", 0),
                        "followers": followers,
                        "views": views,
                    },
                )
                post["total"] = post_result.total_interactions
                post["inconsistency"] = post_result.has_inconsistency
                total_views += views

            post["analysis_mode"] = post_result.analysis_mode
            post["analysis_mode_label"] = "Alcance" if post_result.analysis_mode == "views_only" else "Comunidad"
            total_interactions += post["total"]
            posts_list.append(post)

    community_posts = [p for p in posts_list if p.get("total", 0) > 0]
    reach_posts = [
        p
        for p in posts_list
        if p.get("analysis_mode") == "views_only" or (platform == "tiktok" and p.get("total", 0) == 0 and p.get("views", 0) > 0)
    ]

    if platform == "tiktok":
        analyzed_posts = community_posts + [p for p in reach_posts if p not in community_posts]
        if not analyzed_posts:
            st.error("⚠️ No hay datos para analizar. En TikTok necesitas interacciones o vistas.")
            if st.button("← Volver al Paso 2"):
                st.session_state["wizard_step"] = 2
                st.rerun()
            return

        if community_posts and reach_posts:
            analysis_mode = "hybrid"
        elif reach_posts and not community_posts:
            analysis_mode = "views_only"
        else:
            analysis_mode = "standard"
    else:
        analyzed_posts = community_posts
        analysis_mode = "standard"
        if not analyzed_posts:
            st.error("⚠️ No hay datos para analizar. Por favor completa al menos algunos posts.")
            if st.button("← Volver al Paso 2"):
                st.session_state["wizard_step"] = 2
                st.rerun()
            return
    
    # ========================================================================
    # CÁLCULOS PRINCIPALES
    # ========================================================================
    
    # Total de posts capturados con interacciones
    num_posts = len(analyzed_posts)

    # Derivar periodo real desde fechas validas cuando existan
    if not period_start or not period_end:
        valid_dates = []
        for post in analyzed_posts:
            parsed = pd.to_datetime(post.get("fecha", None), errors="coerce")
            if not pd.isna(parsed):
                valid_dates.append(parsed.date())
        if valid_dates:
            period_start = str(min(valid_dates))
            period_end = str(max(valid_dates))
            days = max((max(valid_dates) - min(valid_dates)).days + 1, 1)
    
    # Engagement general de la cuenta
    engagement_pct = (total_interactions / followers) * 100
    # Engagement por post (comunidad): (Promedio interacciones / Seguidores) * 100
    avg_interactions = total_interactions / max(num_posts, 1)
    engagement_per_post = (avg_interactions / followers) * 100
    
    # Posts por semana varía según el período de DÍAS que ingresa el usuario
    # Fórmula: (número de posts / días) * 7
    # Ej: 15 posts en 30 días = (15 / 30) * 7 = 3.5 posts/semana
    posts_per_week = (num_posts / max(days, 1)) * 7
    
    # Para TikTok
    if platform == "tiktok" and total_views > 0:
        engagement_by_views = (total_interactions / total_views) * 100
    else:
        engagement_by_views = 0
    
    # Segmentación por tipo de contenido (con estadísticas detalladas)
    content_stats = {}
    for post in analyzed_posts:
        ctype = post["type"]
        if ctype not in content_stats:
            content_stats[ctype] = {
                "total_interactions": 0, 
                "posts": 0, 
                "engagement": 0,
                "pct": 0,  # Porcentaje del total de posts
                "avg_engagement": 0  # Engagement promedio por post
            }
        
        content_stats[ctype]["total_interactions"] += post["total"]
        content_stats[ctype]["posts"] += 1
    
    # Calcular porcentajes y engagement promedio por tipo
    for ctype in content_stats:
        posts_count = content_stats[ctype]["posts"]
        content_stats[ctype]["pct"] = (posts_count / num_posts) * 100
        content_stats[ctype]["avg_engagement"] = (content_stats[ctype]["total_interactions"] / posts_count / followers) * 100
    # Diagnóstico basado en thresholds fijos por plataforma
    thresholds = get_engagement_thresholds(platform, "comunidad")
    
    if platform == "tiktok" and analysis_mode == "views_only":
        diagnosis = "📺 SOLO ALCANCE"
        diagnosis_color = "#CC7000"
        diagnosis_level = "views_only"
    elif platform in ["facebook", "instagram"]:
        if engagement_pct >= thresholds["bueno"]:
            diagnosis = "🟢 ALTO"
            diagnosis_color = "#0A7D35"
            diagnosis_level = "alto"
        elif engagement_pct >= thresholds["aceptable"]:
            diagnosis = "🟡 BUENO"
            diagnosis_color = "#003696"
            diagnosis_level = "bueno"
        elif engagement_pct >= thresholds["bajo"]:
            diagnosis = "⚠️ ACEPTABLE"
            diagnosis_color = "#CC7000"
            diagnosis_level = "aceptable"
        else:
            diagnosis = "🔴 BAJO"
            diagnosis_color = "#B42318"
            diagnosis_level = "bajo"
    else:  # TikTok
        if engagement_pct >= thresholds["bueno"]:
            diagnosis = "🟢 ALTO"
            diagnosis_color = "#0A7D35"
            diagnosis_level = "alto"
        elif engagement_pct >= thresholds["promedio"]:
            diagnosis = "🟡 BUENO"
            diagnosis_color = "#003696"
            diagnosis_level = "bueno"
        elif engagement_pct >= thresholds["bajo"]:
            diagnosis = "⚠️ PROMEDIO"
            diagnosis_color = "#CC7000"
            diagnosis_level = "promedio"
        else:
            diagnosis = "🔴 BAJO"
            diagnosis_color = "#B42318"
            diagnosis_level = "bajo"
    
    # Potencial de crecimiento
    growth_scenarios = calculate_growth_potential(engagement_pct, followers, platform)

    # Analizador de contenido: clasificacion y top performer
    analysis_df = pd.DataFrame(posts_list)
    classification = classify_school_content(analysis_df)
    ranked = identify_top_performer(
        classification["data"].assign(
            **{"ER Post": classification["data"].apply(lambda r: (r.get("total", 0) / followers * 100) if followers > 0 else 0.0, axis=1)}
        )
    )
    category_signal = category_effectiveness(classification["data"], followers=followers, min_samples=2)
    post_ers = [(p.get("total", 0) / followers * 100) if followers > 0 else 0.0 for p in analyzed_posts]
    volatility = compute_volatility_guardrail(post_ers)

    best_category_name = None
    if category_signal.get("has_signal") and category_signal.get("best_category"):
        best_category_name = str(category_signal["best_category"].get("categoria", "")).strip() or None

    narrative_recommendation = build_recommendation_text(
        actor_name=st.session_state.get("wizard_actor_name", "David"),
        diagnosis_level="bajo" if diagnosis_level == "views_only" else diagnosis_level,
        posts_per_week=posts_per_week,
        best_category=best_category_name,
        is_volatile=bool(volatility.get("is_volatile", False)),
    )
    
    # ========================================================================
    # RENDERIZAR RESULTADOS
    # ========================================================================
    
    st.divider()
    st.markdown(f"## Paso 3: Tus Resultados")

    if platform == "tiktok" and analysis_mode == "views_only":
        st.info(
            "📺 Modo Reach: hay alcance visual (vistas) pero baja accion de comunidad. "
            "El analisis continua para diagnosticar conversion.",
            icon="📺",
        )
    elif platform == "tiktok" and analysis_mode == "hybrid":
        st.info(
            "🧩 Modo Hibrido: se detectaron posts de comunidad y posts de alcance. "
            "El reporte marca ambos modos por publicacion.",
            icon="🧩",
        )
    
    # Métrica principal
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background: {diagnosis_color}15; padding: 20px; border-radius: 10px; border-left: 4px solid {diagnosis_color};'>
            <div style='color: #6C757D; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;'>Engagement General</div>
            <div style='color: {diagnosis_color}; font-size: 36px; font-weight: bold;'>{engagement_pct:.2f}%</div>
            <div style='color: #495057; font-size: 13px; margin-top: 8px;'>{diagnosis}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: #00369615; padding: 20px; border-radius: 10px; border-left: 4px solid #003696;'>
            <div style='color: #6C757D; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;'>Engagement por Post</div>
            <div style='color: #003696; font-size: 36px; font-weight: bold;'>{engagement_per_post:.2f}%</div>
            <div style='color: #495057; font-size: 13px; margin-top: 8px;'>{total_interactions // num_posts} interacciones/post</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: #FFB81C15; padding: 20px; border-radius: 10px; border-left: 4px solid #FFB81C;'>
            <div style='color: #6C757D; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;'>Frecuencia</div>
            <div style='color: #003696; font-size: 36px; font-weight: bold;'>{posts_per_week:.1f}</div>
            <div style='color: #495057; font-size: 13px; margin-top: 8px;'>posts por semana</div>
        </div>
        """, unsafe_allow_html=True)

    if volatility.get("is_volatile"):
        st.warning(
            f"⚠️ Volatilidad detectada: media {volatility['mean']:.2f}% vs mediana {volatility['median']:.2f}% "
            f"(diferencia {volatility['relative_diff'] * 100:.1f}%). Un post viral puede estar maquillando el promedio.",
            icon="🟧",
        )
    
    # ========================================================================
    # SECCIÓN ESPECIAL: ENGAGEMENT POR VISTAS (SOLO TIKTOK)
    # ========================================================================
    
    if platform == "tiktok" and engagement_by_views > 0:
        st.divider()
        st.markdown("### 🎬 Engagement por Vistas (Rendimiento de Contenido)")
        st.caption("Este métrico mide qué tan bien funciona tu contenido, no tu comunidad")
        
        # Diagnóstico específico para engagement por vistas
        thresholds_vistas = get_engagement_thresholds("tiktok", "vistas")
        
        if engagement_by_views >= thresholds_vistas["bueno"]:
            vistas_diagnosis = "🟢 ALTO"
            vistas_color = "#0A7D35"
        elif engagement_by_views >= thresholds_vistas["aceptable"]:
            vistas_diagnosis = "🟡 BUENO"
            vistas_color = "#003696"
        elif engagement_by_views >= thresholds_vistas["bajo"]:
            vistas_diagnosis = "⚠️ ACEPTABLE"
            vistas_color = "#CC7000"
        else:
            vistas_diagnosis = "🔴 BAJO"
            vistas_color = "#B42318"
        
        col_v1, col_v2, col_v3 = st.columns([2, 1, 1])
        with col_v1:
            st.markdown(f"""
            <div style='background: {vistas_color}15; padding: 20px; border-radius: 10px; border-left: 4px solid {vistas_color};'>
                <div style='color: #6C757D; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;'>Engagement por Vistas</div>
                <div style='color: {vistas_color}; font-size: 36px; font-weight: bold;'>{engagement_by_views:.2f}%</div>
                <div style='color: #495057; font-size: 13px; margin-top: 8px;'>{vistas_diagnosis} • {total_views:,} vistas totales</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_v2:
            st.markdown(f"""
            <div style='background: #F2F4F7; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='color: #6C757D; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;'>Interacciones</div>
                <div style='color: #003696; font-size: 24px; font-weight: bold;'>{total_interactions:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_v3:
            st.markdown(f"""
            <div style='background: #F2F4F7; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='color: #6C757D; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;'>Vistas</div>
                <div style='color: #003696; font-size: 24px; font-weight: bold;'>{total_views:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info(f"""
        **📘 Interpretación:** Este métrico te dice qué % de personas que vieron tu contenido interactuaron con él.  
        **Thresholds TikTok (por vistas):** {thresholds_vistas['labels']['bajo']} | {thresholds_vistas['labels']['aceptable']} | {thresholds_vistas['labels']['bueno']} | {thresholds_vistas['labels']['alto']}
        """)
    
    # ========================================================================
    # SECCIÓN: ANÁLISIS POR TIPO DE CONTENIDO
    # ========================================================================
    
    st.markdown("### 📊 Rendimiento por Tipo de Contenido")
    
    content_df = []
    for ctype, stats in sorted(content_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True):
        content_df.append({
            "Tipo": ctype,
            "% Posts": f"{stats['pct']:.0f}%",
            "Engagement x Post": f"{stats['avg_engagement']:.2f}%",
            "Posts": stats["posts"],
            "Total Interacciones": stats["total_interactions"]
        })
    
    if content_df:
        best_type = sorted(content_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[0]
        st.success(f"✅ **{best_type[0]} es tu estrella:** {best_type[1]['avg_engagement']:.2f}% engagement promedio por post ({int(best_type[1]['pct'])}% de tus posts)")

        if ranked.get("has_data") and ranked.get("top_post"):
            top_post = ranked["top_post"]
            st.info(
                f"🏆 Top Performer: Post #{int(top_post.get('num', 0))} "
                f"({top_post.get('Categoria Canonica', top_post.get('categoria', 'Sin categoria'))}) "
                f"con ER {float(top_post.get('ER Post', 0.0)):.2f}%",
                icon="🏫",
            )
        
        st.dataframe(pd.DataFrame(content_df), use_container_width=True, hide_index=True)

        if category_signal.get("has_signal"):
            best_cat = category_signal["best_category"]
            st.success(
                f"🏫 Efectividad por categoría: **{best_cat['categoria']}** lidera con "
                f"{float(best_cat['er_promedio']):.2f}% de ER promedio (n={int(best_cat['posts'])})."
            )
        
        # Agregar análisis detallado
        st.markdown("#### Interpretación:")
        for ctype, stats in sorted(content_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True):
            pct = stats['pct']
            eng = stats['avg_engagement']
            posts = stats['posts']
            st.caption(f"**{ctype}:** {posts} post(s) ({pct:.0f}% de tu contenido) con {eng:.2f}% de engagement promedio por post")
    
    # ========================================================================
    # SECCIÓN: DIAGNÓSTICO Y ACCIONES
    # ========================================================================
    
    st.markdown("### 🎯 Diagnóstico y Acciones Recomendadas")

    st.info(narrative_recommendation, icon="🧠")
    
    if diagnosis_level == "alto":
        st.markdown(f"""
        <div style='background: #0A7D3515; padding: 20px; border-radius: 10px; border-left: 5px solid #0A7D35;'>
            <h4 style='color: #0A7D35; margin-top: 0;'>🟢 ¡Tu engagement es ALTO!</h4>
            <p>Tu audiencia está muy comprometida. Este es el resultado de contenido de calidad y conexión genuina con tu comunidad.</p>
            
            <h5>📌 Qué hacer esta semana:</h5>
            <ul>
                <li><strong>Mantén la consistencia:</strong> Publica a la misma hora y frecuencia ({posts_per_week:.0f}x/semana)</li>
                <li><strong>Amplifica tu mejor contenido:</strong> Replicate posts como {best_type[0]} que ya funcionan</li>
                <li><strong>Experimenta:</strong> Prueba nuevos formatos sin dejar lo que funciona</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif diagnosis_level == "bueno":
        st.markdown(f"""
        <div style='background: #00369615; padding: 20px; border-radius: 10px; border-left: 5px solid #003696;'>
            <h4 style='color: #003696; margin-top: 0;'>🟡 Tu engagement es BUENO</h4>
            <p>Está dentro de los parámetros normales. Con algunos ajustes estratégicos, podrías llegar al nivel excelente.</p>
            
            <h5>📌 Qué hacer esta semana:</h5>
            <ul>
                <li><strong>Enfócate en {best_type[0]}:</strong> Estos posts son {best_type[1]['avg_engagement']/engagement_per_post:.1f}x más efectivos</li>
                <li><strong>Mejora la frecuencia:</strong> Intenta pasar de {posts_per_week:.0f} a {posts_per_week + 1:.0f} posts/semana</li>
                <li><strong>Crea tendencias:</strong> Usa calls-to-action más claros para invitar interacción</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif diagnosis_level in ["aceptable", "promedio"]:
        st.markdown(f"""
        <div style='background: #CC700015; padding: 20px; border-radius: 10px; border-left: 5px solid #CC7000;'>
            <h4 style='color: #CC7000; margin-top: 0;'>⚠️ Tu engagement necesita mejorar</h4>
            <p>Por debajo del promedio para tu plataforma. Hay mucho potencial para mejorar.</p>
            
            <h5>📌 Qué hacer esta semana:</h5>
            <ul>
                <li><strong>Revisa tu contenido:</strong> ¿Está alineado con lo que tu audiencia quiere?</li>
                <li><strong>Aumenta frecuencia:</strong> Posts más consistentes (intenta diario o casi diario)</li>
                <li><strong>Testa {best_type[0]}:</strong> Es tu mejor formato ({best_type[1]['avg_engagement']:.2f}% engagement/post)</li>
                <li><strong>CTA claros:</strong> Pide comentarios, reacciones, shares explícitamente</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif diagnosis_level == "views_only":
        st.markdown(f"""
        <div style='background: #CC700015; padding: 20px; border-radius: 10px; border-left: 5px solid #CC7000;'>
            <h4 style='color: #CC7000; margin-top: 0;'>📺 Alto alcance visual, baja accion comunitaria</h4>
            <p>Tus publicaciones estan llegando a audiencia, pero no convierten en interacciones.</p>

            <h5>📌 Qué hacer esta semana:</h5>
            <ul>
                <li><strong>Activa CTA concretos:</strong> Termina cada post con una pregunta o accion clara</li>
                <li><strong>Optimiza primeros 3 segundos:</strong> Mejora hook visual y mensaje inicial</li>
                <li><strong>Refuerza conversion:</strong> Invita a comentar, guardar y compartir de forma explicita</li>
                <li><strong>Test A/B:</strong> Prueba dos versiones del mismo tema con CTA distinto</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    else:  # bajo
        st.markdown(f"""
        <div style='background: #B4231815; padding: 20px; border-radius: 10px; border-left: 5px solid #B42318;'>
            <h4 style='color: #B42318; margin-top: 0;'>🔴 Tu engagement es BAJO - ¡Acción Urgente!</h4>
            <p>Tu contenido no está conectando. Necesitas cambios significativos en estrategia.</p>
            
            <h5>📌 Qué hacer YA:</h5>
            <ul>
                <li><strong>CRÍTICO: Aumenta frequencia:</strong> Pasar de {posts_per_week:.0f} a 5-7 posts/semana</li>
                <li><strong>Cambia tu contenido:</strong> Analiza qué está funcionando en tu industria</li>
                <li><strong>Enfócate SOLO en {best_type[0]}:</strong> ({best_type[1]['avg_engagement']:.2f}% vs tu promedio {engagement_per_post:.2f}%)/post)</li>
                <li><strong>Interactúa más:</strong> Responde comentarios, sigue cuentas similares, genera comunidad</li>
                <li><strong>Usa CTAs fuertes:</strong> "Comparte tu opinión en comentarios" vs "Me encanta"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # SECCIÓN: POTENCIAL DE CRECIMIENTO
    # ========================================================================
    
    st.markdown("### 📈 Calculadora de Potencial de Crecimiento")
    
    st.markdown("Si mejoras tu engagement, ¿cuántos nuevos seguidores podrías ganar?")
    
    growth_cols = st.columns(3)
    
    for idx, (improvement, scenario) in enumerate(sorted(growth_scenarios.items())):
        with growth_cols[idx]:
            st.markdown(f"""
            <div style='background: #F2F4F7; padding: 16px; border-radius: 10px; border-left: 4px solid #003696;'>
                <div style='font-weight: bold; color: #003696; margin-bottom: 8px;'>+{improvement}% Engagement</div>
                <div style='font-size: 24px; font-weight: bold; color: #0A7D35; margin-bottom: 8px;'>
                    +{scenario['growth_pct']:.0f}% crecimiento
                </div>
                <small style='color: #495057;'>
                    De {followers:,} → {scenario['followers_3m']:,} seguidores<br>
                    en 3 meses
                </small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("**Nota:** Proyecciones basadas en relación engagement-crecimiento histórica en redes sociales.")
    
    # ========================================================================
    # BOTONES DE ACCIÓN
    # ========================================================================
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Modificar Datos", use_container_width=True):
            st.session_state["wizard_step"] = 2
            st.rerun()
    
    with col2:
        if st.button("🔄 Nuevos Datos", use_container_width=True):
            # Limpiar todos los datos del wizard
            for key in list(st.session_state.keys()):
                if key.startswith("wizard_"):
                    del st.session_state[key]
            st.session_state["wizard_step"] = 1
            st.rerun()
    
    with col3:
        expected_range = calculate_expected_engagement(followers)
        expected_payload = {
            **expected_range,
            "label": f"Típico {expected_range['typical']:.1f}%",
        }
        report_html = generate_engagement_report_html(
            platform=platform,
            followers=followers,
            days=days,
            posts_list=posts_list,
            analysis_mode=analysis_mode,
            engagement_pct=engagement_pct,
            engagement_per_post=engagement_per_post,
            engagement_by_views=engagement_by_views,
            posts_per_week=posts_per_week,
            diagnosis=diagnosis,
            content_stats=content_stats,
            growth_scenarios=growth_scenarios,
            expected=expected_payload,
            period_start=period_start,
            period_end=period_end,
            total_posts=num_posts,
            narrative_summary=narrative_recommendation,
            category_effectiveness=category_signal.get("table", pd.DataFrame()).to_dict("records") if category_signal.get("has_signal") else [],
            volatility_alert=volatility.get("message") if volatility.get("is_volatile") else "",
        )

        st.download_button(
            label="📥 Descargar Reporte HTML",
            data=report_html,
            file_name=f"engagement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            key="download_report",
            use_container_width=True,
        )


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

def render(df=None):
    """
    Punto de entrada principal. Renderiza el flujo asistente completo.
    """
    
    st.header("💡 Calculadora de Engagement")
    st.markdown(
        "Descubre el potencial de tu estrategia de contenido. "
        "Analiza tu engagement en datos reales y obtén recomendaciones accionables."
    )
    
    # Inicializar step
    if "wizard_step" not in st.session_state:
        st.session_state["wizard_step"] = 1
    
    # Mostrar indicador de progreso
    step = st.session_state.get("wizard_step", 1)
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    
    progress_steps = {
        1: ("Datos Básicos", "📋"),
        2: ("Publicaciones", "📝"),
        3: ("Resultados", "📊")
    }
    
    for col_idx, (step_num, (step_name, icon)) in enumerate(progress_steps.items()):
        with [progress_col1, progress_col2, progress_col3][col_idx]:
            if step_num == step:
                st.markdown(f"### {icon} {step_name} **← Estás aquí**")
            elif step_num < step:
                st.markdown(f"### {icon} {step_name} ✅")
            else:
                st.markdown(f"### {icon} {step_name}")
    
    st.markdown("")  # Spacing
    
    # Renderizar paso actual
    if step == 1:
        render_step_1_basic_data()
    elif step == 2:
        render_step_2_posts()
    elif step == 3:
        calculate_and_render_results()


# ============================================================================
# FUNCIONES COMPATIBILIDAD PARA data_entry.py
# ============================================================================

def render_facebook_tab():
    """Wrapper simple para compatibilidad con data_entry.py - Inicia wizard en Facebook."""
    if "wizard_platform" not in st.session_state:
        st.session_state["wizard_platform"] = "facebook"
    render(df=None)


def render_tiktok_tab():
    """Wrapper simple para compatibilidad con data_entry.py - Inicia wizard en TikTok."""
    if "wizard_platform" not in st.session_state:
        st.session_state["wizard_platform"] = "tiktok"
    render(df=None)
