"""
DIAGNÓSTICO Y SOLUCIÓN - Problema con Instagram Interacciones Totales
======================================================================

PROBLEMA IDENTIFICADO:
├─ En el Dashboard Global, Instagram mostraba:
│  ├─ Seguidores totales: 6,166 ✓
│  ├─ Interacciones totales: 0 ✗
│  └─ Engagement: "No hay interacciones registradas en este período"
│
└─ CAUSA RAÍZ:
   ├─ Los datos estaban siendo ingresados en "Respuestas de formulario 3"
   ├─ Pero las hojas "cuentas" y "metricas" (fuentes principales) estaban vacías
   ├─ La columna "Interacciones Totales" estaba vacía en el formulario
   └─ No había importador de formulario para procesar esos datos

SOLUCIÓN IMPLEMENTADA:
1. Creado utils/form_response_importer.py
   ├─ Lee datos desde "Respuestas de formulario 3"
   ├─ Mapea columnas del formulario a estructura de cuentas y métricas
   ├─ Calcula Interacciones = (Engagement Rate / 100) * Seguidores
   ├─ Normaliza nombres de plataforma
   └─ Evita duplicados manteniendo registros más recientes

2. Actualizado utils/data_loader.py
   ├─ Si las hojas cuentas/métricas están vacías
   ├─ Intenta importar desde el formulario
   └─ Usa datos importados como fallback

3. Mejorado views/dashboard.py
   ├─ Función get_engagement_status() ahora acepta engagement_rate
   ├─ Si hay engagement_rate válido (>0), considera que hay datos suficientes
   ├─ No muestra mensaje de "sin interacciones" si hay engagement_rate
   └─ Actualiza todas las llamadas para pasar engagement_rate

VALIDACIÓN:
- Instagram ahora muestra correctamente:
  ├─ Seguidores totales: 6,166
  ├─ Interacciones totales: 290 (calculadas)
  └─ Engagement: 4.44% (promedio de los datos ingresados)

INSTRUCCIONES PARA EL USUARIO:
1. Continúa ingresando datos en "Respuestas de formulario 3"
   ├─ Institución Marista
   ├─ Plataforma Social
   ├─ Seguidores Totales (OBLIGATORIO)
   ├─ Engagement Rate (%) (OBLIGATORIO)
   ├─ Alcance Total (opcional)
   └─ Interacciones Totales (opcional - se calcula si no se ingresa)

2. Los datos se actualizarán en el dashboard cada 60 segundos
3. Puedes editar datos en cualquier momento en el formulario
4. Los datos se respaldan automáticamente en csvs locales

NOTAS TÉCNICAS:
- Las Interacciones se calculan como: (engagement_rate / 100) * seguidores
- El ID de cuenta se genera con: MD5("institución|plataforma|usuario")[:8]
- Se mantiene solo el registro más reciente por mes
- El cache de Streamlit se limpia cada 60 segundos para reflejar cambios

ARCHIVOS MODIFICADOS:
- utils/form_response_importer.py (NUEVO)
- utils/data_loader.py (actualizado)
- views/dashboard.py (actualizado)
"""
