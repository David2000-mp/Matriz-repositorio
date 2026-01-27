# 📝 ARCHIVOS MODIFICADOS - Cambios Exactos

## Archivo 1: utils/sheets_connector.py

### Cambio: Líneas 32-68

**ANTES:**
```python
def _get_service_account_config() -> Optional[dict]:
    """Obtiene credenciales desde st.secrets o variables de entorno."""

    # 1) st.secrets
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    # 2) JSON completo en env
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            return json.loads(sa_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    # 3) Vars individuales
    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")

    if all([pk, client_email, project_id, pk_id]):
        return {
            "type": "service_account",
            "private_key": pk.replace('\\n', '\n') if pk else "",
            "client_email": client_email,
            "project_id": project_id,
            "private_key_id": pk_id,
        }

    return None
```

**DESPUÉS:**
```python
def _get_service_account_config() -> Optional[dict]:
    """Obtiene credenciales desde st.secrets o variables de entorno."""

    # 1) st.secrets
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    # 2) JSON completo en env
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            return json.loads(sa_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    # 3) Vars individuales (con campos OAuth2 completos)
    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")
    auth_uri = os.getenv("GCP_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    token_uri = os.getenv("GCP_TOKEN_URI", "https://oauth2.googleapis.com/token")
    auth_provider_cert = os.getenv("GCP_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")

    if all([pk, client_email, project_id, pk_id]):
        return {
            "type": "service_account",
            "private_key": pk.replace('\\n', '\n') if pk else "",
            "client_email": client_email,
            "project_id": project_id,
            "private_key_id": pk_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_cert,
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
            "client_id": "",
            "universe_domain": "googleapis.com"
        }

    return None
```

### Cambios Agregados:
- ✅ `auth_uri` con default de Google
- ✅ `token_uri` con default de Google
- ✅ `auth_provider_cert` con default de Google
- ✅ `client_x509_cert_url` dinámico basado en client_email
- ✅ `client_id` vacío (no requerido para service account)
- ✅ `universe_domain` para compatibilidad futura

---

## Archivo 2: utils/data_loader.py

### Cambio: Línea 127

**ANTES:**
```python
@st.cache_data(ttl=300)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos cacheados (300 segundos).
    Retorna (cuentas_df, metricas_df) con IDs como strings.
    """
    return _load_data_impl()
```

**DESPUÉS:**
```python
@st.cache_data(ttl=60)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos cacheados (60 segundos).
    Retorna (cuentas_df, metricas_df) con IDs como strings.
    TTL reducido a 60s para reflejar cambios rápidamente sin sobrecargar Sheets.
    """
    return _load_data_impl()
```

### Cambios:
- ✅ `ttl=300` → `ttl=60` (5 minutos → 1 minuto)
- ✅ Docstring actualizado para explicar la razón

---

## Archivo 3: utils/data_manager.py

### Cambio: Línea 121-127

**ANTES (27 líneas):**
```python
def conectar_sheets():
    """
    Función única de conexión a Google Sheets.
    Usa st.secrets['gcp_service_account'] como fuente de credenciales.
    
    Returns:
        gspread.Spreadsheet: Objeto de la hoja de cálculo, o None si falla
    """
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("No se encontraron los secrets 'gcp_service_account'")
            return None
        
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        gc = gspread.authorize(creds)
        name = st.secrets.get("google_sheets_name", "BaseDatosMatriz")
        return gc.open(name)
    except Exception as e:
        st.error(f"Error de conexión a Google Sheets: {e}")
        return None
```

**DESPUÉS (5 líneas):**
```python
def conectar_sheets():
    """
    Función de conexión a Google Sheets (wrapper).
    Delegada a sheets_connector.py para evitar duplicación.
    
    Returns:
        gspread.Spreadsheet: Objeto de la hoja de cálculo, o None si falla
    """
    from utils.sheets_connector import get_sheets_connection
    return get_sheets_connection()
```

### Cambios:
- ✅ Eliminadas 22 líneas de código duplicado
- ✅ Delegación centralizada a `sheets_connector.get_sheets_connection()`
- ✅ Una única fuente de verdad para autenticación
- ✅ Lazy import para evitar circularidad

---

## Archivo 4: .env

### Cambios Agregados:

**NUEVO:**
```bash
GCP_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GCP_TOKEN_URI=https://oauth2.googleapis.com/token
GCP_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
```

### Notas Importantes:
- ✅ Estos valores ya están en .env (agregados ayer)
- ✅ Son defaults de Google OAuth2
- ✅ Pueden ser sobrescritos si necesitas endpoints custom

---

## Resumen de Cambios

| Archivo | Línea(s) | Tipo | Impacto |
|---------|----------|------|---------|
| sheets_connector.py | 32-68 | Agregado | Campos OAuth2 requeridos por Google |
| data_loader.py | 127 | Modificado | TTL más agresivo (1 min vs 5 min) |
| data_manager.py | 121-127 | Refactor | Eliminación de duplicación |
| .env | nuevas | Agregado | URLs de OAuth (opcionales, con defaults) |

## Validación

Todos estos cambios ya están implementados. Para verificar:

```bash
python test_connection_final.py
```

Resultado esperado: **✅ CONEXIÓN ESTABLECIDA - Todo funciona correctamente**

---

**Estado:** 🟢 COMPLETADO
**Fecha:** Hoy
**Próxima fase:** Opcional - Integración de validadores (Fase 3)
