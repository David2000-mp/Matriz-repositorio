# Script para ejecutar CHAMPILYTICS en Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHAMPILYTICS - Maristas Analytics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv_local\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Iniciando aplicacion Streamlit..." -ForegroundColor Green
Write-Host "La aplicacion se abrira automaticamente en tu navegador" -ForegroundColor Green
Write-Host ""

streamlit run app.py
