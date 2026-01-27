# 🔧 GUÍA DE CORRECCIÓN DE ERRORES

**Generado:** 8 de Enero de 2026

---

## ❌ Error 1: Tipo incorrecto en `save_batch()` líneas 239-240

### Problema Identificado

```python
# ❌ CÓDIGO ACTUAL (INCORRECTO)
seguidores = pd.to_numeric(df.get("seguidores", 0), errors="coerce").fillna(0)
interacciones = pd.to_numeric(df.get("interacciones", 0), errors="coerce").fillna(0)
```

**¿Por qué falla?**

- `df.get("seguidores", 0)` devuelve:
  - Un `pandas.Series` si la columna existe
  - Un escalar `0` (float) si NO existe
- `pd.to_numeric(0)` devuelve un float `0.0`
- No se puede hacer `.fillna()` en un float

### ✅ Solución 1: Verificar si columna existe (RECOMENDADO)

```python
# ✅ OPCIÓN A: Verificar existencia
try:
    seguidores = pd.to_numeric(df["seguidores"], errors="coerce").fillna(0)
except (KeyError, TypeError):
    seguidores = pd.Series([0] * len(df))

try:
    interacciones = pd.to_numeric(df["interacciones"], errors="coerce").fillna(0)
except (KeyError, TypeError):
    interacciones = pd.Series([0] * len(df))
```

### ✅ Solución 2: Usar `fillna()` en DataFrame directamente

```python
# ✅ OPCIÓN B: Más limpia
# Rellena columnas faltantes primero
df = df.fillna({
    "seguidores": 0,
    "interacciones": 0
})

seguidores = pd.to_numeric(df["seguidores"], errors="coerce").fillna(0)
interacciones = pd.to_numeric(df["interacciones"], errors="coerce").fillna(0)
```

### ✅ Solución 3: Usar método seguro

```python
# ✅ OPCIÓN C: Función auxiliar
def safe_numeric_fill(df, col_name, default=0):
    """Convierte columna a numérica con valor por defecto seguro."""
    if col_name not in df.columns:
        return pd.Series([default] * len(df))
    return pd.to_numeric(df[col_name], errors="coerce").fillna(default)

seguidores = safe_numeric_fill(df, "seguidores", 0)
interacciones = safe_numeric_fill(df, "interacciones", 0)
```

---

## ❌ Error 2: Tipo incorrecto en `guardar_datos()` línea 398

### Problema Identificado

```python
# ❌ CÓDIGO ACTUAL (TIPO INCORRECTO)
df_copy['fecha'] = df_copy['fecha'].dt.strftime('%Y-%m-%d')
```

**¿Por qué Pylance se queja?**

El type checker no reconoce que `.dt.strftime()` es válido en todas las versiones. Además, si `fecha` no es datetime, lanzará error.

### ✅ Solución: Validar tipo antes de convertir

```python
# ✅ SOLUCIÓN: Validar y convertir seguro
if 'fecha' in df_copy.columns:
    # Asegurar que es datetime
    if not pd.api.types.is_datetime64_any_dtype(df_copy['fecha']):
        df_copy['fecha'] = pd.to_datetime(df_copy['fecha'], errors='coerce')
    
    # Ahora convertir a string de forma segura
    df_copy['fecha'] = df_copy['fecha'].dt.strftime('%Y-%m-%d')
```

### Alternativa más robusta:

```python
# ✅ ALTERNATIVA: Aplicar función personalizada
def safe_date_format(date_value):
    """Convierte fecha a formato YYYY-MM-DD de forma segura."""
    if pd.isna(date_value):
        return None
    if isinstance(date_value, str):
        try:
            return pd.Timestamp(date_value).strftime('%Y-%m-%d')
        except:
            return date_value
    return pd.Timestamp(date_value).strftime('%Y-%m-%d')

if 'fecha' in df_copy.columns:
    df_copy['fecha'] = df_copy['fecha'].apply(safe_date_format)
```

---

## ⚠️ Error 3: Lógica de Deduplicación (Línea 271)

### Problema Identificado

```python
# ⚠️ PROBLEMA: Si fecha es string, deduplicación incompleta
combined_df = (
    combined_df.sort_values(by=['id_cuenta', 'fecha'])
               .drop_duplicates(subset=['id_cuenta', 'fecha'], keep='last')
)
```

**Escenario problemático:**
- Mismo id_cuenta, dos fechas: "2025-01-08" y "2025-01-08 10:30:00"
- Se consideran diferentes aunque es el MISMO día

### ✅ Solución: Normalizar fechas antes de deduplicar

```python
# ✅ SOLUCIÓN RECOMENDADA
if 'id_cuenta' in combined_df.columns and 'fecha' in combined_df.columns:
    # Paso 1: Convertir fecha a datetime
    try:
        combined_df['fecha'] = pd.to_datetime(combined_df['fecha'], errors='coerce')
    except Exception as e:
        logger.warning(f"No se pudo convertir fecha a datetime: {e}")
    
    # Paso 2: Crear fecha normalizada (solo YYYY-MM-DD)
    combined_df['fecha_normalizada'] = combined_df['fecha'].dt.normalize()
    
    # Paso 3: Deduplicar por fecha normalizada
    combined_df = (
        combined_df
        .sort_values(by=['id_cuenta', 'fecha'])
        .drop_duplicates(subset=['id_cuenta', 'fecha_normalizada'], keep='last')
        .drop(columns=['fecha_normalizada'])  # Eliminar columna temporal
    )
```

---

## ⚠️ Error 4: Política de Retorno Ambigua en `guardar_datos()` (Línea 430)

### Problema Identificado

```python
# ⚠️ CÓDIGO ACTUAL: Lógica confusa
if spreadsheet and not sheets_success:
    return False
return sheets_success or csv_success
```

**Problema:**
- Si solo CSV funciona (y Sheets fue intentado pero falló) → retorna `True` (falso positivo)
- Usuario cree que Sheets sincronizó pero solo CSV se guardó

### ✅ Solución: Retorno explícito

```python
# ✅ OPCIÓN A: Más clara - Retornar qué funcionó
result = {
    'sheets': sheets_success,
    'csv': csv_success,
    'overall_success': sheets_success or csv_success
}

# Informar al usuario explícitamente
if spreadsheet:
    if sheets_success:
        logger.info("✅ Sincronización a Google Sheets exitosa")
    elif sheets_error:
        logger.error("❌ Error en Google Sheets (pero CSV está respaldado)")
        try:
            st.warning("⚠️ No se pudo sincronizar a Sheets (datos guardados en CSV local)")
        except:
            pass

return result['overall_success']
```

### ✅ OPCIÓN B: Retornar solo si Sheets funcionó (más estricto)

```python
# ✅ OPCIÓN B: Política estricta
if spreadsheet:
    # Si había spreadsheet, DEBE tener éxito
    if not sheets_success:
        # Pero CSV fue respaldo
        logger.warning("Sheets falló pero CSV está disponible")
        return csv_success  # Retornar verdad de CSV
    return True
else:
    # Sin spreadsheet, confiar en CSV
    return csv_success
```

---

## 🛡️ Error 5: Falta de Reintentos en `sync_cuentas_to_sheets()` (Línea 72)

### Problema

```python
# ⚠️ ACTUAL: Sin reintentos
spreadsheet = conectar_sheets()
if not spreadsheet:
    logger.warning("No se pudo conectar a Google Sheets")
    return False
```

Si Sheets tiene un error temporal, falla inmediatamente.

### ✅ Solución: Agregar Reintentos

```python
# ✅ RECOMENDADO: Con reintentos
import time

def sync_cuentas_to_sheets(df_cuentas: pd.DataFrame, max_retries: int = 3) -> bool:
    """
    Sincroniza la tabla de cuentas a Google Sheets con reintentos.
    """
    for intento in range(max_retries):
        try:
            try:
                from utils import data_manager as dm
                spreadsheet = dm.conectar_sheets()
            except Exception:
                spreadsheet = None
            
            if not spreadsheet:
                if intento < max_retries - 1:
                    logger.warning(f"Intento {intento + 1}/{max_retries} fallido, reintentando...")
                    time.sleep(2 ** intento)  # Backoff exponencial: 1s, 2s, 4s
                    continue
                else:
                    logger.warning("No se pudo conectar a Google Sheets después de reintentos")
                    return False
            
            # ... resto del código de sincronización ...
            
            logger.info(f"✅ Sincronizadas {len(df_cuentas)} cuentas a Google Sheets")
            return True
            
        except Exception as e:
            if intento < max_retries - 1:
                logger.warning(f"Error en intento {intento + 1}/{max_retries}: {e}")
                time.sleep(2 ** intento)
            else:
                logger.error(f"Error final en sync_cuentas_to_sheets: {e}")
                return False
    
    return False
```

---

## 📋 Checklist de Implementación

### Paso 1: Corregir Error 1 (CRÍTICO)
- [ ] Reemplazar código en líneas 239-240 de `data_saver.py`
- [ ] Usar solución recomendada (Opción B)
- [ ] Ejecutar tests para validar

### Paso 2: Corregir Error 2 (CRÍTICO)
- [ ] Reemplazar código en línea 398 de `data_saver.py`
- [ ] Validar tipo de fecha antes de formatear
- [ ] Ejecutar tests

### Paso 3: Corregir Error 3 (IMPORTANTE)
- [ ] Normalizar fechas antes de deduplicar
- [ ] Convertir columna fecha a datetime
- [ ] Ejecutar tests con datos variados

### Paso 4: Corregir Error 4 (IMPORTANTE)
- [ ] Clarificar lógica de retorno en `guardar_datos()`
- [ ] Usar Opción A para máxima claridad
- [ ] Mejorar mensajes al usuario

### Paso 5: Mejorar Error 5 (BUENA PRÁCTICA)
- [ ] Agregar reintentos con backoff exponencial
- [ ] Mejorar logging de intentos
- [ ] Documentar cambios

---

## 🧪 Testing Recomendado

### Caso 1: DataFrame sin columnas requeridas
```python
df_test = pd.DataFrame({
    'id_cuenta': ['abc123']
    # Faltan: seguidores, interacciones, etc.
})
assert save_batch(df_test, "append") == False  # Debe fallar gracefully
```

### Caso 2: Fechas en formato string
```python
df_test = pd.DataFrame({
    'fecha': ['2025-01-08', '2025-01-08 10:30:00'],
    'id_cuenta': ['abc', 'def']
})
# Deduplicación debe funcionar correctamente
```

### Caso 3: Google Sheets no disponible
```python
# Mockear conectar_sheets para retornar None
with patch('utils.sheets_connector.conectar_sheets', return_value=None):
    result = save_batch(test_df)
    assert result == True  # Debe estar ok porque CSV funciona
```

---

## 📝 Notas Importantes

1. **No hay errores de sintaxis**, solo problemas de tipado y lógica
2. La app **funciona actualmente** a pesar de los errores
3. **Pylance** (type checker) solo reclama en 2 lugares
4. Los problemas lógicos pueden causar falsos positivos silenciosos

---

**Próximos Pasos:**
1. Aplicar correcciones en orden de criticidad
2. Ejecutar suite de tests
3. Actualizar documentación
4. Hacer release v2.1.1 con fixes

