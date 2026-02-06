"""
Script temporal para debugging de fechas
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_service_account_config():
    return {
        'type': 'service_account',
        'project_id': os.getenv('GCP_PROJECT_ID'),
        'private_key_id': os.getenv('GCP_PRIVATE_KEY_ID'),
        'private_key': os.getenv('GCP_PRIVATE_KEY').replace('\\n', '\n'),
        'client_email': os.getenv('GCP_CLIENT_EMAIL'),
        'client_id': os.getenv('GCP_CLIENT_ID'),
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': os.getenv('GCP_CLIENT_X509_CERT_URL')
    }

creds = Credentials.from_service_account_info(get_service_account_config(), scopes=SCOPES)
client = gspread.authorize(creds)
ss = client.open_by_key(os.getenv('GOOGLE_SHEETS_ID'))
ws = ss.worksheet('RespuestasForms')

print('=== ANALIZANDO VALORES DE FECHA ===')

records = ws.get_all_records()
df = pd.DataFrame(records)

print('Valores únicos en columna fecha:')
unique_fechas = df['fecha'].unique()
for fecha in unique_fechas[:15]:  # Mostrar primeros 15
    print(f'  "{fecha}" (tipo: {type(fecha)})')

print(f'\nTotal valores únicos: {len(unique_fechas)}')

# Verificar formato de fechas
print('\n=== ANÁLISIS DE FORMATOS ===')
for fecha in unique_fechas[:10]:
    try:
        # Intentar diferentes formatos
        parsed = pd.to_datetime(fecha, errors='coerce', dayfirst=True)
        if pd.isna(parsed):
            parsed = pd.to_datetime(fecha, errors='coerce', format='%d/%m/%Y')
        if pd.isna(parsed):
            parsed = pd.to_datetime(fecha, errors='coerce')
        print(f'"{fecha}" -> {parsed} ({"OK" if not pd.isna(parsed) else "ERROR"})')
    except Exception as e:
        print(f'"{fecha}" -> ERROR: {e}')

# Verificar si hay valores que podrían estar causando el problema
print('\n=== VALORES PROBLEMÁTICOS ===')
for fecha in unique_fechas:
    if '/' in str(fecha):
        parts = str(fecha).split('/')
        if len(parts) >= 3:
            day, month, year = parts[0], parts[1], parts[2]
            if len(day) > 2 or len(month) > 2 or len(year) != 4:
                print(f'Formato sospechoso: "{fecha}"')