@echo off
echo ========================================
echo   CHAMPILYTICS - Maristas Analytics
echo ========================================
echo.
echo Activando entorno virtual...
call venv_local\Scripts\activate.bat
echo.
echo Iniciando aplicacion Streamlit...
streamlit run app.py
pause
