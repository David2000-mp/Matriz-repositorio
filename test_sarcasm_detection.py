#!/usr/bin/env python3
"""
Test para Opción 1 + 2: Detección de sarcasmo por adversativos
"""
import sys
sys.path.insert(0, '/content')

from utils.comment_processor import classify_sentiment

# Test cases: sarcasmo con adversativos
test_cases = [
    # Opción 1: [POSITIVA] + pero + [NEGATIVA] = Negativo/Muy Negativo
    {
        "text": "me encantó esa escuela, pero ahora hay que pagar por todo",
        "expected": ("Negativo", 2),
        "desc": "Opción 1: Encantó pero pagar"
    },
    {
        "text": "Que decepción de escuela, después de haber pasado los mejores años pero resulta que no cumplen",
        "expected": ("Muy Negativo", 1),
        "desc": "Opción 1: Mejores años pero decepción"
    },
    {
        "text": "La razón por la cual me encantó esa escuela, aunque ahora hay que pagar por todo",
        "expected": ("Negativo", 2),
        "desc": "Opción 1: Encantó aunque pagar (aunque)"
    },
    # Opción 2: VERY_NEGATIVE presente + positivas = ignorar positivas
    {
        "text": "extraordinaria guía pero fraudulento en los precios",
        "expected": ("Muy Negativo", 1),
        "desc": "Opción 2: Extraordinaria pero fraude (contexto de párrafo)"
    },
    {
        "text": "Una gran obra pero con arrogancia y soberbia de los directivos",
        "expected": ("Muy Negativo", 1),
        "desc": "Opción 2: Gran obra pero soberbia"
    },
    # Casos que NO deben cambiar (sin adversativos)
    {
        "text": "extraordinaria guía, soy una orgullosa mamá Marista",
        "expected": ("Muy Positivo", 5),
        "desc": "Control: Positivas sin adversativo = Muy Positivo"
    },
    {
        "text": "Que decepción de escuela, nefasta administración",
        "expected": ("Muy Negativo", 1),
        "desc": "Control: Muy Negativas sin adversativo = Muy Negativo"
    },
    # Negaciones con ventana ampliada
    {
        "text": "No es increíble la administración, es verdaderamente nefasta y fraudulenta",
        "expected": ("Muy Negativo", 1),
        "desc": "Negación: 'No es increíble' + 'nefasta' = Muy Negativo"
    },
]

print("\n" + "="*80)
print("TEST: Detección de Sarcasmo por Adversativos (Opción 1 + 2)")
print("="*80)

passed = 0
failed = 0

for test in test_cases:
    label, score = classify_sentiment(test["text"])
    expected_label, expected_score = test["expected"]
    
    is_correct = label == expected_label and score == expected_score
    status = "✅" if is_correct else "❌"
    
    if is_correct:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status} {test['desc']}")
    print(f"   Esperado: {expected_label} ({expected_score})")
    print(f"   Obtenido: {label} ({score})")
    print(f"   Texto: {test['text'][:80]}...")

print("\n" + "="*80)
print(f"RESUMEN: {passed} pasados, {failed} fallados")
print("="*80)
