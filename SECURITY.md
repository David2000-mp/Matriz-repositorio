# 🔒 GUÍA DE SEGURIDAD - MATRIZ DE REDES SOCIALES

## 📋 Tabla de Contenidos
1. [Gestión de Secretos](#gestión-de-secretos)
2. [Control de Acceso](#control-de-acceso)
3. [Buenas Prácticas](#buenas-prácticas)
4. [Despliegue Seguro](#despliegue-seguro)
5. [Respuesta a Incidentes](#respuesta-a-incidentes)

---

## 🔐 Gestión de Secretos

### Estado Actual: ✅ SEGURO

Tu aplicación **YA ESTÁ CONFIGURADA CORRECTAMENTE** para gestionar secretos de forma segura:

#### ✅ Implementaciones Existentes:

1. **Credenciales en `st.secrets`** (línea 121 de `utils/data_manager.py`):
   ```python
   creds_dict = st.secrets["gcp_service_account"]
   ```
   - ✅ No hay credenciales hardcodeadas en el código
   - ✅ Las credenciales se cargan desde archivo externo
   - ✅ El archivo de secretos NO se versiona en Git

2. **Protección en `.gitignore`**:
   ```gitignore
   # Streamlit
   .streamlit/secrets.toml
   ```
   - ✅ Evita commits accidentales de credenciales
   - ✅ Protege contra exposición en repositorio público

3. **Validación de Credenciales** (línea 114 de `utils/data_manager.py`):
   ```python
   if "gcp_service_account" not in st.secrets:
       st.error("❌ Falta configuración de credenciales...")
       return None
   ```
   - ✅ Verifica existencia antes de usar
   - ✅ Manejo de errores graceful
   - ✅ Mensajes de error informativos (sin exponer secretos)

---

## 📁 Archivos de Configuración

### `.streamlit/secrets.toml` (NO VERSIONAR)
Archivo REAL con credenciales activas. **YA EXISTE** en tu proyecto.

**Ubicación:** `.streamlit/secrets.toml`  
**Estado:** ✅ Protegido por `.gitignore`  
**Permisos recomendados (Linux/Mac):** `chmod 600 .streamlit/secrets.toml`

### `.streamlit/secrets.toml.example` (SÍ VERSIONAR)
Plantilla pública para nuevos desarrolladores. **RECIÉN CREADO**.

**Ubicación:** `.streamlit/secrets.toml.example`  
**Propósito:** Documentar estructura de secretos sin exponer valores reales  
**Uso:**
```bash
# Nuevo miembro del equipo ejecuta:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Luego edita secrets.toml con sus credenciales reales
```

---

## 🔑 Configuración de Credenciales de Google Cloud

### Paso 1: Crear Cuenta de Servicio

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto (o crea uno nuevo)
3. Navega a: **IAM & Admin > Service Accounts**
4. Click en **CREATE SERVICE ACCOUNT**
5. Completa:
   - **Service account name:** `matriz-redes-bot`
   - **Service account ID:** Se genera automáticamente
   - **Description:** "Bot para gestionar datos de redes sociales"
6. Click **CREATE AND CONTINUE**
7. Rol: Selecciona **Editor** (o **Owner** si necesitas acceso completo)
8. Click **DONE**

### Paso 2: Generar Clave JSON

1. En la lista de Service Accounts, encuentra la que acabas de crear
2. Click en los tres puntos (⋮) > **Manage keys**
3. Click **ADD KEY > Create new key**
4. Selecciona **JSON**
5. Click **CREATE**
6. Se descargará un archivo `.json` → **GUÁRDALO EN LUGAR SEGURO**

⚠️ **IMPORTANTE:** Esta clave es como una contraseña. Si la pierdes, genera una nueva. Si la expones, revócala inmediatamente.

### Paso 3: Habilitar APIs Necesarias

1. Ve a [API Library](https://console.cloud.google.com/apis/library)
2. Busca y habilita:
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

### Paso 4: Compartir Google Sheet con el Bot

1. Abre tu Google Sheet: [BaseDatosMatriz](https://docs.google.com/spreadsheets/)
2. Click en **Compartir** (botón azul, esquina superior derecha)
3. Agrega el email de la cuenta de servicio:
   - Email: `client_email` del archivo JSON (ej: `bot-matriz@proyecto.iam.gserviceaccount.com`)
   - Permisos: **Editor**
4. Desactiva "Notify people" (el bot no necesita notificación)
5. Click **Share**

### Paso 5: Copiar Credenciales a `secrets.toml`

1. Abre el archivo JSON descargado
2. Copia cada valor al archivo `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "VALOR_DEL_JSON"           # Copia de "project_id"
private_key_id = "VALOR_DEL_JSON"       # Copia de "private_key_id"
private_key = "VALOR_DEL_JSON"          # Copia de "private_key" (MANTENER \n)
client_email = "VALOR_DEL_JSON"         # Copia de "client_email"
client_id = "VALOR_DEL_JSON"            # Copia de "client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "VALOR_DEL_JSON" # Copia de "client_x509_cert_url"
universe_domain = "googleapis.com"
```

⚠️ **NOTA CRÍTICA sobre `private_key`:**
- El valor debe incluir `\n` para representar saltos de línea
- Debe empezar con `-----BEGIN PRIVATE KEY-----\n`
- Debe terminar con `\n-----END PRIVATE KEY-----\n`
- Ejemplo correcto:
  ```toml
  private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADA...(resto de la clave)...hoQ==\n-----END PRIVATE KEY-----\n"
  ```

### Paso 6: Verificar Conexión

```bash
# Ejecuta la aplicación
streamlit run app.py

# Si ves este mensaje, está funcionando:
# ✅ "Conectado a Google Sheets exitosamente"

# Si ves errores:
# ❌ "Falta configuración de credenciales" → Revisa que secrets.toml exista
# ❌ "Error al conectar con Google Sheets" → Revisa que el formato sea correcto
# ❌ "Permission denied" → Revisa que hayas compartido el Sheet con el bot
```

---

## 🛡️ Control de Acceso

### Principio de Mínimo Privilegio

#### Cuenta de Servicio de Google (Bot)
- ✅ **Tiene acceso a:** Google Sheets específico ("BaseDatosMatriz")
- ✅ **Permisos:** Editor (puede leer y escribir)
- ❌ **NO tiene acceso a:** Otros documentos de tu cuenta personal

#### Aplicación Streamlit
- ✅ **Tiene acceso a:** Archivo local `secrets.toml`
- ✅ **Ejecuta con:** Permisos del usuario que lanza `streamlit run`
- ❌ **NO almacena:** Credenciales en memoria después del uso

### Recomendaciones de Acceso

1. **Producción (Streamlit Cloud):**
   - Configura secretos en: `Settings > Secrets` del dashboard
   - NO subas `secrets.toml` al repositorio
   - Usa variables de entorno para configuraciones no sensibles

2. **Desarrollo Local:**
   - Cada desarrollador tiene su propio `secrets.toml`
   - Usar cuentas de servicio diferentes por entorno (dev/staging/prod)
   - Rotar credenciales cada 90 días

3. **CI/CD:**
   - Usa secretos de GitHub Actions / GitLab CI
   - Ejemplo (GitHub Actions):
     ```yaml
     env:
       GCP_SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT }}
     ```

---

## ✅ Buenas Prácticas de Seguridad

### DO ✅

1. **Rotar Credenciales Regularmente**
   - Cada 90 días para producción
   - Inmediatamente si hay sospecha de exposición

2. **Usar Diferentes Cuentas por Entorno**
   ```
   desarrollo:  bot-matriz-dev@proyecto.iam.gserviceaccount.com
   staging:     bot-matriz-staging@proyecto.iam.gserviceaccount.com
   producción:  bot-matriz-prod@proyecto.iam.gserviceaccount.com
   ```

3. **Auditar Accesos**
   - Revisa logs en Google Cloud Console
   - Monitorea accesos inusuales

4. **Mantener Dependencias Actualizadas**
   ```bash
   # Verificar vulnerabilidades conocidas
   pip install safety
   safety check -r requirements.txt
   ```

5. **Validar Entrada de Usuarios**
   - Ya implementado en tu código (línea 421 de `utils/data_manager.py`)
   - Previene inyección de datos maliciosos

### DON'T ❌

1. ❌ **Nunca Hardcodear Credenciales**
   ```python
   # MAL ❌
   API_KEY = "sk-1234567890abcdef"
   PASSWORD = "mi_password_secreto"
   
   # BIEN ✅
   api_key = st.secrets["api_keys"]["openai"]
   password = st.secrets["database"]["password"]
   ```

2. ❌ **Nunca Logear Secretos**
   ```python
   # MAL ❌
   logging.info(f"Conectando con clave: {private_key}")
   
   # BIEN ✅
   logging.info("Conectando a Google Sheets...")
   ```

3. ❌ **Nunca Exponer Secretos en Mensajes de Error**
   ```python
   # MAL ❌
   st.error(f"Error con clave {api_key}: {error}")
   
   # BIEN ✅
   st.error(f"Error al conectar. Verifica configuración.")
   logging.error(f"Error de conexión: {error}")
   ```

4. ❌ **Nunca Compartir `secrets.toml` por Email/Slack**
   - Usa gestores de contraseñas (1Password, LastPass, Bitwarden)
   - O comparte de forma segura con herramientas cifradas

---

## 🚀 Despliegue Seguro

### Streamlit Cloud (Recomendado)

1. **Conectar Repositorio**
   - Ve a [share.streamlit.io](https://share.streamlit.io/)
   - Conecta tu repositorio de GitHub

2. **Configurar Secretos**
   - En el dashboard de tu app: `Settings > Secrets`
   - Copia el contenido de `.streamlit/secrets.toml` local
   - Pega en el editor de secretos de Streamlit Cloud
   - Click **Save**

3. **Variables de Entorno Públicas** (si necesitas)
   ```python
   # En tu código:
   import os
   DEBUG_MODE = os.getenv("DEBUG_MODE", "false") == "true"
   ```
   
   ```toml
   # En Streamlit Cloud > Settings > Secrets
   # (Estas NO son secretas, solo configuraciones)
   DEBUG_MODE = "false"
   LOG_LEVEL = "INFO"
   ```

### Docker (Auto-hospedaje)

Si despliegas con Docker, usa **secretos de Docker**:

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    secrets:
      - gcp_credentials
    environment:
      - STREAMLIT_SECRETS_PATH=/run/secrets/gcp_credentials

secrets:
  gcp_credentials:
    file: ./.streamlit/secrets.toml
```

---

## 🚨 Respuesta a Incidentes

### Si Se Expone una Credencial

#### Acción Inmediata (en 5 minutos):

1. **Revocar la Clave Comprometida**
   ```bash
   # Ve a Google Cloud Console
   # IAM & Admin > Service Accounts
   # Selecciona tu cuenta > KEYS tab
   # Click en los tres puntos (⋮) > DELETE de la clave expuesta
   ```

2. **Generar Nueva Clave**
   - Sigue los pasos de "Paso 2: Generar Clave JSON" arriba
   - Actualiza `secrets.toml` con la nueva clave

3. **Verificar Accesos Anómalos**
   ```bash
   # Ve a Google Cloud Console
   # Logging > Logs Explorer
   # Filtra por: resource.type="service_account"
   # Busca actividad sospechosa en las últimas 24 horas
   ```

4. **Notificar al Equipo**
   - Informa a todos los desarrolladores
   - Documenta el incidente
   - Actualiza procedimientos si es necesario

#### Acción a Medio Plazo (en 24 horas):

5. **Auditoría Completa**
   - Revisa todos los commits recientes en Git
   - Verifica que `.gitignore` esté correctamente configurado
   - Escanea el historial de Git por secretos expuestos:
     ```bash
     # Instalar herramienta de escaneo
     pip install detect-secrets
     
     # Escanear repositorio
     detect-secrets scan > .secrets.baseline
     ```

6. **Actualizar Documentación**
   - Actualiza este documento si encontraste nuevas vulnerabilidades
   - Mejora el proceso de onboarding para nuevos desarrolladores

---

## 📊 Checklist de Seguridad

Antes de cada despliegue, verifica:

- [ ] `.streamlit/secrets.toml` está en `.gitignore`
- [ ] No hay credenciales hardcodeadas en el código
- [ ] Todos los secretos se cargan desde `st.secrets`
- [ ] Las credenciales de producción son diferentes a las de desarrollo
- [ ] Las dependencias están actualizadas (`pip list --outdated`)
- [ ] Se ejecutaron los tests (`pytest tests/`)
- [ ] El código fue revisado por al menos 1 persona
- [ ] Los logs no exponen información sensible
- [ ] La cuenta de servicio tiene permisos mínimos necesarios
- [ ] Se documentaron los cambios en seguridad

---

## 🔗 Referencias y Recursos

- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Google Cloud Platform Benchmark](https://www.cisecurity.org/benchmark/google_cloud_computing_platform)

---

## 📝 Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2024-11-26 | 1.0.0 | Documento inicial - Auditoría de seguridad completa |

---

**Mantenido por:** Equipo de DevOps  
**Última revisión:** 26 de noviembre de 2024  
**Próxima revisión:** 26 de febrero de 2025 (cada 3 meses)
