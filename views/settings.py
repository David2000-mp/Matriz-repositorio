"""
Vista de Configuración para CHAMPILEAKS.
Administración del sistema, simulación de datos y herramientas avanzadas.
Versión Final corregida: Nombres Reales en Reportes.
"""

import streamlit as st
import pandas as pd
import os
import logging

# Importaciones seguras
import utils.data_manager as dm
from utils import save_batch, COLEGIOS_MARISTAS
from utils.helpers import simular
from utils.report_generator import ReportBuilder
from utils.data_loader import CUENTAS_CSV


def render(df=None):
    """
    Renderiza la página de configuración y administración.

    Acepta opcionalmente un `df` para compatibilidad con el entrypoint global.
    """
    st.title("⚙️ CONFIGURACIÓN Y ADMINISTRACIÓN")
    st.caption("🛠️ Herramientas de Gestión y Personalización del Sistema")
    st.markdown("---")

    # Implementación de pestañas
    tab_gestion, tab_reportes, tab_catalogo = st.tabs(
        ["⚙️ Gestión de Datos", "📄 Exportar Reportes", "📋 Catálogo de Instituciones"]
    )

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
        meses = st.slider(
            "📅 Meses a generar", 1, 12, 6, help="Genera datos falsos para pruebas."
        )
        registros_estimados = total_cuentas * meses

        if st.button(
            "🚀 Generar Datos de Prueba", width='stretch', type="primary"
        ):
            with st.spinner(
                f"⏳ Creando {meses} meses de historia para {total_cuentas} cuentas..."
            ):
                # Generar datos
                resultados_simulacion = simular(
                    n=registros_estimados,
                    colegios_maristas=COLEGIOS_MARISTAS,
                    generar_metas=True,
                )

                # Desempaquetado flexible para compatibilidad con distintas firmas
                datos = []
                metas = []
                try:
                    if isinstance(resultados_simulacion, (list, tuple)):
                        if len(resultados_simulacion) == 2:
                            datos, metas = resultados_simulacion
                        elif len(resultados_simulacion) == 3:
                            # Forma: (cuentas, metricas, metas) -> tomamos metricas/metas
                            datos = resultados_simulacion[0]
                            metas = resultados_simulacion[2]
                        else:
                            # Assume it's a flat list of metric dicts
                            datos = list(resultados_simulacion)
                            metas = []
                    else:
                        # Single-object return (e.g., list of dicts)
                        datos = resultados_simulacion
                        metas = []
                except Exception as e:
                    datos = resultados_simulacion
                    metas = []

                # Guardar métricas (batch)
                if isinstance(datos, pd.DataFrame) and not datos.empty:
                    save_batch(datos)  # type: ignore
                else:
                    st.warning("No se generaron datos para guardar")

                # Guardar metas individuales si existen
                # Nota: save_config no está disponible en dm, usar otro método si es necesario
                # for meta in metas:
                #     try:
                #         dm.save_config(
                #             entidad=meta["entidad"],
                #             meta_seguidores=meta["meta_seguidores"],
                #             meta_engagement=meta["meta_engagement"],
                #         )
                #     except Exception:
                #         # No interrumpir el flujo si una meta falla
                #         pass

            st.success(f"🎉 ¡{len(datos):,} registros generados exitosamente!")
            st.balloons()
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # --- Sección Reset ---
        st.subheader("🗑️ Zona de Peligro")
        col_reset1, col_reset2 = st.columns([3, 1])
        with col_reset1:
            st.warning(
                "⚠️ Esta acción eliminará permanentemente TODOS los datos (métricas y cuentas) tanto en Google Sheets como en archivos locales. Los encabezados se preservarán."
            )
        with col_reset2:
            if st.button(
                "🗑️ Resetear Base de Datos", type="secondary", width='stretch'
            ):
                from utils.data_manager import reset_db
                
                with st.status("Ejecutando reset completo..."):
                    success = reset_db()
                
                if success:
                    st.success("✅ Base de datos reseteada exitosamente. Google Sheets y archivos CSV limpiados.")
                    st.info("ℹ️ Los encabezados han sido preservados. Puedes comenzar a cargar datos nuevamente.")
                else:
                    st.error("❌ Error durante el reset. Verifica los logs.")
                
                # Recargar UI para reflejar cambios
                st.rerun()

        st.divider()

        # --- Sección Respaldo ---
        st.subheader("💾 Respaldo de Base de Datos")
        st.info("Descarga un respaldo completo de todos los datos locales (CSV) y configuraciones.")

        if st.button("📦 Generar Respaldo Completo", type="primary"):
            import zipfile
            import io
            from pathlib import Path
            
            with st.spinner("Generando respaldo..."):
                # Intentar cargar datos de Google Sheets
                try:
                    cuentas_sheets, metricas_sheets = dm.load_data()
                    sheets_ok = True
                    st.info("✅ Datos de Google Sheets cargados")
                except Exception as e:
                    st.warning(f"⚠️ No se pudieron cargar datos de Google Sheets: {e}. Usando solo datos locales.")
                    sheets_ok = False
                    cuentas_sheets = pd.DataFrame()
                    metricas_sheets = pd.DataFrame()
                
                # Archivos locales
                archivos_respaldo = {
                    "local_cuentas.csv": dm.CUENTAS_CSV,
                    "local_metricas.csv": dm.METRICAS_CSV,
                }
                
                # Crear ZIP en memoria
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Agregar archivos locales
                    for nombre, ruta in archivos_respaldo.items():
                        if ruta.exists():
                            zip_file.write(ruta, arcname=f"local/{nombre}")
                            st.info(f"✅ Incluido local: {nombre}")
                        else:
                            st.warning(f"⚠️ Archivo local no encontrado: {nombre}")
                    
                    # Agregar datos de Sheets si disponibles
                    if sheets_ok:
                        # Cuentas de Sheets
                        if not cuentas_sheets.empty:
                            csv_cuentas = cuentas_sheets.to_csv(index=False)
                            zip_file.writestr("sheets/cuentas_sheets.csv", csv_cuentas)
                            st.info("✅ Incluido Sheets: cuentas_sheets.csv")
                        
                        # Métricas de Sheets
                        if not metricas_sheets.empty:
                            csv_metricas = metricas_sheets.to_csv(index=False)
                            zip_file.writestr("sheets/metricas_sheets.csv", csv_metricas)
                            st.info("✅ Incluido Sheets: metricas_sheets.csv")
                        
                        # Comentarios
                        try:
                            comentarios = dm.load_comments()
                            if not comentarios.empty:
                                csv_comentarios = comentarios.to_csv(index=False)
                                zip_file.writestr("sheets/comentarios_sheets.csv", csv_comentarios)
                                st.info("✅ Incluido Sheets: comentarios_sheets.csv")
                        except Exception:
                            st.warning("⚠️ No se pudieron cargar comentarios de Sheets")
                        
                        # Usernames editados
                        try:
                            usernames = dm.load_usernames_editados()
                            if not usernames.empty:
                                csv_usernames = usernames.to_csv(index=False)
                                zip_file.writestr("sheets/usernames_editados_sheets.csv", csv_usernames)
                                st.info("✅ Incluido Sheets: usernames_editados_sheets.csv")
                        except Exception:
                            st.warning("⚠️ No se pudieron cargar usernames editados de Sheets")
                    
                    # Agregar metadata
                    timestamp = pd.Timestamp.now()
                    metadata = f"""Respaldo generado el: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Sistema: Social Media Matrix
Versión: v2.0
Fuente de datos:
- Local CSV: {'✅' if dm.CUENTAS_CSV.exists() else '❌'} cuentas, {'✅' if dm.METRICAS_CSV.exists() else '❌'} métricas
- Google Sheets: {'✅ Conectado' if sheets_ok else '❌ Sin conexión'}

Registros:
Local:
- Cuentas: {len(pd.read_csv(dm.CUENTAS_CSV)) if dm.CUENTAS_CSV.exists() else 0}
- Métricas: {len(pd.read_csv(dm.METRICAS_CSV)) if dm.METRICAS_CSV.exists() else 0}

Google Sheets:
- Cuentas: {len(cuentas_sheets)}
- Métricas: {len(metricas_sheets)}
- Comentarios: {len(dm.load_comments()) if sheets_ok else 0}
- Usernames editados: {len(dm.load_usernames_editados()) if sheets_ok else 0}"""
                    zip_file.writestr("README.txt", metadata)
                
                zip_buffer.seek(0)
                
                # Botón de descarga
                st.download_button(
                    label="⬇️ Descargar Respaldo Completo (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"respaldo_completo_social_media_matrix_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    type="primary"
                )
                
                st.success("✅ Respaldo generado exitosamente")
                st.balloons()

        st.divider()
        st.subheader("📤 Cargar métricas por publicación (CSV)")
        st.info(
            "Sube un archivo CSV con métricas por publicación. Columnas esperadas: `fecha`, `seguidores`, `alcance`, `interacciones`, y `id_cuenta` o (`entidad`,`plataforma`,`usuario_red`)."
        )

        with st.expander("Subir CSV de publicaciones"):
            uploaded = st.file_uploader(
                "Selecciona CSV de métricas por publicación",
                type=["csv"],
                accept_multiple_files=False,
            )

            if uploaded is not None:
                try:
                    df_posts = pd.read_csv(uploaded)
                except Exception as e:
                    st.error(f"Error leyendo CSV: {e}")
                    df_posts = None

                if df_posts is not None:
                    st.write("Vista previa:")
                    st.dataframe(df_posts.head(5))

                    # Preparar datos: requerimos fecha y métricas numéricas
                    if "fecha" not in df_posts.columns:
                        st.error("El CSV debe contener la columna 'fecha'.")
                    else:
                        # Mapear id_cuenta si hace falta
                        if "id_cuenta" not in df_posts.columns:
                            if all(c in df_posts.columns for c in [
                                "entidad",
                                "plataforma",
                                "usuario_red",
                            ]):
                                # Crear/recuperar id_cuenta por fila
                                cuentas_cache, _ = dm.load_data()

                                def _map_id(row):
                                    try:
                                        return dm.get_id(
                                            entidad=str(row["entidad"]),
                                            plataforma=str(row["plataforma"]),
                                            usuario_red=str(row["usuario_red"]),
                                            df_cuentas_cache=cuentas_cache,
                                        )
                                    except Exception:
                                        return None

                                df_posts["id_cuenta"] = df_posts.apply(_map_id, axis=1)  # type: ignore
                            else:
                                st.error(
                                    "El CSV debe contener 'id_cuenta' o las columnas 'entidad','plataforma','usuario_red' para mapear IDs."
                                )

                        # Verificar que ahora exista id_cuenta
                        if "id_cuenta" in df_posts.columns and not df_posts["id_cuenta"].isna().all():
                            # Normalizar y convertir tipos
                            df_posts["fecha"] = pd.to_datetime(df_posts["fecha"], errors="coerce")
                            for col in ["seguidores", "alcance", "interacciones", "likes_promedio"]:
                                if col in df_posts.columns:
                                    df_posts[col] = pd.to_numeric(df_posts[col], errors="coerce").fillna(0)

                            # Construir lista de dicts para save_batch
                            datos_para_guardar = []
                            for _, r in df_posts.iterrows():
                                if pd.isna(r.get("fecha")):
                                    continue
                                datos_para_guardar.append(
                                    {
                                        "id_cuenta": str(r.get("id_cuenta")),
                                        "fecha": r.get("fecha"),
                                        "seguidores": int(r.get("seguidores", 0)),
                                        "alcance": int(r.get("alcance", 0)) if not pd.isna(r.get("alcance")) else 0,
                                        "interacciones": int(r.get("interacciones", 0)),
                                        "likes_promedio": float(r.get("likes_promedio", 0)) if not pd.isna(r.get("likes_promedio")) else 0,
                                    }
                                )

                            if datos_para_guardar:
                                try:
                                    # Convertir lista a DataFrame
                                    df_to_save = pd.DataFrame(datos_para_guardar)
                                    save_batch(df_to_save)
                                    st.success(f"✅ {len(datos_para_guardar)} publicaciones guardadas correctamente.")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error guardando publicaciones: {e}")
                            else:
                                st.warning("No se encontraron publicaciones válidas para guardar.")

    # ==============================================================================
    # PESTAÑA 2: REPORTES (Versión Blindada contra KeyError)
    # ==============================================================================
    with tab_reportes:
        st.markdown("### 📄 Generador de Reportes PDF")
        st.info("Descarga informes ejecutivos con análisis automático.")

        # 1. Carga Segura de Datos
        cuentas, metricas = dm.load_data()

        # VALIDACIÓN CRÍTICA: Verificar que 'cuentas' tenga la información base
        if cuentas.empty or "entidad" not in cuentas.columns:
            st.error(
                "⚠️ Error Crítico: La tabla de 'Cuentas' está vacía o malformada. No se pueden asociar nombres."
            )
            if not cuentas.empty:
                st.write("Columnas detectadas en Cuentas:", cuentas.columns.tolist())
            st.stop()

        if metricas.empty:
            st.warning(
                "⚠️ No hay métricas registradas aún. Ve a la pestaña 'Gestión de Datos' para generar datos."
            )
        else:
            # 2. Cruce de Datos (Merge) INTELIGENTE
            # ---------------------------------------------------------
            # Paso A: Estandarizar tipos para evitar errores de merge
            if "id_cuenta" in metricas.columns:
                metricas["id_cuenta"] = metricas["id_cuenta"].astype(str).str.strip()
            if "id_cuenta" in cuentas.columns:
                cuentas["id_cuenta"] = cuentas["id_cuenta"].astype(str).str.strip()

            # Paso B: Evitar duplicidad de columnas (El arreglo del KeyError)
            # Si métricas ya tiene 'entidad', la borramos para usar la versión oficial de 'cuentas'
            if "entidad" in metricas.columns:
                metricas = metricas.drop(columns=["entidad"])

            # Paso C: Realizar la fusión
            # Usamos left join para mantener todas las métricas y pegarles el nombre de la entidad
            df_completo = pd.merge(
                metricas, cuentas[["id_cuenta", "entidad"]], on="id_cuenta", how="left"
            )

            # Paso D: Rellenar nulos si alguna métrica quedó huérfana
            if "entidad" in df_completo.columns:
                df_completo["entidad"] = df_completo["entidad"].fillna("Desconocido")
            else:
                # Si por algún milagro sigue fallando, forzamos la creación
                df_completo["entidad"] = "Desconocido"
            # ---------------------------------------------------------

            # 3. Interfaz de Configuración
            col_conf, col_prev = st.columns([1, 2])

            with col_conf:
                st.subheader("Configuración")

                # --- FILTRO INTELIGENTE DE NOMBRES ---
                raw_entidades = sorted(df_completo["entidad"].unique().tolist())

                # Filtrar nombres inválidos o vacíos
                lista_entidades = [
                    str(e)
                    for e in raw_entidades
                    if e and str(e).lower() != "nan" and str(e) != "Desconocido"
                ]

                if not lista_entidades:
                    st.warning("No se encontraron instituciones con datos.")
                    st.stop()

                entidad_selec = st.selectbox(
                    "Selecciona una institución:", lista_entidades
                )

                if not entidad_selec:
                    st.stop()

                st.markdown("**Secciones a incluir:**")
                inc_kpis = st.checkbox("Tabla de KPIs", value=True)
                inc_graf = st.checkbox("Gráficas de Tendencia", value=True)
                inc_analisis = st.checkbox("Análisis (Texto Automático)", value=True)

                # Botón Generar
                if st.button("Generar PDF", type="primary", width='stretch'):
                    with st.status("Generando PDF..."):
                        # Filtrar datos por la entidad seleccionada
                        df_filtrado = df_completo[
                            df_completo["entidad"] == entidad_selec
                        ].copy()

                        # Ordenar por fecha
                        if "fecha" in df_filtrado.columns:
                            df_filtrado["fecha"] = pd.to_datetime(df_filtrado["fecha"])
                            df_filtrado = df_filtrado.sort_values("fecha")

                        # Instanciar Builder con manejo de errores
                        try:
                            # Asegurar que pasamos un string limpio
                            nombre_limpio = str(entidad_selec).strip()
                            builder = ReportBuilder(
                                df=df_filtrado, entity_name=nombre_limpio
                            )

                            secciones = []
                            if inc_kpis:
                                secciones.append("kpis")
                            if inc_graf:
                                secciones.append("graficas")
                            if inc_analisis:
                                secciones.append("analisis")

                            pdf_bytes = builder.generate(secciones)

                            # Nombre de archivo seguro
                            file_name_safe = (
                                f"Reporte_{nombre_limpio.replace(' ', '_')}.pdf"
                            )

                            try:
                                st.toast("✅ PDF generado", icon="Ⓜ️")
                            except Exception:
                                st.success("✅ Reporte listo")

                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=pdf_bytes,
                                file_name=file_name_safe,
                                mime="application/pdf",
                            )
                        except Exception as e:
                            st.error(f"Error generando PDF: {e}")

            with col_prev:
                st.subheader("Vista Previa de Datos")
                df_vista = df_completo[df_completo["entidad"] == entidad_selec]

                cols_deseadas = ["fecha", "plataforma", "seguidores", "engagement_rate"]
                cols_existentes = [c for c in cols_deseadas if c in df_vista.columns]

                if cols_existentes:
                    st.dataframe(
                        df_vista[cols_existentes].head(10),
                        width='stretch',
                        hide_index=True,
                    )
                else:
                    st.warning("Faltan columnas clave para la vista previa.")

                st.caption(f"Registros encontrados: {len(df_vista)}")

    # ==============================================================================
    # PESTAÑA 3: CATÁLOGO DE INSTITUCIONES
    # ==============================================================================
    with tab_catalogo:
        st.markdown("### 📋 Directorio de Instituciones")

        buscar_cat = st.text_input(
            "🔎 Buscar institución", placeholder="Escribe el nombre del colegio..."
        )

        instituciones_filtradas = {
            k: v
            for k, v in COLEGIOS_MARISTAS.items()
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
            new_redes = st.text_area(
                "Redes (Formato: Facebook:usuario, Instagram:usuario)", height=70
            )

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
                            # Actualizar variable global en memoria para que se vea reflejado al instante
                            COLEGIOS_MARISTAS[new_name] = redes_dict
                            st.success(f"✅ {new_name} agregada correctamente.")
                            st.rerun()  # Recargar la página para ver cambios

                    except Exception as e:
                        st.error(f"Error de formato: {e}")
                else:
                    st.error("Por favor completa todos los campos.")

        with st.expander("🗑️ Eliminar Institución del Catálogo"):
            st.warning(
                "Esta acción eliminará permanentemente la institución seleccionada del catálogo."
            )
            instituciones_existentes = list(COLEGIOS_MARISTAS.keys())

            if not instituciones_existentes:
                st.info("No hay instituciones para eliminar.")
            else:
                institucion_a_eliminar = st.selectbox(
                    "Selecciona la institución a eliminar:", instituciones_existentes
                )

                if st.button("Eliminar Institución", type="primary"):
                    try:
                        # Eliminar de la variable global
                        if institucion_a_eliminar in COLEGIOS_MARISTAS:
                            del COLEGIOS_MARISTAS[institucion_a_eliminar]

                        # Eliminar del archivo CSV local
                        if CUENTAS_CSV.exists():
                            cuentas_df = pd.read_csv(CUENTAS_CSV)
                            cuentas_df = cuentas_df[
                                cuentas_df["entidad"] != institucion_a_eliminar
                            ]
                            cuentas_df.to_csv(
                                CUENTAS_CSV, index=False, encoding="utf-8-sig"
                            )

                        # Eliminar de Google Sheets
                        spreadsheet = dm.conectar_sheets()
                        if spreadsheet:
                            try:
                                sheet_cuentas = spreadsheet.worksheet("cuentas")
                                data = sheet_cuentas.get_all_records()
                                cuentas_df = pd.DataFrame(data)
                                cuentas_df = cuentas_df[
                                    cuentas_df["entidad"] != institucion_a_eliminar
                                ]
                                sheet_cuentas.clear()
                                sheet_cuentas.append_row(dm.COLS_CUENTAS)
                                sheet_cuentas.append_rows(cuentas_df.values.tolist())
                            except Exception as e:
                                st.warning(
                                    "No se pudo actualizar Google Sheets. Cambios aplicados solo localmente."
                                )
                                logging.error(
                                    f"Error eliminando institución de Sheets: {e}"
                                )

                        st.success(
                            f"✅ La institución '{institucion_a_eliminar}' ha sido eliminada correctamente."
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar la institución: {e}")
