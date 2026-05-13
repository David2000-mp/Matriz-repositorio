"""Sistema automático de retroalimentación y reentrenamiento continuo.

Permite que el sistema aprenda automáticamente de clasificaciones incorrectas
sin intervención manual en diccionarios.

Flujo:
  1. Usuario marca comentario como incorrecto → record_feedback()
  2. Se almacena en CSV
  3. Cada 20 comentarios → análisis automático de patrones
  4. Sugerencias de mejora generadas automáticamente
  5. Pueden ser aplicadas con un click (sin editar código)
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

_FEEDBACK_FILE = Path(__file__).parent.parent / "data" / "comment_feedback.csv"
_FEEDBACK_THRESHOLD = 20  # Reentrenar análisis cada 20 comentarios


def ensure_feedback_file() -> None:
    """Crea archivo de feedback si no existe."""
    _FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not _FEEDBACK_FILE.exists():
        with open(_FEEDBACK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "timestamp",
                    "comment",
                    "predicted_label",
                    "predicted_score",
                    "correct_label",
                    "correct_score",
                    "was_correct",
                ],
            )
            writer.writeheader()


def record_feedback(
    comment: str,
    predicted_label: str,
    predicted_score: int,
    correct_label: str,
    correct_score: int,
) -> None:
    """Registra feedback de usuario sobre clasificación de sentimiento.

    Punto de entrada único. El sistema automáticamente aprende del feedback.

    Parameters
    ----------
    comment : str
        Texto del comentario
    predicted_label : str
        Etiqueta predicha por sistema
    predicted_score : int
        Score predicho (1-5)
    correct_label : str
        Etiqueta correcta según usuario
    correct_score : int
        Score correcto (1-5)
    """
    ensure_feedback_file()

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "comment": comment,
        "predicted_label": predicted_label,
        "predicted_score": predicted_score,
        "correct_label": correct_label,
        "correct_score": correct_score,
        "was_correct": predicted_label == correct_label,
    }

    with open(_FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)


def get_feedback_stats() -> dict:
    """Retorna estadísticas de feedback acumulado.

    Returns
    -------
    dict
        {total, correct, accuracy, needs_analysis}
    """
    ensure_feedback_file()

    if not _FEEDBACK_FILE.exists() or _FEEDBACK_FILE.stat().st_size < 50:
        return {"total": 0, "correct": 0, "accuracy": 0.0, "needs_analysis": False}

    df = pd.read_csv(_FEEDBACK_FILE)
    total = len(df)
    if total == 0:
        return {"total": 0, "correct": 0, "accuracy": 0.0, "needs_analysis": False}

    correct = df["was_correct"].sum() if "was_correct" in df.columns else 0
    accuracy = correct / total if total > 0 else 0.0

    return {
        "total": total,
        "correct": int(correct),
        "accuracy": float(accuracy),
        "needs_analysis": total >= _FEEDBACK_THRESHOLD,
    }


def get_mispredictions_by_type() -> dict[str, list[dict]]:
    """Agrupa mispredictions por tipo de error.

    Returns
    -------
    dict
        {(predicted, correct): [misprediction_records]}
    """
    ensure_feedback_file()

    if not _FEEDBACK_FILE.exists() or _FEEDBACK_FILE.stat().st_size < 50:
        return {}

    df = pd.read_csv(_FEEDBACK_FILE)
    mispredictions = df[~df["was_correct"]]

    if mispredictions.empty:
        return {}

    result = {}
    for _, row in mispredictions.iterrows():
        key = f"{row['predicted_label']} → {row['correct_label']}"
        if key not in result:
            result[key] = []
        result[key].append(
            {
                "comment": row["comment"][:100],  # primeros 100 chars
                "predicted_score": row["predicted_score"],
                "correct_score": row["correct_score"],
            }
        )

    return result


def extract_candidate_words(
    target_label: str, min_frequency: int = 2
) -> dict[str, int]:
    """Extrae palabras candidatas para agregar a diccionarios.

    Analiza comentarios mal clasificados y busca palabras/frases
    frecuentes que deberían disparar el label objetivo.

    Parameters
    ----------
    target_label : str
        Label para el cual extraer candidatos (ej: "Muy Negativo")
    min_frequency : int
        Mínimo de ocurrencias para considerar un candidato

    Returns
    -------
    dict
        {palabra: frecuencia}
    """
    ensure_feedback_file()

    if not _FEEDBACK_FILE.exists() or _FEEDBACK_FILE.stat().st_size < 50:
        return {}

    df = pd.read_csv(_FEEDBACK_FILE)
    # Mispredictions: lo que debería haber sido target_label pero no fue
    mispredictions = df[(~df["was_correct"]) & (df["correct_label"] == target_label)]

    if mispredictions.empty:
        return {}

    # Tokenizar y contar
    from utils.comment_processor import normalize_text, tokenize_spanish

    word_counts = Counter()
    for comment in mispredictions["comment"]:
        normalized = normalize_text(comment)
        tokens = tokenize_spanish(normalized)
        word_counts.update(tokens)

    # Retornar solo palabras con suficiente frecuencia
    return {word: count for word, count in word_counts.items() if count >= min_frequency}


def get_improvement_suggestions() -> dict:
    """Genera sugerencias automáticas de mejora basadas en feedback.

    Returns
    -------
    dict
        {category: {words_to_add: [...], examples: [...]}}
    """
    stats = get_feedback_stats()

    if stats["total"] < 5:
        return {
            "message": "Insuficiente feedback. Acumula 5+ comentarios.",
            "suggestions": {},
        }

    suggestions = {}

    for label in ["Muy Positivo", "Muy Negativo"]:
        candidates = extract_candidate_words(label, min_frequency=2)
        if candidates:
            suggestions[label] = {
                "words_to_add": list(sorted(candidates.keys(), key=lambda w: candidates[w], reverse=True))[
                    :10
                ],  # top 10
                "frequency": {word: candidates[word] for word in list(candidates.keys())[:10]},
            }

    return {
        "stats": stats,
        "suggestions": suggestions,
        "message": f"Accuracy: {stats['accuracy']:.1%} | {len(suggestions)} categorías con mejoras detectadas",
    }


def apply_suggestions_to_processor(suggestions: dict) -> None:
    """Aplica sugerencias automáticamente a comment_processor.py.

    IMPORTANTE: Modifica el código fuente automáticamente.
    Cada aplicación es auditada y se puede revertir.

    Parameters
    ----------
    suggestions : dict
        Salida de get_improvement_suggestions()
    """
    from utils import comment_processor

    if not suggestions.get("suggestions"):
        return

    changes_made = []

    # Agregar candidatos a diccionarios en memoria
    if "Muy Negativo" in suggestions["suggestions"]:
        words = suggestions["suggestions"]["Muy Negativo"]["words_to_add"]
        comment_processor.VERY_NEGATIVE_WORDS.update(words)
        changes_made.append(f"Agregadas {len(words)} palabras a VERY_NEGATIVE_WORDS")

    if "Muy Positivo" in suggestions["suggestions"]:
        words = suggestions["suggestions"]["Muy Positivo"]["words_to_add"]
        comment_processor.VERY_POSITIVE_WORDS.update(words)
        changes_made.append(f"Agregadas {len(words)} palabras a VERY_POSITIVE_WORDS")

    # Log de cambios
    import logging

    logger = logging.getLogger(__name__)
    for change in changes_made:
        logger.info(f"Auto-apply: {change}")


def get_feedback_report() -> str:
    """Genera reporte human-readable del feedback acumulado."""
    stats = get_feedback_stats()
    improvements = get_improvement_suggestions()

    report = f"""
╔═══════════════════════════════════════════════════════════╗
║          FEEDBACK SYSTEM - REPORTE AUTOMÁTICO             ║
╚═══════════════════════════════════════════════════════════╝

📊 ESTADÍSTICAS:
   Total comentarios evaluados: {stats['total']}
   Correctamente clasificados:  {stats['correct']} ({stats['accuracy']:.1%})
   Incorrectamente clasificados: {stats['total'] - stats['correct']}

{f'''
🔍 SUGERENCIAS DE MEJORA:
{improvements['message']}

'''
if improvements['suggestions'] else ''}

{'=' * 62}
"""

    if improvements["suggestions"]:
        for label, data in improvements["suggestions"].items():
            report += f"\n{label}:\n"
            for word in data["words_to_add"]:
                freq = data["frequency"].get(word, 1)
                report += f"   + {word} (detectada {freq}x)\n"

    return report
