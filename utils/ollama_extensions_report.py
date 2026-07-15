"""
Extensión de Report Generator con integración Ollama
======================================================
Funciones que generan conclusiones narrativas mejoradas con Ollama.

Este módulo EXTIENDE las funciones existentes sin romper compatibilidad:
- generate_summary_with_ollama: versión mejorada que usa Ollama
- generate_insights_narrative: genera narrativa ejecutiva detallada

Las funciones originales siguen funcionando sin cambios.
"""

from typing import Tuple, List, Dict, Any
from utils.ollama_provider import ollama_provider, RecommendationItem
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)


def generate_summary_with_ollama(
    metric_name: str,
    current_value: float,
    change_pct: float,
    context: str = "",
    category: str = ""
) -> Tuple[str, bool]:
    """
    Genera un resumen narrativo de una métrica usando Ollama.
    
    Estrategia:
    1. Si Ollama está disponible, generar narrativa con contexto
    2. Si Ollama falla, usar template simple
    
    Args:
        metric_name: Nombre de la métrica (ej: "Engagement Rate")
        current_value: Valor actual
        change_pct: Cambio % vs período anterior
        context: Contexto adicional (ej: "competencia está en 3.5%")
        category: Categoría del contexto (ej: "deportes")
    
    Returns:
        Tuple[str, bool]: (narrativa, fue_generado_por_ollama)
    
    Ejemplo:
        summary, used_ollama = generate_summary_with_ollama(
            "Engagement Rate", 4.2, 15.3,
            context="Publicaciones de deportes suben 20%"
        )
        # -> ("El engagement aumentó significativamente...", True)
    """
    full_context = f"Categoría: {category}\n{context}" if category else context
    
    summary, was_ollama = ollama_provider.generate_summary(
        metric_name=metric_name,
        current_value=current_value,
        change_pct=change_pct,
        context=full_context
    )
    
    if was_ollama:
        logger.info(f"Generada conclusión Ollama para {metric_name}: {summary[:80]}...")
    else:
        logger.debug(f"Fallback a conclusión heurística para {metric_name}")
    
    return summary, was_ollama


def generate_insights_narrative(
    account_name: str,
    metrics_dict: Dict[str, Dict[str, Any]],
    top_category: str = None,
    issues: str = ""
) -> Tuple[str, bool]:
    """
    Genera narrativa ejecutiva completa de insights de una cuenta.
    
    Útil para reportes ejecutivos que necesitan interpretación humana.
    
    Args:
        account_name: Nombre de la cuenta (ej: "Colegio Marista Sede Centro")
        metrics_dict: Dict con estructura:
            {
                "followers": {"current": 5000, "change": 12.5},
                "engagement_rate": {"current": 3.5, "change": -5.2},
                "reach": {"current": 25000, "change": 8.0}
            }
        top_category: Categoría top de contenido (ej: "académico")
        issues: Descripción de problemas detectados
    
    Returns:
        Tuple[str, bool]: (narrativa_completa, fue_generado_por_ollama)
    
    Ejemplo:
        narrative, used_ollama = generate_insights_narrative(
            "Colegio Marista",
            {
                "followers": {"current": 5000, "change": 12.5},
                "engagement_rate": {"current": 3.5, "change": -5.2}
            },
            top_category="académico",
            issues="Comentarios negativos sobre cafetería"
        )
    """
    # Construir contexto de métricas
    metrics_summary = []
    for metric_name, values in metrics_dict.items():
        current = values.get("current", 0)
        change = values.get("change", 0)
        metrics_summary.append(f"{metric_name}: {current} ({change:+.1f}%)")
    
    context = "\n".join(metrics_summary)
    if top_category:
        context += f"\nCategoría top: {top_category}"
    if issues:
        context += f"\nProblemas: {issues}"
    
    prompt = f"""Basándote en el desempeño de {account_name} en redes sociales, genera un resumen ejecutivo de 3-4 párrafos que capture los hallazgos clave.

Datos del período:
{context}

Sé conciso, accionable y destaca solo insights relevantes. Explica el significado de los números, no solo repitas cifras."""
    
    # Llamar a Ollama directamente
    response = ollama_provider._call_ollama(prompt)
    was_ollama = response is not None
    
    if not response:
        # Fallback simple
        direction = "positivo" if sum(v.get("change", 0) for v in metrics_dict.values()) > 0 else "desafiante"
        response = f"{account_name} mostró un período {direction} con cambios variados en sus métricas principales."
        logger.info("Usando narrativa heurística (Ollama no disponible)")
    else:
        logger.info(f"Narrativa ejecutiva generada con Ollama ({len(response)} chars)")
    
    return response, was_ollama


def generate_recommendations_for_account(
    account_name: str,
    avg_followers: int,
    engagement_rate: float,
    top_category: str,
    top_category_pct: float,
    negative_comments_pct: float,
    top_terms: str,
    issues: str = ""
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Genera recomendaciones personalizadas basadas en datos (versión mejorada con Ollama).
    
    Útil para secciones "Recomendaciones" en reportes.
    
    Args:
        account_name: Nombre de la cuenta
        avg_followers: Promedio de seguidores
        engagement_rate: Tasa de engagement en %
        top_category: Categoría top de contenido
        top_category_pct: % de contenido en categoría top
        negative_comments_pct: % de comentarios negativos
        top_terms: Términos más mencionados (ej: "cafetería, costo, profesores")
        issues: Problemas detectados
    
    Returns:
        Tuple[List[Dict], bool]: (recomendaciones, fue_generado_por_ollama)
        
        Estructura de cada recomendación:
        {
            "action": "Accionar específica",
            "rationale": "Por qué es importante",
            "impact": "bajo|medio|alto",
            "priority": 1|2|3
        }
    """
    recommendations, was_ollama = ollama_provider.generate_recommendations(
        account_name=account_name,
        avg_followers=avg_followers,
        engagement_rate=engagement_rate,
        top_category=top_category,
        top_category_pct=top_category_pct,
        negative_comments_pct=negative_comments_pct,
        top_terms=top_terms,
        issues=issues
    )
    
    if not recommendations and not was_ollama:
        logger.warning(f"No se generaron recomendaciones para {account_name}")
    
    # Convertir RecommendationItem a dict para fácil serialización
    result = [
        {
            "action": rec.action,
            "rationale": rec.rationale,
            "impact": rec.impact,
            "priority": rec.priority
        }
        for rec in recommendations
    ]
    
    logger.info(f"Generadas {len(result)} recomendaciones ({' Ollama' if was_ollama else ' Heurísticas'})")
    
    return result, was_ollama


__all__ = [
    "generate_summary_with_ollama",
    "generate_insights_narrative",
    "generate_recommendations_for_account",
]
