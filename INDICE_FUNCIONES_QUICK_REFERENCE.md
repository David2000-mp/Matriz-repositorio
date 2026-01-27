# 📑 ÍNDICE COMPLETO DE FUNCIONES - QUICK REFERENCE

**Versión:** 2.1.0  
**Última Actualización:** 8 de Enero de 2026

---

## 🗂️ TABLA DE CONTENIDOS

- [data_saver.py](#data_saverpy) - 8 funciones
- [data_loader.py](#data_loaderpy) - 6 funciones
- [data_manager.py](#data_managerpy) - 5 funciones
- [sheets_connector.py](#sheets_connectorpy) - 2 funciones
- [analytics.py](#analyticspy) - 4+ funciones
- [helpers.py](#helperspy) - 6+ funciones
- [reports.py](#reportspy) - 2 funciones
- [logger.py](#loggerpy) - 6 funciones
- [Views (Streamlit)](#views-streamlit) - 6 vistas

---

## data_saver.py

### 1. `get_id(entidad, plataforma, usuario_red, df_cuentas_cache=None) → str`

**Tipo:** Generador de IDs  
**Parámetros:** 
- `entidad: str` - Nombre institución
- `plataforma: str` - Red social
- `usuario_red: str` - Username
- `df_cuentas_cache: pd.DataFrame | None` - Cache opcional

**Retorna:** `str` - Hash MD5 (32 chars)

**Lógica:**
1. Normaliza inputs
2. Busca en cache
3. Genera hash determinístico si no existe

**Ejemplo:**
```python
id_cuenta = get_id("Colegio A", "Instagram", "@colegioa")
# → "abc123def456..."
```

---

### 2. `_get_metricas_csv_path() → Path`

**Tipo:** Auxiliar interna  
**Retorna:** `Path` - Ruta CSV métricas

**Nota:** No usar directamente, es para tests

---

### 3. `sync_cuentas_to_sheets(df_cuentas) → bool`

**Tipo:** Sincronizador  
**Parámetros:**
- `df_cuentas: pd.DataFrame` - Datos cuentas

**Retorna:** `bool` - Éxito/Fallo

**Operaciones:**
1. Conecta Google Sheets
2. Crea/actualiza hoja "cuentas"
3. Sube datos (headers + filas)

---

### 4. `asegurar_registro_cuenta(df_metricas) → None`

**Tipo:** Validador  
**Parámetros:**
- `df_metricas: pd.DataFrame` - Datos métricos

**Operaciones:**
1. Verifica cuentas existentes
2. Identifica nuevas
3. Agrega a CSV + Sheets

**Uso:** Automático en `save_batch()`

---

### 5. `save_batch(df, modo="append") → bool`

**Tipo:** Guardador  
**Parámetros:**
- `df: pd.DataFrame | list` - Datos
- `modo: str` - "append" | "replace"

**Retorna:** `bool` - Éxito

**Pasos:**
1. Convierte lista → DataFrame
2. Normaliza columnas
3. Calcula `engagement_rate`
4. Asegura cuentas
5. Guarda CSV
6. Sincroniza Sheets

---

### 6. `save_comment(entidad, mes, comentario) → bool`

**Tipo:** Guardador  
**Parámetros:**
- `entidad: str` - Institución
- `mes: str` - Período (ej: "2025-01")
- `comentario: str` - Texto

**Retorna:** `bool` - Éxito

**Operación:** Agrega fila a hoja "comentarios"

---

### 7. `save_username_editado(entidad, plataforma, usuario_editado) → bool`

**Tipo:** Guardador  
**Parámetros:**
- `entidad: str` - Institución
- `plataforma: str` - Red social
- `usuario_editado: str` - Username correcto

**Retorna:** `bool` - Éxito

**Operación:** Actualiza o crea registro de edición

---

### 8. `guardar_datos(nuevo_df, modo="completo") → bool`

**Tipo:** Guardador Principal  
**Parámetros:**
- `nuevo_df: pd.DataFrame` - Datos a guardar
- `modo: str` - "completo" | vacío

**Retorna:** `bool` - Éxito

**Validaciones:**
- Columnas requeridas: id_cuenta, fecha, seguidores, alcance, interacciones, likes_promedio, engagement_rate
- Convierte fecha a 'YYYY-MM-DD'
- Deduplica por (id_cuenta, fecha)

**Estrategia:**
- Intenta Sheets
- Siempre respaldo CSV
- Retorna False si Sheets esperado pero falló

---

## data_loader.py

### 1. `validate_and_fill_columns(df, expected_cols) → pd.DataFrame`

**Tipo:** Validador  
**Parámetros:**
- `df: pd.DataFrame` - DataFrame entrada
- `expected_cols: list` - Columnas esperadas

**Operaciones:**
1. Normaliza nombres (lowercase)
2. Crea columnas faltantes
3. Convierte fecha → datetime
4. Limpia strings
5. Reemplaza IDs inválidos

**Retorna:** DataFrame validado

---

### 2. `_load_data_impl() → Tuple[DataFrame, DataFrame]`

**Tipo:** Implementación interna  
**Retorna:** `(df_cuentas, df_metricas)`

**Intenta:**
1. Google Sheets primero
2. CSV local como fallback

---

### 3. `load_data() → Tuple[DataFrame, DataFrame]`

**Tipo:** Cargador Principal  
**Retorna:** `(df_cuentas, df_metricas)`

**Características:**
- Con caché Streamlit
- Actualiza si hay cambios
- Llamada pública (usar esta)

---

### 4. `load_comments() → pd.DataFrame`

**Tipo:** Cargador  
**Retorna:** DataFrame comentarios

**Columnas:** [entidad, mes, comentario]

---

### 5. `load_configs() → pd.DataFrame`

**Tipo:** Cargador  
**Retorna:** DataFrame configuración

**Columnas:** [entidad, meta_seguidores, meta_engagement]

---

### 6. `load_usernames_editados() → pd.DataFrame`

**Tipo:** Cargador  
**Retorna:** DataFrame ediciones

**Columnas:** [entidad, plataforma, usuario_editado, fecha_modificacion]

---

## data_manager.py

### 1. `get_reverse_lookup() → Dict[str, Dict[str, str]]`

**Tipo:** Mapeo  
**Retorna:** Dict inverso (usuario → entidad/plataforma)

**Estructura:**
```python
{
    "usuario1": {"entidad": "...", "plataforma": "..."},
    ...
}
```

---

### 2. `reload_colegios_maristas() → None`

**Tipo:** Recargador  
**Operación:** Actualiza lista de colegios (puede ser desde Sheets)

---

### 3. `init_files() → None`

**Tipo:** Inicializador  
**Operación:** Crea archivos CSV si no existen

---

### 4. `reset_db() → None`

**Tipo:** Limpiador  
**Operación:** Borra/reinicia CSV (⚠️ CUIDADO - No recuperable)

---

### 5. `conectar_sheets() → Optional[gspread.Spreadsheet]`

**Tipo:** Conector  
**Retorna:** Objeto spreadsheet o None

**Pasos:**
1. Obtiene credenciales
2. Autentica OAuth2
3. Abre spreadsheet

---

## sheets_connector.py

### 1. `_get_service_account_config() → Optional[dict]`

**Tipo:** Configurador  
**Retorna:** Dict credenciales o None

**Fuentes:**
- Variable entorno: `GOOGLE_SHEETS_CREDS`
- Archivo: `secrets/service_account.json`

---

### 2. `conectar_sheets() → Optional[gspread.Spreadsheet]`

**Tipo:** Conector  
**Retorna:** Spreadsheet autenticado o None

---

## analytics.py

**Nota:** Funciones específicas varían (ver código fuente)

### Funciones Principales:

1. **KPI Calculations** - Seguidores, engagement, etc.
2. **Trend Analysis** - Crecimiento/declive
3. **Anomaly Detection** - Valores atípicos
4. **Aggregations** - Por institución/período

---

## helpers.py

### 1. `get_image_base64(image_path) → str`

**Tipo:** Conversor  
**Parámetros:**
- `image_path: Path` - Ruta imagen

**Retorna:** `str` - Base64 codificado

---

### 2. `load_image(filename) → Optional[str]`

**Tipo:** Cargador  
**Parámetros:**
- `filename: str` - Nombre archivo (en carpeta `images/`)

**Retorna:** Base64 o None

---

### 3. `get_banner_css(image_filename, height="200px") → str`

**Tipo:** Generador CSS  
**Retorna:** CSS con imagen codificada

---

### 4. `simular(df_metricas, entidad, meses, crecimiento_mensual_follower, tasa_engagement) → pd.DataFrame`

**Tipo:** Simulador  
**Parámetros:**
- `df_metricas: pd.DataFrame` - Histórico
- `entidad: str` - Institución
- `meses: int` - Meses a proyectar
- `crecimiento_mensual_follower: float` - Tasa (ej: 0.05 = 5%)
- `tasa_engagement: float` - Meta engagement (0-100)

**Retorna:** DataFrame con proyecciones

**Fórmula:** $S_{n+1} = S_n \times (1 + tasa)$

---

### 5. `generar_reporte_html(df, titulo="Reporte de Métricas") → str`

**Tipo:** Generador HTML  
**Retorna:** String HTML completo

---

### 6. `generate_social_url(platform, username) → str`

**Tipo:** Constructor URL  
**Retorna:** URL a perfil social

**Ejemplos:**
- ("Instagram", "user") → "https://instagram.com/user"
- ("Facebook", "user") → "https://facebook.com/user"

---

## reports.py

### 1. `generate_pdf_report(school_name, period, kpis, anomalies, health_score) → bytes`

**Tipo:** Generador PDF  
**Parámetros:**
- `school_name: str` - Institución
- `period: str` - Período
- `kpis: dict` - KPIs calculados
- `anomalies: list` - Anomalías detectadas
- `health_score: float` - Puntuación 0-100

**Retorna:** `bytes` - PDF generado

---

### 2. `generate_html_report(...) → str`

**Tipo:** Generador HTML  
**Parámetros:** Similar a PDF

**Retorna:** `str` - HTML interactivo

---

## logger.py

### 1. `get_logger(name="matriz_redes", level=logging.INFO) → logging.Logger`

**Tipo:** Logger factory  
**Parámetros:**
- `name: str` - Nombre logger
- `level: int` - Nivel logging

**Retorna:** Logger configurado

---

### 2. `set_production_mode() → None`

**Tipo:** Configurador  
**Operación:** Modo producción (sin debug)

---

### 3. `set_debug_mode(enabled=True) → None`

**Tipo:** Configurador  
**Operación:** Activa/desactiva debug verboso

---

### 4. `get_error_log_contents() → Optional[str]`

**Tipo:** Lector  
**Retorna:** Contenido archivo errores

---

### 5. `log_exception(logger, message="Excepción capturada") → None`

**Tipo:** Logger  
**Operación:** Registra excepción actual

---

### 6. `log_function_call(logger, func_name, **kwargs) → None`

**Tipo:** Logger  
**Operación:** Registra llamada función

---

## Views (Streamlit)

### 1. landing.py: `render(df=None)`

**Vista:** Página de Inicio  
**Parámetros:** `df` opcional

**Contenido:**
- Logo/Presentación
- Instrucciones rápidas
- Links a otras vistas

---

### 2. dashboard.py: `render(df=None)`

**Vista:** Dashboard Principal  
**Parámetros:** `df` opcional

**Contenido:**
- KPIs agregados
- Gráficos por institución
- Tablas de datos

**Función Auxiliar:**
```python
paginate_dataframe(df, page_size=1000, page_key="page") → DataFrame
```

---

### 3. analytics.py: `render(df=None)`

**Vista:** Análisis Comparativos  
**Parámetros:** `df` opcional

**Contenido:**
- Comparativas entre instituciones
- Tendencias
- Análisis por período

---

### 4. data_entry.py: `render(df=None)`

**Vista:** Captura Manual  
**Parámetros:** `df` opcional

**Contenido:**
- Formulario para ingreso de métricas
- Validación en vivo
- Guardado a Sheets/CSV

---

### 5. settings.py: `render(df=None)`

**Vista:** Configuración  
**Parámetros:** `df` opcional

**Contenido:**
- Editar metas por institución
- Gestión de usuarios
- Preferencias

---

### 6. changelog.py: `render(df=None)`

**Vista:** Historial  
**Parámetros:** `df` opcional

**Funciones Auxiliares:**
```python
render_changelog()  # Historial de cambios
render_roadmap()    # Roadmap futuro
```

**Contenido:**
- Versiones anteriores
- Changelog detallado
- Roadmap v2.2+

---

## 🔍 BÚSQUEDA RÁPIDA POR FUNCIONALIDAD

### Necesito... Usar esta función:

| Necesidad | Función | Módulo |
|-----------|---------|--------|
| Generar ID único | `get_id()` | data_saver |
| Guardar métricas | `save_batch()` | data_saver |
| Cargar datos | `load_data()` | data_loader |
| Conectar Sheets | `conectar_sheets()` | sheets_connector |
| Calcular engagement | `save_batch()` | data_saver |
| Generar reporte | `generate_pdf_report()` | reports |
| Convertir imagen | `get_image_base64()` | helpers |
| Simular futuro | `simular()` | helpers |
| Registrar error | `log_exception()` | logger |
| Detectar anomalías | analytics.* | analytics |
| Ver dashboard | `dashboard.render()` | views |
| Capturar datos | `data_entry.render()` | views |

---

## ⚠️ FUNCIONES CON PROBLEMAS CONOCIDOS

| Función | Problema | Línea | Estado |
|---------|----------|-------|--------|
| `save_batch()` | Type error fillna | 239-240 | 🔴 Crítico |
| `guardar_datos()` | Type error strftime | 398 | 🔴 Crítico |
| `sync_cuentas_to_sheets()` | Sin reintentos | 72 | 🟡 Mediano |
| `guardar_datos()` | Deduplicación | 271 | 🟡 Mediano |
| `guardar_datos()` | Lógica retorno | 430 | 🟡 Mediano |

---

## 📦 CONSTANTES IMPORTANTES

### Columnas Esperadas

```python
COLS_CUENTAS = ["id_cuenta", "entidad", "plataforma", "usuario_red"]

COLS_METRICAS = [
    "id_cuenta", "fecha", "seguidores", "alcance",
    "interacciones", "likes_promedio", "engagement_rate"
]

COLS_CONFIG = ["entidad", "meta_seguidores", "meta_engagement"]

COLS_COMENTARIOS = ["entidad", "mes", "comentario"]

COLS_USERNAMES_EDITADOS = [
    "entidad", "plataforma", "usuario_editado", "fecha_modificacion"
]
```

### Rutas

```python
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CUENTAS_CSV = DATA_DIR / "cuentas.csv"
METRICAS_CSV = DATA_DIR / "metricas.csv"
```

---

## 🔐 VARIABLES DE ENTORNO

```
GOOGLE_SHEETS_CREDS     → JSON credenciales Google
STREAMLIT_SERVER_PORT   → Puerto Streamlit (default: 8501)
LOG_LEVEL               → Nivel logging
```

---

## 📝 NOTAS FINALES

- ✅ Todas las funciones tienen docstring
- ✅ Type hints presentes (excepto algunas vistas)
- ✅ Manejo de excepciones en lugares críticos
- ⚠️ Tests unitarios incompletos
- ⚠️ Documentación externa en progreso

---

**Documento Generado:** 8 Enero 2026  
**Versión App:** 2.1.0  
**Total Funciones:** 40+

