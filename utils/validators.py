"""
Validadores para formularios de captura de datos.
Validación reactiva de URLs, rangos numéricos y campos requeridos.

Sprint 1 - Week 2: Reducir errores de captura manual con feedback instantáneo
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse


# ============================================
# PATRONES DE VALIDACIÓN DE URLs
# ============================================

SOCIAL_MEDIA_PATTERNS = {
    "Instagram": [
        r"^https?://(www\.)?instagram\.com/[a-zA-Z0-9._]+/?$",
        r"^https?://(www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?$",  # Posts
        r"^@?[a-zA-Z0-9._]+$",  # Solo username
    ],
    "Facebook": [
        r"^https?://(www\.)?facebook\.com/[a-zA-Z0-9.]+/?$",
        r"^https?://(www\.)?fb\.com/[a-zA-Z0-9.]+/?$",
        r"^@?[a-zA-Z0-9.]+$",  # Solo username
    ],
    "TikTok": [
        r"^https?://(www\.)?tiktok\.com/@[a-zA-Z0-9._]+/?$",
        r"^@[a-zA-Z0-9._]+$",  # Username con @
        r"^[a-zA-Z0-9._]+$",  # Username sin @
    ],
    "Twitter": [
        r"^https?://(www\.)?(twitter|x)\.com/[a-zA-Z0-9_]+/?$",
        r"^@?[a-zA-Z0-9_]+$",  # Solo username
    ],
    "LinkedIn": [
        r"^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?$",
        r"^https?://(www\.)?linkedin\.com/company/[a-zA-Z0-9-]+/?$",
        r"^[a-zA-Z0-9-]+$",  # Solo slug
    ],
    "YouTube": [
        r"^https?://(www\.)?youtube\.com/@[a-zA-Z0-9_]+/?$",
        r"^https?://(www\.)?youtube\.com/c/[a-zA-Z0-9_]+/?$",
        r"^https?://(www\.)?youtube\.com/channel/[a-zA-Z0-9_-]+/?$",
        r"^@?[a-zA-Z0-9_]+$",  # Username
    ],
}


# ============================================
# VALIDADORES DE URLs
# ============================================

def validate_social_url(url: str, platform: str) -> Tuple[bool, str]:
    """
    Valida si una URL o username pertenece a una plataforma de redes sociales.
    
    Args:
        url: URL completa o username a validar
        platform: Plataforma ("Instagram", "Facebook", "TikTok", etc.)
    
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
        
    Examples:
        >>> validate_social_url("https://instagram.com/user123", "Instagram")
        (True, "")
        >>> validate_social_url("invalid-url", "Instagram")
        (False, "Formato inválido para Instagram")
    """
    
    if not url or not url.strip():
        return False, "La URL no puede estar vacía"
    
    url = url.strip()
    
    # Obtener patrones para la plataforma
    patterns = SOCIAL_MEDIA_PATTERNS.get(platform, [])
    
    if not patterns:
        # Si no hay patrones específicos, validar que sea una URL válida
        return _is_valid_url(url), "URL inválida" if not _is_valid_url(url) else ""
    
    # Verificar contra cada patrón de la plataforma
    for pattern in patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True, ""
    
    # Si llegamos aquí, no coincide con ningún patrón
    platform_hint = _get_platform_hint(platform)
    return False, f"Formato inválido para {platform}. {platform_hint}"


def _is_valid_url(url: str) -> bool:
    """Valida si una cadena es una URL válida"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) or not url.startswith("http")
    except:
        return False


def _get_platform_hint(platform: str) -> str:
    """Retorna hint de formato esperado por plataforma"""
    hints = {
        "Instagram": "Usa: https://instagram.com/usuario o @usuario",
        "Facebook": "Usa: https://facebook.com/pagina",
        "TikTok": "Usa: https://tiktok.com/@usuario o @usuario",
        "Twitter": "Usa: https://twitter.com/usuario o @usuario",
        "LinkedIn": "Usa: https://linkedin.com/in/usuario o https://linkedin.com/company/empresa",
        "YouTube": "Usa: https://youtube.com/@canal",
    }
    return hints.get(platform, "Verifica el formato de la URL")


# ============================================
# VALIDADORES NUMÉRICOS
# ============================================

def validate_numeric_range(
    value: Optional[float], 
    min_val: float = 0, 
    max_val: Optional[float] = None,
    field_name: str = "Campo"
) -> Tuple[bool, str]:
    """
    Valida si un valor numérico está dentro de un rango permitido.
    
    Args:
        value: Valor a validar (puede ser None)
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido (None = sin límite)
        field_name: Nombre del campo para mensajes de error
    
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
        
    Examples:
        >>> validate_numeric_range(50, 0, 100, "Engagement")
        (True, "")
        >>> validate_numeric_range(150, 0, 100, "Engagement")
        (False, "Engagement debe estar entre 0 y 100")
    """
    
    if value is None:
        return True, ""  # Campos opcionales permiten None
    
    # Validar mínimo
    if value < min_val:
        return False, f"{field_name} debe ser mayor o igual a {min_val}"
    
    # Validar máximo (si existe)
    if max_val is not None and value > max_val:
        return False, f"{field_name} debe estar entre {min_val} y {max_val}"
    
    return True, ""


def validate_followers(value: int) -> Tuple[bool, str]:
    """Valida número de seguidores (debe ser > 0)"""
    if value == 0:
        return False, "El número de seguidores no puede ser 0"
    if value < 0:
        return False, "El número de seguidores debe ser positivo"
    return True, ""


def validate_engagement(value: float) -> Tuple[bool, str]:
    """Valida tasa de engagement (0-100%)"""
    return validate_numeric_range(value, 0.0, 100.0, "Engagement Rate")


def validate_interactions(value: Optional[int]) -> Tuple[bool, str]:
    """Valida número de interacciones (opcional, >= 0 si presente)"""
    if value is None:
        return True, ""
    return validate_numeric_range(value, 0, None, "Interacciones")


# ============================================
# VALIDADORES DE CAMPOS REQUERIDOS
# ============================================

def validate_required(value: Optional[str], field_name: str = "Campo") -> Tuple[bool, str]:
    """
    Valida que un campo requerido no esté vacío.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensaje de error
    
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
    """
    if not value or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} es requerido"
    return True, ""


# ============================================
# VALIDACIÓN DE FORMULARIO COMPLETO
# ============================================

def validate_form(
    entidad: str,
    plataforma: str,
    usuario_red: str,
    seguidores: int,
    engagement_rate: float,
    interacciones: Optional[int] = None,
    me_gusta: Optional[int] = None,
) -> Tuple[bool, list[str]]:
    """
    Valida todos los campos de un formulario de captura.
    
    Returns:
        Tuple[bool, list[str]]: (form_válido, lista_de_errores)
    """
    errors = []
    
    # Validar campos requeridos
    valid, msg = validate_required(entidad, "Institución")
    if not valid:
        errors.append(msg)
    
    valid, msg = validate_required(plataforma, "Plataforma")
    if not valid:
        errors.append(msg)
    
    valid, msg = validate_required(usuario_red, "Usuario/URL")
    if not valid:
        errors.append(msg)
    
    # Validar URL de red social
    if usuario_red and plataforma:
        valid, msg = validate_social_url(usuario_red, plataforma)
        if not valid:
            errors.append(msg)
    
    # Validar campos numéricos
    valid, msg = validate_followers(seguidores)
    if not valid:
        errors.append(msg)
    
    valid, msg = validate_engagement(engagement_rate)
    if not valid:
        errors.append(msg)
    
    if interacciones is not None:
        valid, msg = validate_interactions(interacciones)
        if not valid:
            errors.append(msg)
    
    if me_gusta is not None:
        valid, msg = validate_interactions(me_gusta)  # Misma lógica que interacciones
        if not valid:
            errors.append(msg)
    
    return len(errors) == 0, errors


# ============================================
# HELPERS PARA UI
# ============================================

def get_validation_icon(is_valid: bool) -> str:
    """Retorna emoji para feedback visual de validación"""
    return "✅" if is_valid else "❌"


def get_validation_color(is_valid: bool) -> str:
    """Retorna color para mensaje de validación"""
    return "success" if is_valid else "error"
