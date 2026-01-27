# 🚀 PLAN DE CUTOVER - GUÍA COMPLETA

## 📋 RESUMEN EJECUTIVO

Esta guía te llevará paso a paso por la transición final de tu aplicación CHAMPILYTICS desde la arquitectura monolítica hacia la arquitectura modular refactorizada.

**Tiempo estimado**: 5-10 minutos  
**Riesgo**: Bajo (hay backups en cada paso)  
**Reversible**: Sí (hasta el push final)

---

## ✅ PRE-REQUISITOS

Antes de comenzar, verifica:

- [ ] La app refactorizada (`app_refactored.py`) funciona correctamente
- [ ] Tienes todas tus credenciales guardadas (`.streamlit/secrets.toml`)
- [ ] Estás en la rama correcta (`main`)
- [ ] No tienes cambios sin guardar importantes
- [ ] Tienes conexión a Internet para push a GitHub

---

## 🔧 FASE 1: EJECUCIÓN DEL SCRIPT DE CUTOVER

### Opción A: Ejecutar Script Automatizado (RECOMENDADO)

```powershell
# Navegar al directorio del proyecto
cd "F:\MATRIZ DE REDES\social_media_matrix"

# Ejecutar script de cutover
.\cutover.ps1
```

**Qué hace este script:**
1. ✅ Crea carpeta `legacy/` y guarda backup de `app.py` antiguo
2. ✅ Renombra `app_refactored.py` → `app.py`
3. ✅ Limpia cache (`__pycache__`, `*.pyc`)
4. ✅ Actualiza `.gitignore`
5. ✅ Prepara staging de Git
6. ✅ Verifica estructura de archivos

### Opción B: Ejecución Manual (Paso a Paso)

Si prefieres control total, ejecuta estos comandos uno por uno:

```powershell
# 1. Crear carpeta legacy
New-Item -Path "legacy" -ItemType Directory -Force

# 2. Backup del código antiguo
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "app.py" "legacy/app_monolithic_$timestamp.py"

# 3. Eliminar app.py antiguo
Remove-Item "app.py" -Force

# 4. Renombrar nuevo como oficial
Rename-Item "app_refactored.py" "app.py"

# 5. Limpiar cache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -File -Filter "*.pyc" | Remove-Item -Force
```

---

## 🧪 FASE 2: VERIFICACIÓN POST-CUTOVER

### 2.1 Probar la Aplicación

```powershell
# Activar entorno virtual
.\venv_local\Scripts\Activate.ps1

# Ejecutar app con nuevo nombre
streamlit run app.py
```

**Checklist de Verificación:**
- [ ] La app carga sin errores
- [ ] Landing page se muestra correctamente
- [ ] Dashboard muestra datos y gráficos
- [ ] Navegación entre páginas funciona
- [ ] Captura manual guarda datos
- [ ] No hay errores en la consola

**Si algo falla:**
```powershell
# Restaurar desde backup
Copy-Item "legacy/app_monolithic_*.py" "app.py" -Force
# Investigar el error antes de continuar
```

### 2.2 Verificar Estructura de Archivos

```powershell
# Ver estructura actual
tree /F /A
```

**Estructura esperada:**
```
social_media_matrix/
├── app.py ← NUEVO (ex app_refactored.py)
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
├── utils/
│   ├── __init__.py
│   ├── data_manager.py
│   └── helpers.py
├── components/
│   ├── __init__.py
│   └── styles.py
├── views/
│   ├── __init__.py
│   ├── landing.py
│   ├── dashboard.py
│   ├── analytics.py
│   ├── data_entry.py
│   └── settings.py
├── legacy/ ← NUEVO
│   └── app_monolithic_YYYYMMDD_HHMMSS.py
└── [Documentación .md]
```

---

## 📦 FASE 3: ACTUALIZAR DEPENDENCIAS

### 3.1 Generar requirements.txt Actualizado

```powershell
# Opción 1: Si tienes pip-tools instalado
pip-compile requirements.in -o requirements.txt

# Opción 2: Generar desde entorno actual (RECOMENDADO)
pip freeze > requirements_new.txt

# Revisar diferencias
Compare-Object (Get-Content requirements.txt) (Get-Content requirements_new.txt)

# Si está todo OK, reemplazar
Move-Item requirements_new.txt requirements.txt -Force
```

### 3.2 Verificar Versiones Críticas

```powershell
pip list | Select-String "streamlit|pandas|plotly|gspread|google-auth"
```

**Versiones esperadas:**
- streamlit >= 1.51.0
- pandas >= 2.3.3
- plotly >= 6.5.0
- gspread >= 6.2.1
- google-auth >= 2.41.1

---

## 🔄 FASE 4: CONTROL DE VERSIONES (GIT)

### 4.1 Revisar Estado Actual

```powershell
# Ver qué archivos han cambiado
git status

# Ver diferencias en archivos modificados
git diff

# Ver archivos nuevos sin seguimiento
git ls-files --others --exclude-standard
```

### 4.2 Staging de Archivos

```powershell
# Añadir módulos nuevos
git add utils/ components/ views/

# Añadir configuración
git add .streamlit/config.toml

# Añadir documentación
git add *.md

# Añadir app.py nuevo
git add app.py

# Añadir .gitignore actualizado
git add .gitignore

# Opcional: Scripts de ejecución
git add run_local.ps1 run_local.bat

# Verificar staging
git status
```

**⚠️ IMPORTANTE: NO añadas secrets.toml**
```powershell
# Verificar que secrets.toml NO está staged
git status | Select-String "secrets.toml"

# Si aparece, quitarlo inmediatamente
git reset .streamlit/secrets.toml
```

### 4.3 Crear Commit Profesional

Usando **Conventional Commits** (estándar de la industria):

```powershell
git commit -m "refactor: migrate to modular architecture

BREAKING CHANGE: Complete restructure from monolithic to modular design

- Split 1804-line app.py into 13 modular files
- Created utils/ package for data management and helpers
- Created components/ package for UI styles
- Created views/ package for page rendering
- Implemented lazy loading for views
- Preserved all optimizations (cache TTL, append_rows, ID normalization)
- Added comprehensive documentation (6 MD files)
- Reduced main app.py by 89% (1804 → 200 lines)

New structure:
- utils/data_manager.py (517 lines): Google Sheets integration
- utils/helpers.py (279 lines): Image handling, simulation, reports
- components/styles.py (489 lines): Professional CSS styling
- views/landing.py (135 lines): Hero banner homepage
- views/dashboard.py (246 lines): Global metrics and charts
- views/analytics.py (159 lines): Individual institution analysis
- views/data_entry.py (196 lines): Manual data capture form
- views/settings.py (89 lines): Admin and configuration
- app.py (200 lines): Entry point with navigation

Technical improvements:
- Type hints on all functions
- Professional logging (no more prints)
- Separation of concerns (SoC)
- Single responsibility principle (SRP)
- DRY architecture
- Improved testability and maintainability

Documentation:
- REFACTORING_GUIDE.md: Complete migration guide
- NEXT_STEPS.md: Immediate action items
- README_REFACTORING.md: Executive summary
- TREE_STRUCTURE.md: Visual architecture
- MIGRATION_COMPLETE.md: Validation checklist
- QUICK_START.md: Getting started

Legacy:
- Archived monolithic app.py to legacy/ directory
- Maintained for reference and emergency rollback"
```

**Commit message alternativo (corto):**
```powershell
git commit -m "refactor: modular architecture with 13 independent modules

- Reduced app.py from 1804 to 200 lines (-89%)
- Created utils/, components/, views/ packages
- Lazy loading and improved navigation
- Comprehensive documentation
- Preserved all optimizations
- See REFACTORING_GUIDE.md for details"
```

### 4.4 Verificar Commit

```powershell
# Ver el commit recién creado
git log -1 --stat

# Ver cambios detallados
git show HEAD
```

### 4.5 Push a GitHub

```powershell
# Revisar remoto configurado
git remote -v

# Push a main (o master según tu repo)
git push origin main

# Si es la primera vez con esta estructura
git push -u origin main
```

**Si hay conflictos:**
```powershell
# Descargar cambios remotos primero
git pull origin main --rebase

# Resolver conflictos si los hay
# Luego continuar
git rebase --continue

# Finalmente push
git push origin main
```

---

## 🌐 FASE 5: DEPLOY A STREAMLIT CLOUD (OPCIONAL)

### 5.1 Verificar Archivos Necesarios

**Checklist para Streamlit Cloud:**
- [x] `app.py` existe
- [x] `requirements.txt` actualizado
- [x] `.streamlit/config.toml` existe
- [x] Estructura modular (`utils/`, `components/`, `views/`)

### 5.2 Configurar Secrets en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Selecciona tu repositorio: `David2000-mp/Matriz-repositorio`
3. Branch: `main`
4. Main file: `app.py`
5. Advanced settings → Secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "hybrid-shelter-426922-i8"
private_key_id = "f0cd7bbfa0ec13d362bdbc69a0281434c6f07405"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCoXb9dLh9NZDJO\nO46X6xIv/hE/0Eboh659RUnX5JBgvc11NEORjqCNqFQw1orslWN2jnnzblLlVmGt\nY4ei1QLbLuyZ4kTmzHGmQwbndNiaFAwzpC7FWbGDayVQaWslzJyHgbExjQz6inrr\nhRS8Wd2l0us1sjt0pTdkDdJdnu+4cvOqzkZ6QzHSSpHd+ljswc4xwKfH4DZl+UVI\nASkZjIWvHRWdDyYj0NnWR4U+CGrvtVqepoMpdG7fA4C1DkqKzFtkSiOyt6DiWR2w\nQtXB+98sCb2NWaueTuZdsFyUY7WFOy+DGTuvxgRG93Dhi8I44cXRB2zcYYqD2wW0\nT8E1V5ubAgMBAAECggEAI5/qfOHkd7CqwEjzzAtORt9gcPs19b+32QPPMyJGtmGS\n1qjfXy4ppK+oWMkcjiCx8gUFos+GNMaJVnHH4llmCFCueYUaBSffKEnobRMZPcje\nKBMmXlWzLNaAB7q2lEHuIPH9NzncNCsXBTycfZoaPxsY77ytvemzhbUy/OJDYOiB\n7931F5zC778JP+WBmF+4b4LuNnPOPJG5hBK0cWSx9F0Aw6GIXzFHJ2ZIwKq07Y5v\nGveaktZTyb5bJ6zv1N2Zzra+p6DKWifqZSgP0CZ7yaXzFtURwd43qPsWpoNEE/Kc\nU1Miygvhq2uRkcxaXm7+v6qIM18DUwRnguNEWAZGkQKBgQDRlCifTTWVxjsBsmyf\nwB5oB9oI3w3J6dtYe/ElptgZsa7IS86TPcUhixsxvDJLfD/dZtumIQty2+AsBTap\nPVcgAhVmphAqI5xIUDNQjtkDyjW8LfynXp6g0VZcoDZZ3Qzmg4QwtaVfcYfifcJI\nzIbnOGrFqGB/B89um67SIIWQGQKBgQDNqLHbR/jeHCjMr9T0o8fFXP6R4ydxXr76\nXqh0plHHHOOs4Pdk3JmkdDQ+QmVHFQYVKe77VnvghbqohKRDD/S/sD/TqEqa2yA3\nxYOtlrW3Uz+s4U7dUMP6dpvpqQFRQmkY3xnB8Qz88WZhmK3yG30X0DYo23E4WC4t\nMq5suN9v0wKBgAepfwKz8+2R3b5mI4qDn5j2EIaagQqMvjQx89MIkoX99QHlo5vG\nelqLl2buFnikBkG17PnZ421DlKKHXkQ5teG5scaa86RWwPPz2qxrTIvS7LwAgmgs\nEWiXvqyMPvByIHKdBEwzl+QxZmJlbqDyuUviyCSJz11Vj8PfdTjBb6ChAoGAHhwT\nphIcepBO3ODlYcfUyK17y+og7TU86rUPHrz2/hrZroblUYwGppAo0fCwmT6XvGN+\nTKf1zQJnOKLq1bKxV5s7TQa3nYJ1bhTp2XFWO3fhu7Lk8/wOJU5WN1h6C+aYMn7/\na2iaSTIililfVjH2F5VxSHwQUHqAkDd6WAqdE+cCgYBlnQCkd/wFbZP+qYeqUd6Y\nfM+T1huhsga1lXio4Xs9SbDNeI6aRCAoc+z+x9pwvVuwo2CpAhH1jSpaGCzk4C4D\nLSKlRdHKoeJ1DcZ/NPFUPF/SbPRGwYrO/PyuIH2GRzscOONugrd8QuGfOrMjTHpw\ny84km7DC9J4Fkf0ugnrhoQ==\n-----END PRIVATE KEY-----\n"
client_email = "bot-matriz@hybrid-shelter-426922-i8.iam.gserviceaccount.com"
client_id = "117687675203601215901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/bot-matriz%40hybrid-shelter-426922-i8.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

6. Click "Save"
7. La app se desplegará automáticamente

---

## ✅ FASE 6: VERIFICACIÓN FINAL

### 6.1 Checklist Post-Deploy

**Local:**
- [ ] `app.py` funciona sin errores
- [ ] Todas las vistas cargan correctamente
- [ ] Datos se guardan en Google Sheets
- [ ] No hay warnings críticos en consola

**Git/GitHub:**
- [ ] Commit exitoso con mensaje profesional
- [ ] Push completado sin errores
- [ ] Ver cambios en GitHub web
- [ ] Branch `main` actualizado

**Streamlit Cloud (si aplica):**
- [ ] App desplegada exitosamente
- [ ] URL pública accesible
- [ ] Secrets configurados correctamente
- [ ] No hay errores en logs

### 6.2 Test de Regresión

```powershell
# Test 1: Cargar datos
streamlit run app.py

# Test 2: Navegación
# Probar cada página manualmente:
# - Landing → Dashboard → Analytics → Captura → Config

# Test 3: Funcionalidad crítica
# - Dashboard: Gráficos renderizan
# - Analytics: Filtros funcionan
# - Captura: Guarda datos
# - Config: Simulador genera datos
```

---

## 🔙 ROLLBACK (Si algo sale mal)

### Opción 1: Rollback Local

```powershell
# Restaurar desde legacy
$latestBackup = Get-ChildItem "legacy/app_monolithic_*.py" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latestBackup.FullName "app.py" -Force

# Reiniciar app
streamlit run app.py
```

### Opción 2: Rollback Git (Antes del Push)

```powershell
# Deshacer el commit (mantiene cambios)
git reset --soft HEAD~1

# Deshacer el commit (elimina cambios)
git reset --hard HEAD~1
```

### Opción 3: Rollback Git (Después del Push)

```powershell
# Crear commit de reversión
git revert HEAD

# Push del revert
git push origin main
```

---

## 📊 MÉTRICAS DE ÉXITO

Al finalizar el cutover, deberías tener:

- ✅ **0 errores** en la ejecución
- ✅ **100% funcionalidad** preservada
- ✅ **13 módulos** independientes
- ✅ **89% reducción** en app.py (1804 → 200 líneas)
- ✅ **6 archivos** de documentación
- ✅ **1 backup** seguro en legacy/
- ✅ **0 secrets** en Git
- ✅ **Commit profesional** con mensaje descriptivo

---

## 🎉 CELEBRACIÓN

¡Has completado exitosamente la migración más importante de tu aplicación!

**Logros desbloqueados:**
- 🏆 Arquitecto de Software
- 🏆 DevOps Engineer
- 🏆 Code Refactoring Master
- 🏆 Git Workflow Expert

**Próximos pasos sugeridos:**
1. Anunciar el cambio al equipo
2. Actualizar documentación externa
3. Planear features nuevas ahora más fáciles de implementar
4. Considerar agregar testing automatizado

---

**Última actualización**: 2024  
**Versión**: 2.0 - Production Ready  
**Autor**: DevOps Team  
**Estado**: ✅ Completado
