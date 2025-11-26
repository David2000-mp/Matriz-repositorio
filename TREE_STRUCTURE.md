# 🌳 ESTRUCTURA DE ARCHIVOS - CHAMPILYTICS v2.0

```
📁 social_media_matrix/
│
├── 📁 .streamlit/
│   ├── config.toml ✅                    # Configuración de tema y colores
│   └── secrets.toml                     # (Crear manualmente con credenciales)
│
├── 📁 utils/                            # MÓDULO: Lógica de Negocio
│   ├── __init__.py ✅                   # Exportaciones del paquete
│   ├── data_manager.py ✅               # Gestión de datos y Google Sheets
│   │   ├── conectar_sheets()           # Conexión con google-auth
│   │   ├── load_data()                 # Carga con caché (TTL=600s)
│   │   ├── guardar_datos()             # Guardado optimizado (append_rows)
│   │   ├── save_batch()                # Guardado por lotes
│   │   ├── get_id()                    # Gestión de IDs únicos
│   │   ├── reset_db()                  # Reset completo
│   │   └── COLEGIOS_MARISTAS           # Catálogo de 17 instituciones
│   │
│   └── helpers.py ✅                    # Utilidades generales
│       ├── get_image_base64()          # Codificación de imágenes
│       ├── load_image()                # Carga de imágenes locales
│       ├── get_banner_css()            # CSS para banners
│       ├── simular()                   # Generación de datos sintéticos
│       └── generar_reporte_html()      # Reportes descargables
│
├── 📁 components/                       # MÓDULO: UI y Estilos
│   ├── __init__.py ✅                   # Exportaciones del paquete
│   └── styles.py ✅                     # Estilos CSS personalizados
│       ├── inject_custom_css()         # Inyección de CSS
│       ├── COLOR_PRIMARY               # Azul Marista #003696
│       ├── COLOR_SECONDARY             # Azul oscuro #002566
│       └── COLOR_MAP                   # Colores por plataforma
│
├── 📁 views/                            # MÓDULO: Páginas de la App
│   ├── __init__.py ✅                   # Exportaciones del paquete
│   │
│   ├── landing.py ✅                    # Página de Inicio [100%]
│   │   └── render()                    # Hero banner + navegación rápida
│   │
│   ├── dashboard.py ⚠️                  # Dashboard Global [20%]
│   │   └── render()                    # KPIs + gráficos agregados
│   │       ├── TODO: Filtros período
│   │       ├── TODO: Pie chart (plataformas)
│   │       ├── TODO: Area chart (tendencia)
│   │       └── TODO: Bar chart (ranking)
│   │
│   ├── analytics.py ⚠️                  # Análisis Individual [20%]
│   │   └── render()                    # Análisis por institución
│   │       ├── TODO: Selector institución
│   │       ├── TODO: KPIs individuales
│   │       └── TODO: Gráficos evolución
│   │
│   ├── data_entry.py ⚠️                 # Captura Manual [20%]
│   │   └── render()                    # Formulario de ingreso
│   │       ├── TODO: Form completo
│   │       ├── TODO: Validación datos
│   │       └── TODO: Guardado + feedback
│   │
│   └── settings.py ⚠️                   # Configuración [60%]
│       └── render()                    # Admin y herramientas
│           ├── ✅ Simulador de datos
│           ├── ✅ Reset BD
│           ├── ✅ Catálogo instituciones
│           └── TODO: Diagnósticos avanzados
│
├── 📁 data/                             # Archivos CSV (fallback local)
│   ├── cuentas.csv
│   └── metricas.csv
│
├── 📁 images/                           # Recursos visuales
│   ├── logo_maristas.png
│   ├── banner_landing.jpg
│   └── icon_maristas.png
│
├── 📄 app.py                            # ORIGINAL [NO MODIFICAR]
│                                        # 1804 líneas - Versión monolítica
│
├── 📄 app_refactored.py ✅              # NUEVO - Punto de Entrada [100%]
│   ├── Configuración inicial
│   ├── Importaciones modulares
│   ├── Navegación sidebar
│   └── Lazy loading de vistas
│
├── 📄 requirements.txt                  # Dependencias Python
│   ├── streamlit==1.51.0
│   ├── pandas==2.3.3
│   ├── plotly==6.5.0
│   ├── gspread==6.2.1
│   └── google-auth==2.41.1
│
├── 📄 REFACTORING_GUIDE.md ✅           # Guía completa de migración
├── 📄 NEXT_STEPS.md ✅                  # Pasos inmediatos
├── 📄 README_REFACTORING.md ✅          # Resumen ejecutivo
├── 📄 TREE_STRUCTURE.md ✅              # Este archivo
│
└── 📁 venv_local/                       # Entorno virtual Python 3.13.1
    └── ...

```

---

## 📊 Estadísticas de Código

| Módulo | Archivos | Líneas | Estado | Funciones |
|--------|----------|--------|--------|-----------|
| **utils/** | 3 | ~800 | ✅ 100% | 12 |
| **components/** | 2 | ~650 | ✅ 100% | 1 |
| **views/** | 6 | ~550 | ⚠️ 50% | 5 |
| **app_refactored.py** | 1 | ~200 | ✅ 100% | 1 |
| **TOTAL** | 12 | ~2200 | ⚠️ 60% | 19 |

---

## 🔄 Flujo de Ejecución

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Usuario ejecuta: streamlit run app_refactored.py           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. app_refactored.py: Configuración inicial                    │
│     - st.set_page_config()                                      │
│     - Logging setup                                             │
│     - inject_custom_css()                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. main(): Navegación y estado                                 │
│     - Inicializar st.session_state.page                         │
│     - Renderizar sidebar con menú                               │
│     - Verificar si hay datos (load_data)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Lazy Loading de Vista Seleccionada                          │
│                                                                  │
│     if page == "landing":                                       │
│         from views.landing import render                        │
│         render()                                                │
│                                                                  │
│     elif page == "dashboard":                                   │
│         from views.dashboard import render                      │
│         render()                                                │
│                                                                  │
│     elif page == "analisis":                                    │
│         from views.analytics import render                      │
│         render()                                                │
│                                                                  │
│     # ... etc para cada vista                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Vista Renderizada: Interacción Usuario                      │
│     - Cargar datos (utils.load_data)                            │
│     - Renderizar UI                                             │
│     - Manejar eventos (botones, filtros)                        │
│     - Guardar cambios (utils.save_batch)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Dependencias entre Módulos

```
app_refactored.py
     │
     ├─→ components.styles (inject_custom_css)
     │
     ├─→ utils.data_manager (load_data)
     │
     └─→ views.*
          │
          ├─→ utils.data_manager (todas las views)
          │    ├─ load_data()
          │    ├─ save_batch()
          │    ├─ reset_db()
          │    └─ COLEGIOS_MARISTAS
          │
          ├─→ utils.helpers (landing, settings)
          │    ├─ simular()
          │    ├─ generar_reporte_html()
          │    └─ get_banner_css()
          │
          └─→ components.styles (todas las views)
               └─ COLOR_MAP
```

---

## 📦 Módulos Externos (requirements.txt)

```
streamlit 1.51.0        → Framework web
├─ pandas 2.3.3         → Manipulación de datos
├─ plotly 6.5.0         → Visualizaciones interactivas
└─ google-auth 2.41.1   → Autenticación Google
    └─ gspread 6.2.1    → API Google Sheets
```

---

## 🎯 Puntos de Entrada

### Para Desarrollo Local
```powershell
streamlit run app_refactored.py
```

### Para Producción (Streamlit Cloud)
```yaml
# .streamlit/config.toml debe existir
# secrets.toml debe estar en Streamlit Cloud Settings
```

---

## 🔐 Archivos de Configuración

### `.streamlit/config.toml` ✅
```toml
[theme]
primaryColor = "#003696"    # Azul Marista
backgroundColor = "#F4F6F9"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#212529"
```

### `.streamlit/secrets.toml` (Usuario debe crear)
```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
# ... resto de credenciales Google Sheets
```

---

## 📝 Archivos de Documentación

| Archivo | Propósito | Audiencia |
|---------|-----------|-----------|
| `REFACTORING_GUIDE.md` | Guía completa de migración | Desarrolladores |
| `NEXT_STEPS.md` | Pasos inmediatos | Desarrolladores |
| `README_REFACTORING.md` | Resumen ejecutivo | Project Managers |
| `TREE_STRUCTURE.md` | Estructura visual | Todos |
| `README.md` | Documentación general | Usuarios finales |

---

**Última actualización**: 2024  
**Versión**: 2.0 - Arquitectura Modular  
**Estado**: 60% Completado - Core funcional
