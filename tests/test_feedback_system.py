"""Tests para el sistema automático de retroalimentación."""

import pytest
from pathlib import Path
import pandas as pd

from utils import comment_processor, feedback_system


def test_record_feedback_creates_csv():
    """Verifica que record_feedback crea el archivo CSV."""
    feedback_system.record_feedback(
        comment="Test comment",
        predicted_label="Neutral",
        predicted_score=3,
        correct_label="Positivo",
        correct_score=4,
    )

    assert feedback_system._FEEDBACK_FILE.exists()


def test_feedback_stats_returns_dict():
    """Verifica que get_feedback_stats retorna dict válido."""
    stats = feedback_system.get_feedback_stats()

    assert isinstance(stats, dict)
    assert "total" in stats
    assert "correct" in stats
    assert "accuracy" in stats


def test_record_feedback_and_stats():
    """Registra feedback y verifica que se cuenta correctamente."""
    initial_stats = feedback_system.get_feedback_stats()
    initial_total = initial_stats["total"]

    feedback_system.record_feedback(
        comment="Decepcion de escuela",
        predicted_label="Neutral",
        predicted_score=3,
        correct_label="Muy Negativo",
        correct_score=1,
    )

    updated_stats = feedback_system.get_feedback_stats()
    assert updated_stats["total"] == initial_total + 1


def test_improvement_suggestions_format():
    """Verifica formato de sugerencias de mejora."""
    # Agregar feedback primero para que haya datos
    for i in range(5):
        comment_processor.record_comment_feedback(
            comment="Que terrible escuela muy mala",
            predicted_label="Neutral",
            predicted_score=3,
            correct_label="Muy Negativo",
            correct_score=1,
        )
    
    suggestions = feedback_system.get_improvement_suggestions()

    assert isinstance(suggestions, dict)
    assert "suggestions" in suggestions
    assert "message" in suggestions


def test_feedback_wrapper_functions():
    """Prueba funciones wrapper en comment_processor."""
    # record_comment_feedback
    comment_processor.record_comment_feedback(
        comment="Test feedback",
        predicted_label="Neutral",
        predicted_score=3,
        correct_label="Negativo",
        correct_score=2,
    )

    # get_feedback_stats
    stats = comment_processor.get_feedback_stats()
    assert stats["total"] >= 1

    # get_improvement_suggestions
    suggestions = comment_processor.get_improvement_suggestions()
    assert isinstance(suggestions, dict)


def test_mispredictions_by_type():
    """Verifica agrupación de mispredictions."""
    comment_processor.record_comment_feedback(
        comment="Que decepcion",
        predicted_label="Positivo",
        predicted_score=4,
        correct_label="Muy Negativo",
        correct_score=1,
    )

    mispredictions = feedback_system.get_mispredictions_by_type()
    # Si hay errores, debe estar en el dict
    if mispredictions:
        for key, records in mispredictions.items():
            assert isinstance(records, list)
            assert len(records) > 0


def test_extract_candidate_words():
    """Verifica extracción de palabras candidatas."""
    # Agregar varios feedback items para "Muy Negativo"
    for i in range(3):
        comment_processor.record_comment_feedback(
            comment="Nefasta administración de la escuela",
            predicted_label="Neutral",
            predicted_score=3,
            correct_label="Muy Negativo",
            correct_score=1,
        )

    candidates = feedback_system.extract_candidate_words("Muy Negativo")
    # Si hay suficiente feedback, debería detectar "nefasta"
    if candidates:
        assert isinstance(candidates, dict)


def test_feedback_report_format():
    """Verifica que reporte se genera sin errores."""
    report = feedback_system.get_feedback_report()
    assert isinstance(report, str)
    assert len(report) > 0
    assert "FEEDBACK SYSTEM" in report
