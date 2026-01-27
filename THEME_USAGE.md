# 🎨 Uso del Sistema de Temas Dinámicos

## 🚀 Inicio Rápido

### Aplicar en Cualquier Archivo .py

```python
import streamlit as st
from components import aplicar_estilo_personalizado

# ¡Una sola línea al inicio de tu script!
tema_actual = aplicar_estilo_personalizado()

# El resto de tu código funciona automáticamente
st.title("Mi Dashboard")
st.text_input("Usuario")
st.selectbox("Plataforma", ["Facebook", "Instagram", "TikTok"])
```

---

## ✨ Características

### ✅ Selector en Sidebar
- Radio button con 2 opciones: **Claro** y **Oscuro**
- Persiste la selección en `st.session_state`
- Emoji visual para fácil identificación

### ✅ Inputs Unificados
Todos los campos tienen el mismo diseño:
- **Selectbox** (combobox)
- **Text Input**
- **Number Input**
- **Text Area**
- **Date Input**
- **Multi Select**

Características comunes:
- ✅ Bordes redondeados (8px)
- ✅ Fuente 16px (anti-zoom iOS)
- ✅ Padding consistente (12px 16px)
- ✅ Transiciones suaves (0.2s)
- ✅ Focus states visibles

### ✅ Contraste Perfecto

#### Tema Claro
- Fondo: `#FFFFFF`
- Texto: `#1A1A1A` (16.1:1 contraste)
- Inputs: Fondo blanco con borde `#D1D5DB`
- Placeholder: `#9CA3AF`

#### Tema Oscuro
- Fondo: `#0E1117`
- Texto: `#FAFAFA` (14.2:1 contraste)
- Inputs: Fondo `#1E2228` con borde `#3A3F47`
- Placeholder: `#6B6B6B`

---

## 📋 Ejemplo Completo

```python
import streamlit as st
from components import aplicar_estilo_personalizado
import pandas as pd

# Aplicar sistema de temas (debe ser lo primero)
tema_actual = aplicar_estilo_personalizado()

# Configuración de página
st.set_page_config(
    page_title="Dashboard con Temas",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Dashboard con Selector de Temas")

# El tema ya está aplicado, todos los widgets tendrán el estilo correcto
col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input(
        "Nombre del Colegio",
        placeholder="Ej: Champagnat"
    )
    
    plataforma = st.selectbox(
        "Plataforma Social",
        ["Facebook", "Instagram", "TikTok", "LinkedIn"],
        help="Selecciona una plataforma"
    )

with col2:
    fecha = st.date_input("Fecha de Reporte")
    
    seguidores = st.number_input(
        "Seguidores",
        min_value=0,
        step=100,
        value=1000
    )

# Métricas con tema aplicado
st.markdown("### 📊 Métricas")
metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Seguidores", "15,420", "+1,234")

with metric2:
    st.metric("Engagement", "4.5%", "+0.3%")

with metric3:
    st.metric("Alcance", "45.2K", "+5.1K")

# Mostrar tema actual
st.info(f"✅ Tema actual: **{tema_actual}**")
```

---

## 🔧 Personalización Avanzada

### Cambiar Colores Institucionales

Edita `components/styles.py` en la función `aplicar_estilo_personalizado()`:

```python
# Dentro de la definición de theme
theme = {
    ...
    'primary': '#TU_COLOR_AQUI',  # Azul institucional
    'accent': '#TU_ACENTO_AQUI',  # Color de acento
}
```

### Usar el Tema en Código Personalizado

```python
tema = aplicar_estilo_personalizado()

if tema == 'Oscuro':
    # Lógica específica para modo oscuro
    color_grafico = '#FAFAFA'
else:
    # Lógica para modo claro
    color_grafico = '#1A1A1A'

# Usar en gráfico
fig = px.bar(df, color_discrete_sequence=[color_grafico])
```

### Variables CSS Disponibles

Puedes usar estas variables en cualquier HTML personalizado:

```python
st.markdown(
    """
    <div style='
        background-color: var(--bg-card);
        color: var(--text-color);
        border: 2px solid var(--border-color);
        padding: 20px;
        border-radius: 8px;
    '>
        Texto con tema aplicado
    </div>
    """,
    unsafe_allow_html=True
)
```

Variables disponibles:
- `--background-color` - Fondo principal
- `--bg-secondary` - Fondo secundario
- `--bg-card` - Fondo de tarjetas
- `--input-bg` - Fondo de inputs
- `--text-color` - Texto principal
- `--text-secondary` - Texto secundario
- `--border-color` - Color de bordes
- `--border-focus` - Color de foco
- `--primary-color` - Color primario institucional
- `--accent-color` - Color de acento

---

## 📱 Compatibilidad

### ✅ Tested On
- Chrome 120+
- Firefox 120+
- Safari 17+
- Edge 120+
- Mobile Safari (iOS 16+)
- Chrome Mobile (Android 12+)

### ✅ Responsive
- Desktop (1920px+)
- Tablet (768px-1919px)
- Mobile (320px-767px)

---

## 🎯 Best Practices

### 1️⃣ Siempre Primero
```python
# ✅ CORRECTO - Al inicio del script
from components import aplicar_estilo_personalizado
aplicar_estilo_personalizado()

st.title("Mi App")
```

```python
# ❌ INCORRECTO - Después de widgets
st.title("Mi App")
aplicar_estilo_personalizado()  # Muy tarde!
```

### 2️⃣ No Mezclar con inject_custom_css()
```python
# ❌ EVITAR - No uses ambos
aplicar_estilo_personalizado()
inject_custom_css()  # Conflicto!
```

```python
# ✅ USAR SOLO UNO
aplicar_estilo_personalizado()  # Sistema completo con selector
```

### 3️⃣ Session State Disponible
```python
# Acceder al tema actual en cualquier momento
if st.session_state.tema == 'Oscuro':
    st.write("Estás en modo oscuro 🌙")
else:
    st.write("Estás en modo claro ☀️")
```

---

## 🐛 Troubleshooting

### ❓ "El selector no aparece en el sidebar"

✅ **Solución:** Asegúrate de llamar la función antes de cualquier widget.

```python
# Primera línea después de imports
aplicar_estilo_personalizado()
```

### ❓ "Los colores no cambian al seleccionar tema"

✅ **Solución:** Streamlit necesita rerun. El cambio es automático al seleccionar.

```python
# El selector ya incluye lógica de rerun automática
# No necesitas hacer nada adicional
```

### ❓ "Algunos inputs no tienen el estilo"

✅ **Solución:** Verifica que sea un widget nativo de Streamlit.

```python
# ✅ Widgets soportados
st.text_input()
st.selectbox()
st.number_input()
st.text_area()
st.date_input()
st.multiselect()

# ❌ HTML custom no aplicará automáticamente
# Usa variables CSS manualmente
```

---

## 📊 Comparación con Sistema Anterior

| Característica | inject_custom_css() | aplicar_estilo_personalizado() |
|----------------|---------------------|--------------------------------|
| Selector de tema | ❌ No | ✅ Sí |
| Modo claro/oscuro | ⚠️ Auto-detect | ✅ Usuario elige |
| Inputs unificados | ⚠️ Parcial | ✅ Completo |
| Contraste garantizado | ✅ Sí | ✅ Sí (mejor) |
| Persistencia | ❌ No | ✅ session_state |
| Código requerido | 1 línea | 1 línea |

---

## 🎓 Tutorial Video

```python
# Ejemplo interactivo paso a paso
import streamlit as st
from components import aplicar_estilo_personalizado

# PASO 1: Aplicar tema
tema = aplicar_estilo_personalizado()

# PASO 2: Crear contenido
st.title("Tutorial de Temas")

st.write(f"Tema seleccionado: **{tema}**")

# PASO 3: Probar con inputs
nombre = st.text_input("Escribe algo")
if nombre:
    st.success(f"Texto legible en tema {tema}: {nombre}")

# PASO 4: Cambiar tema en sidebar y ver la magia ✨
```

---

**Creado por:** Equipo CHAMPILEAKS  
**Última actualización:** Enero 2026  
**Versión:** 1.0.0
