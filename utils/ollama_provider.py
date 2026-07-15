"""
Ollama Provider - Proveedor de modelos LLM locales
===================================================
Clase responsable de integración con Ollama para:
- Generación de conclusiones narrativas
- Análisis de sentimiento avanzado (con contexto)
- Clasificación temática flexible
- Generación de recomendaciones personalizadas

Característica clave: FALLBACK AUTOMÁTICO a heurísticas locales si Ollama no responde.
Esto garantiza que la aplicación funcione incluso sin Ollama activado.

Instalación de Ollama:
  1. Descargar desde https://ollama.ai
  2. Iniciar servicio: `ollama serve`
  3. Descargar modelo: `ollama pull mistral` (default, ~4.1GB)
  4. Verificar: `curl http://localhost:11434/api/tags`

Configuración en st.secrets.toml:
  [ollama]
  base_url = "http://localhost:11434"
  model = "mistral"
  timeout = 30
  enabled = true
"""

import streamlit as st
import json
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)

# ===========================
# ENUMS
# ===========================

class SentimentLevel(Enum):
    VERY_NEGATIVE = "muy_negativo"
    NEGATIVE = "negativo"
    NEUTRAL = "neutral"
    POSITIVE = "positivo"
    VERY_POSITIVE = "muy_positivo"


# ===========================
# DATA CLASSES
# ===========================

@dataclass
class SentimentAnalysis:
    """Resultado de análisis de sentimiento."""
    sentiment: SentimentLevel
    confidence: float  # 0.0-1.0
    rationale: str  # Explicación del sentimiento
    lexicon_score: Optional[float] = None  # Score del lexicón (fallback)


@dataclass
class ThemeClassification:
    """Resultado de clasificación temática."""
    primary_theme: str
    secondary_themes: list  # Temas secundarios
    confidence: float  # 0.0-1.0
    rationale: str


@dataclass
class RecommendationItem:
    """Recomendación individual."""
    action: str
    rationale: str  # Por qué es importante
    impact: str  # Impacto esperado (bajo/medio/alto)
    priority: int  # 1 (alta) a 3 (baja)


# ===========================
# PROMPTS TEMPLATES
# ===========================

PROMPTS = {
    "summary": """Basándote en los siguientes datos de red social, genera un resumen ejecutivo en español de 2-3 párrafos que destaque los hallazgos clave.

Datos:
- Métrica: {metric_name}
- Valor actual: {current_value}
- Cambio vs período anterior: {change_pct}%
- Contexto: {context}

Instrucciones:
1. Sé conciso y accionable
2. Destaca solo insights relevantes
3. Usa lenguaje profesional pero accesible
4. NO repitas números; interpreta el significado

Resumen:""",

    "sentiment": """Analiza el sentimiento del siguiente comentario en redes sociales. Considera contexto, sarcasmo y matices.

Comentario: "{text}"

Proporciona respuesta en JSON con esta estructura:
{{
  "sentiment": "muy_negativo|negativo|neutral|positivo|muy_positivo",
  "confidence": 0.0-1.0,
  "rationale": "Explicación breve de por qué tiene este sentimiento"
}}

Respuesta JSON:""",

    "theme": """Clasifica el siguiente contenido en temas relevantes para una institución educativa.

Título: {title}
Descripción: {description}

Temas posibles: académico, deportes, cultura, administración, bienestar, comunicación, eventos, otro

Proporciona respuesta en JSON:
{{
  "primary_theme": "tema_principal",
  "secondary_themes": ["tema_secundario1", "tema_secundario2"],
  "confidence": 0.0-1.0,
  "rationale": "Justificación breve"
}}

Respuesta JSON:""",

    "recommendation": """Basándote en los datos de desempeño de la cuenta {account_name}, genera 3-5 recomendaciones accionables.

Datos últimas 4 semanas:
- Promedio de seguidores: {avg_followers}
- Engagement rate: {engagement_rate}%
- Top categoría: {top_category} ({top_category_pct}%)
- Comentarios negativos: {negative_comments}%
- Términos más mencionados: {top_terms}

Problemas detectados: {issues}

Proporciona recomendaciones en JSON:
{{
  "recommendations": [
    {{
      "action": "Acción específica a tomar",
      "rationale": "Por qué es importante",
      "impact": "bajo|medio|alto",
      "priority": 1|2|3
    }}
  ]
}}

Respuesta JSON:"""
}


# ===========================
# OLLAMA PROVIDER
# ===========================

class OllamaProvider:
    """
    Proveedor centralizado de Ollama para CHAMPILEAKS.
    - Gestiona conexión a Ollama local
    - Fallback automático a heurísticas si falla
    - Caché de respuestas frecuentes
    - Logging detallado
    """

    def __init__(self, base_url: str = None, model: str = None, timeout: int = 30):
        """
        Inicializa el provider con configuración desde st.secrets o parámetros.

        Args:
            base_url: URL base de Ollama (default: http://localhost:11434)
            model: Modelo a usar (default: mistral)
            timeout: Timeout en segundos (default: 30)
        """
        # Cargar configuración
        try:
            if st.secrets and "ollama" in st.secrets:
                config = st.secrets["ollama"]
                self.base_url = base_url or config.get("base_url", "http://localhost:11434")
                self.model = model or config.get("model", "mistral")
                self.timeout = timeout or config.get("timeout", 30)
                self.enabled = config.get("enabled", True)
            else:
                self.base_url = base_url or "http://localhost:11434"
                self.model = model or "mistral"
                self.timeout = timeout
                self.enabled = True
        except Exception as e:
            logger.warning(f"No se pudo cargar configuración de st.secrets: {e}. Usando valores por defecto.")
            self.base_url = base_url or "http://localhost:11434"
            self.model = model or "mistral"
            self.timeout = timeout
            self.enabled = True

        self._client = None
        self._is_available = None
        self._response_cache = {}

        logger.info(f"OllamaProvider inicializado: {self.base_url}, modelo={self.model}, timeout={self.timeout}s")

    def _read_cache_entry(self, cache_key: str) -> Optional[Tuple[Any, bool]]:
        """Lee entrada de caché manteniendo compatibilidad con formato legado."""
        if cache_key not in self._response_cache:
            return None

        cached = self._response_cache[cache_key]
        if isinstance(cached, tuple) and len(cached) == 2:
            return cached[0], bool(cached[1])

        # Compatibilidad hacia atrás: entradas antiguas no guardaban bandera.
        return cached, True

    def _write_cache_entry(self, cache_key: str, value: Any, used_ollama: bool) -> None:
        """Escribe entrada de caché en formato uniforme."""
        self._response_cache[cache_key] = (value, used_ollama)

    def _extract_json_payload(self, response: str) -> Optional[Dict[str, Any]]:
        """Intenta extraer un objeto JSON aunque venga envuelto en texto o code fences."""
        if not response:
            return None

        candidates = []
        raw = response.strip()
        if raw:
            candidates.append(raw)

        if "```" in raw:
            chunks = [chunk.strip() for chunk in raw.split("```") if chunk.strip()]
            for chunk in chunks:
                if chunk.lower().startswith("json"):
                    chunk = chunk[4:].strip()
                if chunk:
                    candidates.append(chunk)

        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidates.append(raw[start:end + 1].strip())

        for candidate in candidates:
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue

        return None

    def _parse_confidence(self, value: Any, default: float = 0.7) -> float:
        """Convierte confidence a float en [0, 1] con fallback seguro."""
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            confidence = default

        if confidence < 0:
            return 0.0
        if confidence > 1:
            return 1.0
        return confidence

    def _normalize_sentiment_level(self, raw_value: Any) -> Optional[SentimentLevel]:
        """Normaliza etiquetas de sentimiento provenientes del LLM."""
        if raw_value is None:
            return None

        normalized = str(raw_value).strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "muy_negativo": SentimentLevel.VERY_NEGATIVE,
            "very_negative": SentimentLevel.VERY_NEGATIVE,
            "negativo": SentimentLevel.NEGATIVE,
            "negative": SentimentLevel.NEGATIVE,
            "neutral": SentimentLevel.NEUTRAL,
            "positivo": SentimentLevel.POSITIVE,
            "positive": SentimentLevel.POSITIVE,
            "muy_positivo": SentimentLevel.VERY_POSITIVE,
            "very_positive": SentimentLevel.VERY_POSITIVE,
        }
        return aliases.get(normalized)

    def _normalize_theme(self, raw_theme: Any) -> str:
        """Normaliza nombres de temas para evitar variaciones ortográficas."""
        normalized = str(raw_theme or "").strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        aliases = {
            "academico": "académico",
            "deportes": "deportes",
            "cultura": "cultura",
            "administracion": "administración",
            "bienestar": "bienestar",
            "comunicacion": "comunicación",
            "eventos": "eventos",
            "otro": "otro",
            "otros": "otro",
            "other": "otro",
        }
        return aliases.get(normalized, str(raw_theme or "").strip().lower())

    def _get_client(self):
        """Obtiene o crea el cliente de Ollama (lazy loading)."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
                logger.info("Cliente Ollama creado exitosamente")
            except ImportError:
                logger.error("Módulo 'ollama' no instalado. Instala con: pip install ollama")
                self._client = False
            except Exception as e:
                logger.error(f"Error creando cliente Ollama: {e}")
                self._client = False

        return self._client if self._client else None

    def is_available(self) -> bool:
        """
        Verifica si Ollama está disponible sin hacer llamadas costosas.
        
        Returns:
            bool: True si Ollama responde, False si no está disponible
        """
        if not self.enabled:
            logger.info("Ollama deshabilitado en configuración")
            return False

        if self._is_available is not None:
            return self._is_available

        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self._is_available = response.status_code == 200
            if self._is_available:
                logger.info("Ollama está disponible y respondiendo")
            else:
                logger.warning(f"Ollama no responde (status {response.status_code})")
            return self._is_available
        except Exception as e:
            logger.warning(f"Ollama no disponible: {e}. Usando fallback a heurísticas.")
            self._is_available = False
            return False

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Llama a Ollama con el prompt dado.

        Args:
            prompt: Prompt a enviar a Ollama

        Returns:
            Respuesta de Ollama o None si falla
        """
        if not self.is_available():
            return None

        try:
            client = self._get_client()
            if not client:
                return None

            response = client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.3,  # Bajo para respuestas consistentes
                    "top_p": 0.9,
                    "top_k": 40,
                }
            )

            result = response.get("response", "").strip()
            logger.debug(f"Ollama respondió exitosamente ({len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"Error llamando a Ollama: {e}")
            return None

    # ===========================
    # MÉTODOS PÚBLICOS
    # ===========================

    def generate_summary(self, metric_name: str, current_value: float, change_pct: float, context: str = "") -> Tuple[str, bool]:
        """
        Genera un resumen narrativo de una métrica.

        Args:
            metric_name: Nombre de la métrica (ej: "Engagement Rate")
            current_value: Valor actual
            change_pct: Cambio porcentual vs período anterior
            context: Contexto adicional

        Returns:
            Tuple[str, bool]: (texto_resumen, fue_generado_por_ollama)
        """
        cache_key = f"summary:{metric_name}:{current_value}:{change_pct}"
        cached = self._read_cache_entry(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit: {cache_key}")
            return cached

        prompt = PROMPTS["summary"].format(
            metric_name=metric_name,
            current_value=current_value,
            change_pct=change_pct,
            context=context or "(sin contexto adicional)"
        )

        response = self._call_ollama(prompt)
        used_ollama = response is not None

        if not response:
            # FALLBACK: resumen heurístico simple
            direction = "aumentó" if change_pct > 0 else "disminuyó" if change_pct < 0 else "se mantuvo"
            response = f"La métrica '{metric_name}' {direction} un {abs(change_pct):.1f}% con respecto al período anterior, llegando a {current_value}."
            logger.info("Usando resumen heurístico (fallback)")

        self._write_cache_entry(cache_key, response, used_ollama)
        return response, used_ollama

    def classify_sentiment(self, text: str) -> Tuple[SentimentAnalysis, bool]:
        """
        Clasifica sentimiento de un comentario con contexto avanzado.

        Args:
            text: Texto del comentario

        Returns:
            Tuple[SentimentAnalysis, bool]: (análisis, fue_generado_por_ollama)
        """
        cache_key = f"sentiment:{hash(text)}"
        cached = self._read_cache_entry(cache_key)
        if cached is not None:
            return cached

        prompt = PROMPTS["sentiment"].format(text=text[:500])  # Limitar a 500 chars
        response = self._call_ollama(prompt)

        if response:
            data = self._extract_json_payload(response)
            if data:
                sentiment = self._normalize_sentiment_level(data.get("sentiment"))
                if sentiment is not None:
                    analysis = SentimentAnalysis(
                        sentiment=sentiment,
                        confidence=self._parse_confidence(data.get("confidence", 0.7), default=0.7),
                        rationale=str(data.get("rationale", "")).strip() or "Clasificación generada por Ollama.",
                        lexicon_score=None
                    )
                    self._write_cache_entry(cache_key, analysis, True)
                    return analysis, True
            logger.warning("Error parseando respuesta Ollama. Usando fallback.")

        # FALLBACK: usar heurísticas simples basadas en palabras clave
        analysis = self._classify_sentiment_heuristic(text)
        logger.info("Usando clasificación heurística de sentimiento (fallback)")
        self._write_cache_entry(cache_key, analysis, False)
        return analysis, False

    def classify_topic(self, title: str, description: str = "") -> Tuple[ThemeClassification, bool]:
        """
        Clasifica tema de contenido de forma flexible.

        Args:
            title: Título del contenido
            description: Descripción adicional

        Returns:
            Tuple[ThemeClassification, bool]: (clasificación, fue_generado_por_ollama)
        """
        cache_key = f"theme:{hash(title + description)}"
        cached = self._read_cache_entry(cache_key)
        if cached is not None:
            return cached

        prompt = PROMPTS["theme"].format(
            title=title[:200],
            description=description[:200]
        )
        response = self._call_ollama(prompt)

        if response:
            data = self._extract_json_payload(response)
            if data and data.get("primary_theme"):
                primary_theme = self._normalize_theme(data.get("primary_theme"))
                secondary_themes = [
                    self._normalize_theme(theme)
                    for theme in data.get("secondary_themes", [])
                    if str(theme).strip()
                ]
                secondary_themes = [theme for theme in secondary_themes if theme != primary_theme][:2]

                classification = ThemeClassification(
                    primary_theme=primary_theme,
                    secondary_themes=secondary_themes,
                    confidence=self._parse_confidence(data.get("confidence", 0.7), default=0.7),
                    rationale=str(data.get("rationale", "")).strip() or "Clasificación generada por Ollama."
                )
                self._write_cache_entry(cache_key, classification, True)
                return classification, True
            logger.warning("Error parseando clasificación temática. Usando fallback.")

        # FALLBACK: usar categorías predefinidas
        classification = self._classify_topic_heuristic(title, description)
        logger.info("Usando clasificación temática heurística (fallback)")
        self._write_cache_entry(cache_key, classification, False)
        return classification, False

    def generate_recommendations(self, account_name: str, avg_followers: int, engagement_rate: float,
                                 top_category: str, top_category_pct: float, negative_comments_pct: float,
                                 top_terms: str, issues: str = "") -> Tuple[list, bool]:
        """
        Genera recomendaciones personalizadas basadas en datos.

        Args:
            account_name: Nombre de la cuenta
            avg_followers: Promedio de seguidores
            engagement_rate: Tasa de engagement en %
            top_category: Categoría top (ej: "academico")
            top_category_pct: Porcentaje de top categoría
            negative_comments_pct: Porcentaje de comentarios negativos
            top_terms: Términos más mencionados (comma-separated)
            issues: Descripción de problemas detectados

        Returns:
            Tuple[list, bool]: (recomendaciones, fue_generado_por_ollama)
        """
        cache_key = f"recs:{account_name}:{engagement_rate}:{negative_comments_pct}:{top_category}:{top_terms[:50]}"
        cached = self._read_cache_entry(cache_key)
        if cached is not None:
            return cached

        prompt = PROMPTS["recommendation"].format(
            account_name=account_name,
            avg_followers=avg_followers,
            engagement_rate=engagement_rate,
            top_category=top_category,
            top_category_pct=top_category_pct,
            negative_comments=negative_comments_pct,
            top_terms=top_terms[:100],  # Limitar
            issues=issues or "(ninguno detectado)"
        )
        response = self._call_ollama(prompt)

        recommendations = []
        if response:
            data = self._extract_json_payload(response)
            if data:
                for rec_data in data.get("recommendations", []):
                    if not isinstance(rec_data, dict):
                        continue

                    action = str(rec_data.get("action", "")).strip()
                    if not action:
                        continue

                    try:
                        priority = int(rec_data.get("priority", 2))
                    except (TypeError, ValueError):
                        priority = 2
                    priority = max(1, min(3, priority))

                    rec = RecommendationItem(
                        action=action,
                        rationale=str(rec_data.get("rationale", "")).strip(),
                        impact=str(rec_data.get("impact", "medio")).strip().lower() or "medio",
                        priority=priority
                    )
                    recommendations.append(rec)

            if recommendations:
                logger.info(f"Generadas {len(recommendations)} recomendaciones con Ollama")
                self._write_cache_entry(cache_key, recommendations, True)
                return recommendations, True

            logger.warning("Error parseando recomendaciones. Usando fallback.")

        # FALLBACK: recomendaciones simples basadas en heurísticas
        recommendations = self._generate_recommendations_heuristic(
            account_name, engagement_rate, negative_comments_pct, issues
        )
        logger.info("Usando recomendaciones heurísticas (fallback)")
        self._write_cache_entry(cache_key, recommendations, False)
        return recommendations, False

    # ===========================
    # MÉTODOS FALLBACK (HEURÍSTICAS)
    # ===========================

    def _classify_sentiment_heuristic(self, text: str) -> SentimentAnalysis:
        """Clasificación de sentimiento por palabras clave."""
        text_lower = text.lower()

        # Palabras positivas
        positive_words = ["excelente", "bueno", "maravilloso", "feliz", "amor", "perfecto",
                         "increíble", "gracias", "admirable", "progreso", "éxito"]
        # Palabras negativas
        negative_words = ["malo", "terrible", "horrible", "odio", "asco", "triste", "decepción",
                         "fraude", "incompetencia", "falla", "problema", "crítico"]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if neg_count > pos_count:
            sentiment = SentimentLevel.NEGATIVE if neg_count > 2 else SentimentLevel.NEUTRAL
            confidence = min(0.3 + neg_count * 0.15, 0.95)
        elif pos_count > neg_count:
            sentiment = SentimentLevel.POSITIVE if pos_count > 2 else SentimentLevel.NEUTRAL
            confidence = min(0.3 + pos_count * 0.15, 0.95)
        else:
            sentiment = SentimentLevel.NEUTRAL
            confidence = 0.5

        return SentimentAnalysis(
            sentiment=sentiment,
            confidence=confidence,
            rationale=f"Heurística: {pos_count} palabras positivas, {neg_count} palabras negativas",
            lexicon_score=confidence
        )

    def _classify_topic_heuristic(self, title: str, description: str) -> ThemeClassification:
        """Clasificación temática por palabras clave."""
        text = (title + " " + description).lower()

        themes = {
            "académico": ["clase", "estudiante", "curso", "examen", "aprendizaje", "educación"],
            "deportes": ["deporte", "equipo", "gol", "campeonato", "atleta", "cancha"],
            "cultura": ["arte", "música", "teatro", "danza", "cultura", "presentación"],
            "administración": ["junta", "directiva", "norma", "reglamento", "políticas"],
            "bienestar": ["salud", "consejería", "bienestar", "psicología", "nutrición"],
            "comunicación": ["comunicado", "noticia", "anuncio", "información"],
            "eventos": ["evento", "actividad", "congreso", "seminario", "encuentro"],
        }

        scores = {}
        for theme, keywords in themes.items():
            scores[theme] = sum(1 for kw in keywords if kw in text)

        max_score = max(scores.values()) if scores else 0
        primary = max(scores, key=scores.get) if max_score > 0 else "otro"
        secondary = [t for t, s in scores.items() if s > 0 and t != primary][:2]

        confidence = min(0.5 + max_score * 0.1, 0.95) if max_score > 0 else 0.4

        return ThemeClassification(
            primary_theme=primary,
            secondary_themes=secondary,
            confidence=confidence,
            rationale=f"Heurística basada en palabras clave ({max_score} matches)"
        )

    def _generate_recommendations_heuristic(self, account_name: str, engagement_rate: float,
                                            negative_comments_pct: float, issues: str) -> list:
        """Genera recomendaciones por heurísticas simples."""
        recommendations = []

        if engagement_rate < 2.0:
            recommendations.append(RecommendationItem(
                action="Aumentar frecuencia de publicaciones",
                rationale="Engagement bajo (<2%) indica falta de frecuencia o relevancia",
                impact="alto",
                priority=1
            ))

        if negative_comments_pct > 20:
            recommendations.append(RecommendationItem(
                action="Revisar tono y relevancia del contenido",
                rationale=f"Alto porcentaje de comentarios negativos ({negative_comments_pct}%)",
                impact="alto",
                priority=1
            ))

        recommendations.append(RecommendationItem(
            action="Analizar comentarios de fans para identificar tendencias",
            rationale="Comprensión de audiencia es clave para crecimiento sostenible",
            impact="medio",
            priority=2
        ))

        return recommendations

    # ===========================
    # UTILIDADES
    # ===========================

    def clear_cache(self):
        """Limpia caché de respuestas."""
        self._response_cache.clear()
        logger.info("Caché de Ollama limpiado")

    def get_cache_stats(self) -> Dict:
        """Retorna estadísticas de caché."""
        return {
            "cache_size": len(self._response_cache),
            "ollama_available": self.is_available(),
            "model": self.model,
            "base_url": self.base_url,
        }


# ===========================
# INSTANCIA GLOBAL SINGLETON
# ===========================

ollama_provider = OllamaProvider()

__all__ = [
    "OllamaProvider",
    "ollama_provider",
    "SentimentAnalysis",
    "SentimentLevel",
    "ThemeClassification",
    "RecommendationItem",
]
