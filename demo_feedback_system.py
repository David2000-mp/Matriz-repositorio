#!/usr/bin/env python
"""Demostración del sistema automático de retroalimentación.

Ejecuta: python demo_feedback_system.py

Este script muestra cómo el sistema aprende automáticamente
de comentarios mal clasificados sin intervención manual.
"""

from utils.comment_processor import (
    classify_sentiment,
    record_comment_feedback,
    get_feedback_stats,
    get_improvement_suggestions,
    get_feedback_report,
)


def main():
    print("=" * 70)
    print("DEMO: SISTEMA AUTOMÁTICO DE RETROALIMENTACIÓN")
    print("=" * 70)
    print()

    # Comentarios de prueba que suenan como mala clasificación
    test_comments = [
        {
            "text": "Que decepción de escuela, después de años con ustedes",
            "expected": "Muy Negativo",
        },
        {
            "text": "Nefasta administración, los directivos no cumplen valores",
            "expected": "Muy Negativo",
        },
        {
            "text": "Extraordinaria guía para los chicos, orgullosa mamá Marista",
            "expected": "Muy Positivo",
        },
        {
            "text": "Mi casa, extraño mucho la formación marista",
            "expected": "Positivo",
        },
    ]

    print("\n1️⃣  PASO 1: Clasificar comentarios\n")
    predictions = []
    for item in test_comments:
        label, score = classify_sentiment(item["text"])
        predictions.append((item, label, score))
        print(f"   Texto: {item['text'][:60]}...")
        print(f"   Predicho: [{score}] {label}")
        print(f"   Esperado: {item['expected']}")
        is_correct = "✅" if label == item["expected"] else "❌"
        print(f"   {is_correct}")
        print()

    print("\n2️⃣  PASO 2: Registrar feedback para correcciones\n")
    for item, predicted_label, predicted_score in predictions:
        if predicted_label != item["expected"]:
            print(f"   Registrando corrección: {item['text'][:50]}...")
            # Convertir expected a score
            expected_scores = {
                "Muy Positivo": 5,
                "Positivo": 4,
                "Neutral": 3,
                "Negativo": 2,
                "Muy Negativo": 1,
            }
            record_comment_feedback(
                comment=item["text"],
                predicted_label=predicted_label,
                predicted_score=predicted_score,
                correct_label=item["expected"],
                correct_score=expected_scores[item["expected"]],
            )
            print(f"      ✓ Feedback registrado")

    print("\n3️⃣  PASO 3: Ver estadísticas del feedback\n")
    stats = get_feedback_stats()
    print(f"   Total comentarios con feedback: {stats['total']}")
    print(f"   Correctamente clasificados:     {stats['correct']}")
    print(f"   Accuracy actual:                {stats['accuracy']:.1%}")

    print("\n4️⃣  PASO 4: Obtener sugerencias automáticas\n")
    suggestions = get_improvement_suggestions()
    print(f"   {suggestions['message']}")

    if suggestions["suggestions"]:
        print("\n   Palabras sugeridas para agregar:")
        for label, data in suggestions["suggestions"].items():
            print(f"\n   {label}:")
            for word in data["words_to_add"][:5]:
                freq = data["frequency"].get(word, 1)
                print(f"      + {word} ({freq}x detectada)")

    print("\n5️⃣  PASO 5: Reporte completo\n")
    report = get_feedback_report()
    print(report)

    print("\n" + "=" * 70)
    print("✨ RESUMEN")
    print("=" * 70)
    print("""
El sistema automáticamente:
  ✓ Detectó comentarios mal clasificados
  ✓ Almacenó feedback en data/comment_feedback.csv
  ✓ Analizó patrones de error
  ✓ Sugirió palabras para mejorar

PRÓXIMO PASO:
  En la UI, los usuarios pueden marcar "Mal clasificado" en cada
  comentario. El sistema automáticamente:
  
  1. Registra el feedback
  2. Cada 20+ comentarios, analiza patrones
  3. Sugiere mejoras sin tocar código
  4. Las mejoras se aplican automáticamente

¡Cero intervención manual necesaria! 🚀
    """)


if __name__ == "__main__":
    main()
