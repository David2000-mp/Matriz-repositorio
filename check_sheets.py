#!/usr/bin/env python3
import toml
from pathlib import Path
from google.oauth2.service_account import Credentials
import gspread

secrets_path = Path.home() / '.streamlit' / 'secrets.toml'
with open(secrets_path, 'r', encoding='utf-8') as f:
    secrets = toml.load(f)

sheet_id = secrets['general']['google_sheets_id']
print(f'📊 Google Sheet ID: {sheet_id}')

print('\n🔐 Autenticando...')
creds_info = secrets['gcp_service_account']
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
client = gspread.authorize(creds)
print('✅ Autenticación exitosa')

print('\n📂 Intentando abrir Google Sheet...')
try:
    spreadsheet = client.open_by_key(sheet_id)
    print(f'✅ Google Sheet abierto: "{spreadsheet.title}"')
    
    print('\n📄 Hojas disponibles:')
    for sheet in spreadsheet.worksheets():
        print(f'   - {sheet.title} ({sheet.row_count}x{sheet.col_count})')
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    print(f'\n⚠️ POSIBLES CAUSAS:')
    print(f'   1. No compartiste el sheet con: botmatrizv2@matriz-app-479304.iam.gserviceaccount.com')
    print(f'   2. El Sheet ID es incorrecto')
    print(f'   3. Elimina el acceso e intenta compartir nuevamente')
