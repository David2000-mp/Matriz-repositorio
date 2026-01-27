# 📋 REPORTE COMPLETO: ERRORES Y FUNCIONES DE LA APP

**Generado:** 8 de Enero de 2026  
**Proyecto:** Social Media Matrix - CHAMPILEAKS  
**Versión:** 2.1.0 - Sprint 5

---

## 🔴 PARTE 1: REPORTE DE ERRORES DETECTADOS

### Errores de Tipo (Pylance)

Se han detectado **3 errores de tipo** en `utils/data_saver.py`:

#### ❌ Error 1: `fillna()` sobre float (Línea 239-240)

**Ubicación:** [data_saver.py](data_saver.py#L239-L240)

**Código problemático:**
```python
seguidores = pd.to_numeric(df.get("seguidores", 0), errors="coerce").fillna(0)
interacciones = pd.to_numeric(df.get("interacciones", 0), errors="coerce").fillna(0)
```

**Problema:**
- `pd.to_numeric()` devuelve un `Series` cuando recibe un `Series`, pero devuelve `float` cuando recibe un escalar
- `df.get("seguidores", 0)` devuelve `0` (un escalar) si la columna no existe
- No se puede llamar `.fillna()` sobre un escalar `float`

**Solución recomendada:**
```python
seguidores_col = df.get("seguidores")
if seguidores_col is not None:
    seguidores = pd.to_numeric(seguidores_col, errors="coerce").fillna(0)
else:
    seguidores = pd.Series([0] * len(df))

interacciones_col = df.get("interacciones")
if interacciones_col is not None:
    interacciones = pd.to_numeric(interacciones_col, errors="coerce").fillna(0)
else:
    interacciones = pd.Series([0] * len(df))
```

---

#### ❌ Error 2: `strftime()` sobre Properties (Línea 398)

**Ubicación:** [data_saver.py](data_saver.py#L398)

**Código problemático:**
```python
df_copy['fecha'] = df_copy['fecha'].dt.strftime('%Y-%m-%d')
```

**Problema:**
- `.dt` es un accessor de pandas para Series tipo datetime
- Cuando se accede a `.dt.strftime()`, devuelve una Series de strings
- El type checker (Pylance) no reconoce que `strftime()` es un método válido en el accessor
- Esto es un falso positivo del type checker, pero puede causar problemas si `fecha` no es datetime

**Solución recomendada:**
```python
if 'fecha' in df_copy.columns and pd.api.types.is_datetime64_any_dtype(df_copy['fecha']):
    df_copy['fecha'] = df_copy['fecha'].dt.strftime('%Y-%m-%d')
else:
    df_copy['fecha'] = pd.to_datetime(df_copy['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
```

---

### Problemas Lógicos Detectados

#### ⚠️ Problema 1: Falta de Validación de Entrada en `get_id()`

**Ubicación:** [data_saver.py](data_saver.py#L19)

**Descripción:**
- La función `get_id()` no valida si `entidad`, `plataforma` o `usuario_red` son `None` antes de normalizar
- Si alguno es `None`, `.strip()` lanzará un `AttributeError`

**Código actual:**
```python
entidad_clean = (entidad or "").strip().lower()  # ✅ Está protegido
plataforma_clean = (plataforma or "").strip().lower()  # ✅ Está protegido
usuario_clean = (usuario_red or "").strip().lower()  # ✅ Está protegido
```

**Status:** ✅ **ESTÁ BIEN** - Usa `or ""` para manejar `None`

---

#### ⚠️ Problema 2: Falta de Manejo de Excepciones en `sync_cuentas_to_sheets()`

**Ubicación:** [data_saver.py](data_saver.py#L72)

**Descripción:**
- Si Google Sheets devuelve un error de autenticación, la función falla silenciosamente
- No hay reintentos automáticos

**Status:** ⚠️ **MEDIANO** - Necesita mejora de resiliencia

---

#### ⚠️ Problema 3: Deduplicación por `(id_cuenta, fecha)` Incompleta

**Ubicación:** [data_saver.py](data_saver.py#L271)

**Descripción:**
```python
combined_df = (
    combined_df.sort_values(by=['id_cuenta', 'fecha'])
               .drop_duplicates(subset=['id_cuenta', 'fecha'], keep='last')
)
```

**Problema:**
- Si `fecha` es de tipo string y no datetime, la deduplicación puede no funcionar correctamente
- Dos strings "2025-01-08" y "2025-01-08 10:30" se considerarían diferentes

**Status:** ⚠️ **MEDIANO** - Requiere estandarización de tipos

---

#### ⚠️ Problema 4: Retorno de Valor Ambiguo en `guardar_datos()`

**Ubicación:** [data_saver.py](data_saver.py#L361)

**Descripción:**
```python
# Política de retorno honesta: si hubo spreadsheet pero no hubo éxito en Sheets, retornar False
if spreadsheet and not sheets_success:
    return False
# En otro caso, éxito si cualquiera funcionó
return sheets_success or csv_success
```

**Problema:**
- La lógica es confusa: retorna `False` si Sheets falla pero retorna `True` si CSV funciona
- Esto puede dar un falso positivo si solo CSV funciona y Sheets se esperaba sincronizar

**Status:** ⚠️ **MEDIANO** - Necesita clarificación

---

### Resumen de Errores

| ID | Severidad | Tipo | Ubicación | Estado |
|----|-----------|------|-----------|--------|
| E1 | 🔴 Alto | Type Error | `data_saver.py:239-240` | Requiere Fix |
| E2 | 🔴 Alto | Type Error | `data_saver.py:398` | Requiere Fix |
| E3 | 🟡 Medio | Logic | `data_saver.py:72` | Mejora |
| E4 | 🟡 Medio | Logic | `data_saver.py:271` | Mejora |
| E5 | 🟡 Medio | Logic | `data_saver.py:430` | Clarificar |

---

## 🟢 PARTE 2: GUÍA COMPLETA DE FUNCIONES

### 📦 Módulo: `utils/data_saver.py`

**Propósito:** Guardado de datos en Google Sheets y CSV local

#### 1️⃣ `get_id(entidad, plataforma, usuario_red, df_cuentas_cache=None) → str`

**Descripción:**
Genera o recupera un ID único (determinístico) para una combinación entidad-plataforma-usuario.

**Parámetros:**
- `entidad` (str): Nombre de la institución (ej: "Colegio México (Roma)")
- `plataforma` (str): Red social (ej: "Instagram", "Facebook", "TikTok")
- `usuario_red` (str): Username/handle en esa red social
- `df_cuentas_cache` (DataFrame, opcional): Cache de cuentas existentes. Si es None, carga automáticamente

**Retorna:**
- `str`: ID de 32 caracteres (hash MD5) o ID existente si encontrado

**Flujo:**
1. Normaliza entradas a lowercase y sin espacios
2. Busca en cache si existe registro previo
3. Si existe, devuelve `id_cuenta` existente
4. Si no existe, genera hash MD5 determinístico

**Ejemplo:**
```python
id_cuenta = get_id("Colegio México (Roma)", "Instagram", "colegiomexicoroma")
# Retorna: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" (hash MD5)
```

---

#### 2️⃣ `_get_metricas_csv_path() → Path`

**Descripción:**
Obtiene la ruta del archivo CSV de métricas, permitiendo monkeypatch via `utils.data_manager` en tests.

**Retorna:**
- `Path`: Ruta al archivo CSV de métricas (ej: `data/metricas.csv`)

**Nota:** Función interna, no usar directamente

---

#### 3️⃣ `sync_cuentas_to_sheets(df_cuentas: pd.DataFrame) → bool`

**Descripción:**
Sincroniza la tabla de cuentas a la hoja "cuentas" de Google Sheets.

**Parámetros:**
- `df_cuentas` (DataFrame): DataFrame con columnas [id_cuenta, entidad, plataforma, usuario_red]

**Retorna:**
- `bool`: True si sincronización exitosa, False si falló

**Operación:**
1. Conecta a Google Sheets
2. Obtiene o crea hoja "cuentas"
3. Limpia valores NaN/Inf
4. Sube datos (headers + filas)

**Ejemplo:**
```python
df_cuentas = pd.DataFrame({
    'id_cuenta': ['abc123', 'def456'],
    'entidad': ['Colegio A', 'Colegio B'],
    'plataforma': ['Instagram', 'Facebook'],
    'usuario_red': ['colegioa', 'colegiob']
})
if sync_cuentas_to_sheets(df_cuentas):
    print("✅ Sincronizado a Sheets")
else:
    print("❌ Error al sincronizar")
```

---

#### 4️⃣ `asegurar_registro_cuenta(df_metricas: pd.DataFrame) → None`

**Descripción:**
Verifica que todas las cuentas en un DataFrame de métricas existan en el CSV de cuentas. Si no existen, las registra automáticamente.

**Parámetros:**
- `df_metricas` (DataFrame): DataFrame con columnas que incluyan id_cuenta, entidad, plataforma, usuario_red

**Operación:**
1. Carga cuentas existentes desde CSV
2. Identifica nuevas cuentas en el batch
3. Agrega nuevas cuentas al CSV
4. Sincroniza a Google Sheets

**Nota:** Función de propósito general, se ejecuta automáticamente en `save_batch()`

---

#### 5️⃣ `save_batch(df, modo="append") → bool`

**Descripción:**
Prepara, normaliza y guarda un batch de métricas.

**Parámetros:**
- `df` (DataFrame | list): Datos a guardar. Acepta lista de dicts o DataFrame
- `modo` (str): "append" (agregar) o "replace" (reemplazar todo)

**Retorna:**
- `bool`: True si guardado exitoso, False/None si falló

**Operaciones:**
1. Convierte lista a DataFrame si es necesario
2. Normaliza columnas y valores
3. Calcula `engagement_rate` si falta: $(interacciones/seguidores) \times 100$
4. Asegura que las cuentas existan
5. Guarda en CSV local
6. Sincroniza a Google Sheets vía `data_manager.guardar_datos()`

**Ejemplo:**
```python
batch = [
    {
        'id_cuenta': 'abc123',
        'entidad': 'Colegio A',
        'plataforma': 'Instagram',
        'usuario_red': 'colegioa',
        'fecha': '2025-01-08',
        'seguidores': 10000,
        'alcance': 5000,
        'interacciones': 500,
        'likes_promedio': 100
    }
]
if save_batch(batch):
    print("✅ Batch guardado")
```

---

#### 6️⃣ `save_comment(entidad, mes, comentario) → bool`

**Descripción:**
Guarda un comentario o nota sobre una institución en un período.

**Parámetros:**
- `entidad` (str): Nombre de la institución
- `mes` (str): Período (ej: "2025-01", "Enero 2025")
- `comentario` (str): Texto del comentario

**Retorna:**
- `bool`: True si guardado exitoso

**Operación:**
1. Conecta a Google Sheets
2. Obtiene o crea hoja "comentarios"
3. Agrega fila con [entidad, mes, comentario]
4. Limpia caché de Streamlit

---

#### 7️⃣ `save_username_editado(entidad, plataforma, usuario_editado) → bool`

**Descripción:**
Guarda o actualiza un username que fue editado/corregido manualmente.

**Parámetros:**
- `entidad` (str): Institución
- `plataforma` (str): Red social
- `usuario_editado` (str): Nuevo nombre de usuario correcto

**Retorna:**
- `bool`: True si guardado exitoso

**Operación:**
1. Busca si existe registro previo
2. Si existe, actualiza la fila
3. Si no existe, agrega nueva fila
4. Registra timestamp de modificación

---

#### 8️⃣ `guardar_datos(nuevo_df, modo="completo") → bool`

**Descripción:**
Función principal para guardar datos en Google Sheets y CSV local.

**Parámetros:**
- `nuevo_df` (DataFrame): Datos a guardar con columnas requeridas
- `modo` (str): "completo" (reemplazar todo) o vacío (agregar)

**Retorna:**
- `bool`: True si guardado exitoso en Sheets Y/O CSV

**Validaciones:**
- Verifica que existan columnas: id_cuenta, fecha, seguidores, alcance, interacciones, likes_promedio, engagement_rate
- Convierte fecha a formato 'YYYY-MM-DD'
- Deduplica por (id_cuenta, fecha)

**Estrategia de Guardado:**
1. Intenta sincronizar a Google Sheets (modo="completo" limpia primero)
2. Siempre guarda respaldo en CSV local
3. Si Sheets existe pero falla → retorna False
4. Si Sheets no existe pero CSV funciona → retorna True

---

### 📦 Módulo: `utils/data_loader.py`

**Propósito:** Carga de datos desde Google Sheets y CSV

#### 1️⃣ `validate_and_fill_columns(df, expected_cols) → pd.DataFrame`

**Descripción:**
Normaliza, rellena columnas faltantes y reordena según esquema esperado.

**Parámetros:**
- `df` (DataFrame): DataFrame a validar
- `expected_cols` (list): Lista de columnas esperadas

**Operaciones:**
1. Normaliza nombres de columnas a lowercase sin espacios
2. Crea columnas faltantes con valores None
3. Convierte columnas de fecha a datetime (NaT si hay error)
4. Limpia strings en entidad, plataforma, usuario_red
5. Reemplaza valores inválidos de id_cuenta ("nan", "none", "inf", etc.) con "unknown"

**Retorna:**
- DataFrame con columnas validadas y reordenadas

---

#### 2️⃣ `_load_data_impl() → Tuple[pd.DataFrame, pd.DataFrame]`

**Descripción:**
Implementación interna de carga de datos. Intenta cargar desde Google Sheets primero, luego desde CSV local.

**Retorna:**
- Tupla: (DataFrame de cuentas, DataFrame de métricas)

---

#### 3️⃣ `load_data() → Tuple[pd.DataFrame, pd.DataFrame]`

**Descripción:**
Carga datos principales desde Google Sheets o CSV. Versión pública con caché de Streamlit.

**Retorna:**
- Tupla: (df_cuentas, df_metricas)

**Caché:** Almacena resultado para reducir llamadas a Sheets (invalida cuando hay cambios)

---

#### 4️⃣ `load_comments() → pd.DataFrame`

**Descripción:**
Carga tabla de comentarios desde Google Sheets.

**Retorna:**
- DataFrame con columnas [entidad, mes, comentario]

---

#### 5️⃣ `load_configs() → pd.DataFrame`

**Descripción:**
Carga configuraciones de metas por institución.

**Retorna:**
- DataFrame con columnas [entidad, meta_seguidores, meta_engagement]

---

#### 6️⃣ `load_usernames_editados() → pd.DataFrame`

**Descripción:**
Carga tabla de usernames que fueron editados/corregidos manualmente.

**Retorna:**
- DataFrame con columnas [entidad, plataforma, usuario_editado, fecha_modificacion]

---

### 📦 Módulo: `utils/data_manager.py`

**Propósito:** Gestión centralizada de datos (importa desde data_loader, data_saver, etc.)

#### 1️⃣ `get_reverse_lookup() → Dict[str, Dict[str, str]]`

**Descripción:**
Crea un mapeo inverso usuario_red → (entidad, plataforma).

**Retorna:**
```python
{
    "colegiomexicoroma": {
        "entidad": "Colegio México (Roma)",
        "plataforma": "Instagram"
    },
    ...
}
```

---

#### 2️⃣ `reload_colegios_maristas() → None`

**Descripción:**
Recarga la lista de colegios Maristas desde la fuente (puede ser Google Sheets o constante hardcoded).

---

#### 3️⃣ `init_files() → None`

**Descripción:**
Inicializa archivos CSV locales si no existen.

---

#### 4️⃣ `reset_db() → None`

**Descripción:**
Limpia/reinicia la base de datos local (CSV).

---

#### 5️⃣ `conectar_sheets() → Optional[gspread.Spreadsheet]`

**Descripción:**
Conecta a Google Sheets usando credenciales de service account.

**Retorna:**
- Objeto spreadsheet si exitoso, None si falla

---

### 📦 Módulo: `utils/sheets_connector.py`

**Propósito:** Conectividad a Google Sheets

#### 1️⃣ `_get_service_account_config() → Optional[dict]`

**Descripción:**
Obtiene credenciales de Google Sheets desde variable de entorno o archivo secrets.

**Retorna:**
- Dict con credenciales JSON, o None si no existen

---

#### 2️⃣ `conectar_sheets() → Optional[gspread.Spreadsheet]`

**Descripción:**
Realiza autenticación y conexión a Google Sheets.

**Pasos:**
1. Obtiene credenciales
2. Autentica con OAuth2
3. Abre spreadsheet específico
4. Retorna objeto gspread.Spreadsheet

---

### 🎨 Módulo: `utils/helpers.py`

**Propósito:** Funciones auxiliares de utilidad general

#### 1️⃣ `get_image_base64(image_path) → str`

**Descripción:**
Convierte una imagen a base64 para incrustar en HTML.

**Retorna:**
- String en formato base64 de la imagen

---

#### 2️⃣ `load_image(filename) → Optional[str]`

**Descripción:**
Carga una imagen desde la carpeta `images/` y la convierte a base64.

---

#### 3️⃣ `get_banner_css(image_filename, height="200px") → str`

**Descripción:**
Genera CSS para mostrar una imagen como banner de fondo.

**Retorna:**
- String CSS con imagen codificada en base64

---

#### 4️⃣ `simular(df_metricas, entidad, meses, crecimiento_mensual_follower, tasa_engagement) → pd.DataFrame`

**Descripción:**
Simula métricas futuras basado en crecimiento y engagement proyectados.

**Parámetros:**
- `df_metricas` (DataFrame): Métricas históricas
- `entidad` (str): Institución a simular
- `meses` (int): Número de meses a proyectar
- `crecimiento_mensual_follower` (float): Tasa de crecimiento mensual (0.05 = 5%)
- `tasa_engagement` (float): Engagement rate objetivo (0-100)

**Retorna:**
- DataFrame con métricas proyectadas

**Fórmula Simulada:**
- Seguidores: $S_{n+1} = S_n \times (1 + tasa)$
- Engagement: se proyecta hacia la `tasa_engagement` objetivo

---

#### 5️⃣ `generar_reporte_html(df, titulo="Reporte de Métricas") → str`

**Descripción:**
Genera un reporte HTML completo con tablas y gráficos.

**Retorna:**
- String HTML con tablas, estilos y datos formateados

---

#### 6️⃣ `generate_social_url(platform, username) → str`

**Descripción:**
Genera URL a perfil social basado en plataforma y username.

**Ejemplos:**
- ("Instagram", "colegiomexicoroma") → "https://instagram.com/colegiomexicoroma"
- ("Facebook", "colegiomexicoroma") → "https://facebook.com/colegiomexicoroma"

---

### 📊 Módulo: `utils/analytics.py`

**Propósito:** Análisis y cálculos analíticos de métricas

**Funciones principales (ver código fuente para detalles):**
- Cálculo de tendencias
- Detección de anomalías
- Agregación de KPIs
- Comparativas entre instituciones

---

### 📋 Módulo: `utils/logger.py`

**Propósito:** Sistema de logging centralizado

#### 1️⃣ `get_logger(name="matriz_redes", level=logging.INFO) → logging.Logger`

**Descripción:**
Obtiene un logger configurado para la aplicación.

**Retorna:**
- Objeto logger con handlers para archivo y consola

---

#### 2️⃣ `set_production_mode() → None`

**Descripción:**
Configura el logger en modo producción (sin debug verboso).

---

#### 3️⃣ `set_debug_mode(enabled=True) → None`

**Descripción:**
Activa/desactiva modo debug con logging detallado.

---

#### 4️⃣ `get_error_log_contents() → Optional[str]`

**Descripción:**
Lee y retorna contenido del archivo de error log.

---

#### 5️⃣ `log_exception(logger, message="Excepción capturada") → None`

**Descripción:**
Registra una excepción actual con stack trace.

---

#### 6️⃣ `log_function_call(logger, func_name, **kwargs) → None`

**Descripción:**
Registra una llamada de función con sus argumentos.

---

### 🎯 Módulo: `utils/reports.py`

**Propósito:** Generación de reportes PDF e HTML

#### 1️⃣ `generate_pdf_report(school_name, period, kpis, anomalies, health_score) → bytes`

**Descripción:**
Genera un reporte PDF completo para una institución.

**Parámetros:**
- `school_name` (str): Nombre de la institución
- `period` (str): Período reportado (ej: "Enero 2025")
- `kpis` (dict): KPIs calculados
- `anomalies` (list): Anomalías detectadas
- `health_score` (float): Puntuación de salud (0-100)

**Retorna:**
- Bytes del PDF generado

---

#### 2️⃣ `generate_html_report(...) → str`

**Descripción:**
Genera un reporte HTML interactivo.

**Retorna:**
- String HTML

---

### 🖼️ Módulo: `views/`

**Propósito:** Interfaces Streamlit de la aplicación

#### Vista: `landing.py`
- **Función:** `render(df=None)`
- **Descripción:** Página de inicio con presentación de la aplicación

#### Vista: `dashboard.py`
- **Función:** `render(df=None)`
- **Función auxiliar:** `paginate_dataframe(df, page_size=1000, page_key="page")`
- **Descripción:** Dashboard principal con gráficos y KPIs agregados

#### Vista: `analytics.py`
- **Función:** `render(df=None)`
- **Descripción:** Análisis comparativos y tendencias entre instituciones

#### Vista: `data_entry.py`
- **Función:** `render(df=None)`
- **Descripción:** Formulario para ingreso manual de métricas

#### Vista: `settings.py`
- **Función:** `render(df=None)`
- **Descripción:** Configuración de metas, usuarios y ajustes

#### Vista: `changelog.py`
- **Función:** `render(df=None)`
- **Función auxiliar:** `render_changelog()`
- **Función auxiliar:** `render_roadmap()`
- **Descripción:** Historial de cambios y roadmap de versiones

#### Vista: `reports.py`
- **Función:** `render_report_view(df_metricas, trend_figures)`
- **Descripción:** Visualización y generación de reportes

---

## 📊 Arquitectura de la Aplicación

```
┌─────────────────────────────────────┐
│      app.py (Main Entry Point)      │
│  - Streamlit Page Config            │
│  - Sidebar Navigation               │
│  - Router de Vistas                 │
└─────────────────────────────────────┘
                   ↓
    ┌──────────────────────────────┐
    │    VIEWS (Streamlit UIs)     │
    ├──────────────────────────────┤
    │  - landing.py (Inicio)       │
    │  - dashboard.py (KPIs)       │
    │  - analytics.py (Análisis)   │
    │  - data_entry.py (Entrada)   │
    │  - settings.py (Config)      │
    │  - changelog.py (Versiones)  │
    └──────────────────────────────┘
                   ↓
    ┌──────────────────────────────┐
    │   UTILS (Lógica de Negocio)  │
    ├──────────────────────────────┤
    │  data_manager.py (Orquesta)  │
    │  data_loader.py (Lectura)    │
    │  data_saver.py (Escritura)   │
    │  sheets_connector.py (API)   │
    │  analytics.py (Cálculos)     │
    │  reports.py (Generador)      │
    │  helpers.py (Utilidades)     │
    │  logger.py (Logging)         │
    └──────────────────────────────┘
                   ↓
    ┌──────────────────────────────┐
    │  DATA SOURCES (Persistencia) │
    ├──────────────────────────────┤
    │  Google Sheets API           │
    │  Local CSV Files (backup)    │
    └──────────────────────────────┘
```

---

## 🔧 Flujo de Datos Típico

### Ingreso de Métricas:
1. Usuario ingresa datos en `data_entry.py` → `render()`
2. Se valida y normaliza en `save_batch()` → `data_saver.py`
3. Se asegura que cuentas existan en `asegurar_registro_cuenta()` → CSV
4. Se sincroniza a Google Sheets vía `guardar_datos()` → Google API
5. Se limpia caché de Streamlit

### Lectura de Métricas:
1. Vista solicita datos (ej: `dashboard.py`)
2. Carga con `load_data()` → `data_loader.py`
3. Intenta Google Sheets (si está disponible)
4. Fallback a CSV local si Sheets no responde
5. Se cachea en Streamlit para reducir llamadas

### Generación de Reporte:
1. Usuario selecciona institución y período en `reports.py`
2. Se carga datos históricos con `load_data()`
3. Se calcula KPIs con funciones en `analytics.py`
4. Se genera PDF/HTML con `generate_pdf_report()` o `generate_html_report()`
5. Se descarga o visualiza en la app

---

## 🚀 Recomendaciones para Mejoras

### Críticas (Requieren Atención Inmediata)

1. **Fijar Errores de Tipo** en `data_saver.py`:
   - Líneas 239-240: Cambiar `df.get()` por acceso seguro a columnas
   - Línea 398: Agregar validación de tipo antes de `dt.strftime()`

2. **Mejorar Manejo de Errores de Sheets**:
   - Agregar reintentos automáticos
   - Mejorar mensajes de error al usuario

### Importantes (Próximo Sprint)

3. **Estandarizar Fechas**: Todas las fechas deben ser `datetime64`, no strings

4. **Clarificar Lógica de Retorno**: `guardar_datos()` debe retornar explícitamente qué almacenamiento funcionó

5. **Agregar Validación de Columnas**: Antes de procesar, validar que todas las columnas requeridas existan

### Mejoras (Backlog)

6. **Caché Inteligente**: Implementar invalidación de caché basada en cambios reales

7. **Audit Trail**: Registrar quién, cuándo y qué cambió

8. **Sincronización Bidireccional**: Detectar cambios en Sheets y actualizar local

---

## 📝 Resumen Ejecutivo

**Total de Funciones Documentadas:** 40+

**Líneas de Código:** ~3,000

**Módulos Principales:** 8

**Vistas Streamlit:** 6

**Errores Detectados:** 5 (2 críticos, 3 mejorables)

**Estado General:** ✅ **FUNCIONAL** con mejoras pendientes

---

**Fin del Reporte**
