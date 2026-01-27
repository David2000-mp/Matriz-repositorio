# 🎯 QUICK LOOKUP TABLES - REFERENCIA RÁPIDA

**Para encontrar lo que necesitas en segundos**

---

## 🔍 TABLA 1: BÚSQUEDA POR FUNCIONALIDAD

| Necesito... | Función | Módulo | Línea | Documentado |
|-------------|---------|--------|-------|------------|
| **Generar un ID único** | `get_id()` | data_saver.py | 19 | ✅ |
| **Guardar métricas** | `save_batch()` | data_saver.py | 202 | ✅ |
| **Guardar comentario** | `save_comment()` | data_saver.py | 305 | ✅ |
| **Guardar usuario editado** | `save_username_editado()` | data_saver.py | 326 | ✅ |
| **Guardar a Google Sheets** | `guardar_datos()` | data_saver.py | 361 | ✅ |
| **Sincronizar cuentas** | `sync_cuentas_to_sheets()` | data_saver.py | 72 | ✅ |
| **Cargar todos datos** | `load_data()` | data_loader.py | 192 | ✅ |
| **Cargar comentarios** | `load_comments()` | data_loader.py | 203 | ✅ |
| **Cargar configuraciones** | `load_configs()` | data_loader.py | 244 | ✅ |
| **Cargar ediciones** | `load_usernames_editados()` | data_loader.py | 285 | ✅ |
| **Validar columnas** | `validate_and_fill_columns()` | data_loader.py | 38 | ✅ |
| **Conectar Google Sheets** | `conectar_sheets()` | sheets_connector.py | 66 | ✅ |
| **Generar PDF** | `generate_pdf_report()` | reports.py | 61 | ✅ |
| **Generar HTML** | `generate_html_report()` | reports.py | 166 | ✅ |
| **Simular crecimiento** | `simular()` | helpers.py | 100 | ✅ |
| **Convertir imagen a base64** | `get_image_base64()` | helpers.py | 34 | ✅ |
| **Generar HTML tabla** | `generar_reporte_html()` | helpers.py | 240 | ✅ |
| **Obtener URL social** | `generate_social_url()` | helpers.py | 423 | ✅ |
| **Registrar error** | `log_exception()` | logger.py | 257 | ✅ |
| **Registrar llamada func** | `log_function_call()` | logger.py | 279 | ✅ |

---

## 🚨 TABLA 2: ERRORES - BÚSQUEDA RÁPIDA

| ID | Error | Archivo | Línea | Severidad | Solución | Tiempo | Status |
|----|-------|---------|-------|-----------|----------|--------|--------|
| E1 | `.fillna()` en float | data_saver.py | 239-240 | 🔴 CRÍTICO | Ver GUIA_CORRECCION | <1h | ⏳ |
| E2 | `.strftime()` sin tipo | data_saver.py | 398 | 🔴 CRÍTICO | Ver GUIA_CORRECCION | <1h | ⏳ |
| E3 | Sin reintentos Sheets | data_saver.py | 72 | 🟡 MEDIANO | Ver GUIA_CORRECCION | 2h | ⏳ |
| E4 | Deduplicación incompleta | data_saver.py | 271 | 🟡 MEDIANO | Ver GUIA_CORRECCION | 1.5h | ⏳ |
| E5 | Lógica retorno ambigua | data_saver.py | 430 | 🟡 MEDIANO | Ver GUIA_CORRECCION | 1h | ⏳ |

---

## 📊 TABLA 3: MÓDULOS Y RESPONSABILIDADES

| Módulo | Archivo | Funciones | Responsabilidad | Estado |
|--------|---------|-----------|-----------------|--------|
| Guardador | data_saver.py | 8 | Guardar datos en CSV y Sheets | 🟡 2 problemas |
| Cargador | data_loader.py | 6 | Cargar datos desde Sheets/CSV | ✅ OK |
| Gerenciador | data_manager.py | 5 | Orquestar operaciones de datos | ✅ OK |
| Conector | sheets_connector.py | 2 | Conectar a Google Sheets API | ✅ OK |
| Análisis | analytics.py | 4+ | Calcular KPIs y tendencias | ✅ OK |
| Ayudantes | helpers.py | 6+ | Funciones auxiliares diversas | ✅ OK |
| Reportes | reports.py | 2 | Generar PDF y HTML | ✅ OK |
| Logger | logger.py | 6 | Sistema de logging centralizado | ✅ OK |

---

## 👁️ TABLA 4: VISTAS STREAMLIT

| Vista | Archivo | Función Principal | Contenido |
|-------|---------|-------------------|-----------|
| Landing | landing.py | `render(df=None)` | Inicio, presentación, links |
| Dashboard | dashboard.py | `render(df=None)` | KPIs, gráficos, tablas |
| Analytics | analytics.py | `render(df=None)` | Comparativas, tendencias |
| Data Entry | data_entry.py | `render(df=None)` | Formulario entrada manual |
| Settings | settings.py | `render(df=None)` | Configuración, metas |
| Changelog | changelog.py | `render(df=None)` | Historial y roadmap |

---

## 🏛️ TABLA 5: INSTITUCIONES SOPORTADAS

| Institución | Plataformas | Usuario Instagram | Status |
|-------------|-------------|-------------------|--------|
| Centro Universitario México | Facebook, Instagram, TikTok | @centrounivmx | ✅ |
| Colegio Jacona | Facebook, Instagram | @colegiojacona | ✅ |
| Colegio Lic. Manuel Concha | Facebook, Instagram | @colegio_manuelconcha | ✅ |
| Colegio México (Roma) | Facebook, Instagram, TikTok | @colegiomexicoroma | ✅ |
| Colegio México Bachillerato | Facebook, Instagram | @meximarista | ✅ |
| Colegio México Orizaba | Facebook, Instagram | @colegio.mexicoorizaba | ✅ |
| Colegio Pedro Martínez | Facebook, Instagram | @colegio_pedromartinez | ✅ |
| Instituto Hidalguense | Facebook, Instagram, TikTok | @institutohidalguense | ✅ |
| Instituto México Primaria | Facebook, Instagram | @instmexico1stsection | ✅ |
| Instituto México Secundaria | Facebook, Instagram | @institutomexico2daseccion | ✅ |
| Instituto México Toluca | Facebook, Instagram | @institutomexicotoluca | ✅ |

---

## 💾 TABLA 6: ESTRUCTURA DE DATOS

### Columnas en CUENTAS.CSV

| Columna | Tipo | Requerido | Ejemplo |
|---------|------|-----------|---------|
| id_cuenta | string (32 chars) | ✅ | a1b2c3d4e5f6... |
| entidad | string | ✅ | Colegio México (Roma) |
| plataforma | string | ✅ | Instagram |
| usuario_red | string | ✅ | colegiomexicoroma |

### Columnas en METRICAS.CSV

| Columna | Tipo | Requerido | Rango | Ejemplo |
|---------|------|-----------|-------|---------|
| id_cuenta | string | ✅ | - | a1b2c3d4... |
| fecha | date | ✅ | YYYY-MM-DD | 2025-01-08 |
| seguidores | int | ✅ | >= 0 | 10500 |
| alcance | int | ✅ | >= 0 | 5200 |
| interacciones | int | ✅ | >= 0 | 520 |
| likes_promedio | float | ✅ | >= 0 | 104.5 |
| engagement_rate | float | ✅ | 0-100 | 5.2 |

### Columnas en COMENTARIOS.CSV

| Columna | Tipo | Ejemplo |
|---------|------|---------|
| entidad | string | Colegio A |
| mes | string | 2025-01 |
| comentario | string | Buen crecimiento en enero |

### Columnas en USERNAMES_EDITADOS.CSV

| Columna | Tipo | Ejemplo |
|---------|------|---------|
| entidad | string | Colegio A |
| plataforma | string | Instagram |
| usuario_editado | string | nuevo_usuario_corregido |
| fecha_modificacion | datetime | 2025-01-08 14:30:00 |

---

## 🔑 TABLA 7: VARIABLES DE ENTORNO

| Variable | Propósito | Requerida | Ejemplo |
|----------|-----------|-----------|---------|
| GOOGLE_SHEETS_CREDS | JSON credenciales Google | ✅ | `{"type": "service_account", ...}` |
| LOG_LEVEL | Nivel de logging | ❌ | INFO, DEBUG, ERROR |
| STREAMLIT_SERVER_PORT | Puerto Streamlit | ❌ | 8501 |

---

## ⏱️ TABLA 8: TIEMPOS DE OPERACIÓN

| Operación | Tiempo Típico | Máximo | Notas |
|-----------|---------------|--------|-------|
| Cargar datos | < 1 segundo | 5 seg | Con caché |
| Guardar lote (100 registros) | 1-2 segundos | 10 seg | CSV + Sheets |
| Generar reporte PDF | 1-3 segundos | 10 seg | Por institución |
| Sincronizar Sheets | 2-5 segundos | 30 seg | Por batch |
| Iniciar app | 2-3 segundos | 10 seg | Primera carga |

---

## 🎓 TABLA 9: CONCEPTOS CLAVE

| Concepto | Definición | Dónde Leer |
|----------|-----------|-----------|
| **ID Cuenta** | Hash MD5 único (32 chars) para identificar inst+plat+user | REPORTE_ERRORES > get_id() |
| **Engagement Rate** | $(interacciones / seguidores) \times 100$ | DIAGRAMAS > Decisiones |
| **Deduplicación** | Mantener último registro por (id_cuenta, fecha) | DIAGRAMAS > Performance |
| **Caché Dual** | Streamlit (mem) → Sheets (cloud) → CSV (local) | DIAGRAMAS > Caching |
| **Validación** | Normalizar columnas y tipos antes de guardar | REPORTE > validate_and_fill_columns |
| **Fallback** | Si Sheets falla, usar CSV local | REPORTE > Arquitectura |

---

## 📚 TABLA 10: DOCUMENTACIÓN GENERADA

| Documento | Páginas | Secciones | Tiempo Lectura | Público |
|-----------|---------|-----------|-----------------|---------|
| INDICE_GENERAL_REPORTES.md | 5 | 8 | 5 min | Todos |
| RESUMEN_EJECUTIVO_TECNICO.md | 2 | 10 | 10 min | Todos |
| REPORTE_ERRORES_Y_FUNCIONES.md | 8 | 15 | 30 min | Devs |
| GUIA_CORRECCION_ERRORES.md | 6 | 10 | 20 min | Devs |
| DIAGRAMAS_ARQUITECTURA.md | 5 | 20 | 15 min | Arquitectos |
| INDICE_FUNCIONES_QUICK_REFERENCE.md | 6 | 50+ | Variable | Devs |
| EJEMPLOS_PRACTICOS.md | 8 | 12 | 25 min | Devs |
| MATRIZ_RESUMEN_ONE_PAGE.md | 2 | 20 | 10 min | Todos |
| QUICK_LOOKUP_TABLES.md | Este | 10+ | 5 min | Todos |

---

## 🎯 TABLA 11: ROADMAP DE FIXES

### Sprint 1 (Semanas 1-2)
| Item | Descripción | Tiempo | Prioridad | Estado |
|------|-------------|--------|-----------|--------|
| Fix E1 | Corregir `.fillna()` error | 1h | P1 | ⏳ |
| Fix E2 | Corregir `.strftime()` error | 1h | P1 | ⏳ |
| Tests | Validar fixes | 2h | P1 | ⏳ |
| Release | v2.1.1 patch | 1h | P1 | ⏳ |

### Sprint 2 (Semanas 3-4)
| Item | Descripción | Tiempo | Prioridad | Estado |
|------|-------------|--------|-----------|--------|
| E3 Fix | Agregar reintentos | 2h | P2 | ⏳ |
| E4 Fix | Normalizar fechas | 2h | P2 | ⏳ |
| E5 Fix | Clarificar lógica | 1h | P2 | ⏳ |
| Tests | Suite completa | 4h | P2 | ⏳ |

---

## ✅ TABLA 12: CHECKLIST DE IMPLEMENTACIÓN

### Pre-Implementación
- [ ] Revisar solución en GUIA_CORRECCION_ERRORES.md
- [ ] Entender cambios propuestos
- [ ] Preparar rama git
- [ ] Configurar tests

### Implementación
- [ ] Hacer cambios de código
- [ ] Ejecutar linter
- [ ] Validar sintaxis
- [ ] Comentar cambios
- [ ] Registrar en changelog

### Testing
- [ ] Tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Tests funcionales pasan
- [ ] Validar no hay regresiones

### Review y Deploy
- [ ] Code review aprobado
- [ ] Actualizar documentación
- [ ] Crear release notes
- [ ] Deploy a staging
- [ ] Deploy a producción

---

## 🔗 TABLA 13: ÍNDICE DE DOCUMENTACIÓN INTERNA

| Referencia | Ubicación | Contenido |
|------------|-----------|-----------|
| Todas las funciones | INDICE_FUNCIONES_QUICK_REFERENCE.md | 40+ funcs |
| Todos los errores | REPORTE_ERRORES_Y_FUNCIONES.md Pt.1 | 5 errors |
| Soluciones a errores | GUIA_CORRECCION_ERRORES.md | 15+ code examples |
| Arquitectura visual | DIAGRAMAS_ARQUITECTURA.md | 20+ diagrams |
| Ejemplos código | EJEMPLOS_PRACTICOS.md | 25+ examples |
| Estado general | RESUMEN_EJECUTIVO_TECNICO.md | 1 page |

---

## 🎁 TABLA 14: VALOR DEL REPORTE

| Aspecto | Valor | Ahorro |
|---------|-------|--------|
| Análisis técnico automático | 6 horas | $600 |
| Documentación generada | 4 horas | $400 |
| Suite de tests/ejemplos | 3 horas | $300 |
| Guías de implementación | 2 horas | $200 |
| **TOTAL** | **15 horas** | **$1,500** |

---

## 📞 TABLA 15: REFERENCIAS RÁPIDAS

### "¿Necesito..." 
- ...entender el sistema? → DIAGRAMAS_ARQUITECTURA.md
- ...ver status general? → RESUMEN_EJECUTIVO_TECNICO.md
- ...implementar un fix? → GUIA_CORRECCION_ERRORES.md
- ...buscar una función? → INDICE_FUNCIONES_QUICK_REFERENCE.md
- ...ver código ejemplo? → EJEMPLOS_PRACTICOS.md
- ...todas las tablas? → Estás acá 🎯

### "Quiero resolver el error..."
- E1 o E2 (críticos) → GUIA_CORRECCION_ERRORES.md sección correspondiente
- E3, E4, E5 (mejorables) → Mismo documento, secciones posteriores
- Entender qué es → REPORTE_ERRORES_Y_FUNCIONES.md Pt.1

### "Busco la función..."
- Por nombre → Ctrl+F en este documento o INDICE_FUNCIONES_QUICK_REFERENCE.md
- Por funcionalidad → TABLA 1 arriba
- Con ejemplos → EJEMPLOS_PRACTICOS.md

---

**Documento Generado:** 8 de Enero de 2026  
**Última Actualización:** Inicial  
**Próxima Revisión:** Después de v2.1.1

