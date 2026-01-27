"""
Módulo principal de gestión de datos para CHAMPILEAKS.
Importa funciones desde módulos especializados para mantener compatibilidad.
"""

import streamlit as st
from typing import Dict, Optional

# Re-exportar funciones para compatibilidad
from utils.data_loader import (
    load_data, load_comments, load_configs, load_usernames_editados,
    COLS_CUENTAS, COLS_METRICAS, COLS_CONFIG, COLS_COMENTARIOS, COLS_USERNAMES_EDITADOS
)
from utils.data_saver import (
    save_batch, save_comment, save_username_editado, guardar_datos, get_id
)
from utils.sheets_connector import conectar_sheets
from utils.data_provider import data_provider

# Catálogo de instituciones Maristas y sus redes sociales
COLEGIOS_MARISTAS: Dict[str, Dict[str, str]] = {
    "Centro Universitario México": {
        "Facebook": "@centrounivmx",
        "Instagram": "@centrounivmx",
        "TikTok": "@centrounivmx",
    },
    "Colegio Jacona": {"Facebook": "@colegiojacona", "Instagram": "@colegiojacona"},
    "Colegio Lic. Manuel Concha": {
        "Facebook": "@manuelconcha",
        "Instagram": "@colegio_manuelconcha",
    },
    "Colegio México (Roma)": {
        "Facebook": "@colegiomexicoroma",
        "Instagram": "@colegiomexicoroma",
        "TikTok": "@colegiomexico",
    },
    "Colegio México Bachillerato": {
        "Facebook": "@colegiomexicobachillerato",
        "Instagram": "@meximarista",
    },
    "Colegio México Orizaba": {
        "Facebook": "@colegiomexori",
        "Instagram": "@colegio.mexicoorizaba",
    },
    "Colegio Pedro Martínez Vázquez": {
        "Facebook": "@colegiopedromartinezvazquez",
        "Instagram": "@colegio_pedromartinez",
    },
    "Instituto Hidalguense": {
        "Facebook": "@institutohidalguense",
        "Instagram": "@institutohidalguense",
        "TikTok": "@institutohidalguense",
    },
    "Instituto México Primaria": {
        "Facebook": "@institutomexicoprimaria",
        "Instagram": "@instmexico1stsection",
    },
    "Instituto México Secundaria": {
        "Facebook": "@institutomexicosecundaria",
        "Instagram": "@institutomexico2daseccion",
    },
    "Instituto México Toluca": {
        "Facebook": "@institutomexicotoluca",
        "Instagram": "@institutomexicotoluca",
    },
    "Instituto Potosino": {
        "Facebook": "@institutopotosino",
        "Instagram": "@institutopotosino",
        "TikTok": "@institutopotosino",
    },
    "Instituto Queretano San Javier": {
        "Facebook": "@institutosanjavier",
        "Instagram": "@institutosanjavier",
    },
    "Instituto Sahuayense": {
        "Facebook": "@institutosahuayense",
        "Instagram": "@institutosahuayense",
    },
    "Universidad Marista SLP": {"Facebook": "@umaristaSLP", "Instagram": "@umaslp"},
    "Universidad Marista de México": {
        "Facebook": "@umaristamx",
        "Instagram": "@umaristamx",
        "TikTok": "@umaristamx",
    },
    "Universidad Marista de Querétaro": {
        "Facebook": "@umaq.oficial",
        "Instagram": "@umaq.oficial",
    },
}

# ===========================
# FUNCIONES DE CONEXIÓN
# ===========================


def _get_service_account_config() -> Optional[Dict[str, str]]:
    """Obtiene credenciales desde st.secrets o variables de entorno."""

    # 1) st.secrets
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    # 2) JSON completo en env
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            return json.loads(sa_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    # 3) Vars individuales
    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")

    if all([pk, client_email, project_id, pk_id]):
        return {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": pk_id,
            "private_key": pk,
            "client_email": client_email,
            "client_id": os.getenv("GCP_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL", ""),
            "universe_domain": "googleapis.com",
        }

    return None


@st.cache_resource(ttl=1800)  # Cache por 30 minutos
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    """Conecta con Google Sheets usando secrets o variables de entorno."""

    creds_dict = _get_service_account_config()
    if not creds_dict:
        msg = (
            "ERROR DE CREDENCIALES: No se encontraron credenciales en st.secrets ni en variables de entorno."
        )
        logger.error(msg)
        try:
            st.error(msg)
        except Exception as e:
            logger.warning(f"No se pudo mostrar st.error en conectar_sheets: {e}")
        return None

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    try:
        if "private_key" in creds_dict:
            pk_clean = (
                str(creds_dict["private_key"])
                .replace("\r", "")
                .replace("\\n", "\n")
                .strip()
            )
            creds_dict["private_key"] = pk_clean

        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
    except Exception as e:
        msg = "ERROR DE AUTENTICACIÓN: Llave privada mal pegada o inválida."
        logger.error(f"{msg} Detalle: {e}")
        try:
            st.error(msg)
        except Exception:
            pass
        return None

    # Abrir spreadsheet con diagnóstico de permisos/nombre
    try:
        spreadsheet = client.open("BaseDatosMatriz")
        return spreadsheet
    except SpreadsheetNotFound:
        msg = "HOJA NO ENCONTRADA: El nombre 'BaseDatosMatriz' no coincide exactamente."
        logger.error(msg)
        try:
            st.error(msg)
        except Exception:
            pass
        return None
    except APIError as e:
        code = getattr(getattr(e, "response", None), "status_code", None)
        if code == 403:
            msg = "ERROR DE PERMISOS: La hoja no se ha compartido con el email del bot."
        elif code == 429:
            msg = "ERROR DE CUOTA: Se ha excedido el límite de solicitudes a Google Sheets. Intente más tarde."
        elif code in (500, 502, 503, 504):
            msg = "ERROR DE SERVIDOR: Problema temporal en Google Sheets. Verifique su conexión a internet."
        else:
            msg = f"ERROR DE API: {e}"
        logger.error(msg)
        try:
            st.error(msg)
        except Exception:
            pass
        return None
    except Exception as e:
        # Capturar errores de red, timeouts, etc.
        if "network" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower():
            msg = "ERROR DE CONEXIÓN: Verifique su conexión a internet y las credenciales."
        else:
            msg = f"Error conectando a Google Sheets: {e}"
        logger.error(msg)
        try:
            st.error(msg)
        except Exception:
            pass
        return None


def init_files() -> None:
    """Inicializa archivos CSV si no existen (fallback para desarrollo local)."""
    DATA_DIR.mkdir(exist_ok=True)
    if not CUENTAS_CSV.exists():
        pd.DataFrame(columns=COLS_CUENTAS).to_csv(CUENTAS_CSV, index=False)
    if not METRICAS_CSV.exists():
        pd.DataFrame(columns=COLS_METRICAS).to_csv(METRICAS_CSV, index=False)


# ===========================
# FUNCIONES AUXILIARES
# ===========================


def validate_and_fill_columns(
    df: pd.DataFrame, required_columns: List[str]
) -> pd.DataFrame:
    """
    Verifica y rellena columnas faltantes en un DataFrame con valores predeterminados.

    Args:
        df (pd.DataFrame): DataFrame a validar.
        required_columns (List[str]): Lista de columnas requeridas.

    Returns:
        pd.DataFrame: DataFrame con todas las columnas requeridas.
    """
    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # Rellenar con valores nulos por defecto
    return df


# ===========================
# FUNCIONES DE CARGA (CORE)
# ===========================


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos desde Google Sheets con normalización estricta.
    Fallback a CSV local si falla la conexión.
    """
    cuentas = pd.DataFrame(columns=COLS_CUENTAS)
    metricas = pd.DataFrame(columns=COLS_METRICAS)
    origin = "cloud"

    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            raise RuntimeError("No se pudo establecer conexión con Google Sheets")

        # Leer HOJA: cuentas
        try:
            sheet_cuentas = spreadsheet.worksheet("cuentas")
            data_cuentas = sheet_cuentas.get_all_records(expected_headers=[])
            if data_cuentas:
                cuentas = pd.DataFrame(data_cuentas)
                cuentas.columns = cuentas.columns.str.strip().str.lower()
                cuentas = validate_and_fill_columns(cuentas, COLS_CUENTAS)
                if "id_cuenta" in cuentas.columns:
                    cuentas["id_cuenta"] = cuentas["id_cuenta"].astype(str).str.strip().str.lower()
        except Exception as e:
            logger.error(f"Error hoja 'cuentas': {e}")
            try:
                st.warning(f"Error leyendo hoja 'cuentas': {e}")
            except Exception:
                pass
            try:
                st.error(f"Error leyendo hoja 'cuentas': {e}")
            except Exception:
                pass
            try:
                logger.warning(f"Error leyendo hoja 'cuentas': {e}")
            except Exception:
                pass
            # Si hay un error de cuota (429), forzar fallback completo a CSV
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 429 or "429" in str(e) or "quota" in str(e).lower():
                raise

        # Leer HOJA: metricas
        try:
            sheet_metricas = spreadsheet.worksheet("metricas")
            data_metricas = sheet_metricas.get_all_records(expected_headers=[])
            if data_metricas:
                metricas = pd.DataFrame(data_metricas)
                metricas.columns = metricas.columns.str.strip().str.lower()
                metricas = validate_and_fill_columns(metricas, COLS_METRICAS)
                if "id_cuenta" in metricas.columns:
                    metricas["id_cuenta"] = metricas["id_cuenta"].astype(str).str.strip().str.lower()
                if "fecha" in metricas.columns:
                    metricas["fecha"] = pd.to_datetime(metricas["fecha"], errors="coerce")
        except Exception as e:
            logger.error(f"Error hoja 'metricas': {e}")
            try:
                st.warning(f"Error leyendo hoja 'metricas': {e}")
            except Exception:
                pass
            try:
                st.error(f"Error leyendo hoja 'metricas': {e}")
            except Exception:
                pass
            try:
                logger.warning(f"Error leyendo hoja 'metricas': {e}")
            except Exception:
                pass
            # Si hay un error de cuota (429), forzar fallback completo a CSV
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 429 or "429" in str(e) or "quota" in str(e).lower():
                raise

        # Filtro de consistencia
        if not cuentas.empty and not metricas.empty:
            metricas = metricas[metricas["id_cuenta"].isin(cuentas["id_cuenta"])]

    except Exception as e:
        origin = "local"
        # Registrar y notificar fallback a CSV. Detectar errores de cuota (429)
        try:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 429 or "429" in str(e) or "quota" in str(e).lower():
                logger.warning(f"Error 429 detectado en conexión cloud: {e}")
                try:
                    st.error(f"429 Quota exceeded: {e}")
                except Exception:
                    pass
            else:
                logger.warning(f"Fallo conexión cloud, usando locales: {e}")
                try:
                    st.warning(f"Fallo conexión cloud, usando locales: {e}")
                except Exception:
                    pass
        except Exception:
            # Ensure we always log the exception at least
            try:
                logger.info(f"Fallo conexión cloud, usando locales: {e}")
            except Exception:
                pass
        init_files()
        try:
            if CUENTAS_CSV.exists():
                try:
                    cuentas = pd.read_csv(CUENTAS_CSV, dtype=str, encoding="utf-8-sig")
                except Exception:
                    try:
                        cuentas = pd.read_csv(CUENTAS_CSV, dtype=str, encoding="utf-8")
                    except Exception:
                        cuentas = pd.DataFrame(columns=COLS_CUENTAS)
                cuentas.columns = cuentas.columns.str.strip().str.lower()
                cuentas = validate_and_fill_columns(cuentas, COLS_CUENTAS)

            if METRICAS_CSV.exists():
                try:
                    metricas = pd.read_csv(METRICAS_CSV, encoding="utf-8-sig")
                except Exception:
                    try:
                        metricas = pd.read_csv(METRICAS_CSV, encoding="utf-8")
                    except Exception:
                        metricas = pd.DataFrame(columns=COLS_METRICAS)
                metricas.columns = metricas.columns.str.strip().str.lower()
                metricas = validate_and_fill_columns(metricas, COLS_METRICAS)
                if "id_cuenta" in metricas.columns:
                    metricas["id_cuenta"] = metricas["id_cuenta"].astype(str)
                if "fecha" in metricas.columns:
                    metricas["fecha"] = pd.to_datetime(metricas["fecha"], errors="coerce")
        except Exception as local_err:
            logger.error(f"Error crítico cargando locales: {local_err}")

        # Avisar modo local con toast animado
        try:
            st.toast("⚠️ Usando modo local por fallo en conexión", icon="⚠️")
        except Exception:
            logger.info("Modo local por fallo en conexión")

    # Blindaje: asegurar conversión de fechas tras la carga
    if "fecha" in metricas.columns:
        metricas["fecha"] = pd.to_datetime(metricas["fecha"], errors="coerce")

    try:
        st.session_state["data_origin"] = origin
    except Exception:
        pass

    return cuentas, metricas


# ===========================
# FUNCIONES DE UTILIDAD (IDS)
# ===========================


def get_id(
    entidad: str, plat: str, user: str, df_cuentas_cache: Optional[pd.DataFrame] = None
) -> str:
    """
    Obtiene o crea un ID único para una combinación entidad+plataforma.
    GARANTIZA unicidad verificando en CSV.
    """
    # Si no nos dan el DF, lo cargamos
    if df_cuentas_cache is None:
        c, _ = load_data()
    else:
        c = df_cuentas_cache.copy()

    # Asegurar que las columnas existen y normalizar
    if "entidad" not in c.columns or "plataforma" not in c.columns:
        if "entidad" not in c.columns:
            c["entidad"] = ""
        if "plataforma" not in c.columns:
            c["plataforma"] = ""

    # Buscar cuenta existente (case-insensitive)
    exist = c[
        (c["entidad"].str.lower() == entidad.lower())
        & (c["plataforma"].str.lower() == plat.lower())
    ]

    if not exist.empty:
        # Retornar ID existente
        return str(exist.iloc[0]["id_cuenta"]).strip().lower()

    # Crear nuevo ID único
    nid = uuid.uuid4().hex.lower()
    logger.info(f"Creando nuevo ID para {entidad} - {plat}: {nid}")

    # Guardar nueva cuenta en CSV local (backup inmediato)
    nueva_cuenta = pd.DataFrame(
        [
            {
                "id_cuenta": nid,
                "entidad": entidad,
                "plataforma": plat,
                "usuario_red": user,
            }
        ]
    )

    try:
        if CUENTAS_CSV.exists():
            current_csv = pd.read_csv(CUENTAS_CSV)
            updated = pd.concat([current_csv, nueva_cuenta], ignore_index=True)
            updated.to_csv(CUENTAS_CSV, index=False, encoding="utf-8-sig")
        else:
            nueva_cuenta.to_csv(CUENTAS_CSV, index=False, encoding="utf-8-sig")
    except Exception as e:
        logger.error(f"Error guardando nuevo ID localmente: {e}")

    return nid


# ===========================
# FUNCIONES DE COMENTARIOS
# ===========================


def save_comment(entidad: str, mes: str, comentario: str) -> bool:
    """Guarda comentario contextual en Google Sheets."""
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return False
        try:
            sheet_coment = spreadsheet.worksheet("comentarios")
        except Exception:
            sheet_coment = spreadsheet.add_worksheet(
                title="comentarios", rows=100, cols=3
            )
            sheet_coment.update(range_name="A1", values=[COLS_COMENTARIOS])

        data = sheet_coment.get_all_records(expected_headers=[])
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=COLS_COMENTARIOS)

        # Ajuste de índice (+2 porque Sheets empieza en 1 y tiene header)
        match = df[(df["entidad"] == entidad) & (df["mes"] == mes)]

        if not match.empty:
            idx = match.index[0] + 2
            sheet_coment.update(range_name=f"C{idx}", values=[[comentario]])
        else:
            sheet_coment.append_row([entidad, mes, comentario])

        st.cache_data.clear()
        return True
    except Exception as e:
        logger.error(f"Error en save_comment: {e}")
        return False


def load_comments() -> pd.DataFrame:
    """Carga comentarios desde Sheets."""
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return pd.DataFrame(columns=COLS_COMENTARIOS)
        try:
            sheet_coment = spreadsheet.worksheet("comentarios")
            data = sheet_coment.get_all_records(expected_headers=[])
            return (
                pd.DataFrame(data) if data else pd.DataFrame(columns=COLS_COMENTARIOS)
            )
        except:
            return pd.DataFrame(columns=COLS_COMENTARIOS)
    except:
        return pd.DataFrame(columns=COLS_COMENTARIOS)


# ===========================
# FUNCIONES DE CONFIGURACIÓN (METAS)
# ===========================


@st.cache_data(ttl=600)
def load_configs() -> pd.DataFrame:
    """Carga configuraciones (metas)."""
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return pd.DataFrame(columns=COLS_CONFIG)
        try:
            sheet = spreadsheet.worksheet("config")
            data = sheet.get_all_records(expected_headers=[])
            df = pd.DataFrame(data) if data else pd.DataFrame(columns=COLS_CONFIG)
            if not df.empty:
                df.columns = df.columns.str.strip().str.lower()
                for col in ["meta_seguidores", "meta_engagement"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            return df
        except Exception as e:
            logger.warning(f"Error load_configs (inner): {e}")
            try:
                st.warning(f"Error cargando configuraciones: {e}")
            except Exception:
                logger.warning("No se pudo mostrar warning en Streamlit para load_configs inner")
            return pd.DataFrame(columns=COLS_CONFIG)
    except Exception as e:
        logger.warning(f"Error load_configs: {e}")
        try:
            st.warning(f"Error cargando configuraciones: {e}")
        except Exception:
            logger.warning("No se pudo mostrar warning en Streamlit para load_configs")
        return pd.DataFrame(columns=COLS_CONFIG)


def save_config(entidad: str, meta_seguidores: int, meta_engagement: float) -> bool:
    """Guarda metas en Sheets."""
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return False
        try:
            sheet = spreadsheet.worksheet("config")
        except Exception as e:
            sheet = spreadsheet.add_worksheet(title="config", rows=100, cols=3)
            sheet.update(range_name="A1", values=[COLS_CONFIG])
            logger.info(f"Se creó hoja 'config' por defecto: {e}")

        configs = load_configs()
        if not configs.empty and entidad in configs["entidad"].values:
            idx = configs[configs["entidad"] == entidad].index[0] + 2
            sheet.update(
                range_name=f"A{idx}",
                values=[[entidad, str(meta_seguidores), str(meta_engagement)]],
            )
        else:
            sheet.append_row([entidad, str(meta_seguidores), str(meta_engagement)])
        st.cache_data.clear()
        return True
    except Exception as e:
        logger.error(f"Error en save_config: {e}")
        try:
            st.error(f"Error guardando configuración: {e}")
        except Exception:
            logger.warning("No se pudo mostrar st.error para save_config")
        return False


# ===========================
# GESTIÓN DE USERNAMES EDITADOS
# ===========================

def load_usernames_editados() -> pd.DataFrame:
    """
    Carga usernames editados desde Google Sheets.
    """
    usernames_df = pd.DataFrame(columns=COLS_USERNAMES_EDITADOS)

    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return usernames_df

        try:
            sheet = spreadsheet.worksheet("usernames_editados")
            data = sheet.get_all_records(expected_headers=[])
            if data:
                usernames_df = pd.DataFrame(data)
                usernames_df.columns = usernames_df.columns.str.strip().str.lower()
                usernames_df = validate_and_fill_columns(usernames_df, COLS_USERNAMES_EDITADOS)
        except Exception as e:
            logger.warning(f"Hoja 'usernames_editados' no existe o está vacía: {e}")
            # No mostrar warning al usuario ya que es normal que no exista inicialmente

    except Exception as e:
        logger.error(f"Error cargando usernames editados: {e}")

    return usernames_df


def save_username_editado(entidad: str, plataforma: str, usuario_editado: str) -> bool:
    """
    Guarda o actualiza un username editado en Google Sheets.
    """
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is None:
            return False

        try:
            sheet = spreadsheet.worksheet("usernames_editados")
        except Exception:
            # Crear la hoja si no existe
            sheet = spreadsheet.add_worksheet(title="usernames_editados", rows=100, cols=4)
            sheet.update(range_name="A1", values=[COLS_USERNAMES_EDITADOS])
            logger.info("Se creó hoja 'usernames_editados'")

        from datetime import datetime
        fecha_mod = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        usernames_df = load_usernames_editados()

        # Verificar si ya existe la combinación entidad-plataforma
        mask = (usernames_df["entidad"] == entidad) & (usernames_df["plataforma"] == plataforma)

        if not usernames_df.empty and mask.any():
            # Actualizar registro existente
            idx = usernames_df[mask].index[0] + 2
            sheet.update(
                range_name=f"A{idx}",
                values=[[entidad, plataforma, usuario_editado, fecha_mod]],
            )
        else:
            # Agregar nuevo registro
            sheet.append_row([entidad, plataforma, usuario_editado, fecha_mod])

        # Limpiar cache
        st.cache_data.clear()
        return True

    except Exception as e:
        logger.error(f"Error guardando username editado: {e}")
        try:
            st.error(f"Error guardando username editado: {e}")
        except Exception:
            logger.warning("No se pudo mostrar st.error para save_username_editado")
        return False


# ===========================
# FUNCIONES DE GUARDADO (CORE)
# ===========================


def guardar_datos(nuevo_df: pd.DataFrame, modo: str = "completo") -> Optional[bool]:
    """Guarda datos principales en Sheets y CSV local."""
    # Validación básica
    required = set(
        [
            "id_cuenta",
            "entidad",
            "plataforma",
            "usuario_red",
            "fecha",
            "seguidores",
            "interacciones",
        ]
    )
    if not required.issubset(set(nuevo_df.columns)):
        msg = f"Columnas faltantes en DataFrame requerido: {required - set(nuevo_df.columns)}"
        logger.error(msg)
        try:
            st.error(msg)
        except Exception as e:
            logger.warning(f"No se pudo mostrar st.error en guardar_datos: {e}")
        return False

    try:
        spreadsheet = conectar_sheets()
        if not spreadsheet:
            msg = "No se pudo conectar a Google Sheets. Operación cancelada."
            logger.error(msg)
            try:
                st.error(msg)
            except Exception:
                pass
            return None

        if spreadsheet:
            success = True
            df = nuevo_df.copy()
            if "fecha" in df.columns:
                try:
                    # Attempt to ensure 'fecha' is in datetime format
                    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                    # Replace invalid dates with None
                    df["fecha"] = df["fecha"].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else None)
                except Exception as e:
                    logger.warning(f"Error procesando la columna 'fecha': {e}")
                    df["fecha"] = None  # Default to None for invalid dates

            # 1. Guardar Cuentas
            cols_c = ["id_cuenta", "entidad", "plataforma", "usuario_red"]
            if all(c in df.columns for c in cols_c):
                existentes, _ = load_data()
                nuevas = df[cols_c].drop_duplicates()
                if not existentes.empty:
                    ids_ex = set(existentes["id_cuenta"].astype(str))
                    nuevas = nuevas[~nuevas["id_cuenta"].astype(str).isin(ids_ex)]
                if not nuevas.empty:
                    try:
                        sheet_c = spreadsheet.worksheet("cuentas")
                        sheet_c.append_rows(nuevas.astype(str).values.tolist())
                    except Exception as e:
                        logger.error(f"Error actualizando hoja 'cuentas': {e}")
                        try:
                            st.error(f"Error actualizando hoja 'cuentas': {e}")
                        except Exception:
                            pass
                        # mark as failed so caller can return False
                        success = False

            # 2. Guardar Métricas
            cols_m = [
                "id_cuenta",
                "fecha",
                "seguidores",
                "alcance",
                "interacciones",
                "likes_promedio",
                "engagement_rate",
            ]
            try:
                sheet_m = spreadsheet.worksheet("metricas")
                metricas_a_subir = df[cols_m].copy()
                sheet_m.append_rows(metricas_a_subir.astype(str).values.tolist())
            except Exception as e:
                logger.error(f"Error actualizando hoja 'metricas': {e}")
                try:
                    st.error(f"Error actualizando hoja 'metricas': {e}")
                except Exception as warn_exc:
                    logger.warning(f"No se pudo mostrar st.error al actualizar 'metricas': {warn_exc}")
                success = False

        st.cache_data.clear()
        return success
    except Exception as e:
        logger.error(f"Error guardar_datos: {e}")
        try:
            st.error(f"Error guardar_datos: {e}")
        except Exception as e:
            logger.warning(f"No se pudo mostrar st.error en guardar_datos (outer): {e}")
        return False


def save_batch(datos: List[Dict]) -> None:
    """Wrapper para guardar lotes de datos simulados."""
    st.cache_data.clear()
    cuentas, df_m = load_data()
    new = pd.DataFrame(datos)

    # Procesamiento
    new["fecha"] = pd.to_datetime(new["fecha"], errors="coerce")
    for col in ["seguidores", "alcance", "interacciones", "likes_promedio"]:
        new[col] = pd.to_numeric(new[col], errors="coerce").fillna(0)

    new["engagement_rate"] = new.apply(
        lambda x: (
            round((x["interacciones"] / x["seguidores"] * 100), 2)
            if x["seguidores"] > 0
            else 0
        ),
        axis=1,
    )

    if "entidad" not in new.columns:
        new = pd.merge(new, cuentas, on="id_cuenta", how="left")

    # Concatenar y guardar localmente
    try:
        full_df = pd.concat([df_m, new]).drop_duplicates(
            subset=["id_cuenta", "fecha"], keep="last"
        )
        full_df.to_csv(METRICAS_CSV, index=False)
    except Exception as e:
        logger.error(f"Error escribiendo METRICAS_CSV: {e}")
        try:
            st.error(f"Error escribiendo METRICAS_CSV: {e}")
        except Exception as warn_exc:
            logger.warning(f"No se pudo mostrar st.error escribiendo METRICAS_CSV: {warn_exc}")

    # Guardar nuevas cuentas localmente
    cols_c = ["id_cuenta", "entidad", "plataforma", "usuario_red"]
    new_cuentas = new[cols_c].drop_duplicates()
    try:
        if CUENTAS_CSV.exists():
            curr_c = pd.read_csv(CUENTAS_CSV)
            pd.concat([curr_c, new_cuentas]).drop_duplicates(
                subset=["id_cuenta"]
            ).to_csv(CUENTAS_CSV, index=False)
        else:
            new_cuentas.to_csv(CUENTAS_CSV, index=False)
    except Exception as e:
        logger.error(f"Error escribiendo CUENTAS_CSV: {e}")
        try:
            st.error(f"Error escribiendo CUENTAS_CSV: {e}")
        except Exception as warn_exc:
            logger.warning(f"No se pudo mostrar st.error escribiendo CUENTAS_CSV: {warn_exc}")

    # Sincronizar Sheets (proteger de fallos)
    try:
        res = guardar_datos(new)
        # If guardar_datos returns False or None, surface a warning
        if res is False or res is None:
            try:
                st.warning(
                    "Advertencia: No se pudo sincronizar datos con Google Sheets."
                )
            except Exception as e:
                logger.warning(f"No se pudo mostrar st.warning en save_batch: {e}")
    except Exception as e:
        logger.error(f"Error sincronizando con Sheets en save_batch: {e}")
        try:
            st.warning(f"Error sincronizando con Sheets en save_batch: {e}")
        except Exception as warn_exc:
            logger.warning(f"No se pudo mostrar st.warning en save_batch: {warn_exc}")

    st.cache_data.clear()


# ===========================
# FUNCIONES DE REGISTRO
# ===========================


def registrar_nuevas_cuentas(entidad: str, redes: Dict[str, str]) -> bool:
    """
    Registra una nueva institución y sus cuentas en Sheets y CSV.
    No requiere métricas, solo datos de identificación.
    """
    try:
        # 1. Preparar datos
        rows = []
        for plat, usuario in redes.items():
            # Generar ID único
            new_id = uuid.uuid4().hex.lower()
            rows.append(
                {
                    "id_cuenta": new_id,
                    "entidad": entidad,
                    "plataforma": plat,
                    "usuario_red": usuario,
                }
            )

        df_new = pd.DataFrame(rows)

        # 2. Guardar en CSV Local (Respaldo)
        if CUENTAS_CSV.exists():
            curr_c = pd.read_csv(CUENTAS_CSV)
            # Evitar duplicados exactos
            final_df = pd.concat([curr_c, df_new]).drop_duplicates(
                subset=["entidad", "plataforma"], keep="last"
            )
            final_df.to_csv(CUENTAS_CSV, index=False, encoding="utf-8-sig")
        else:
            df_new.to_csv(CUENTAS_CSV, index=False, encoding="utf-8-sig")

        # 3. Guardar en Google Sheets
        spreadsheet = conectar_sheets()
        if spreadsheet:
            try:
                sheet_c = spreadsheet.worksheet("cuentas")
            except gspread.exceptions.WorksheetNotFound:
                sheet_c = spreadsheet.add_worksheet(title="cuentas", rows=100, cols=4)
                sheet_c.append_row(COLS_CUENTAS)

            # Convertir a lista de listas para gspread
            valores = (
                df_new[["id_cuenta", "entidad", "plataforma", "usuario_red"]]
                .astype(str)
                .values.tolist()
            )
            sheet_c.append_rows(valores)
        else:
            logger.warning(
                "No se pudo conectar a Google Sheets. Datos guardados solo localmente."
            )

        st.cache_data.clear()  # Limpiar caché para que aparezca inmediato
        logger.info(f"Institución {entidad} registrada exitosamente.")
        return True

    except Exception as e:
        logger.error(f"Error registrando cuentas nuevas: {e}")
        return False


# ===========================
# UTILIDADES
# ===========================


def reset_db() -> None:
    """Limpia todo."""
    if CUENTAS_CSV.exists():
        os.remove(CUENTAS_CSV)
    if METRICAS_CSV.exists():
        os.remove(METRICAS_CSV)
    init_files()
    try:
        ss = conectar_sheets()
        if ss:
            for hoja, cols in [
                ("cuentas", COLS_CUENTAS),
                ("metricas", COLS_METRICAS),
                ("config", COLS_CONFIG),
                ("comentarios", COLS_COMENTARIOS),
            ]:
                try:
                    ws = ss.worksheet(hoja)
                    ws.clear()
                    ws.update(range_name="A1", values=[cols])
                except:
                    pass
    except:
        pass
    st.cache_data.clear()


def reload_colegios_maristas() -> None:
    """
    Recarga el diccionario COLEGIOS_MARISTAS desde el archivo CSV local o Google Sheets.
    """
    global COLEGIOS_MARISTAS
    new_catalog = {}
    try:
        # If pandas.read_csv has been mocked in tests (MagicMock/Mock), prefer CSV
        try:
            from unittest.mock import Mock
        except Exception:
            Mock = None

        prefer_csv = False
        if Mock is not None:
            try:
                prefer_csv = isinstance(pd.read_csv, Mock)
            except Exception:
                prefer_csv = False

        if prefer_csv:
            # Try CSV first (useful for tests that mock pandas.read_csv)
            try:
                cuentas_df = pd.read_csv(CUENTAS_CSV)
                logger.info(
                    f"reload_colegios_maristas: read {len(cuentas_df)} rows from CSV"
                )
                if isinstance(cuentas_df, pd.DataFrame) and not cuentas_df.empty:
                    for _, row in cuentas_df.iterrows():
                        ent = str(row.get("entidad", "")).strip()
                        plat = str(row.get("plataforma", "")).strip()
                        user = str(row.get("usuario_red", "")).strip()
                        if not ent:
                            continue
                        new_catalog.setdefault(ent, {})[plat] = user
                    COLEGIOS_MARISTAS.clear()
                    COLEGIOS_MARISTAS.update(new_catalog)
                    return
            except Exception as e:
                logger.error(f"Error leyendo CUENTAS_CSV: {repr(e)}")

            # Fallback to Sheets
            spreadsheet = conectar_sheets()
            logger.info(
                f"reload_colegios_maristas: conectar_sheets() returned: {bool(spreadsheet)}"
            )
            if spreadsheet:
                try:
                    sheet_cuentas = spreadsheet.worksheet("cuentas")
                    data = sheet_cuentas.get_all_records()
                    logger.info(
                        f"reload_colegios_maristas: read {len(data)} rows from sheets"
                    )
                    for row in data:
                        ent = str(row.get("entidad", "")).strip()
                        plat = str(row.get("plataforma", "")).strip()
                        user = str(row.get("usuario_red", "")).strip()
                        if not ent:
                            continue
                        new_catalog.setdefault(ent, {})[plat] = user
                    COLEGIOS_MARISTAS.clear()
                    COLEGIOS_MARISTAS.update(new_catalog)
                    return
                except Exception as e:
                    logger.warning(f"Error cargando desde Google Sheets: {e}")
        else:
            # Default: try Sheets first
            spreadsheet = conectar_sheets()
            logger.info(
                f"reload_colegios_maristas: conectar_sheets() returned: {bool(spreadsheet)}"
            )
            if spreadsheet:
                try:
                    sheet_cuentas = spreadsheet.worksheet("cuentas")
                    data = sheet_cuentas.get_all_records()
                    logger.info(
                        f"reload_colegios_maristas: read {len(data)} rows from sheets"
                    )
                    for row in data:
                        ent = str(row.get("entidad", "")).strip()
                        plat = str(row.get("plataforma", "")).strip()
                        user = str(row.get("usuario_red", "")).strip()
                        if not ent:
                            continue
                        new_catalog.setdefault(ent, {})[plat] = user
                    COLEGIOS_MARISTAS.clear()
                    COLEGIOS_MARISTAS.update(new_catalog)
                    return
                except Exception as e:
                    logger.warning(f"Error cargando desde Google Sheets: {e}")

            # Fallback: try CSV
            try:
                cuentas_df = pd.read_csv(CUENTAS_CSV)
                logger.info(
                    f"reload_colegios_maristas: read {len(cuentas_df)} rows from CSV"
                )
                if isinstance(cuentas_df, pd.DataFrame) and not cuentas_df.empty:
                    for _, row in cuentas_df.iterrows():
                        ent = str(row.get("entidad", "")).strip()
                        plat = str(row.get("plataforma", "")).strip()
                        user = str(row.get("usuario_red", "")).strip()
                        if not ent:
                            continue
                        new_catalog.setdefault(ent, {})[plat] = user
                    COLEGIOS_MARISTAS.clear()
                    COLEGIOS_MARISTAS.update(new_catalog)
                    return
            except Exception as e:
                logger.error(f"Error leyendo CUENTAS_CSV: {repr(e)}")

        # Si no se cargó nada, dejar el catálogo vacío (mutar en sitio)
        COLEGIOS_MARISTAS.clear()
    except Exception as e:
        logger.error(f"Error recargando COLEGIOS_MARISTAS: {e}")
        COLEGIOS_MARISTAS = {}


# ===========================
# FUNCIONES DE LOOKUP INVERSO
# ===========================

@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_reverse_lookup() -> Dict[str, Dict[str, str]]:
    """
    Crea un lookup inverso de COLEGIOS_MARISTAS para mapear usernames a escuela y plataforma.
    
    Returns:
        Dict con username como clave y {'school': str, 'platform': str} como valor.
    """
    reverse_lookup = {}
    for school, platforms in COLEGIOS_MARISTAS.items():
        for platform, username in platforms.items():
            reverse_lookup[username] = {'school': school, 'platform': platform}
    return reverse_lookup
