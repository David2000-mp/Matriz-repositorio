# ⚡ Quick Start Ollama (5 minutos)

## 1️⃣ Instalar Ollama (3 min)

### Windows
1. Descarga: https://ollama.ai/download/windows
2. Ejecuta el `.exe` → Next → Finish
3. En **PowerShell nueva**, ejecuta:
   ```powershell
   ollama serve
   ```
4. Deja esa terminal abierta

### macOS
```bash
# Descarga desde https://ollama.ai/download/mac
# O usa Homebrew:
brew install ollama

# En Terminal:
ollama serve
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

✅ Deberías ver: `"Listening on 127.0.0.1:11434"`

---

## 2️⃣ Descargar Modelo (1 min)

**En NUEVA terminal** (NO cierres la del paso 1):

```bash
ollama pull mistral
```

Espera a que termine. Verás: `success`

**Tamaño**: ~4.1 GB  
**Tiempo**: 5-15 min (depende de tu conexión)

---

## 3️⃣ Instalar Python Dependency (30 seg)

```bash
cd c:\Users\SPARTAN PC\Matriz-repositorio
pip install ollama
```

---

## 4️⃣ Ejecutar CHAMPILEAKS

```bash
streamlit run app.py
```

**✅ ¡LISTO!**

Ollama ahora se usa automáticamente en:
- 💬 Análisis de comentarios (sentimiento contextual)
- 📊 Reportes (conclusiones narrativas)
- 📝 Contenido (clasificación temática)
- 💡 Recomendaciones (personalizadas)

---

## ❌ Si no funciona

### Verificar Ollama está corriendo
```bash
curl http://localhost:11434/api/tags
```

Si falla → vuelve al terminal del paso 1 y verifica que dice `Listening...`

### Ver logs detallados
En CHAMPILEAKS, busca en la terminal:
- ✅ `"Ollama está disponible"` = funcionando
- ⚠️ `"Ollama no disponible"` = fallback a heurísticas

### Modelo no descargado
```bash
ollama list
```

Si no ves `mistral`, descárgalo:
```bash
ollama pull mistral
```

---

## 🎯 Próximos Pasos

- Lee [OLLAMA_SETUP.md](OLLAMA_SETUP.md) para config avanzada
- Lee [OLLAMA_IMPLEMENTATION_SUMMARY.md](OLLAMA_IMPLEMENTATION_SUMMARY.md) para detalles técnicos
- Prueba las funciones mejoradas en código Python si quieres

---

## 📍 Ubicación de Archivos

- **Core**: `utils/ollama_provider.py`
- **Funciones mejoradas**: `utils/ollama_extensions*.py`
- **Setup**: `OLLAMA_SETUP.md`
- **Resumen**: `OLLAMA_IMPLEMENTATION_SUMMARY.md`
- **Config**: `.env.example`

---

## ⏱️ Tiempos de Respuesta

| Métrica | Tiempo |
|---|---|
| Primera llamada | 5-10s (carga de modelo) |
| Llamadas subsecuentes | 2-3s |
| Caché hit | <100ms |

**Aceptable para UI de Streamlit** (no bloquea más de 3s típico)

---

¡Disfruta de CHAMPILEAKS con poder de LLM local! 🚀
