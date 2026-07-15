"""
Extensión de Content Analyzer con integración Ollama
======================================================
Funciones mejoradas para clasificación temática flexible.

Este módulo EXTIENDE las funciones existentes sin romper compatibilidad:
- classify_content_with_ollama: versión mejorada que usa Ollama
- detect_themes_with_ollama: detección automática de nuevos temas

Las funciones originales siguen funcionando sin cambios.
"""

from typing import Tuple, Dict, List, Any
from utils.ollama_provider import ollama_provider, ThemeClassification
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)


def classify_content_with_ollama(
    title: str,
    description: str = "",
    hardcoded_categories: List[str] = None
) -> Tuple[str, List[str], float, bool]:
    """
    Clasifica contenido con detección automática de temas usando Ollama.
    
    Estrategia:
    1. Si Ollama disponible, usar clasificación flexible (puede detectar nuevos temas)
    2. Si Ollama falla, usar categorías hardcodeadas
    
    Args:
        title: Título del contenido
        description: Descripción o texto adicional
        hardcoded_categories: Lista de categorías permitidas (fallback)
    
    Returns:
        Tuple[str, List[str], float, bool]: (categoria_principal, categorias_secundarias, confianza, usado_ollama)
    
    Ejemplo:
        primary, secondary, conf, used_ollama = classify_content_with_ollama(
            title="Nuevo laboratorio de robótica",
            description="Inauguramos moderno laboratorio...",
            hardcoded_categories=["académico", "eventos", "innovación"]
        )
        # -> ("académico", ["innovación", "eventos"], 0.92, True)
    """
    if not title and not description:
        return "Otro", [], 0.0, False
    
    # Intentar con Ollama
    classification, was_ollama = ollama_provider.classify_topic(title, description)
    
    if was_ollama and classification.primary_theme:
        logger.debug(f"Tema Ollama: {classification.primary_theme} (conf: {classification.confidence:.2f})")
        logger.info(f"Usado Ollama para clasificar: '{title[:50]}...'")
        
        return (
            classification.primary_theme,
            classification.secondary_themes,
            classification.confidence,
            True
        )
    else:
        # Fallback a categorías simples o hardcodeadas
        if hardcoded_categories is None:
            hardcoded_categories = ["académico", "deportes", "cultura", "administración",
                                   "bienestar", "comunicación", "eventos", "otro"]
        
        logger.debug(f"Fallback a categorías hardcodeadas para: '{title[:50]}...'")
        
        # Búsqueda simple en título/descripción
        text = (title + " " + description).lower()
        matched = [cat for cat in hardcoded_categories if cat.lower() in text]
        
        primary = matched[0] if matched else "Otro"
        secondary = matched[1:] if len(matched) > 1 else []
        confidence = 0.5 if matched else 0.3
        
        return primary, secondary, confidence, False


def detect_emerging_themes(
    contents_df: pd.DataFrame,
    title_column: str = "titulo",
    description_column: str = "descripcion",
    sample_size: int = 10
) -> Tuple[Dict[str, int], bool]:
    """
    Detecta temas emergentes (nuevos) no contemplados en categorías hardcodeadas.
    
    Útil para análisis de trends y evolución de contenido en el tiempo.
    
    Args:
        contents_df: DataFrame con contenidos
        title_column: Nombre de columna de títulos
        description_column: Nombre de columna de descripciones
        sample_size: Cantidad de posts a analizar (para no sobrecargar Ollama)
    
    Returns:
        Tuple[Dict[str, int], bool]: (temas_emergentes_con_freq, fue_usado_ollama)
        
        Estructura: {"tema1": 3, "tema2": 2, ...}
    """
    if contents_df.empty:
        return {}, False
    
    # Tomar muestra
    sample = contents_df.sample(min(sample_size, len(contents_df)))
    
    emerging_themes = {}
    was_ollama = False
    
    for idx, row in sample.iterrows():
        title = str(row.get(title_column, ""))
        desc = str(row.get(description_column, ""))
        
        if not title and not desc:
            continue
        
        classification, used = ollama_provider.classify_topic(title, desc)
        
        if used and classification.secondary_themes:
            was_ollama = True
            
            # Registrar temas secundarios como potencialmente nuevos
            for theme in classification.secondary_themes:
                if theme not in ["otro", "otro/diversos"]:
                    emerging_themes[theme] = emerging_themes.get(theme, 0) + 1
    
    if emerging_themes:
        logger.info(f"Temas emergentes detectados: {emerging_themes}")
    
    return emerging_themes, was_ollama


def enrich_content_with_themes(
    contents_df: pd.DataFrame,
    title_column: str = "titulo",
    description_column: str = "descripcion"
) -> pd.DataFrame:
    """
    Enriquece DataFrame de contenidos con clasificación temática mejorada.
    
    Agrega columnas:
    - tema_principal
    - temas_secundarios (JSON list o string comma-separated)
    - tema_confianza (0.0-1.0)
    - tema_usado_ollama (True/False para auditoria)
    
    Args:
        contents_df: DataFrame con contenidos
        title_column: Columna de títulos
        description_column: Columna de descripciones
    
    Returns:
        DataFrame enriquecido con columnas temáticas
    """
    enriched = contents_df.copy()
    
    logger.info(f"Iniciando enriquecimiento temático para {len(enriched)} contenidos...")
    
    # Aplicar clasificación
    def classify_row(row):
        title = str(row.get(title_column, ""))
        desc = str(row.get(description_column, ""))
        return classify_content_with_ollama(title, desc)
    
    results = enriched.apply(classify_row, axis=1, result_type="expand")
    
    enriched["tema_principal"] = results[0]
    enriched["temas_secundarios"] = results[1].apply(lambda x: ",".join(x) if x else "")
    enriched["tema_confianza"] = results[2]
    enriched["tema_usado_ollama"] = results[3]
    
    # Estadísticas
    ollama_count = enriched["tema_usado_ollama"].sum()
    logger.info(f"Enriquecimiento completo: {ollama_count} de {len(enriched)} usaron Ollama")
    logger.info(f"Distribución de temas:\n{enriched['tema_principal'].value_counts().to_string()}")
    
    return enriched


__all__ = [
    "classify_content_with_ollama",
    "detect_emerging_themes",
    "enrich_content_with_themes",
]
