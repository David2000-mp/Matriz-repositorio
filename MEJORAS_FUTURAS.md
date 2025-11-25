# 📋 Mejoras Futuras para Producción

Este documento lista las optimizaciones recomendadas para escalar la aplicación CHAMPILYTICS.

## 🚀 Implementadas ✅

### 1. Cache Optimizado (TTL 600s)
- **Antes**: 30 segundos → 120 requests/hora por usuario
- **Ahora**: 600 segundos → 6 requests/hora por usuario
- **Beneficio**: Evita Error 429 de Google API

### 2. Normalización de IDs
- **Problema resuelto**: Merge fallaba con espacios o mayúsculas inconsistentes
- **Implementación**: `.str.strip().str.lower()` en todos los id_cuenta
- **Resultado**: Merge 100% confiable

### 3. Logging Profesional
- Reemplazados todos los `print()` por `logging.info/error/warning`
- Formato: `[HH:MM:SS] LEVEL: mensaje`

### 4. Append Incremental
- **Antes**: `clear() + update()` → Sobrescribía TODO
- **Ahora**: `append_rows()` → Solo agrega registros nuevos
- **Beneficio**: Previene race conditions y timeouts

### 5. Validación de Credenciales
- Verifica que `st.secrets["gcp_service_account"]` existe antes de usarlo
- Previene crashes en clones del repositorio

## 🔧 Pendientes (No Crítico)

### 1. Modularización del Código
**Estado**: El archivo tiene 1800+ líneas

**Recomendación**: Dividir en módulos
```
social_media_matrix/
├── app.py              # Main + navegación
├── data_manager.py     # Google Sheets + CSV
├── styles.py           # CSS + UI helpers
└── config.py           # Constantes + COLEGIOS_MARISTAS
```

**Implementación**:
```python
# app.py
from data_manager import load_data, save_batch
from styles import inject_custom_css
from config import COLEGIOS_MARISTAS
```

### 2. Catálogo Dinámico de Colegios
**Problema actual**: `COLEGIOS_MARISTAS` está hardcoded

**Solución**: Crear tercera hoja en Google Sheets llamada `catalogo`
```
| entidad                  | plataforma | usuario_red        |
|--------------------------|------------|--------------------|
| Centro Universitario MX  | Facebook   | @centrounivmx      |
| Centro Universitario MX  | Instagram  | @centrounivmx      |
```

**Beneficio**: Agregar colegios sin editar código

### 3. Contenedores Nativos de Streamlit
**Reemplazar**:
```python
st.markdown('<div class="css-card">', unsafe_allow_html=True)
# ... contenido
st.markdown('</div>', unsafe_allow_html=True)
```

**Por**:
```python
with st.container(border=True):
    # ... contenido
```

**Beneficio**: 
- Soporte nativo de modo claro/oscuro
- Compatible con futuras versiones de Streamlit
- Menos código CSS personalizado

### 4. Deprecation Warnings
- `use_container_width=True` → `width='stretch'` (post-2025)
- `worksheet.update('A1', data)` → `worksheet.update(values=data, range_name='A1')`

## 🗄️ Escalabilidad (Futuro Lejano)

### Cuándo migrar a Base de Datos Real
**Señales de alarma**:
- Más de 10,000 filas en Google Sheets
- Carga de página > 5 segundos
- Errores de timeout frecuentes

**Opciones de migración**:
1. **SQLite** (simple, local, gratis)
2. **PostgreSQL** (producción, escalable)
3. **BigQuery** (Google Cloud, ideal para analytics)

### Implementación con SQLite (más fácil)
```python
import sqlite3

def load_data():
    conn = sqlite3.connect('champilytics.db')
    cuentas = pd.read_sql('SELECT * FROM cuentas', conn)
    # Filtro por fecha directamente en SQL
    metricas = pd.read_sql('''
        SELECT * FROM metricas 
        WHERE fecha >= date('now', '-6 months')
    ''', conn)
    conn.close()
    return cuentas, metricas
```

## 📊 Monitoreo Recomendado

### Métricas a observar
- Tiempo de carga de `load_data()` (meta: < 2 segundos)
- Número de errores 429 por día (meta: 0)
- Tamaño de Google Sheets (alerta: > 5,000 filas)

### Herramientas
- **Streamlit Cloud**: Logs automáticos
- **Google Cloud Console**: Cuota de API usage

## 🎯 Roadmap Sugerido

| Prioridad | Tarea | Tiempo estimado |
|-----------|-------|-----------------|
| ✅ Alta | Normalización de IDs | Completado |
| ✅ Alta | Cache optimizado | Completado |
| ⚠️ Media | Modularizar código | 2-3 horas |
| 🟡 Baja | Catálogo dinámico | 1-2 horas |
| 🔵 Futura | Migrar a PostgreSQL | 1 semana |

---

**Última actualización**: Noviembre 24, 2025  
**Versión de la app**: v13.0 • Dos Hojas (Optimizada)
