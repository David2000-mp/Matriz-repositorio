# 🚀 CHAMPILYTICS - Guía de Ejecución Local

## ✅ Configuración Completada

Se ha creado un entorno virtual llamado `venv_local` con todas las dependencias instaladas.

## 📋 Formas de Ejecutar la Aplicación

### Opción 1: Script Automático (Recomendado)

**Windows Command Prompt (CMD):**
```bash
run_local.bat
```

**Windows PowerShell:**
```powershell
.\run_local.ps1
```

### Opción 2: Manual

1. **Activar el entorno virtual:**
   ```bash
   # CMD
   venv_local\Scripts\activate.bat
   
   # PowerShell
   .\venv_local\Scripts\Activate.ps1
   ```

2. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

3. **Abrir en el navegador:**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`

## 🔍 Probar Conexión a Google Sheets

Antes de ejecutar la aplicación completa, puedes probar la conexión:

```bash
# Activar entorno virtual primero
venv_local\Scripts\activate

# Ejecutar test
streamlit run test_sheets.py
```

## 📦 Dependencias Instaladas

- ✅ streamlit >= 1.28.0
- ✅ pandas >= 2.0.0
- ✅ plotly >= 5.17.0
- ✅ gspread >= 5.12.0
- ✅ oauth2client >= 4.1.3

## ⚙️ Configuración Importante

Asegúrate de que:
1. El archivo `.streamlit/secrets.toml` existe y tiene las credenciales correctas
2. La cuenta de servicio tiene permisos de Editor en "BaseDatosMatriz"
3. El nombre de la hoja de Google Sheets es exactamente "BaseDatosMatriz"

## 🛑 Detener la Aplicación

Presiona `Ctrl + C` en la terminal para detener el servidor de Streamlit.

## 🐛 Solución de Problemas

### Error de PowerShell: "No se puede ejecutar scripts"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error de conexión a Google Sheets
- Verifica que `.streamlit/secrets.toml` tenga el formato correcto
- Confirma que la cuenta de servicio tenga permisos
- Ejecuta `streamlit run test_sheets.py` para diagnosticar

### Puerto 8501 en uso
```bash
streamlit run app.py --server.port 8502
```

## 📞 Comandos Útiles

```bash
# Ver versión de Streamlit
streamlit --version

# Limpiar caché de Streamlit
streamlit cache clear

# Ejecutar en otro puerto
streamlit run app.py --server.port 8080
```

---
**CHAMPILYTICS v12.0** - Sistema de Analytics Marista
