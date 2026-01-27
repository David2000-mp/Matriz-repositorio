import os
import sys
import pandas as pd

# Asegurar que el directorio raíz esté en sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from utils.data_loader import CUENTAS_CSV, COLS_CUENTAS
from utils.data_saver import sync_cuentas_to_sheets

print("🔄 Restaurando cuentas desde CSV a Google Sheets...")
if CUENTAS_CSV.exists():
    df = pd.read_csv(CUENTAS_CSV)
    if not df.empty:
        df = df[COLS_CUENTAS].copy()
        synced = sync_cuentas_to_sheets(df)
        print(f"✅ Sync {'exitosa' if synced else 'omitida'}: {len(df)} cuentas")
    else:
        print("⚠️ CSV de cuentas está vacío; no hay nada que sincronizar")
else:
    print("⚠️ No existe CSV de cuentas; no se puede restaurar")
