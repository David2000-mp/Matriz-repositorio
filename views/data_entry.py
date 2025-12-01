import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import save_batch, load_data, COLEGIOS_MARISTAS
from components.styles import inject_custom_css

def render():
    """Renderiza la vista de captura de datos (Manual y Masiva)."""
    inject_custom_css()
    
    st.title("📝 Captura de Datos")
    st.markdown("---")

    # Crear pestañas principales
    tab_manual, tab_masiva = st.tabs(["✍️ Captura Manual", "📂 Carga Masiva (Excel/CSV)"])

    # ==========================================
    # PESTAÑA 1: CAPTURA MANUAL (Tu código original)
    # ==========================================
    with tab_manual:
        st.subheader("Registro Individual")
        
        # Cargar datos para validaciones
        try:
            cuentas, _ = load_data()
        except:
            cuentas = pd.DataFrame()

        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de Institución
            lista_instituciones = list(COLEGIOS_MARISTAS.keys())
            entidad = st.selectbox("Institución", lista_instituciones)
            
            # Selector de Plataforma (Dinámico según institución)
            redes_disponibles = list(COLEGIOS_MARISTAS[entidad].keys())
            plataforma = st.selectbox("Plataforma", redes_disponibles)
            
            # Mostrar usuario automático
            usuario = COLEGIOS_MARISTAS[entidad][plataforma]
            st.caption(f"Cuenta: **{usuario}**")

        with col2:
            fecha = st.date_input("Fecha del Reporte", datetime.now())

        st.markdown("### Métricas")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            seguidores = st.number_input("Seguidores Totales", min_value=0, step=1)
            alcance = st.number_input("Alcance / Impresiones", min_value=0, step=1)
        
        with c2:
            interacciones = st.number_input("Interacciones Totales", min_value=0, step=1)
            likes = st.number_input("Likes Promedio", min_value=0.0, step=0.1)
        
        with c3:
            # Cálculo automático de engagement sugerido
            eng_sugerido = 0.0
            if seguidores > 0:
                eng_sugerido = (interacciones / seguidores) * 100
            
            engagement = st.number_input("Engagement Rate (%)", min_value=0.0, step=0.01, value=eng_sugerido)
            if eng_sugerido > 0:
                st.caption(f"Calculado: {eng_sugerido:.2f}%")

        # Botón de Guardado Manual
        if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
            if seguidores > 0:
                datos = [{
                    "entidad": entidad,
                    "plataforma": plataforma,
                    "usuario_red": usuario,
                    "fecha": fecha.strftime('%Y-%m-%d'),
                    "seguidores": seguidores,
                    "alcance": alcance,
                    "interacciones": interacciones,
                    "likes_promedio": likes,
                    "engagement_rate": engagement
                }]
                
                with st.spinner("Guardando en la nube..."):
                    save_batch(datos)
                st.success("✅ ¡Registro guardado exitosamente!")
                st.balloons()
            else:
                st.error("⚠️ Los seguidores no pueden ser 0")

    # ==========================================
    # PESTAÑA 2: CARGA MASIVA (Tu código nuevo)
    # ==========================================
    with tab_masiva:
        st.subheader("Importar Datos Históricos")
        st.info("Sube un archivo Excel o CSV con las columnas: `entidad`, `plataforma`, `fecha`, `seguidores`, `alcance`, `interacciones`.")
        st.markdown("---")
        st.markdown("### 1. Selecciona tu archivo de datos masivos")
        archivo = st.file_uploader(
            "[📂] Haz clic aquí para subir tu archivo CSV o Excel",
            type=["csv", "xlsx"],
            accept_multiple_files=False
        )

        if archivo is not None:
            st.markdown("---")
            st.markdown("### 2. Vista previa y validación")
            # Detectar tipo de archivo y leer con pandas
            try:
                if archivo.name.lower().endswith(".csv"):
                    df = pd.read_csv(archivo)
                elif archivo.name.lower().endswith(".xlsx"):
                    df = pd.read_excel(archivo)
                else:
                    st.error("Formato de archivo no soportado.")
                    st.stop()
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
                st.stop()

            # Normalizar nombres de columnas (eliminar espacios y minúsculas)
            df.columns = [str(col).strip().lower() for col in df.columns]

            # Columnas mínimas requeridas para que el sistema funcione
            columnas_requeridas = ['entidad', 'plataforma', 'fecha', 'seguidores']
            faltantes = [col for col in columnas_requeridas if col not in df.columns]

            if faltantes:
                st.error(f"❌ Faltan las siguientes columnas requeridas en tu archivo: {faltantes}")
                st.markdown("**Ejemplo de estructura esperada:**")
                st.code("entidad, plataforma, fecha, seguidores, alcance, interacciones")
            else:
                st.success(f"✅ Archivo válido. Se detectaron {len(df)} registros.")
                st.markdown("---")
                st.markdown("### 3. Confirma y procesa tu carga masiva")
                st.dataframe(df.head(10), width='stretch')
                st.markdown("---")
                # Botón destacado y centrado
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    procesar = st.button("🚀 PROCESAR Y SUBIR A LA NUBE", type="primary", use_container_width=True)
                if procesar:
                    try:
                        # Convertir a formato de lista de diccionarios para save_batch
                        if 'fecha' in df.columns:
                            df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
                        datos_masivos = df.to_dict('records')
                        with st.spinner(f"Procesando {len(datos_masivos)} registros. Esto puede tardar unos segundos..."):
                            save_batch(datos_masivos)
                        st.success(f"¡Éxito! {len(datos_masivos)} registros han sido procesados y guardados.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Hubo un error al procesar el lote: {e}")
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
                width='stretch',
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
