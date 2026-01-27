# ✅ CHECKLIST DE IMPLEMENTACIÓN - FASE 1

**Tiempo estimado:** 45 minutos  
**Dificultad:** ⭐⭐ Intermedia  
**Riesgo:** Bajo (no se pierden datos)

---

## ANTES DE COMENZAR

### Requisitos
- [ ] Acceso a Google Cloud Console (admin de proyecto)
- [ ] Acceso a Google Sheets (editor)
- [ ] Acceso a terminal/PowerShell
- [ ] Editor de texto (VSCode, Notepad++, etc.)

### Archivos que necesitarás
- [ ] JSON descargado de Service Account (del paso 1)
- [ ] Archivo `.env` en raíz del proyecto
- [ ] URL de tu Google Sheets

---

## SECCIÓN 1: OBTENER CREDENCIALES (10 minutos)

### Step 1.1 - Acceder a Google Cloud Console
- [ ] Ir a https://console.cloud.google.com
- [ ] Verificar que estés en el proyecto correcto (parte superior)
  - Proyecto: `hybrid-shelter-426922-i8`
  - Si no, click en dropdown y seleccionar

### Step 1.2 - Navegar a Service Accounts
- [ ] Menú izquierdo → **IAM & Admin**
- [ ] Click en **Service Accounts**
- [ ] Buscar la cuenta: `matriz-bot` (o similar)
- [ ] Click en el nombre para abrirla

### Step 1.3 - Crear o Descargar Key JSON
- [ ] Ir a tab **Keys**
- [ ] Botón **Add Key** → **Create new key**
- [ ] Seleccionar formato: **JSON**
- [ ] Click **Create**
- [ ] Archivo se descarga automáticamente (ej: `hybrid-shelter-426922-i8-9c6fc02fffb6.json`)

### Step 1.4 - Extraer información del JSON
Abrir JSON descargado con editor de texto y copiar estos valores:

```
private_key_id = "9c6fc02fffb6dea31445a60a5b65e6457dbf4202"
    ↑ Buscar en: "private_key_id"
    ✏️ Copiar valor completo

private_key = "-----BEGIN PRIVATE KEY-----\nMIIEv...truncado...\n-----END PRIVATE KEY-----\n"
    ↑ Buscar en: "private_key"
    ✏️ Copiar valor COMPLETO incluyendo BEGIN/END y \n

client_email = "matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com"
    ↑ Buscar en: "client_email"
    ✏️ Copiar valor completo

project_id = "hybrid-shelter-426922-i8"
    ↑ Buscar en: "project_id"
    ✏️ Copiar valor completo
```

**✅ Paso 1 completado:** Tienes 4 valores copiados

---

## SECCIÓN 2: CONFIGURAR .ENV (10 minutos)

### Step 2.1 - Abrir archivo .env
- [ ] Navegar a: `f:\MATRIZ DE REDES\social_media_matrix\.env`
- [ ] Abrir con VSCode o editor
  - **⚠️ NO usar Notepad simple, puede agregar BOM**

### Step 2.2 - Reemplazar contenido
Copiar y reemplazar TODO el contenido de `.env` con esto:

```dotenv
# ============================================================================
# GOOGLE SHEETS CREDENTIALS - ACTUALIZAR CON VALORES REALES
# ============================================================================

# ID del Google Sheets (extraer de URL: /spreadsheets/d/[ESTE]/edit)
GOOGLE_SHEETS_ID=1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY

# Credenciales de Service Account (desde JSON descargado)
GCP_PROJECT_ID=hybrid-shelter-426922-i8
GCP_PRIVATE_KEY_ID=9c6fc02fffb6dea31445a60a5b65e6457dbf4202
GCP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEv...COPIAR_VALOR_COMPLETO...\n-----END PRIVATE KEY-----\n"
GCP_CLIENT_EMAIL=matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com
```

**⚠️ CRÍTICO:**
- [ ] Reemplazar valores placeholders con valores REALES
- [ ] NO dejar placeholders como "TU_PRIVATE_KEY_AQUI"
- [ ] Conservar `\n` en private_key (esos son saltos de línea)
- [ ] Conservar comillas dobles alrededor de valores

### Step 2.3 - Guardar archivo
- [ ] Ctrl+S (o File → Save)
- [ ] Verificar que no haya asterisco (*) en la pestaña (indica cambios sin guardar)

**✅ Paso 2 completado:** .env configurado con valores reales

---

## SECCIÓN 3: OBTENER GOOGLE SHEETS ID (5 minutos)

### Step 3.1 - Copiar ID de Google Sheets
- [ ] Abrir tu Google Sheets: https://docs.google.com/spreadsheets/...
- [ ] Copiar el ID de la URL:
  ```
  URL: https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit
  Ejemplo: https://docs.google.com/spreadsheets/d/1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY/edit
  ```
- [ ] ID: `1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY`

### Step 3.2 - Actualizar GOOGLE_SHEETS_ID en .env
- [ ] Volver a archivo `.env`
- [ ] Encontrar línea: `GOOGLE_SHEETS_ID=...`
- [ ] Reemplazar con tu ID real
- [ ] Guardar

**✅ Paso 3 completado:** GOOGLE_SHEETS_ID actualizado

---

## SECCIÓN 4: COMPARTIR GOOGLE SHEETS (5 minutos)

### Step 4.1 - Abrir Google Sheets
- [ ] Ir a tu spreadsheet: https://docs.google.com/spreadsheets/d/[TU_ID]/edit

### Step 4.2 - Click en "Compartir"
- [ ] Botón azul **"Share"** en esquina superior derecha

### Step 4.3 - Agregar Service Account
- [ ] En popup: campo "Add people and groups"
- [ ] Pegar email: `matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com`
  - (O el email que tengas en `GCP_CLIENT_EMAIL`)

### Step 4.4 - Establecer permisos
- [ ] Dropdown de permisos → **Editor** (NO Viewer, NO Commenter)
  - [ ] Desmarcar "Notify people" (no enviar email)
  - [ ] Click **Share**

### Step 4.5 - Verificar
- [ ] Debería mostrar: "✅ Access has been shared"
- [ ] Refrescar página (F5)

**✅ Paso 4 completado:** Service account tiene acceso de Editor

---

## SECCIÓN 5: VERIFICAR EN TERMINAL (10 minutos)

### Step 5.1 - Abrir terminal
**Windows (PowerShell):**
- [ ] Click derecho en carpeta → "Open Terminal" o abrir PowerShell
- [ ] Navegar a carpeta:
  ```powershell
  cd "f:\MATRIZ DE REDES\social_media_matrix"
  ```

**Mac/Linux:**
- [ ] Abrir Terminal
- [ ] Navegar:
  ```bash
  cd ~/social_media_matrix
  ```

### Step 5.2 - Activar virtual environment
**Windows:**
- [ ] Ejecutar:
  ```powershell
  .\venv_stable\Scripts\Activate.ps1
  ```
- [ ] Verificar que terminal muestra `(venv_stable)` al inicio

**Mac/Linux:**
- [ ] Ejecutar:
  ```bash
  source venv/bin/activate
  ```
- [ ] Verificar que terminal muestra `(venv)` al inicio

### Step 5.3 - Ejecutar diagnóstico
- [ ] Ejecutar:
  ```bash
  python diagnostic_sheets.py
  ```

### Step 5.4 - Revisar salida
Esperar a que termine (30-60 segundos). Debería mostrar:

```
================================================================================
🔍 REPORTE DE DIAGNÓSTICO - GOOGLE SHEETS CONNECTIVITY
================================================================================

📊 Estado general: ✅ TODAS LAS PRUEBAS PASARON

[Credenciales]
Estado: ✅ PASÓ
  ✅ Archivo .env existe
  ✅ GOOGLE_SHEETS_ID: 1FXoHqYH3TnesWAvYTWHnZ0...
  ✅ GCP_PRIVATE_KEY: Formato válido

[Conectividad API]
Estado: ✅ PASÓ
  ✅ Autenticación exitosa
  ✅ Spreadsheet abierto: BaseDatosMatriz

[Estructura de Sheets]
Estado: ✅ PASÓ
  ✅ Hoja 'cuentas' existe (17 registros)
  ✅ Hoja 'metricas' existe (324 registros)
  ...
```

**✅ Si ves ✅ en todo:** Continúa al Paso 6

**❌ Si ves ❌ o ⚠️:** Ir a sección TROUBLESHOOTING abajo

**✅ Paso 5 completado:** Diagnóstico pasó todas las pruebas

---

## SECCIÓN 6: VERIFICAR EN LA APP (10 minutos)

### Step 6.1 - Iniciar Streamlit
En la misma terminal:
- [ ] Ejecutar:
  ```bash
  streamlit run app.py
  ```
- [ ] Esperar a que muestre:
  ```
  Local URL: http://localhost:8501
  ```

### Step 6.2 - Abrir en navegador
- [ ] Ir a: http://localhost:8501
- [ ] Esperar a que cargue la página (20-30 segundos)

### Step 6.3 - Verificar inicio sin errores
- [ ] ✅ No hay error rojo de "Credenciales"
- [ ] ✅ Dashboard muestra datos (no vacío)
- [ ] ✅ Sidebar carga normalmente

### Step 6.4 - Test de lectura
- [ ] Click en **"📊 Dashboard Global"**
- [ ] Debería mostrar gráficos y datos
- [ ] Si ves datos → ✅ Lectura funciona

### Step 6.5 - Test de escritura
- [ ] Click en **"📝 Captura Manual"**
- [ ] Llenar formulario de prueba:
  ```
  Institución: [Cualquiera]
  Red Social: [Cualquiera]
  Usuario: @test_username
  Seguidores: 100
  Alcance: 50
  ... (otros campos)
  ```
- [ ] Click **Guardar**
- [ ] Debería mostrar: `✅ Datos guardados exitosamente`

### Step 6.6 - Verificar en Google Sheets
- [ ] Abrir tu Google Sheets en navegador
- [ ] Ir a pestaña "metricas"
- [ ] Última fila debería tener el registro que acabas de guardar
- [ ] Si está ahí → ✅ Escritura funciona

**✅ Paso 6 completado:** App funciona completamente

---

## SECCIÓN TROUBLESHOOTING

### ❌ Problema: "GOOGLE_SHEETS_ID no configurado"

**Causa:** Variable vacía en .env

**Solución:**
1. [ ] Abrir `.env`
2. [ ] Verificar que `GOOGLE_SHEETS_ID=...` NO está vacío
3. [ ] Copiar ID correcto de Google Sheets URL
4. [ ] Guardar y reintentar

---

### ❌ Problema: "No se encontraron credenciales"

**Causa:** `.env` no se está leyendo correctamente

**Solución:**
1. [ ] En terminal, verificar que se lee:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_SHEETS_ID'))"
   ```
2. [ ] Si muestra vacío, verificar que `.env` está en raíz del proyecto
3. [ ] En VSCode: Ver que archivo está en la carpeta correcta
4. [ ] Si aún no funciona, reiniciar terminal/PowerShell

---

### ❌ Problema: "SpreadsheetNotFound"

**Causa:** ID de Google Sheets es incorrecto o no compartido

**Solución:**
1. [ ] Copiar ID correcto de URL
   - URL correcta: `https://docs.google.com/spreadsheets/d/1FXoHqYH3T.../edit`
   - ID: Todo entre `/d/` y `/edit`
2. [ ] Verificar que compartiste el sheet con el service account
   - [ ] Google Sheets → Compartir → Buscar `matriz-bot@...`
   - [ ] Si no está, agregarlo

---

### ❌ Problema: "Permission denied" o "permission_denied"

**Causa:** Service account NO tiene permisos de Editor

**Solución:**
1. [ ] Abrir Google Sheets
2. [ ] Click Compartir
3. [ ] Buscar `matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com`
4. [ ] Si está con permisos de "Viewer", cambiar a "Editor"
5. [ ] Si no está, agregarlo como "Editor"
6. [ ] Esperar 1-2 minutos (Google tarda en sincronizar)
7. [ ] Reintentar diagnóstico

---

### ❌ Problema: "Hoja 'cuentas' no encontrada"

**Causa:** Google Sheets no tiene la estructura correcta

**Solución:**
1. [ ] Abrir Google Sheets
2. [ ] Verificar que tenga estas pestañas:
   - [ ] `cuentas`
   - [ ] `metricas`
   - [ ] `config`
   - [ ] `comentarios`
   - [ ] `usernames_editados`
3. [ ] Si faltan, crearlas manualmente con estos encabezados:
   - **cuentas:** id_cuenta, entidad, plataforma, usuario_red
   - **metricas:** id_cuenta, fecha, seguidores, alcance, interacciones, likes_promedio, engagement_rate
   - **config:** entidad, meta_seguidores, meta_engagement

---

## ✅ VALIDACIÓN FINAL

Si completaste todos los pasos, deberías tener:

- [ ] ✅ Archivo `.env` con valores reales (no placeholders)
- [ ] ✅ `python diagnostic_sheets.py` muestra "✅ PASÓ" en todos
- [ ] ✅ App carga sin errores de autenticación
- [ ] ✅ Dashboard muestra datos
- [ ] ✅ Puedo guardar datos y aparecen en Google Sheets
- [ ] ✅ Archivo `diagnostic_results.json` existe

**Si todo está ✅, entonces FASE 1 está COMPLETA** 🎉

---

## SIGUIENTE PASO

Una vez completada FASE 1:

1. **Documentar cualquier problema** que hayas encontrado
2. **Hacer commit** de los cambios (`.env` va en .gitignore, así que no se guarda)
3. **Comunicar** a usuarios que la conexión está restaurada
4. **Agendar FASE 2** (Blindaje Preventivo) para mañana

---

## NOTAS IMPORTANTES

- ⚠️ **Nunca compartir `.env`** en Git. Está en `.gitignore` por razones de seguridad
- ⚠️ **Streamlit Cloud** requiere configurar secrets separadamente en https://share.streamlit.io/settings/secrets
- 💡 **Si `.env` no funciona**, puede ser porque:
  - Archivo tiene BOM (Byte Order Mark) - Abrir en VSCode y guardar como "UTF-8 without BOM"
  - Variables mal formateadas - Verificar sin espacios alrededor de `=`
  - Rutas incorrectas - Asegurarse que `.env` está en la carpeta raíz del proyecto

---

**¡Completado! ✅**

Tiempo usado: ~45 minutos  
Siguiente: Fase 2 (Mañana)
