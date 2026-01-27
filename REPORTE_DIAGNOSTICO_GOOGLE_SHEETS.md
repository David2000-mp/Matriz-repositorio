# 📋 REPORTE DETALLADO DE DIAGNÓSTICO - GOOGLE SHEETS CONNECTIVITY

**Fecha de Generación:** Enero 9, 2026  
**Aplicación:** ChampiLeaks (Maristas Analytics)  
**Estado Actual:** ⚠️ CONEXIÓN A GOOGLE SHEETS COMPROMETIDA  

---

## 1️⃣ ANÁLISIS DEL ERROR ACTUAL

### Síntoma Observado
La aplicación Streamlit ha dejado de comunicarse correctamente con Google Sheets. Los usuarios reportan:
- ❌ Incapacidad de leer datos desde Google Sheets
- ❌ Fallos al guardar nuevas métricas
- ❌ Datos cacheados obsoletos que no se actualizan
- ❌ Errores en la hoja de "cuentas" durante auto-upsert

### Causas Raíz Identificadas

#### **PROBLEMA 1: Configuración de Credenciales Incompleta**

**Ubicación:** [.env](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/.env) y [.streamlit/secrets.toml](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/.streamlit/secrets.toml)

**Diagnóstico:**
```dotenv
# ESTADO ACTUAL (.env):
GOOGLE_SHEETS_ID=                          # ❌ VACÍO - Sin ID del Spreadsheet
GCP_PRIVATE_KEY="...TU_PRIVATE_KEY_AQUI"   # ❌ PLACEHOLDER - No sustituido
GCP_CLIENT_EMAIL=tu-service-account@...    # ❌ PLACEHOLDER - No sustituido
GCP_PROJECT_ID=tu-project-id               # ❌ PLACEHOLDER - No sustituido
GCP_PRIVATE_KEY_ID=tu-private-key-id       # ❌ PLACEHOLDER - No sustituido
```

**Impacto:**
- La función `_get_service_account_config()` en [sheets_connector.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/sheets_connector.py) retorna `None` porque ninguna de las 3 opciones de fallback encuentra credenciales válidas
- `conectar_sheets()` intenta abrir un spreadsheet con ID = `None`
- Toda operación de lectura/escritura falla silenciosamente

**Ruta de Falla:**
```python
# sheets_connector.py líneas 67-93
@st.cache_resource(ttl=1800)
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    # Línea 76: creds_dict = _get_service_account_config()  # ← RETORNA None
    if not creds_dict:
        logger.warning("No se encontraron credenciales de Google Sheets")
        return None  # ← RETORNA None aquí
    
    # Línea 82: spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID") ...
    # ← GOOGLE_SHEETS_ID = "" (vacío), por lo que spreadsheet_id = None
    if not spreadsheet_id:
        logger.error("GOOGLE_SHEETS_ID no configurado")
        return None  # ← RETORNA None aquí
```

#### **PROBLEMA 2: Conflicto de Estrategias de Autenticación**

**Ubicación:** [sheets_connector.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/sheets_connector.py#L33) vs [data_manager.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_manager.py#L121)

**Diagnóstico:**
Existen **2 funciones de conexión simultáneas** con estrategias diferentes:

**`sheets_connector.py` (Líneas 33-93):**
- 3 opciones de fallback (st.secrets → JSON env → vars individuales)
- **Espera ID en:** `GOOGLE_SHEETS_ID` env variable
- **Abre spreadsheet por:** ID (`gc.open_by_key()`)

**`data_manager.py` (Líneas 121-141):**
- Solo 1 opción (st.secrets)
- **Espera ID en:** `google_sheets_name` (nombre, no ID)
- **Abre spreadsheet por:** nombre (`gc.open()`)

**Conflicto:**
- `data_manager.py` busca un spreadsheet de nombre `"BaseDatosMatriz"` por defecto
- `sheets_connector.py` busca un spreadsheet por ID
- Si el nombre no coincide exactamente, falla silenciosamente
- Si el ID no existe, falla silenciosamente
- **Ninguno advierte al usuario cuál es el problema**

#### **PROBLEMA 3: Caché Bloqueado**

**Ubicación:** [data_loader.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_loader.py#L119) línea 119

**Diagnóstico:**
```python
@st.cache_data(ttl=300)  # ← CACHÉ por 5 minutos
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Carga datos cacheados (300 segundos)."""
    return _load_data_impl()
```

**Problema:**
- Si `conectar_sheets()` falla en primer load, el DataFrame cacheado queda vacío
- Durante los próximos 5 minutos, `load_data()` retorna ese DataFrame vacío cacheado
- **Incluso si se arregla la conexión, el usuario debe esperar 5 minutos para ver datos frescos**
- Fallback a CSV local funciona, pero puede estar desactualizado

**Flujo Actual:**
```
Usuario abre app
    ↓
load_data() ejecuta
    ↓
conectar_sheets() retorna None
    ↓
data_loader intenta `spreadsheet.worksheet("cuentas")` → ❌ ERROR
    ↓
Cae a CSV fallback
    ↓
Resultado cacheado por 5 minutos
    ↓
Usuario ve datos obsoletos aunque Sheets se haya reparado
```

#### **PROBLEMA 4: Validación de Estructura de Spreadsheet Ausente**

**Ubicación:** [data_loader.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_loader.py#L67) y [data_saver.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_saver.py#L101)

**Diagnóstico:**
No hay validación de que las hojas requeridas existan:

```python
# data_loader.py línea 74
try:
    ws_c = spreadsheet.worksheet("cuentas")  # ← ¿Existe la hoja?
    c_data = ws_c.get_all_records()
    if c_data:
        cuentas_df = pd.DataFrame(c_data).fillna('')
except:  # ← Captura CUALQUIER error, incluyendo:
         # - Hoja no existe
         # - Permisos insuficientes
         # - Quota excedido
    logger.warning("Hoja 'cuentas' no encontrada.")
```

**Impacto:**
- No se distingue entre "hoja no existe" vs "permiso denegado" vs "quota excedido"
- Usuario recibe un aviso genérico que no ayuda a diagnosticar el problema real
- La app no puede recuperarse automáticamente

#### **PROBLEMA 5: Manejo de IDs como Enteros (Type Corruption)**

**Ubicación:** [data_loader.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_loader.py#L29-L36)

**Diagnóstico:**
El sistema intenta proteger IDs como strings:

```python
def _normalize_id_column(df: pd.DataFrame, col: str = "id_cuenta") -> pd.DataFrame:
    """Asegura que la columna de ID se trata SIEMPRE como string."""
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df
```

**Pero:**
- Google Sheets puede leer `"12345"` como `12345` (número)
- Cuando se convierte a string: `"12345"` ≠ `"abc123"` (ambos son strings, pero valor diferente)
- Si el ID original era un hash MD5 de 8 caracteres (`"4fe0d087"`), pero Sheets lo interpretó como número, se pierde
- El sistema no valida que IDs tengan el formato esperado antes de procesar

---

## 2️⃣ MAPEO DE FLUJO: ¿DÓNDE EXACTAMENTE FALLA?

### Diagrama de Decisión: Lectura vs Escritura

```
┌─ Intento de lectura (load_data)
│  │
│  ├─ ¿Existen credenciales en st.secrets?
│  │  ├─ NO → retorna None
│  │  └─ SÍ → continúa
│  │
│  ├─ ¿GOOGLE_SHEETS_ID está configurado?
│  │  ├─ NO → retorna None
│  │  └─ SÍ → continúa
│  │
│  ├─ ¿Google Sheets API responde?
│  │  ├─ NO → catch exception, fallback a CSV ❌
│  │  └─ SÍ → continúa
│  │
│  ├─ ¿Existen hojas "cuentas", "metricas"?
│  │  ├─ NO → catch exception, fallback a CSV ❌
│  │  └─ SÍ → continúa
│  │
│  └─ ✅ Lectura exitosa + cachear por 5 minutos
│
└─ Intento de escritura (guardar_datos)
   │
   ├─ ¿Existen credenciales?
   │  ├─ NO → return False ❌
   │  └─ SÍ → continúa
   │
   ├─ ¿Google Sheets API responde?
   │  ├─ NO → return False ❌
   │  └─ SÍ → continúa
   │
   ├─ ¿Auto-upsert funciona? (insert en "cuentas")
   │  ├─ NO → warning, continúa ⚠️
   │  └─ SÍ → continúa
   │
   ├─ ¿Append a "metricas" funciona?
   │  ├─ NO → return False ❌
   │  └─ SÍ → continúa
   │
   ├─ ¿Respaldo CSV funciona?
   │  ├─ NO → warning ⚠️
   │  └─ SÍ → continúa
   │
   └─ ✅ Datos guardados (Sheets + CSV)
```

### Punto de Falla Crítico

**Lectura:**
- `conectar_sheets()` retorna `None` → **Falla ANTES de intentar lectura**
- Fallback a CSV funciona (respuesta degradada)

**Escritura:**
- Si `conectar_sheets()` funciona pero append falla → **Intenta respaldo CSV**
- Si ambos fallan → **Usuario pierde datos sin saberlo**

---

## 3️⃣ PLAN DE ACCIÓN: RESTAURAR CONEXIÓN SIN CORROMPER IDs

### Fase 1: Reparación Inmediata (Hoy)

#### 1.1 - Configurar Credenciales Correctamente

**Pasos:**

```bash
# 1. Obtener credenciales reales de Google Cloud Platform
# - Ir a Console.cloud.google.com
# - Servicio Accounts → Seleccionar cuenta de servicio
# - Tab "Keys" → Crear nueva JSON key
# - Descargar JSON

# 2. Extraer valores del JSON descargado:
# - private_key: (incluye saltos de línea \n)
# - client_email: bot-matriz@proyecto.iam.gserviceaccount.com
# - project_id: hybrid-shelter-426922-i8
# - private_key_id: 9c6fc02fffb6dea31445a60a5b65e6457dbf4202

# 3. Configurar .env o secrets.toml con valores REALES
```

**Validación:**
```bash
# Script de verificación (crear test_connectivity.py):
python check_google_sheets.py --verify

# Salida esperada:
# ✅ Credenciales cargadas
# ✅ Spreadsheet encontrado: "BaseDatosMatriz"
# ✅ Hoja "cuentas" existe
# ✅ Hoja "metricas" existe
# ✅ Hoja "config" existe
# ❌ Cualquier otro resultado = problema específico
```

#### 1.2 - Unificar Estrategia de Conexión

**Cambio Propuesto:**

Usar **`sheets_connector.py` como ÚNICA fuente de conexión** (ya tiene las 3 opciones de fallback).

Actualizar `data_manager.py`:
```python
# ANTES (data_manager.py línea 121):
def conectar_sheets():
    # Código duplicado con estrategia diferente

# DESPUÉS:
from utils.sheets_connector import conectar_sheets  # ← Lazy import
# Usar directamente en data_manager
```

**Beneficio:**
- Una sola función, una sola lógica
- Fallback funcionando: st.secrets → env JSON → vars individuales

#### 1.3 - Mejorar Mensajes de Error

**Cambio Propuesto:**

```python
# En sheets_connector.py (línea 67-93)
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            msg = "CREDENCIALES FALTANTES: Revisa .streamlit/secrets.toml o variables de entorno"
            logger.error(msg)
            try:
                st.error(msg)  # ← Mostrar al usuario
            except:
                pass
            return None
        
        # ... resto del código ...
        
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID") or ...
        if not spreadsheet_id:
            msg = "GOOGLE_SHEETS_ID no configurado. Agrégalo a .env o secrets.toml"
            logger.error(msg)
            try:
                st.error(msg)  # ← Mostrar al usuario
            except:
                pass
            return None
        
        # ... resto del código ...
    
    except Exception as e:
        # Diferenciar tipos de error
        msg = f"ERROR DE CONEXIÓN A GOOGLE SHEETS: {type(e).__name__}: {str(e)[:100]}"
        logger.error(msg)
        try:
            st.error(msg)  # ← Mostrar al usuario
        except:
            pass
        return None
```

### Fase 2: Blindaje Preventivo (Próximas 48 horas)

#### 2.1 - Validación de Estructura de Sheets

**Crear función:**
```python
# utils/sheets_validator.py
def validate_sheets_structure(spreadsheet) -> Tuple[bool, List[str]]:
    """
    Valida que el spreadsheet tenga todas las hojas requeridas con columnas correctas.
    
    Returns:
        (is_valid, errors_list)
    """
    required_sheets = {
        "cuentas": ["id_cuenta", "entidad", "plataforma", "usuario_red"],
        "metricas": ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"],
        "config": ["entidad", "meta_seguidores", "meta_engagement"],
        "comentarios": ["entidad", "mes", "comentario"],
        "usernames_editados": ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]
    }
    
    errors = []
    for sheet_name, expected_cols in required_sheets.items():
        try:
            ws = spreadsheet.worksheet(sheet_name)
            actual_cols = ws.get_all_records()[0].keys() if ws.get_all_records() else []
            for col in expected_cols:
                if col not in actual_cols:
                    errors.append(f"Hoja '{sheet_name}': columna '{col}' faltante")
        except Exception as e:
            errors.append(f"Hoja '{sheet_name}': {str(e)}")
    
    return len(errors) == 0, errors
```

**Usar en:**
```python
# Al conectar
spreadsheet = conectar_sheets()
if spreadsheet:
    is_valid, errors = validate_sheets_structure(spreadsheet)
    if not is_valid:
        logger.error(f"Estructura de Sheets inválida: {errors}")
        st.error(f"❌ Problema con Google Sheets:\n" + "\n".join(errors))
        spreadsheet = None  # Tratar como conexión fallida
```

#### 2.2 - Invalidación Inteligente de Caché

**Cambio Propuesto:**

```python
# En data_loader.py (línea 119)
# ANTES:
@st.cache_data(ttl=300)  # 5 minutos de caché fijo
def load_data():
    return _load_data_impl()

# DESPUÉS:
@st.cache_data(ttl=60)  # Reducir a 1 minuto cuando en Streamlit Cloud
def load_data():
    """Carga datos. Cache se invalida automáticamente tras escritura."""
    data = _load_data_impl()
    
    # Invalidar si viene de CSV fallback
    if connected_to_sheets is False:
        st.warning("⚠️ Leyendo desde respaldo local (offline mode)")
    
    return data
```

**Plus: Invalidación Manual**
```python
# En data_saver.py, después de guardar
def guardar_datos(nuevo_df):
    # ... guardar ...
    
    # Invalidar caché de carga
    st.cache_data.clear()  # ← Fuerza refresh en próxima lectura
    
    # Plus: Recargar datos frescos automáticamente
    from utils.data_provider import data_provider
    data_provider.invalidate_cache()
```

#### 2.3 - Protección de IDs (Type Safety)

**Crear validador:**
```python
# utils/id_validator.py
def validate_id_format(id_cuenta: str) -> bool:
    """
    Valida que el ID tenga el formato esperado (8 caracteres hex MD5).
    Previene corrupción de tipos.
    """
    if not isinstance(id_cuenta, str):
        return False
    if len(id_cuenta) != 8:
        return False
    try:
        int(id_cuenta, 16)  # Validar que son hexadecimales
        return True
    except ValueError:
        return False

def sanitize_id_column(df: pd.DataFrame, col: str = "id_cuenta") -> pd.DataFrame:
    """
    Sanitiza columna de IDs:
    1. Convierte a string
    2. Valida formato
    3. Rechaza valores inválidos
    """
    if col not in df.columns:
        return df
    
    df = df.copy()
    invalid_ids = []
    
    for idx, val in df[col].items():
        str_val = str(val).strip()
        if not validate_id_format(str_val):
            invalid_ids.append((idx, str_val))
            df.at[idx, col] = None
    
    if invalid_ids:
        logger.warning(f"IDs inválidos encontrados y reemplazados con None: {invalid_ids}")
    
    df[col] = df[col].astype(str)
    return df
```

---

## 4️⃣ SUGERENCIA DE BLINDAJE: EVITAR FUTUROS ERRORES EN STREAMLIT CLOUD

### 4.1 - Configuración de Secrets en Streamlit Cloud

**Pasos:**

1. **Ir a:** https://share.streamlit.io/settings/secrets
2. **Agregar (TOML format):**
```toml
google_sheets_id = "1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY"

[gcp_service_account]
type = "service_account"
project_id = "hybrid-shelter-426922-i8"
private_key_id = "9c6fc02fffb6dea31445a60a5b65e6457dbf4202"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkq...\n-----END PRIVATE KEY-----\n"
client_email = "matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

3. **Verificar compartición en Google Sheets:**
   - Ir al spreadsheet
   - Click "Compartir"
   - Agregar email del service account con permisos de "Editor"

### 4.2 - CI/CD Health Check

**Crear:** `.github/workflows/check-sheets-connectivity.yml`

```yaml
name: Check Google Sheets Connectivity
on:
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python check_google_sheets.py --verify
        env:
          GOOGLE_SHEETS_ID: ${{ secrets.GOOGLE_SHEETS_ID }}
          GCP_SERVICE_ACCOUNT_JSON: ${{ secrets.GCP_SERVICE_ACCOUNT_JSON }}
```

### 4.3 - Monitoreo de Errores en Producción

**Implementar logging agregado:**

```python
# En app.py
import logging
from datetime import datetime

class ProductionLogger:
    def __init__(self):
        self.errors_log = []
    
    def log_critical(self, module: str, error: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "error": error
        }
        self.errors_log.append(entry)
        
        # Opcional: Enviar a servicio externo (Sentry, etc.)
        # send_to_monitoring_service(entry)

prod_logger = ProductionLogger()

# Usar en catches
try:
    data = load_data()
except Exception as e:
    prod_logger.log_critical("data_loader", str(e))
    st.error("Error cargando datos")
```

### 4.4 - Graceful Degradation Strategy

**Implementar fallbacks en capas:**

```python
def load_data_resilient():
    """
    Intenta cargar datos en orden de preferencia:
    1. Google Sheets (time = 0-2s)
    2. CSV Local (time = 0-1s)
    3. Default Mock Data (time = 0s)
    """
    
    # Nivel 1: Google Sheets
    try:
        sheets = conectar_sheets()
        if sheets:
            data = _load_from_sheets(sheets)
            if not data.empty:
                return data, "sheets"
    except:
        pass
    
    # Nivel 2: CSV Local
    try:
        data = pd.read_csv("data/cuentas.csv")
        if not data.empty:
            logger.warning("Usando CSV local como fallback")
            return data, "csv"
    except:
        pass
    
    # Nivel 3: Mock Data
    logger.error("Usando mock data (modo degradado)")
    return generate_mock_data(), "mock"
```

---

## 5️⃣ CÓDIGO DE REFERENCIA: ARCHIVOS CRÍTICOS

### Estructura de Archivos Analizados

| Archivo | Líneas | Responsabilidad | Estado |
|---------|--------|-----------------|--------|
| [sheets_connector.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/sheets_connector.py) | 100 | Autenticación OAuth + conexión | ⚠️ Necesita mejoras |
| [data_loader.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_loader.py) | 200 | Lectura desde Sheets/CSV | ⚠️ Caché bloqueado |
| [data_saver.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_saver.py) | 479 | Escritura a Sheets/CSV | ⚠️ Fallback requiere validación |
| [data_manager.py](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/utils/data_manager.py) | 285 | Hub central | ❌ Duplica lógica de conexión |
| [.env](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/.env) | 15 | Variables de entorno | ❌ VACÍO |
| [.streamlit/secrets.toml](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/.streamlit/secrets.toml) | ? | Secrets de Streamlit | ❌ REQUIERE CONFIGURACIÓN |

### Errores Registrados

**Archivo:** [.app_errors.log](file:///f:/MATRIZ%20DE%20REDES/social_media_matrix/.app_errors.log)

Últimos errores (Noviembre 26, 2025):
```
2025-11-26 18:30:13 | ERROR    | utils.data_manager | guardar_datos:300 | 
  Exception: Google Sheets API Error

2025-11-26 18:31:22 | ERROR    | utils.data_manager | guardar_datos:331 | 
  Error al actualizar 'cuentas': API Error al actualizar

2025-11-26 18:31:22 | ERROR    | utils.data_manager | guardar_datos:362 | 
  Error append métricas: API Error al actualizar
```

---

## 6️⃣ CHECKLIST DE IMPLEMENTACIÓN

### ✅ Pre-requisitos

- [ ] Acceso a Google Cloud Console
- [ ] Spreadsheet existente o permiso para crear uno
- [ ] Service Account con permisos de "Editor"
- [ ] Archivo JSON de credenciales descargado
- [ ] Terminal/Git configurado para environment local

### ✅ Fase 1: Configuración (30 minutos)

- [ ] Extraer `private_key`, `client_email`, `project_id` de JSON GCP
- [ ] Actualizar `.env` con valores REALES
- [ ] Actualizar `.streamlit/secrets.toml` con valores REALES
- [ ] Compartir Spreadsheet con service account email (permisos de Editor)
- [ ] Ejecutar `python check_google_sheets.py --verify`

### ✅ Fase 2: Correcciones de Código (2-3 horas)

- [ ] Unificar `data_manager.py` para usar `sheets_connector.py`
- [ ] Mejorar mensajes de error en `sheets_connector.py`
- [ ] Crear `sheets_validator.py` para validar estructura
- [ ] Reducir TTL de caché en `data_loader.py` (300 → 60 segundos)
- [ ] Crear `id_validator.py` para proteger IDs

### ✅ Fase 3: Testing (2 horas)

- [ ] Test de conectividad: `python test_sheets.py`
- [ ] Test de lectura: Cargar app y revisar datos
- [ ] Test de escritura: Capturar nuevos datos, verificar en Sheets
- [ ] Test de fallback: Desconectar internet, verificar CSV respaldo
- [ ] Test de caché: Modificar Sheets, esperar 1 minuto, recargar app

### ✅ Fase 4: Despliegue (1 hora)

- [ ] Commit y push a repositorio
- [ ] Configurar Streamlit Cloud secrets
- [ ] Desplegar a `streamlit run app.py`
- [ ] Verificar logs en Streamlit Cloud
- [ ] Comunicar a usuarios que conexión está restaurada

---

## 7️⃣ CONCLUSIONES Y RECOMENDACIONES

### Resumen del Problema
La aplicación ha dejado de comunicarse con Google Sheets debido a **credenciales no configuradas** y **caché bloqueado** que impide actualizaciones. Existe una **duplicación de lógica de conexión** entre `sheets_connector.py` y `data_manager.py` que dificulta el mantenimiento.

### Recomendación Prioritaria
**Restaurar credenciales INMEDIATAMENTE** (máximo 30 minutos). Sin esto, ninguna lectura/escritura funcionará. Seguir Fase 1 del Plan de Acción.

### Recomendación Secundaria
**Implementar blindaje de caché y validación** (2-3 horas). Prevenir que futuros errores de autenticación bloqueen la app durante 5 minutos.

### Recomendación de Largo Plazo
**Centralizar monitoreo y alertas** en Streamlit Cloud. Implementar health checks automáticos que notifiquen cuando Google Sheets deja de responder.

---

**Fin del Reporte**  
*Próximo paso: Ejecutar Fase 1 del Plan de Acción*
