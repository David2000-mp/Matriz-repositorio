# ============================================================================
# SCRIPT DE VERIFICACION DE SEGURIDAD Y BUILD
# ============================================================================
# 
# Proposito: Verificar que el entorno esta correctamente configurado
#            y cumple con los estandares de seguridad
#
# Uso: .\verify_security.ps1
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICACION DE SEGURIDAD Y BUILD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errorsFound = 0
$warningsFound = 0

# 1. Verificar .gitignore
Write-Host "[1/8] Verificando .gitignore..." -NoNewline
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "secrets\.toml") {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FALTA '.streamlit/secrets.toml'" -ForegroundColor Red
        $errorsFound++
    }
} else {
    Write-Host " ARCHIVO .gitignore NO EXISTE" -ForegroundColor Red
    $errorsFound++
}

# 2. Verificar secrets.toml
Write-Host "[2/8] Verificando .streamlit/secrets.toml..." -NoNewline
if (Test-Path ".streamlit/secrets.toml") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " NO EXISTE" -ForegroundColor Red
    $errorsFound++
}

# 3. Verificar secrets.toml.example
Write-Host "[3/8] Verificando .streamlit/secrets.toml.example..." -NoNewline
if (Test-Path ".streamlit/secrets.toml.example") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " NO EXISTE (recomendado)" -ForegroundColor Yellow
    $warningsFound++
}

# 4. Verificar requirements.txt
Write-Host "[4/8] Verificando requirements.txt..." -NoNewline
if (Test-Path "requirements.txt") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " NO EXISTE" -ForegroundColor Red
    $errorsFound++
}

# 5. Verificar virtual environment
Write-Host "[5/8] Verificando virtual environment..." -NoNewline
if (Test-Path "venv_local/Scripts/python.exe") {
    Write-Host " OK (venv_local)" -ForegroundColor Green
} elseif (Test-Path "venv/bin/python") {
    Write-Host " OK (venv)" -ForegroundColor Green
} else {
    Write-Host " NO EXISTE" -ForegroundColor Yellow
    $warningsFound++
}

# 6. Verificar estructura de codigo
Write-Host "[6/8] Verificando estructura de codigo..." -NoNewline
$requiredFiles = @("app.py", "utils/data_manager.py", "components/styles.py")
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}
if ($missingFiles.Count -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FALTAN ARCHIVOS" -ForegroundColor Red
    $errorsFound++
}

# 7. Verificar documentacion
Write-Host "[7/8] Verificando documentacion..." -NoNewline
$docs = @("SECURITY.md", "BUILD_RELEASE.md")
$missingDocs = @()
foreach ($doc in $docs) {
    if (-not (Test-Path $doc)) {
        $missingDocs += $doc
    }
}
if ($missingDocs.Count -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FALTAN: $($missingDocs -join ', ')" -ForegroundColor Yellow
    $warningsFound++
}

# 8. Verificar tests
Write-Host "[8/8] Verificando tests..." -NoNewline
if (Test-Path "tests/test_data_manager.py") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " NO EXISTEN TESTS" -ForegroundColor Yellow
    $warningsFound++
}

# RESUMEN
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errorsFound -eq 0 -and $warningsFound -eq 0) {
    Write-Host "TODO PERFECTO!" -ForegroundColor Green
    Write-Host "Tu proyecto esta listo para produccion." -ForegroundColor Green
    Write-Host ""
    Write-Host "Siguiente paso: streamlit run app.py" -ForegroundColor Cyan
    exit 0
} else {
    if ($errorsFound -gt 0) {
        Write-Host "ERRORES CRITICOS: $errorsFound" -ForegroundColor Red
    }
    if ($warningsFound -gt 0) {
        Write-Host "ADVERTENCIAS: $warningsFound" -ForegroundColor Yellow
    }
    Write-Host ""
    
    if ($errorsFound -gt 0) {
        Write-Host "ACCION REQUERIDA: Corrige los errores antes de desplegar." -ForegroundColor Red
        Write-Host "Consulta SECURITY.md para mas informacion." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "Hay advertencias pero puedes continuar." -ForegroundColor Yellow
        exit 0
    }
}
