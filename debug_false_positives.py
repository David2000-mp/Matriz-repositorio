#!/usr/bin/env python3
"""
Debug: Por qué están siendo clasificadas como Muy Positivo
"""
import sys
sys.path.insert(0, '/content')

from utils.comment_processor import (
    normalize_text, tokenize_spanish, classify_sentiment,
    VERY_POSITIVE_PHRASES, VERY_POSITIVE_WORDS,
    VERY_NEGATIVE_WORDS, VERY_NEGATIVE_PHRASES
)

test_cases = [
    "Que decepción de escuela, después de haber pasado los mejores años pero resulta que no cumplen",
    "extraordinaria guía pero fraudulento en los precios",
]

for text in test_cases:
    print(f"\n{'='*80}")
    print(f"TEXTO: {text}")
    print('='*80)
    
    normalized = normalize_text(text)
    
    # Verificar qué frases VERY_POSITIVE/NEGATIVE coinciden
    print("\n🔍 FRASES MUY POSITIVAS ENCONTRADAS:")
    for phrase in VERY_POSITIVE_PHRASES:
        if phrase in normalized:
            print(f"  ✅ '{phrase}'")
    
    print("\n🔍 FRASES MUY NEGATIVAS ENCONTRADAS:")
    for phrase in VERY_NEGATIVE_PHRASES:
        if phrase in normalized:
            print(f"  ✅ '{phrase}'")
    
    print("\n🔍 PALABRAS MUY POSITIVAS ENCONTRADAS:")
    tokens = tokenize_spanish(normalized)
    very_pos_words = [t for t in tokens if t in VERY_POSITIVE_WORDS]
    print(f"  {very_pos_words}")
    
    print("\n🔍 PALABRAS MUY NEGATIVAS ENCONTRADAS:")
    very_neg_words = [t for t in tokens if t in VERY_NEGATIVE_WORDS]
    print(f"  {very_neg_words}")
    
    # Clasificación
    label, score = classify_sentiment(text)
    print(f"\n🎯 CLASIFICACIÓN: {label} ({score})")

