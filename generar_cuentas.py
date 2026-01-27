"""
Script para generar cuentas desde el catálogo COLEGIOS_MARISTAS
y sincronizarlas a Google Sheets
"""

import pandas as pd
from utils.data_manager import COLEGIOS_MARISTAS, load_data, get_id, sync_cuentas_to_sheets
from utils.data_loader import CUENTAS_CSV

print("🏫 Generando cuentas desde catálogo COLEGIOS_MARISTAS...")
print(f"📚 Total instituciones: {len(COLEGIOS_MARISTAS)}")

# Cargar datos actuales para cache de IDs
cuentas_cache, _ = load_data()

cuentas = []
for entidad, redes in COLEGIOS_MARISTAS.items():
    print(f"  - {entidad}: {len(redes)} redes sociales")
    for plataforma, usuario in redes.items():
        id_cuenta = get_id(entidad, plataforma, usuario, df_cuentas_cache=cuentas_cache)
        cuentas.append({
            "id_cuenta": id_cuenta,
            "entidad": entidad,
            "plataforma": plataforma,
            "usuario_red": usuario,
        })

df_cuentas = pd.DataFrame(cuentas)
print(f"\n✅ Total cuentas generadas: {len(df_cuentas)}")

# Guardar en CSV local
print(f"\n💾 Guardando en {CUENTAS_CSV}...")
df_cuentas.to_csv(CUENTAS_CSV, index=False)
print("✅ Guardado en CSV local")

# Sincronizar a Google Sheets
print("\n☁️ Sincronizando a Google Sheets...")
resultado = sync_cuentas_to_sheets(df_cuentas)

if resultado:
    print("✅ ¡Cuentas sincronizadas exitosamente a Google Sheets!")
    print(f"\n📊 Resumen de cuentas:")
    print(df_cuentas.groupby('plataforma').size().to_string())
else:
    print("⚠️ No se pudo sincronizar a Google Sheets, pero están guardadas en CSV local")
