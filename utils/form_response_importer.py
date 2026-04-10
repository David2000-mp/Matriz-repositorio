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
from datetime import datetime
from typing import Optional, Tuple

from utils.account_normalization import build_account_key, normalize_platform_name, normalize_social_user
from utils.logger import get_logger

logger = get_logger(__name__)


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
        
        headers = [h.strip() for h in raw_data[0]]
        
        logger.debug(f"Headers encontrados: {headers}")
        
        # Procesar cada fila de respuesta
        # Estructura esperada del formulario:
        # Col 0: Marca temporal
        # Col 1: Fecha del Reporte
        # Col 2: Institución Marista
        # Col 3: Plataforma Social
        # Col 4: Usuario o URL
        # Col 5: Seguidores Totales
        # Col 6: Engagement Rate (%)
        # Col 7: Alcance Total
        # Col 8: Interacciones Totales
        # Col 9: Comentarios Contextuales
        
        for row_idx, row in enumerate(raw_data[1:], start=2):
            try:
                # Extender fila si es necesario
                if len(row) < 10:
                    row = row + [''] * (10 - len(row))
                
                # Extraer campos por índice
                fecha = _parse_fecha(row[1] if len(row) > 1 else '')
                entidad = row[2].strip() if len(row) > 2 else ''
                plataforma = row[3].strip() if len(row) > 3 else ''
                usuario_red = row[4].strip() if len(row) > 4 else ''
                
                # Campos numéricos
                seguidores_str = row[5] if len(row) > 5 else '0'
                engagement_str = row[6] if len(row) > 6 else '0'
                alcance_str = row[7] if len(row) > 7 else '0'
                interacciones_str = row[8] if len(row) > 8 else ''
                
                # Normalizar valores
                seguidores = int(_parse_numeric_value(seguidores_str, 0))
                engagement_rate = _parse_numeric_value(engagement_str, 0.0)
                alcance = int(_parse_numeric_value(alcance_str, 0))
                
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
