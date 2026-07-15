"""
Extensión de Comment Processor con integración Ollama
======================================================
Funciones mejoradas que usa Ollama para análisis avanzado, con fallback a heurísticas.

Este módulo EXTIENDE las funciones existentes sin romper compatibilidad:
- classify_sentiment_with_ollama: versión mejorada de classify_sentiment
- add_sentiment_analysis_with_ollama: versión mejorada que usa Ollama

Las funciones originales siguen funcionando sin cambios.
"""

from typing import Tuple
from utils.ollama_provider import ollama_provider, SentimentAnalysis, SentimentLevel
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)


def classify_sentiment_with_ollama(comment: str) -> Tuple[str, int]:
    """
    Clasifica sentimiento usando Ollama (si disponible) con fallback a heurísticas.
    
    Estrategia:
    1. Si Ollama está disponible, usar análisis avanzado (contexto, sarcasmo, matices)
    2. Si Ollama falla o no responde, usar heurísticas locales (palabras clave)
    
    Retorna:
        Tuple[str, int]: (etiqueta_sentimiento, score_1a5)
        
    Ejemplo:
        label, score = classify_sentiment_with_ollama("Me encanta la escuela, aunque el costo es alto")
        # -> ("Positivo", 4) - Ollama entiende que es principalmente positivo
    """
    # Primero, intentar con Ollama
    analysis, was_ollama = ollama_provider.classify_sentiment(comment)
    
    if was_ollama and analysis.rationale:
        logger.debug(f"Sentimiento Ollama: {analysis.sentiment.value} (conf: {analysis.confidence:.2f})")
        
        # Mapear SentimentLevel a label y score
        label_map = {
            SentimentLevel.VERY_NEGATIVE: ("Muy Negativo", 1),
            SentimentLevel.NEGATIVE: ("Negativo", 2),
            SentimentLevel.NEUTRAL: ("Neutral", 3),
            SentimentLevel.POSITIVE: ("Positivo", 4),
            SentimentLevel.VERY_POSITIVE: ("Muy Positivo", 5),
        }
        
        label, score = label_map[analysis.sentiment]
        logger.info(f"Usando sentimiento Ollama para: '{comment[:50]}...'")
        return label, score
    else:
        # Fallback a heurísticas
        logger.debug(f"Fallback a heurísticas (Ollama no disponible)")
        # Importar la función original
        from utils.comment_processor import classify_sentiment
        return classify_sentiment(comment)


def add_sentiment_analysis_with_ollama(
    df: pd.DataFrame,
    comment_column: str = "comentario_original"
) -> pd.DataFrame:
    """
    Agrega análisis de sentimiento mejorado con Ollama a un DataFrame.
    
    Es un wrapper sobre add_sentiment_analysis que usa classify_sentiment_with_ollama.
    
    Args:
        df: DataFrame con comentarios
        comment_column: Nombre de la columna con comentarios
        
    Returns:
        DataFrame con columnas agregadas:
        - sentimiento_etiqueta
        - sentimiento_score
        
    Ejemplo:
        df = pd.read_csv("comentarios.csv")
        df_enriched = add_sentiment_analysis_with_ollama(df)
        print(df_enriched[["comentario_original", "sentimiento_etiqueta"]])
    """
    if comment_column not in df.columns:
        raise ValueError(f"La columna requerida '{comment_column}' no existe en el DataFrame.")
    
    enriched = df.copy()
    logger.info(f"Iniciando análisis de sentimiento con Ollama para {len(enriched)} comentarios...")
    
    # Aplicar función mejorada
    payload = enriched[comment_column].fillna("").astype(str).map(classify_sentiment_with_ollama)
    enriched["sentimiento_etiqueta"] = payload.map(lambda item: item[0])
    enriched["sentimiento_score"] = payload.map(lambda item: int(item[1]))
    
    logger.info(f"Análisis completado. Distribucion:")
    logger.info(enriched["sentimiento_etiqueta"].value_counts().to_string())
    
    return enriched


def get_sentiment_with_rationale(comment: str) -> dict:
    """
    Obtiene sentimiento y explicación detallada (solo disponible con Ollama).
    
    Útil para auditoria y comprensión de decisiones del modelo.
    
    Args:
        comment: Texto del comentario
        
    Returns:
        dict con: {
            "label": str,
            "score": int,
            "rationale": str,  # Explicación del sentimiento
            "confidence": float,  # 0.0-1.0, confianza del análisis
            "used_ollama": bool,  # Si se usó Ollama o fallback a heurísticas
        }
    """
    analysis, was_ollama = ollama_provider.classify_sentiment(comment)
    
    label_map = {
        SentimentLevel.VERY_NEGATIVE: ("Muy Negativo", 1),
        SentimentLevel.NEGATIVE: ("Negativo", 2),
        SentimentLevel.NEUTRAL: ("Neutral", 3),
        SentimentLevel.POSITIVE: ("Positivo", 4),
        SentimentLevel.VERY_POSITIVE: ("Muy Positivo", 5),
    }
    
    label, score = label_map[analysis.sentiment]
    
    return {
        "label": label,
        "score": score,
        "rationale": analysis.rationale,
        "confidence": analysis.confidence,
        "used_ollama": was_ollama,
    }


__all__ = [
    "classify_sentiment_with_ollama",
    "add_sentiment_analysis_with_ollama",
    "get_sentiment_with_rationale",
]
