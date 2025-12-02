# 🗺️ Roadmap de Desarrollo - CHAMPILYTICS

Mapa estratégico de evolución del proyecto siguiendo metodología ágil con sprints de 2 semanas.

---

## 🏁 Sprint 1: Cimientos y Seguridad
**Status**: ✅ **COMPLETADO** (100%)  
**Objetivo**: Limpiar la casa. Pasar de un script monolítico a una aplicación modular y segura.

### Semana 1: Modularización y Secretos
- [x] **Refactorización de Archivos**: Separación en `/utils`, `/views`, `/components`
- [x] **Gestión de Secretos**: Implementación de `secrets.toml` y eliminación de hardcoding
- [x] **Dependencias**: `requirements.txt` congelado y entornos virtuales configurados

### Semana 2: Robustez de Datos
- [x] **Conexión Resiliente**: Manejo de errores de `gspread` y reconexión automática
- [x] **Logging**: Sistema de `logger.py` implementado para auditoría
- [x] **Cache**: `@st.cache_data` implementado y optimizado en `data_manager.py`

---

## 🏗️ Sprint 2: Calidad de Datos y Normalización
**Status**: ✅ **COMPLETADO** (100%)  
**Objetivo**: Asegurar que los datos que entran estén limpios y estandarizados.

### Semana 3: Estandarización
- [x] **Normalización de IDs**: Lógica de `get_id` y limpieza de strings (`strip`/`lower`) implementada
- [x] **Validación de Tipos (Backend)**: `save_batch` fuerza tipos numéricos y datetime

### Semana 4: Captura Inteligente
- [x] **Formularios Dinámicos**: `data_entry.py` ajusta campos según la institución
- [x] **Detector de Duplicados**: Implementado `drop_duplicates` en la lógica de guardado
- [x] **Carga Masiva**: Componente para subir Excel/CSV con múltiples meses (implementado en sidebar)

---

## 🧠 Sprint 3: Motor de Análisis y Predicción
**Status**: ✅ **COMPLETADO** (100%)  
**Objetivo**: Hacer que los datos generen valor mediante cálculos matemáticos.

### Semana 5: Métricas Temporales
- [x] **Cálculo MoM**: Funciones para variaciones Month-over-Month implementadas en `analytics.py`
- [x] **Agregación Temporal**: Sistema de cálculo mensual con deltas (`calculate_growth_metrics`)

### Semana 6: Algoritmos Avanzados
- [x] **Score de Salud Digital**: Engagement ponderado implementado
- [x] **Benchmarking**: Sistema de comparación vs promedio de red con cuartiles
- [x] **Detección de Contexto**: Líneas de referencia y alertas visuales mediante deltas

---

## 📊 Sprint 4: Visualización y UX
**Status**: ✅ **COMPLETADO** (100%)  
**Objetivo**: Interfaces avanzadas con interactividad y personalización.

### Semana 7: Dashboards Interactivos
- [x] **Filtros Globales**: Selector de mes sincronizado con KPIs
- [x] **Toggle de Métricas**: Alternancia entre Seguidores/Interacciones en gráficas
- [x] **Rango Histórico**: Toggle entre vista mensual y histórica completa

### Semana 8: Visualización Avanzada
- [x] **Gráficas Multi-escala**: Separación de volumen y calidad (engagement)
- [x] **Agregación 2 Pasos**: Snapshot + sum para evitar duplicación
- [x] **Cuartiles Visuales**: Categorización automática (🟢 Top 25%, 🔵 Medio, 🟠 Bottom)
- [x] **Líneas de Benchmark**: Promedios de red como referencias en gráficas individuales

---

## 👤 Sprint 5: Personalización y Roles
**Status**: 🟡 **EN PROGRESO** (40%)  
**Objetivo**: Que la aplicación se adapte a quién la está viendo (Director vs. Analista).

### Semana 9: Identidad y Preferencias
- [x] **Selectores Persistentes**: `st.session_state` para recordar filtros y métricas
- [x] **Constructor de Vistas**: Permitir elegir qué 3 gráficas ver en pantalla de inicio
- [x] **Configuración de Usuario**: Panel para definir metas propias (KPIs personalizados) y guardado en hoja separada de configs

### Semana 10: Reportes a Medida
- [x] **Comentarios Contextuales**: Agregar notas de texto sobre mes específico (ej: "Campaña de inscripciones")
- [ ] **Exportación Personalizada**: Plantillas de reporte con secciones seleccionables

---

## 🎨 Sprint 6: UI/UX Moderna y Accesibilidad
**Status**: ⬜ **PENDIENTE** (0%)  
**Objetivo**: Interfaz de usuario profesional con accesibilidad y navegación fluida.

### Semana 11: Layout Moderno
- [ ] **Diseño Responsivo**: Optimización para tablets y monitores 4K
- [ ] **Temas Personalizables**: Modo oscuro/claro con toggle
- [ ] **Navegación por Teclado**: Shortcuts para acciones frecuentes (Ctrl+D para dashboard)

### Semana 12: Visualización Avanzada v2
- [ ] **Heatmaps Interactivos**: Engagement por día de semana y hora
- [ ] **Drill-down**: Click en institución para ver detalle sin cambiar de página
- [ ] **Animaciones Suaves**: Transiciones entre vistas con `st.spinner` customizado

---

## 📤 Sprint 7: Integración, Seguridad y Entrega Final
**Status**: ⬜ **PENDIENTE** (0%)  
**Objetivo**: Conexión con sistemas externos y automatización de procesos.

### Semana 13: APIs y Webhooks
- [ ] **API REST**: Endpoints para consultar datos desde otros sistemas
- [ ] **Webhooks Salientes**: Notificaciones automáticas a Slack/Teams cuando hay anomalías
- [ ] **Integración Google Sheets**: Sincronización bidireccional con hojas de cálculo

### Semana 14: Automatización Inteligente
- [ ] **Scheduler de Reportes**: Envío automático de resúmenes semanales por email
- [ ] **Forecasting con Prophet**: Predicciones 1-2 meses adelante con bandas de confianza
- [ ] **Alertas Proactivas**: Notificaciones push cuando engagement cae >15%

---

## 🚀 Sprint 8: Escalabilidad y Performance
**Status**: ⬜ **PLANIFICADO** (0%)  
**Objetivo**: Optimización para soportar crecimiento a 100+ instituciones.

### Semana 15: Optimización de Datos
- [ ] **Lazy Loading**: Cargar gráficas solo cuando el usuario abre la pestaña
- [ ] **Paginación**: Limitar ranking a Top 20 con opción de "Ver más"
- [ ] **Compresión de Datos**: Archivos Parquet en vez de CSV para queries rápidas

### Semana 16: Infraestructura
- [ ] **Multi-tenancy**: Separación lógica de datos por provincia/red
- [ ] **Rate Limiting**: Prevención de sobrecarga en picos de tráfico
- [ ] **Monitoreo**: Dashboard de observabilidad con tiempos de respuesta

---

## 🎓 Sprint 9: Capacitación y Documentación
**Status**: 🟡 **EN PROGRESO** (30%)  
**Objetivo**: Que cualquier nuevo usuario pueda usar el sistema sin ayuda.

### Semana 17: Documentación Técnica
- [x] **CHANGELOG.md**: Historial completo de versiones (implementado en v2.1.0)
- [ ] **README Completo**: Instalación, configuración y troubleshooting
- [ ] **API Docs**: Documentación automática con Swagger/OpenAPI

### Semana 18: Materiales de Usuario Final
- [ ] **Video Tutoriales**: Grabaciones de 2-3 minutos por funcionalidad
- [ ] **Tooltips Contextuales**: Ayuda inline con `st.info` en cada sección
- [ ] **FAQ Interactivo**: Buscador de preguntas frecuentes integrado

---

## 🔒 Sprint 10: Seguridad y Compliance
**Status**: ⬜ **PLANIFICADO** (0%)  
**Objetivo**: Cumplimiento de estándares de privacidad y protección de datos.

### Semana 19: Autenticación y Autorización
- [ ] **Login con SSO**: Integración con Google Workspace/Microsoft Entra
- [ ] **Roles y Permisos**: Administrador, Analista, Visualizador
- [ ] **Auditoría de Accesos**: Log de quién vio qué y cuándo

### Semana 20: Protección de Datos
- [ ] **Encriptación**: Datos sensibles encriptados en reposo (SQLite con SQLCipher)
- [ ] **Anonimización**: Opción de ocultar nombres de instituciones en demos
- [ ] **GDPR Compliance**: Exportación y eliminación de datos personales

---

## 📊 Métricas de Progreso Global

| Sprint | Nombre | Status | Progreso | Fecha Est. Completado |
|--------|--------|--------|----------|----------------------|
| 1 | Cimientos y Seguridad | ✅ Completado | 100% | Nov 2025 |
| 2 | Calidad de Datos | ✅ Completado | 100% | Nov 2025 |
| 3 | Motor de Análisis | ✅ Completado | 100% | Dic 2025 |
| 4 | Visualización y UX | ✅ Completado | 100% | Dic 2025 |
| 5 | Personalización | 🟡 En Progreso | 40% | Dic 2025 |
| 6 | UI/UX Moderna | ⬜ Pendiente | 0% | Ene 2026 |
| 7 | Integración | ⬜ Pendiente | 0% | Feb 2026 |
| 8 | Escalabilidad | ⬜ Planificado | 0% | Mar 2026 |
| 9 | Documentación | 🟡 En Progreso | 30% | Abr 2026 |
| 10 | Seguridad | ⬜ Planificado | 0% | May 2026 |

---

## 🎯 Prioridades Actuales (Diciembre 2025)

### 🔥 Crítico
1. **Sincronización Bidireccional**
2. **Promedios Móviles**
3. **Score de Salud Digital**

### 🚀 Importante
4. **Detección de Anomalías + Alertas**
5. **Forecasting con Prophet**
6. **Selectores Persistentes**

### 💡 Deseado
7. **Vista "Mi Colegio"**
8. **Configuración de KPIs**
9. **Scheduler de Reportes**

---

## 📝 Notas de Implementación

### Decisiones Arquitectónicas
- **SQLite como BD primaria**: Suficiente para <100 instituciones, migrará a PostgreSQL en Sprint 8
- **Plotly como motor gráfico**: Interactividad nativa sin JS custom
- **Streamlit como framework**: Prototipado rápido, se evaluará Next.js en v3.0.0

### Deuda Técnica Conocida
- Falta cobertura de tests unitarios (target: 80% para Sprint 8)
- Hardcoding de `COLEGIOS_MARISTAS` en `utils/__init__.py` (migrar a DB en Sprint 5)
- Uso de `st.experimental_rerun()` deprecado (actualizar a `st.rerun()` completado)

---

## 🤝 Contribuciones

Para agregar nuevas funcionalidades:
1. Abre un issue vinculado al sprint correspondiente
2. Actualiza este roadmap marcando `[ ]` → `[x]` al completar
3. Documenta el cambio en `CHANGELOG.md` con número de versión

---

**Última actualización**: 2025-12-01  
**Versión actual**: v2.1.0  
**Sprint activo**: Sprint 5 - Personalización y Roles

### Actualización 2025-12-02
- Se corrigieron problemas de visibilidad en el menú desplegable de la vista institucional.
- Se agregó la funcionalidad para guardar nuevas instituciones y redes sociales directamente en Google Sheets.
- Se mejoró la sincronización de datos para reflejar cambios en tiempo real en las gráficas.
