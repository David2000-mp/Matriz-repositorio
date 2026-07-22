"""
Demo de Animaciones de Hover
Ejecutar con: streamlit run demo_animaciones.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme_styles import get_theme_css

# Aplicar estilos globales
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.title("🎨 Demo de Animaciones de Hover")
st.caption("Pasa el mouse sobre las cajas para ver las animaciones")

st.markdown("---")

# Demo 1: Métricas KPI con animaciones
st.subheader("1. Métricas KPI Animadas")
st.caption("Hover sobre las métricas para ver el efecto de elevación y brillo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Seguidores Totales 🎯",
        value="45,243",
        delta="+12.5%"
    )

with col2:
    st.metric(
        label="Engagement Rate 💫",
        value="5.8%",
        delta="+2.3%"
    )

with col3:
    st.metric(
        label="Interacciones 💬",
        value="2,631",
        delta="+8.1%"
    )

with col4:
    st.metric(
        label="Salud Digital 🏥",
        value="87/100",
        delta="Excelente"
    )

st.markdown("---")

# Demo 2: Expanders animados
st.subheader("2. Expanders con Animación de Deslizamiento")
st.caption("Hover sobre los expanders para ver el efecto de deslizamiento lateral")

with st.expander("📱 Instagram - Ver detalles", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Seguidores", "25,000")
    with col2:
        st.metric("Engagement", "7.2%")
    with col3:
        st.metric("Interacciones", "1,800")

with st.expander("📘 Facebook - Ver detalles", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Seguidores", "15,000")
    with col2:
        st.metric("Engagement", "3.5%")
    with col3:
        st.metric("Interacciones", "525")

with st.expander("🎵 TikTok - Ver detalles", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Seguidores", "5,243")
    with col2:
        st.metric("Engagement", "12.1%")
    with col3:
        st.metric("Interacciones", "634")

st.markdown("---")

# Demo 3: Tabla con hover en filas
st.subheader("3. Tabla Interactiva con Hover en Filas")
st.caption("Hover sobre las filas de la tabla para ver el efecto de resaltado")

df_demo = pd.DataFrame({
    'Entidad': ['Colegio A', 'Colegio B', 'Colegio C', 'Colegio D', 'Colegio E'],
    'Plataforma': ['Instagram', 'Facebook', 'TikTok', 'Instagram', 'Facebook'],
    'Seguidores': [10000, 15000, 5000, 8000, 12000],
    'Engagement': ['6.5%', '3.2%', '11.0%', '5.8%', '4.1%']
})

st.dataframe(df_demo, use_container_width=True, hide_index=True)

st.markdown("---")

# Demo 4: Gráfica con animación
st.subheader("4. Gráfica con Efecto de Elevación")
st.caption("Hover sobre la gráfica para ver el efecto de elevación")

# Crear gráfica de ejemplo
fig = go.Figure()
fig.add_trace(go.Bar(
    x=['Instagram', 'Facebook', 'TikTok', 'Twitter', 'LinkedIn'],
    y=[25000, 15000, 5243, 8000, 3500],
    marker_color=['#E4405F', '#1877F2', '#000000', '#1DA1F2', '#0A66C2'],
    text=[25000, 15000, 5243, 8000, 3500],
    textposition='auto',
))

fig.update_layout(
    title="Seguidores por Plataforma",
    xaxis_title="Plataforma",
    yaxis_title="Seguidores",
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Demo 5: Tarjetas personalizadas con animación
st.subheader("5. Tarjetas Personalizadas")
st.caption("Hover sobre las tarjetas para ver el efecto de elevación")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='padding: 20px; border: 2px solid #003696; border-radius: 12px; background: white;'>
        <h3 style='color: #003696; margin: 0;'>📊 Dashboard</h3>
        <p style='color: #495057; margin: 10px 0 0 0;'>Vista general de todas las métricas</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='padding: 20px; border: 2px solid #0A7D35; border-radius: 12px; background: white;'>
        <h3 style='color: #0A7D35; margin: 0;'>🔍 Análisis</h3>
        <p style='color: #495057; margin: 10px 0 0 0;'>Análisis detallado por entidad</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='padding: 20px; border: 2px solid #FFB81C; border-radius: 12px; background: white;'>
        <h3 style='color: #B8860B; margin: 0;'>📝 Captura</h3>
        <p style='color: #495057; margin: 10px 0 0 0;'>Ingreso manual de datos</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.success("✅ Todas las animaciones están funcionando correctamente. Pasa el mouse sobre cualquier elemento para verlas en acción.")

# Información adicional
with st.expander("ℹ️ Detalles Técnicos de las Animaciones"):
    st.markdown("""
    ### Animaciones Implementadas:
    
    1. **Métricas KPI (`st.metric`)**
       - Elevación con `translateY(-4px)`
       - Escala ligera `scale(1.02)`
       - Sombra dinámica con blur de 24px
       - Efecto de brillo (shimmer) al pasar el mouse
       - Transición suave de 0.3s con easing `cubic-bezier`
    
    2. **Expanders**
       - Deslizamiento lateral con `translateX(4px)`
       - Cambio de fondo sutil
       - Sombra de 12px
    
    3. **Tablas**
       - Filas con escala `scale(1.01)` en hover
       - Cambio de color de fondo al 4% de opacidad
       - Transición rápida de 0.2s
    
    4. **Gráficas Plotly**
       - Elevación de 4px
       - Sombra más pronunciada (24px blur)
       - Transición de 0.3s
    
    5. **Tarjetas Personalizadas**
       - Elevación de 2px
       - Sombra de 16px
       - Transición suave
    
    ### Principios de Diseño:
    - **Consistencia**: Todas las animaciones usan el mismo timing (0.3s)
    - **Sutileza**: Movimientos pequeños (2-4px) para no ser invasivos
    - **Accesibilidad**: Respeta `prefers-reduced-motion` del sistema
    - **Performance**: Usa `transform` y `opacity` para animaciones eficientes
    """)
