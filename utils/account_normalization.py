"""Helpers para normalizar plataformas y cuentas sociales."""

from urllib.parse import parse_qs, unquote, urlparse


def normalize_platform_name(platform: str) -> str:
    """Normaliza nombres de plataforma a estándares de visualización."""
    raw = str(platform or "").strip().lower()
    mapping = {
        "instagram": "Instagram",
        "facebook": "Facebook",
        "facebook page": "Facebook",
        "tiktok": "TikTok",
        "tik tok": "TikTok",
        "twitter": "Twitter",
        "x": "X",
        "linkedin": "LinkedIn",
        "youtube": "YouTube",
        "threads": "Threads",
        "bluesky": "BlueSky",
    }
    return mapping.get(raw, raw.title()) if raw else ""


def normalize_social_user(usuario_red: str, platform: str = "") -> str:
    """Reduce un usuario/URL a un identificador canónico estable.

    Ejemplos:
    - `https://www.facebook.com/MaristasIH/?locale=es_LA` -> `maristasih`
    - `@umaristamx` -> `umaristamx`
    - `https://www.tiktok.com/@cuenta` -> `cuenta`
    """
    raw = str(usuario_red or "").strip()
    if not raw or raw.lower() in {"nan", "none", "null"}:
        return ""

    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        path_parts = [part for part in parsed.path.split("/") if part and part not in {"pages", "pg"}]
        raw = path_parts[-1] if path_parts else ""
        if not raw and parsed.query:
            raw = parse_qs(parsed.query).get("q", [""])[0]
        raw = unquote(raw)

    raw = raw.strip().rstrip("/")
    raw = raw.split("?")[0].split("#")[0].strip()

    if "/" in raw:
        parts = [part for part in raw.split("/") if part]
        raw = parts[-1] if parts else raw

    if str(platform or "").strip().lower() == "tiktok":
        raw = raw.lstrip("@")

    return raw.lstrip("@").strip().lower()


def build_account_key(entidad: str, plataforma: str, usuario_red: str = "") -> str:
    """Genera una llave estable para identificar una cuenta social."""
    entidad_key = str(entidad or "").strip().lower()
    plataforma_key = normalize_platform_name(plataforma).strip().lower()
    usuario_key = normalize_social_user(usuario_red, plataforma)

    parts = [entidad_key, plataforma_key]
    if usuario_key:
        parts.append(usuario_key)

    return "|".join(parts)
