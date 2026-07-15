"""
Paquete de utilidades para CHAMPILEAKS.
"""

from .data_manager import (
    conectar_sheets,
    COLEGIOS_MARISTAS,
    save_batch,
    save_comment,
    save_username_editado,
    guardar_datos,
    get_id,
    sync_cuentas_to_sheets,
    load_data,
    load_usernames_editados,
    load_configs,
    load_base_maestra_colegios,
    load_base_demografica_colegios,
    get_reverse_lookup,
    load_comments,
    COLS_CUENTAS,
    COLS_METRICAS,
    COLS_CONFIG,
    COLS_COMENTARIOS,
    COLS_USERNAMES_EDITADOS,
    COLS_BASE_MAESTRA_COLEGIOS,
    COLS_BASE_DEMOGRAFICA_COLEGIOS,
    METRICAS_CSV,
    CUENTAS_CSV,
)

from .helpers import (
    get_image_base64,
    load_image,
    get_banner_css,
    simular,
    generar_reporte_html,
)

from .ollama_provider import (
    ollama_provider,
    OllamaProvider,
    SentimentAnalysis,
    SentimentLevel,
    ThemeClassification,
    RecommendationItem,
)

from .ollama_extensions import (
    classify_sentiment_with_ollama,
    add_sentiment_analysis_with_ollama,
    get_sentiment_with_rationale,
)

from .ollama_extensions_report import (
    generate_summary_with_ollama,
    generate_insights_narrative,
    generate_recommendations_for_account,
)

from .ollama_extensions_content import (
    classify_content_with_ollama,
    detect_emerging_themes,
    enrich_content_with_themes,
)

from . import comment_processor

__all__ = [
    # Data manager
    "conectar_sheets",
    "COLEGIOS_MARISTAS",
    "save_batch",
    "save_comment",
    "save_username_editado",
    "guardar_datos",
    "get_id",
    "sync_cuentas_to_sheets",
    "load_data",
    "load_usernames_editados",
    "load_configs",
    "load_base_maestra_colegios",
    "load_base_demografica_colegios",
    "get_reverse_lookup",
    "load_comments",
    "COLS_CUENTAS",
    "COLS_METRICAS",
    "COLS_CONFIG",
    "COLS_COMENTARIOS",
    "COLS_USERNAMES_EDITADOS",
    "COLS_BASE_MAESTRA_COLEGIOS",
    "COLS_BASE_DEMOGRAFICA_COLEGIOS",
    "METRICAS_CSV",
    "CUENTAS_CSV",
    # Data loader
    # (removed, now imported from data_manager)
    # Helpers
    "get_image_base64",
    "load_image",
    "get_banner_css",
    "simular",
    "generar_reporte_html",
    # Ollama / LLM Integration - Core
    "ollama_provider",
    "OllamaProvider",
    "SentimentAnalysis",
    "SentimentLevel",
    "ThemeClassification",
    "RecommendationItem",
    # Ollama Extensions - Comment Processing
    "classify_sentiment_with_ollama",
    "add_sentiment_analysis_with_ollama",
    "get_sentiment_with_rationale",
    # Ollama Extensions - Report Generation
    "generate_summary_with_ollama",
    "generate_insights_narrative",
    "generate_recommendations_for_account",
    # Ollama Extensions - Content Analysis
    "classify_content_with_ollama",
    "detect_emerging_themes",
    "enrich_content_with_themes",
    # Comment Processing
    "comment_processor",
]
