# 📄 CÓDIGO REFACTORIZADO: sheets_connector.py

## 🔍 Vista General

**Archivo:** `utils/sheets_connector.py`  
**Líneas:** 263  
**Cambio:** Refactorización completa para Cloud-Ready

---

## 📋 Funciones Principales

### 1. `_normalize_private_key(pk: str) -> str`

```python
def _normalize_private_key(pk: str) -> str:
    """
    Normaliza la private_key para manejar tanto \\n literales como saltos de línea reales.
    """
    if not pk:
        return ""
    return pk.replace('\\n', '\n')
```

**Propósito:** Maneja correctamente los saltos de línea en la clave privada.

**Casos:**
- `.env` tiene: `GCP_PRIVATE_KEY=...-----\nMIIEv...` (literal `\n`)
- Google Auth necesita: líneas reales (newline character)
- Esta función convierte automáticamente

---

### 2. `_get_service_account_config() -> Optional[Dict[str, Any]]`

**Jerarquía de búsqueda (en orden):**

```
1. st.secrets["gcp_service_account"]       ← STREAMLIT CLOUD
   └─ Más rápido, seguro, recomendado

2. os.getenv("GCP_SERVICE_ACCOUNT_JSON")   ← JSON COMPLETO
   └─ Alternativa flexible

3. Variables individuales GCP_*             ← DESARROLLO LOCAL
   ├─ GCP_PRIVATE_KEY
   ├─ GCP_CLIENT_EMAIL
   ├─ GCP_PROJECT_ID
   ├─ GCP_PRIVATE_KEY_ID
   └─ (opcionales) GCP_AUTH_URI, etc.
```

**Ventaja:** La app elige automáticamente dónde leer según el ambiente.

---

### 3. `_get_google_sheets_id() -> Optional[str]`

**Búsqueda de ID (en orden):**

```
1. st.secrets["google_sheets_id"]           ← Streamlit Cloud
2. st.secrets["general"]["google_sheets_id"] ← Streamlit Cloud (alternativo)
3. os.getenv("GOOGLE_SHEETS_ID")            ← Variables de entorno locales
```

---

### 4. `conectar_sheets() -> Optional[gspread.Spreadsheet]`

```python
@st.cache_resource(ttl=1800)  # Cache por 30 minutos
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    """
    Establece conexión con Google Sheets.
    Usa lógica jerárquica: primero st.secrets (Cloud), luego .env (local).
    """
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.error("No se encontraron credenciales...")
            return None

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet_id = _get_google_sheets_id()
        
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_ID no configurado")
            return None

        spreadsheet = gc.open_by_key(spreadsheet_id)
        logger.info(f"✓ Conexión exitosa: {spreadsheet.title}")
        return spreadsheet

    except Exception as e:
        logger.error(f"Error conectando: {e}")
        return None
```

**Cache:** Se cacheatea por 30 minutos para evitar llamadas innecesarias a Google.

---

### 5. `validate_sheets_connection() -> Dict[str, Any]` ⭐

**Retorna:**

```python
{
    'success': bool,        # ¿Conexión OK?
    'message': str,         # Mensaje para mostrar
    'error': str | None,    # Detalles del error (si hay)
    'config_source': str    # De dónde se leyó: 'st.secrets', 'env_json', 'env_vars', 'none'
}
```

**Ejemplo de respuesta exitosa:**

```python
{
    'success': True,
    'message': '✓ Conectado a: CHAMPILEAKS',
    'error': None,
    'config_source': 'st.secrets'
}
```

**Ejemplo de respuesta fallida:**

```python
{
    'success': False,
    'message': 'Configura credenciales en Streamlit Cloud (Secrets) o en .env',
    'error': "No se encontraron credenciales configuradas",
    'config_source': 'none'
}
```

---

### 6. `display_connection_status()` ⭐⭐

**Uso en app.py:**

```python
from utils.sheets_connector import display_connection_status

# Al inicio de la app
_ = display_connection_status()
```

**Resultado en UI:**

```
✅ Conectado a: CHAMPILEAKS
   └─ Verde, confiable

O si hay error:

⚠️ Error de conexión: No se encontraron credenciales
├─ Rojo, visible, con opción de expandir
└─ Detalles técnicos (si clickeas "Detalles del error")
```

**Código:**

```python
def display_connection_status():
    """Muestra el estado de la conexión en st.sidebar."""
    with st.sidebar:
        validation = validate_sheets_connection()
        
        if validation['success']:
            st.success(f"🔗 {validation['message']}", icon="✅")
        else:
            st.error(f"⚠️ {validation['message']}", icon="❌")
            with st.expander("Detalles del error"):
                st.code(f"{validation['error']}\n\nFuente: {validation['config_source']}")
        
        return validation['success']
```

---

## 🚀 Flujo de Ejecución

### Inicio de la App

```
┌─ streamlit run app.py
│
├─ app.py carga: display_connection_status()
│
├─ sheets_connector._get_service_account_config()
│  ├─ ¿Hay st.secrets["gcp_service_account"]?
│  │  ├─ Sí → Usa eso (Streamlit Cloud)
│  │  └─ No → Continúa
│  ├─ ¿Hay GCP_SERVICE_ACCOUNT_JSON env?
│  │  ├─ Sí → Usa eso
│  │  └─ No → Continúa
│  └─ ¿Hay variables GCP_* en .env?
│     ├─ Sí → Usa eso (Desarrollo local)
│     └─ No → Retorna None
│
├─ validate_sheets_connection() intenta conectar
│
└─ display_connection_status() muestra:
   ├─ ✅ Verde si funcionó
   └─ ⚠️ Rojo si falló (con detalles)
```

---

## 🔐 Seguridad

### Private Key Handling

```python
# ANTES (inseguro si hay espacios):
private_key = pk

# AHORA (normalizado):
private_key = _normalize_private_key(pk)
# Convierte: "-----BEGIN\nMIIEv..." → validado para Google Auth
```

### Protección en Git

```gitignore
.env                    # No se sube (contiene credenciales)
.streamlit/secrets.toml # No se sube (Streamlit local)
__pycache__/            # No se sube (compilados)
```

### En Streamlit Cloud

- Los Secrets se encriptan en servidores de Streamlit
- No se guardan en Git
- Se cargan automáticamente al iniciar la app
- No aparecen en logs

---

## 📦 Dependencias Requeridas

```txt
gspread>=5.11.0              # API Python para Google Sheets
google-auth>=2.23.0          # Autenticación Google
google-auth-oauthlib>=1.2.0  # OAuth2
google-auth-httplib2>=0.2.0  # HTTP transport
google-api-python-client     # API client (nuevo)
streamlit>=1.28.0            # Framework
python-dotenv>=1.0.0         # Para .env en desarrollo
```

---

## 🧪 Testing Local

### Verificar que funciona en desarrollo

```powershell
# 1. Activa venv
.\.venv\Scripts\Activate.ps1

# 2. Corre la app
streamlit run app.py

# 3. Deberías ver en el sidebar:
# ✅ Conectado a: CHAMPILEAKS
```

### Verificar que funciona en Cloud

```
1. Abre https://[usuario]-[repo].streamlit.app
2. Busca en el sidebar: ✅ Conectado a: CHAMPILEAKS
3. Si ves ✅ verde = éxito ✓
```

---

## 📝 Cambios vs Versión Anterior

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Búsqueda de credenciales** | OR simple | Jerarquía de 3 niveles |
| **Manejo de private_key** | Propenso a errores | Normalización automática |
| **Validación de conexión** | Manual | Función `validate_sheets_connection()` |
| **UI de estado** | Nada | `display_connection_status()` en sidebar |
| **Google Sheets ID** | 1 nivel | 3 niveles de búsqueda |
| **Logging** | Básico | Detallado con sources |
| **Error handling** | Silencioso | Visible en UI |

---

## 💡 Casos de Uso

### Caso 1: Desarrollo Local

```
1. Usuario tiene .env con credenciales
2. App arranca
3. _get_service_account_config() busca:
   - st.secrets (no existe) → No
   - GCP_SERVICE_ACCOUNT_JSON (no existe) → No
   - Variables GCP_* (sí existen) → ✓ Usa esto
4. Conecta y funciona
5. Sidebar muestra: ✅ Conectado
```

### Caso 2: Streamlit Cloud

```
1. Desarrollador pega secrets en el panel de Streamlit Cloud
2. App se despliega y arranca
3. _get_service_account_config() busca:
   - st.secrets["gcp_service_account"] (sí existe) → ✓ Usa esto
4. Conecta y funciona
5. Sidebar muestra: ✅ Conectado
```

### Caso 3: Fallo de Configuración

```
1. Alguien olvidó pegar los secrets en Streamlit Cloud
2. App arranca pero sin credenciales
3. validate_sheets_connection() retorna error
4. Sidebar muestra: ⚠️ No se encontraron credenciales
   └─ Usuario sabe inmediatamente qué hacer
```

---

## 🎯 Próximos Pasos

1. ✅ **Codigo refactorizado** - Ya está en [utils/sheets_connector.py](../../utils/sheets_connector.py)
2. ✅ **Integración en app.py** - Ya importa `display_connection_status()`
3. ✅ **requirements.txt** - Ya actualizado con dependencias
4. ⏭️ **Subir a GitHub** - Próximo paso para ti
5. ⏭️ **Desplegar en Streamlit Cloud** - Después de GitHub

---

## 📚 Referencias

- [Documentación Streamlit Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google Sheets API (gspread)](https://docs.gspread.org/)
- [Google Auth Library](https://google-auth.readthedocs.io/)

---

**Estado:** ✅ Completado  
**Fecha:** 9 de Enero, 2026  
**Versión:** 1.0.0 Cloud-Ready
