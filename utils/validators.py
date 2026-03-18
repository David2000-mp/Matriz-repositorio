"""
Validadores para formularios de captura de datos.
Validación reactiva de URLs, rangos numéricos y campos requeridos.

Sprint 1 - Week 2: Reducir errores de captura manual con feedback instantáneo
"""

import re
from typing import Tuple, Optional
import unicodedata
from urllib.parse import urlparse
import pandas as pd

from utils.catalog import COLEGIOS_MARISTAS


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


def check_missing_data_per_institution(df, date_range):
    """
    Valida datos faltantes por institución.
    
    Args:
        df: DataFrame con datos
        date_range: Tupla (start_date, end_date)
    
    Returns:
        List[dict]: Lista de problemas encontrados
    """
    issues = []
    start_date, end_date = date_range
    
    # Filtrar por rango de fechas
    df_filtered = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    
    institutions = df['entidad'].unique()
    platforms = ["Facebook", "Instagram", "TikTok", "Twitter"]
    
    for institution in institutions:
        df_inst = df_filtered[df_filtered['entidad'] == institution]
        
        # Verificar si institución tiene datos
        if df_inst.empty:
            issues.append({
                'institution': institution,
                'platform': 'Todas',
                'issue_type': 'Sin datos en el período'
            })
            continue
        
        # Verificar plataformas
        for platform in platforms:
            df_plat = df_inst[df_inst['plataforma'] == platform]
            if df_plat.empty:
                issues.append({
                    'institution': institution,
                    'platform': platform,
                    'issue_type': 'Sin datos de plataforma'
                })
        
        # Verificar engagement
        if 'engagement_rate' in df_inst.columns:
            engagement_missing = df_inst['engagement_rate'].isna() | (df_inst['engagement_rate'] == 0)
            if engagement_missing.any():
                issues.append({
                    'institution': institution,
                    'platform': 'Varias',
                    'issue_type': 'Engagement faltante o cero'
                })
            
            # Verificar engagement fuera de rango
            engagement_invalid = (df_inst['engagement_rate'] < 0) | (df_inst['engagement_rate'] > 100)
            if engagement_invalid.any():
                issues.append({
                    'institution': institution,
                    'platform': 'Varias',
                    'issue_type': 'Engagement fuera de rango (0-100%)'
                })
    
    return issues


def normalize_report_date_to_month_start(report_date) -> pd.Timestamp:
    """
    Normaliza una fecha al primer día del mes.

    Args:
        report_date: Fecha en formato date/datetime/string

    Returns:
        pd.Timestamp: Fecha normalizada (día 1)
    """
    ts = pd.to_datetime(report_date, errors="coerce")
    if pd.isna(ts):
        raise ValueError("Fecha de reporte inválida")
    return ts.to_period("M").to_timestamp()


def _canonical_institution_name(value: str) -> str:
    """Canoniza nombre de institución para matching robusto."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(without_accents.lower().split())


def get_monthly_pending_institutions(
    df,
    min_platforms: int = 2,
    target_month=None,
    universe_institutions: Optional[list[str]] = None,
) -> dict:
    """
    Genera reporte de instituciones pendientes por cobertura mensual.

    Reglas:
    - Mes objetivo: último mes con datos, salvo que se envíe target_month.
    - Institución completa: plataformas únicas >= min_platforms.
    - Duplicados: institución+plataforma+mes cuentan una sola vez (último registro).

    Args:
        df: DataFrame con columnas entidad, plataforma, fecha
        min_platforms: Umbral mínimo de plataformas para completar
        target_month: Mes objetivo opcional (str YYYY-MM, datetime o Period)
        universe_institutions: Universo opcional de instituciones activas

    Returns:
        dict con target_month, summary y pending_rows
    """
    if min_platforms < 1:
        raise ValueError("min_platforms debe ser >= 1")

    universe = universe_institutions or list(COLEGIOS_MARISTAS.keys())
    universe = [inst for inst in universe if inst]
    canonical_to_display = {
        _canonical_institution_name(inst): inst for inst in universe
    }
    universe_keys = set(canonical_to_display.keys())

    if df is None or getattr(df, "empty", True):
        pending_rows = [
            {
                "institucion": canonical_to_display[key],
                "plataformas_actuales": 0,
                "estado": "Crítico",
            }
            for key in sorted(universe_keys)
        ]
        return {
            "target_month": None,
            "summary": {
                "total_activas": len(universe_keys),
                "completas": 0,
                "pendientes": len(pending_rows),
                "min_platforms": min_platforms,
            },
            "pending_rows": pending_rows,
        }

    required_cols = {"entidad", "plataforma", "fecha"}
    if not required_cols.issubset(set(df.columns)):
        pending_rows = [
            {
                "institucion": canonical_to_display[key],
                "plataformas_actuales": 0,
                "estado": "Crítico",
            }
            for key in sorted(universe_keys)
        ]
        return {
            "target_month": None,
            "summary": {
                "total_activas": len(universe_keys),
                "completas": 0,
                "pendientes": len(pending_rows),
                "min_platforms": min_platforms,
            },
            "pending_rows": pending_rows,
        }

    dfx = df.copy()
    dfx["fecha"] = pd.to_datetime(dfx["fecha"], errors="coerce")
    dfx = dfx.dropna(subset=["fecha"])

    if dfx.empty:
        pending_rows = [
            {
                "institucion": canonical_to_display[key],
                "plataformas_actuales": 0,
                "estado": "Crítico",
            }
            for key in sorted(universe_keys)
        ]
        return {
            "target_month": None,
            "summary": {
                "total_activas": len(universe_keys),
                "completas": 0,
                "pendientes": len(pending_rows),
                "min_platforms": min_platforms,
            },
            "pending_rows": pending_rows,
        }

    dfx["periodo"] = dfx["fecha"].dt.to_period("M")

    if target_month is None:
        target_period = dfx["periodo"].max()
    else:
        target_period = pd.to_datetime(target_month).to_period("M")

    df_month = dfx[dfx["periodo"] == target_period].copy()
    df_month["entidad_key"] = df_month["entidad"].apply(_canonical_institution_name)
    df_month = df_month[df_month["entidad_key"].isin(universe_keys)]

    # Deduplicar por institución+plataforma+mes usando el último registro temporal
    df_month = df_month.sort_values("fecha")
    df_month = df_month.drop_duplicates(
        subset=["entidad_key", "plataforma", "periodo"],
        keep="last",
    )

    counts = (
        df_month.groupby("entidad_key")["plataforma"]
        .nunique()
        .to_dict()
    )

    complete_keys = {k for k, v in counts.items() if v >= min_platforms}
    pending_keys = sorted(universe_keys - complete_keys)

    pending_rows = []
    for key in pending_keys:
        current = int(counts.get(key, 0))
        status = "Crítico" if current == 0 else "Advertencia"
        pending_rows.append(
            {
                "institucion": canonical_to_display[key],
                "plataformas_actuales": current,
                "estado": status,
            }
        )

    return {
        "target_month": str(target_period),
        "summary": {
            "total_activas": len(universe_keys),
            "completas": len(complete_keys),
            "pendientes": len(pending_rows),
            "min_platforms": min_platforms,
        },
        "pending_rows": pending_rows,
    }


# ============================================
# HELPERS PARA UI
# ============================================

def get_validation_icon(is_valid: bool) -> str:
    """Retorna emoji para feedback visual de validación"""
    return "✅" if is_valid else "❌"


def get_validation_color(is_valid: bool) -> str:
    """Retorna color para mensaje de validación"""
    return "success" if is_valid else "error"
