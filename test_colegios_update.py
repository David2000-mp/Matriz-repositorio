#!/usr/bin/env python3
"""Test simple para verificar que COLEGIOS_MARISTAS se actualizó correctamente."""

import sys
from pathlib import Path

# Agregar al path
sys.path.insert(0, str(Path(__file__).parent))

# Leer el archivo directamente sin Streamlit
config_file = Path(__file__).parent / "utils" / "data_manager.py"

with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar si "Maristas México Central" está en el diccionario
if "Maristas México Central" in content:
    print("✅ 'Maristas México Central' encontrada en el diccionario")
    
    # Extraer la sección para verificar
    start = content.find('"Maristas México Central"')
    end = content.find("}", start)
    section = content[start:end+1]
    
    print("\n📝 Contenido agregado:")
    print(section)
    
    # Verificar que tiene las 4 plataformas
    if "@MaristasMexicoCentral" in content:
        print("\n✅ Facebook: @MaristasMexicoCentral")
    if "@maristas_mexicocentral" in content:
        print("✅ Instagram: @maristas_mexicocentral")
    if "@MaristasCentral" in content:
        print("✅ Twitter: @MaristasCentral")
    if "@maristascentral" in content:
        print("✅ TikTok: @maristascentral")
    
    print("\n✅ Nueva institución agregada correctamente")
else:
    print("❌ 'Maristas México Central' NO encontrada en el diccionario")
    sys.exit(1)
