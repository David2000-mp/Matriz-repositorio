"""
Script para importar datos desde el CSV específico del usuario
con mapeo correcto de columnas.
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
from utils.logger import get_logger
from datetime import datetime

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

def importar_csv_formato_usuario(csv_path):
    """Importa datos desde el CSV específico del usuario"""

    try:
        # Leer CSV
        df = pd.read_csv(csv_path)
        logger.info(f"CSV cargado: {len(df)} filas")

        # Mostrar columnas encontradas
        logger.info(f"Columnas del CSV: {list(df.columns)}")

        # Mapeo de columnas del CSV a las de Google Sheets
        column_mapping = {
            "Marca temporal": "marca_temporal",  # Guardar como referencia
            "Selecciona el colegio:  ": "entidad",
            "Selecciona su Red Social ": "plataforma",
            "Engagment:": "engagement_rate",
            "Seguidores": "seguidores",
            "FECHA DE CAPTURA": "fecha",  # Esta es la fecha principal ahora
            "SUBIDO A FORMS": None  # Ignorar esta columna si existe
        }

        # Renombrar columnas
        df.rename(columns=column_mapping, inplace=True)

        # Eliminar columnas que deben ignorarse
        columns_to_drop = [col for col in df.columns if col is None or col == "SUBIDO A FORMS"]
        if columns_to_drop:
            df.drop(columns=columns_to_drop, inplace=True)

        # Convertir engagement de decimal a porcentaje
        if 'engagement_rate' in df.columns:
            # Convertir strings con coma a float
            df['engagement_rate'] = df['engagement_rate'].astype(str).str.replace(',', '.')
            df['engagement_rate'] = pd.to_numeric(df['engagement_rate'], errors='coerce')

            # Convertir de decimal a porcentaje (2.79 -> 279%)
            df['engagement_rate'] = df['engagement_rate'] * 100

            # Aplicar límite del 20%
            df.loc[df['engagement_rate'] > 20, 'engagement_rate'] = 20.0

        # Convertir seguidores a numérico
        if 'seguidores' in df.columns:
            df['seguidores'] = pd.to_numeric(df['seguidores'], errors='coerce').fillna(0).astype(int)

        # Agregar columnas faltantes
        df['alcance'] = 0  # Se dejará vacío para que lo complete el usuario
        df['interacciones'] = 0  # Se calculará automáticamente
        df['comentarios'] = ''
        df['usuario_red'] = ''  # No hay en el CSV

        # Calcular interacciones automáticamente
        mask_calculable = (df['seguidores'] > 0) & (df['engagement_rate'] > 0)
        if mask_calculable.any():
            df.loc[mask_calculable, 'interacciones'] = (
                df.loc[mask_calculable, 'seguidores'] * df.loc[mask_calculable, 'engagement_rate']
            ) / 100
            df['interacciones'] = df['interacciones'].round().astype(int)

        # Reordenar columnas según el formato esperado
        expected_columns = [
            "fecha", "entidad", "plataforma", "usuario_red",
            "seguidores", "engagement_rate", "alcance", "interacciones", "comentarios"
        ]

        # Filtrar solo las columnas que existen
        final_columns = [col for col in expected_columns if col in df.columns]
        df = df[final_columns]

        logger.info(f"Datos procesados: {len(df)} filas")
        logger.info(f"Columnas finales: {list(df.columns)}")

        # Conectar a Google Sheets
        ss = get_sheets_connection()
        if not ss:
            return False

        # Obtener worksheet 'RespuestasForms'
        ws = ss.worksheet("RespuestasForms")

        # Preparar datos para actualizar
        headers = df.columns.tolist()
        data = [headers] + df.values.tolist()

        # Limpiar valores NaN
        for row in data[1:]:
            for i, val in enumerate(row):
                if pd.isna(val):
                    row[i] = ''

        # Actualizar hoja
        ws.clear()
        ws.update(data, range_name='A1')

        logger.info(f"✅ Datos importados exitosamente: {len(data)-1} filas")
        return True

    except Exception as e:
        logger.error(f"Error importando CSV: {e}")
        return False

if __name__ == "__main__":
    # Ruta al CSV del usuario
    csv_path = r"c:\Users\david\Downloads\CAPTURA MANUAL DE LOS COLEGIOS (respuestas) - Respuestas de formulario 1.csv"

    print("🔄 Importando datos desde CSV del usuario...")

    success = importar_csv_formato_usuario(csv_path)

    if success:
        print("✅ Importación completada exitosamente")
        print("Los datos han sido procesados y subidos a Google Sheets con el formato correcto.")
    else:
        print("❌ Error durante la importación")