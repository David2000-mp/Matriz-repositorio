"""
Data Provider - Proveedor unificado de datos
==================================================
Clase responsable de unificar métricas y cuentas.
Solo importa de data_loader (lectura).
Preserva IDs como strings en todas las operaciones.

Responsabilidades:
  - Cargar datos desde data_loader
  - Fusionar métricas y cuentas sin pérdida de información
  - Mantener caché local
  - Invalidar caché cuando data_saver escribe
"""

import streamlit as st
import pandas as pd
from typing import Tuple, List
from utils.logger import get_logger
from utils.analytics import normalize_monthly_latest
from utils.text_mining import enrich_text_columns

logger = get_logger(__name__)


def normalize_merge_columns(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
    """
    Normaliza columnas después de merge pandas para evitar sufijos _x/_y.
    
    Args:
        df: DataFrame después de merge
        columns: Lista de columnas a normalizar (default: entidad, plataforma, usuario_red)
    
    Returns:
        DataFrame con columnas normalizadas
    """
    if columns is None:
        columns = ["entidad", "plataforma", "usuario_red"]
    
    for logical in columns:
        if logical in df.columns:
            continue
        for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
            if suff in df.columns:
                ser = df.loc[:, suff]
                if isinstance(ser, pd.DataFrame):
                    ser = ser.squeeze()
                df[logical] = ser
                break
        else:
            df[logical] = "Unknown"
    
    return df


class DataProvider:
    """
    Proveedor centralizado de datos para toda la aplicación.
    Gestiona caché local y fusión de DataFrames.
    """
    
    def __init__(self):
        """Inicializa el provider con caché vacío."""
        self._data_cache = None
        self._merged_cache = None
        self._comments_consolidated_cache = None
        self._last_schema_hash = ""

    def get_data(self, force_reload: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Obtiene cuentas y métricas con caché local.
        
        Args:
            force_reload: Si True, ignora caché y recarga desde fuente
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (cuentas, metricas)
        """
        current_schema_hash = ""

        if force_reload:
            # Limpiar caché de Streamlit cuando se fuerza recarga
            try:
                logger.info("🔄 Limpiando caché de Streamlit para recargar datos...")
                st.cache_data.clear()
                logger.info("✓ Caché de Streamlit limpiado")
            except Exception as e:
                logger.warning(f"No se pudo limpiar caché de Streamlit: {e}")
            
            self._data_cache = None
            self._merged_cache = None
            logger.info("Forzando recarga de datos desde Google Sheets...")

        try:
            from utils.data_loader import load_data, get_form_schema_hash

            current_schema_hash = get_form_schema_hash()
            if current_schema_hash and current_schema_hash != self._last_schema_hash:
                logger.info("🔄 Cambio de esquema detectado en formulario. Invalidando caché local...")
                self._data_cache = None
                self._merged_cache = None
            self._last_schema_hash = current_schema_hash
        except Exception as e:
            logger.warning(f"No se pudo validar hash de esquema de formulario: {e}")
            from utils.data_loader import load_data
        
        if self._data_cache is None:
            try:
                logger.debug("Llamando a load_data()...")
                self._data_cache = load_data(schema_hash=current_schema_hash)
                cuentas_df, metricas_df = self._data_cache
                logger.info(f"✓ Datos cargados: {len(cuentas_df)} cuentas, {len(metricas_df)} métricas")
                if len(cuentas_df) > 0:
                    logger.debug(f"  Entidades: {cuentas_df['entidad'].unique().tolist()}")
            except Exception as e:
                logger.error(f"Error cargando datos en DataProvider: {e}")
                self._data_cache = (pd.DataFrame(), pd.DataFrame())
        
        return self._data_cache

    def get_merged_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Obtiene datos fusionados (métricas + cuentas) preservando IDs como strings.
        Limpia automáticamente NaN en columnas de etiquetas para evitar TypeErrors en UI.
        
        Args:
            force_reload: Si True, ignora caché y recarga desde fuente
        
        Returns:
            pd.DataFrame: Fusión de métricas y cuentas en id_cuenta (sin NaN en labels)
        """
        if force_reload:
            self._merged_cache = None
        
        if self._merged_cache is None:
            cuentas, metricas = self.get_data(force_reload)
            
            if cuentas.empty or metricas.empty:
                self._merged_cache = pd.DataFrame()
                return self._merged_cache
            
            # CRÍTICO: Normalizar IDs como STRING antes de fusionar
            cuentas = cuentas.copy()
            metricas = metricas.copy()
            
            # Garantizar que id_cuenta es string (NUNCA número)
            cuentas["id_cuenta"] = cuentas["id_cuenta"].astype(str).str.strip()
            metricas["id_cuenta"] = metricas["id_cuenta"].astype(str).str.strip()
            
            # Guardar información de debug para mostrar al final
            ids_metricas = set(metricas["id_cuenta"].unique())
            ids_cuentas = set(cuentas["id_cuenta"].unique())
            debug_info = {
                'ids_metricas': len(ids_metricas),
                'ids_cuentas': len(ids_cuentas),
                'coinciden': len(ids_metricas & ids_cuentas),
                'solo_metricas': len(ids_metricas - ids_cuentas),
                'solo_cuentas': len(ids_cuentas - ids_metricas),
                'ejemplos_huerfanos': list(ids_metricas - ids_cuentas)[:3] if len(ids_metricas - ids_cuentas) > 0 else []
            }

            # --- LIMPIEZA: Eliminar registros de métricas que no tienen cuenta vinculada ---
            metricas = metricas[metricas["id_cuenta"].isin(cuentas["id_cuenta"])]

            # Fusión: métricas es la tabla principal (hechos)
            df_merged = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
            
            # Normalizar fecha si existe
            if "fecha" in df_merged.columns:
                df_merged['fecha'] = pd.to_datetime(df_merged['fecha'], errors='coerce')
            
            # ============================================================
            # LIMPIEZA DEFENSIVA: Eliminar NaN en columnas de etiquetas
            # Esto previene TypeErrors cuando Streamlit intenta usar
            # estos valores en st.metric, st.write, etc.
            # Aplicar fillna('') para garantizar que NO haya NaN
            # ============================================================
            label_columns = ['entidad', 'plataforma', 'usuario_red']
            for col in label_columns:
                if col in df_merged.columns:
                    # 1. Reemplazar NaN por string vacío
                    df_merged[col] = df_merged[col].fillna('')
                    # 2. Convertir a string
                    df_merged[col] = df_merged[col].astype(str)
                    # 3. Eliminar 'nan' string si Pandas lo convirtió
                    df_merged[col] = df_merged[col].replace('nan', '')
                    # 4. Verificar que no haya NaN
                    assert not df_merged[col].isna().any(), f"Aún hay NaN en {col}"
            
            # Rellenar NaN en columnas numéricas con 0
            numeric_columns = ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
            for col in numeric_columns:
                if col in df_merged.columns:
                    # Convertir strings con `%` o coma decimal a formato numérico legible
                    df_merged[col] = (
                        df_merged[col]
                        .astype(str)
                        .str.replace('%', '', regex=False)
                        .str.replace('\u00a0', '', regex=False)
                        .str.replace(' ', '', regex=False)
                        .str.replace(',', '.', regex=False)
                    )
                    df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').fillna(0)

            # Consolidar: mantener solo el último registro por cuenta y mes para evitar duplicados
            df_merged = normalize_monthly_latest(df_merged)

            # Enriquecer columnas textuales con sentimiento y palabras clave.
            df_merged = enrich_text_columns(df_merged)

            # Recalcular engagement_rate si falta o viene vacío
            if 'engagement_rate' not in df_merged.columns or df_merged['engagement_rate'].isna().any():
                if {'interacciones', 'seguidores'}.issubset(df_merged.columns):
                    df_merged['engagement_rate'] = df_merged.apply(
                        lambda r: (r['interacciones'] / r['seguidores'] * 100.0) if r.get('seguidores', 0) else 0.0,
                        axis=1,
                    )

            # Normalizar columnas después de merge (eliminar sufijos _x/_y)
            df_merged = normalize_merge_columns(df_merged)

            # Priorizar métricas clave (seguidores, engagement) y luego secundarios
            preferred_order = [
                'id_cuenta', 'entidad', 'plataforma', 'usuario_red', 'fecha',
                'seguidores', 'engagement_rate', 'alcance', 'interacciones', 'likes_promedio'
            ]
            cols_order = [c for c in preferred_order if c in df_merged.columns]
            cols_order += [c for c in df_merged.columns if c not in cols_order]
            df_merged = df_merged.loc[:, cols_order]
            
            # Almacenar info de debug en session_state para mostrar al final
            if 'debug_merge_info' not in st.session_state:
                st.session_state.debug_merge_info = {}
            st.session_state.debug_merge_info = debug_info
            
            self._merged_cache = df_merged
            logger.debug(f"Datos fusionados: {len(df_merged)} registros (limpiados de NaN)")
        
        return self._merged_cache

    def invalidate_cache(self):
        """
        Invalida ambos cachés (local y st.cache_data).
        Se llama automáticamente después de escribir datos.
        """
        self._data_cache = None
        self._merged_cache = None
        self._comments_consolidated_cache = None
        try:
            st.cache_data.clear()
            logger.debug("Cache invalidado en DataProvider")
        except Exception as e:
            logger.warning(f"Error limpiando st.cache_data en DataProvider: {e}")

    def get_consolidated_comments(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Obtiene comentarios históricos consolidados desde Google Sheets.

        Args:
            force_reload: Si True, limpia caché y vuelve a consultar la hoja.

        Returns:
            pd.DataFrame: Comentarios consolidados normalizados y sin duplicados.
        """
        if force_reload:
            self._comments_consolidated_cache = None
            try:
                st.cache_data.clear()
            except Exception as e:
                logger.warning(f"No se pudo limpiar st.cache_data al recargar comentarios: {e}")

        if self._comments_consolidated_cache is None:
            try:
                from utils.sheets_connector import load_consolidated_comments

                self._comments_consolidated_cache = load_consolidated_comments()
                logger.info(
                    "✓ Comentarios consolidados cargados: %s registros",
                    len(self._comments_consolidated_cache),
                )
            except Exception as e:
                logger.error(f"Error cargando comentarios consolidados: {e}")
                self._comments_consolidated_cache = pd.DataFrame()

        return self._comments_consolidated_cache.copy()


# Instancia global singleton
data_provider = DataProvider()


# === Funciones públicas convenientes ===

def get_data(force_reload: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Obtiene datos cacheados.
    Equivalente a: data_provider.get_data(force_reload)
    """
    return data_provider.get_data(force_reload)


def get_merged_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Obtiene datos fusionados cacheados.
    Equivalente a: data_provider.get_merged_data(force_reload)
    """
    return data_provider.get_merged_data(force_reload)


def get_consolidated_comments(force_reload: bool = False) -> pd.DataFrame:
    """Obtiene base histórica de Comentarios Consolidados."""
    return data_provider.get_consolidated_comments(force_reload)