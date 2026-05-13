#!/usr/bin/env python3
"""
Debug detallado del primer comentario
"""
import sys
sys.path.insert(0, '/content')

from utils.comment_processor import (
    normalize_text, tokenize_spanish, classify_sentiment,
    VERY_NEGATIVE_WORDS, NEGATIVE_WORDS, VERY_POSITIVE_WORDS, POSITIVE_WORDS,
    VERY_NEGATIVE_PHRASES, NEGATIVE_PHRASES, VERY_POSITIVE_PHRASES, POSITIVE_PHRASES
)

comment = "Que decepción de escuela, después de haber pasado 3 de mis mejores años de vida con ustedes (generación 75-78 secundaria). PROBLEMAS: 1) Respecto a los trámites, es increíble que no tengan terminal para pagar con tarjeta de crédito los uniformes u otros. Quieren que se haga por transferencia, enviar correo, mostrarlo en ventanilla, etc. etc. Que molestias para los papás."

print("="*80)
print("DEBUG: Primer comentario")
print("="*80)

print(f"\n📝 TEXTO ORIGINAL ({len(comment)} chars):")
print(comment[:150] + "...")

# Normalizar
normalized = normalize_text(comment)
print(f"\n🔤 NORMALIZADO:")
print(normalized[:150] + "...")

# Buscar palabras críticas
print(f"\n🔍 BÚSQUEDA DE PALABRAS CRÍTICAS:")
for word in VERY_NEGATIVE_WORDS:
    if word in normalized:
        print(f"   ✅ Encontrada: '{word}'")

for word in NEGATIVE_WORDS:
    if word in normalized:
        print(f"   🟡 Encontrada (NEGATIVE): '{word}'")

for word in VERY_POSITIVE_WORDS:
    if word in normalized:
        print(f"   🟢 Encontrada (VERY_POSITIVE): '{word}'")

for word in POSITIVE_WORDS:
    if word in normalized:
        print(f"   💚 Encontrada (POSITIVE): '{word}'")

# Buscar frases
print(f"\n📋 BÚSQUEDA DE FRASES:")
for phrase in VERY_NEGATIVE_PHRASES:
    if phrase in normalized:
        print(f"   ✅ Encontrada (VERY_NEGATIVE): '{phrase}'")

for phrase in NEGATIVE_PHRASES:
    if phrase in normalized:
        print(f"   🟡 Encontrada (NEGATIVE): '{phrase}'")

for phrase in VERY_POSITIVE_PHRASES:
    if phrase in normalized:
        print(f"   🟢 Encontrada (VERY_POSITIVE): '{phrase}'")

for phrase in POSITIVE_PHRASES:
    if phrase in normalized:
        print(f"   💚 Encontrada (POSITIVE): '{phrase}'")

# Clasificar
label, score = classify_sentiment(comment)
print(f"\n🎯 CLASIFICACIÓN FINAL:")
print(f"   Label: {label}")
print(f"   Score: {score}")
print(f"   ❌ ERROR: Debería ser 'Muy Negativo' (1)")

