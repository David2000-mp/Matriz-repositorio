"""
Utilidades de mineria de textos (100% local y gratuito).

Incluye:
- Limpieza y tokenizacion basica para espanol.
- Sentimiento por lexicon (reglas) sin APIs externas.
- Extraccion de palabras clave por frecuencia.
- Agregaciones para dashboards de texto.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Iterable

import pandas as pd

SPANISH_STOPWORDS = {
    "a", "al", "algo", "algun", "alguna", "algunas", "alguno", "algunos", "alli", "ambos",
    "ante", "antes", "aquel", "aquella", "aquellas", "aquello", "aquellos", "aqui", "asi",
    "aun", "aunque", "bajo", "bien", "cada", "casi", "como", "con", "contra", "cual",
    "cuales", "cualquier", "cuando", "cuanto", "de", "debe", "deben", "debido", "del", "desde",
    "donde", "dos", "el", "ella", "ellas", "ello", "ellos", "en", "entre", "era", "eramos",
    "eran", "eres", "es", "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estaban",
    "estado", "estais", "estamos", "estan", "estar", "estas", "este", "esto", "estos", "fue",
    "fueron", "ha", "hace", "hacia", "han", "hasta", "hay", "la", "las", "le", "les", "lo",
    "los", "mas", "me", "mi", "mientras", "mis", "mucho", "muy", "nada", "ni", "no", "nos",
    "nosotros", "nuestra", "nuestro", "nuevamente", "o", "os", "otra", "otras", "otro", "otros",
    "para", "pero", "poco", "por", "porque", "que", "quien", "quienes", "se", "sea", "segun",
    "ser", "si", "siempre", "sin", "sobre", "son", "su", "sus", "tal", "tambien", "te", "tener",
    "tiene", "tienen", "todo", "todos", "tu", "tus", "un", "una", "unas", "uno", "unos", "usted",
    "ustedes", "ya",
    # Ruido comun del dominio/redes
    "https", "http", "www", "com", "instagram", "facebook", "tiktok", "twitter", "post", "posts",
    "publicacion", "publicaciones", "contenido", "contenidos", "comentario", "comentarios",
}

POSITIVE_WORDS = {
    "bueno", "excelente", "positivo", "crece", "mejor", "mejora", "alto", "fuerte", "exito",
    "logro", "logros", "relevante", "efectivo", "engagement", "apoyo", "participacion", "viral",
    "funciona", "fortaleza", "oportunidad", "avance", "incremento", "aumento", "activo",
}

NEGATIVE_WORDS = {
    "malo", "negativo", "bajo", "cae", "caida", "debil", "problema", "errores", "error", "riesgo",
    "critico", "alerta", "falla", "falla", "ruido", "queja", "quejas", "disminucion", "abandono",
    "inconsistente", "manual", "captura", "pendiente", "retraso", "sin", "poco", "nulo",
}

TEXT_COLUMNS_DEFAULT = (
    "tema_mas_visto",
    "top_5_publicaciones",
    "comentarios_consolidados",
    "obs_engagement",
    "notas_operacionales",
    "alertas_riesgos",
    "publicacion_destacada",
)


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+", re.UNICODE)


def _to_ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    if not text or text == "nan":
        return ""
    text = _to_ascii_fold(text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_spanish(text: str) -> list[str]:
    if not text:
        return []
    tokens = [tok for tok in TOKEN_RE.findall(text) if len(tok) >= 3]
    return [tok for tok in tokens if tok not in SPANISH_STOPWORDS and not tok.isdigit()]


def sentiment_from_tokens(tokens: Iterable[str]) -> tuple[str, float]:
    token_list = list(tokens)
    if not token_list:
        return "neutral", 0.0

    positive = sum(1 for tok in token_list if tok in POSITIVE_WORDS)
    negative = sum(1 for tok in token_list if tok in NEGATIVE_WORDS)
    score = (positive - negative) / max(1, len(token_list))

    if score >= 0.08:
        return "positivo", float(score)
    if score <= -0.08:
        return "negativo", float(score)
    return "neutral", float(score)


def extract_keywords(tokens: Iterable[str], top_n: int = 5) -> list[str]:
    token_list = list(tokens)
    if not token_list:
        return []
    counts = Counter(token_list)
    return [word for word, _ in counts.most_common(top_n)]


def enrich_text_columns(df: pd.DataFrame, text_columns: tuple[str, ...] = TEXT_COLUMNS_DEFAULT) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    enriched = df.copy()
    for col in text_columns:
        if col not in enriched.columns:
            continue

        normalized = enriched[col].fillna("").astype(str).map(normalize_text)
        tokens_series = normalized.map(tokenize_spanish)

        sentiment_payload = tokens_series.map(sentiment_from_tokens)
        enriched[f"{col}_sentiment"] = sentiment_payload.map(lambda item: item[0])
        enriched[f"{col}_sentiment_score"] = sentiment_payload.map(lambda item: round(item[1], 4))
        enriched[f"{col}_word_count"] = tokens_series.map(len)
        enriched[f"{col}_keywords"] = tokens_series.map(lambda toks: ", ".join(extract_keywords(toks, top_n=5)))

    return enriched


def sentiment_distribution(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    sentiment_col = f"{text_column}_sentiment"
    if sentiment_col not in df.columns:
        return pd.DataFrame(columns=["sentimiento", "total"])

    counts = (
        df[sentiment_col]
        .fillna("neutral")
        .astype(str)
        .str.strip()
        .replace("", "neutral")
        .value_counts()
        .rename_axis("sentimiento")
        .reset_index(name="total")
    )
    return counts


def keyword_frequency(df: pd.DataFrame, text_column: str, top_n: int = 20) -> pd.DataFrame:
    if text_column not in df.columns:
        return pd.DataFrame(columns=["palabra", "total"])

    all_tokens: list[str] = []
    for value in df[text_column].fillna("").astype(str):
        normalized = normalize_text(value)
        all_tokens.extend(tokenize_spanish(normalized))

    if not all_tokens:
        return pd.DataFrame(columns=["palabra", "total"])

    counts = Counter(all_tokens).most_common(top_n)
    return pd.DataFrame(counts, columns=["palabra", "total"])


def sentiment_monthly_trend(df: pd.DataFrame, text_column: str, date_column: str = "fecha") -> pd.DataFrame:
    sentiment_score_col = f"{text_column}_sentiment_score"
    if date_column not in df.columns or sentiment_score_col not in df.columns:
        return pd.DataFrame(columns=["mes", "score_promedio"])

    trend = df[[date_column, sentiment_score_col]].copy()
    trend[date_column] = pd.to_datetime(trend[date_column], errors="coerce")
    trend = trend.dropna(subset=[date_column])
    if trend.empty:
        return pd.DataFrame(columns=["mes", "score_promedio"])

    trend["mes"] = trend[date_column].dt.to_period("M").dt.to_timestamp()
    result = (
        trend.groupby("mes", as_index=False)[sentiment_score_col]
        .mean(numeric_only=True)
        .rename(columns={sentiment_score_col: "score_promedio"})
        .sort_values("mes")
    )
    return result


def build_manual_observations(df: pd.DataFrame, source_col: str = "comentarios_consolidados") -> pd.DataFrame:
    if source_col not in df.columns:
        return pd.DataFrame(columns=["fecha", "entidad", "plataforma", source_col])

    manual_markers = ("manual", "captura", "observacion", "nota", "ajuste", "correccion")
    subset_cols = [col for col in ["fecha", "entidad", "plataforma", source_col] if col in df.columns]
    comments = df[subset_cols].copy()

    normalized = comments[source_col].fillna("").astype(str).map(normalize_text)
    mask = normalized.map(lambda t: any(marker in t for marker in manual_markers))
    result = comments[mask].copy()

    if "fecha" in result.columns:
        result["fecha"] = pd.to_datetime(result["fecha"], errors="coerce")
        result = result.sort_values("fecha", ascending=False)

    return result.head(50)
