"""
Vista de Calculadora de Engagement para CHAMPILEAKS.
Herramienta para calcular y analizar engagement en Facebook y TikTok.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging


def calculate_facebook_engagement():
    """
    Calcula métricas de engagement para Facebook.
    Utiliza datos del formulario en st.session_state.
    """
    # Obtener valores principales
    followers = st.session_state.get("fb_followers", 0)
    days = st.session_state.get("fb_days", 0)
    reach = st.session_state.get("fb_reach", None)
    
    if not followers or not days:
        return None
    
    # Calcular interacciones totales desde los 15 posts
    total_interactions = 0
    total_reactions = 0
    total_comments = 0
    total_shares = 0
    
    for i in range(1, 16):
        reactions = st.session_state.get(f"fb_post_{i}_reactions", 0) or 0
        comments = st.session_state.get(f"fb_post_{i}_comments", 0) or 0
        shares = st.session_state.get(f"fb_post_{i}_shares", 0) or 0
        
        total_reactions += int(reactions)
        total_comments += int(comments)
        total_shares += int(shares)
        total_interactions += int(reactions) + int(comments) + int(shares)
    
    if total_interactions == 0:
        return None
    
    # Cálculos principales
    posts = 15
    engagement_percentage = (total_interactions / followers) * 100
    engagement_per_post_percentage = ((total_interactions / posts) / followers) * 100
    engagement_per_post = total_interactions / posts
    posts_per_week = posts / (days / 7)
    
    # Análisis de benchmarks
    if engagement_percentage >= 5:
        engagement_status = "✅ EXCELENTE"
        engagement_color = "#0A7D35"
        engagement_desc = "Muy por encima del promedio. Tu audiencia está altamente comprometida."
    elif engagement_percentage >= 2.5:
        engagement_status = "✅ BUENO"
        engagement_color = "#0A7D35"
        engagement_desc = "Dentro de los parámetros normales. Mantén esta estrategia."
    elif engagement_percentage >= 1:
        engagement_status = "⚠️ MODERADO"
        engagement_color = "#CC7000"
        engagement_desc = "Por debajo de lo ideal. Considera mejorar la calidad del contenido."
    else:
        engagement_status = "❌ BAJO"
        engagement_color = "#B42318"
        engagement_desc = "Necesitas revisar tu estrategia de contenido urgentemente."
    
    return {
        "total_interactions": total_interactions,
        "total_reactions": total_reactions,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "followers": followers,
        "days": days,
        "posts": posts,
        "reach": reach,
        "engagement_percentage": engagement_percentage,
        "engagement_per_post_percentage": engagement_per_post_percentage,
        "engagement_per_post": engagement_per_post,
        "posts_per_week": posts_per_week,
        "engagement_status": engagement_status,
        "engagement_color": engagement_color,
        "engagement_desc": engagement_desc,
    }


def calculate_tiktok_engagement():
    """
    Calcula métricas de engagement para TikTok.
    Utiliza datos del formulario en st.session_state.
    """
    # Obtener valores principales
    followers = st.session_state.get("tk_followers", 0)
    days = st.session_state.get("tk_days", 0)
    
    if not followers or not days:
        return None
    
    # Calcular interacciones totales desde los 15 videos
    total_views = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_saves = 0
    
    for i in range(1, 16):
        views = st.session_state.get(f"tk_video_{i}_views", 0) or 0
        likes = st.session_state.get(f"tk_video_{i}_likes", 0) or 0
        comments = st.session_state.get(f"tk_video_{i}_comments", 0) or 0
        shares = st.session_state.get(f"tk_video_{i}_shares", 0) or 0
        saves = st.session_state.get(f"tk_video_{i}_saves", 0) or 0
        
        total_views += int(views)
        total_likes += int(likes)
        total_comments += int(comments)
        total_shares += int(shares)
        total_saves += int(saves)
    
    total_interactions = total_likes + total_comments + total_shares + total_saves
    
    if total_interactions == 0 or total_views == 0:
        return None
    
    # Cálculos principales para TikTok
    videos = 15
    engagement_views = (total_interactions / total_views) * 100
    engagement_followers = (total_interactions / followers) * 100
    
    # Engagement ponderado (Likes×1 + Comments×2 + Saves×3 + Shares×4)
    weighted_score = (total_likes * 1) + (total_comments * 2) + (total_saves * 3) + (total_shares * 4)
    engagement_weighted = (weighted_score / total_views) * 100
    
    # Análisis de benchmarks por vistas (métrica principal)
    if engagement_views < 3:
        views_status = "❌ BAJO"
        views_color = "#B42318"
        views_desc = "El contenido no está reteniendo a la audiencia. Revisa el hook inicial de tus videos."
    elif engagement_views < 6:
        views_status = "⚠️ PROMEDIO"
        views_color = "#CC7000"
        views_desc = "Aceptable para cuentas en crecimiento. Hay margen de mejora."
    elif engagement_views < 12:
        views_status = "✅ ALTO"
        views_color = "#0A7D35"
        views_desc = "El contenido está conectando muy bien. ¡Que buen trabajo!"
    else:
        views_status = "✅ VIRAL/EXCELENTE"
        views_color = "#0A7D35"
        views_desc = "Típico de tendencias fuertes. Tu contenido es muy atractivo."
    
    return {
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_saves": total_saves,
        "total_interactions": total_interactions,
        "followers": followers,
        "days": days,
        "videos": videos,
        "engagement_views": engagement_views,
        "engagement_followers": engagement_followers,
        "engagement_weighted": engagement_weighted,
        "views_status": views_status,
        "views_color": views_color,
        "views_desc": views_desc,
    }


def render_facebook_tab():
    """Renderiza la pestaña de Facebook."""
    st.markdown("### 📘 Calculadora de Engagement - Facebook")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fb_followers = st.number_input(
            "Seguidores actuales",
            min_value=1,
            value=st.session_state.get("fb_followers", 2500),
            key="fb_followers",
            help="Seguidores totales de la página"
        )
    with col2:
        fb_days = st.number_input(
            "Período de análisis (días)",
            min_value=1,
            max_value=365,
            value=st.session_state.get("fb_days", 30),
            key="fb_days",
            help="Número de días que abarca tu análisis"
        )
    with col3:
        fb_reach = st.number_input(
            "Alcance total (opcional)",
            min_value=0,
            value=st.session_state.get("fb_reach", 0) or 0,
            key="fb_reach",
            help="Personas alcanzadas en el período (la métrica de alcance de Facebook)"
        )
    
    st.markdown("---")
    st.markdown("#### 📝 Ingresa tus 15 publicaciones")
    st.info("Completa los campos de cada publicación. Las interacciones se sumarán automáticamente.", icon="ℹ️")
    
    # Grid de 15 publicaciones (5 filas x 3 columnas)
    for row in range(5):
        cols = st.columns(3, gap="medium")
        for col_idx, col in enumerate(cols):
            post_num = row * 3 + col_idx + 1
            with col:
                st.markdown(f"**Publicación #{post_num}**")
                c1, c2, c3 = st.columns(3, gap="small")
                with c1:
                    reactions = st.number_input(
                        "Reacciones",
                        min_value=0,
                        value=st.session_state.get(f"fb_post_{post_num}_reactions", 0),
                        key=f"fb_post_{post_num}_reactions",
                        label_visibility="collapsed"
                    )
                with c2:
                    comments = st.number_input(
                        "Comentarios",
                        min_value=0,
                        value=st.session_state.get(f"fb_post_{post_num}_comments", 0),
                        key=f"fb_post_{post_num}_comments",
                        label_visibility="collapsed"
                    )
                with c3:
                    shares = st.number_input(
                        "Compartidos",
                        min_value=0,
                        value=st.session_state.get(f"fb_post_{post_num}_shares", 0),
                        key=f"fb_post_{post_num}_shares",
                        label_visibility="collapsed"
                    )
                total = int(reactions) + int(comments) + int(shares)
                st.caption(f"**Total:** {total} interacciones")
    
    st.markdown("---")
    
    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Calcular Engagement", key="fb_calculate", use_container_width=True):
            results = calculate_facebook_engagement()
            if results:
                st.session_state["fb_results"] = results
                st.rerun()
            else:
                st.error("⚠️ Verifica que hayas ingresado seguidores, período y al menos algunas interacciones.")
    
    with col2:
        if st.button("🔄 Limpiar Todo", key="fb_reset", use_container_width=True):
            # Limpiar session_state de Facebook
            keys_to_clear = [k for k in st.session_state.keys() if k.startswith("fb_")]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()
    
    # Mostrar resultados si existen
    if "fb_results" in st.session_state:
        results = st.session_state["fb_results"]
        st.markdown("---")
        st.markdown("### 📊 Resultados del Análisis")
        
        # Fila 1: Engagement principal
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid {results['engagement_color']};">
                <div style="font-size: 14px; color: #495057; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;">Engagement por Seguidores</div>
                <div style="font-size: 32px; font-weight: bold; color: {results['engagement_color']};">{results['engagement_percentage']:.2f}%</div>
                <div style="color: #495057; margin-top: 8px; font-size: 13px;">{results['engagement_status']}</div>
                <div style="color: #6C757D; margin-top: 4px; font-size: 12px;">{results['engagement_desc']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid #003696;">
                <div style="font-size: 14px; color: #495057; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;">Engagement por Publicación</div>
                <div style="font-size: 32px; font-weight: bold; color: #003696;">{results['engagement_per_post_percentage']:.2f}%</div>
                <div style="color: #495057; margin-top: 8px; font-size: 12px;">
                    {results['engagement_per_post']:.0f} interacciones promedio por publicación<br>
                    <small style="color: #6C757D;">📊 {results['total_reactions']} reacciones | {results['total_comments']} comentarios | {results['total_shares']} compartidos</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Fila 2: Benchmarks
        st.markdown("#### 📈 Benchmarks para Páginas Locales")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Estándares de Engagement:**
            - ✅ Excelente: >5%
            - ✅ Bueno: 2.5% - 5%
            - ⚠️ Moderado: 1% - 2.5%
            - ❌ Bajo: <1%
            """)
        
        with col2:
            st.markdown(f"""
            **Tu Situación:**
            - 📊 Engagement actual: {results['engagement_percentage']:.2f}%
            - 📈 Total de interacciones: {results['total_interactions']} en {results['posts']} publicaciones
            - ⏱️ Período: {results['days']} días
            - 📅 Frecuencia: {results['posts_per_week']:.1f} posts/semana
            """)
        
        # Fila 3: Recomendación de frecuencia
        st.markdown("#### 💡 Recomendación de Frecuencia Óptima")
        
        if results['posts_per_week'] < 2:
            rec_status = "🔴 CRÍTICO"
            rec_title = "Muy pocas publicaciones"
            rec_action = "Aumenta a 3-5 posts/semana"
            rec_detail = f"Actualmente estás en {results['posts_per_week']:.1f} posts/semana ({results['posts']} en {results['days']} días). El alcance orgánico cae significativamente con menos de 3 posts semanales."
            rec_color = "#B42318"
        elif results['posts_per_week'] < 3:
            rec_status = "🟡 ALERTA"
            rec_title = "Frecuencia baja"
            rec_action = "Aumenta a 3-5 posts/semana"
            rec_detail = f"La frecuencia óptima comienza en 3 posts/semana. Actualmente: {results['posts_per_week']:.1f} posts/semana."
            rec_color = "#CC7000"
        elif results['posts_per_week'] <= 5:
            rec_status = "✅ ÓPTIMO"
            rec_title = "Frecuencia correcta"
            rec_action = "Mantén entre 3-5 posts/semana"
            rec_color = "#0A7D35"
            if results['engagement_percentage'] >= 2.5:
                rec_detail = f"Estás en la zona dorada con {results['posts_per_week']:.1f} posts/semana. Tu engagement es sano. Mantén esta cadencia."
            else:
                rec_detail = f"Estás en la zona dorada con {results['posts_per_week']:.1f} posts/semana. Aunque el engagement es bajo, la frecuencia es correcta. Mejora la calidad del contenido."
        else:
            rec_status = "🟡 ADVERTENCIA"
            rec_title = "Algo frecuente"
            rec_action = "Considera reducir"
            rec_color = "#CC7000"
            rec_detail = f"Estás en {results['posts_per_week']:.1f} posts/semana. Si el engagement es alto (>5%), puedes mantener. Si es bajo (<2%), reduce."
        
        st.markdown(f"""
        <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid {rec_color};">
            <div style="font-size: 16px; color: {rec_color}; font-weight: bold; margin-bottom: 8px;">{rec_status}: {rec_title}</div>
            <div style="color: #495057; margin-bottom: 12px;"><strong>{rec_action}</strong></div>
            <div style="color: #6C757D; font-size: 13px; line-height: 1.6;">{rec_detail}</div>
            <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #DEE2E6;">
                <strong>Estructura sugerida de contenido:</strong><br>
                <small style="color: #6C757D;">
                • 2-3 posts de valor (informativos, noticias, utilidad)<br>
                • 1-2 posts de engagement (preguntas, opinión, comunidad)<br>
                • 1 post fuerte (video corto o imagen clave)<br>
                <em>Distribuye esto a lo largo de la semana</em>
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis de alcance si está disponible
        if results['reach'] and results['reach'] > 0:
            st.markdown("---")
            st.markdown("#### 🌐 Análisis de Alcance")
            reach_per_post = results['reach'] / results['posts']
            reach_per_post_percentage = (results['reach'] / results['followers']) * 100
            st.markdown(f"""
            **Alcance promedio:** {reach_per_post:.0f} personas/post  
            **Cobertura sobre tu base:** {reach_per_post_percentage:.1f}% de tus seguidores ven cada post en promedio
            """)


def render_tiktok_tab():
    """Renderiza la pestaña de TikTok."""
    st.markdown("### 🎵 Calculadora de Engagement - TikTok")
    
    col1, col2 = st.columns(2)
    with col1:
        tk_followers = st.number_input(
            "Seguidores actuales",
            min_value=1,
            value=st.session_state.get("tk_followers", 5000),
            key="tk_followers",
            help="Seguidores totales de tu cuenta"
        )
    with col2:
        tk_days = st.number_input(
            "Período de análisis (días)",
            min_value=1,
            max_value=365,
            value=st.session_state.get("tk_days", 30),
            key="tk_days",
            help="Número de días que abarca tu análisis"
        )
    
    st.markdown("---")
    st.markdown("#### 🎬 Ingresa tus 15 videos")
    st.info("Completa los campos de cada video. Las interacciones se sumarán automáticamente.", icon="ℹ️")
    
    # Grid de 15 videos (5 filas x 3 columnas)
    for row in range(5):
        cols = st.columns(3, gap="medium")
        for col_idx, col in enumerate(cols):
            video_num = row * 3 + col_idx + 1
            with col:
                st.markdown(f"**Video #{video_num}**")
                c1, c2 = st.columns(2, gap="small")
                with c1:
                    views = st.number_input(
                        "Vistas",
                        min_value=0,
                        value=st.session_state.get(f"tk_video_{video_num}_views", 0),
                        key=f"tk_video_{video_num}_views",
                        label_visibility="collapsed"
                    )
                    likes = st.number_input(
                        "Me gusta",
                        min_value=0,
                        value=st.session_state.get(f"tk_video_{video_num}_likes", 0),
                        key=f"tk_video_{video_num}_likes",
                        label_visibility="collapsed"
                    )
                    comments = st.number_input(
                        "Comentarios",
                        min_value=0,
                        value=st.session_state.get(f"tk_video_{video_num}_comments", 0),
                        key=f"tk_video_{video_num}_comments",
                        label_visibility="collapsed"
                    )
                
                with c2:
                    shares = st.number_input(
                        "Compartidos",
                        min_value=0,
                        value=st.session_state.get(f"tk_video_{video_num}_shares", 0),
                        key=f"tk_video_{video_num}_shares",
                        label_visibility="collapsed"
                    )
                    saves = st.number_input(
                        "Guardados",
                        min_value=0,
                        value=st.session_state.get(f"tk_video_{video_num}_saves", 0),
                        key=f"tk_video_{video_num}_saves",
                        label_visibility="collapsed"
                    )
                
                total = int(likes) + int(comments) + int(shares) + int(saves)
                st.caption(f"**Total:** {total} interacciones")
    
    st.markdown("---")
    
    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Calcular Engagement TikTok", key="tk_calculate", use_container_width=True):
            results = calculate_tiktok_engagement()
            if results:
                st.session_state["tk_results"] = results
                st.rerun()
            else:
                st.error("⚠️ Verifica que hayas ingresado seguidores, período, al menos algunas interacciones y vistas.")
    
    with col2:
        if st.button("🔄 Limpiar Todo", key="tk_reset", use_container_width=True):
            # Limpiar session_state de TikTok
            keys_to_clear = [k for k in st.session_state.keys() if k.startswith("tk_")]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()
    
    # Mostrar resultados si existen
    if "tk_results" in st.session_state:
        results = st.session_state["tk_results"]
        st.markdown("---")
        st.markdown("### 📊 Resultados del Análisis")
        
        # Fila 1: Las tres métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid {results['views_color']};">
                <div style="font-size: 12px; color: #495057; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;">Engagement por Vistas<br><small>(Métrica Principal)</small></div>
                <div style="font-size: 28px; font-weight: bold; color: {results['views_color']};">{results['engagement_views']:.2f}%</div>
                <div style="color: #495057; margin-top: 8px; font-size: 11px;">{results['views_status']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Engagement por seguidores
            if results['engagement_followers'] < 3:
                followers_status = "❌ BAJO"
                followers_color = "#B42318"
            elif results['engagement_followers'] < 6:
                followers_status = "⚠️ PROMEDIO"
                followers_color = "#CC7000"
            elif results['engagement_followers'] < 12:
                followers_status = "✅ ALTO"
                followers_color = "#0A7D35"
            else:
                followers_status = "✅ EXCELENTE"
                followers_color = "#0A7D35"
            
            st.markdown(f"""
            <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid {followers_color};">
                <div style="font-size: 12px; color: #495057; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;">Engagement por Seguidores</div>
                <div style="font-size: 28px; font-weight: bold; color: {followers_color};">{results['engagement_followers']:.2f}%</div>
                <div style="color: #495057; margin-top: 8px; font-size: 11px;">{followers_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Engagement ponderado
            if results['engagement_weighted'] < 3:
                weighted_status = "❌ BAJO"
                weighted_color = "#B42318"
            elif results['engagement_weighted'] < 6:
                weighted_status = "⚠️ PROMEDIO"
                weighted_color = "#CC7000"
            elif results['engagement_weighted'] < 12:
                weighted_status = "✅ ALTO"
                weighted_color = "#0A7D35"
            else:
                weighted_status = "✅ VIRAL"
                weighted_color = "#0A7D35"
            
            st.markdown(f"""
            <div style="background: #F2F4F7; padding: 20px; border-radius: 10px; border-left: 4px solid {weighted_color};">
                <div style="font-size: 12px; color: #495057; margin-bottom: 8px; text-transform: uppercase; font-weight: 600;">Engagement Ponderado</div>
                <div style="font-size: 28px; font-weight: bold; color: {weighted_color};">{results['engagement_weighted']:.2f}%</div>
                <div style="color: #495057; margin-top: 8px; font-size: 11px;">{weighted_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Benchmarks
        st.markdown("#### 📈 Benchmarks en TikTok")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Interpretación de Engagement por Vistas:**
            - 🔴 Menos del 3%: Bajo - revisar estrategia
            - 🟡 3% - 6%: Promedio - aceptable
            - 🟢 6% - 12%: Alto - muy bien
            - 🟢 Más del 12%: Viral/Excelente
            """)
        
        with col2:
            st.markdown(f"""
            **Tu análisis:**
            - 📊 Engagement por Vistas: {results['engagement_views']:.2f}%
            - 👥 Engagement por Seguidores: {results['engagement_followers']:.2f}%
            - ⭐ Engagement Ponderado: {results['engagement_weighted']:.2f}%
            - 📈 Total de vistas: {results['total_views']:,}
            - 📺 Período: {results['days']} días | {results['videos']} videos
            """)
        
        # Desglose de interacciones
        st.markdown("#### 💬 Desglose de Interacciones")
        
        total_inter = results['total_interactions']
        like_pct = (results['total_likes'] / total_inter * 100) if total_inter > 0 else 0
        comment_pct = (results['total_comments'] / total_inter * 100) if total_inter > 0 else 0
        save_pct = (results['total_saves'] / total_inter * 100) if total_inter > 0 else 0
        share_pct = (results['total_shares'] / total_inter * 100) if total_inter > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            - ❤️ Me gusta: {results['total_likes']:,} ({like_pct:.1f}%)
            - 💬 Comentarios: {results['total_comments']:,} ({comment_pct:.1f}%)
            """)
        
        with col2:
            st.markdown(f"""
            - 🔖 Guardados: {results['total_saves']:,} ({save_pct:.1f}%)
            - ↗️ Compartidos: {results['total_shares']:,} ({share_pct:.1f}%)
            """)
        
        st.markdown(f"**Total: {total_inter:,} interacciones**")
        st.caption("💡 Los Guardados y Compartidos son las acciones más valiosas para el algoritmo de TikTok.")


def render(df=None):
    """
    Renderiza la página completa de la Calculadora de Engagement.
    
    Parámetro df por compatibilidad con el enrutador.
    """
    st.header("💡 Calculadora de Engagement")
    st.markdown("Analiza y optimiza tu engagement en redes sociales con métricas confiables.")
    
    # Crear tabs para Facebook y TikTok
    tab1, tab2 = st.tabs(["📘 Facebook", "🎵 TikTok"])
    
    with tab1:
        render_facebook_tab()
    
    with tab2:
        render_tiktok_tab()
    
    # Footer informativo
    st.markdown("---")
    st.markdown("""
    **ℹ️ Cómo interpretar los resultados:**
    
    - **Engagement por Seguidores:** Porcentaje de tu base que interactuó con el contenido. Mayor es mejor.
    - **Engagement por Publicación:** Promedio de interacciones que genera cada post/video.
    - **Benchmarks:** Estándares de la industry para comparar tu rendimiento.
    - **Recomendaciones:** Basadas en mejores prácticas de social media marketing.
    """)
