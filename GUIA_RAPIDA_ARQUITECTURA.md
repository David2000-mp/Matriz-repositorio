# ⚡ GUÍA RÁPIDA - ARQUITECTURA REFACTORIZADA

**Status:** ✅ COMPLETADO  
**Fecha:** 8 Enero 2026

---

## 🎯 CAMBIOS PRINCIPALES (30 SEGUNDO SUMMARY)

### Problema Resuelto
- ❌ Importaciones circulares entre modules
- ❌ IDs convertidos erróneamente a números
- ❌ Caché no se invalida después de escribir

### Solución Implementada
- ✅ **Flujo unidireccional:** data_loader → data_manager ← data_saver
- ✅ **IDs protegidos:** Siempre `.astype(str)`, nunca `pd.to_numeric()`
- ✅ **Caché automático:** Cada escritura llama `st.cache_data.clear()`

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

```python
# ❌ ANTES (Problema)
from utils.data_manager import conectar_sheets  # En data_saver.py, línea 1
→ Importa data_manager
  → Importa data_saver
    → Importa data_manager (CIRCULAR ⚠️)

# ✅ DESPUÉS (Resuelto)
def guardar_datos(...):
    from utils.sheets_connector import get_sheets_connection  # Lazy, línea 200
    ss = get_sheets_connection()
    # Sin circular import ✅
```

---

## 🔑 FUNCIONES CRÍTICAS

| Función | Módulo | Propósito | IDs Seguros |
|---------|--------|----------|------------|
| `load_data()` | data_loader | Lee desde Sheets | ✅ |
| `get_id(e,p,u)` | data_saver | Genera MD5 string | ✅ |
| `guardar_datos(df)` | data_saver | Escribe + invalida caché | ✅ |
| `get_merged_data()` | data_provider | Fusion (metricas+cuentas) | ✅ |

---

## 💡 REGLAS DE ORO

### 1. IDs SIEMPRE Strings
```python
# ✅ Correcto
df['id_cuenta'] = df['id_cuenta'].astype(str).str.strip()
df = pd.read_csv(file, dtype={"id_cuenta": str})

# ❌ Nunca
df['id_cuenta'] = pd.to_numeric(df['id_cuenta'])
df['id_cuenta'] = df['id_cuenta'].astype(int)
```

### 2. Imports Lazy en data_manager/data_saver
```python
# ✅ Correcto (dentro de función)
def save_comment(...):
    from utils.data_saver import save_comment as _save_comment
    return _save_comment(...)

# ❌ Nunca (nivel de módulo)
from utils.data_saver import save_comment
```

### 3. Caché Invalidado Automáticamente
```python
# ✅ En data_saver.py: Cada función termina con
def _invalidate_caches():
    st.cache_data.clear()
    from utils.data_provider import data_provider
    data_provider.invalidate_cache()

if success:
    _invalidate_caches()  # Automático ✅
```

---

## 🔍 ESTRUCTURA NUEVA

```
utils/
├── data_loader.py       (LECTURA - load_data, load_comments, etc)
├── data_saver.py        (ESCRITURA - guardar_datos, save_comment, etc)
├── data_provider.py     (UNIFICADOR - get_merged_data, caché local)
├── data_manager.py      (HUB CENTRAL - COLEGIOS_MARISTAS, wrappers)
├── sheets_connector.py  (CONEXIÓN - get_sheets_connection)
└── __init__.py          (EXPORTA 23 funciones públicas)
```

### Flujo
```
app.py/views/
    ↓
from utils.data_manager import (...)
    ├─→ [LECTURA] load_data()
    ├─→ [ESCRITURA] guardar_datos(), save_batch(), save_comment()
    ├─→ [UNIFICACIÓN] data_provider.get_merged_data()
    └─→ [CATÁLOGO] COLEGIOS_MARISTAS (17 colegios)
```

---

## 📌 CASOS DE USO

### Caso 1: Cargar datos
```python
from utils import load_data

cuentas, metricas = load_data()  # Cacheado 300s
# IDs en ambos DataFrames: string ✅
```

### Caso 2: Guardar métricas
```python
from utils import guardar_datos

nuevo_df = ...  # DataFrame con métricas
success = guardar_datos(nuevo_df)
# Automáticamente: Sheets + CSV + caché invalidado ✅
```

### Caso 3: Obtener datos fusionados
```python
from utils.data_provider import data_provider

merged = data_provider.get_merged_data()
# merged['id_cuenta'] → todos strings ✅
# merged['entidad'] → nombres de colegios ✅
```

### Caso 4: Generar ID único
```python
from utils import get_id

account_id = get_id("Instituto México", "Facebook", "@inmx")
# account_id = "abc12345" (string) ✅
type(account_id) == str  # True ✅
```

---

## ⚠️ ERRORES COMUNES (EVITAR)

### Error 1: Convertir IDs a números
```python
# ❌ NO
df['id_cuenta'] = pd.to_numeric(df['id_cuenta'])

# ✅ SÍ
df['id_cuenta'] = df['id_cuenta'].astype(str)
```

### Error 2: Import circular de data_saver en módulo-level
```python
# ❌ NO (en data_saver.py, línea 1)
from utils.data_manager import conectar_sheets

# ✅ SÍ (dentro de función)
def guardar_datos(...):
    from utils.sheets_connector import get_sheets_connection
    ss = get_sheets_connection()
```

### Error 3: Olvidar invalidar caché
```python
# ❌ NO
def save_comment(...):
    ws.append_row([...])
    return True

# ✅ SÍ
def save_comment(...):
    ws.append_row([...])
    _invalidate_caches()  # Automático después
    return True
```

---

## 🧪 VERIFICACIÓN RÁPIDA

### ¿Todo funciona?
```bash
# Test 1: Imports sin error
python -c "from utils import load_data, save_batch, get_id"
# Si no hay error → ✅

# Test 2: ID es string
python -c "from utils import get_id; print(type(get_id('A','FB','u')).__name__)"
# Debe imprimir: str ✅

# Test 3: Load data con strings
python -c "from utils import load_data; c, m = load_data(); print(c['id_cuenta'].dtype)"
# Debe imprimir: object (string) ✅
```

---

## 📚 DOCUMENTACIÓN COMPLETA

- **ARQUITECTURA_REFACTORIZADA.md** - 259 líneas, documentación exhaustiva
- **VALIDACION_REFACTORIZACION.md** - Checklist de validación
- **Este archivo** - Guía rápida (referencia)

---

## 🎯 HOJA DE TRUCOS

### Imports Comunes
```python
# Opción 1: De utils (conveniente)
from utils import (
    load_data,
    save_batch,
    guardar_datos,
    COLEGIOS_MARISTAS,
)

# Opción 2: De data_manager (específico)
from utils.data_manager import load_data, save_batch

# Opción 3: De modules específicos
from utils.data_loader import load_data
from utils.data_saver import guardar_datos
from utils.data_provider import data_provider
```

### Patrones Comunes
```python
# Patrón 1: Lectura
cuentas, metricas = load_data()

# Patrón 2: Escritura con validación
nuevo_df = ...
if guardar_datos(nuevo_df):
    st.success("Guardado ✅")
else:
    st.error("Error al guardar")

# Patrón 3: Datos fusionados
from utils.data_provider import data_provider
merged = data_provider.get_merged_data(force_reload=False)
for idx, row in merged.iterrows():
    school = row['entidad']  # Nombre del colegio ✅
    followers = row['seguidores']

# Patrón 4: Generar y guardar ID
from utils import get_id, guardar_datos
new_id = get_id(school, platform, username)
# new_id → "abc12345" (string) ✅
```

---

## 🚀 EN PRODUCCIÓN

- ✅ **Cero imports circulares** - Validado
- ✅ **IDs protegidos como strings** - Validado  
- ✅ **Caché invalidado automáticamente** - Validado
- ✅ **17 colegios en catálogo** - Validado
- ✅ **Compatible con views/** - Validado

**LISTO PARA DEPLOY** 🎉

---

**Última actualización:** 8 Enero 2026  
**Mantenedor:** Arquitecto de Software
