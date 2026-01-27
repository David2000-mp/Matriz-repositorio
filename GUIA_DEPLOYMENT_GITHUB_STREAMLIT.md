# 🚀 Guía Completa: Despliegue GitHub + Streamlit Cloud

**Aplicación:** ChampiLeaks / Maristas Analytics  
**Fecha:** 9 de Enero de 2026  
**Ambiente:** Desarrollo Local → Streamlit Cloud

---

## 📋 Tabla de Contenidos

1. [Refactorización Realizada](#-refactorización-realizada)
2. [Preparación para Git](#-preparación-para-git)
3. [Comandos de Git](#-comandos-de-git)
4. [Configuración en Streamlit Cloud](#-configuración-en-streamlit-cloud)
5. [Validación Post-Despliegue](#-validación-post-despliegue)

---

## 🔧 Refactorización Realizada

### sheets_connector.py - Cambios Cloud-Ready

Se implementó una **lógica jerárquica de configuración** que permite que tu app funcione tanto en desarrollo local como en Streamlit Cloud:

#### 1. **Obtención de Credenciales (Orden de Prioridad)**

```
1. st.secrets (Streamlit Cloud) ← PRIORIDAD ALTA
   └─ st.secrets["gcp_service_account"]
   
2. Env var: GCP_SERVICE_ACCOUNT_JSON (JSON completo)
   
3. Variables individuales de .env (Desarrollo local) ← PRIORIDAD BAJA
   └─ GCP_PRIVATE_KEY
   └─ GCP_CLIENT_EMAIL
   └─ GCP_PROJECT_ID
   └─ GCP_PRIVATE_KEY_ID
   └─ GCP_AUTH_URI
   └─ GCP_TOKEN_URI
   └─ GCP_AUTH_PROVIDER_CERT_URL
```

#### 2. **Manejo Correcto de Private Key**

```python
# La función _normalize_private_key() maneja ambos casos:
'GCP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQ...'  # \n literal (desde .env)
└─ Se convierte a → real newline character para validación de Google
```

#### 3. **Validación de Conexión**

Nuevas funciones agregadas:

```python
# Valida la conexión y retorna estado detallado
validate_sheets_connection() → Dict[str, Any]
    - success: bool
    - message: str
    - error: str | None
    - config_source: 'st.secrets' | 'env_json' | 'env_vars' | 'none'

# Muestra el estado en sidebar (✓ o ⚠️)
display_connection_status()
```

---

## 📂 Preparación para Git

### ✅ Archivos a Subir

```
✓ app.py
✓ requirements.txt
✓ utils/sheets_connector.py (refactorizado)
✓ .gitignore (actualizado)
✓ pyproject.toml
✓ Toda tu lógica de app (vistas, componentes, etc.)
✓ Documentación (README.md, etc.)
```

### ❌ Archivos a NUNCA Subir (ya están en .gitignore)

```
✗ .env (contiene credenciales privadas)
✗ .streamlit/secrets.toml
✗ __pycache__/
✗ venv/ (entorno virtual)
✗ .venv/
✗ *.pyc
✗ .DS_Store / Thumbs.db
```

### 📝 Verificar .gitignore

Asegúrate de que tu `.gitignore` contenga:

```gitignore
# Environment Variables (IMPORTANTE - CREDENCIALES)
.env
.env.local
.env.*.local
secrets.toml

# Streamlit
.streamlit/secrets.toml
.streamlit/

# Virtual Environment
venv/
ENV/
venv_*
.venv
```

---

## 🔗 Comandos de Git

### Paso 1: Inicializar Repositorio (si no existe)

```powershell
cd "f:\MATRIZ DE REDES\social_media_matrix"

# Inicializar git
git init

# Configurar usuario (si es primera vez)
git config user.name "Tu Nombre"
git config user.email "tu.email@example.com"

# Agregar repositorio remoto (reemplaza USER/REPO)
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
```

### Paso 2: Agregar Archivos y Confirmar

```powershell
# Ver qué archivos van a subirse (verifica que NO incluya .env)
git status

# Agregar todos los archivos (excepto los en .gitignore)
git add .

# Crear commit
git commit -m "🚀 Versión Cloud-Ready: Sheets connector jerárquico + Streamlit Cloud compatible"

# Ver commits
git log --oneline -5
```

### Paso 3: Subir a GitHub

```powershell
# Si es primera vez (main branch)
git push -u origin main

# Subsecuentes
git push origin main

# Verificar
git log --oneline origin/main -5
```

### Paso 4: Crear Primera Release (Opcional)

```powershell
# Tag para marcar versión
git tag -a v1.0.0 -m "Versión 1.0.0 - Cloud Ready"

# Subir tags
git push origin --tags
```

---

## ☁️ Configuración en Streamlit Cloud

### Paso 1: Conectar GitHub a Streamlit Cloud

1. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
2. **Sign in** con GitHub
3. Haz clic en **"New app"**
4. Selecciona:
   - **Repository:** tu-usuario/tu-repositorio
   - **Branch:** main
   - **Main file path:** app.py

### Paso 2: Agregar Secrets

Una vez desplegada la app:

1. Ve al **⚙️ Settings** de tu app en Streamlit Cloud
2. Abre la sección **"Secrets"**
3. **Opción A: Cargar credenciales JSON completo**

```toml
[gcp_service_account]
type = "service_account"
project_id = "matriz-app-479304"
private_key_id = "e463230e6e16ec4fa86e3c21d178024a8a534102"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCdO7M/F22vY2+n\n2lw2I4qNpl6pKRfWa3tDwEgU6EmfZQP1aMvDGyurK5lwup2SvFLPLUyQzEMnMOfC\nc07jdyr7X993/l1aiJw+cLoQe00PEWQsQBiVSB/QxIBPoj26fi6lqcsk9+/zR7/v\noCaehyIaxQ+c2iHx7B0LjHTuhpOzVw5IaTvSg1+KEO0+wm9MFK9sWjV4LUiOd6qb\nWdkDJuSYeWQC4GJj3yEWW3DhW78xlXhEsCkQDEq50ao7JYwTSUFo3UyMgR9FVx8k\nYjy4rfpMQoPiudqTo1bMWiuh8vV/lExAVpfd062t6GIWDsdMGqelrk8Yim05J/4C\nfrIFwQ5lAgMBAAECggEAGJqZNa/1mLqjY/16LPmaSoikau2UfpfSkdtCnEzuClx9\nBle3/OehSXd42whEtIu2HJfO0aC5CGaxeX7gMx14cx4BQs5hrtNOOcIbh4031XoH\n9hmwjxmaaul4151AchChPYiokngeyu+pE/b4XBmyx0QbaZTDt47WS7KWsKWL8sXX\ndZYSkSc4Si+1/xWOYFF5uiTAmLf2eFQx0VoCa16t6fubbKMtHAaAd6cyo0Ixd6vJ\nG5wp7ml4fmXA91zODmwjYiuifDvATaAZvx3/JSJAO0iLxyVH9E/UH8vRuLBwAOCM\n7z/pvDF+sziJ5rMPAquoz0cE1cA/rsYFk7FSvTt28QKBgQDWxieH6/PYbuXkxX2I\nvgoaeuxJrDP9z64HIiRtfsl8Z9+epUe+uIVPKX6OHvdnJyH60dzTOS9URHQWJIkX\nrKM9YuP1lXjK/r7KQ4HOUmQgX1irZcJXqtsDz8wfcJXSe4S7M5VKwuyUeVg3G4GO\nZ2FsQjiADTq9oFJEDzBoZ4AIcQKBgQC7ageJGKKZzKQquLksFFa60jny39yHtBSq\nuvJDYtZbdgP4q6vUX34HXeWIzPfLLdLI7rcp6lL4eKRYYW4xwc0362m/6XcwLSXZ\nWC4wrPxdIRKVXVTLgU+P1ig/sOBOLMrkb9ezECaGgYLnQT9TpdtQHyjyB3I5QQKz\nXHIK0qO/NQKBgQCOXZeCn8Npqkk1ljuaUu57kxPh2gY0rl+bVuRyuGJy1qACl2ix\nYbrsOIMtThWNCQGbM1V/ph5ba2zP6LP/P26NmGmnNsd1N9vcU1dOHotEci9infdv\nCVBYfHvAM278sOfQ92Z0wjT0TmNNVCxS6vBHRLYTG7HeVNFzT+Y0rrbN4QKBgF7j\nulkBriIs6NnwmWDmE1uX4VtFWQUkempPKSZRPrMkN7KKSP/IMalNM1BmZvfqhZTS\nuM5yI/xGKP/OpNpwg5VSjkJq1LwBv+4hpZFjpIsKmbwiezJmkIAFMG+/AHLUXw32\nSsIQ5VCo9jxcXtHdYgNZI4QXnQ+8CMADiIJOUDYZAoGAJ2Kle0M2PiNpxqE1lay4\nJTMF0ExHRFZDXRKNJpt0wBJUZz2lMouCKl1KcqsfFQoz2blvTNFjd+a4ch+/B1IA\nDi3z+OyD513cNb0iSjNgHlma6NwrpM4A/tdka2TyaVz0kjGKtFO1KDNhudah9cQr\nQ1FCPVEIltbQWRTwT2z9oPw=\n-----END PRIVATE KEY-----"
client_email = "botmatrizv2@matriz-app-479304.iam.gserviceaccount.com"
client_id = "117519836387820156889"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/botmatrizv2%40matriz-app-479304.iam.gserviceaccount.com"
universe_domain = "googleapis.com"

[general]
google_sheets_id = "1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY"
```

**⚠️ IMPORTANTE:** 
- El `private_key` DEBE tener saltos de línea reales (`\n`), no literales
- Copia exactamente desde tu .env, pero los saltos de línea ya están procesados
- Verifica que `google_sheets_id` coincida con tu spreadsheet

### Paso 3: Reiniciar App

Después de agregar los Secrets:
1. Haz clic en **"Rerun"** (o la app se reinicia automáticamente)
2. Deberías ver en el sidebar izquierdo: **✅ Conectado a: [Tu Spreadsheet]**

---

## ✅ Validación Post-Despliegue

### En Tu Máquina Local

```powershell
# Activar entorno virtual
cd "f:\MATRIZ DE REDES\social_media_matrix"
.\.venv\Scripts\Activate.ps1

# Correr app localmente
streamlit run app.py

# Deberías ver en el sidebar:
# ✅ Conectado a: CHAMPILEAKS (o tu nombre de sheet)
```

### En Streamlit Cloud

1. Abre tu URL: `https://[tu-usuario]-[repo-name].streamlit.app`
2. Busca en el **sidebar izquierdo** el estado de conexión
3. **Esperado:** Un cuadro verde con ✅ y el nombre de tu spreadsheet

### Qué Hacer Si Aparece ⚠️ Error

Si ves `⚠️ Error de conexión`:

1. **Verifica los Secrets:** Ve a Settings → Secrets
   - ¿Está `gcp_service_account` correctamente formateado?
   - ¿Tiene `google_sheets_id`?

2. **Prueba la private_key:** En el terminal local:
   ```powershell
   $pk = $env:GCP_PRIVATE_KEY
   # Debería imprimir múltiples líneas
   Write-Output $pk
   ```

3. **Revisa los logs:** En Streamlit Cloud → App settings → View logs
   ```
   Busca líneas que digan "Credenciales encontradas en..."
   ```

4. **Recarga con caché limpio:**
   ```powershell
   # Borra cache de Streamlit
   Remove-Item -Path ~/.streamlit/cache -Force -Recurse
   streamlit run app.py
   ```

---

## 📦 Contenido del requirements.txt

Tu `requirements.txt` incluye:

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
kaleido>=0.2.1
gspread>=5.11.0
google-auth>=2.23.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.80.0
fpdf>=1.7.2
reportlab>=4.0.0
python-dotenv>=1.0.0
requests>=2.31.0
urllib3>=2.0.0
certifi>=2023.7.22
```

**Nota:** `python-dotenv` es opcional en Cloud (no se ejecuta), pero se mantiene por compatibilidad local.

---

## 🔐 Protección de Datos

### En .gitignore

Verificado que está:
- ✅ `.env` (credenciales locales)
- ✅ `.streamlit/secrets.toml` (si existe)
- ✅ `venv/` y `.venv/` (entornos virtuales)
- ✅ `__pycache__/` y `*.pyc` (archivos compilados)

### Antes de Hacer Push

```powershell
# Verificar que NO hay archivos sensibles en staging
git status

# Si accidentalmente agregaste .env:
git reset HEAD .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "✓ Fix: .env added to gitignore"
```

---

## 🎯 Resumen de Cambios Realizados

| Archivo | Cambio |
|---------|--------|
| `utils/sheets_connector.py` | ✅ Lógica jerárquica de credenciales + funciones de validación |
| `app.py` | ✅ Llamada a `display_connection_status()` en el inicio |
| `requirements.txt` | ✅ Actualizado con Google Cloud dependencies |
| `.gitignore` | ✅ Protección mejorada de credenciales |

---

## 📞 Troubleshooting Rápido

| Síntoma | Causa | Solución |
|---------|-------|----------|
| `❌ No se encontraron credenciales` | Secrets no configurados | Ve a Settings → Secrets en Streamlit Cloud |
| `❌ GOOGLE_SHEETS_ID no configurado` | Falta el ID | Agrega `google_sheets_id` a Secrets |
| `⚠️ JSON invalido` | Formato de `private_key` | Verifica saltos de línea en Secrets |
| App funciona local, falla en Cloud | Variables de .env no se cargan | Streamlit Cloud necesita Secrets, no .env |
| `ModuleNotFoundError: gspread` | Falta instalar dependencias | Verifica que `requirements.txt` esté en root |

---

## ✨ Próximos Pasos

1. ✅ Push a GitHub
2. ✅ Conectar en Streamlit Cloud
3. ✅ Agregar Secrets
4. ✅ Validar conexión (ver ✅ en sidebar)
5. 🎉 Compartir URL con tu equipo

**URL de tu app:** `https://[tu-usuario]-[repo-name].streamlit.app`

---

**Fecha de actualización:** 9 de Enero, 2026  
**Estado:** ✅ Listo para Streamlit Cloud
