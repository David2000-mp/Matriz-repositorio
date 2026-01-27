"""
CHECKLIST DE VALIDACIÓN POST-SINCRONIZACIÓN

Ejecuta este script para validar que la sincronización fue exitosa.
"""

import sys
from pathlib import Path
import pandas as pd

def check(condition, message):
    """Imprime resultado de una verificación."""
    status = "✅" if condition else "❌"
    print(f"{status} {message}")
    return condition

def validate_all():
    all_pass = True
    
    print("=" * 70)
    print("VALIDACIÓN POST-SINCRONIZACIÓN")
    print("=" * 70)
    
    # 1. Archivos locales existen
    print("\n1. VALIDACIÓN DE ARCHIVOS LOCALES")
    print("-" * 70)
    
    cuentas_csv = Path("data/cuentas.csv")
    metricas_csv = Path("data/metricas.csv")
    
    all_pass &= check(cuentas_csv.exists(), f"data/cuentas.csv existe")
    all_pass &= check(metricas_csv.exists(), f"data/metricas.csv existe")
    
    if not cuentas_csv.exists() or not metricas_csv.exists():
        print("\n❌ Archivos CSV no encontrados. Abortar.")
        return False
    
    # 2. Contenido de CSV
    print("\n2. VALIDACIÓN DE CONTENIDO CSV")
    print("-" * 70)
    
    df_cuentas = pd.read_csv(cuentas_csv)
    df_metricas = pd.read_csv(metricas_csv)
    
    all_pass &= check(len(df_cuentas) > 0, f"Cuentas CSV no vacío: {len(df_cuentas)} filas")
    all_pass &= check(len(df_metricas) > 0, f"Metricas CSV no vacío: {len(df_metricas)} filas")
    all_pass &= check(len(df_metricas) == 471, f"Metricas CSV contiene 471 registros (actual: {len(df_metricas)})")
    
    # 3. Columnas requeridas
    print("\n3. VALIDACIÓN DE COLUMNAS")
    print("-" * 70)
    
    cols_cuentas = {'id_cuenta', 'entidad', 'plataforma', 'usuario_red'}
    cols_metricas = {'id_cuenta', 'fecha', 'seguidores', 'alcance', 
                     'interacciones', 'likes_promedio', 'engagement_rate'}
    
    all_pass &= check(
        cols_cuentas.issubset(df_cuentas.columns),
        f"Cuentas tiene todas las columnas requeridas: {cols_cuentas}"
    )
    all_pass &= check(
        cols_metricas.issubset(df_metricas.columns),
        f"Metricas tiene todas las columnas requeridas: {cols_metricas}"
    )
    
    # 4. Validación de tipos de datos
    print("\n4. VALIDACIÓN DE TIPOS DE DATOS")
    print("-" * 70)
    
    expected_types = {
        'id_cuenta': 'object',
        'fecha': 'object',
        'seguidores': 'int64',
        'alcance': 'int64',
        'interacciones': 'int64',
        'likes_promedio': 'int64',
        'engagement_rate': 'float64'
    }
    
    for col, expected_type in expected_types.items():
        if col in df_metricas.columns:
            actual_type = str(df_metricas[col].dtype)
            match = actual_type == expected_type
            all_pass &= check(
                match,
                f"{col}: {actual_type} (esperado: {expected_type})"
            )
    
    # 5. Validación de IDs determinísticos
    print("\n5. VALIDACIÓN DE IDS DETERMINÍSTICOS")
    print("-" * 70)
    
    ids_en_metricas = set(df_metricas['id_cuenta'].dropna().unique())
    ids_en_cuentas = set(df_cuentas['id_cuenta'].dropna().unique())
    
    all_pass &= check(
        len(ids_en_metricas) > 0,
        f"Metricas tiene {len(ids_en_metricas)} IDs únicos"
    )
    all_pass &= check(
        ids_en_metricas.issubset(ids_en_cuentas),
        f"Todos los IDs en metricas están registrados en cuentas"
    )
    
    # Verificar que IDs son determinísticos (MD5 hash, 32 caracteres)
    id_sample = df_metricas['id_cuenta'].iloc[0]
    is_md5 = isinstance(id_sample, str) and len(id_sample) == 32
    all_pass &= check(
        is_md5,
        f"IDs son hashes MD5 de 32 caracteres (ejemplo: {id_sample})"
    )
    
    # 6. Validación de valores anomalos
    print("\n6. VALIDACIÓN: SIN VALORES ANOMALOS")
    print("-" * 70)
    
    has_inf = False
    has_nan_numeric = False
    
    for col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']:
        if col in df_metricas.columns:
            col_has_inf = df_metricas[col].isin([float('inf'), float('-inf')]).any()
            col_has_nan = df_metricas[col].isna().sum() > 0
            
            has_inf |= col_has_inf
            has_nan_numeric |= col_has_nan
    
    all_pass &= check(not has_inf, "No hay valores inf o -inf en columnas numéricas")
    all_pass &= check(not has_nan_numeric, "No hay valores NaN en columnas numéricas")
    
    # 7. Validación de contenido
    print("\n7. VALIDACIÓN DE CONTENIDO")
    print("-" * 70)
    
    # Sample rows
    all_pass &= check(
        df_metricas['id_cuenta'].notna().all(),
        "Todos los registros de metricas tienen id_cuenta"
    )
    all_pass &= check(
        df_metricas['fecha'].notna().all(),
        "Todos los registros de metricas tienen fecha"
    )
    
    # 8. Validación de rangos
    print("\n8. VALIDACIÓN DE RANGOS DE DATOS")
    print("-" * 70)
    
    seg_min = df_metricas['seguidores'].min()
    seg_max = df_metricas['seguidores'].max()
    eng_min = df_metricas['engagement_rate'].min()
    eng_max = df_metricas['engagement_rate'].max()
    
    all_pass &= check(
        seg_min >= 0,
        f"Seguidores minimo >= 0: {seg_min}"
    )
    all_pass &= check(
        seg_max > 0,
        f"Seguidores maximo > 0: {seg_max}"
    )
    all_pass &= check(
        eng_min >= 0 and eng_max <= 100,
        f"Engagement rate en rango [0, 100]: min={eng_min:.2f}, max={eng_max:.2f}"
    )
    
    # 9. Resumen estadístico
    print("\n9. ESTADÍSTICAS RESUMEN")
    print("-" * 70)
    print(f"Instituciones/Cuentas: {len(df_cuentas)}")
    print(f"Registros de metricas: {len(df_metricas)}")
    print(f"Rango de fechas: {df_metricas['fecha'].min()} a {df_metricas['fecha'].max()}")
    print(f"Promedio seguidores: {df_metricas['seguidores'].mean():.0f}")
    print(f"Promedio engagement rate: {df_metricas['engagement_rate'].mean():.2f}%")
    
    # 10. Estado final
    print("\n" + "=" * 70)
    if all_pass:
        print("✅ TODAS LAS VALIDACIONES PASARON")
        print("\nProximos pasos:")
        print("1. Presiona 'C' en Streamlit para limpiar caché")
        print("2. Abre http://localhost:8501 en el navegador")
        print("3. Verifica que el Dashboard muestre 471 registros")
    else:
        print("❌ ALGUNAS VALIDACIONES FALLARON")
        print("\nRecomendaciones:")
        print("1. Ejecuta: python -m tools.mega_sync_total")
        print("2. Ejecuta: python live_trace_test.py")
        print("3. Revisa los logs para más detalles")
    print("=" * 70)
    
    return all_pass

if __name__ == "__main__":
    try:
        success = validate_all()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR durante validación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
