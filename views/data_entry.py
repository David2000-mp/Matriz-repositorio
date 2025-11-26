"""
Vista de Captura Manual de Datos para CHAMPILYTICS.
Formulario para ingreso manual de métricas.
"""

import streamlit as st
import pandas as pd
from datetime import date
import logging
from utils import load_data, save_batch, get_id, COLEGIOS_MARISTAS

def render():
    """
    Renderiza el formulario de captura manual de datos con validación.
    """
    st.title("CAPTURA MANUAL DE DATOS")
    st.caption("Registro de Métricas por Cuenta")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.info("💡 **Instrucciones**: Selecciona la institución y plataforma, ingresa las métricas del período y guarda.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario de captura
    with st.form("capture_form", clear_on_submit=True):
        st.markdown("### Información de la Cuenta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            entidad = st.selectbox(
                "Institución Marista",
                list(COLEGIOS_MARISTAS.keys()),
                help="Selecciona la institución educativa"
            )
        
        with col2:
            if entidad:
                plataformas_disponibles = list(COLEGIOS_MARISTAS[entidad].keys())
                plataforma = st.selectbox(
                    "Plataforma Social",
                    plataformas_disponibles,
                    help="Selecciona la red social"
                )
                # Obtener usuario automáticamente
                usuario_red = COLEGIOS_MARISTAS[entidad][plataforma]
            else:
                plataforma = None
                usuario_red = ""
        
        st.divider()
        st.markdown("### Métricas del Período")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            seguidores = st.number_input(
                "Seguidores Totales",
                min_value=0,
                value=0,
                step=10,
                help="Número total de seguidores al final del período"
            )
        
        with col2:
            alcance = st.number_input(
                "Alcance Total",
                min_value=0,
                value=0,
                step=10,
                help="Número de personas únicas que vieron el contenido"
            )
        
        with col3:
            interacciones = st.number_input(
                "Interacciones Totales",
                min_value=0,
                value=0,
                step=1,
                help="Suma de likes, comentarios, shares, etc."
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            likes_promedio = st.number_input(
                "Likes Promedio por Post",
                min_value=0,
                value=0,
                step=1,
                help="Promedio de likes por publicación"
            )
        
        with col2:
            fecha_captura = st.date_input(
                "Fecha del Reporte",
                value=date.today(),
                help="Fecha del período reportado"
            )
        
        st.divider()
        
        # Mostrar preview del engagement rate calculado
        if seguidores > 0:
            engagement_preview = (interacciones / seguidores * 100)
            st.metric(
                "Engagement Rate Calculado",
                f"{engagement_preview:.2f}%",
                help="Se calcula automáticamente: (Interacciones / Seguidores) × 100"
            )
        
        submitted = st.form_submit_button("💾 Guardar Datos", use_container_width=True, type="primary")
        
        if submitted:
            # Validación de datos
            if seguidores == 0:
                st.error("❌ Error: El número de seguidores no puede ser 0")
            elif not entidad or not plataforma:
                st.error("❌ Error: Debes seleccionar una institución y plataforma")
            else:
                try:
                    # Preparar datos para guardar
                    cuentas_cache, _ = load_data()
                    
                    # Obtener o crear ID de cuenta
                    id_cuenta = get_id(entidad, plataforma, usuario_red, df_cuentas_cache=cuentas_cache)
                    
                    # Calcular engagement rate
                    engagement_rate = round((interacciones / seguidores * 100), 2) if seguidores > 0 else 0
                    
                    # Crear registro
                    nuevo_registro = [{
                        "id_cuenta": id_cuenta,
                        "entidad": entidad,
                        "plataforma": plataforma,
                        "usuario_red": usuario_red,
                        "fecha": pd.to_datetime(fecha_captura),
                        "seguidores": int(seguidores),
                        "alcance": int(alcance),
                        "interacciones": int(interacciones),
                        "likes_promedio": int(likes_promedio),
                        "engagement_rate": engagement_rate
                    }]
                    
                    # Guardar en base de datos
                    with st.spinner("Guardando datos..."):
                        save_batch(nuevo_registro)
                    
                    st.success(f"✅ Datos guardados exitosamente para **{entidad}** ({plataforma})")
                    
                    # Mostrar resumen
                    st.markdown("#### Resumen del Registro")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Seguidores", f"{seguidores:,}")
                    col2.metric("Interacciones", f"{interacciones:,}")
                    col3.metric("Engagement", f"{engagement_rate:.2f}%")
                    
                    logging.info(f"Captura manual: {entidad} - {plataforma} - {fecha_captura}")
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar los datos: {e}")
                    logging.error(f"Error en captura manual: {e}")
    
    # Mostrar últimos registros capturados
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Últimos Registros")
    
    try:
        cuentas, metricas = load_data()
        
        if not metricas.empty:
            # Merge para mostrar datos completos
            df_recent = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
            df_recent = df_recent.sort_values('fecha', ascending=False).head(10)
            
            # Preparar para display
            df_display = df_recent[['fecha', 'entidad', 'plataforma', 'seguidores', 'interacciones', 'engagement_rate']].copy()
            df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "fecha": "Fecha",
                    "entidad": "Institución",
                    "plataforma": "Plataforma",
                    "seguidores": st.column_config.NumberColumn("Seguidores", format="%d"),
                    "interacciones": st.column_config.NumberColumn("Interacciones", format="%d"),
                    "engagement_rate": st.column_config.NumberColumn("ER %", format="%.2f")
                }
            )
        else:
            st.info("No hay registros previos. Comienza capturando datos arriba.")
    
    except Exception as e:
        st.warning(f"No se pudieron cargar los registros previos: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
