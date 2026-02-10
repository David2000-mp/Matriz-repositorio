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
        platform_options = ["facebook", "tiktok"]
        platform_display = ["📘 Facebook", "🎵 TikTok"]
        
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
    st.info(
        f"📊 **Resumen:** Analizarás **{expected_posts} publicaciones** de {{platform}} "
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
    """Paso 2 del asistente: Ingreso de publicaciones con validación visual."""
    
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
    
    # Grid de 15 publicaciones
    posts_data = []
    
    for row in range(5):
        cols = st.columns(3, gap="medium")
        for col_idx, col in enumerate(cols):
            post_num = row * 3 + col_idx + 1
            
            with col:
                st.markdown(f"### Post #{post_num}")
                
                # Tipo de contenido - Si es TikTok, pre-seleccionar Video
                default_index = 1 if platform == "tiktok" else 0  # 🎥 Video para TikTok, 📸 Imagen para Facebook
                
                # Si ya existe valor en session_state, usarlo; si no, usar default
                if f"wizard_post_{post_num}_type" not in st.session_state:
                    st.session_state[f"wizard_post_{post_num}_type"] = content_types[default_index]
                
                content_type = st.selectbox(
                    "Tipo de contenido",
                    content_types,
                    key=f"wizard_post_{post_num}_type",
                    label_visibility="collapsed",
                    help="Selecciona el tipo de contenido para este post"
                )
                
                if platform == "facebook":
                    # Facebook inputs
                    st.markdown("**👍 Reacciones**")
                    st.caption("Me gusta, Me encanta, Me divierte, Me asombra, Me entristece, Me enoja")
                    reactions = st.number_input(
                        "Reacciones",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_reactions", 0),
                        key=f"wizard_post_{post_num}_reactions",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("**💬 Comentarios**")
                    st.caption("Todos los comentarios en el post")
                    comments = st.number_input(
                        "Comentarios",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_comments", 0),
                        key=f"wizard_post_{post_num}_comments",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("**📤 Compartidos**")
                    st.caption("Veces que fue compartido o re-compartido")
                    shares = st.number_input(
                        "Compartidos",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_shares", 0),
                        key=f"wizard_post_{post_num}_shares",
                        label_visibility="collapsed"
                    )
                    
                    total = int(reactions) + int(comments) + int(shares)
                    
                    # Validación visual en tiempo real
                    validation = validate_post_engagement(int(reactions), int(comments), int(shares), followers)
                    
                else:  # TikTok
                    st.markdown("**👁️ Vistas**")
                    st.caption("Número total de veces que el video fue visto")
                    views = st.number_input(
                        "Vistas",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_views", 0),
                        key=f"wizard_post_{post_num}_views",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("**👍 Me gusta**")
                    st.caption("Número de likes que recibió el video")
                    likes = st.number_input(
                        "Me gusta",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_likes", 0),
                        key=f"wizard_post_{post_num}_likes",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("**💬 Comentarios**")
                    st.caption("Comentarios en el video")
                    comments = st.number_input(
                        "Comentarios",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_comments", 0),
                        key=f"wizard_post_{post_num}_comments",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("**📤 Compartidos**")
                    st.caption("Veces que fue compartido o enviado")
                    shares = st.number_input(
                        "Compartidos",
                        min_value=0,
                        value=st.session_state.get(f"wizard_post_{post_num}_shares", 0),
                        key=f"wizard_post_{post_num}_shares",
                        label_visibility="collapsed"
                    )
                    
                    # Total: Solo likes + comentarios + compartidos (según reglas oficiales)
                    total = int(likes) + int(comments) + int(shares)
                    
                    # Validación visual en tiempo real
                    validation = validate_post_engagement(int(likes), int(comments), int(shares), followers)
                
                # Mostrar indicador visual
                st.markdown(
                    f"<div style='padding: 8px; border-radius: 6px; background: {validation['color']}20; "
                    f"border-left: 4px solid {validation['color']};'>"
                    f"<strong>{validation['icon']} {validation['message']}</strong>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                st.caption(f"**Total:** {total} interacciones")
                
                posts_data.append({
                    "post_num": post_num,
                    "type": content_type,
                    "total": total,
                    "status": validation["status"]
                })
    
    st.divider()
    
    # Resumen rápido
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
    
    # Navegación
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Volver al Paso 1", use_container_width=True):
            st.session_state["wizard_step"] = 1
            st.rerun()
    
    with col3:
        if st.button("Calcular Resultados →", use_container_width=True, type="primary"):
            st.session_state["wizard_step"] = 3
            st.rerun()


# ============================================================================
# PASO 3: RESULTADOS Y ANÁLISIS
# ============================================================================

def calculate_and_render_results():
    """Paso 3: Calcular y mostrar resultados con análisis completo."""
    
    platform = st.session_state.get("wizard_platform", "facebook")
    followers = st.session_state.get("wizard_followers", 2500)
    days = st.session_state.get("wizard_days", 30)
    
    # Recopilar datos de publicaciones
    posts_list = []
    total_interactions = 0
    total_views = 0
    
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
            post["total"] = reactions + comments + shares
            total_interactions += post["total"]
            
        else:  # TikTok
            views = st.session_state.get(f"wizard_post_{i}_views", 0)
            likes = st.session_state.get(f"wizard_post_{i}_likes", 0)
            comments = st.session_state.get(f"wizard_post_{i}_comments", 0)
            shares = st.session_state.get(f"wizard_post_{i}_shares", 0)
            post["views"] = views
            post["likes"] = likes
            post["comments"] = comments
            post["shares"] = shares
            # Total: Solo likes + comentarios + compartidos (no guardados ni vistas)
            post["total"] = likes + comments + shares
            total_interactions += post["total"]
            total_views += views
        
        posts_list.append(post)
    
    if total_interactions == 0:
        st.error("⚠️ No hay datos para analizar. Por favor completa al menos algunos posts.")
        if st.button("← Volver al Paso 2"):
            st.session_state["wizard_step"] = 2
            st.rerun()
        return
    
    # ========================================================================
    # CÁLCULOS PRINCIPALES
    # ========================================================================
    
    num_posts = 15
    # Engagement general de la cuenta
    engagement_pct = (total_interactions / followers) * 100
    # Engagement por post (comunidad): (Promedio interacciones / Seguidores) * 100
    avg_interactions = total_interactions / num_posts
    engagement_per_post = (avg_interactions / followers) * 100
    posts_per_week = num_posts / (days / 7)
    
    # Para TikTok
    if platform == "tiktok" and total_views > 0:
        engagement_by_views = (total_interactions / total_views) * 100
    else:
        engagement_by_views = 0
    
    # Segmentación por tipo de contenido
    content_stats = {}
    for post in posts_list:
        ctype = post["type"]
        if ctype not in content_stats:
            content_stats[ctype] = {"total_interactions": 0, "posts": 0, "engagement": 0}
        
        content_stats[ctype]["total_interactions"] += post["total"]
        content_stats[ctype]["posts"] += 1
        content_stats[ctype]["engagement"] = (content_stats[ctype]["total_interactions"] / content_stats[ctype]["posts"] / followers) * 100
    
    # Diagnóstico basado en thresholds fijos por plataforma
    thresholds = get_engagement_thresholds(platform, "comunidad")
    
    if platform == "facebook":
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
    
    # ========================================================================
    # RENDERIZAR RESULTADOS
    # ========================================================================
    
    st.divider()
    st.markdown(f"## Paso 3: Tus Resultados")
    
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
    for ctype, stats in sorted(content_stats.items(), key=lambda x: x[1]["engagement"], reverse=True):
        content_df.append({
            "Tipo": ctype,
            "Engagement %": f"{stats['engagement']:.2f}%",
            "Posts": stats["posts"],
            "Total Interacciones": stats["total_interactions"]
        })
    
    if content_df:
        st.markdown("Mejor rendimiento por tipo de contenido:")
        best_type = sorted(content_stats.items(), key=lambda x: x[1]["engagement"], reverse=True)[0]
        st.success(f"✅ **{best_type[0]} es tu estrella:** {best_type[1]['engagement']:.2f}% engagement")
        
        st.dataframe(pd.DataFrame(content_df), use_container_width=True, hide_index=True)
    
    # ========================================================================
    # SECCIÓN: DIAGNÓSTICO Y ACCIONES
    # ========================================================================
    
    st.markdown("### 🎯 Diagnóstico y Acciones Recomendadas")
    
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
                <li><strong>Enfócate en {best_type[0]}:</strong> Estos posts son {best_type[1]['engagement']/engagement_per_post:.1f}x más efectivos</li>
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
                <li><strong>Testa {best_type[0]}:</strong> Es tu mejor formato ({best_type[1]['engagement']:.2f}%)</li>
                <li><strong>CTA claros:</strong> Pide comentarios, reacciones, shares explícitamente</li>
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
                <li><strong>Enfócate SOLO en {best_type[0]}:</strong> ({best_type[1]['engagement']:.2f}% vs tu promedio {engagement_per_post:.2f}%)</li>
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
        if st.button("📥 Descargar Reporte", use_container_width=True, type="primary"):
            # Generar reporte HTML
            thresholds_info = get_engagement_thresholds(platform, "comunidad")
            report_html = generate_engagement_report_html(
                platform=platform,
                followers=followers,
                days=days,
                posts_list=posts_list,
                engagement_pct=engagement_pct,
                engagement_per_post=engagement_per_post,
                engagement_by_views=engagement_by_views,
                posts_per_week=posts_per_week,
                diagnosis=diagnosis,
                content_stats=content_stats,
                growth_scenarios=growth_scenarios,
                expected=thresholds_info
            )
            
            # Crear descarga
            st.download_button(
                label="📥 Descargar como HTML",
                data=report_html,
                file_name=f"engagement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                key="download_report"
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
