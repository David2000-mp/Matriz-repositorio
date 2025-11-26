# 🏗️ REFACTORIZACIÓN A ARQUITECTURA MODULAR - GUÍA COMPLETA

## 📋 Estado Actual

### ✅ Completado

1. **Estructura de Directorios**
   ```
   social_media_matrix/
   ├── utils/
   │   ├── __init__.py ✅
   │   ├── data_manager.py ✅ (Completo)
   │   └── helpers.py ✅ (Completo)
   ├── components/
   │   ├── __init__.py ✅
   │   └── styles.py ✅ (Completo)
   ├── views/
   │   ├── __init__.py ✅
   │   ├── landing.py ✅ (Completo)
   │   ├── dashboard.py ⚠️ (Esqueleto)
   │   ├── analytics.py ⚠️ (Esqueleto)
   │   ├── data_entry.py ⚠️ (Esqueleto)
   │   └── settings.py ⚠️ (Parcial)
   ├── app_refactored.py ✅ (Completo)
   └── app.py (Original - NO MODIFICAR)
   ```

2. **Módulos Completados**
   - ✅ `utils/data_manager.py`: Toda la lógica de datos (conectar_sheets, load_data, guardar_datos, etc.)
   - ✅ `utils/helpers.py`: Funciones utilitarias (imágenes, simulación, reportes HTML)
   - ✅ `components/styles.py`: CSS completo con inject_custom_css()
   - ✅ `views/landing.py`: Página de inicio con hero banner funcional
   - ✅ `app_refactored.py`: Punto de entrada con navegación lazy loading

### ⚠️ Pendiente

Las siguientes vistas tienen solo esqueletos y necesitan migración del código original:

1. **`views/dashboard.py`** 
   - Código fuente: `app.py` líneas 1102-1337
   - Funcionalidad: Dashboard global con KPIs, gráficos y filtros

2. **`views/analytics.py`**
   - Código fuente: `app.py` líneas 1337-1470
   - Funcionalidad: Análisis detallado por institución

3. **`views/data_entry.py`**
   - Código fuente: `app.py` líneas 1470-1549
   - Funcionalidad: Formulario de captura manual

4. **`views/settings.py`**
   - Código fuente: `app.py` líneas 1549-1631
   - Funcionalidad: Configuración avanzada (parcialmente implementado)

---

## 🛠️ CÓMO COMPLETAR LA MIGRACIÓN

### Paso 1: Migrar Dashboard (PRIORITARIO)

Abrir `views/dashboard.py` y reemplazar el contenido con:

```python
"""
Vista Dashboard Global para CHAMPILYTICS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import load_data, simular, save_batch, reset_db, generar_reporte_html
from components import COLOR_MAP

def render():
    """Renderiza el dashboard global con KPIs y visualizaciones."""
    st.title("DASHBOARD GLOBAL")
    st.caption("Red Marista • Análisis Consolidado")
    
    cuentas, metricas = load_data()
    logging.info(f"Dashboard - Cuentas: {len(cuentas)}, Métricas: {len(metricas)}")
    
    if not cuentas.empty and 'entidad' in cuentas.columns:
        entidades = cuentas['entidad'].dropna().unique().tolist()
        logging.info(f"Dashboard - Entidades en cuentas ({len(entidades)}): {sorted(entidades) if entidades else 'Ninguna'}")
    
    if metricas.empty:
        st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
        return

    # Merge con validación
    if cuentas.empty:
        st.error("❌ No hay información de cuentas.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resetear Base de Datos", use_container_width=True):
                with st.spinner('Reseteando...'):
                    reset_db()
                st.success("✅ Base de datos reseteada")
                st.rerun()
        with col2:
            if st.button("🎲 Generar Datos Demo (6 meses)", use_container_width=True):
                with st.spinner('Generando datos...'):
                    from utils.data_manager import COLEGIOS_MARISTAS
                    total_cuentas = sum(len(redes) for redes in COLEGIOS_MARISTAS.values())
                    save_batch(simular(n=total_cuentas * 6, colegios_maristas=COLEGIOS_MARISTAS))
                st.success("✅ Datos generados")
                st.rerun()
        return
    
    df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
    logging.info(f"Dashboard - Después del merge: {len(df)} registros, Entidades: {df['entidad'].nunique() if 'entidad' in df.columns else 'N/A'}")
    
    # COPIAR EL RESTO DEL CÓDIGO DESDE app.py LÍNEAS 1135-1337
    # Incluye:
    # - Verificación de merge exitoso
    # - Filtros (mes/año)
    # - KPIs con delta MoM
    # - Tabs con gráficos (pie, area, bar)
```

**Instrucción detallada:**
1. Abre `app.py` original en una ventana
2. Copia las líneas 1135-1337 (desde "# Verificar que el merge..." hasta antes de `def page_analisis_detalle()`)
3. Pégalas en `views/dashboard.py` después del merge
4. Asegúrate de que todas las importaciones necesarias estén en el encabezado

### Paso 2: Migrar Analytics

Seguir el mismo proceso para `views/analytics.py`:
- Fuente: `app.py` líneas 1337-1470
- Proceso: Copiar y pegar el cuerpo de `page_analisis_detalle()` en la función `render()`

### Paso 3: Migrar Data Entry

Para `views/data_entry.py`:
- Fuente: `app.py` líneas 1470-1549
- Proceso: Copiar el formulario completo de captura manual

### Paso 4: Completar Settings

Para `views/settings.py`:
- Fuente: `app.py` líneas 1549-1631
- Proceso: Ya tiene estructura básica, solo completar tabs faltantes

---

## 🚀 TESTING Y VALIDACIÓN

### Probar la App Refactorizada

```powershell
# Activar entorno virtual
.\venv_local\Scripts\Activate.ps1

# Ejecutar versión refactorizada
streamlit run app_refactored.py
```

### Checklist de Funcionalidad

- [ ] Landing page muestra seguidores totales
- [ ] Navegación entre páginas funciona sin errores
- [ ] Dashboard carga datos y muestra gráficos
- [ ] Analytics filtra por institución correctamente
- [ ] Captura manual guarda datos en Google Sheets
- [ ] Settings resetea y genera datos demo
- [ ] CSS personalizado se aplica correctamente
- [ ] No hay errores de importación en consola

---

## 📦 MIGRACIÓN FINAL

Una vez que todas las vistas estén completas y probadas:

### 1. Backup del Original

```powershell
# Renombrar archivo original
mv app.py app_legacy.py
```

### 2. Activar Versión Refactorizada

```powershell
# Renombrar versión nueva
mv app_refactored.py app.py
```

### 3. Actualizar Git

```powershell
git add .
git commit -m "refactor: Arquitectura modular limpia (utils, components, views)"
git push origin main
```

---

## 📚 ESTRUCTURA DE MÓDULOS

### `utils/data_manager.py`

**Responsabilidad:** Gestión de datos y conexiones

- `conectar_sheets()`: Conexión a Google Sheets
- `load_data()`: Carga de datos con caché
- `guardar_datos()`: Guardado optimizado con append_rows
- `save_batch()`: Guardado por lotes
- `get_id()`: Gestión de IDs únicos
- `reset_db()`: Reset completo de BD
- `COLEGIOS_MARISTAS`: Catálogo de instituciones

### `utils/helpers.py`

**Responsabilidad:** Utilidades generales

- `get_image_base64()`: Codificación de imágenes
- `load_image()`: Carga de imágenes locales
- `get_banner_css()`: Generación de CSS para banners
- `simular()`: Generación de datos sintéticos
- `generar_reporte_html()`: Reportes descargables

### `components/styles.py`

**Responsabilidad:** UI y estilos visuales

- `inject_custom_css()`: Inyección de CSS personalizado
- `COLOR_PRIMARY`, `COLOR_SECONDARY`, etc.: Constantes de color
- `COLOR_MAP`: Colores por plataforma social

### `views/*.py`

**Responsabilidad:** Páginas de la aplicación

Cada vista tiene una función `render()` que se invoca desde `app.py`

---

## 🔧 TROUBLESHOOTING

### Error: ModuleNotFoundError

```python
# Asegúrate de que __init__.py existe en cada directorio
# Y que los imports sean correctos:
from utils import load_data  # ✅ Correcto
from utils.data_manager import load_data  # ✅ También correcto
from data_manager import load_data  # ❌ Incorrecto
```

### Error: "X no está definido"

Verifica que todas las funciones/constantes importadas estén en `__all__` de `__init__.py`

### CSS no se aplica

Asegúrate de que `inject_custom_css()` se llama en `app.py` antes de renderizar vistas

---

## 🎯 BENEFICIOS DE LA ARQUITECTURA MODULAR

1. **Mantenibilidad**: Cada módulo tiene una responsabilidad clara
2. **Escalabilidad**: Fácil agregar nuevas vistas o funcionalidades
3. **Testing**: Módulos independientes se pueden testear aisladamente
4. **Colaboración**: Múltiples desarrolladores pueden trabajar en paralelo
5. **Lazy Loading**: Solo se cargan las vistas que se usan (optimización)
6. **Reutilización**: Funciones compartidas en utils y components

---

## 📞 CONTACTO Y SOPORTE

Si encuentras problemas durante la migración:

1. Revisa los logs en consola de Streamlit
2. Verifica que todas las dependencias estén instaladas
3. Compara con el código original en `app.py`
4. Consulta la documentación de Streamlit: https://docs.streamlit.io

---

**Última actualización**: 2024  
**Versión**: 2.0 (Arquitectura Modular)  
**Autor**: GitHub Copilot  
**Estado**: En Migración (60% completado)
