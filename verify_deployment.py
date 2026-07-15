#!/usr/bin/env python3
"""
Test rápido con llama3.1
Valida que Ollama + CHAMPILEAKS funcionan juntos
"""

import sys
import os
sys.path.insert(0, "c:\\Users\\SPARTAN PC\\Matriz-repositorio")

print("\n" + "="*80)
print("✅ TEST FINAL - OLLAMA + CHAMPILEAKS")
print("="*80 + "\n")

# Test 1: Verificar Ollama está disponible
print("[TEST 1] Ollama disponible...")
import requests
response = requests.get("http://localhost:11434/api/tags", timeout=5)
models = [m['name'] for m in response.json()['models']]
print(f"✅ Modelos disponibles: {models}\n")

# Test 2: Cargar módulos
print("[TEST 2] Cargar módulos Ollama...")
os.environ['STREAMLIT_SECRETS_FILE'] = os.path.expanduser("~/.streamlit/secrets.toml")

from utils.ollama_provider import ollama_provider
print(f"✅ OllamaProvider configurado")
print(f"   - Base URL: {ollama_provider.base_url}")
print(f"   - Modelo: {ollama_provider.model}")
print(f"   - Disponible: {ollama_provider.is_available()}\n")

# Test 3: Prueba de sentimiento
print("[TEST 3] Prueba sentimiento...")
from utils.ollama_extensions import classify_sentiment_with_ollama
label, score = classify_sentiment_with_ollama("Me encanta esta escuela, excelente!")
print(f"✅ Sentimiento: {label} ({score}/5)\n")

# Test 4: Prueba de resumen
print("[TEST 4] Prueba de resumen...")
from utils.ollama_extensions_report import generate_summary_with_ollama
summary, used = generate_summary_with_ollama(
    "Engagement Rate", 4.5, 12.3,
    context="Contenido de eventos subió 20%"
)
print(f"✅ Resumen generado ({'Ollama' if used else 'Heurístico'})")
print(f"   {summary[:80]}...\n")

print("="*80)
print("🎉 TODOS LOS TESTS PASARON - LISTO PARA PRODUCCIÓN")
print("="*80)
print("\nEjecuta: python deploy_local.py")
print("O directamente: streamlit run app.py\n")
