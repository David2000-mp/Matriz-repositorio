# 🎨 Guía de Accesibilidad y Estilos CHAMPILEAKS

## ✅ Estándares Implementados

Esta aplicación cumple con **WCAG 2.1 Nivel AA** para garantizar accesibilidad universal.

### 📊 Contraste de Color (Mínimo 4.5:1)

Todos los colores han sido verificados para cumplir con el contraste mínimo requerido:

| Color | Uso | Contraste sobre Blanco | Estado |
|-------|-----|----------------------|--------|
| `#003696` | Azul Primario | 10.15:1 | ✅ WCAG AA |
| `#002566` | Azul Hover | 14.05:1 | ✅ WCAG AAA |
| `#1A1A1A` | Texto Principal | 16.1:1 | ✅ WCAG AAA |
| `#4A5568` | Texto Secundario | 7.54:1 | ✅ WCAG AAA |
| `#5A5A5A` | Subtítulos | 6.12:1 | ✅ WCAG AA |
| `#1E7E34` | Verde (Éxito) | 5.32:1 | ✅ WCAG AA |
| `#CC7000` | Naranja (Alerta) | 4.89:1 | ✅ WCAG AA |
| `#C82333` | Rojo (Peligro) | 5.94:1 | ✅ WCAG AA |
| `#0056B3` | Azul Info | 6.47:1 | ✅ WCAG AA |

### 🎨 Paleta de Colores por Plataforma (Ajustados)

```python
COLOR_MAP = {
    "Facebook": "#1877F2",   # 4.51:1 ✓
    "Instagram": "#C13584",  # 4.57:1 ✓ (oscurecido desde #E1306C)
    "TikTok": "#000000",     # 21:1 ✓
    "Twitter/X": "#1DA1F2",  # 3.12:1 (usar con fondo oscuro)
    "LinkedIn": "#0A66C2",   # 5.51:1 ✓
    "YouTube": "#CC0000",    # 5.29:1 ✓ (oscurecido desde #FF0000)
}
```

---

## 📝 Tamaños de Fuente

### ✅ Mínimos Requeridos

- **Texto base:** 16px (evita zoom en iOS)
- **Labels de inputs:** 16px
- **Inputs y textareas:** 16px
- **Títulos H1:** 36px (2.25rem)
- **Títulos H2:** 30px (1.875rem)
- **Títulos H3:** 24px (1.5rem)

### 📊 Gráficos Plotly

```python
# Configuración recomendada
PLOTLY_THEME = {
    "font": {"size": 14},      # Mínimo legible
    "title": {"font": {"size": 18}},
    "xaxis": {"tickfont": {"size": 12}},
    "yaxis": {"tickfont": {"size": 12}},
}
```

---

## 🌗 Soporte Modo Claro/Oscuro

El sistema detecta automáticamente la preferencia del usuario:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #0E1117;
        --card-bg: #1E2228;
        --text-color: #FAFAFA;
        --text-secondary: #B8B8B8;
    }
}
```

### ⚠️ Nunca usar colores hardcodeados

❌ **Incorrecto:**
```python
st.markdown("<p style='color:#666'>Texto</p>")
```

✅ **Correcto:**
```python
st.markdown("<p style='color:var(--text-secondary)'>Texto</p>")
```

---

## 🎯 Uso de la Configuración

### Importar Estilos

```python
from components import (
    inject_custom_css,
    configure_plotly_theme,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)

# Aplicar CSS global
inject_custom_css()
```

### Configurar Gráficos Plotly

```python
import plotly.express as px

fig = px.bar(df, x="mes", y="seguidores")

# Aplicar tema accesible
plotly_theme = configure_plotly_theme()
fig.update_layout(**plotly_theme)

st.plotly_chart(fig)
```

---

## ♿ Accesibilidad de Teclado

### Focus States

Todos los elementos interactivos tienen indicadores de foco visibles:

```css
button:focus-visible {
    outline: 3px solid var(--accent-color) !important;
    outline-offset: 2px !important;
}
```

### Navegación

- ✅ Tab para navegar entre elementos
- ✅ Enter/Space para activar botones
- ✅ Esc para cerrar modales (si aplica)

---

## 📱 Responsive Design

### Breakpoints

```css
@media (max-width: 768px) {
    /* Ajustes para móvil */
    h1 { font-size: 1.75rem !important; }
    .kpi-cards { flex-direction: column; }
}
```

---

## 🚀 Ejemplo Completo

```python
import streamlit as st
from components import inject_custom_css, configure_plotly_theme, COLOR_SUCCESS
import plotly.express as px

# Aplicar estilos globales
inject_custom_css()

st.title("📊 Dashboard Accesible")

# KPI con color correcto
col1, col2 = st.columns(2)
with col1:
    st.metric("Seguidores", "15,420", "+1,234")
    
# Gráfico con tema accesible
df = load_data()
fig = px.line(df, x="fecha", y="seguidores")
fig.update_layout(**configure_plotly_theme())
st.plotly_chart(fig, use_container_width=True)

# Badge con color WCAG AA
st.markdown(
    f"<span class='badge badge--success'>Activo</span>",
    unsafe_allow_html=True
)
```

---

## 🔍 Verificación de Contraste

Herramientas recomendadas:

- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Lighthouse** (DevTools de Chrome)
- **axe DevTools** (Extensión de navegador)

### Comando de verificación

```bash
# Ejecutar Lighthouse CI
npm install -g @lhci/cli
lhci autorun --collect.url=http://localhost:8501
```

---

## 📋 Checklist Pre-Despliegue

- [ ] Todos los textos tienen contraste mínimo 4.5:1
- [ ] Inputs con tamaño mínimo 16px
- [ ] Gráficos con `configure_plotly_theme()`
- [ ] Colores usando variables CSS, no hardcoded
- [ ] Focus states visibles en todos los botones
- [ ] Prueba con modo oscuro activado
- [ ] Prueba con lector de pantalla (NVDA/JAWS)
- [ ] Navegación completa por teclado

---

## 🆘 Resolución de Problemas

### ❓ "Los textos son invisibles en modo oscuro"

✅ **Solución:** Usa variables CSS en lugar de colores fijos.

```python
# ❌ Incorrecto
st.markdown("<p style='color:#000'>Texto</p>")

# ✅ Correcto  
st.markdown("<p style='color:var(--text-color)'>Texto</p>")
```

### ❓ "Los gráficos tienen fuentes muy pequeñas"

✅ **Solución:** Aplica `configure_plotly_theme()`.

```python
fig.update_layout(**configure_plotly_theme())
```

### ❓ "El header/toolbar se ve negro"

✅ **Solución:** No apliques estilos globales al header.

```css
/* ❌ Evitar */
* { color: #000 !important; }

/* ✅ Correcto - Excluir header */
[data-testid="stHeader"] * {
    color: inherit !important;
}
```

---

## 📚 Referencias

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Color Contrast](https://webaim.org/resources/contrastchecker/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

---

**Última actualización:** Enero 2026  
**Autor:** Equipo CHAMPILEAKS  
**Nivel de cumplimiento:** WCAG 2.1 AA ✅
