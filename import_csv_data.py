"""
Script para importar datos del CSV de respuestas manuales a Google Sheets.
Mapea las columnas del CSV al formato esperado por la aplicación.
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.engagement_validation import normalize_engagement_series

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

        # ID del spreadsheet (debe estar en .env o secrets)
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        if not spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID no configurado")

        ss = client.open_by_key(spreadsheet_id)
        return ss
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}")
        return None

def importar_datos_csv(csv_path):
    """Importa datos del CSV al formato de la aplicación"""

    # Leer CSV
    df_csv = pd.read_csv(csv_path)
    logger.info(f"Leído CSV con {len(df_csv)} filas")

    # Mapear columnas (con nombres exactos del CSV)
    column_mapping = {
        'Marca temporal': 'marca_temporal',
        'Selecciona el colegio:  ': 'entidad',  # Nota: dos espacios al final
        'Selecciona su Red Social ': 'plataforma',  # Un espacio al final
        'Engagment:': 'engagement_rate',  # Con dos 'g'
        'Seguidores': 'seguidores',
        'FECHA DE CAPTURA': 'fecha'
    }

    df_mapped = df_csv.rename(columns=column_mapping)

    # Limpiar y transformar datos
    df_mapped['entidad'] = df_mapped['entidad'].str.strip()
    df_mapped['plataforma'] = df_mapped['plataforma'].str.strip()

    # Normalización canónica: engagement en porcentaje [0, 100]
    df_mapped['engagement_rate'] = normalize_engagement_series(df_mapped['engagement_rate'])

    # Convertir seguidores
    df_mapped['seguidores'] = pd.to_numeric(df_mapped['seguidores'], errors='coerce')

    # Convertir fecha
    df_mapped['fecha'] = pd.to_datetime(df_mapped['fecha'], errors='coerce', dayfirst=True)

    # Agregar columnas faltantes con valores por defecto
    df_mapped['usuario_red'] = ''  # No hay en CSV
    df_mapped['alcance'] = 0       # No hay en CSV
    df_mapped['interacciones'] = 0 # No hay en CSV
    df_mapped['comentarios'] = ''  # No hay en CSV

    # Reordenar columnas al formato esperado
    expected_columns = [
        'marca_temporal', 'fecha', 'entidad', 'plataforma', 'usuario_red',
        'seguidores', 'engagement_rate', 'alcance', 'interacciones', 'comentarios'
    ]

    df_final = df_mapped[expected_columns]

    # Limpiar datos: eliminar filas con valores críticos faltantes
    df_final = df_final.dropna(subset=['entidad', 'plataforma', 'seguidores', 'fecha'])

    # Aplicar cálculos automáticos (como en la aplicación)
    # Cálculo de interacciones si faltan
    mask_calculable = (df_final['interacciones'] == 0) & (df_final['seguidores'] > 0) & (df_final['engagement_rate'] > 0)
    if mask_calculable.any():
        df_final.loc[mask_calculable, 'interacciones'] = (
            df_final.loc[mask_calculable, 'seguidores'] * (df_final.loc[mask_calculable, 'engagement_rate'] / 100)
        )
        df_final['interacciones'] = df_final['interacciones'].round().astype(int)

    # Estimar alcance si falta
    mask_alcance_vacio = (df_final['alcance'].isna()) | (df_final['alcance'] == 0)
    if 'seguidores' in df_final.columns:
        df_final.loc[mask_alcance_vacio, 'alcance'] = df_final.loc[mask_alcance_vacio, 'seguidores'] * 2.5

    logger.info(f"Datos procesados: {len(df_final)} filas válidas")

    return df_final

def subir_a_google_sheets(df, worksheet_name='RespuestasForms'):
    """Sube el DataFrame a Google Sheets"""

    ss = get_sheets_connection()
    if not ss:
        logger.error("No se pudo conectar a Google Sheets")
        return False

    try:
        # Obtener o crear worksheet
        try:
            ws = ss.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            ws = ss.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            logger.info(f"Creada nueva hoja: {worksheet_name}")

        # Limpiar hoja existente
        ws.clear()
        logger.info("Hoja limpiada")

        # Preparar datos para subida
        headers = df.columns.tolist()
        data = [headers] + df.values.tolist()

        # Convertir fechas a string
        for row in data[1:]:  # Saltar headers
            for i, val in enumerate(row):
                if pd.isna(val):
                    row[i] = ''
                elif isinstance(val, pd.Timestamp):
                    row[i] = val.strftime('%Y-%m-%d')

        # Subir datos
        ws.update(data, range_name='A1')
        logger.info(f"Datos subidos exitosamente: {len(data)-1} filas")

        return True

    except Exception as e:
        logger.error(f"Error subiendo datos: {e}")
        return False

if __name__ == "__main__":
    # Ruta al CSV (ajusta según tu ubicación)
    csv_path = r"c:\Users\david\Downloads\CAPTURA MANUAL DE LOS COLEGIOS (respuestas) - Respuestas de formulario 1.csv"

    print("🚀 Iniciando importación de datos CSV a Google Sheets...")

    # Importar y procesar datos
    df_importado = importar_datos_csv(csv_path)

    if df_importado.empty:
        print("❌ No se pudieron procesar los datos del CSV")
        exit(1)

    print(f"✅ Datos procesados: {len(df_importado)} filas")
    print("Vista previa de los primeros 5 registros:")
    print(df_importado.head().to_string())

    # Confirmar subida
    confirm = input("\n¿Deseas subir estos datos a Google Sheets? (s/n): ")
    if confirm.lower() == 's':
        success = subir_a_google_sheets(df_importado)
        if success:
            print("🎉 Datos subidos exitosamente a Google Sheets!")
            print("Ahora puedes ver los datos en la aplicación.")
        else:
            print("❌ Error al subir datos a Google Sheets")
    else:
        print("Operación cancelada.")