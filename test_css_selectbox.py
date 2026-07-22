"""
Script para verificar que el CSS de selectboxes se genera correctamente
"""

from utils.theme_styles import get_theme_css

# Generar CSS
css = get_theme_css()

# Buscar reglas críticas
print("=" * 80)
print("VERIFICACIÓN DE CSS - SELECTBOXES EN SIDEBAR")
print("=" * 80)

# 1. Verificar que NO existe el selector universal problemático
if 'section[data-testid="stSidebar"] *,' in css and 'color: #FFFFFF !important' in css:
    print("\n❌ PROBLEMA: Selector universal encontrado (puede causar texto blanco)")
    # Buscar la línea exacta
    lines = css.split('\n')
    for i, line in enumerate(lines):
        if 'section[data-testid="stSidebar"] *,' in line:
            print(f"   Línea {i}: {line.strip()}")
else:
    print("\n✅ OK: No se encontró selector universal problemático")

# 2. Verificar reglas de selectbox con texto negro
print("\n" + "=" * 80)
print("REGLAS DE SELECTBOX (deben tener color: #212529)")
print("=" * 80)

selectbox_rules = [
    'section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]',
    'color: #212529 !important',
]

for rule in selectbox_rules:
    if rule in css:
        print(f"✅ Encontrado: {rule}")
    else:
        print(f"❌ NO encontrado: {rule}")

# 3. Extraer sección completa de selectboxes
print("\n" + "=" * 80)
print("SECCIÓN COMPLETA DE SELECTBOXES EN SIDEBAR")
print("=" * 80)

lines = css.split('\n')
in_selectbox_section = False
selectbox_section = []

for line in lines:
    if '=== SELECTBOXES EN SIDEBAR ===' in line:
        in_selectbox_section = True
    
    if in_selectbox_section:
        selectbox_section.append(line)
        
    if in_selectbox_section and '=== RADIO BUTTONS EN SIDEBAR ===' in line:
        break

for line in selectbox_section[:50]:  # Primeras 50 líneas
    print(line)

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)

# Contar cuántas veces aparece color: #FFFFFF vs color: #212529 en el sidebar
sidebar_section = css[css.find('=== SIDEBAR INSTITUCIONAL ==='):css.find('=== CARDS Y CONTENEDORES ===')]
white_count = sidebar_section.count('color: #FFFFFF')
black_count = sidebar_section.count('color: #212529')

print(f"\nEn la sección SIDEBAR:")
print(f"  - Reglas con 'color: #FFFFFF': {white_count}")
print(f"  - Reglas con 'color: #212529': {black_count}")

print("\n✅ Si ves reglas de selectbox con 'color: #212529', el CSS está correcto")
print("✅ El problema estaba en el selector universal que ahora debe estar excluido")
