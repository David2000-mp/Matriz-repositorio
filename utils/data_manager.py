"""
Módulo de gestión de datos para CHAMPILYTICS.
Maneja conexiones a Google Sheets, carga y guardado de datos.
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Tuple, Optional, Dict, List
import os
import uuid

# Importar sistema de logging centralizado
from utils.logger import get_logger, log_exception

# Crear logger para este módulo
logger = get_logger(__name__)

# ===========================
# CONSTANTES DE DATOS
# ===========================

# Rutas de archivos CSV (fallback local)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CUENTAS_CSV = DATA_DIR / "cuentas.csv"
METRICAS_CSV = DATA_DIR / "metricas.csv"

# Columnas de las tablas
COLS_CUENTAS = ["id_cuenta", "entidad", "plataforma", "usuario_red"]
COLS_METRICAS = ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]

# Catálogo de instituciones Maristas y sus redes sociales
COLEGIOS_MARISTAS: Dict[str, Dict[str, str]] = {
    "Centro Universitario México": {
        "Facebook": "@centrounivmx",
        "Instagram": "@centrounivmx",
        "TikTok": "@centrounivmx"
    },
    "Colegio Jacona": {
        "Facebook": "@colegiojacona",
        "Instagram": "@colegiojacona"
    },
    "Colegio Lic. Manuel Concha": {
        "Facebook": "@manuelconcha",
        "Instagram": "@colegio_manuelconcha"
    },
    "Colegio México (Roma)": {
        "Facebook": "@colegiomexicoroma",
        "Instagram": "@colegiomexicoroma",
        "TikTok": "@colegiomexico"
    },
    "Colegio México Bachillerato": {
        "Facebook": "@colegiomexicobachillerato",
        "Instagram": "@meximarista"
    },
    "Colegio México Orizaba": {
        "Facebook": "@colegiomexori",
        "Instagram": "@colegio.mexicoorizaba"
    },
    "Colegio Pedro Martínez Vázquez": {
        "Facebook": "@colegiopedromartinezvazquez",
        "Instagram": "@colegio_pedromartinez"
    },
    "Instituto Hidalguense": {
        "Facebook": "@institutohidalguense",
        "Instagram": "@institutohidalguense",
        "TikTok": "@institutohidalguense"
    },
    "Instituto México Primaria": {
        "Facebook": "@institutomexicoprimaria",
        "Instagram": "@instmexico1stsection"
    },
    "Instituto México Secundaria": {
        "Facebook": "@institutomexicosecundaria",
        "Instagram": "@institutomexico2daseccion"
    },
    "Instituto México Toluca": {
        "Facebook": "@institutomexicotoluca",
        "Instagram": "@institutomexicotoluca"
    },
    "Instituto Potosino": {
        "Facebook": "@institutopotosino",
        "Instagram": "@institutopotosino",
        "TikTok": "@institutopotosino"
    },
    "Instituto Queretano San Javier": {
        "Facebook": "@institutosanjavier",
        "Instagram": "@institutosanjavier"
    },
    "Instituto Sahuayense": {
        "Facebook": "@institutosahuayense",
        "Instagram": "@institutosahuayense"
    },
    "Universidad Marista SLP": {
        "Facebook": "@umaristaSLP",
        "Instagram": "@umaslp"
    },
    "Universidad Marista de México": {
        "Facebook": "@umaristamx",
        "Instagram": "@umaristamx",
        "TikTok": "@umaristamx"
    },
    "Universidad Marista de Querétaro": {
        "Facebook": "@umaq.oficial",
        "Instagram": "@umaq.oficial"
    }
}

# ===========================
# FUNCIONES DE CONEXIÓN
# ===========================

@st.cache_resource(ttl=300)
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    """
    Conecta con Google Sheets usando credenciales de Streamlit secrets.
    
    Returns:
        Spreadsheet object o None si falla la conexión
    """
    try:
        # Validar que existen las credenciales antes de usarlas
        if "gcp_service_account" not in st.secrets:
            error_msg = "No se encontraron credenciales en st.secrets. Crea .streamlit/secrets.toml con gcp_service_account"
            logger.error(error_msg)
            st.error(f"❌ {error_msg}")
            return None
        
        # Definimos los permisos
        scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
        
        # Leemos las credenciales desde los secretos de Streamlit
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # Autorizamos
        client = gspread.authorize(creds)
        
        # Abrimos el documento completo (no solo sheet1)
        spreadsheet = client.open("BaseDatosMatriz")
        return spreadsheet
    except Exception as e:
        log_exception(logger, f"Error conectando a Google Sheets: {e}")
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return None


def init_files() -> None:
    """Inicializa archivos CSV si no existen (fallback para desarrollo local)."""
    DATA_DIR.mkdir(exist_ok=True)
    if not CUENTAS_CSV.exists():
        pd.DataFrame(columns=COLS_CUENTAS).to_csv(CUENTAS_CSV, index=False)
    if not METRICAS_CSV.exists():
        pd.DataFrame(columns=COLS_METRICAS).to_csv(METRICAS_CSV, index=False)


# ===========================
# FUNCIONES DE CARGA
# ===========================

@st.cache_data(ttl=600)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos desde Google Sheets con normalización estricta de IDs.
    
    NOTA DE ESCALABILIDAD:
    - get_all_records() descarga TODAS las filas de la hoja
    - Con 1 año de datos (>10,000 filas), esto causará timeouts
    - Solución futura: Migrar a BigQuery, PostgreSQL o filtrar por fecha en la query
    
    Returns:
        Tuple[DataFrame cuentas, DataFrame metricas]
    """
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is not None:
            # Leer HOJA 1: cuentas
            try:
                sheet_cuentas = spreadsheet.worksheet('cuentas')
                data_cuentas = sheet_cuentas.get_all_records(expected_headers=[])
                c = pd.DataFrame(data_cuentas) if data_cuentas else pd.DataFrame(columns=COLS_CUENTAS)
                
                # Limpiar nombres de columnas
                if not c.empty:
                    c.columns = c.columns.str.strip().str.lower()  # Normalizar nombres
                    # NORMALIZACIÓN CRÍTICA: Forzar string, quitar espacios, minúsculas
                    if 'id_cuenta' in c.columns:
                        c['id_cuenta'] = c['id_cuenta'].astype(str).str.strip().str.lower()
                    logger.info(f"Cuentas cargadas: {len(c)} registros")
            except Exception as e:
                logger.error(f"Error leyendo hoja 'cuentas': {e}")
                c = pd.DataFrame(columns=COLS_CUENTAS)
            
            # Leer HOJA 2: metricas
            try:
                sheet_metricas = spreadsheet.worksheet('metricas')
                data_metricas = sheet_metricas.get_all_records(expected_headers=[])
                m = pd.DataFrame(data_metricas) if data_metricas else pd.DataFrame(columns=COLS_METRICAS)
                
                if not m.empty:
                    # Limpiar nombres de columnas
                    m.columns = m.columns.str.strip().str.lower()  # Normalizar nombres
                    # NORMALIZACIÓN CRÍTICA: Forzar string, quitar espacios, minúsculas
                    if 'id_cuenta' in m.columns:
                        m['id_cuenta'] = m['id_cuenta'].astype(str).str.strip().str.lower()
                    
                    # Validar columnas necesarias
                    required_cols = ['id_cuenta', 'fecha']
                    if not all(col in m.columns for col in required_cols):
                        faltantes = set(required_cols) - set(m.columns)
                        st.error(f"❌ Columnas faltantes en hoja 'metricas': {', '.join(faltantes)}")
                        logger.error(f"Columnas faltantes: {faltantes}")
                        return c, pd.DataFrame(columns=COLS_METRICAS)

                    # LIMPIEZA DE FECHAS
                    m['fecha'] = m['fecha'].astype(str)
                    logger.debug(f"Primeras 3 fechas raw: {m['fecha'].head(3).tolist()}")
                    m['fecha'] = pd.to_datetime(m['fecha'], errors='coerce', format='%Y-%m-%d')
                    m = m.dropna(subset=['fecha'])

                    # LIMPIEZA NUMÉRICA
                    cols_numericas = ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
                    for col in cols_numericas:
                        if col in m.columns:
                            m[col] = m[col].astype(str).str.replace(',', '', regex=False)
                            m[col] = pd.to_numeric(m[col], errors='coerce').fillna(0)
                    
                    logger.info(f"Métricas cargadas: {len(m)} registros")
            except Exception as e:
                logger.error(f"Error leyendo hoja 'metricas': {e}")
                m = pd.DataFrame(columns=COLS_METRICAS)
            
            # FILTRO DE SEGURIDAD
            if not c.empty and not m.empty:
                m = m[m['id_cuenta'].isin(c['id_cuenta'])]
            
            return c, m

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error detallado leyendo Sheets: {error_msg}")
        
        # Manejo específico de error 429 (Quota exceeded)
        if "429" in error_msg or "Quota" in error_msg:
            st.error("⛔ Límite de Google API alcanzado. Espera 1 minuto y recarga la página.")
            logger.warning("Error 429: Quota de Google Sheets excedida")
        else:
            st.warning(f"⚠️ Error de lectura en la nube: {e}. Usando datos locales.")

    # --- FALLBACK A CSV LOCAL ---
    init_files()
    try:
        c = pd.read_csv(CUENTAS_CSV, dtype=str)
        if not c.empty:
            c.columns = c.columns.str.strip().str.lower()
            if 'id_cuenta' in c.columns:
                c['id_cuenta'] = c['id_cuenta'].astype(str).str.strip().str.lower()
        
        m = pd.read_csv(METRICAS_CSV)
        
        # Validar que CSV tiene datos
        if not m.empty:
            m.columns = m.columns.str.strip().str.lower()
            if 'id_cuenta' in m.columns:
                m['id_cuenta'] = m['id_cuenta'].astype(str).str.strip().str.lower()
            m['fecha'] = pd.to_datetime(m['fecha'], errors='coerce')
            m = m.dropna(subset=['fecha'])
            for col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']:
                if col in m.columns:
                    m[col] = pd.to_numeric(m[col], errors='coerce').fillna(0)
        
        # FILTRO DE SEGURIDAD
        if not c.empty and not m.empty:
            m = m[m['id_cuenta'].isin(c['id_cuenta'])]
            
        return c, m
    except Exception as e:
        return pd.DataFrame(columns=COLS_CUENTAS), pd.DataFrame(columns=COLS_METRICAS)


# ===========================
# FUNCIONES DE GUARDADO
# ===========================

def guardar_datos(nuevo_df: pd.DataFrame, modo: str = 'completo') -> bool:
    """
    Guarda datos en Google Sheets - Dos hojas separadas.
    
    Args:
        nuevo_df: DataFrame con los datos a guardar
        modo: 'completo' (reescribe todo) o 'append' (solo agrega nuevos)
    
    Returns:
        True si fue exitoso, False si hubo error
    """
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is not None:
            # Convertir fecha a string para Google Sheets
            df_to_save = nuevo_df.copy()
            if 'fecha' in df_to_save.columns:
                df_to_save['fecha'] = df_to_save['fecha'].dt.strftime('%Y-%m-%d')
            
            # GUARDAR EN HOJA 1: cuentas (sin duplicados) - MERGE CON EXISTENTES
            cols_cuentas = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
            if all(col in df_to_save.columns for col in cols_cuentas):
                # Cargar cuentas existentes
                cuentas_existentes, _ = load_data()
                
                # Extraer cuentas nuevas
                df_cuentas_nuevas = df_to_save[cols_cuentas].drop_duplicates().reset_index(drop=True)
                
                # Identificar SOLO las cuentas realmente nuevas (no duplicadas)
                if not cuentas_existentes.empty:
                    ids_existentes = set(cuentas_existentes['id_cuenta'].tolist())
                    cuentas_a_agregar = df_cuentas_nuevas[~df_cuentas_nuevas['id_cuenta'].isin(ids_existentes)]
                else:
                    cuentas_a_agregar = df_cuentas_nuevas
                
                # Agregar solo las nuevas (evita sobrescribir todo)
                if not cuentas_a_agregar.empty:
                    try:
                        sheet_cuentas = spreadsheet.worksheet('cuentas')
                        nuevas_filas = cuentas_a_agregar.astype(str).values.tolist()
                        sheet_cuentas.append_rows(nuevas_filas)
                        logger.info(f"Hoja 'cuentas': {len(cuentas_a_agregar)} cuentas nuevas agregadas")
                    except Exception as e:
                        logger.error(f"Error al actualizar 'cuentas': {e}")
                else:
                    logger.info("Hoja 'cuentas': No hay cuentas nuevas para agregar")
            
            # GUARDAR EN HOJA 2: metricas (OPTIMIZADO CON APPEND)
            cols_metricas = ['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
            if all(col in df_to_save.columns for col in cols_metricas):
                # 1. Cargar métricas existentes para no duplicar
                _, metricas_existentes = load_data()
                
                # 2. Crear columna clave única (ID + Fecha) para filtrar
                df_to_save['key'] = df_to_save['id_cuenta'] + df_to_save['fecha']
                if not metricas_existentes.empty:
                    metricas_existentes['key'] = metricas_existentes['id_cuenta'] + metricas_existentes['fecha'].astype(str)
                    keys_existentes = set(metricas_existentes['key'].tolist())
                else:
                    keys_existentes = set()

                # 3. Filtrar solo las filas que NO existen
                metricas_nuevas = df_to_save[~df_to_save['key'].isin(keys_existentes)].copy()
                
                # 4. Limpiar y preparar para subir
                metricas_nuevas = metricas_nuevas[cols_metricas]  # Quitar columna key temporal
                
                if not metricas_nuevas.empty:
                    try:
                        sheet_metricas = spreadsheet.worksheet('metricas')
                        datos_append = metricas_nuevas.astype(str).values.tolist()
                        sheet_metricas.append_rows(datos_append)  # <--- APPEND EN LUGAR DE CLEAR+UPDATE
                        logger.info(f"Hoja 'metricas': {len(metricas_nuevas)} registros nuevos agregados")
                    except Exception as e:
                        logger.error(f"Error append métricas: {e}")
                        raise
                else:
                    logger.info("No hay métricas nuevas para subir")
            
            st.cache_data.clear()
            return True
    except Exception as e:
        log_exception(logger, f"Error crítico en guardar_datos: {e}")
        st.error(f"❌ Error al guardar en Google Sheets: {e}")
        return False


def save_batch(datos: List[Dict]) -> None:
    """
    Guarda un lote de datos nuevos (wrapper que usa guardar_datos).
    
    Args:
        datos: Lista de diccionarios con los datos a guardar
    """
    # OPTIMIZACIÓN: Limpiar caché antes de cargar para evitar datos obsoletos
    st.cache_data.clear()
    
    cuentas, df_m = load_data()
    new = pd.DataFrame(datos)
    logger.info(f"save_batch - Nuevos datos: {len(new)} registros, Entidades únicas: {new['entidad'].nunique() if 'entidad' in new.columns else 'N/A'}")
    
    # Convertir fecha a datetime si no lo es
    new['fecha'] = pd.to_datetime(new['fecha'], errors='coerce')
    
    # Asegurar tipos numéricos
    for col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio']:
        new[col] = pd.to_numeric(new[col], errors='coerce').fillna(0)
    
    # Calcular engagement rate
    new['engagement_rate'] = new.apply(lambda x: round((x['interacciones']/x['seguidores']*100), 2) if x['seguidores']>0 else 0, axis=1)
    
    # Agregar información de cuenta si no existe (CRÍTICO para Google Sheets)
    if 'entidad' not in new.columns or 'plataforma' not in new.columns:
        new = pd.merge(new, cuentas, on='id_cuenta', how='left')
    
    # Eliminar duplicados (misma cuenta + misma fecha)
    if not df_m.empty and not new.empty:
        df_m['k'] = df_m['id_cuenta'] + df_m['fecha'].dt.strftime('%Y-%m-%d')
        new['k'] = new['id_cuenta'] + new['fecha'].dt.strftime('%Y-%m-%d')
        df_m = df_m[~df_m['k'].isin(new['k'])].drop(columns=['k'])
        new = new.drop(columns=['k'])
    
    # Concatenar y asegurar orden de columnas
    result = pd.concat([df_m, new], ignore_index=True).sort_values(['id_cuenta', 'fecha'])
    
    # Asegurar que todas las columnas necesarias existan
    cols_necesarias = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red', 'fecha', 
                       'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
    for col in cols_necesarias:
        if col not in result.columns:
            result[col] = '' if col in ['id_cuenta', 'entidad', 'plataforma', 'usuario_red'] else 0
    
    result = result[cols_necesarias]  # Ordenar columnas
    
    # OPTIMIZACIÓN: Primero guardar en CSV (rápido y sin límites)
    result.to_csv(METRICAS_CSV, index=False)
    
    # También guardar cuentas CSV (extraer y combinar con existentes)
    try:
        cols_cuentas = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
        cuentas_nuevas = result[cols_cuentas].drop_duplicates()
        
        # Leer cuentas existentes del CSV
        if os.path.exists(CUENTAS_CSV):
            cuentas_csv = pd.read_csv(CUENTAS_CSV, dtype=str)
            cuentas_completas = pd.concat([cuentas_csv, cuentas_nuevas], ignore_index=True)
            cuentas_completas = cuentas_completas.drop_duplicates(subset=['id_cuenta']).reset_index(drop=True)
        else:
            cuentas_completas = cuentas_nuevas
        
        cuentas_completas.to_csv(CUENTAS_CSV, index=False)
    except Exception as e:
        logger.error(f"Error guardando cuentas CSV: {e}")
    
    # Luego intentar sincronizar con Google Sheets (una sola operación)
    try:
        guardar_datos(result)
    except Exception as e:
        # Si falla Google Sheets, al menos ya tenemos el CSV guardado
        if "429" in str(e):
            st.warning("⚠️ Datos guardados localmente. Google Sheets temporalmente no disponible (límite de API).")
        else:
            st.warning(f"⚠️ Datos guardados localmente. Error al sincronizar con Google Sheets: {e}")
    
    # Limpiar caché después de guardar
    st.cache_data.clear()


# ===========================
# FUNCIONES DE UTILIDAD
# ===========================

def get_id(entidad: str, plat: str, user: str, df_cuentas_cache: Optional[pd.DataFrame] = None) -> str:
    """
    Obtiene o crea un ID único para una combinación entidad+plataforma.
    
    Args:
        entidad: Nombre de la institución
        plat: Plataforma (Facebook, Instagram, TikTok)
        user: Usuario de la red social
        df_cuentas_cache: DataFrame de cuentas pre-cargado (optimización)
    
    Returns:
        ID de cuenta (string)
    
    GARANTIZA unicidad verificando en CSV Y Google Sheets
    """
    # Si no nos dan el DF, lo cargamos (comportamiento legacy)
    if df_cuentas_cache is None:
        c, _ = load_data()
    else:
        c = df_cuentas_cache
    
    # Asegurar que las columnas existen y normalizar
    if 'entidad' not in c.columns or 'plataforma' not in c.columns:
        logger.warning("Columnas 'entidad' o 'plataforma' no encontradas en cuentas")
        c['entidad'] = c.get('entidad', '')
        c['plataforma'] = c.get('plataforma', '')
    
    # Buscar cuenta existente (case-insensitive para evitar duplicados por mayúsculas)
    exist = c[(c['entidad'].str.lower() == entidad.lower()) & 
              (c['plataforma'].str.lower() == plat.lower())]
    
    if not exist.empty:
        logger.debug(f"ID existente encontrado para {entidad} - {plat}")
        # Normalizar ID al retornarlo
        return str(exist.iloc[0]['id_cuenta']).strip().lower()
    
    # Crear nuevo ID único (normalizado desde el inicio)
    nid = uuid.uuid4().hex.lower()  # Siempre en minúsculas
    logger.info(f"Creando nuevo ID para {entidad} - {plat}: {nid}")
    
    # Guardar nueva cuenta en CSV local (backup)
    nueva_cuenta = pd.DataFrame([{
        "id_cuenta": nid, 
        "entidad": entidad, 
        "plataforma": plat, 
        "usuario_red": user
    }])
    c_actualizado = pd.concat([c, nueva_cuenta], ignore_index=True)
    c_actualizado.to_csv(CUENTAS_CSV, index=False)
    
    return nid


def reset_db() -> None:
    """Resetea toda la base de datos (CSV local y Google Sheets)."""
    # Limpiar CSV local
    if CUENTAS_CSV.exists():
        os.remove(CUENTAS_CSV)
    if METRICAS_CSV.exists():
        os.remove(METRICAS_CSV)
    
    init_files()
    
    # Limpiar Google Sheets
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet:
            # Limpiar hoja 'cuentas'
            try:
                sheet_cuentas = spreadsheet.worksheet('cuentas')
                sheet_cuentas.clear()
                headers_cuentas = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
                sheet_cuentas.update('A1', [headers_cuentas])
                logger.info("Hoja 'cuentas' reseteada")
            except Exception as e:
                logger.error(f"Error reseteando 'cuentas': {e}")
            
            # Limpiar hoja 'metricas'
            try:
                sheet_metricas = spreadsheet.worksheet('metricas')
                sheet_metricas.clear()
                headers_metricas = ['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
                sheet_metricas.update('A1', [headers_metricas])
                logger.info("Hoja 'metricas' reseteada")
            except Exception as e:
                logger.error(f"Error reseteando 'metricas': {e}")
    except Exception as e:
        logger.error(f"Error general reseteando Google Sheets: {e}")
    
    st.cache_data.clear()
    st.cache_resource.clear()
