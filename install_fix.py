import sys
import subprocess

# Esto fuerza la instalación en EL MISMO Python que está ejecutando este script
print(f"Instalando en: {sys.executable}")
subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf", "kaleido"])
print("✅ INSTALACIÓN COMPLETADA. Ahora borra este archivo y corre 'streamlit run app.py'")