#!/usr/bin/env python3
"""
Script de prueba: Validar integración Ollama en CHAMPILEAKS
=============================================================
Prueba todos los módulos y funciones clave.
"""

import sys
import os
from datetime import datetime

# Agregar utils al path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("🧪 TEST SUITE: OLLAMA INTEGRATION FOR CHAMPILEAKS")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

failed_tests = []
warnings = []

# ============================================================================
# TEST 1: Verificar que Ollama está corriendo
# ============================================================================
print("\n[TEST 1] Verificar que Ollama está disponible...")
print("-" * 80)

try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"✅ Ollama DISPONIBLE")
        print(f"   Modelos descargados: {len(models)}")
        for model in models:
            size_gb = model.get("size", 0) / (1024**3)
            print(f"   - {model['name']} ({size_gb:.1f}GB)")
        ollama_available = True
    else:
        print(f"❌ Ollama respondió con error: {response.status_code}")
        ollama_available = False
except Exception as e:
    print(f"❌ Ollama NO DISPONIBLE: {e}")
    ollama_available = False
    failed_tests.append("TEST 1: disponibilidad Ollama")

# ============================================================================
# TEST 2: Importar módulos Ollama
# ============================================================================
print("\n[TEST 2] Importar módulos...")
print("-" * 80)

try:
    from utils.ollama_provider import (
        ollama_provider,
        OllamaProvider,
        SentimentLevel,
        SentimentAnalysis,
        ThemeClassification,
        RecommendationItem,
    )
    print("✅ ollama_provider importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando ollama_provider: {e}")
    sys.exit(1)

try:
    from utils.ollama_extensions import (
        classify_sentiment_with_ollama,
        get_sentiment_with_rationale,
    )
    print("✅ ollama_extensions (sentiment) importado")
except ImportError as e:
    print(f"❌ Error importando ollama_extensions: {e}")
    sys.exit(1)

try:
    from utils.ollama_extensions_report import (
        generate_summary_with_ollama,
        generate_recommendations_for_account,
    )
    print("✅ ollama_extensions_report importado")
except ImportError as e:
    print(f"❌ Error importando ollama_extensions_report: {e}")
    sys.exit(1)

try:
    from utils.ollama_extensions_content import (
        classify_content_with_ollama,
        detect_emerging_themes,
    )
    print("✅ ollama_extensions_content importado")
except ImportError as e:
    print(f"❌ Error importando ollama_extensions_content: {e}")
    sys.exit(1)

# ============================================================================
# TEST 3: Verificar OllamaProvider singleton
# ============================================================================
print("\n[TEST 3] Verificar OllamaProvider...")
print("-" * 80)

print(f"   Base URL: {ollama_provider.base_url}")
print(f"   Modelo: {ollama_provider.model}")
print(f"   Timeout: {ollama_provider.timeout}s")
print(f"   Habilitado: {ollama_provider.enabled}")

is_available = ollama_provider.is_available()
print(f"   ✅ Ollama disponible: {is_available}")
if ollama_available and not is_available:
    failed_tests.append("TEST 3: provider reporta no disponible")

cache_stats = ollama_provider.get_cache_stats()
print(f"   Cache stats: {cache_stats}")

# ============================================================================
# TEST 4: Test de Sentimiento
# ============================================================================
print("\n[TEST 4] Prueba de Análisis de Sentimiento...")
print("-" * 80)

test_comments = [
    "Excelente colegio, me encanta!",
    "Terrible experiencia, muy caro y mala atención.",
    "Es un colegio normal, nada especial.",
]

for comment in test_comments:
    try:
        label, score = classify_sentiment_with_ollama(comment)
        print(f"   Comentario: '{comment[:50]}...'")
        print(f"   Sentimiento: {label} (score: {score}/5)")
        
        # Obtener rationale
        analysis_detail = get_sentiment_with_rationale(comment)
        print(f"   Confianza: {analysis_detail['confidence']:.2f}")
        print(f"   Rationale: {analysis_detail['rationale'][:60]}...")
        if ollama_available and not analysis_detail.get("used_ollama", False):
            warnings.append(f"TEST 4: sentimiento en fallback para '{comment[:25]}...'")
        print()
    except Exception as e:
        print(f"   ❌ Error en sentimiento: {e}\n")
        failed_tests.append("TEST 4: análisis de sentimiento")

# ============================================================================
# TEST 5: Test de Resumen de Métrica
# ============================================================================
print("\n[TEST 5] Prueba de Generación de Resumen...")
print("-" * 80)

try:
    summary, was_ollama = generate_summary_with_ollama(
        metric_name="Engagement Rate",
        current_value=4.2,
        change_pct=15.3,
        context="Publicaciones de eventos aumentaron 20%"
    )
    print(f"✅ Resumen generado ({'Ollama' if was_ollama else 'Heurístico'})")
    if ollama_available and not was_ollama:
        warnings.append("TEST 5: resumen en fallback")
    print(f"   {summary[:120]}...")
except Exception as e:
    print(f"❌ Error generando resumen: {e}")
    failed_tests.append("TEST 5: generación de resumen")

# ============================================================================
# TEST 6: Test de Clasificación de Contenido
# ============================================================================
print("\n[TEST 6] Prueba de Clasificación de Contenido...")
print("-" * 80)

try:
    primary, secondary, conf, was_ollama = classify_content_with_ollama(
        title="Nuevo laboratorio de robótica",
        description="Inauguramos un laboratorio equipado con tecnología de punta"
    )
    print(f"✅ Contenido clasificado ({'Ollama' if was_ollama else 'Heurístico'})")
    if ollama_available and not was_ollama:
        warnings.append("TEST 6: clasificación de contenido en fallback")
    print(f"   Tema principal: {primary}")
    print(f"   Temas secundarios: {secondary}")
    print(f"   Confianza: {conf:.2f}")
except Exception as e:
    print(f"❌ Error clasificando contenido: {e}")
    failed_tests.append("TEST 6: clasificación de contenido")

# ============================================================================
# TEST 7: Test de Recomendaciones
# ============================================================================
print("\n[TEST 7] Prueba de Generación de Recomendaciones...")
print("-" * 80)

try:
    recs, was_ollama = generate_recommendations_for_account(
        account_name="Colegio Marista Centro",
        avg_followers=5000,
        engagement_rate=3.5,
        top_category="académico",
        top_category_pct=45,
        negative_comments_pct=15,
        top_terms="cafetería, costo, profesores",
        issues="Comentarios negativos sobre precios"
    )
    print(f"✅ Recomendaciones generadas ({'Ollama' if was_ollama else 'Heurísticas'})")
    if ollama_available and not was_ollama:
        warnings.append("TEST 7: recomendaciones en fallback")
    print(f"   Total: {len(recs)} recomendaciones")
    for i, rec in enumerate(recs[:2], 1):
        print(f"   {i}. {rec['action'][:60]}...")
except Exception as e:
    print(f"❌ Error generando recomendaciones: {e}")
    failed_tests.append("TEST 7: generación de recomendaciones")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN DE TESTS")
print("=" * 80)

if failed_tests:
    print("❌ TESTS CON FALLAS")
    for failure in failed_tests:
        print(f"   - {failure}")
elif ollama_available:
    print("✅ Ollama está corriendo y disponible")
    print("✅ Todos los módulos importados correctamente")
    print("✅ OllamaProvider funciona correctamente")
    print("✅ Funciones de extensión disponibles")
    if warnings:
        print("\n⚠️ TESTS COMPLETADOS CON ADVERTENCIAS")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print("\n🎉 TODOS LOS TESTS PASADOS - LISTO PARA DESPLIEGUE")
else:
    print("⚠️  Ollama no está disponible")
    print("✅ Sistema usará fallback a heurísticas locales")
    print("ℹ️  Para activar Ollama: asegúrate que 'ollama serve' esté corriendo")

print("\n" + "=" * 80)
print("Próximo paso: Ejecutar 'streamlit run app.py' para desplegar CHAMPILEAKS")
print("=" * 80)

if failed_tests:
    sys.exit(1)
