"""
Script para revisar y actualizar interacciones automáticamente
basado en las reglas de la aplicación.
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
from utils.logger import get_logger

# Cargar variables de entorno
load_dotenv()

logger = get_logger(__name__)

# Configuración de Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_service_account_config():
    """Obtiene configuración de cuenta de servicio"""
    if os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true":
        # Streamlit Cloud
        import streamlit as st
        return st.secrets["gcp_service_account"]
    else:
        # Desarrollo local
        return {
            "type": "service_account",
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("GCP_CLIENT_EMAIL"),
            "client_id": os.getenv("GCP_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL")
        }

def get_sheets_connection():
    """Conecta a Google Sheets"""
    try:
        creds = Credentials.from_service_account_info(get_service_account_config(), scopes=SCOPES)
        client = gspread.authorize(creds)

        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        if not spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID no configurado")

        ss = client.open_by_key(spreadsheet_id)
        return ss
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}")
        return None

def revisar_actualizar_interacciones():
    """Revisa y actualiza interacciones según reglas de la aplicación"""

    ss = get_sheets_connection()
    if not ss:
        logger.error("No se pudo conectar a Google Sheets")
        return False

    try:
        # Obtener worksheet 'RespuestasForms'
        ws = ss.worksheet("RespuestasForms")
        records = ws.get_all_records()

        if not records:
            logger.info("La hoja 'RespuestasForms' está vacía")
            return True

        df = pd.DataFrame(records)

        # Limpiar espacios en columnas
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)

        # Renombrar columnas si es necesario
        rename_dict = {
            "Fecha del Reporte": "fecha",
            "Institución Marista": "entidad",
            "Plataforma Social": "plataforma",
            "Usuario o URL de la red": "usuario_red",
            "Seguidores Totales: Validación: Es un número > Mayor que 0": "seguidores",
            "Engagement Rate (%): Validación: Es un número > Entre 0 y 100": "engagement_rate",
            "Alcance Total": "alcance",
            "Interacciones Totales": "interacciones",
            "Comentarios Contextuales": "comentarios"
        }
        df.rename(columns=rename_dict, inplace=True)

        # Convertir tipos de datos
        cols_numericas = ['seguidores', 'alcance', 'interacciones', 'engagement_rate']
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Aplicar reglas de cálculo automático de interacciones
        cambios_realizados = 0

        # Regla 1: Calcular interacciones faltantes
        mask_calculable = (df['interacciones'] == 0) & (df['seguidores'] > 0) & (df['engagement_rate'] > 0)
        if mask_calculable.any():
            df.loc[mask_calculable, 'interacciones'] = (
                df.loc[mask_calculable, 'seguidores'] * df.loc[mask_calculable, 'engagement_rate']
            ) / 100
            df['interacciones'] = df['interacciones'].round().astype(int)
            cambios_realizados += mask_calculable.sum()
            logger.info(f"Calculadas {mask_calculable.sum()} interacciones faltantes")

        # Nota: No se calcula alcance automáticamente según las reglas de la aplicación

        # Agregar columna de validación
        df['error_validacion'] = ''

        # Validaciones
        if 'seguidores' in df.columns:
            invalid_seguidores = df['seguidores'] <= 0
            df.loc[invalid_seguidores, 'error_validacion'] = 'Seguidores Totales debe ser > 0'

        if 'engagement_rate' in df.columns:
            # Nota: Permitimos engagement > 100% ya que puede ocurrir en redes sociales
            invalid_engagement = (df['engagement_rate'] < 0)
            df.loc[invalid_engagement, 'error_validacion'] = 'Engagement Rate debe ser >= 0'

        if cambios_realizados > 0:
            # Preparar datos para actualizar
            headers = df.columns.tolist()
            data = [headers] + df.values.tolist()

            # Convertir fechas y limpiar valores
            for row in data[1:]:
                for i, val in enumerate(row):
                    if pd.isna(val):
                        row[i] = ''
                    elif isinstance(val, pd.Timestamp):
                        row[i] = val.strftime('%Y-%m-%d')

            # Actualizar hoja
            ws.clear()
            ws.update(data, range_name='A1')
            logger.info(f"Datos actualizados: {len(data)-1} filas, {cambios_realizados} cambios realizados")
            return True
        else:
            logger.info("No se realizaron cambios - datos ya están actualizados")
            return True

    except Exception as e:
        logger.error(f"Error revisando interacciones: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Iniciando revisión automática de interacciones...")

    success = revisar_actualizar_interacciones()

    if success:
        print("✅ Revisión completada exitosamente")
        print("Las interacciones han sido verificadas y actualizadas según las reglas de la aplicación.")
    else:
        print("❌ Error durante la revisión")