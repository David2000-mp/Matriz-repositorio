"""
Vista de Configuración para CHAMPILYTICS.
Administración del sistema, simulación de datos y herramientas avanzadas.
Versión Final corregida: Nombres Reales en Reportes.
"""

import streamlit as st
import pandas as pd
import os
import logging

# Importaciones seguras
import utils.data_manager as dm 
from utils import save_batch, reset_db, COLEGIOS_MARISTAS
from utils.helpers import simular
from utils.report_generator import ReportBuilder
from utils.data_manager import CUENTAS_CSV

def render():
    """
    Renderiza la página de configuración y administración.
    """
    st.title("⚙️ CONFIGURACIÓN Y ADMINISTRACIÓN")
    st.caption("🛠️ Herramientas de Gestión y Personalización del Sistema")
    st.markdown("---")

    # Implementación de pestañas
    tab_gestion, tab_reportes, tab_catalogo = st.tabs([
        "⚙️ Gestión de Datos", 
        "📄 Exportar Reportes", 
        "📋 Catálogo de Instituciones"
    ])

    # ==============================================================================
    # PESTAÑA 1: GESTIÓN DE DATOS (Simulador y Reset)
    # ==============================================================================
    with tab_gestion:
        st.markdown("### 🧬 Simulador y Control de Datos")
        st.info("Herramientas para generar datos de prueba o limpiar la base de datos.")
        
        col_info1, col_info2 = st.columns(2)
        col_info1.metric("Instituciones Registradas", len(COLEGIOS_MARISTAS))
        total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
        col_info2.metric("Cuentas Totales Monitoreadas", total_cuentas)
        
        st.divider()
        
        # --- Sección Simulador ---
        st.subheader("🎲 Simulador de Datos Históricos")
        meses = st.slider("📅 Meses a generar", 1, 12, 6, help="Genera datos falsos para pruebas.")
        registros_estimados = total_cuentas * meses
        
        if st.button("🚀 Generar Datos de Prueba", use_container_width=True, type="primary"):
            with st.spinner(f"⏳ Creando {meses} meses de historia para {total_cuentas} cuentas..."):
                # Generar datos
                datos, metas = simular(n=registros_estimados, colegios_maristas=COLEGIOS_MARISTAS, generar_metas=True)
                
                # Guardar métricas (batch)
                save_batch(datos)
                
                # Guardar metas individuales
                for meta in metas:
                    dm.save_config(
                        entidad=meta["entidad"], 
                        meta_seguidores=meta["meta_seguidores"], 
                        meta_engagement=meta["meta_engagement"]
                    )
                    
            st.success(f"🎉 ¡{len(datos):,} registros generados exitosamente!")
            st.balloons()
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # --- Sección Reset ---
        st.subheader("🗑️ Zona de Peligro")
        col_reset1, col_reset2 = st.columns([3, 1])
        with col_reset1:
            st.warning("Esta acción eliminará permanentemente TODOS los datos (métricas y configuraciones). Úsala si ves IDs raros en los nombres.")
        with col_reset2:
            if st.button("Resetear Base de Datos", type="secondary", use_container_width=True):
                reset_db()
                st.cache_data.clear()
                st.success("✅ Base de datos reiniciada.")
                st.rerun()

    # ==============================================================================
    # PESTAÑA 2: REPORTES (Versión Blindada contra KeyError)
    # ==============================================================================
    with tab_reportes:
        st.markdown("### 📄 Generador de Reportes PDF")
        st.info("Descarga informes ejecutivos con análisis automático.")

        # 1. Carga Segura de Datos
        cuentas, metricas = dm.load_data()

        # VALIDACIÓN CRÍTICA: Verificar que 'cuentas' tenga la información base
        if cuentas.empty or 'entidad' not in cuentas.columns:
            st.error("⚠️ Error Crítico: La tabla de 'Cuentas' está vacía o malformada. No se pueden asociar nombres.")
            if not cuentas.empty:
                st.write("Columnas detectadas en Cuentas:", cuentas.columns.tolist())
            st.stop()

        if metricas.empty:
            st.warning("⚠️ No hay métricas registradas aún. Ve a la pestaña 'Gestión de Datos' para generar datos.")
        else:
            # 2. Cruce de Datos (Merge) INTELIGENTE
            # ---------------------------------------------------------
            # Paso A: Estandarizar tipos para evitar errores de merge
            if 'id_cuenta' in metricas.columns:
                metricas['id_cuenta'] = metricas['id_cuenta'].astype(str).str.strip()
            if 'id_cuenta' in cuentas.columns:
                cuentas['id_cuenta'] = cuentas['id_cuenta'].astype(str).str.strip()

            # Paso B: Evitar duplicidad de columnas (El arreglo del KeyError)
            # Si métricas ya tiene 'entidad', la borramos para usar la versión oficial de 'cuentas'
            if 'entidad' in metricas.columns:
                metricas = metricas.drop(columns=['entidad'])

            # Paso C: Realizar la fusión
            # Usamos left join para mantener todas las métricas y pegarles el nombre de la entidad
            df_completo = pd.merge(
                metricas, 
                cuentas[['id_cuenta', 'entidad']], 
                on="id_cuenta", 
                how="left"
            )
            
            # Paso D: Rellenar nulos si alguna métrica quedó huérfana
            if 'entidad' in df_completo.columns:
                df_completo['entidad'] = df_completo['entidad'].fillna("Desconocido")
            else:
                # Si por algún milagro sigue fallando, forzamos la creación
                df_completo['entidad'] = "Desconocido"
            # ---------------------------------------------------------

            # 3. Interfaz de Configuración
            col_conf, col_prev = st.columns([1, 2])

            with col_conf:
                st.subheader("Configuración")
                
                # --- FILTRO INTELIGENTE DE NOMBRES ---
                raw_entidades = sorted(df_completo['entidad'].unique().tolist())
                
                # Filtrar nombres inválidos o vacíos
                lista_entidades = [
                    str(e) for e in raw_entidades 
                    if e and str(e).lower() != "nan" and str(e) != "Desconocido"
                ]
                
                if not lista_entidades:
                    st.warning("No se encontraron instituciones con datos.")
                    st.stop()

                entidad_selec = st.selectbox("Selecciona una institución:", lista_entidades)

                if not entidad_selec:
                    st.stop()

                st.markdown("**Secciones a incluir:**")
                inc_kpis = st.checkbox("Tabla de KPIs", value=True)
                inc_graf = st.checkbox("Gráficas de Tendencia", value=True)
                inc_analisis = st.checkbox("Análisis (Texto Automático)", value=True)

                # Botón Generar
                if st.button("Generar PDF", type="primary", use_container_width=True):
                    with st.spinner("🔨 Construyendo reporte..."):
                        # Filtrar datos por la entidad seleccionada
                        df_filtrado = df_completo[df_completo["entidad"] == entidad_selec].copy()
                        
                        # Ordenar por fecha
                        if 'fecha' in df_filtrado.columns:
                            df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'])
                            df_filtrado = df_filtrado.sort_values('fecha')

                        # Instanciar Builder con manejo de errores
                        try:
                            # Asegurar que pasamos un string limpio
                            nombre_limpio = str(entidad_selec).strip()
                            builder = ReportBuilder(df=df_filtrado, entity_name=nombre_limpio)
                            
                            secciones = []
                            if inc_kpis: secciones.append("kpis")
                            if inc_graf: secciones.append("graficas")
                            if inc_analisis: secciones.append("analisis")

                            pdf_bytes = builder.generate(secciones)

                            # Nombre de archivo seguro
                            file_name_safe = f"Reporte_{nombre_limpio.replace(' ', '_')}.pdf"

                            st.success("✅ Reporte listo")
                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=pdf_bytes,
                                file_name=file_name_safe,
                                mime="application/pdf"
                            )
                        except Exception as e:
                            st.error(f"Error generando PDF: {e}")
                            # Imprimir el error en consola para debug
                            print(f"DEBUG ERROR PDF: {e}")

            with col_prev:
                st.subheader("Vista Previa de Datos")
                df_vista = df_completo[df_completo["entidad"] == entidad_selec]
                
                cols_deseadas = ['fecha', 'plataforma', 'seguidores', 'engagement_rate']
                cols_existentes = [c for c in cols_deseadas if c in df_vista.columns]
                
                if cols_existentes:
                    st.dataframe(
                        df_vista[cols_existentes].head(10), 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning("Faltan columnas clave para la vista previa.")
                
                st.caption(f"Registros encontrados: {len(df_vista)}")

    # ==============================================================================
    # PESTAÑA 3: CATÁLOGO DE INSTITUCIONES
    # ==============================================================================
    with tab_catalogo:
        st.markdown("### 📋 Directorio de Instituciones")
        
        buscar_cat = st.text_input("🔎 Buscar institución", placeholder="Escribe el nombre del colegio...")
        
        instituciones_filtradas = {
            k: v for k, v in COLEGIOS_MARISTAS.items()
            if not buscar_cat or buscar_cat.lower() in k.lower()
        }

        if not instituciones_filtradas:
            st.warning("No se encontraron resultados.")
        else:
            st.caption(f"Mostrando {len(instituciones_filtradas)} instituciones")
            for entidad, redes in instituciones_filtradas.items():
                with st.expander(f"🏛️ {entidad} ({len(redes)} canales)"):
                    for plat, usuario in redes.items():
                        c1, c2 = st.columns([1, 3])
                        c1.markdown(f"**{plat}**")
                        c2.code(usuario)
        
        st.divider()

        with st.expander("➕ Agregar Nueva Institución al Catálogo"):
            st.info("Esto agregará la institución a la base de datos de cuentas.")
            new_name = st.text_input("Nombre de la Institución")
            new_redes = st.text_area("Redes (Formato: Facebook:usuario, Instagram:usuario)", height=70)
            
            if st.button("Guardar Nueva Institución"):
                if new_name and new_redes:
                    try:
                        # Parsear el texto a diccionario
                        redes_dict = {}
                        for item in new_redes.split(","):
                            if ":" in item:
                                plat, user = item.split(":", 1)
                                redes_dict[plat.strip()] = user.strip()
                        
                        if not redes_dict:
                            st.error("Formato incorrecto. Usa: 'Plataforma:Usuario'")
                        else:
                            # USAR LA NUEVA FUNCIÓN DE DATA_MANAGER
                            exito = dm.registrar_nuevas_cuentas(new_name, redes_dict)
                            
                            if exito:
                                # Actualizar variable global en memoria para que se vea reflejado al instante
                                COLEGIOS_MARISTAS[new_name] = redes_dict 
                                st.success(f"✅ {new_name} agregada correctamente.")
                                st.rerun() # Recargar la página para ver cambios
                            else:
                                st.error("Hubo un error al guardar en la base de datos.")

                    except Exception as e:
                        st.error(f"Error de formato: {e}")
                else:
                    st.error("Por favor completa todos los campos.")

        with st.expander("🗑️ Eliminar Institución del Catálogo"):
            st.warning("Esta acción eliminará permanentemente la institución seleccionada del catálogo.")
            instituciones_existentes = list(COLEGIOS_MARISTAS.keys())

            if not instituciones_existentes:
                st.info("No hay instituciones para eliminar.")
            else:
                institucion_a_eliminar = st.selectbox("Selecciona la institución a eliminar:", instituciones_existentes)

                if st.button("Eliminar Institución", type="primary"):
                    try:
                        # Eliminar de la variable global
                        if institucion_a_eliminar in COLEGIOS_MARISTAS:
                            del COLEGIOS_MARISTAS[institucion_a_eliminar]

                        # Eliminar del archivo CSV local
                        if CUENTAS_CSV.exists():
                            cuentas_df = pd.read_csv(CUENTAS_CSV)
                            cuentas_df = cuentas_df[cuentas_df['entidad'] != institucion_a_eliminar]
                            cuentas_df.to_csv(CUENTAS_CSV, index=False, encoding='utf-8-sig')

                        # Eliminar de Google Sheets
                        spreadsheet = dm.conectar_sheets()
                        if spreadsheet:
                            try:
                                sheet_cuentas = spreadsheet.worksheet('cuentas')
                                data = sheet_cuentas.get_all_records()
                                cuentas_df = pd.DataFrame(data)
                                cuentas_df = cuentas_df[cuentas_df['entidad'] != institucion_a_eliminar]
                                sheet_cuentas.clear()
                                sheet_cuentas.append_row(dm.COLS_CUENTAS)
                                sheet_cuentas.append_rows(cuentas_df.values.tolist())
                            except Exception as e:
                                st.warning("No se pudo actualizar Google Sheets. Cambios aplicados solo localmente.")
                                dm.logger.error(f"Error eliminando institución de Sheets: {e}")

                        st.success(f"✅ La institución '{institucion_a_eliminar}' ha sido eliminada correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar la institución: {e}")