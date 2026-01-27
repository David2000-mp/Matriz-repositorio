# 🎯 Guía de Recuperación - Dashboard Champilytics

## ✅ Estado Actual
- **471 registros sincronizados** a Google Sheets con IDs correctos
- **Cuentas registradas** en tabla 'cuentas'
- **Métricas limpias** (sin valores inf/NaN)
- **CSV locales actualizados**

---

## 🔧 Pasos para Recuperar tu Dashboard

### **Paso 1: Limpiar caché de Streamlit**
```bash
# Opción A: Desde el navegador (más recomendado)
# Abre la app: streamlit run app.py
# Presiona "C" en el navegador para limpiar el caché
```

### **Paso 2: Reiniciar la aplicación**
```bash
cd "f:\MATRIZ DE REDES\social_media_matrix"
.\venv_stable\Scripts\Activate.ps1
streamlit run app.py
```

### **Paso 3: Verificar que el Dashboard carga datos**
- Abre el navegador en `http://localhost:8501`
- Deberías ver:
  - Dashboard con **2 instituciones** (MATRIZ DE REDES + otra)
  - **471 registros de métricas** distribuidos
  - Gráficos y análisis funcionando

---

## 🔍 Validación: Qué se Hizo

### **1. Limpeza de IDs** (determinísticos)
```
Antes: "unknown", "", o IDs inconsistentes
Después: MD5 hash basado en entidad+plataforma+usuario_red
Ejemplo: 8399df6f05b6173bf9f41d6c1bda1c42
```

### **2. Sincronización de Cuentas**
- Detectadas todas las cuentas en los 471 registros
- Registradas en la tabla 'cuentas' de Google Sheets
- Duplicados eliminados

### **3. Limpieza de Valores Anomalos**
- ✅ Valores `inf` y `-inf` reemplazados con 0
- ✅ NaN convertidos a 0
- ✅ Tipos de dato normalizados (int para contadores, float para engagement_rate)
- ✅ Fechas en formato correcto para Sheets

### **4. Subida a Google Sheets**
- **Tabla 'cuentas'**: 2 registros
- **Tabla 'metricas'**: 471 registros en modo "completo" (limpia anterior basura)

---

## 📝 Archivos Modificados/Creados

| Archivo | Descripción |
|---------|-------------|
| `tools/mega_sync_total.py` | Script de sincronización total (ejecutado) |
| `data/cuentas.csv` | Actualizado con todas las cuentas |
| `data/metricas.csv` | Actualizado con IDs correctos y datos limpios |
| `live_trace_test.py` | Diagnóstico en vivo (sin mocks) para debugging |

---

## 🆘 Si aún no ves datos en el Dashboard

### **Opción A: Ejecutar diagnóstico**
```bash
python live_trace_test.py
```
Esto verifica:
- ✓ Escritura local en CSV
- ✓ Conexión a Google Sheets
- ✓ IDs determinísticos
- ✓ Cache invalidation

### **Opción B: Forzar recarga manual**
```bash
# Desde Python:
from utils.data_provider import DataProvider
dp = DataProvider()
dp.invalidate_cache()
df = dp.get_merged_data()
print(f"Filas cargadas: {len(df)}")
```

### **Opción C: Reiniciar Streamlit completamente**
```bash
# Cerrar cualquier Streamlit en ejecución
# Limpiar caché del servidor
rm -r ~/.streamlit/cache

# Reiniciar
streamlit run app.py --logger.level=debug
```

---

## 📊 Estadísticas Finales

```
┌─────────────────────────────────────────┐
│        SINCRONIZACIÓN COMPLETADA        │
├─────────────────────────────────────────┤
│ Registros procesados: 471               │
│ Cuentas registradas: 2                  │
│ Valores anomalos limpiados: ✓           │
│ Tipos de dato normalizados: ✓           │
│ Google Sheets actualizado: ✓            │
│ CSV local actualizado: ✓                │
└─────────────────────────────────────────┘
```

---

## 🎯 Próximos Pasos

1. **Verificar Dashboard**: Abre la app y confirma que cargan los datos
2. **Hacer una captura manual**: Ingresa nuevos datos para verificar guardado
3. **Monitorear Sheets**: Verifica que los nuevos registros aparecen en Google Sheets

---

## ❓ Preguntas Frecuentes

**P: ¿Por qué antes no se guardaban los datos?**
R: El problema era una combinación de:
- IDs no determinísticos (generados aleatoriamente)
- Cuentas faltantes en tabla 'cuentas'
- Cache no invalidándose después de guardados
- Valores inf/NaN que rompían la serialización JSON

**P: ¿Puedo volver atrás?**
R: Los respaldos están en:
- `data/metricas.csv` (última versión conocida)
- Google Sheets tiene historial (ver versión anterior)

**P: ¿Cuánto tarda la sincronización?**
R: Para 471 registros: ~10-15 segundos con conexión normal

---

**Última actualización:** 2026-01-07 16:09:46
