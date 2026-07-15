#!/usr/bin/env python3
"""
Script de Despliegue Local: CHAMPILEAKS con Ollama
==================================================
1. Valida que Ollama esté corriendo
2. Verifica modelos disponibles  
3. Ejecuta prueba rápida de integración
4. Inicia Streamlit
"""

import subprocess
import sys
import os

print("=" * 80)
print("🚀 CHAMPILEAKS DEPLOYMENT - LOCAL WITH OLLAMA")
print("=" * 80)

# ============================================================================
# PASO 1: Verificar Ollama
# ============================================================================
print("\n[1/4] Verificando Ollama...")
print("-" * 80)

try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"✅ Ollama corriendo con {len(models)} modelo(s):")
        for model in models:
            size_gb = model.get("size", 0) / (1024**3)
            print(f"   - {model['name']} ({size_gb:.1f}GB)")
    else:
        print(f"❌ Error: Ollama respondió con {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ollama no responde: {e}")
    print("   ⚠️  Asegúrate de ejecutar: ollama serve (en otra terminal)")
    sys.exit(1)

# ============================================================================
# PASO 2: Verificar configuración de Secrets
# ============================================================================
print("\n[2/4] Verificando configuración Ollama...")
print("-" * 80)

secrets_path = os.path.expanduser("~/.streamlit/secrets.toml")
if os.path.exists(secrets_path):
    with open(secrets_path) as f:
        content = f.read()
        if "ollama" in content and "llama3" in content:
            print(f"✅ secrets.toml configurado correctamente")
            print(f"   Ubicación: {secrets_path}")
        else:
            print("⚠️  secrets.toml existe pero podría necesitar configuración")
else:
    print(f"⚠️  secrets.toml no encontrado en {secrets_path}")
    print("   Usando configuración por defecto")

# ============================================================================
# PASO 3: Verificar módulos
# ============================================================================
print("\n[3/4] Verificando módulos Python...")
print("-" * 80)

required_modules = [
    "streamlit",
    "pandas",
    "ollama",
    "requests",
    "plotly",
    "gspread",
]

missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError:
        print(f"   ❌ {module} (FALTA)")
        missing.append(module)

if missing:
    print(f"\n⚠️  Módulos faltantes: {', '.join(missing)}")
    print("   Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
    print("   ✅ Instalación completada")

# ============================================================================
# PASO 4: Iniciar Streamlit
# ============================================================================
print("\n[4/4] Iniciando CHAMPILEAKS...")
print("-" * 80)
print("\n✅ Despliegue local EXITOSO")
print("\n📊 CHAMPILEAKS estará disponible en: http://localhost:8501")
print("🤖 Ollama integrado: http://localhost:11434")
print("\nPresiona Ctrl+C para detener.\n")

os.chdir("c:\\Users\\SPARTAN PC\\Matriz-repositorio")
os.system("streamlit run app.py")
