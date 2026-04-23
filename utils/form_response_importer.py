"""
Form Response Importer - Importar datos desde Google Form a las hojas estructuradas
====================================================================================
Lee datos de la hoja "Respuestas de formulario 3" y los importa a:
- cuentas: Información de las cuentas de redes sociales
- metricas: Métricas asociadas a esas cuentas

Responsabilidades:
  - Leer "Respuestas de formulario 3"
  - Mapear columnas del formulario a las estructuras esperadas
  - Generar id_cuenta único para cada combinación Institución + Plataforma
  - Evitar duplicados manteniendo el registro más reciente
  - Calcular Interacciones totales si falta (desde engagement_rate * seguidores / 100)
"""

import pandas as pd
import hashlib
import re
import unicodedata
from datetime import datetime
from typing import Optional, Tuple, Dict, List

from utils.account_normalization import build_account_key, normalize_platform_name, normalize_social_user
from utils.logger import get_logger

logger = get_logger(__name__)


def _normalize_header_label(header: str) -> str:
    """Normaliza headers para matching flexible."""
    value = "" if header is None else str(header)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def _canonical_alias_map() -> Dict[str, set]:
    return {
        "fecha": {"fecha del reporte", "fecha"},
        "entidad": {"institucion marista", "institucion", "entidad"},
        "plataforma": {"plataforma social", "plataforma"},
        "usuario_red": {"usuario o url de la red", "usuario o url", "usuario red"},
        "seguidores": {
            "seguidores totales: validacion: es un numero > mayor que 0",
            "seguidores totales",
            "seguidores",
        },
        "engagement_rate": {
            "engagement rate (%): validacion: es un numero > entre 0 y 100",
            "engagement rate (%)",
            "engagement rate",
            "engagment rate",
        },
        "alcance": {"alcance total", "alcance"},
        "interacciones": {"interacciones totales", "interacciones"},
        "comentarios": {
            "comentarios contextuales",
            '"comentarios contextuales"',
            "comentarios",
        },
        "media_visualizaciones": {"media de visualizaciones"},
        "tema_mas_visto": {"tema mas visto"},
        "engagement_contenido_imagenes": {
            "engagement por contenido: imagenes",
            "engagment por contenido: imagenes",
        },
        "engagement_contenido_links": {
            "engagement por contenido: links",
            "engagment por contenido: links",
        },
        "engagement_contenido_videos": {
            "engagement por contenido: videos",
            "engagment por contenido: videos",
        },
        "top_5_publicaciones": {
            "top 5 publicaciones por rendimiento",
            "top 5 publicaciones por rendieminto",
        },
        "engagement_tema_mas_visto": {
            "engagement del tema mas visto",
            "engagment del tema mas visto",
        },
        "publicaciones_por_semana": {"publicaciones por semana"},
        "tema_principal": {"tema principal del contenido del periodo"},
        "obs_engagement": {"observaciones de engagement del periodo"},
        "notas_operacionales": {"notas operacionales relevantes"},
        "alertas_riesgos": {"alertas o riesgos detectados"},
        "tuvo_cambios_operacionales": {"¿hubo cambios operacionales durante este periodo?", "hubo cambios operacionales durante este periodo"},
        "publicacion_destacada": {"publicacion destacada"},
    }


def _build_header_groups(headers: List[str]) -> Dict[str, List[int]]:
    """Devuelve índices por columna canónica tolerando variantes de texto."""
    alias_map = _canonical_alias_map()
    groups: Dict[str, List[int]] = {k: [] for k in alias_map}

    for idx, header in enumerate(headers):
        normalized = _normalize_header_label(header)
        for canonical, aliases in alias_map.items():
            if normalized in aliases:
                groups[canonical].append(idx)
                break
    return groups


def _get_first_value(row: List[str], indexes: List[int], default: str = "") -> str:
    """Toma el primer valor no vacío de una lista de índices."""
    if not indexes:
        return default

    for idx in indexes:
        if idx < len(row):
            raw = row[idx]
            text = "" if raw is None else str(raw).strip()
            if text:
                return text
    return default


def _get_joined_values(row: List[str], indexes: List[int]) -> str:
    """Concatena valores no vacíos sin duplicados."""
    if not indexes:
        return ""

    chunks: List[str] = []
    for idx in indexes:
        if idx < len(row):
            raw = row[idx]
            text = "" if raw is None else str(raw).strip()
            if text and text not in chunks:
                chunks.append(text)
    return " | ".join(chunks)


def _normalize_platform_name(platform: str) -> str:
    """Compatibilidad interna: delega a la normalización compartida."""
    return normalize_platform_name(platform)


def _find_existing_account(cuentas_list: list[dict], entidad: str, plataforma: str, usuario_red: str):
    """Busca coincidencias previas para no partir una misma cuenta en varios IDs."""
    entidad_key = str(entidad or "").strip().lower()
    plataforma_key = _normalize_platform_name(plataforma).strip().lower()
    usuario_key = normalize_social_user(usuario_red, plataforma)

    candidates = [
        cuenta for cuenta in cuentas_list
        if str(cuenta.get("entidad", "")).strip().lower() == entidad_key
        and _normalize_platform_name(cuenta.get("plataforma", "")).strip().lower() == plataforma_key
    ]

    if not candidates:
        return None

    if usuario_key:
        for cuenta in candidates:
            if normalize_social_user(cuenta.get("usuario_red", ""), plataforma) == usuario_key:
                return cuenta

        blank_candidate = next(
            (cuenta for cuenta in candidates if not normalize_social_user(cuenta.get("usuario_red", ""), plataforma)),
            None,
        )
        if blank_candidate is not None:
            return blank_candidate

    if len(candidates) == 1:
        return candidates[0]

    return None


def _generate_account_id(entidad: str, plataforma: str, usuario_red: str = "") -> str:
    """
    Genera un ID único y consistente para una cuenta.
    Usa una llave canónica para que variantes de URL no creen cuentas duplicadas.
    """
    key = build_account_key(entidad, plataforma, usuario_red)
    hash_obj = hashlib.md5(key.encode())
    short_hash = hash_obj.hexdigest()[:8]
    return f"form_{short_hash}"


def _parse_fecha(fecha_str: str) -> Optional[str]:
    """Parse fecha del formato español (DD/MM/YYYY) o ISO (YYYY-MM-DD)."""
    if not fecha_str or pd.isna(fecha_str):
        return datetime.now().strftime("%Y-%m-%d")
    
    fecha_str = str(fecha_str).strip()
    
    # Intentar formatos comunes
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
        try:
            dt = datetime.strptime(fecha_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Fallback: usar fecha actual
    logger.warning(f"No se pudo parsear fecha '{fecha_str}', usando actual")
    return datetime.now().strftime("%Y-%m-%d")


def _parse_numeric_value(raw_value, default: float = 0.0) -> float:
    """Convierte textos numéricos flexibles como `0.49%`, `1,25` o `1 200` a float."""
    if raw_value is None or pd.isna(raw_value):
        return default

    cleaned = str(raw_value).strip()
    if not cleaned:
        return default

    cleaned = (
        cleaned.replace('%', '')
        .replace('\u00a0', '')
        .replace(' ', '')
        .replace(',', '.')
    )

    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = ''.join(parts[:-1]) + '.' + parts[-1]

    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return default


def _calculate_interactions(engagement_rate: float, seguidores: int) -> int:
    """Calcula interacciones totales desde engagement rate y seguidores."""
    if seguidores <= 0 or engagement_rate <= 0:
        return 0
    
    # interacciones = (engagement_rate / 100) * seguidores
    interactions = int((engagement_rate / 100.0) * seguidores)
    return max(0, interactions)


def _normalize_booleanish(value: str) -> str:
    """Normaliza respuestas tipo si/no a valores estables para analitica."""
    normalized = _normalize_header_label(value)
    if normalized in {"si", "sí", "yes", "true", "1"}:
        return "si"
    if normalized in {"no", "false", "0"}:
        return "no"
    return ""


def import_form_responses(spreadsheet) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee las respuestas del formulario y las convierte a DataFrames estructurados.
    
    Args:
        spreadsheet: Objeto de gsheet con conexión a Google Sheets
    
    Returns:
        Tuple[cuentas_df, metricas_df]: DataFrames listos para guardar
    """
    cuentas_list = []
    metricas_list = []
    
    try:
        ws_form = spreadsheet.worksheet("Respuestas de formulario 3")
        raw_data = ws_form.get()
        
        if not raw_data or len(raw_data) < 2:
            logger.warning("Hoja de respuestas de formulario vacía")
            return pd.DataFrame(), pd.DataFrame()
        
        headers = [str(h).strip() for h in raw_data[0]]
        header_groups = _build_header_groups(headers)
        
        logger.debug(f"Headers encontrados: {headers}")
        
        for row_idx, row in enumerate(raw_data[1:], start=2):
            try:
                row_data = list(row)
                if len(row_data) < len(headers):
                    row_data.extend([''] * (len(headers) - len(row_data)))

                # Extraer campos por header canónico
                fecha = _parse_fecha(_get_first_value(row_data, header_groups.get("fecha", []), ''))
                entidad = _get_first_value(row_data, header_groups.get("entidad", []), '').strip()
                plataforma = _get_first_value(row_data, header_groups.get("plataforma", []), '').strip()
                usuario_red = _get_first_value(row_data, header_groups.get("usuario_red", []), '').strip()

                # Campos numéricos base
                seguidores_str = _get_first_value(row_data, header_groups.get("seguidores", []), '0')
                engagement_str = _get_first_value(row_data, header_groups.get("engagement_rate", []), '0')
                alcance_str = _get_first_value(row_data, header_groups.get("alcance", []), '0')
                interacciones_str = _get_first_value(row_data, header_groups.get("interacciones", []), '')

                # Campos nuevos
                media_visualizaciones_str = _get_first_value(row_data, header_groups.get("media_visualizaciones", []), '0')
                tema_mas_visto = _get_first_value(row_data, header_groups.get("tema_mas_visto", []), '')
                eng_img_str = _get_first_value(row_data, header_groups.get("engagement_contenido_imagenes", []), '0')
                eng_links_str = _get_first_value(row_data, header_groups.get("engagement_contenido_links", []), '0')
                eng_videos_str = _get_first_value(row_data, header_groups.get("engagement_contenido_videos", []), '0')
                top_5_publicaciones = _get_first_value(row_data, header_groups.get("top_5_publicaciones", []), '')
                eng_tema_mas_visto_str = _get_first_value(row_data, header_groups.get("engagement_tema_mas_visto", []), '0')
                publicaciones_semana_str = _get_first_value(row_data, header_groups.get("publicaciones_por_semana", []), '0')
                comentarios_consolidados = _get_joined_values(row_data, header_groups.get("comentarios", []))
                tema_principal = _get_first_value(row_data, header_groups.get("tema_principal", []), '').strip()
                obs_engagement = _get_first_value(row_data, header_groups.get("obs_engagement", []), '').strip()
                notas_operacionales = _get_first_value(row_data, header_groups.get("notas_operacionales", []), '').strip()
                alertas_riesgos = _get_first_value(row_data, header_groups.get("alertas_riesgos", []), '').strip()
                tuvo_cambios_operacionales = _normalize_booleanish(
                    _get_first_value(row_data, header_groups.get("tuvo_cambios_operacionales", []), '')
                )
                publicacion_destacada = _get_first_value(row_data, header_groups.get("publicacion_destacada", []), '').strip()
                
                # Normalizar valores
                seguidores = int(_parse_numeric_value(seguidores_str, 0))
                engagement_rate = _parse_numeric_value(engagement_str, 0.0)
                alcance = int(_parse_numeric_value(alcance_str, 0))
                media_visualizaciones = _parse_numeric_value(media_visualizaciones_str, 0.0)
                engagement_contenido_imagenes = _parse_numeric_value(eng_img_str, 0.0)
                engagement_contenido_links = _parse_numeric_value(eng_links_str, 0.0)
                engagement_contenido_videos = _parse_numeric_value(eng_videos_str, 0.0)
                engagement_tema_mas_visto = _parse_numeric_value(eng_tema_mas_visto_str, 0.0)
                publicaciones_por_semana = _parse_numeric_value(publicaciones_semana_str, 0.0)
                
                # Interacciones: usar valor ingresado o calcular desde engagement
                if interacciones_str and str(interacciones_str).strip():
                    parsed_interacciones = _parse_numeric_value(interacciones_str, -1)
                    interacciones = int(parsed_interacciones) if parsed_interacciones >= 0 else _calculate_interactions(engagement_rate, seguidores)
                else:
                    interacciones = _calculate_interactions(engagement_rate, seguidores)
                
                # Validaciones
                if not entidad or not plataforma:
                    logger.debug(f"Fila {row_idx}: Institución o Plataforma vacía, omitiendo")
                    continue
                
                # Normalizar plataforma
                plataforma = _normalize_platform_name(plataforma)

                # Reutilizar cuenta existente si la URL cambió, trae query params o viene vacía
                existing_account = _find_existing_account(cuentas_list, entidad, plataforma, usuario_red)
                if existing_account is not None:
                    id_cuenta = existing_account['id_cuenta']
                    if usuario_red and not str(existing_account.get('usuario_red', '')).strip():
                        existing_account['usuario_red'] = usuario_red
                else:
                    id_cuenta = _generate_account_id(entidad, plataforma, usuario_red)
                    cuenta_dict = {
                        'id_cuenta': id_cuenta,
                        'entidad': entidad,
                        'plataforma': plataforma,
                        'usuario_red': usuario_red,
                    }
                    cuentas_list.append(cuenta_dict)
                
                # Agregar a lista de métricas
                metricas_dict = {
                    'id_cuenta': id_cuenta,
                    'fecha': fecha,
                    'seguidores': seguidores,
                    'alcance': alcance,
                    'interacciones': interacciones,
                    'likes_promedio': 0,  # No viene en el formulario
                    'engagement_rate': engagement_rate,
                    'media_visualizaciones': media_visualizaciones,
                    'tema_mas_visto': tema_mas_visto,
                    'engagement_contenido_imagenes': engagement_contenido_imagenes,
                    'engagement_contenido_links': engagement_contenido_links,
                    'engagement_contenido_videos': engagement_contenido_videos,
                    'top_5_publicaciones': top_5_publicaciones,
                    'engagement_tema_mas_visto': engagement_tema_mas_visto,
                    'publicaciones_por_semana': publicaciones_por_semana,
                    'comentarios_consolidados': comentarios_consolidados,
                    'tema_principal': tema_principal,
                    'obs_engagement': obs_engagement,
                    'notas_operacionales': notas_operacionales,
                    'alertas_riesgos': alertas_riesgos,
                    'tuvo_cambios_operacionales': tuvo_cambios_operacionales,
                    'publicacion_destacada': publicacion_destacada,
                }
                metricas_list.append(metricas_dict)
                
                logger.debug(f"Importada fila {row_idx}: {entidad} - {plataforma} ({id_cuenta}) - Interacciones: {interacciones}")
                
            except Exception as e:
                logger.warning(f"Error procesando fila {row_idx}: {e}")
                continue
        
        cuentas_df = pd.DataFrame(cuentas_list)
        metricas_df = pd.DataFrame(metricas_list)
        
        logger.info(f"Importadas {len(cuentas_df)} cuentas y {len(metricas_df)} métricas desde formulario")
        
        return cuentas_df, metricas_df
        
    except Exception as e:
        logger.error(f"Error importando respuestas de formulario: {e}")
        return pd.DataFrame(), pd.DataFrame()
