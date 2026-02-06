"""
Data Saver - Funciones de escritura de datos
==================================================
Este módulo SOLO escribe datos en Google Sheets y CSV local.
NO importa nada de data_manager a nivel de módulo (lazy imports).
NO importa de data_loader.
Los IDs se preservan SIEMPRE como strings (nunca pd.to_numeric).

Flujo unidireccional:
  data_saver.py → (importa en data_manager.py al final)

Cache Management:
  Cada función que escribe invalida st.cache_data y DataProvider.
"""

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
METRICAS_CSV = DATA_DIR / "metricas.csv"
CUENTAS_CSV = DATA_DIR / "cuentas.csv"

COLS_METRICAS = ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]
COLS_CUENTAS = ["id_cuenta", "entidad", "plataforma", "usuario_red"]


def get_id(entidad, plataforma, usuario, df_cuentas_cache=None, **kwargs) -> str:
    """
    Busca el ID existente en df_cuentas_cache (case-insensitive) o genera uno nuevo si no existe.
    """
    u_entidad = str(entidad).strip().lower()
    u_plataforma = str(plataforma).strip().lower()
    u_usuario = str(usuario).strip()
    if u_usuario.startswith(('http://', 'https://')):
        parts = u_usuario.rstrip('/').split('/')
        if len(parts) > 0:
            u_usuario = parts[-1]
    if u_usuario.startswith('@'):
        u_usuario = u_usuario[1:]
    u_usuario = u_usuario.lower().strip()

    cuentas_df = None
    if df_cuentas_cache is not None:
        cuentas_df = df_cuentas_cache
    else:
        # Siempre intentar llamar load_data si df_cuentas_cache es None
        try:
            from utils.data_loader import load_data
            cuentas_df, _ = load_data()
            logger.info("get_id: load_data() fue llamado porque df_cuentas_cache=None")
        except Exception as e:
            logger.warning(f"No se pudo cargar cuentas para lookup en get_id: {e}")
            cuentas_df = None

    if cuentas_df is not None and not cuentas_df.empty:
        cuentas_norm = cuentas_df.copy()
        # Check required columns exist
        required_cols = ["entidad", "plataforma", "usuario_red"]
        if all(col in cuentas_norm.columns for col in required_cols):
            for col in required_cols:
                cuentas_norm[col] = cuentas_norm[col].astype(str).str.strip().str.lower()
            mask = (
                (cuentas_norm["entidad"] == u_entidad) &
                (cuentas_norm["plataforma"] == u_plataforma) &
                (cuentas_norm["usuario_red"].str.lstrip('@') == u_usuario)
            )
            match = cuentas_norm[mask]
            if not match.empty:
                return str(match.iloc[0]["id_cuenta"])
        else:
            logger.warning(f"DataFrame de cuentas no tiene columnas requeridas: {required_cols}")

    unique_str = f"{u_entidad}|{u_plataforma}|{u_usuario}"
    hash_id = hashlib.md5(unique_str.encode()).hexdigest()[:8]
    return str(hash_id)


def _normalize_id_column(df: pd.DataFrame, col: str="id_cuenta") -> pd.DataFrame:
    """
    Asegura que la columna de ID se trata SIEMPRE como string.
    Previene conversiones a número que corrompan datos.
    """
    if col in df.columns:
        # Normaliza a minúsculas y sin espacios
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def _invalidate_caches():
    """
    Invalida todos los cachés después de escribir datos.
    Esto es CRÍTICO para que los cambios sean instantáneos.
    """
    try:
        st.cache_data.clear()
        logger.debug("Cache st.cache_data limpiado")
    except Exception as e:
        logger.warning(f"Error limpiando st.cache_data: {e}")
    # Invalidar caché del DataProvider si está disponible
    try:
        from utils.data_provider import data_provider
        data_provider.invalidate_cache()
        logger.debug("Cache DataProvider invalidado")
    except ImportError as e:
        logger.warning(f"DataProvider no importado: {e}")
    except Exception as e:
        logger.warning(f"Error invalidando DataProvider: {e}")


def sync_cuentas_to_sheets(df_cuentas: pd.DataFrame) -> bool:
    """
    Sincroniza DataFrame de cuentas con Google Sheets.
    Preserva IDs como strings.
    
    Args:
        df_cuentas: DataFrame con columnas ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
    
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        # Lazy import para evitar circularidad
        from utils.sheets_connector import get_sheets_connection
        
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("cuentas")
            df_copy = df_cuentas.copy()
            df_copy = _normalize_id_column(df_copy, "id_cuenta")
            ws.clear()
            # Asegurar que todos los valores se escriben como strings
            data_to_write = [COLS_CUENTAS] + df_copy[COLS_CUENTAS].astype(str).values.tolist()
            ws.update(data_to_write)
            _invalidate_caches()
            logger.info("Cuentas sincronizadas a Google Sheets")
            return True
    except Exception as e:
        logger.error(f"Error sincronizando cuentas a Sheets: {e}")
    
    return False


def _auto_upsert_cuentas(df_metricas: pd.DataFrame) -> bool:
    """
    Auto-Upsert: Verifica que todas las cuentas en df_metricas existan en la hoja cuentas.
    Si una métrica tiene una cuenta nueva (id_cuenta desconocido), la inserta automáticamente.
    
    Args:
        df_metricas: DataFrame de métricas con columnas: id_cuenta, entidad, plataforma, usuario_red
    
    Returns:
        bool: True si el upsert fue exitoso o no fue necesario
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if not ss:
            logger.warning("No se pudo conectar a Google Sheets para auto-upsert")
            return True  # No fallar, solo warning
        
        # Leer cuentas existentes
        try:
            ws_cuentas = ss.worksheet("cuentas")
            existing_records = ws_cuentas.get_all_records()
            existing_ids = set([str(r.get("id_cuenta", "")).strip() for r in existing_records])
        except:
            existing_ids = set()
            logger.warning("No se pudo leer cuentas existentes")
        
        # Identificar IDs nuevos
        new_ids = set()
        rows_to_insert = []
        
        for idx, row in df_metricas.iterrows():
            account_id = str(row.get("id_cuenta", "")).strip()
            if account_id and account_id not in existing_ids:
                new_ids.add(account_id)
                entidad = str(row.get("entidad", "Unknown")).strip()
                plataforma = str(row.get("plataforma", "Unknown")).strip()
                usuario = str(row.get("usuario_red", "Unknown")).strip()
                rows_to_insert.append([account_id, entidad, plataforma, usuario])
        
        # Insertar nuevas cuentas si las hay
        if rows_to_insert:
            try:
                ws_cuentas.append_rows(rows_to_insert)
                logger.info(f"Auto-insertadas {len(rows_to_insert)} cuentas nuevas")
            except Exception as e:
                logger.warning(f"Error en auto-upsert de cuentas: {e}")
        
        return True
    except Exception as e:
        logger.warning(f"Error en auto-upsert: {e}")
        return True  # No fallar el guardado principal


def guardar_datos(nuevo_df: pd.DataFrame, modo: str="append", csv_path=None, **kwargs) -> bool:
    """
    Guarda métricas en Google Sheets con fallback a CSV local.
    Motor de integridad: auto-upsert + column blindage + cache invalidation.
    
    Args:
        nuevo_df: DataFrame con métricas (debe incluir: id_cuenta, entidad, plataforma, usuario_red, fecha, seguidores, alcance, interacciones, likes_promedio, engagement_rate)
        modo: "append" para agregar, otro valor para sobrescribir
    
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    # Path injection: if any path is provided (csv_path or via kwargs), use it strictly, never fallback to default if present
    if csv_path is None and 'csv_path' in kwargs:
        csv_path = kwargs['csv_path']
    # Strict path creation
    if csv_path is not None:
        target_path = Path(csv_path).resolve()
    else:
        target_path = METRICAS_CSV.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    nuevo_df = nuevo_df.copy()
    nuevo_df = _normalize_id_column(nuevo_df, "id_cuenta")

    # Siempre crear el archivo CSV, incluso si el DataFrame está vacío o le faltan columnas
    try:
        # Si faltan columnas, reindex las que existan y rellena el resto
        df_limpio = nuevo_df.reindex(columns=COLS_METRICAS)
        for col in COLS_METRICAS:
            if col in df_limpio.columns:
                if col == 'fecha':
                    df_limpio[col] = pd.to_datetime(df_limpio[col], errors='coerce').dt.strftime('%Y-%m-%d')
                elif col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio']:
                    df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce').fillna(0).astype(int)
                elif col == 'engagement_rate':
                    df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce').fillna(0.0).round(4)
                else:
                    df_limpio[col] = df_limpio[col].astype(str)
    except Exception as e:
        logger.error(f"Error procesando columnas requeridas: {e}")
        # Si hay error, crear archivo vacío con encabezados
        df_limpio = pd.DataFrame(columns=COLS_METRICAS)

    # 3. GUARDAR EN GOOGLE SHEETS (best effort, no afecta retorno)
    sheets_success = True
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("metricas")
            data_rows = df_limpio.values.tolist()
            if data_rows:
                if modo != "append":
                    # Limpiar la hoja antes de sobrescribir
                    ws.clear()
                    # Agregar headers
                    ws.append_row(COLS_METRICAS)
                ws.append_rows(data_rows)
                logger.info(f"✅ Guardados {len(data_rows)} registros en Google Sheets (modo: {modo})")
            else:
                logger.info("No hay datos para guardar en Google Sheets (batch vacío)")
        else:
            sheets_success = False
            logger.warning("No se pudo conectar a Google Sheets para guardar métricas")
    except Exception as e:
        sheets_success = False
        logger.warning(f"Error escribiendo en Google Sheets: {e}")

    # 4. RESPALDO EN CSV LOCAL (siempre intentar, incluso si Sheets falla)
    csv_success = True
    try:
        if modo == "append" and target_path.exists():
            try:
                old_df = pd.read_csv(target_path, dtype={"id_cuenta": str})
                old_df = _normalize_id_column(old_df, "id_cuenta")
            except Exception as e:
                logger.warning(f"Error leyendo CSV existente: {e}")
                old_df = pd.DataFrame(columns=COLS_METRICAS)
            # Concatenar, deduplicar por orden de aparición (nuevos al final)
            concat_df = pd.concat([old_df, df_limpio], ignore_index=True)
            final_df = concat_df.drop_duplicates(subset=["id_cuenta", "fecha"], keep="last")
            final_df = final_df.sort_values(by=["fecha"]).reset_index(drop=True)
        else:
            # Si no hay datos, igual crear archivo con encabezados
            final_df = df_limpio.copy()
            if final_df.empty:
                final_df = pd.DataFrame(columns=COLS_METRICAS)
        final_df = _normalize_id_column(final_df, "id_cuenta")
        final_df[COLS_METRICAS].to_csv(target_path, index=False)
        # Fallback: Si el archivo no existe tras el guardado, créalo manualmente con encabezados
        if not target_path.exists():
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(','.join(COLS_METRICAS) + '\n')
        logger.info(f"✅ Datos guardados en CSV: {target_path}")
    except Exception as e:
        csv_success = False
        logger.error(f"Error guardando en CSV: {e}")

    # 5. INVALIDAR CACHÉS
    if sheets_success or csv_success:
        try:
            import streamlit as st
            st.cache_data.clear()
            logger.info("✅ Cachés invalidados")
        except Exception as e:
            logger.warning(f"Error invalidando cachés tras guardar datos: {e}")
        _invalidate_caches()

    # Debe retornar True solo si el CSV fue exitoso, False si falló el CSV
    if not csv_success:
        logger.warning("guardar_datos: Falló al guardar en CSV (crítico)")
        return False
    return True


def save_batch(df: pd.DataFrame, csv_path=None, **kwargs) -> bool:
    """
    Guarda un batch de métricas.
    Alias conveniente para guardar_datos.
    Permite pasar tanto un DataFrame como una lista de dicts.
    """
    import pandas as pd
    if isinstance(df, list):
        df = pd.DataFrame(df)
    # Siempre llamar guardar_datos, incluso si el batch está vacío
    if csv_path is None and 'csv_path' in kwargs:
        csv_path = kwargs['csv_path']
        kwargs = {k: v for k, v in kwargs.items() if k != 'csv_path'}
    result = guardar_datos(df, csv_path=csv_path, **kwargs)
    if not result:
        logger.warning("save_batch: guardar_datos devolvió False (fallo en guardado)")
    return result


def reset_db() -> bool:
    """
    Resetea completamente la base de datos:
    1. Limpia hojas de Google Sheets (metricas, cuentas) preservando encabezados
    2. Borra archivos CSV locales correspondientes
    3. Invalida todos los cachés
    
    SEGURIDAD: Preserva siempre la fila de encabezados en Google Sheets.
    
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    success_sheets = False
    success_csv = False
    
    # ========================================================================
    # 1. LIMPIAR GOOGLE SHEETS (preservando encabezados)
    # ========================================================================
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        
        if ss:
            # Limpiar hoja de métricas
            try:
                ws_metricas = ss.worksheet("metricas")
                ws_metricas.clear()  # Borra todo
                # Restaurar encabezados (7 columnas estrictas)
                headers_metricas = ['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
                ws_metricas.append_row(headers_metricas)
                logger.info("✅ Hoja 'metricas' limpiada (encabezados preservados)")
            except Exception as e:
                logger.error(f"Error limpiando hoja 'metricas': {e}")
            
            # Limpiar hoja de cuentas
            try:
                ws_cuentas = ss.worksheet("cuentas")
                ws_cuentas.clear()  # Borra todo
                # Restaurar encabezados (4 columnas)
                headers_cuentas = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
                ws_cuentas.append_row(headers_cuentas)
                logger.info("✅ Hoja 'cuentas' limpiada (encabezados preservados)")
            except Exception as e:
                logger.error(f"Error limpiando hoja 'cuentas': {e}")
            
            success_sheets = True
            logger.info("✅ Google Sheets reseteado exitosamente")
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets para reset: {e}")
    
    # ========================================================================
    # 2. BORRAR ARCHIVOS CSV LOCALES
    # ========================================================================
    try:
        # Borrar metricas.csv
        if METRICAS_CSV.exists():
            METRICAS_CSV.unlink()
            logger.info(f"✅ Archivo {METRICAS_CSV} eliminado")
        
        # Borrar cuentas.csv
        if CUENTAS_CSV.exists():
            CUENTAS_CSV.unlink()
            logger.info(f"✅ Archivo {CUENTAS_CSV} eliminado")
        
        success_csv = True
    except Exception as e:
        logger.error(f"Error borrando archivos CSV: {e}")
    
    # ========================================================================
    # 3. INVALIDAR CACHÉS
    # ========================================================================
    if success_sheets or success_csv:
        try:
            import streamlit as st
            st.cache_data.clear()
            logger.info("✅ Cachés de Streamlit invalidados")
        except:
            pass
        
        _invalidate_caches()
        logger.info("✅ Reset completado exitosamente")
        return True
    
    return False


def save_comment(entidad: str, mes: str, comentario: str) -> bool:
    """
    Guarda comentario contextual para una entidad en un mes.
    Invalida cachés después de escribir.
    
    Args:
        entidad: Nombre de la institución
        mes: Período (ej: "2024-01")
        comentario: Texto del comentario
    
    Returns:
        bool: True si fue exitoso
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("comentarios")
            ws.append_row([str(entidad), str(mes), str(comentario)])
            _invalidate_caches()
            logger.info(f"Comentario guardado para {entidad}")
            return True
    except Exception as e:
        logger.error(f"Error guardando comentario: {e}")
    
    return False


def save_username_editado(entidad: str, plataforma: str, usuario_editado: str) -> bool:
    """
    Guarda un nombre de usuario editado.
    Invalida cachés después de escribir.
    
    Args:
        entidad: Nombre de la institución
        plataforma: Red social
        usuario_editado: Nuevo nombre de usuario
    
    Returns:
        bool: True si fue exitoso
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("usernames_editados")
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            ws.append_row([str(entidad), str(plataforma), str(usuario_editado), fecha_hoy])
            _invalidate_caches()
            logger.info(f"Username editado guardado: {entidad}/{plataforma}")
            return True
    except Exception as e:
        logger.error(f"Error guardando username editado: {e}")
    
    return False
