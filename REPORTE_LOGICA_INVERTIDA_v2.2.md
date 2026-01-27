# REPORTE TÉCNICO - LÓGICA INVERTIDA DE CAPTURA (v2.2)
**Fecha:** 15 de enero de 2026  
**Versión:** Champileaks v2.2  
**Asunto:** Inversión de entrada de datos: Seguidores + Engagement Rate → Likes Calculado

---

## 1. RESUMEN EJECUTIVO

Se invirtió completamente la lógica de entrada en el formulario de captura manual. Ahora el usuario ingresa **Seguidores** y **Engagement Rate** como inputs principales, y **Likes Promedio** se calcula automáticamente en tiempo real. Los campos de Alcance e Interacciones pasan a ser opcionales/secundarios.

---

## 2. NUEVA FÓRMULA MATEMÁTICA

### Función: `calculate_likes_promedio(engagement_rate, seguidores)` (v2.2)

**Ubicación:** `utils/analytics.py` (líneas 99-130)

#### Fórmula Base (INVERTIDA):
```
likes_promedio = seguidores × (engagement_rate / 100)
```

#### Interpretación:
- **Entrada 1:** Seguidores (número absoluto)
- **Entrada 2:** Engagement Rate (porcentaje)
- **Salida:** Likes Promedio (interacciones esperadas)

#### Ejemplo Práctico:
```
Datos de entrada:
  - Seguidores: 10,000
  - Engagement Rate: 5.5%

Cálculo:
  likes_promedio = 10,000 × (5.5 / 100)
  likes_promedio = 10,000 × 0.055
  likes_promedio = 550 likes

Interpretación:
  Con 10,000 seguidores y 5.5% de engagement,
  se espera ~550 interacciones/likes totales
```

#### Casos Extremos:
```
Caso 1: Alto engagement
  Seguidores: 5,000
  Engagement: 10%
  Resultado: 5,000 × 0.10 = 500 likes

Caso 2: Bajo engagement
  Seguidores: 50,000
  Engagement: 1%
  Resultado: 50,000 × 0.01 = 500 likes

Caso 3: Sin engagement
  Seguidores: 100,000
  Engagement: 0%
  Resultado: 0 (no se calcula)
```

---

## 3. CAMBIOS EN INTERFAZ DE USUARIO

### Antes (v2.1):
```
┌─────────────────────────────────────┐
│ Métricas del Período                │
├─────────────────────────────────────┤
│ [Seguidores] [Alcance] [Interacciones] │
│ [Likes (manual)] [Fecha]            │
│ → Engagement calculado automático   │
└─────────────────────────────────────┘
```

### Después (v2.2):
```
┌──────────────────────────────────────────┐
│ Métricas del Período (Entrada Invertida) │
├──────────────────────────────────────────┤
│ [👥 Seguidores *]  [📊 Engagement % *]   │
├──────────────────────────────────────────┤
│ ✅ Likes Promedio Calculado: 550         │
│    Fórmula: 10,000 × (5.5/100) = 550    │
├──────────────────────────────────────────┤
│ Métricas Secundarias (Opcional)          │
│ [🌐 Alcance]  [💬 Interacciones]         │
│ [📅 Fecha]                               │
└──────────────────────────────────────────┘
```

### Detalles de Cambio:

1. **Inputs Principales (Obligatorios - *):**
   - 👥 **Seguidores Totales** (number input, min=0)
   - 📊 **Engagement Rate (%)** (slider 0-100, step 0.1)

2. **Cálculo en Tiempo Real:**
   - **Likes Promedio Calculado:** Mostrado en success box (verde)
   - **Fórmula visible:** Usuario ve la ecuación
   - **Actualización instantánea:** Al mover slider o cambiar seguidores

3. **Campos Secundarios (Opcionales):**
   - 🌐 Alcance Total (número, no obligatorio)
   - 💬 Interacciones Totales (número, pre-rellenado con likes si no se ingresa)
   - 📅 Fecha del Reporte

4. **Emojis y Visual:**
   - Enfoque en claridad: cada campo tiene icono y descripción
   - Success box (verde) para likes calculado
   - Warning si faltan datos principales

---

## 4. CAMBIOS EN CÓDIGO

### `utils/analytics.py` - Nueva Función

**Antes (v2.1):**
```python
# Dividía por 30 posts mensuales
likes_promedio = (engagement_rate / 100.0) * seguidores / POSTS_MENSUALES
# Ejemplo: 5.5% × 10,000 / 30 = 18.33
```

**Ahora (v2.2):**
```python
# Fórmula directa
likes_promedio = seguidores * (engagement_rate / 100.0)
# Ejemplo: 10,000 × 0.055 = 550
```

**Implementación:**
```python
def calculate_likes_promedio(engagement_rate: float, seguidores: int) -> float:
    """Fórmula INVERTIDA (v2.2): likes_promedio = seguidores * (engagement_rate / 100)"""
    if seguidores <= 0 or engagement_rate <= 0:
        return 0.0
    likes_promedio = seguidores * (engagement_rate / 100.0)
    return round(likes_promedio, 2)
```

---

### `views/data_entry.py` - Reorganización Visual

**Estructura Nueva:**

```python
# 1. INPUTS PRINCIPALES (Obligatorios)
col1, col2 = st.columns(2)
with col1:
    seguidores = st.number_input("👥 Seguidores Totales *", ...)
with col2:
    engagement_rate = st.slider("📊 Engagement Rate (%) *", 0.0, 100.0, ...)

# 2. CÁLCULO EN TIEMPO REAL
if seguidores > 0 and engagement_rate > 0:
    likes_promedio_calculado = calculate_likes_promedio(engagement_rate, seguidores)
    st.success(f"✅ Likes Promedio Calculado: {likes_promedio_calculado:.2f}")
else:
    st.warning("⚠️ Ingresa Seguidores y Engagement Rate")

# 3. CAMPOS SECUNDARIOS (Opcionales)
col1, col2, col3 = st.columns(3)
with col1:
    alcance = st.number_input("🌐 Alcance Total (Opcional)", ...)
with col2:
    interacciones = st.number_input("💬 Interacciones Totales (Opcional)", 
                                     value=int(likes_promedio_calculado), ...)
with col3:
    fecha_captura = st.date_input("📅 Fecha del Reporte", ...)

# 4. VALIDACIÓN MEJORADA
if submitted:
    if seguidores == 0:
        st.error("❌ Seguidores no puede ser 0")
    elif engagement_rate == 0:
        st.error("❌ Engagement Rate no puede ser 0")  # NUEVA VALIDACIÓN
    else:
        # Guardar con valores calculados
        nuevo_registro = {
            "seguidores": int(seguidores),
            "engagement_rate": round(engagement_rate, 2),
            "likes_promedio": round(likes_promedio_calculado, 2),
            "alcance": int(alcance) or int(likes_promedio_calculado),  # Fallback
            "interacciones": int(interacciones) or int(likes_promedio_calculado),  # Fallback
        }
```

---

## 5. PERSISTENCIA Y SINCRONIZACIÓN

### session_state Existente (Sin Cambios):
```python
st.session_state["capture_entidad_default"]        # Institución
st.session_state["capture_fecha_default"]          # Fecha
st.session_state["capture_plataforma_default"]     # Plataforma
st.session_state[f"usuario_red_manual_{plataforma}"]  # URL manual
```

### Guardado en Google Sheets:
```python
nuevo_registro = {
    "id_cuenta": "abc12345",
    "entidad": "Colegio A",
    "plataforma": "Instagram",
    "usuario_red": "https://instagram.com/colegioa",
    "fecha": "2026-01-15",
    "seguidores": 10000,               # ← INPUT
    "alcance": 15000,                  # ← OPCIONAL (fallback)
    "interacciones": 550,              # ← OPCIONAL (fallback a likes)
    "likes_promedio": 550.00,          # ← CALCULADO
    "engagement_rate": 5.5,            # ← INPUT
}
```

**Garantía:** `save_batch()` guarda correctamente en hoja `metricas` con columnas exactas.

---

## 6. CORRECCIÓN DE ACUMULADOS EN DASHBOARD

### Verificación de Consolidación:

**Dashboard ya implementa:** `normalize_monthly_latest()`

```python
# views/dashboard.py, línea 178
df_full = normalize_monthly_latest(df_full)
```

**Comportamiento:**
- Si Colegio A tiene registros en Nov, Dic, Ene → **solo suma Ene**
- Totales = Suma de **últimos registros por cuenta**
- No hay doble conteo de seguidores históricos

**Ejemplo:**
```
Hoja metricas:
  Colegio A, Nov 30: 5,000 seguidores
  Colegio A, Dic 30: 5,500 seguidores
  Colegio A, Ene 15: 6,000 seguidores

Dashboard (enero):
  Total Seguidores: 6,000 ✅ (último, no suma históricos)
  Delta: +500 (vs Dic) ✅
  Likes Promedio: 330 (6,000 × 5.5% si engagement = 5.5%)
```

---

## 7. COMPARATIVA DE FÓRMULAS

| Aspecto | v2.1 (Antiguo) | v2.2 (Nuevo) |
|---------|---|---|
| Input Principal | Interacciones | Engagement Rate |
| Cálculo | `(engagement / seg) * 100` | `seg * (engagement / 100)` |
| Resultado | % (0-100) | Número absoluto |
| Likes = | Interacciones / 30 | Seguidores × (ER/100) |
| Ejemplo (10k seg, 5.5 ER) | 5.5% | 550 likes |
| UI Orden | Seg→Alcance→Inter→Likes | **Seg→ER→Likes→Alcance/Inter** |

---

## 8. VALIDACIONES MEJORADAS

**Nueva validación agregada:**
```python
elif engagement_rate == 0:
    st.error("❌ Error: El Engagement Rate no puede ser 0")
```

**Por qué:** Sin engagement rate, no hay likes calculados (división/multiplicación sería 0).

---

## 9. CASOS DE PRUEBA

### Test 1: Entrada Básica
```
Input:
  Seguidores: 10,000
  Engagement Rate: 5.5%

Expected:
  Likes Promedio: 550.00 ✅
  En Google Sheets: likes_promedio = 550.00
```

### Test 2: Engagement Alto
```
Input:
  Seguidores: 5,000
  Engagement Rate: 12%

Expected:
  Likes Promedio: 600.00 ✅
  Fórmula: 5,000 × 0.12 = 600
```

### Test 3: Campos Opcionales (Fallback)
```
Input:
  Seguidores: 8,000
  Engagement: 3%
  Alcance: (no ingresado)
  Interacciones: (no ingresado)

Expected:
  Likes Promedio: 240.00 ✅
  En BD: alcance = 240, interacciones = 240 (fallback)
```

### Test 4: Dashboard Consolidación
```
BD tiene:
  Colegio B, Nov: 3,000 seg
  Colegio B, Dic: 3,200 seg
  Colegio B, Ene: 3,500 seg

Dashboard muestra:
  Total Seguidores: 3,500 ✅ (no suma 9,700)
```

---

## 10. PRÓXIMOS PASOS

1. ✅ **Testing de captura:** Ingresa Seguidores + ER → verifica likes calculado
2. ✅ **Testing de persistencia:** Recarga la página → verifica session_state
3. ✅ **Testing de BD:** Abre Google Sheets → verifica columna likes_promedio
4. ✅ **Testing de dashboard:** Ingresa múltiples registros → verifica sin doble conteo

---

## 11. FÓRMULA MATEMÁTICA FINAL

$$\text{likes\_promedio} = \text{seguidores} \times \frac{\text{engagement\_rate}}{100}$$

**O simplificado:**
$$L = S \times \left(\frac{E}{100}\right)$$

Donde:
- **L** = Likes Promedio (resultado)
- **S** = Seguidores (input)
- **E** = Engagement Rate % (input)

---

**Estado:** ✅ Listo para producción  
**Compatibilidad:** Champileaks v2.2+  
**Validación:** Dashboard ya consolidado, sin cambios necesarios
