# 📋 Cheat Sheet: Despliegue Rápido

## 1️⃣ Preparación Final (5 min)

```powershell
cd "f:\MATRIZ DE REDES\social_media_matrix"

# Verificar que .env NO se va a subir
git status | Select-String ".env"  # NO debe aparecer

# Verificar requirements.txt está actualizado
Get-Content requirements.txt | Select-String "gspread|google-auth"

# Limpiar archivos temporales
Remove-Item -Path ".streamlit\cache" -Force -Recurse -ErrorAction SilentlyContinue
```

## 2️⃣ Subir a GitHub (10 min)

```powershell
# 1. Agregar archivos
git add .

# 2. Ver qué se va a subir (VERIFICA que NO sea .env)
git status

# 3. Si accidentalmente agregaste .env, sácalo:
# git reset HEAD .env

# 4. Confirmar
git commit -m "🚀 Cloud Ready: Sheets connector jerárquico + Streamlit Cloud"

# 5. Subir
git push origin main

# 6. Verificar en https://github.com/tu-usuario/tu-repo
```

## 3️⃣ Streamlit Cloud (15 min)

### A. Conectar y Crear App

```
1. Ve a https://streamlit.io/cloud
2. Click: "New app"
3. Selecciona:
   - Repository: tu-usuario/social_media_matrix
   - Branch: main
   - Main file: app.py
4. Espera a que se despliegue...
```

### B. Agregar Secrets

```
Settings (⚙️) → Secrets
```

**Copia y pega esto, reemplazando con TUS valores:**

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
- Los saltos de línea en `private_key` ya están como `\n` (no necesitas reemplazar nada)
- El ID debe ser exactamente: `1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY`

### C. Guardar y Rerun

```
1. Click "Save"
2. La app se reinicia automáticamente
3. Espera a que termine...
```

## 4️⃣ Validación (2 min)

### En Local

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py

# Abre en navegador: http://localhost:8501
# Busca en el sidebar izquierdo:
# ✅ Conectado a: CHAMPILEAKS
```

### En Cloud

```
1. Abre tu URL: https://[usuario]-[repo].streamlit.app
2. Busca en el sidebar:
   - Verde + ✅ = Funcionando ✓
   - Rojo + ⚠️ = Revisar Secrets
```

## 🆘 Problemas Comunes

### ❌ "No se encontraron credenciales"
**Solución:** 
- Ve a Settings → Secrets
- Verifica que `[gcp_service_account]` esté ahí
- Haz click en "Save" aunque no cambies nada

### ❌ "GOOGLE_SHEETS_ID no configurado"
**Solución:**
- En Secrets, agrega bajo `[general]`:
  ```toml
  [general]
  google_sheets_id = "1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY"
  ```

### ❌ Error de validación de private_key
**Solución:**
- Copia la `private_key` EXACTA de tu .env
- Los `\n` ya están correctos (no necesitas procesarlos)

### ✅ Funciona en local, pero no en Cloud
**Solución:**
- El problema es 99% de veces los Secrets
- Ve a Logs (Settings → View logs) y busca "Credenciales encontradas en..."
- Si dice "none", los Secrets no se cargaron

---

## 📊 Flujo Jerárquico de Credenciales

```
STREAMLIT CLOUD:
  └─ st.secrets["gcp_service_account"] ← INTENTA PRIMERO
  └─ Si no, busca env var GCP_SERVICE_ACCOUNT_JSON
  └─ Si no, busca variables individuales

DESARROLLO LOCAL:
  └─ .env (GCP_PRIVATE_KEY, etc.)
```

---

## 🎁 Bonus: Comando Git para Verificar

```powershell
# Ver que .env NO está en tracking
git status

# Ver qué se va a subir
git ls-files --others --exclude-standard

# Historial de commits
git log --oneline -5
```

---

**¡Listo! Tu app está en Streamlit Cloud 🎉**
