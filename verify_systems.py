#!/usr/bin/env python3
"""
Script de verificación final de los sistemas para producción.
Verifica conectividad, columnas, dependencias y estado general.
"""

import sys
import subprocess
import pandas as pd
from pathlib import Path
from utils.schema_columns import COLS_CUENTAS, COLS_METRICAS

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

try:
    from utils.data_manager import conectar_sheets, COLS_CONFIG, COLS_COMENTARIOS, COLS_USERNAMES_EDITADOS
    from utils import load_data
    from utils.data_manager import load_comments, load_usernames_editados
    print('✅ Importaciones exitosas')
except ImportError as e:
    print(f'❌ Error en importaciones: {e}')
    sys.exit(1)

def verificar_dependencias():
    """Verifica que las dependencias estén instaladas."""
    required = ['streamlit', 'pandas', 'gspread', 'google']
    try:
        for pkg in required:
            __import__(pkg)
        print('✅ Dependencias verificadas')
        return True
    except ImportError as e:
        print(f'❌ Dependencia faltante: {e}')
        return False

def verificar_conectividad_sheets():
    """Verifica conectividad con Google Sheets."""
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet:
            print('✅ Conectividad con Google Sheets OK')
            return spreadsheet
        else:
            print('❌ Error conectando a Google Sheets')
            return None
    except Exception as e:
        print(f'❌ Error en conectividad: {e}')
        return None

def verificar_columnas(spreadsheet):
    """Verifica existencia de columnas necesarias en las hojas."""
    hojas_requeridas = {
        'cuentas': COLS_CUENTAS,
        'metricas': COLS_METRICAS,
        'config': COLS_CONFIG,
        'comentarios': COLS_COMENTARIOS,
        'usernames_editados': COLS_USERNAMES_EDITADOS
    }
    
    for hoja, cols in hojas_requeridas.items():
        try:
            sheet = spreadsheet.worksheet(hoja)
            headers = sheet.row_values(1) if sheet.row_count > 0 else []  # Primera fila o vacío
            if not headers:  # Si no hay headers, asumir que se crearán
                print(f'⚠️  Hoja {hoja} vacía - se crearán headers automáticamente')
                continue
            if not all(col in headers for col in cols):
                faltantes = [col for col in cols if col not in headers]
                print(f'❌ Columnas faltantes en {hoja}: {faltantes}')
                return False
            print(f'✅ Columnas OK en {hoja}')
        except Exception as e:
            if 'usernames_editados' in str(e):  # Hoja opcional, se crea si no existe
                print(f'⚠️  Hoja {hoja} no existe - se creará automáticamente')
                continue
            print(f'❌ Error verificando {hoja}: {e}')
            return False
    return True

def verificar_datos():
    """Verifica carga de datos y ausencia de datos de prueba."""
    try:
        cuentas, metricas = load_data()
        comentarios = load_comments()
        usernames = load_usernames_editados()
        
        print(f'✅ Cuentas cargadas: {len(cuentas)} registros')
        print(f'✅ Métricas cargadas: {len(metricas)} registros')
        print(f'✅ Comentarios cargados: {len(comentarios)} registros')
        print(f'✅ Usernames editados: {len(usernames)} registros')
        
        # Verificar datos de prueba
        test_cuentas = cuentas[cuentas['entidad'].str.contains('TEST|test|Colegio Test', na=False, case=False)]
        test_comentarios = comentarios[comentarios['entidad'].str.contains('TEST|test', na=False, case=False)]
        
        if len(test_cuentas) > 0 or len(test_comentarios) > 0:
            print(f'🧹 Datos de prueba restantes: {len(test_cuentas)} cuentas, {len(test_comentarios)} comentarios')
            return False
        else:
            print('✅ Sin datos de prueba')
            return True
    except Exception as e:
        print(f'❌ Error verificando datos: {e}')
        return False

def main():
    print('🔍 Verificación final del sistema para producción...\n')
    
    checks = [
        verificar_dependencias,
        lambda: verificar_conectividad_sheets() is not None,
        lambda: verificar_columnas(verificar_conectividad_sheets()),
        verificar_datos
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print('\n🎉 SISTEMA LISTO PARA PRODUCCIÓN')
        sys.exit(0)
    else:
        print('\n❌ Verificación fallida - Revisar errores arriba')
        sys.exit(1)

if __name__ == '__main__':
    main()