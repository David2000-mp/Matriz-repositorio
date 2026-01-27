# 📊 DIAGRAMA DE FUNCIONES Y FLUJOS DE LA APLICACIÓN

---

## 📦 Estructura de Módulos

```
┌─────────────────────────────────────────────────────────────────────┐
│                          APP.PY (MAIN)                              │
│  - Configuración Streamlit                                          │
│  - Sidebar con navegación                                           │
│  - Router de vistas                                                 │
└────────────────────────┬────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐    ┌──────────────┐
    │ LANDING │   │DASHBOARD │    │ DATA_ENTRY   │
    │(Inicio) │   │  (KPIs)  │    │ (Formulario) │
    └────┬────┘   └────┬─────┘    └──────┬───────┘
         │             │                 │
         └─────────────┼─────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
      ┌──────────┐         ┌─────────────┐
      │ANALYTICS │         │ SETTINGS    │
      │(Análisis)│         │(Configurar) │
      └────┬─────┘         └─────┬───────┘
           │                     │
           └──────────┬──────────┘
                      │
              ┌───────▼────────┐
              │   CHANGELOG    │
              │  (Versiones)   │
              └────────────────┘
```

---

## 🔄 Flujo de Ingreso de Datos

```
USUARIO INGRESA DATOS EN data_entry.py
           │
           ▼
   ┌───────────────────┐
   │ Validación Local  │
   │ - Campos requeridos
   │ - Tipos de dato
   └────────┬──────────┘
            │
            ▼
   ┌───────────────────────┐
   │  save_batch()         │
   │ (data_saver.py)       │
   │ 1. Normalizar datos   │
   │ 2. Calcular engage_rt │
   └────────┬──────────────┘
            │
            ▼
   ┌───────────────────────────┐
   │ asegurar_registro_cuenta()│
   │ - Verificar si cuenta     │
   │   existe en CSV           │
   │ - Crear si no existe      │
   └────────┬──────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
CSV LOCAL      GOOGLE SHEETS
(Backup)       (Principal)
    │               │
    └───────┬───────┘
            │
            ▼
    ┌──────────────────┐
    │ Cache Streamlit  │
    │  (Invalidar)     │
    └──────────────────┘
```

---

## 🔍 Flujo de Lectura de Datos

```
VISTA SOLICITA DATOS
(dashboard.py, analytics.py, etc.)
        │
        ▼
   ┌──────────────────┐
   │  load_data()     │
   │(data_loader.py)  │
   │ Con caché        │
   └────────┬─────────┘
            │
    ┌───────▼─────────┐
    │ ¿Caché válido? │
    └───────┬─────────┘
            │
    ┌───────┴───────┐
    │ NO            │ SÍ
    ▼               └──────────┐
    │                          │
    ├─► Google Sheets          │
    │   conectar_sheets()      │
    │   │                      │
    │   ├─ ✅ Éxito            │
    │   │  └──┐                │
    │   │     │                │
    │   └─ ❌ Error            │
    │       │                  │
    │       ▼                  │
    └─► CSV Local              │
        (Respaldo)             │
        │                      │
        └──────────────┬───────┘
                       │
                       ▼
              ┌────────────────┐
              │ validate_and_  │
              │ fill_columns() │
              └────────┬───────┘
                       │
                       ▼
              ┌────────────────┐
              │ Retornar datos │
              │   a la vista   │
              └────────────────┘
```

---

## 📊 Funciones de Análisis

```
load_data() ────────────┐
                        │
                        ▼
              ┌──────────────────┐
              │ analytics.py     │
              │ - Agregaciones   │
              │ - Tendencias     │
              │ - Anomalías      │
              └────────┬─────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
  KPIs por        Gráficos         Alertas
  Instituto      Interactivos     Anomalías
      │                │                │
      └────────────────┼────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Mostrar en      │
              │  dashboard.py    │
              └──────────────────┘
```

---

## 📄 Flujo de Generación de Reportes

```
Usuario selecciona:
- Institución
- Período
- Tipo de reporte (PDF/HTML)
        │
        ▼
   ┌──────────────────┐
   │ load_data() para │
   │ período especifico
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ analytics.py             │
   │ Calcular:                │
   │ - KPIs (seguidores, etc) │
   │ - Tendencias             │
   │ - Anomalías              │
   │ - Health Score           │
   └────────┬─────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
generate_pdf_report  generate_html_report
    │                │
    ├─► Renderizar   │
    │    tablas      │
    │    gráficos    │
    │    textos      │
    │                │
    ▼                ▼
   PDF             HTML
    │                │
    └────────┬───────┘
             │
             ▼
    Descargar/Visualizar
```

---

## 🗄️ Estructura de Base de Datos (CSV Local)

### cuentas.csv
```
id_cuenta                        | entidad              | plataforma | usuario_red
────────────────────────────────┼──────────────────────┼────────────┼──────────
a1b2c3d4e5f6g7h8i9j0k1l2m3n4 | Colegio México (Roma)| Instagram  | colegiomexicoroma
b2c3d4e5f6g7h8i9j0k1l2m3n4o5 | Colegio Jacona       | Facebook   | colegiojacona
```

### metricas.csv
```
id_cuenta | fecha      | seguidores | alcance | interacciones | likes_prom | engagement_rate
──────────┼────────────┼────────────┼─────────┼───────────────┼────────────┼─────────────────
abc123    | 2025-01-08 | 10000      | 5000    | 500           | 100        | 5.00
abc123    | 2025-01-09 | 10050      | 5200    | 520           | 104        | 5.16
def456    | 2025-01-08 | 5000       | 2500    | 150           | 30         | 3.00
```

### comentarios.csv
```
entidad              | mes        | comentario
─────────────────────┼────────────┼─────────────────────────
Colegio México (Roma)| 2025-01    | Buen crecimiento en IG
Colegio Jacona       | 2025-01    | Necesita más engagement
```

### usernames_editados.csv
```
entidad        | plataforma | usuario_editado | fecha_modificacion
───────────────┼────────────┼─────────────────┼──────────────────────────
Colegio A      | Instagram  | nuevo_usuario   | 2025-01-08 14:30:00
```

---

## 🔐 Flujo de Autenticación Google Sheets

```
app.py
  │
  ├─► sheets_connector.py
  │   │
  │   └─► _get_service_account_config()
  │       │
  │       ├─► Variable de entorno: GOOGLE_SHEETS_CREDS
  │       └─► Archivo: secrets/service_account.json
  │           │
  │           ▼
  │       {
  │         "type": "service_account",
  │         "project_id": "...",
  │         "private_key": "...",
  │         ...
  │       }
  │
  └─► google.oauth2.service_account.Credentials.from_service_account_info()
      │
      ▼
   gspread.authorize()
      │
      ▼
   spreadsheet = client.open("CHAMPILEAKS")
```

---

## 📊 Mapa de Columnas Esperadas

### COLS_CUENTAS (data_loader.py)
```
id_cuenta       → Hash MD5 único (32 caracteres)
entidad         → Nombre de institución
plataforma      → Red social (Instagram, Facebook, TikTok)
usuario_red     → Username/handle
```

### COLS_METRICAS (data_loader.py)
```
id_cuenta       → Link a cuentas.csv
fecha           → Tipo: datetime
seguidores      → Tipo: int/float
alcance         → Tipo: int/float
interacciones   → Tipo: int/float
likes_promedio  → Tipo: float
engagement_rate → Tipo: float (calculado)
```

### COLS_CONFIG (data_loader.py)
```
entidad           → Institución
meta_seguidores   → Meta objetivo
meta_engagement   → Meta objetivo (%)
```

---

## 🎯 Decisiones de Diseño Clave

### 1. Caché Dual
```
┌─────────────────────────────┐
│ Nivel 1: Streamlit Cache    │
│ (En memoria durante sesión) │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Nivel 2: Google Sheets      │
│ (Principal, en la nube)     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Nivel 3: CSV Local          │
│ (Respaldo, fallback)        │
└─────────────────────────────┘
```

### 2. ID Determinístico
```
Entrada: ("Colegio México", "Instagram", "colegiomexicoroma")
   │
   ▼
Normalizar: ("colegio méxico", "instagram", "colegiomexicoroma")
   │
   ▼
Buscar en BD actual: ¿Existe?
   │
   ├─ SÍ: Retornar ID existente
   │
   └─ NO: Generar MD5(entrada normalizada)
      │
      ▼
      Retornar: "a1b2c3d4e5f6..."

VENTAJA: Mismo input siempre = mismo ID
         (idempotente)
```

### 3. Engagement Rate
```
Fórmula: engagement_rate = (interacciones / seguidores) × 100

Validaciones:
├─ Si seguidores = 0 → engagement_rate = 0
├─ Si NaN/Inf → reemplazar por 0
└─ Redondear a 2 decimales

Ejemplo:
├─ 500 interacciones, 10000 seguidores → 5.00%
├─ 100 interacciones, 5000 seguidores  → 2.00%
└─ 0 seguidores                        → 0.00%
```

---

## ⚡ Performance & Optimizaciones

### Caching Strategy
```
┌──────────────────────────────┐
│ load_data() con @st.cache_data
│                              │
│ Cache válido si:             │
│ - No hubo cambios en Sheets  │
│ - No hubo cambios en CSV     │
│ - Usuario no limpió caché    │
└──────────────────────────────┘
```

### Deduplicación
```
CSV Antiguo + Nuevo Batch
         │
         ▼
    Concatenar
         │
         ▼
   Ordernar por id_cuenta, fecha
         │
         ▼
   drop_duplicates(subset=[id_cuenta, fecha], keep='last')
         │
         ▼
    Guardar resultado
```

---

## 🚨 Puntos Críticos de Falla

```
RIESGO 1: Google Sheets no disponible
├─ IMPACTO: Métricas no se sincronizan
└─ MITIGACIÓN: Guardar en CSV local (respaldo)

RIESGO 2: Columnas faltantes en DataFrame
├─ IMPACTO: Error al guardar
└─ MITIGACIÓN: validate_and_fill_columns()

RIESGO 3: Fechas en formato inconsistente
├─ IMPACTO: Deduplicación falla
└─ MITIGACIÓN: Convertir a datetime en carga

RIESGO 4: ID cuenta duplicados
├─ IMPACTO: Datos confundidos
└─ MITIGACIÓN: Hash determinístico único

RIESGO 5: API rate limit de Google Sheets
├─ IMPACTO: Solicitudes rechazadas
└─ MITIGACIÓN: Implementar caché + reintentos
```

---

## 📈 Tamaño Actual de Datos

```
Estimado por institución:
├─ Cuentas: 1-5 (Instagram, Facebook, TikTok)
├─ Métricas: ~30-365 filas por año
│   (1 entrada por día = 365 filas/año)
├─ Comentarios: ~12 por año
└─ Usernames editados: ~2-5 por año

Total Filas:
├─ Si 15 instituciones × 365 días = 5,475 filas métricas
├─ Si 15 instituciones × 5 cuentas = 75 filas cuentas
└─ Tamaño estimado CSV: ~100KB

→ NO hay problemas de escala
```

---

## 🔄 Ciclo de Vida de los Datos

```
ENTRADA               PROCESAMIENTO            ALMACENAMIENTO        SALIDA
───────────────────────────────────────────────────────────────────────────

Manual en             validate_and_fill        CSV + Google          Dashboard
data_entry.py    →   normalize_types      →   Sheets            →   KPIs/Gráficos
                      calculate_engagement      (Sinc. async)         Reportes

                                                                  Analytics
                                                                  Predicciones
                                                                  Alertas

Ciclo:
Día 1:  Entrada → CSV
Día 2:  Entrada → CSV
...
Mes 1:  Análisis de datos acumulados
Mes 3:  Reporte consolidado + predicciones
```

---

## 📝 Leyenda de Símbolos

```
✅ - Funciona correctamente
❌ - Error/Falla
⚠️  - Advertencia/Cuidado
→  - Flujo/Dirección
┌─ - Límite/Contenedor
│  - Conexión vertical
└─ - Fin de contenedor
─  - Línea horizontal
```

