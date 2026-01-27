# 🚀 CUTOVER PLAN - MIGRACIÓN A PRODUCCIÓN
# Ejecutar estos comandos paso a paso en PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHAMPILYTICS - CUTOVER A PRODUCCIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# FASE 1: BACKUP Y ARCHIVADO
# ============================================

Write-Host "[FASE 1] Creando estructura de backup..." -ForegroundColor Yellow

# Crear carpeta legacy para código antiguo
New-Item -Path "legacy" -ItemType Directory -Force | Out-Null

# Mover app.py antiguo a legacy con timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "app.py" "legacy/app_monolithic_$timestamp.py" -Force
Write-Host "OK Backup creado: legacy/app_monolithic_$timestamp.py" -ForegroundColor Green

# ============================================
# FASE 2: RENOMBRADO DE ARCHIVOS
# ============================================

Write-Host ""
Write-Host "[FASE 2] Renombrando archivos..." -ForegroundColor Yellow

# Eliminar app.py antiguo
Remove-Item "app.py" -Force
Write-Host "OK Eliminado: app.py (antiguo)" -ForegroundColor Green

# Renombrar app_refactored.py a app.py
Rename-Item "app_refactored.py" "app.py" -Force
Write-Host "OK Renombrado: app_refactored.py -> app.py (nuevo)" -ForegroundColor Green

# ============================================
# FASE 3: LIMPIEZA DE CACHE
# ============================================

Write-Host ""
Write-Host "[FASE 3] Limpiando cache y temporales..." -ForegroundColor Yellow

# Eliminar __pycache__ recursivamente
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "OK Limpiado: __pycache__ (todos)" -ForegroundColor Green

# Eliminar .pyc recursivamente
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force
Write-Host "OK Limpiado: *.pyc (todos)" -ForegroundColor Green

# Eliminar .pytest_cache si existe
if (Test-Path ".pytest_cache") {
    Remove-Item ".pytest_cache" -Recurse -Force
    Write-Host "OK Limpiado: .pytest_cache" -ForegroundColor Green
}

# ============================================
# FASE 4: GITIGNORE
# ============================================

Write-Host ""
Write-Host "[FASE 4] Actualizando .gitignore..." -ForegroundColor Yellow

# Crear/actualizar .gitignore
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
venv_local/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Streamlit
.streamlit/secrets.toml

# Data (sensitive)
data/*.csv

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Legacy
legacy/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary
*.tmp
*.bak
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent -Force
Write-Host "OK Actualizado: .gitignore" -ForegroundColor Green

# ============================================
# FASE 5: VERIFICACIÓN
# ============================================

Write-Host ""
Write-Host "[FASE 5] Verificando estructura..." -ForegroundColor Yellow

$requiredFiles = @("app.py", "requirements.txt", ".gitignore")
$requiredDirs = @("utils", "components", "views", ".streamlit")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "OK Encontrado: $file" -ForegroundColor Green
    } else {
        Write-Host "ERROR Faltante: $file" -ForegroundColor Red
    }
}

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "OK Encontrado: $dir/" -ForegroundColor Green
    } else {
        Write-Host "ERROR Faltante: $dir/" -ForegroundColor Red
    }
}

# ============================================
# FASE 6: GIT STAGING
# ============================================

Write-Host ""
Write-Host "[FASE 6] Preparando commit..." -ForegroundColor Yellow

# Añadir nuevos archivos
git add utils/ components/ views/ .streamlit/config.toml
Write-Host "OK Staged: Modulos nuevos" -ForegroundColor Green

# Añadir documentación
git add *.md
Write-Host "OK Staged: Documentacion" -ForegroundColor Green

# Añadir app.py nuevo y eliminar antiguo
git add app.py
if (Test-Path "app_refactored.py") {
    git rm --cached app_refactored.py -f 2>$null
}
Write-Host "OK Staged: app.py (nuevo)" -ForegroundColor Green

# Añadir .gitignore
git add .gitignore
Write-Host "OK Staged: .gitignore" -ForegroundColor Green

# Añadir scripts de ejecución
git add run_local.ps1 run_local.bat 2>$null
Write-Host "OK Staged: Scripts de ejecucion" -ForegroundColor Green

# ============================================
# RESUMEN
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CUTOVER COMPLETADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Revisar cambios: git status" -ForegroundColor White
Write-Host "2. Hacer commit: git commit -m `"refactor: arquitectura modular completa`"" -ForegroundColor White
Write-Host "3. Push a remoto: git push origin main" -ForegroundColor White
Write-Host "4. Probar app: streamlit run app.py" -ForegroundColor White
Write-Host ""
