@echo off
REM ==========================================================================
REM QUICK TEST: Valida que la sincronización fue exitosa
REM Ejecuta: .\quick_test.bat
REM ==========================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              CHAMPILYTICS QUICK TEST (Windows)                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Activar virtual environment
call .\venv_stable\Scripts\Activate.ps1 >nul 2>&1

if errorlevel 1 (
    echo [ERROR] No se pudo activar venv_stable
    exit /b 1
)

echo [1/3] Validando integridad local...
python validate_sync.py
if errorlevel 1 (
    echo.
    echo [ERROR] Validación falló
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando conexión a Google Sheets...
python -c "from utils.sheets_connector import conectar_sheets; s=conectar_sheets(); print('✅ Conectado a:', s.title if s else 'ERROR')" 2>nul

echo.
echo [3/3] Conteo de registros en CSV...
python -c "import pandas as pd; c=len(pd.read_csv('data/cuentas.csv')); m=len(pd.read_csv('data/metricas.csv')); print(f'✅ Cuentas: {c}, Metricas: {m}')"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         ✅ PRUEBA RÁPIDA COMPLETADA EXITOSAMENTE             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Proximos pasos:
echo   1. Abre: streamlit run app.py
echo   2. Presiona C en el navegador para limpiar caché
echo   3. Verifica que aparecen 471 registros
echo.
pause
