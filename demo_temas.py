"""
🎨 DEMO: Sistema de Temas Dinámicos
Ejemplo completo de uso de aplicar_estilo_personalizado()

Para ejecutar:
    streamlit run demo_temas.py
"""

import streamlit as st
from components import aplicar_estilo_personalizado
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ============================================
# APLICAR TEMA (SIEMPRE PRIMERO)
# ============================================
tema_actual = aplicar_estilo_personalizado()

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Demo Sistema de Temas",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONTENIDO PRINCIPAL
# ============================================

st.title("🎨 Demo Completa: Sistema de Temas Dinámicos")

st.markdown(f"""
### ✅ Tema Actual: **{tema_actual}**

Esta demo muestra todos los componentes con el sistema de temas unificado.
Cambia el tema en la barra lateral y observa cómo todos los elementos se adaptan automáticamente.
""")

st.markdown("---")

# ============================================
# SECCIÓN 1: INPUTS UNIFICADOS
# ============================================

st.markdown("## 📝 Inputs Unificados")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Text Input")
    nombre = st.text_input(
        "Nombre del Colegio",
        placeholder="Ej: Champagnat",
        help="Escribe el nombre del colegio"
    )
    
    email = st.text_input(
        "Email de Contacto",
        placeholder="ejemplo@colegio.edu",
        type="default"
    )

with col2:
    st.markdown("### Selectbox")
    plataforma = st.selectbox(
        "Plataforma Social",
        ["Facebook", "Instagram", "TikTok", "Twitter/X", "LinkedIn", "YouTube"],
        help="Selecciona una plataforma para análisis"
    )
    
    mes = st.selectbox(
        "Mes de Análisis",
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
    )

with col3:
    st.markdown("### Number & Date")
    seguidores = st.number_input(
        "Seguidores Iniciales",
        min_value=0,
        max_value=1000000,
        step=100,
        value=5000
    )
    
    fecha = st.date_input(
        "Fecha de Reporte",
        value=datetime.now()
    )

st.markdown("---")

# ============================================
# SECCIÓN 2: TEXT AREA Y MULTISELECT
# ============================================

st.markdown("## 📄 Campos de Texto Largo")

col1, col2 = st.columns(2)

with col1:
    descripcion = st.text_area(
        "Descripción del Colegio",
        placeholder="Escribe una breve descripción...",
        height=150,
        help="Máximo 500 caracteres"
    )

with col2:
    redes_seleccionadas = st.multiselect(
        "Redes Sociales Activas",
        ["Facebook", "Instagram", "TikTok", "Twitter/X", "LinkedIn", "YouTube"],
        default=["Facebook", "Instagram"]
    )
    
    if redes_seleccionadas:
        st.success(f"✅ {len(redes_seleccionadas)} plataforma(s) seleccionada(s)")

st.markdown("---")

# ============================================
# SECCIÓN 3: MÉTRICAS Y KPIS
# ============================================

st.markdown("## 📊 Métricas y KPIs")

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        label="Seguidores Totales",
        value="15,420",
        delta="+1,234",
        delta_color="normal"
    )

with metric2:
    st.metric(
        label="Engagement Rate",
        value="4.5%",
        delta="+0.3%",
        delta_color="normal"
    )

with metric3:
    st.metric(
        label="Alcance Mensual",
        value="45.2K",
        delta="+5.1K",
        delta_color="normal"
    )

with metric4:
    st.metric(
        label="Interacciones",
        value="2,850",
        delta="-120",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================
# SECCIÓN 4: GRÁFICOS
# ============================================

st.markdown("## 📈 Gráficos con Tema")

# Datos de ejemplo
fechas = pd.date_range(start='2024-01-01', periods=30, freq='D')
df_ejemplo = pd.DataFrame({
    'Fecha': fechas,
    'Seguidores': [5000 + i*50 + (i%7)*30 for i in range(30)],
    'Engagement': [3.5 + (i%10)*0.2 for i in range(30)]
})

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Crecimiento de Seguidores")
    fig_seguidores = px.line(
        df_ejemplo,
        x='Fecha',
        y='Seguidores',
        title='Seguidores en el Tiempo'
    )
    
    # Adaptar colores según tema
    if tema_actual == 'Oscuro':
        fig_seguidores.update_layout(
            plot_bgcolor='#1E2228',
            paper_bgcolor='#1E2228',
            font_color='#FAFAFA'
        )
    else:
        fig_seguidores.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#1A1A1A'
        )
    
    st.plotly_chart(fig_seguidores, use_container_width=True)

with col2:
    st.markdown("### Engagement Rate")
    fig_engagement = px.bar(
        df_ejemplo.tail(10),
        x='Fecha',
        y='Engagement',
        title='Engagement últimos 10 días'
    )
    
    if tema_actual == 'Oscuro':
        fig_engagement.update_layout(
            plot_bgcolor='#1E2228',
            paper_bgcolor='#1E2228',
            font_color='#FAFAFA'
        )
    else:
        fig_engagement.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#1A1A1A'
        )
    
    st.plotly_chart(fig_engagement, use_container_width=True)

st.markdown("---")

# ============================================
# SECCIÓN 5: TABLA DE DATOS
# ============================================

st.markdown("## 📋 Tabla de Datos")

df_tabla = pd.DataFrame({
    'Plataforma': ['Facebook', 'Instagram', 'TikTok', 'LinkedIn'],
    'Seguidores': [12500, 8900, 15200, 3400],
    'Engagement': ['4.5%', '6.2%', '8.1%', '3.2%'],
    'Crecimiento': ['+12%', '+18%', '+25%', '+8%']
})

st.dataframe(df_tabla, use_container_width=True)

st.markdown("---")

# ============================================
# SECCIÓN 6: BOTONES Y ACCIONES
# ============================================

st.markdown("## 🎯 Botones y Acciones")

btn1, btn2, btn3, btn4 = st.columns(4)

with btn1:
    if st.button("✅ Guardar Datos", use_container_width=True):
        st.success("Datos guardados correctamente")

with btn2:
    if st.button("📊 Generar Reporte", use_container_width=True):
        st.info("Generando reporte...")

with btn3:
    if st.button("🔄 Actualizar", use_container_width=True):
        st.warning("Actualizando datos...")

with btn4:
    if st.button("❌ Cancelar", use_container_width=True):
        st.error("Operación cancelada")

st.markdown("---")

# ============================================
# SECCIÓN 7: INFORMACIÓN DEL TEMA
# ============================================

st.markdown("## ℹ️ Información del Sistema")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.info(f"""
    **Tema Activo:** {tema_actual}
    
    **Características:**
    - ✅ Contraste WCAG AA
    - ✅ Fuentes 16px mínimo
    - ✅ Inputs unificados
    - ✅ Responsive design
    - ✅ Focus states visibles
    """)

with info_col2:
    st.success(f"""
    **Paleta de Colores ({tema_actual}):**
    
    {'**Fondo:** #0E1117' if tema_actual == 'Oscuro' else '**Fondo:** #FFFFFF'}
    {'**Texto:** #FAFAFA' if tema_actual == 'Oscuro' else '**Texto:** #1A1A1A'}
    {'**Inputs:** #1E2228' if tema_actual == 'Oscuro' else '**Inputs:** #FFFFFF'}
    **Primario:** {'#4A90E2' if tema_actual == 'Oscuro' else '#003696'}
    **Acento:** #FFB81C
    """)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 20px;'>
    <p>🎨 <strong>Sistema de Temas Dinámicos v1.0</strong></p>
    <p>Desarrollado por Equipo CHAMPILEAKS | Enero 2026</p>
    <p>Para más información, consulta <code>THEME_USAGE.md</code></p>
</div>
""", unsafe_allow_html=True)
