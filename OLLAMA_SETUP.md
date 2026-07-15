# 🤖 Guía de Instalación y Configuración de Ollama en CHAMPILEAKS

## ¿Qué es Ollama?

Ollama es una plataforma que permite ejecutar modelos de lenguaje grandes (LLMs) en tu máquina local, sin enviar datos a servidores externos. Esto garantiza:

✅ **Privacidad total** — Los datos nunca salen de tu máquina  
✅ **Sin costo** — Usa recursos locales, sin subscripciones  
✅ **Funcionamiento offline** — No requiere conexión a internet  
✅ **Control completo** — Elige qué modelo usar  

---

## Requisitos Previos

### Hardware Mínimo
- **RAM**: 8 GB (recomendado 16 GB para mejor rendimiento)
- **Disco**: 10 GB libres (para descargar modelos)
- **GPU** (opcional pero recomendado):
  - NVIDIA: CUDA 11.x+ con 4GB+ VRAM (ideal: 8GB+)
  - Apple: Apple Silicon (M1/M2/M3) — optimizado automáticamente
  - AMD: ROCm support (experimental)

### Software
- Windows 10/11, macOS 11+, o Linux (Ubuntu 18.04+)
- PowerShell, Terminal, o Bash
- 10-15 minutos de tiempo libre para instalación y descarga

---

## Paso 1: Descargar e Instalar Ollama

### Windows
1. Descarga el instalador: https://ollama.ai/download/windows
2. Ejecuta el instalador `.exe`
3. Sigue los pasos del instalador (típicamente: Next → Next → Finish)
4. Ollama se instalará en: `C:\Users\<TuUsuario>\AppData\Local\Programs\Ollama`

### macOS
1. Descarga el instalador: https://ollama.ai/download/mac
2. Abre el archivo `.dmg`
3. Arrastra la app "Ollama" a la carpeta "Applications"
4. Abre Ollama.app desde Applications

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## Paso 2: Iniciar el Servicio de Ollama

Ollama debe estar ejecutándose en segundo plano para que CHAMPILEAKS pueda acceder a él.

### Windows
```powershell
# En PowerShell o Command Prompt
ollama serve
```

O simplemente abre la app "Ollama" desde el menú Start.

### macOS
```bash
# En Terminal
ollama serve
```

### Linux
```bash
# En Terminal
ollama serve
```

**Verás algo como:**
```
time=2024-01-15T10:30:00.123Z level=INFO source=main.go:104 msg="Listening on 127.0.0.1:11434"
```

✅ Deja esta terminal abierta mientras uses CHAMPILEAKS.

---

## Paso 3: Descargar un Modelo

**⚠️ IMPORTANTE: Ollama DEBE estar en ejecución (paso anterior) antes de descargar modelos.**

En una **nueva terminal/PowerShell** (NO cierres la anterior), ejecuta:

### Opción 1: Mistral (RECOMENDADO)
```bash
ollama pull mistral
```
- Tamaño: ~4.1 GB
- Velocidad: Rápido (2-3seg por respuesta)
- Multilingüe: Sí (español muy bueno)
- Recomendado para: Uso general

### Opción 2: Llama 2
```bash
ollama pull llama2
```
- Tamaño: ~3.8 GB
- Velocidad: Rápido
- Multilingüe: Bueno
- Recomendado para: Calidad máxima

### Opción 3: Neural-Chat (Ultra-ligero)
```bash
ollama pull neural-chat
```
- Tamaño: ~1.9 GB
- Velocidad: Ultra-rápido (1-2seg)
- Multilingüe: Limitado
- Recomendado para: Si tienes <8GB RAM

**La descarga comenzará automáticamente. Espera a que termine.** Verás:
```
pulling d92dd527f119... 100% ▓▓▓▓▓▓▓▓▓▓ 4.1 GB
verifying sha256 digest
writing manifest
removing any unused layers
success
```

---

## Paso 4: Verificar Instalación

En una nueva terminal, ejecuta:

```bash
# Listar modelos disponibles
ollama list
```

Deberías ver:
```
NAME            ID              SIZE    MODIFIED
mistral         xyz...          4.1 GB  2 hours ago
```

O prueba manualmente:

```bash
# Test simple
curl http://localhost:11434/api/tags
```

Si ves un JSON con tus modelos, ¡está funcionando! ✅

---

## Paso 5: Configurar CHAMPILEAKS

### 5.1 Instalar dependencia Python

```bash
cd c:\Users\SPARTAN PC\Matriz-repositorio
pip install ollama
```

O si estás usando `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5.2 Agregar configuración (Opcional, si no está en secrets)

Si usas `st.secrets.toml` (Streamlit), agrega:

```toml
[ollama]
base_url = "http://localhost:11434"
model = "mistral"
timeout = 30
enabled = true
```

O establece variables de entorno:

```bash
# Windows PowerShell
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_MODEL="mistral"
```

```bash
# Linux/Mac
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"
```

---

## Paso 6: Ejecutar CHAMPILEAKS

```bash
# En la raíz del proyecto
streamlit run app.py
```

CHAMPILEAKS ahora intentará usar Ollama automáticamente. Si no está disponible, usará heurísticas locales (fallback automático).

---

## ✅ Verificación: ¿Está Ollama siendo usado?

### En la UI de Streamlit

Si ves conclusiones, recomendaciones y análisis de sentimiento **narrativos y contextuales** (no solo reglas simples), ¡Ollama está activo!

### En los logs (terminal de CHAMPILEAKS)

```
2024-01-15 10:45:23 | INFO     | ollama_provider | is_available | Cliente Ollama creado exitosamente
2024-01-15 10:45:24 | DEBUG    | ollama_provider | _call_ollama | Ollama respondió exitosamente (245 chars)
```

### Si NO está funcionando

Verás:
```
2024-01-15 10:45:23 | WARNING  | ollama_provider | is_available | Ollama no disponible. Usando fallback a heurísticas.
```

**Troubleshooting:**

1. ¿Ollama está corriendo?
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Si falla, reinicia Ollama (`ollama serve` en nueva terminal)

2. ¿Modelo descargado?
   ```bash
   ollama list
   ```
   Si está vacío, descarga: `ollama pull mistral`

3. ¿Firewall bloqueando puerto 11434?
   - Windows Defender → Permitir aplicación → Ollama

4. ¿Usando proxy?
   - Modifica `st.secrets.toml`: `base_url = "http://tu-proxy:puerto"`

---

## 🔧 Modelos Alternativos

Si Mistral no te satisface, prueba otros:

```bash
# Descarga adicionales
ollama pull openchat          # 7B, bueno para español
ollama pull dolphin-phi       # 2.7B, ultra-ligero
ollama pull orca-mini         # 3B, balanceado
```

Para usar otro modelo, modifica `st.secrets.toml`:

```toml
[ollama]
model = "openchat"  # Cambiar aquí
```

---

## 📊 Benchmarks de Rendimiento Esperado

| Modelo | Tamaño | RAM Min. | GPU Ideal | Resp. Promedio |
|--------|--------|----------|-----------|---|
| **mistral** | 4.1 GB | 8 GB | 4GB | 2-3s |
| llama2 | 3.8 GB | 8 GB | 4GB | 2-4s |
| neural-chat | 1.9 GB | 4 GB | 2GB | 1-2s |
| openchat | 3.9 GB | 8 GB | 4GB | 2-3s |

**Primera llamada**: +3-5seg (carga del modelo a memoria)  
**Llamadas subsecuentes**: Tiempo mostrado (modelo ya en RAM)

---

## ⚙️ Configuración Avanzada (Opcional)

### Deshabilitar Ollama temporalmente

```toml
[ollama]
enabled = false  # Usa siempre fallback a heurísticas
```

### Usar Ollama remoto (servidor externo)

```toml
[ollama]
base_url = "http://192.168.1.100:11434"  # IP del servidor
model = "mistral"
```

### Aumentar timeout (para conexiones lentas)

```toml
[ollama]
timeout = 60  # En lugar de 30 segundos
```

### Cambiar temperatura (creatividad vs coherencia)

En `utils/ollama_provider.py`, línea ~190:

```python
"temperature": 0.3,  # 0.0 = determinístico, 1.0 = creativo
```

---

## 📚 Documentación Oficial

- Ollama Docs: https://github.com/ollama/ollama
- Model Library: https://ollama.ai/library
- API Reference: https://github.com/ollama/ollama/blob/main/docs/api.md

---

## ❓ Preguntas Frecuentes (FAQ)

**P: ¿CHAMPILEAKS funcionará sin Ollama?**  
R: Sí. Si Ollama no está disponible, el sistema usa automáticamente análisis heurísticos locales (sin LLM).

**P: ¿Cuánto espacio de disco requiere?**  
R: ~15 GB: 10 GB para Ollama + 5 GB para modelos (mistral o similar).

**P: ¿Puedo usar Ollama mientras trabajo en otras cosas?**  
R: Sí. Ollama usa CPU + GPU según disponibilidad. Si configuración es lenta, reduce temperatura o usa modelo más ligero.

**P: ¿Es seguro ejecutar Ollama 24/7?**  
R: Sí. Es un servicio simple. Para ahorrar recursos, puedes cerrarlo cuando no uses CHAMPILEAKS.

**P: ¿Puedo cambiar de modelo sin reinstalar?**  
R: Sí. Solo ejecuta `ollama pull nuevo-modelo` y cambia `model` en `st.secrets.toml`.

**P: ¿Qué pasa con mis datos?**  
R: Todo se procesa localmente. Cero datos se envían a internet (a menos que usesGoogle Sheets, que ya estaba configurado).

---

## 🚀 Próximos Pasos

1. ✅ Ollama instalado y ejecutando
2. ✅ Modelo descargado (mistral recomendado)
3. ✅ Python dependencies instaladas (`pip install ollama`)
4. ✅ Configuración en `st.secrets.toml`
5. ⏭️ Ejecutar CHAMPILEAKS: `streamlit run app.py`
6. ⏭️ Verificar logs para confirmar que Ollama está activo
7. ⏭️ Usar la interfaz normalmente (Ollama se usará automáticamente en análisis avanzados)

---

## 📞 Soporte

Si hay problemas:

1. Verifica que `ollama serve` esté en ejecución en terminal separada
2. Verifica que el modelo esté descargado: `ollama list`
3. Revisa los logs de CHAMPILEAKS (ej: "ERROR" o "WARNING" en terminal Streamlit)
4. Prueba manualmente: `curl http://localhost:11434/api/tags`
5. Verifica que no haya firewall bloqueando puerto 11434

¡Listo! Disfruta de CHAMPILEAKS con poder de LLM local. 🎉
