# 🎨 Animaciones de Hover Implementadas

## Descripción General

Se han implementado animaciones suaves y profesionales que se activan cuando el usuario pasa el mouse sobre diferentes elementos de la interfaz. Las animaciones mejoran la experiencia de usuario sin ser invasivas.

## 📋 Elementos Animados

### 1. Métricas KPI (`st.metric`)

**Efectos aplicados:**
- ✨ **Elevación**: Se eleva 4px hacia arriba
- 📏 **Escala**: Aumenta al 102% de su tamaño original
- 🌟 **Sombra dinámica**: Sombra azul suave con 24px de blur
- 💫 **Efecto shimmer**: Brillo animado que recorre la caja
- 🎨 **Gradiente sutil**: Fondo con gradiente azul muy ligero
- 🔵 **Borde**: El borde cambia al azul institucional

**Código CSS:**
```css
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 24px rgba(0, 54, 150, 0.12);
    border-color: #003696;
    background: linear-gradient(135deg, rgba(0, 54, 150, 0.02) 0%, #FFFFFF 100%);
}
```

**Duración**: 0.3 segundos con curva `cubic-bezier(0.4, 0, 0.2, 1)`

---

### 2. Expanders (Desgloses por Plataforma)

**Efectos aplicados:**
- ➡️ **Deslizamiento lateral**: Se mueve 4px hacia la derecha
- 🌫️ **Sombra suave**: Sombra con 12px de blur
- 🎨 **Fondo sutil**: Fondo azul al 2% de opacidad

**Código CSS:**
```css
[data-testid="stExpander"]:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(0, 54, 150, 0.08);
    background: rgba(0, 54, 150, 0.02);
}
```

**Duración**: 0.3 segundos

---

### 3. Tablas Interactivas

**Efectos aplicados (filas):**
- 📈 **Escala**: Aumenta al 101% (muy sutil)
- 🎨 **Fondo**: Color azul al 4% de opacidad
- ⚡ **Transición rápida**: 0.2 segundos

**Código CSS:**
```css
table tbody tr:hover {
    background-color: rgba(0, 54, 150, 0.04);
    transform: scale(1.01);
}
```

**Efectos aplicados (tabla completa):**
- 🌫️ **Sombra**: Sombra suave al hacer hover sobre la tabla

---

### 4. Gráficas Plotly

**Efectos aplicados:**
- ⬆️ **Elevación**: Se eleva 4px
- 🌟 **Sombra pronunciada**: Sombra azul con 24px de blur

**Código CSS:**
```css
.js-plotly-plot:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 54, 150, 0.12);
}
```

**Duración**: 0.3 segundos

---

### 5. Tarjetas Personalizadas

**Efectos aplicados:**
- ⬆️ **Elevación ligera**: Se eleva 2px
- 🌫️ **Sombra media**: Sombra con 16px de blur

**Código CSS:**
```css
.stMarkdown > div[style*="border"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
```

**Duración**: 0.3 segundos

---

## 🎯 Principios de Diseño

### Consistencia
- Todas las animaciones usan el mismo timing base: **0.3 segundos**
- Función de easing consistente: `cubic-bezier(0.4, 0, 0.2, 1)`
- Colores alineados con la paleta institucional

### Sutileza
- Movimientos pequeños (2-4px) para no ser invasivos
- Escalas mínimas (1.01-1.02) para mantener profesionalismo
- Opacidades bajas en fondos y sombras

### Performance
- Uso de `transform` y `opacity` para animaciones GPU-aceleradas
- Sin uso de propiedades costosas como `width` o `height`
- Animaciones optimizadas para no afectar el rendimiento

### Accesibilidad
- Las animaciones son visuales, no afectan la funcionalidad
- Compatible con `prefers-reduced-motion` del sistema operativo
- Contraste WCAG AA mantenido en todos los estados

---

## 🚀 Cómo Ver las Animaciones

### Opción 1: En la Aplicación Principal
1. Ejecutar: `streamlit run app_refactored.py`
2. Navegar al Dashboard
3. Pasar el mouse sobre cualquier métrica, expander o gráfica

### Opción 2: Demo Interactiva
1. Ejecutar: `streamlit run demo_animaciones.py`
2. Se abrirá una página con ejemplos de todas las animaciones
3. Incluye explicaciones técnicas detalladas

---

## 📁 Archivos Modificados

### `utils/global_styles.py`
- Agregadas 150+ líneas de CSS para animaciones
- Sección completa dedicada a hover effects
- Keyframes para animaciones avanzadas (shimmer, float)

### `demo_animaciones.py` (nuevo)
- Archivo de demostración interactiva
- Muestra todos los tipos de animaciones
- Incluye documentación técnica

---

## 🔧 Personalización

### Cambiar la Velocidad de Animación

En `global_styles.py`, buscar:
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
```

Cambiar `0.3s` a:
- `0.2s` para más rápido
- `0.5s` para más lento

### Cambiar la Elevación

Buscar `translateY(-4px)` y ajustar:
- `-2px` para menos elevación
- `-6px` para más elevación

### Cambiar la Intensidad de Sombra

Buscar `box-shadow` y ajustar los valores:
```css
box-shadow: 0 8px 24px rgba(0, 54, 150, 0.12);
           /* ↑   ↑    ↑                    ↑
              |   |    |                    └─ Opacidad (0.12 = 12%)
              |   |    └───────────────────── Blur (24px)
              |   └────────────────────────── Spread (8px)
              └────────────────────────────── Offset Y (0px)
```

### Desactivar Animaciones Específicas

Comentar o eliminar el bloque CSS correspondiente en `global_styles.py`.

---

## ✅ Resultados

- ✨ **Experiencia mejorada**: La interfaz se siente más moderna y responsiva
- 🎨 **Feedback visual**: El usuario sabe claramente dónde está su mouse
- 🚀 **Performance óptima**: Sin impacto en velocidad de carga o interacción
- 📱 **Responsive**: Funcionan correctamente en diferentes tamaños de pantalla
- ♿ **Accesible**: No interfieren con lectores de pantalla o navegación por teclado

---

## 📊 Métricas de Implementación

| Elemento | Animaciones | Duración | Propiedades Animadas |
|----------|-------------|----------|---------------------|
| Métricas KPI | 5 | 0.3s | transform, shadow, border, background |
| Expanders | 3 | 0.3s | transform, shadow, background |
| Tablas (filas) | 2 | 0.2s | transform, background |
| Gráficas | 2 | 0.3s | transform, shadow |
| Tarjetas | 2 | 0.3s | transform, shadow |

**Total**: 14 efectos de animación diferentes aplicados a 5 tipos de elementos

---

## 🎓 Próximos Pasos Sugeridos

1. **Animaciones de entrada**: Agregar animaciones cuando los elementos aparecen por primera vez
2. **Microinteracciones**: Añadir feedback en botones y formularios
3. **Loading states**: Animaciones de skeleton mientras se cargan datos
4. **Transiciones de página**: Suavizar cambios entre vistas
5. **Tooltips animados**: Información adicional con animaciones sutiles

---

## 📞 Soporte

Para modificar o extender las animaciones, consultar:
- `utils/global_styles.py` - Estilos globales y animaciones
- `demo_animaciones.py` - Ejemplos y documentación
- [CSS Tricks - Transitions](https://css-tricks.com/almanac/properties/t/transition/)
- [MDN - Using CSS animations](https://developer.mozilla.org/es/docs/Web/CSS/CSS_Animations/Using_CSS_animations)
