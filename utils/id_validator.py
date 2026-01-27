"""
id_validator.py - Validación de IDs de cuenta
===============================================
Módulo para proteger la integridad de IDs. Los IDs deben ser:
- String (nunca números)
- Formato: 8 caracteres hexadecimales (MD5 truncado)
- Ejemplos: "4fe0d087", "a1b2c3d4"
"""

import pandas as pd
import logging
from typing import Tuple, List
import re

logger = logging.getLogger(__name__)


def validate_id_format(id_cuenta: str) -> bool:
    """
    Valida que el ID tenga el formato esperado (8 caracteres hex MD5).
    Previene corrupción de tipos.

    Args:
        id_cuenta: String a validar

    Returns:
        bool: True si es válido (8 chars hex), False en caso contrario

    Ejemplos:
        >>> validate_id_format("4fe0d087")  # ✅ Válido
        True
        >>> validate_id_format("12345")  # ❌ Solo 5 caracteres
        False
        >>> validate_id_format("ZZZZZZZZ")  # ❌ No es hexadecimal
        False
    """
    if not isinstance(id_cuenta, str):
        return False

    # Limpiar espacios
    id_cuenta = id_cuenta.strip()

    # Validar largo: exactamente 8 caracteres
    if len(id_cuenta) != 8:
        return False

    # Validar que sean caracteres hexadecimales
    if not re.match(r'^[0-9a-fA-F]{8}$', id_cuenta):
        return False

    return True


def sanitize_id_column(df: pd.DataFrame, col: str = "id_cuenta") -> Tuple[pd.DataFrame, List[Tuple[int, str]]]:
    """
    Sanitiza columna de IDs:
    1. Convierte todos a string
    2. Valida formato (8 chars hex)
    3. Marca como None los IDs inválidos

    Args:
        df: DataFrame a sanitizar
        col: Nombre de la columna de IDs (default: "id_cuenta")

    Returns:
        Tuple[pd.DataFrame, List[Tuple[int, str]]]:
            - DataFrame sanitizado
            - Lista de (row_index, invalid_value) encontrados

    Ejemplo:
        >>> df = pd.DataFrame({
        ...     "id_cuenta": ["4fe0d087", "12345", "abc", "a1b2c3d4"],
        ...     "nombre": ["A", "B", "C", "D"]
        ... })
        >>> clean_df, invalid = sanitize_id_column(df)
        >>> invalid
        [(1, "12345"), (2, "abc")]
        >>> clean_df["id_cuenta"].tolist()
        ["4fe0d087", None, None, "a1b2c3d4"]
    """
    if col not in df.columns:
        logger.warning(f"Columna '{col}' no existe en DataFrame")
        return df, []

    df = df.copy()
    invalid_ids = []

    for idx, val in df[col].items():
        original_val = val
        str_val = str(val).strip()

        # Validar formato
        if not validate_id_format(str_val):
            invalid_ids.append((idx, original_val))
            df.at[idx, col] = None
            logger.warning(f"ID inválido en fila {idx}: '{original_val}' (no cumple formato 8-hex)")
        else:
            # Mantener como string lowercase
            df.at[idx, col] = str_val.lower()

    # Convertir la columna a string
    df[col] = df[col].astype(str)

    if invalid_ids:
        logger.warning(f"Se encontraron {len(invalid_ids)} IDs inválidos y fueron marcados como None")

    return df, invalid_ids


def validate_id_uniqueness(df: pd.DataFrame, col: str = "id_cuenta") -> Tuple[bool, List[str]]:
    """
    Valida que no haya IDs duplicados en el DataFrame.

    Args:
        df: DataFrame a validar
        col: Nombre de la columna de IDs

    Returns:
        Tuple[bool, List[str]]:
            - bool: True si todos los IDs son únicos
            - List[str]: IDs duplicados encontrados (vacía si todo OK)

    Ejemplo:
        >>> df = pd.DataFrame({
        ...     "id_cuenta": ["4fe0d087", "a1b2c3d4", "4fe0d087"],
        ... })
        >>> is_unique, duplicates = validate_id_uniqueness(df)
        >>> is_unique
        False
        >>> duplicates
        ["4fe0d087"]
    """
    if col not in df.columns:
        return True, []

    duplicates = df[col][df[col].duplicated()].unique().tolist()

    if duplicates:
        logger.warning(f"IDs duplicados encontrados: {duplicates}")
        return False, duplicates

    return True, []


def generate_id(entidad: str, plataforma: str, usuario: str) -> str:
    """
    Genera un ID único consistente como MD5 de 8 caracteres.
    AGNÓSTICO AL FORMATO: Extrae username de URL completa o limpia handles con @.

    Args:
        entidad: Nombre de la escuela/institución
        plataforma: Red social (Facebook, Instagram, etc.)
        usuario: Puede ser URL completa, handle con @, o username limpio

    Returns:
        str: Hash MD5 de 8 caracteres (ej: '4fe0d087')

    Ejemplos:
        >>> generate_id("CUM", "FB", "https://facebook.com/maristascum")
        "4fe0d087"
        >>> generate_id("CUM", "FB", "@maristascum")
        "4fe0d087"
        >>> generate_id("CUM", "FB", "maristascum")
        "4fe0d087"
        # (Todos generan el mismo ID porque se normaliza)
    """
    import hashlib

    # Normalizar entidad y plataforma
    u_entidad = str(entidad).strip().lower()
    u_plataforma = str(plataforma).strip().lower()

    # Limpiar usuario
    u_usuario = str(usuario).strip()

    # Si es una URL completa, extraer username
    if u_usuario.startswith(('http://', 'https://')):
        parts = u_usuario.rstrip('/').split('/')
        if len(parts) > 0:
            u_usuario = parts[-1]

    # Si es un handle con @, removerlo
    if u_usuario.startswith('@'):
        u_usuario = u_usuario[1:]

    # Normalizar
    u_usuario = u_usuario.lower().strip()

    # Generar hash
    unique_str = f"{u_entidad}|{u_plataforma}|{u_usuario}"
    hash_id = hashlib.md5(unique_str.encode()).hexdigest()[:8]

    return str(hash_id)


def report_id_issues(df: pd.DataFrame, col: str = "id_cuenta") -> dict:
    """
    Genera reporte completo de problemas con IDs.

    Args:
        df: DataFrame a analizar
        col: Nombre de la columna de IDs

    Returns:
        dict: Reporte con keys:
            - valid_count: IDs válidos
            - invalid_count: IDs inválidos
            - duplicate_count: IDs duplicados
            - issues: Lista de strings describiendo problemas

    Ejemplo:
        >>> report = report_id_issues(df)
        >>> print(f"✅ {report['valid_count']} IDs válidos")
        >>> print(f"❌ {report['invalid_count']} IDs inválidos")
    """
    report = {
        "valid_count": 0,
        "invalid_count": 0,
        "duplicate_count": 0,
        "issues": []
    }

    if col not in df.columns:
        report["issues"].append(f"Columna '{col}' no existe")
        return report

    # Contar IDs válidos e inválidos
    clean_df, invalid_ids = sanitize_id_column(df.copy(), col)
    valid_count = len(clean_df) - len(invalid_ids)
    report["valid_count"] = valid_count
    report["invalid_count"] = len(invalid_ids)

    if invalid_ids:
        report["issues"].append(f"❌ {len(invalid_ids)} IDs inválidos encontrados")
        # Mostrar ejemplos
        examples = [str(val) for _, val in invalid_ids[:3]]
        report["issues"].append(f"   Ejemplos: {examples}")

    # Verificar duplicados
    is_unique, duplicates = validate_id_uniqueness(clean_df, col)
    if not is_unique:
        report["duplicate_count"] = len(duplicates)
        report["issues"].append(f"❌ {len(duplicates)} IDs duplicados encontrados")
        report["issues"].append(f"   IDs: {duplicates[:5]}")

    # Verificar nulos
    null_count = clean_df[col].isna().sum()
    if null_count > 0:
        report["issues"].append(f"⚠️ {null_count} valores nulos (None) en columna '{col}'")

    if not report["issues"]:
        report["issues"].append("✅ No se encontraron problemas con IDs")

    return report
