# 📝 Historial de Cambios - CHAMPILEAKS

Todas las modificaciones notables del proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [2.1.0] - 2025-12-01

### ✨ Agregado
- **Benchmarking Automático**: 
  - KPIs individuales ahora muestran delta vs promedio de red (`+X% vs red`)
  - Líneas de referencia punteadas en gráficas individuales mostrando promedio de red por plataforma
  - Indicadores de cuartil en ranking institucional (🟢 Top 25%, 🔵 Medio 50%, 🟠 Bottom 25%)
- **Comparación de Rendimiento**: Categorización automática de instituciones según métricas

### 🔧 Mejorado
- Cálculo de promedios de red ponderados por entidad
- Tooltips enriquecidos con información de benchmarking
- Visualización de posición relativa en tiempo real

---

## [2.0.0] - 2025-12-01

### 🚀 Refactorización Mayor
- **Agregación de Datos Corregida**:
  - Implementación de agregación en 2 pasos (snapshot + sum) para evitar duplicación
  - Seguidores: `max` por entidad/fecha → `sum` por plataforma
  - Interacciones: `sum` directo con deduplicación
- **Sincronización de KPIs**: 
  - KPIs ahora reaccionan al mes seleccionado en el filtro
  - Deltas MoM calculados desde `df_growth` con fallback
- **Separación de Escalas en Analytics**:
  - Volumen (Seguidores/Interacciones) y Calidad (Engagement) en tabs separados
  - Ejes Y con sufijo `%` para engagement

### 🐛 Corregido
- Orden visual en ranking de barras horizontales (categoryarray dinámico)
- Filtrado de registros NaN antes de agregaciones (eliminadas barras fantasma)
- Formato de porcentajes en ejes y tooltips (engagement 0-100 sin doble %)
- Eliminado `width='stretch'` deprecado en dataframes

### 🔧 Mejorado
- Parsing datetime global al inicio del render
- Selector de mes por defecto sincronizado con último mes en `df_growth`
- Gráfica de tendencia con toggle "Histórico Completo" vs "Mes seleccionado"
- Pie chart con toggle de métrica (Seguidores/Interacciones)

---

## [1.5.0] - 2025-11-30

### ✨ Agregado
- **Inteligencia de Negocio**:
  - Integración de `calculate_growth_metrics` en dashboard principal
  - KPIs con deltas MoM (Month-over-Month)
  - Tab "📈 Tendencias de Crecimiento" con evolución mensual
- **Análisis Individual Mejorado**:
  - Ordenamiento cronológico estricto (`sort_values` por fecha/plataforma)
  - Conversión datetime explícita para evitar orden alfabético

### 🔧 Mejorado
- Gráficas de línea con `markers=True` para distinguir datos reales
- Hover unificado (`hovermode='x unified'`) en todas las gráficas de tendencia
- Tooltips formateados con separadores de miles (`:,.0f`)

---

## [1.4.0] - 2025-11-29

### ✨ Agregado
- **Comparativa Institucional**:
  - Barras agrupadas (`barmode="group"`) para mejor legibilidad
  - Altura dinámica según cantidad de instituciones (300 + 30px por colegio)
  - Ranking automático por total de seguidores
- **Persistencia de Estado**:
  - `st.session_state` para selector de métrica en tendencias
  - Radio buttons para alternar entre Seguidores/Interacciones

### 🔧 Mejorado
- Leyenda horizontal inferior en todas las gráficas comparativas
- Color mapping consistente (`COLOR_MAP`) en toda la aplicación
- Formato de engagement en eje X cuando es métrica de ordenamiento

---

## [1.3.0] - 2025-11-28

### ✨ Agregado
- **Módulo de Analytics** (`utils/analytics.py`):
  - Función `calculate_growth_metrics` para cálculo de deltas MoM
  - Engagement ponderado por alcance
  - Agregación mensual automática
- **Vista de Análisis de Tendencias** (`views/analytics.py`):
  - Resumen mensual global con métricas consolidadas
  - Análisis individual por institución
  - Gráficas de evolución de seguidores y engagement rate

### 🔧 Mejorado
- Cálculo de engagement rate estandarizado: `(interacciones / seguidores) * 100`
- Validación de datos antes de cálculos (división por cero, NaN)

---

## [1.2.0] - 2025-11-27

### ✨ Agregado
- **Filtros Interactivos**:
  - Selector de mes en dashboard principal
  - Selector de métrica de ordenamiento (seguidores/engagement)
- **Exportación de Reportes**:
  - Función `generar_reporte_html` con estilos CSS embebidos
  - Botón de descarga por mes seleccionado

### 🔧 Mejorado
- Merge validado entre métricas y cuentas (detección de datos corruptos)
- Botones de reseteo y regeneración de datos
- Mensajes de error descriptivos con soluciones sugeridas

---

## [1.1.0] - 2025-11-26

### ✨ Agregado
- **Visualizaciones del Dashboard**:
  - Gráfica de distribución por plataforma (pie chart con donut)
  - Gráfica de tendencia de crecimiento (line chart)
  - Comparativa por institución (bar chart horizontal)
- **KPIs Dinámicos**:
  - Seguidores Totales
  - Interacciones del Mes
  - Engagement Promedio
  - Colegios Reportando

### 🔧 Mejorado
- Paleta de colores consistente por plataforma
- Tema Plotly unificado (`plotly_white`)
- Márgenes y espaciado optimizados

---

## [1.0.0] - 2025-11-25

### 🎉 Lanzamiento Inicial
- **Arquitectura Base**:
  - Sistema modular con vistas separadas (Dashboard, Analytics, Config)
  - Gestión de datos con SQLite (`champilytics.db`)
  - Carga y validación de datos desde CSV
- **Simulador de Datos**:
  - Generación de métricas sintéticas para testing
  - Soporte para múltiples instituciones maristas
  - Configuración de cuentas por plataforma (Facebook, Instagram, X, TikTok, YouTube)
- **Componentes UI**:
  - Navegación por sidebar
  - Sistema de tabs para organización de contenido
  - Cards con estilos CSS personalizados
- **Funcionalidades Core**:
  - Carga de cuentas desde `cuentas.csv`
  - Carga de métricas desde `metricas.csv`
  - Cálculo de engagement rate básico
  - Reset de base de datos

---

## Tipos de Cambios
- `✨ Agregado` - Nuevas funcionalidades
- `🔧 Mejorado` - Cambios en funcionalidades existentes
- `🐛 Corregido` - Correcciones de bugs
- `🚀 Refactorización` - Cambios internos sin afectar funcionalidad
- `🗑️ Eliminado` - Funcionalidades removidas
- `🔒 Seguridad` - Vulnerabilidades corregidas

---

## Roadmap (Próximas Versiones)

### [2.2.0] - Planificado
- Sparklines en KPIs (mini-gráficas de tendencia)
- Anotaciones automáticas de cambios >20% MoM
- Export de gráficas a PNG/PDF

### [2.3.0] - Planificado
- Comparador de instituciones (selección múltiple)
- Selector de rango de fechas (vs mes único)
- Heatmap de engagement por día de semana

### [3.0.0] - En Evaluación
- Forecast con Prophet (predicciones 1-2 meses)
- Detección de anomalías con alertas
- API REST para integración externa
