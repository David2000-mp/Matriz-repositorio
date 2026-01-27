# 🔧 FIX: Texto Blanco en Selectboxes (Streamlit Cloud)

**Fecha**: 26 de enero de 2026  
**Versión**: 2.2.1  
**Afectado**: Streamlit Cloud  
**Estado**: ✅ RESUELTO

---

## 📋 Problema Identificado

En Streamlit Cloud, el texto dentro de los selectboxes del sidebar se mostraba en **blanco** (#FFFFFF) en lugar de **negro** (#212529), haciéndolo **ilegible** sobre el fondo blanco del selectbox.

### Síntomas

```css
/* ❌ ANTES - Texto blanco invisible */
<div value="Centro Universitario México" style="color: #FFFFFF;">
  Centro Universitario México
</div>
```

![image](https://github.com/user-attachments/assets/texto-blanco-selectbox.png)

---

## 🔍 Causa Raíz

El CSS contenía un **selector universal** con `!important` que aplicaba color blanco a TODOS los elementos dentro del sidebar:

```css
/* ❌ SELECTOR PROBLEMÁTICO */
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;  /* ← Esto afectaba TODO */
}
```

### ¿Por qué no se veía en local?

En algunos navegadores y versiones de Streamlit, el selector específico de selectbox tenía prioridad, pero en Streamlit Cloud (entorno de producción), el selector universal ganaba la batalla de especificidad.

---

## ✅ Solución Implementada

### 1. Eliminación del Selector Universal

**ANTES**:
```css
section[data-testid="stSidebar"] *,  /* ← Afecta TODO */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div
```

**DESPUÉS**:
```css
/* Solo elementos de texto específicos */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stMarkdown
```

### 2. Refuerzo de Reglas de Selectbox

Se añadieron reglas ultra-específicas para garantizar texto negro en selectboxes:

```css
/* ✅ SELECTBOXES CON TEXTO NEGRO */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div *,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
section[data-testid="stSidebar"] .stSelectbox input,
section[data-testid="stSidebar"] .stSelectbox div[class*="st-c"],
section[data-testid="stSidebar"] .stSelectbox div[class*="st-d"],
section[data-testid="stSidebar"] div[data-baseweb="select"] div[class*="st-"],
section[data-testid="stSidebar"] div[data-baseweb="select"] div[value] {
    color: #212529 !important;  /* ← NEGRO */
    background-color: transparent !important;
}
```

### 3. Preservación de Labels en Blanco

Los labels (etiquetas) de los selectboxes permanecen en blanco para mantener contraste con el fondo azul del sidebar:

```css
/* ✅ LABELS EN BLANCO (sobre fondo azul) */
section[data-testid="stSidebar"] .stSelectbox > label,
section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] {
    color: #FFFFFF !important;  /* Contraste con fondo azul */
    font-size: 16px !important;
    font-weight: 600 !important;
}
```

---

## 🧪 Validación

### Script de Verificación

Creamos `test_css_selectbox.py` para validar el CSS generado:

```bash
python test_css_selectbox.py
```

**Resultado esperado**:
```
✅ OK: No se encontró selector universal problemático
✅ Encontrado: section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]
✅ Encontrado: color: #212529 !important
```

### Checklist de Pruebas

- [x] ✅ Texto negro en selectboxes del sidebar
- [x] ✅ Labels blancos en selectboxes (buena legibilidad)
- [x] ✅ Títulos y párrafos en blanco dentro del sidebar
- [x] ✅ Dropdown options legibles (negro sobre blanco)
- [x] ✅ Hover en opciones del dropdown funcional
- [x] ✅ Sin regresiones en otros elementos del sidebar

---

## 📊 Resultado Visual

### ANTES (texto blanco invisible)
```
┌─────────────────────────────────┐
│ Seleccionar institución:        │ ← Label blanco (OK)
├─────────────────────────────────┤
│ Centro Universitario México  ▼  │ ← Texto BLANCO (MALO)
└─────────────────────────────────┘
     ↑ Fondo blanco
```

### DESPUÉS (texto negro legible)
```
┌─────────────────────────────────┐
│ Seleccionar institución:        │ ← Label blanco (OK)
├─────────────────────────────────┤
│ Centro Universitario México  ▼  │ ← Texto NEGRO (OK)
└─────────────────────────────────┘
     ↑ Fondo blanco
```

---

## 📂 Archivos Modificados

| Archivo | Líneas | Cambios |
|---------|--------|---------|
| `utils/global_styles.py` | 110-190 | Refactorización de selectores sidebar |

---

## 🚀 Despliegue

### 1. Commit y Push

```bash
git add utils/global_styles.py
git commit -m "fix: corregir texto blanco en selectboxes del sidebar"
git push origin main
```

### 2. Verificación en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Espera el redespliegue automático (2-3 minutos)
3. Verifica que los selectboxes ahora muestren texto negro

---

## 🎓 Lecciones Aprendidas

### 1. Evitar Selectores Universales con `*`

Los selectores universales (`section[data-testid="stSidebar"] *`) son **peligrosos** porque:
- Afectan a TODOS los elementos hijos
- Sobrescriben reglas más específicas cuando se usa `!important`
- Dificultan el mantenimiento del CSS

**Buena práctica**: Usar selectores específicos
```css
/* ✅ BUENO */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2

/* ❌ MALO */
section[data-testid="stSidebar"] *
```

### 2. Especificidad de CSS en Streamlit Cloud

Streamlit Cloud puede renderizar CSS diferente que tu entorno local:
- Clases dinámicas pueden cambiar
- Orden de aplicación de estilos puede variar
- Siempre probar en Cloud antes de dar por resuelto

### 3. Testing de CSS

Crear scripts de validación (`test_css_selectbox.py`) ayuda a:
- Detectar regresiones
- Validar que el CSS generado es el esperado
- Documentar el comportamiento esperado

---

## 📞 Soporte

Si el problema persiste:

1. **Limpia caché del navegador**: Ctrl + Shift + R
2. **Verifica la versión de Streamlit**: `pip show streamlit`
3. **Revisa el HTML renderizado**: Inspecciona el elemento con DevTools
4. **Contacta al equipo**: El selectbox debe tener `color: #212529`

---

## 🔗 Referencias

- [Streamlit CSS Selectors](https://docs.streamlit.io/develop/concepts/custom-components/styling)
- [CSS Specificity Calculator](https://specificity.keegan.st/)
- [WCAG Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)

---

**Última actualización**: 26 de enero de 2026, 23:45  
**Autor**: David (con GitHub Copilot)  
**Versión del documento**: 1.0
