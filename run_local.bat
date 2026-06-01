@echo off
echo ========================================
echo   CHAMPILEAKS - Local Runner
echo ========================================
echo.
set REPO_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_DIR%run_local.ps1"
if errorlevel 1 (
	echo.
	echo Error al iniciar CHAMPILEAKS.
	pause
)
