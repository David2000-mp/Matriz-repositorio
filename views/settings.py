"""
Vista de Configuración para CHAMPILYTICS.
Administración del sistema, simulación de datos y herramientas avanzadas.

PENDIENTE: Migrar código completo desde app.py línea 1549-1631
"""

import streamlit as st
import logging
from utils import simular, save_batch, reset_db, COLEGIOS_MARISTAS
from utils.data_manager import load_configs, save_config

def render():
    """
    Renderiza la página de configuración y administración.
    
    TODO: Implementar:
    - Tabs para diferentes secciones
    - Generador de datos sintéticos (simulación)
    - Reset de base de datos
    - Visualización de catálogo de instituciones
    - Configuración de caché
    - Diagnósticos del sistema
    """
    st.title("⚙️ CONFIGURACIÓN Y ADMINISTRACIÓN")
    st.caption("🛠️ Herramientas de Gestión y Personalización del Sistema")
    st.markdown("---")
    
    # Implementación temporal básica
    tab1, tab2, tab3, tab4 = st.tabs(["🎲 Simulador", "🗑️ Base de Datos", "📋 Catálogo", "🎯 Mis Metas"])
    
    with tab1:
        st.markdown("### 🎲 Generador de Datos de Prueba")
        st.info("📊 Crea datos sintéticos para todas las instituciones del catálogo")
        
        col_info1, col_info2 = st.columns(2)
        col_info1.metric("Instituciones", len(COLEGIOS_MARISTAS))
        total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
        col_info2.metric("Cuentas totales", total_cuentas)
        
        st.divider()
        
        meses = st.slider(
            "📅 Meses de histórico", 
            1, 12, 6,
            help="Selecciona cuántos meses de datos quieres generar"
        )
        
        registros_estimados = total_cuentas * meses
        st.caption(f"📊 Se generarán aproximadamente **{registros_estimados:,}** registros")
        
        if st.button("🚀 Generar Datos", use_container_width=True, type="primary"):
            with st.spinner(f"⏳ Generando {meses} meses de datos para {total_cuentas} cuentas..."):
                n_registros = total_cuentas * meses
                datos, metas = simular(n=n_registros, colegios_maristas=COLEGIOS_MARISTAS, generar_metas=True)
                save_batch(datos)
                
                # Guardar metas generadas
                for meta in metas:
                    save_config(
                        entidad=meta["entidad"],
                        meta_seguidores=meta["meta_seguidores"],
                        meta_engagement=meta["meta_engagement"]
                    )
            
            st.success(f"🎉 ¡{len(datos):,} registros y {len(metas)} metas generadas exitosamente!")
            st.info(f"📊 **Metas creadas:** Cada institución ahora tiene objetivos de seguidores y engagement")
            st.balloons()
            st.rerun()
    
    with tab2:
        st.markdown("### 🗑️ Gestión de Base de Datos")
        st.warning("⚠️ **ADVERTENCIA:** Esta acción eliminará TODOS los datos y metas permanentemente")
        
        st.markdown("🛡️ **Qué se eliminará:**")
        st.markdown("""
        - ❌ Todas las métricas (seguidores, interacciones, engagement)
        - ❌ Todas las cuentas registradas
        - ❌ Todas las configuraciones de metas personalizadas
        - ❌ Archivos CSV locales de respaldo
        """)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗑️ Solo Resetear")
            st.caption("Elimina todo sin generar datos nuevos")
            if st.button("🗑️ Resetear Base de Datos", use_container_width=True, help="Elimina todos los datos permanentemente"):
                with st.spinner("🗑️ Eliminando datos..."):
                    reset_db()
                st.success("✅ Base de datos reseteada correctamente")
                st.info("💡 Ahora puedes generar datos nuevos desde el tab 'Simulador'")
                st.rerun()
        
        with col2:
            st.markdown("#### 🔄 Resetear y Regenerar")
            st.caption("Elimina todo y crea datos demo")
            if st.button("🚀 Resetear + Generar Demo", use_container_width=True, type="primary", help="Reinicia el sistema con 6 meses de datos de ejemplo"):
                with st.spinner("⏳ Reseteando y generando datos..."):
                    reset_db()
                    total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
                    datos, metas = simular(n=total_cuentas * 6, colegios_maristas=COLEGIOS_MARISTAS, generar_metas=True)
                    save_batch(datos)
                    
                    # Guardar metas generadas
                    for meta in metas:
                        save_config(
                            entidad=meta["entidad"],
                            meta_seguidores=meta["meta_seguidores"],
                            meta_engagement=meta["meta_engagement"]
                        )
                st.success(f"🎉 ¡Sistema reiniciado con {len(datos):,} registros y {len(metas)} metas!")
                st.info("📊 Datos demo incluyen objetivos personalizados para cada institución")
                st.balloons()
                st.rerun()
    
    with tab3:
        st.markdown("### 📋 Catálogo de Instituciones Maristas")
        
        col_cat1, col_cat2, col_cat3 = st.columns(3)
        col_cat1.metric("🏛️ Instituciones", len(COLEGIOS_MARISTAS))
        total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
        col_cat2.metric("📱 Cuentas totales", total_cuentas)
        plataformas = set()
        for redes in COLEGIOS_MARISTAS.values():
            plataformas.update(redes.keys())
        col_cat3.metric("🌍 Plataformas", len(plataformas))
        
        st.divider()
        
        # Buscador
        buscar_cat = st.text_input("🔎 Buscar institución", placeholder="Escribe para filtrar...")
        
        # Mostrar catálogo
        instituciones_filtradas = {
            k: v for k, v in COLEGIOS_MARISTAS.items() 
            if not buscar_cat or buscar_cat.lower() in k.lower()
        }
        
        if not instituciones_filtradas:
            st.warning("⚠️ No se encontraron resultados")
        else:
            st.caption(f"Mostrando {len(instituciones_filtradas)} de {len(COLEGIOS_MARISTAS)} instituciones")
            
            for entidad, redes in instituciones_filtradas.items():
                with st.expander(f"🏛️ {entidad} ({len(redes)} cuentas)"):
                    for plat, usuario in redes.items():
                        col_plat, col_user = st.columns([1, 2])
                        col_plat.markdown(f"**{plat}**")
                        col_user.code(usuario)
        
        st.divider()
        st.caption("📝 **Nota:** Para editar este catálogo, modifica el archivo `utils/data_manager.py`")
    
    with tab4:
        st.markdown("### Configuración de Metas Personalizadas")
        st.caption("Define objetivos específicos para tu institución")
        
        # Verificar institución activa
        institucion_activa = st.session_state.get("institucion_activa", "Todas las Instituciones")
        
        if not institucion_activa or institucion_activa == "Todas las Instituciones":
            st.warning("⚠️ **Acción requerida:** Selecciona una institución específica")
            st.info("💡 **Cómo hacerlo:** Usa el selector **'🏛️ Mi Institución'** en el sidebar izquierdo para elegir tu colegio")
            
            st.markdown("---")
            st.markdown("### 👀 Vista previa de funcionalidad")
            st.markdown("""
            Una vez que selecciones una institución, podrás:
            - 🎯 Definir meta de seguidores totales
            - 📊 Establecer objetivo de engagement rate
            - 💾 Guardar configuración personalizada
            - 📊 Ver progreso en el Dashboard
            """)
        else:
            st.success(f"📍 Configurando metas para: **{institucion_activa}**")
            
            # Cargar configuraciones existentes
            with st.spinner("Cargando configuración..."):
                df_configs = load_configs()
            
            # Buscar configuración actual de la institución
            meta_seguidores_actual = 0
            meta_engagement_actual = 0.0
            
            if not df_configs.empty and institucion_activa in df_configs['entidad'].values:
                config_actual = df_configs[df_configs['entidad'] == institucion_activa].iloc[0]
                meta_seguidores_actual = int(config_actual.get('meta_seguidores', 0))
                meta_engagement_actual = float(config_actual.get('meta_engagement', 0.0))
                st.info(f"ℹ️ Esta institución ya tiene metas configuradas. Puedes actualizarlas abajo.")
            
            st.divider()
            
            # Formulario de configuración
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👥 Meta de Seguidores")
                meta_seguidores = st.number_input(
                    "Objetivo total de seguidores (todas las plataformas)",
                    min_value=0,
                    max_value=1000000,
                    value=meta_seguidores_actual,
                    step=100,
                    help="Define el número objetivo de seguidores que quieres alcanzar"
                )
                
            with col2:
                st.markdown("#### 📊 Meta de Engagement")
                meta_engagement = st.number_input(
                    "Objetivo de engagement rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=meta_engagement_actual,
                    step=0.1,
                    format="%.2f",
                    help="Define el porcentaje de engagement que quieres alcanzar"
                )
            
            st.divider()
            
            # Vista previa
            st.markdown("#### 📋 Resumen de Configuración")
            col_preview1, col_preview2 = st.columns(2)
            
            col_preview1.metric("Meta Seguidores", f"{meta_seguidores:,}")
            col_preview2.metric("Meta Engagement", f"{meta_engagement:.2f}%")
            
            # Botón de guardado
            if st.button("💾 Guardar Metas", type="primary", use_container_width=True, help="Guarda la configuración en Google Sheets"):
                with st.spinner("⏳ Guardando configuración en la nube..."):
                    exito = save_config(institucion_activa, meta_seguidores, meta_engagement)
                
                if exito:
                    st.success("🎉 ¡Metas guardadas exitosamente!")
                    st.info("📊 **Próximo paso:** Ve al Dashboard para ver tu progreso hacia las metas")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error al guardar las metas")
                    st.warning("🛠️ **Solución:** Verifica tu conexión a internet e inténtalo nuevamente")
                    st.info("📞 **Ayuda:** Contacta al administrador si el problema persiste")
            
            # Mostrar todas las configuraciones existentes
            if not df_configs.empty:
                st.divider()
                st.markdown("#### 📊 Todas las Configuraciones")
                st.dataframe(
                    df_configs,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "entidad": "Institución",
                        "meta_seguidores": st.column_config.NumberColumn("Meta Seguidores", format="%d"),
                        "meta_engagement": st.column_config.NumberColumn("Meta Engagement", format="%.2f%%")
                    }
                )
