# 📊 RESUMEN EJECUTIVO - DIAGNÓSTICO GOOGLE SHEETS

**Aplicación:** ChampiLeaks (Maristas Analytics)  
**Fecha:** Enero 9, 2026  
**Estado:** ⚠️ CONEXIÓN COMPROMETIDA  
**Gravedad:** 🔴 CRÍTICA (app no funciona sin Sheets)  

---

## 🎯 LÍNEA INFERIOR

Tu aplicación **NO puede leer ni escribir datos en Google Sheets** porque:

1. **Las credenciales no están configuradas** (archivo `.env` vacío)
2. **El caché bloquea actualizaciones** durante 5 minutos
3. **No hay validación de estructura** para diferenciar errores
4. **Existe duplicación de lógica** entre dos módulos

**Tiempo para arreglar:** 30-60 minutos (Fase 1)  
**Costo de no arreglar:** Pérdida total de funcionalidad + datos

---

## 📋 ENTREGABLES GENERADOS

| Documento | Propósito | Acción |
|-----------|-----------|--------|
| [REPORTE_DIAGNOSTICO_GOOGLE_SHEETS.md](./REPORTE_DIAGNOSTICO_GOOGLE_SHEETS.md) | Análisis completo de problemas | 📖 LEER PRIMERO |
| [GUIA_IMPLEMENTACION_FASE1.md](./GUIA_IMPLEMENTACION_FASE1.md) | Pasos para restaurar conexión | 🚀 HACER PRIMERO |
| `diagnostic_sheets.py` | Script de diagnóstico automático | ▶️ EJECUTAR AHORA |
| `utils/sheets_validator.py` | Validador de estructura | 📦 YA INCLUIDO |
| `utils/id_validator.py` | Protector de IDs | 📦 YA INCLUIDO |

---

## ⚡ 3 PASOS INMEDIATOS (30 minutos)

### ✅ PASO 1: Obtener Credenciales (10 min)

```bash
# 1. Ir a Google Cloud Console
# https://console.cloud.google.com/iam-admin/serviceaccounts

# 2. Crear o descargar JSON key de Service Account
# Copiar estos valores:
# - private_key_id
# - private_key
# - client_email
# - project_id
# - google_sheets_id (de Google Sheets URL)
```

### ✅ PASO 2: Actualizar .env (10 min)

```bash
# 1. Abrir archivo: f:\MATRIZ DE REDES\social_media_matrix\.env

# 2. Reemplazar con valores reales:
GOOGLE_SHEETS_ID=1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY
GCP_PROJECT_ID=hybrid-shelter-426922-i8
GCP_PRIVATE_KEY_ID=9c6fc02fffb6dea31445a60a5b65e6457dbf4202
GCP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GCP_CLIENT_EMAIL=matriz-bot@hybrid-shelter-426922-i8.iam.gserviceaccount.com

# 3. Compartir Google Sheets con el email (permisos: Editor)
```

### ✅ PASO 3: Validar (10 min)

```bash
# Ejecutar script de diagnóstico
cd "f:\MATRIZ DE REDES\social_media_matrix"
.\venv_stable\Scripts\Activate.ps1
python diagnostic_sheets.py

# Salida esperada: ✅ TODAS LAS PRUEBAS PASARON
```

---

## 🔍 ANÁLISIS TÉCNICO RESUMIDO

### Problema #1: Credenciales Ausentes (CRÍTICO)

```
.env vacío
  ↓
sheets_connector._get_service_account_config() retorna None
  ↓
conectar_sheets() retorna None
  ↓
load_data() cae a fallback CSV
  ↓
guardar_datos() falla sin respaldo
  ↓
❌ DATOS PERDIDOS
```

**Impacto:** 100% de funcionalidad comprometida

### Problema #2: Caché Bloqueado (ALTO)

```
Si Sheets falla en primer intento
  ↓
load_data() cachea resultado vacío por 5 minutos
  ↓
Usuario debe esperar para ver datos frescos
  ↓
Incluso si se arregla Sheets, sigue viendo datos viejos
```

**Impacto:** Usuarios ver datos obsoletos

### Problema #3: Duplicación de Lógica (MEDIO)

```
sheets_connector.py         data_manager.py
  - Abre por ID              - Abre por nombre
  - Fallbacks múltiples      - Solo st.secrets
  - Mejor mantenimiento      - Duplica código
```

**Impacto:** Difícil mantener, confuso diagnosticar

### Problema #4: Validación Ausente (MEDIO)

```
No se distingue entre:
- Hoja no existe → ❌ Estructura inválida
- Permisos insuficientes → ⚠️ Error de autenticación
- Quota excedido → ⏸️ Rate limiting
- Todo falla silenciosamente
```

**Impacto:** Difícil diagnosticar problemas

---

## 📊 MAPEO DE RIESGO

```
CRÍTICO (Arreglar YA)
├─ Credenciales no configuradas ────────────────────→ Fase 1 (30 min)
└─ Google Sheets no accesible ─────────────────────→ Fase 1 (30 min)

ALTO (Arreglar en 48h)
├─ Caché bloquea actualizaciones ──────────────────→ Fase 2 (2h)
├─ Sin validación de estructura ───────────────────→ Fase 2 (2h)
└─ Duplicación de lógica ─────────────────────────→ Fase 2 (2h)

MEDIO (Arreglar semana siguiente)
├─ IDs pueden corromperse ────────────────────────→ Fase 2 (1h)
├─ Sin alertas en Streamlit Cloud ───────────────→ Fase 3 (3h)
└─ Sin health checks automáticos ────────────────→ Fase 3 (3h)
```

---

## 🛠️ PLAN DE ACCIÓN

### Fase 1: Restauración (HOY - 30 minutos)
- [ ] Obtener credenciales GCP
- [ ] Actualizar `.env` con valores reales
- [ ] Compartir Google Sheets con service account
- [ ] Ejecutar `diagnostic_sheets.py`
- [ ] Verificar que la app funciona

**Salida esperada:** App funcional, datos fluyen

### Fase 2: Blindaje (Mañana - 3-4 horas)
- [ ] Reducir TTL de caché (300 → 60 segundos)
- [ ] Implementar `sheets_validator.py` en `data_loader.py`
- [ ] Implementar `id_validator.py` en escrituras
- [ ] Unificar lógica de conexión (usar solo `sheets_connector.py`)
- [ ] Mejorar mensajes de error

**Salida esperada:** Caché no bloquea, IDs protegidos, errores claros

### Fase 3: Monitoreo (Próximas 2 semanas)
- [ ] Configurar secrets en Streamlit Cloud
- [ ] Implementar CI/CD health checks (GitHub Actions)
- [ ] Agregar logging centralizado (Sentry)
- [ ] Implementar graceful degradation

**Salida esperada:** Alertas automáticas si Sheets cae, fallback robusto

---

## 📞 PRÓXIMOS PASOS

**AHORA (próximos 30 minutos):**

1. Abre [GUIA_IMPLEMENTACION_FASE1.md](./GUIA_IMPLEMENTACION_FASE1.md)
2. Sigue los 6 pasos exactamente como se indica
3. Ejecuta `python diagnostic_sheets.py`
4. Valida que la app funciona

**SI TIENES ERRORES:**

1. Ejecuta `python diagnostic_sheets.py --fix-cache` para limpiar caché
2. Revisa sección TROUBLESHOOTING en la guía
3. Consulta [REPORTE_DIAGNOSTICO_GOOGLE_SHEETS.md](./REPORTE_DIAGNOSTICO_GOOGLE_SHEETS.md) para detalle técnico

**DESPUÉS DE ARREGLAR:**

1. Abre la app y prueba lectura/escritura
2. Verifica datos en Google Sheets
3. Comunica a usuarios que conexión está restaurada

---

## 📌 NOTAS IMPORTANTES

### Sobre Streamlit Cloud
- Los secrets en Streamlit Cloud NO se heredan de `.env`
- Necesitas configurarlos en https://share.streamlit.io/settings/secrets
- El formato debe ser TOML (NO JSON)

### Sobre Google Sheets
- El service account email DEBE tener permisos de "Editor"
- El spreadsheet DEBE tener las 5 hojas requeridas (cuentas, metricas, config, comentarios, usernames_editados)
- Los IDs DEBEN ser strings hexadecimales de 8 caracteres

### Sobre Datos Existentes
- NO se perderán datos al arreglar credenciales
- Los datos en Google Sheets se mantienen igual
- El CSV local es respaldo, pero NO es el source of truth

---

## 🎓 EDUCATIVO

### ¿Por qué pasó esto?

1. **Variables de entorno con placeholders** - Se copiaron plantillas sin llenar valores reales
2. **Caché agresivo** - 5 minutos es demasiado para una app que debe reflejar cambios inmediatos
3. **Fallback débil** - Cuando Sheets falla, CSV local permite continuar pero con datos desactualizados
4. **Validación ausente** - Cuando algo falla, no se sabe qué falló exactamente

### ¿Cómo evitarlo en el futuro?

1. **Validation on startup** - Verificar credenciales antes de dejar usar la app
2. **Graceful degradation** - Mostrar modo "offline" cuando Sheets no está disponible
3. **Clear errors** - No capturar todas las excepciones genéricamente
4. **Health checks** - Monitoreo automático en Streamlit Cloud

---

## ✅ VALIDACIÓN DE ÉXITO

Una vez completada Fase 1, deberías ver:

```
✅ App carga sin errores
✅ Dashboard muestra datos de Google Sheets
✅ Captura manual guarda datos en Sheets y CSV
✅ Nuevos datos aparecen en Sheets en <2 segundos
✅ Caché se invalida tras escribir datos
✅ No hay errores en logs (.app_errors.log)
```

---

**Tiempo total estimado:** 45 minutos  
**Personas requeridas:** 1 (tú)  
**Riesgo:** Bajo (no se pierden datos)  
**ROI:** Alto (app vuelve a funcionar)

¡Adelante! 🚀
