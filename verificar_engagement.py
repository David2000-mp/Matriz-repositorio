"""
Script para verificar y ajustar engagement rate automáticamente
basado en las reglas de la aplicación (máximo 20%).
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

def verificar_ajustar_engagement():
    """Verifica y ajusta engagement rate a máximo 20%"""

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

        # Verificar engagement > 20%
        cambios_realizados = 0

        if 'engagement_rate' in df.columns:
            mask_engagement_alto = df['engagement_rate'] > 20
            valores_altos = mask_engagement_alto.sum()

            if valores_altos > 0:
                logger.info(f"Encontrados {valores_altos} valores de engagement > 20%")

                # Mostrar valores antes del ajuste
                for idx, row in df[mask_engagement_alto].iterrows():
                    logger.info(f"  - {row.get('entidad', 'N/A')} - {row.get('plataforma', 'N/A')}: {row['engagement_rate']}%")

                # Ajustar a 20%
                df.loc[mask_engagement_alto, 'engagement_rate'] = 20.0
                cambios_realizados += valores_altos
                logger.info(f"Ajustados {valores_altos} valores de engagement a 20%")

                # Recalcular interacciones si es necesario
                # Si engagement fue ajustado, recalcular interacciones
                mask_recalcular = mask_engagement_alto & (df['seguidores'] > 0)
                if mask_recalcular.any():
                    df.loc[mask_recalcular, 'interacciones'] = (
                        df.loc[mask_recalcular, 'seguidores'] * df.loc[mask_recalcular, 'engagement_rate']
                    ) / 100
                    df['interacciones'] = df['interacciones'].round().astype(int)
                    logger.info(f"Recalculadas {mask_recalcular.sum()} interacciones después del ajuste de engagement")

        # Agregar columna de validación
        df['error_validacion'] = ''

        # Validaciones actualizadas
        if 'seguidores' in df.columns:
            invalid_seguidores = df['seguidores'] <= 0
            df.loc[invalid_seguidores, 'error_validacion'] = 'Seguidores Totales debe ser > 0'

        if 'engagement_rate' in df.columns:
            invalid_engagement = (df['engagement_rate'] < 0) | (df['engagement_rate'] > 20)
            df.loc[invalid_engagement, 'error_validacion'] = 'Engagement Rate debe estar entre 0 y 20'

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
            logger.info(f"Datos actualizados: {len(data)-1} filas, {cambios_realizados} ajustes realizados")
            return True
        else:
            logger.info("No se encontraron valores de engagement > 20% - datos ya están correctos")
            return True

    except Exception as e:
        logger.error(f"Error verificando engagement: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando engagement rate (máximo 20%)...")

    success = verificar_ajustar_engagement()

    if success:
        print("✅ Verificación completada exitosamente")
        print("Los valores de engagement han sido verificados y ajustados según la regla máxima del 20%.")
    else:
        print("❌ Error durante la verificación")