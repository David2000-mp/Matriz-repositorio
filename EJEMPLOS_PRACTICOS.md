# 💡 EJEMPLOS PRÁCTICOS DE USO - COOKBOOK

**Versión:** 2.1.0  
**Propósito:** Guía con ejemplos reales de cómo usar cada función

---

## 📌 TABLA DE CONTENIDOS

1. [Guardar Datos](#guardar-datos)
2. [Cargar Datos](#cargar-datos)
3. [Generar Reportes](#generar-reportes)
4. [Análisis y Simulaciones](#análisis-y-simulaciones)
5. [Manejo de Errores](#manejo-de-errores)
6. [Casos de Uso Complejos](#casos-de-uso-complejos)

---

## 🚀 GUARDAR DATOS

### Ejemplo 1: Guardar Métricas de Una Institución

```python
import pandas as pd
from utils.data_saver import save_batch

# Preparar datos
datos = pd.DataFrame({
    'id_cuenta': ['abc123'],
    'entidad': ['Colegio México (Roma)'],
    'plataforma': ['Instagram'],
    'usuario_red': ['colegiomexicoroma'],
    'fecha': ['2025-01-08'],
    'seguidores': [10500],
    'alcance': [5200],
    'interacciones': [520],
    'likes_promedio': [104]
})

# Guardar
if save_batch(datos):
    print("✅ Datos guardados exitosamente")
else:
    print("❌ Error al guardar")
```

### Ejemplo 2: Guardar en Lote (Múltiples Registros)

```python
from utils.data_saver import save_batch

# Lista de métricas
batch = [
    {
        'id_cuenta': 'abc123',
        'entidad': 'Colegio A',
        'plataforma': 'Instagram',
        'usuario_red': 'colegioa',
        'fecha': '2025-01-08',
        'seguidores': 10000,
        'alcance': 5000,
        'interacciones': 500,
        'likes_promedio': 100
    },
    {
        'id_cuenta': 'def456',
        'entidad': 'Colegio B',
        'plataforma': 'Facebook',
        'usuario_red': 'colegiob',
        'fecha': '2025-01-08',
        'seguidores': 8000,
        'alcance': 4000,
        'interacciones': 400,
        'likes_promedio': 80
    }
]

# Guardar lote completo
success = save_batch(batch, modo="append")
print(f"Guardados {len(batch)} registros" if success else "Error en lote")
```

### Ejemplo 3: Reemplazar Todos los Datos (Cuidado)

```python
from utils.data_saver import save_batch
import pandas as pd

# Cargar datos nuevos
df_nuevo = pd.read_csv('datos_nuevos.csv')

# Reemplazar TODO (no append)
if save_batch(df_nuevo, modo="replace"):
    print("✅ Datos reemplazados")
else:
    print("❌ Error al reemplazar")
```

### Ejemplo 4: Guardar Comentario

```python
from utils.data_saver import save_comment

# Guardar nota sobre institución
if save_comment(
    entidad="Colegio México (Roma)",
    mes="2025-01",
    comentario="Buen crecimiento en Instagram este mes"
):
    print("✅ Comentario guardado")
```

### Ejemplo 5: Guardar Username Editado

```python
from utils.data_saver import save_username_editado

# Si descubrimos que el usuario era incorrecto
if save_username_editado(
    entidad="Colegio A",
    plataforma="Instagram",
    usuario_editado="usuario_correcto"
):
    print("✅ Usuario actualizado")
```

---

## 📖 CARGAR DATOS

### Ejemplo 1: Cargar Todos los Datos

```python
from utils.data_loader import load_data

# Cargar desde Google Sheets o CSV
df_cuentas, df_metricas = load_data()

print(f"Cuentas cargadas: {len(df_cuentas)}")
print(f"Métricas cargadas: {len(df_metricas)}")

# Ver primeros registros
print(df_metricas.head())
```

### Ejemplo 2: Filtrar Datos Por Institución

```python
from utils.data_loader import load_data

_, df_metricas = load_data()

# Filtrar por institución
colegio_metricas = df_metricas[
    df_metricas['entidad'] == 'Colegio México (Roma)'
]

print(f"Registros para Colegio México (Roma): {len(colegio_metricas)}")
print(colegio_metricas)
```

### Ejemplo 3: Filtrar Por Período

```python
from utils.data_loader import load_data
import pandas as pd

_, df_metricas = load_data()

# Convertir fecha a datetime
df_metricas['fecha'] = pd.to_datetime(df_metricas['fecha'])

# Filtrar enero 2025
enero = df_metricas[
    (df_metricas['fecha'] >= '2025-01-01') &
    (df_metricas['fecha'] < '2025-02-01')
]

print(f"Registros en enero 2025: {len(enero)}")
```

### Ejemplo 4: Cargar Configuraciones

```python
from utils.data_loader import load_configs, load_comments

# Cargar metas por institución
configs = load_configs()
print(configs)

# Cargar comentarios
comentarios = load_comments()
print(comentarios)
```

---

## 📊 GENERAR REPORTES

### Ejemplo 1: Generar Reporte PDF

```python
from utils.reports import generate_pdf_report
import pandas as pd
from datetime import datetime

# Preparar datos de KPIs
kpis = {
    'seguidores': {
        'valor': 10500,
        'cambio': 500,  # Cambio respecto período anterior
        'tendencia': 'up'
    },
    'engagement': {
        'valor': 5.2,
        'cambio': 0.5,
        'tendencia': 'up'
    },
    'alcance': {
        'valor': 5200,
        'cambio': 200,
        'tendencia': 'up'
    }
}

# Anomalías detectadas
anomalias = [
    {'fecha': '2025-01-05', 'tipo': 'pico_inusual', 'valor': 1500},
]

# Generar PDF
pdf_bytes = generate_pdf_report(
    school_name="Colegio México (Roma)",
    period="Enero 2025",
    kpis=kpis,
    anomalies=anomalias,
    health_score=85.5
)

# Guardar a archivo
with open('reporte.pdf', 'wb') as f:
    f.write(pdf_bytes)

print("✅ PDF generado: reporte.pdf")
```

### Ejemplo 2: Generar Reporte HTML

```python
from utils.reports import generate_html_report

# Parámetros similares a PDF
html = generate_html_report(
    school_name="Colegio México (Roma)",
    period="Enero 2025",
    kpis=kpis,
    anomalies=anomalias,
    health_score=85.5
)

# Guardar HTML
with open('reporte.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ HTML generado: reporte.html")
```

### Ejemplo 3: Generar HTML Desde DataFrame

```python
from utils.helpers import generar_reporte_html
import pandas as pd

# DataFrame con métricas
df = pd.DataFrame({
    'entidad': ['Colegio A', 'Colegio B'],
    'plataforma': ['Instagram', 'Facebook'],
    'seguidores': [10000, 8000],
    'engagement_rate': [5.2, 4.1]
})

# Generar HTML
html = generar_reporte_html(
    df=df,
    titulo="Reporte de Redes Sociales - Enero 2025"
)

with open('reporte_html.html', 'w') as f:
    f.write(html)
```

---

## 📈 ANÁLISIS Y SIMULACIONES

### Ejemplo 1: Simular Crecimiento Futuro

```python
from utils.helpers import simular
from utils.data_loader import load_data

# Cargar datos históricos
_, df_metricas = load_data()

# Simular 3 meses de crecimiento para Colegio A
proyecciones = simular(
    df_metricas=df_metricas,
    entidad="Colegio A",
    meses=3,
    crecimiento_mensual_follower=0.05,  # 5% crecimiento mensual
    tasa_engagement=4.5  # Meta: 4.5% engagement
)

print("Proyecciones (próximos 3 meses):")
print(proyecciones)
```

### Ejemplo 2: Calcular Tendencias

```python
from utils.data_loader import load_data
import pandas as pd

_, df_metricas = load_data()

# Filtrar por institución
colegio = df_metricas[df_metricas['entidad'] == 'Colegio A']

# Ordenar por fecha
colegio = colegio.sort_values('fecha')

# Calcular cambio en seguidores
colegio['cambio_seguidores'] = colegio['seguidores'].diff()

# Calcular % cambio
colegio['pct_cambio'] = (
    colegio['cambio_seguidores'] / 
    colegio['seguidores'].shift(1) * 100
).round(2)

print("Tendencia de crecimiento:")
print(colegio[['fecha', 'seguidores', 'cambio_seguidores', 'pct_cambio']])
```

### Ejemplo 3: Comparar Institución Vs Meta

```python
from utils.data_loader import load_data, load_configs
import pandas as pd

# Cargar datos y configs
_, df_metricas = load_data()
df_configs = load_configs()

# Obtener meta para institución
entidad = "Colegio A"
meta = df_configs[df_configs['entidad'] == entidad]
meta_seguidores = meta['meta_seguidores'].values[0]
meta_engagement = meta['meta_engagement'].values[0]

# Obtener último registro
ultimo_registro = df_metricas[
    df_metricas['entidad'] == entidad
].sort_values('fecha').iloc[-1]

# Comparar
print(f"\n{'Métrica':<20} {'Actual':<15} {'Meta':<15} {'Estado':<10}")
print("-" * 60)

# Seguidores
seg_actual = ultimo_registro['seguidores']
status_seg = "✅" if seg_actual >= meta_seguidores else "❌"
print(f"{'Seguidores':<20} {seg_actual:<15} {meta_seguidores:<15} {status_seg:<10}")

# Engagement
eng_actual = ultimo_registro['engagement_rate']
status_eng = "✅" if eng_actual >= meta_engagement else "❌"
print(f"{'Engagement %':<20} {eng_actual:<15.2f} {meta_engagement:<15} {status_eng:<10}")
```

---

## ⚠️ MANEJO DE ERRORES

### Ejemplo 1: Manejo Robusto de Guardado

```python
from utils.data_saver import save_batch
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)

def guardar_con_validacion(df):
    """Guarda datos con validación y logging."""
    try:
        # Validar que no esté vacío
        if df is None or df.empty:
            logger.warning("DataFrame vacío, no hay nada que guardar")
            return False
        
        # Validar columnas requeridas
        columnas_requeridas = [
            'id_cuenta', 'fecha', 'seguidores', 'alcance',
            'interacciones', 'likes_promedio'
        ]
        
        faltantes = set(columnas_requeridas) - set(df.columns)
        if faltantes:
            logger.error(f"Columnas faltantes: {faltantes}")
            return False
        
        # Intentar guardar
        resultado = save_batch(df)
        
        if resultado:
            logger.info(f"✅ {len(df)} registros guardados exitosamente")
            return True
        else:
            logger.error("❌ Error al guardar en save_batch")
            return False
            
    except Exception as e:
        logger.error(f"Excepción inesperada: {e}")
        return False

# Usar función
df_test = pd.DataFrame({'id_cuenta': ['abc']})  # Incompleto
guardar_con_validacion(df_test)
# → "Columnas faltantes: ..."
```

### Ejemplo 2: Reintentos Automáticos

```python
from utils.data_loader import load_data
from utils.logger import get_logger
import time

logger = get_logger(__name__)

def cargar_con_reintentos(max_intentos=3):
    """Carga datos con reintentos automáticos."""
    for intento in range(max_intentos):
        try:
            df_cuentas, df_metricas = load_data()
            logger.info(f"✅ Datos cargados en intento {intento + 1}")
            return df_cuentas, df_metricas
        except Exception as e:
            if intento < max_intentos - 1:
                espera = 2 ** intento  # Backoff: 1s, 2s, 4s
                logger.warning(
                    f"Intento {intento + 1} falló: {e}. "
                    f"Reintentando en {espera}s..."
                )
                time.sleep(espera)
            else:
                logger.error(f"❌ Falló después de {max_intentos} intentos")
                raise

# Usar
try:
    df_cuentas, df_metricas = cargar_con_reintentos()
except:
    print("No se pudo cargar datos después de reintentos")
```

---

## 🔧 CASOS DE USO COMPLEJOS

### Caso 1: Pipeline Completo de Ingesta Diaria

```python
from utils.data_loader import load_data
from utils.data_saver import save_batch
from utils.logger import get_logger
import pandas as pd
from datetime import datetime

logger = get_logger(__name__)

def ingesta_diaria(datos_nuevos_csv):
    """
    Pipeline diario de ingesta de métricas:
    1. Cargar datos nuevos
    2. Validar
    3. Enriquecer
    4. Guardar
    """
    try:
        # 1. Cargar nuevos datos
        logger.info("📖 Cargando datos nuevos...")
        df_nuevo = pd.read_csv(datos_nuevos_csv)
        
        # 2. Validar estructura
        logger.info("✓ Validando estructura...")
        columnas_req = ['entidad', 'plataforma', 'usuario_red', 
                       'seguidores', 'alcance', 'interacciones', 'likes_promedio']
        if not all(col in df_nuevo.columns for col in columnas_req):
            logger.error("❌ Columnas faltantes en datos nuevos")
            return False
        
        # 3. Enriquecer (agregar fecha actual si falta)
        if 'fecha' not in df_nuevo.columns:
            df_nuevo['fecha'] = datetime.now().strftime('%Y-%m-%d')
        
        # 4. Generar IDs si faltan
        from utils.data_saver import get_id
        if 'id_cuenta' not in df_nuevo.columns:
            df_nuevo['id_cuenta'] = df_nuevo.apply(
                lambda row: get_id(row['entidad'], row['plataforma'], 
                                  row['usuario_red']),
                axis=1
            )
        
        # 5. Guardar
        logger.info(f"💾 Guardando {len(df_nuevo)} registros...")
        if save_batch(df_nuevo):
            logger.info("✅ Ingesta completa exitosa")
            return True
        else:
            logger.error("❌ Error al guardar")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en pipeline: {e}")
        return False

# Ejecutar diariamente
if __name__ == "__main__":
    success = ingesta_diaria('datos_hoy.csv')
```

### Caso 2: Generar Reportes Automáticos Mensualmente

```python
from utils.data_loader import load_data, load_configs
from utils.reports import generate_pdf_report
from utils.logger import get_logger
import pandas as pd
from pathlib import Path

logger = get_logger(__name__)

def generar_reportes_mensuales(mes_year):
    """
    Genera reportes PDF para todas las instituciones.
    
    Args:
        mes_year: "2025-01"
    """
    try:
        # 1. Cargar datos
        _, df_metricas = load_data()
        df_configs = load_configs()
        
        # 2. Filtrar por mes
        df_mes = df_metricas[
            df_metricas['fecha'].astype(str).str.startswith(mes_year)
        ]
        
        # 3. Iterar por institución
        instituciones = df_mes['entidad'].unique()
        
        for entidad in instituciones:
            logger.info(f"📊 Generando reporte para {entidad}...")
            
            # Datos institución
            datos_inst = df_mes[df_mes['entidad'] == entidad]
            
            # Calcular KPIs (simplificado)
            kpis = {
                'seguidores': {
                    'valor': datos_inst['seguidores'].iloc[-1],
                    'cambio': (datos_inst['seguidores'].iloc[-1] - 
                              datos_inst['seguidores'].iloc[0]),
                    'tendencia': 'up'
                },
                'engagement': {
                    'valor': datos_inst['engagement_rate'].mean(),
                    'cambio': 0,
                    'tendencia': 'stable'
                }
            }
            
            # Generar PDF
            pdf_bytes = generate_pdf_report(
                school_name=entidad,
                period=mes_year,
                kpis=kpis,
                anomalies=[],
                health_score=85.0
            )
            
            # Guardar
            output_dir = Path("reportes_mensales") / mes_year
            output_dir.mkdir(parents=True, exist_ok=True)
            
            safe_name = entidad.replace(' ', '_').replace('(', '').replace(')', '')
            filepath = output_dir / f"{safe_name}_reporte.pdf"
            
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"✅ Guardado: {filepath}")
        
        logger.info(f"✅ Reportes de {mes_year} completados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generando reportes: {e}")
        return False

# Ejecutar
if __name__ == "__main__":
    generar_reportes_mensuales("2025-01")
```

### Caso 3: Detectar Anomalías y Alertar

```python
from utils.data_loader import load_data
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)

def detectar_anomalias(desv_estandar=2.0):
    """
    Detecta cambios anómalos en métricas.
    
    Args:
        desv_estandar: Threshold en desviaciones estándar
    """
    _, df_metricas = load_data()
    
    alertas = []
    
    for entidad in df_metricas['entidad'].unique():
        datos = df_metricas[df_metricas['entidad'] == entidad].sort_values('fecha')
        
        # Calcular cambios día a día
        datos['cambio_seguidores'] = datos['seguidores'].diff()
        
        # Estadísticas
        media = datos['cambio_seguidores'].mean()
        desv = datos['cambio_seguidores'].std()
        
        # Identificar outliers
        threshold = media + (desv_estandar * desv)
        
        anomalias = datos[datos['cambio_seguidores'] > threshold]
        
        if len(anomalias) > 0:
            for _, row in anomalias.iterrows():
                alerta = {
                    'entidad': entidad,
                    'fecha': row['fecha'],
                    'cambio': row['cambio_seguidores'],
                    'tipo': 'pico_crecimiento'
                }
                alertas.append(alerta)
                
                logger.warning(
                    f"⚠️ ALERTA: {entidad} creció "
                    f"{row['cambio_seguidores']:.0f} seguidores el {row['fecha']}"
                )
    
    return alertas

# Ejecutar
anomalias = detectar_anomalias(desv_estandar=2.5)
print(f"Encontradas {len(anomalias)} anomalías")
```

---

## 📱 INTEGRACIÓN CON STREAMLIT

### Ejemplo: Vista Personalizada

```python
import streamlit as st
from utils.data_loader import load_data
from utils.data_saver import save_batch
import pandas as pd

def render():
    """Vista para entrada manual de datos."""
    
    st.title("📝 Captura Manual de Métricas")
    
    # Formulario
    with st.form("metrics_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            entidad = st.selectbox("Institución", [
                "Colegio A", "Colegio B", "Colegio C"
            ])
            plataforma = st.selectbox("Red Social", [
                "Instagram", "Facebook", "TikTok"
            ])
        
        with col2:
            usuario = st.text_input("Usuario")
            fecha = st.date_input("Fecha")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            seguidores = st.number_input("Seguidores", min_value=0)
            alcance = st.number_input("Alcance", min_value=0)
        
        with col4:
            interacciones = st.number_input("Interacciones", min_value=0)
            likes_prom = st.number_input("Likes Promedio", min_value=0.0)
        
        submitted = st.form_submit_button("Guardar")
    
    if submitted:
        # Preparar datos
        from utils.data_saver import get_id
        
        id_cuenta = get_id(entidad, plataforma, usuario)
        
        df_nuevo = pd.DataFrame({
            'id_cuenta': [id_cuenta],
            'entidad': [entidad],
            'plataforma': [plataforma],
            'usuario_red': [usuario],
            'fecha': [fecha.strftime('%Y-%m-%d')],
            'seguidores': [seguidores],
            'alcance': [alcance],
            'interacciones': [interacciones],
            'likes_promedio': [likes_prom]
        })
        
        # Guardar
        if save_batch(df_nuevo):
            st.success("✅ Métricas guardadas")
            st.cache_data.clear()  # Limpiar caché
        else:
            st.error("❌ Error al guardar")
```

---

## 🎓 CONCLUSIÓN

Estos ejemplos cubren los casos de uso más comunes. Adapta el código a tus necesidades específicas combinando las funciones disponibles.

**Recuerda:**
- ✅ Siempre validar datos antes de guardar
- ✅ Usar manejo de excepciones robusto
- ✅ Loggear operaciones importantes
- ✅ Limpiar caché de Streamlit después de cambios

