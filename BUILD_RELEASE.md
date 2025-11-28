# 🚀 GUÍA DE BUILD Y RELEASE - MATRIZ DE REDES SOCIALES

## 📋 Tabla de Contenidos
1. [Información General](#información-general)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Build Local](#build-local)
4. [Testing Pre-Release](#testing-pre-release)
5. [Release a Producción](#release-a-producción)
6. [Rollback](#rollback)
7. [Monitoreo Post-Release](#monitoreo-post-release)

---

## 📦 Información General

### Versiones de Software

| Componente | Versión Mínima | Versión Recomendada | Notas |
|------------|----------------|---------------------|-------|
| Python | 3.11 | 3.13 | La app usa funcionalidades modernas |
| pip | 23.0 | 24.0+ | Para mejor resolución de dependencias |
| Git | 2.30 | 2.42+ | Para comandos modernos |
| Streamlit | 1.28.0 | 1.51.0 | Versión con st.secrets estable |

### Estructura de Dependencias

```
requirements.txt          → Producción (11 paquetes core)
requirements-dev.txt      → Desarrollo + Testing (35 paquetes adicionales)
```

**Tamaño aproximado de instalación:**
- Producción: ~450 MB
- Desarrollo: ~650 MB (incluye pytest, black, mypy, etc.)

---

## 🛠️ Preparación del Entorno

### 1. Clonar Repositorio

```bash
# HTTPS (recomendado para lectura)
git clone https://github.com/David2000-mp/Matriz-repositorio.git
cd Matriz-repositorio

# SSH (recomendado si tienes llave SSH configurada)
git clone git@github.com:David2000-mp/Matriz-repositorio.git
cd Matriz-repositorio
```

### 2. Crear Virtual Environment

#### Linux / macOS:
```bash
# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Verificar activación (debe mostrar ruta dentro de venv)
which python
```

#### Windows (PowerShell):
```powershell
# Crear venv
python -m venv venv_local

# Activar venv
.\venv_local\Scripts\Activate.ps1

# Si hay error de política de ejecución:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar activación (debe mostrar (venv_local) al inicio del prompt)
Get-Command python
```

### 3. Instalar Dependencias

#### Para Producción:
```bash
# Instalar solo dependencias de producción
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "streamlit|pandas|plotly|gspread"

# Debe mostrar:
# streamlit    1.51.0
# pandas       2.3.3
# plotly       6.5.0
# gspread      6.2.1
```

#### Para Desarrollo (incluye testing):
```bash
# Instalar dependencias de producción + desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verificar instalación de herramientas de testing
pytest --version
# Debe mostrar: pytest 8.3.3

black --version
# Debe mostrar: black, 24.10.0
```

### 4. Configurar Secretos

```bash
# Copiar plantilla de secretos
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Editar con tus credenciales reales
# (Ver SECURITY.md para instrucciones detalladas)
nano .streamlit/secrets.toml  # o usa tu editor favorito
```

---

## 🏗️ Build Local

### Verificar Integridad del Código

```bash
# 1. Verificar sintaxis de Python (no ejecuta código)
python -m py_compile app.py

# 2. Verificar imports (detecta módulos faltantes)
python -c "import app; print('✅ Imports OK')"

# 3. Verificar estructura de archivos
ls -la app.py utils/ components/ views/
# Debe mostrar:
# app.py
# utils/data_manager.py
# utils/helpers.py
# components/styles.py
# views/*.py
```

### Ejecutar Aplicación Localmente

```bash
# Iniciar servidor de desarrollo
streamlit run app.py

# Opciones adicionales:
streamlit run app.py --server.port 8502              # Puerto personalizado
streamlit run app.py --server.headless true          # Sin abrir navegador
streamlit run app.py --server.runOnSave true         # Hot-reload
streamlit run app.py --logger.level debug            # Logs detallados
```

### Verificar Funcionalidades Core

Checklist manual (en tu navegador http://localhost:8501):

- [ ] **Landing Page:** Carga sin errores
- [ ] **Conexión a Google Sheets:** Mensaje "✅ Conectado exitosamente"
- [ ] **Vista Dashboard:** Gráficos se renderizan correctamente
- [ ] **Vista Analytics:** Tablas se cargan sin errores
- [ ] **Data Entry:** Formulario funciona (sin guardar datos reales aún)
- [ ] **Settings:** Panel de configuración accesible
- [ ] **Navegación:** Todos los botones del sidebar funcionan

---

## 🧪 Testing Pre-Release

### Suite Completa de Tests

```bash
# Ejecutar todos los tests unitarios
pytest tests/ -v

# Resultado esperado:
# =================== 18 passed, 1 skipped in X.XXs ===================
```

### Tests con Cobertura

```bash
# Ejecutar tests con reporte de cobertura
pytest --cov=utils --cov=components --cov=views --cov-report=html

# Abrir reporte HTML
# Windows:
start htmlcov/index.html

# Linux/Mac:
open htmlcov/index.html  # o xdg-open en Linux

# Cobertura esperada:
# utils/data_manager.py: 71%+
# TOTAL: 27%+ (mejorará conforme agreguemos más tests)
```

### Tests de Integración (Opcional)

```bash
# Test de conexión real a Google Sheets (requiere credenciales válidas)
pytest tests/ -v -m integration

# ADVERTENCIA: Este test hace llamadas REALES a la API de Google
# Solo ejecutar si estás seguro de tus credenciales
```

### Linting y Formato

```bash
# 1. Verificar estilo de código (PEP 8)
flake8 app.py utils/ components/ views/ --max-line-length=120

# 2. Verificar tipos con mypy (opcional, puede mostrar muchos warnings)
mypy app.py utils/ --ignore-missing-imports

# 3. Formatear código automáticamente
black app.py utils/ components/ views/

# 4. Verificar que no hay cambios después del formato
git diff
# Si muestra cambios, commitea: git add . && git commit -m "style: format code with black"
```

---

## 🚀 Release a Producción

### Estrategia de Versionado

Seguimos **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

- **MAJOR:** Cambios incompatibles con versiones anteriores (ej: cambio en estructura de datos)
- **MINOR:** Nuevas funcionalidades compatibles (ej: nueva vista de Analytics)
- **PATCH:** Correcciones de bugs (ej: fix en cálculo de engagement rate)

Ejemplo: `v1.2.3`

### Checklist Pre-Release

- [ ] Todos los tests pasan (`pytest tests/ -v`)
- [ ] Cobertura de código ≥ 60% (`pytest --cov`)
- [ ] Código formateado con black (`black .`)
- [ ] Sin errores de linting (`flake8 . --max-line-length=120`)
- [ ] Documentación actualizada (`README.md`, `CHANGELOG.md`)
- [ ] Secretos NO están en el código ni en Git (`git log --all --full-history --source --grep="private_key"`)
- [ ] `.gitignore` incluye `.streamlit/secrets.toml`
- [ ] Changelog actualizado con nuevos cambios

### Proceso de Release

#### Opción A: Streamlit Cloud (Recomendado para MVP)

1. **Preparar Rama de Release**
   ```bash
   # Crear rama de release desde main
   git checkout main
   git pull origin main
   git checkout -b release/v1.2.3
   
   # Actualizar CHANGELOG.md
   nano CHANGELOG.md
   # Agregar:
   # ## [1.2.3] - 2024-11-26
   # ### Added
   # - Nueva funcionalidad X
   # ### Fixed
   # - Bug Y corregido
   
   # Commit y push
   git add CHANGELOG.md
   git commit -m "chore: prepare release v1.2.3"
   git push origin release/v1.2.3
   ```

2. **Crear Pull Request**
   - Ve a GitHub: https://github.com/David2000-mp/Matriz-repositorio/pulls
   - Click en "New Pull Request"
   - Base: `main` ← Compare: `release/v1.2.3`
   - Título: `Release v1.2.3: [descripción breve]`
   - Descripción: Copia el contenido del CHANGELOG para esta versión
   - Asigna revisores
   - Click "Create Pull Request"

3. **Code Review y Aprobación**
   - Espera aprobación de al menos 1 reviewer
   - Resuelve comentarios si los hay
   - Una vez aprobado, haz merge a `main`

4. **Crear Git Tag**
   ```bash
   # Volver a main y actualizar
   git checkout main
   git pull origin main
   
   # Crear tag anotado
   git tag -a v1.2.3 -m "Release v1.2.3: [descripción breve]"
   
   # Push del tag
   git push origin v1.2.3
   
   # Verificar tags existentes
   git tag -l
   ```

5. **Desplegar en Streamlit Cloud**
   - Ve a https://share.streamlit.io/
   - Click en tu aplicación existente (o "New app" si es primera vez)
   - Configuración:
     - **Repository:** David2000-mp/Matriz-repositorio
     - **Branch:** main
     - **Main file path:** app.py
     - **Python version:** 3.11
   - Click en **Settings > Secrets**
   - Copia el contenido de tu `.streamlit/secrets.toml` local
   - Pega en el editor de secretos
   - Click **Save**
   - Click **Reboot app**

6. **Verificar Despliegue**
   ```bash
   # Tu app estará disponible en:
   # https://[tu-app-name].streamlit.app/
   
   # Verificar:
   # 1. La app carga sin errores 500
   # 2. Conexión a Google Sheets funciona
   # 3. Todas las vistas son accesibles
   # 4. No hay logs de error en: Settings > Logs
   ```

#### Opción B: Auto-Hospedaje con Docker

1. **Crear Dockerfile**
   ```bash
   # Crear archivo Dockerfile en la raíz del proyecto
   nano Dockerfile
   ```

   ```dockerfile
   FROM python:3.13-slim
   
   # Metadata
   LABEL maintainer="tu-email@example.com"
   LABEL version="1.2.3"
   LABEL description="Matriz de Redes Sociales"
   
   # Variables de entorno
   ENV PYTHONUNBUFFERED=1 \
       PYTHONDONTWRITEBYTECODE=1 \
       PIP_NO_CACHE_DIR=1 \
       PIP_DISABLE_PIP_VERSION_CHECK=1
   
   # Directorio de trabajo
   WORKDIR /app
   
   # Instalar dependencias del sistema (si las hay)
   RUN apt-get update && apt-get install -y --no-install-recommends \
       && rm -rf /var/lib/apt/lists/*
   
   # Copiar y instalar dependencias de Python
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Copiar código de la aplicación
   COPY app.py .
   COPY utils/ ./utils/
   COPY components/ ./components/
   COPY views/ ./views/
   COPY .streamlit/ ./.streamlit/
   
   # Exponer puerto de Streamlit
   EXPOSE 8501
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
       CMD curl --fail http://localhost:8501/_stcore/health || exit 1
   
   # Comando de inicio
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build de la Imagen**
   ```bash
   # Build con tag de versión
   docker build -t matriz-redes:v1.2.3 .
   docker build -t matriz-redes:latest .
   
   # Verificar imagen creada
   docker images | grep matriz-redes
   ```

3. **Ejecutar Contenedor Localmente**
   ```bash
   # Ejecutar contenedor de prueba
   docker run -d \
     --name matriz-redes-test \
     -p 8501:8501 \
     -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro \
     matriz-redes:v1.2.3
   
   # Ver logs
   docker logs -f matriz-redes-test
   
   # Verificar que funciona
   curl http://localhost:8501/_stcore/health
   # Debe responder: {"status":"ok"}
   
   # Abrir en navegador
   open http://localhost:8501
   
   # Detener contenedor de prueba
   docker stop matriz-redes-test
   docker rm matriz-redes-test
   ```

4. **Push a Docker Registry**
   ```bash
   # Docker Hub (público)
   docker login
   docker tag matriz-redes:v1.2.3 tuusuario/matriz-redes:v1.2.3
   docker tag matriz-redes:latest tuusuario/matriz-redes:latest
   docker push tuusuario/matriz-redes:v1.2.3
   docker push tuusuario/matriz-redes:latest
   
   # O GitHub Container Registry (privado)
   echo $GITHUB_TOKEN | docker login ghcr.io -u David2000-mp --password-stdin
   docker tag matriz-redes:v1.2.3 ghcr.io/david2000-mp/matriz-redes:v1.2.3
   docker push ghcr.io/david2000-mp/matriz-redes:v1.2.3
   ```

5. **Desplegar en Servidor**
   ```bash
   # SSH al servidor de producción
   ssh usuario@tu-servidor.com
   
   # Pull de la imagen
   docker pull tuusuario/matriz-redes:v1.2.3
   
   # Detener versión anterior (si existe)
   docker stop matriz-redes-prod || true
   docker rm matriz-redes-prod || true
   
   # Ejecutar nueva versión
   docker run -d \
     --name matriz-redes-prod \
     --restart unless-stopped \
     -p 80:8501 \
     -v /ruta/segura/secrets.toml:/app/.streamlit/secrets.toml:ro \
     -e TZ=America/Mexico_City \
     tuusuario/matriz-redes:v1.2.3
   
   # Verificar health
   docker ps | grep matriz-redes-prod
   curl http://localhost/_stcore/health
   ```

---

## 🔄 Rollback

### Si Algo Sale Mal en Producción

#### Rollback en Streamlit Cloud

1. **Identificar Commit Anterior Estable**
   ```bash
   # Ver historial de commits
   git log --oneline -10
   
   # Ejemplo de output:
   # a1b2c3d (HEAD -> main, tag: v1.2.3) chore: prepare release v1.2.3
   # e4f5g6h (tag: v1.2.2) fix: corregir cálculo de engagement
   # h7i8j9k feat: agregar nueva vista de analytics
   ```

2. **Revertir en Streamlit Cloud**
   - Opción A: Cambiar branch a un tag anterior
     - Settings > Advanced > Branch: Cambiar a `v1.2.2`
     - Click "Reboot app"
   
   - Opción B: Revertir commit en Git
     ```bash
     # Crear rama de hotfix
     git checkout -b hotfix/rollback-v1.2.3
     
     # Revertir commit problemático
     git revert a1b2c3d --no-edit
     
     # Push y crear PR urgente
     git push origin hotfix/rollback-v1.2.3
     # Merge inmediato a main
     # Streamlit Cloud detectará el cambio y redesplegará automáticamente
     ```

#### Rollback en Docker

```bash
# SSH al servidor
ssh usuario@tu-servidor.com

# Detener versión problemática
docker stop matriz-redes-prod
docker rm matriz-redes-prod

# Ejecutar versión anterior (v1.2.2)
docker run -d \
  --name matriz-redes-prod \
  --restart unless-stopped \
  -p 80:8501 \
  -v /ruta/segura/secrets.toml:/app/.streamlit/secrets.toml:ro \
  -e TZ=America/Mexico_City \
  tuusuario/matriz-redes:v1.2.2

# Verificar que funciona
curl http://localhost/_stcore/health
```

---

## 📊 Monitoreo Post-Release

### Streamlit Cloud

1. **Revisar Logs**
   - Dashboard de Streamlit Cloud > Logs
   - Buscar errores con palabras clave: `ERROR`, `Exception`, `Failed`

2. **Métricas de Uso**
   - Dashboard > Analytics
   - Verificar:
     - Número de usuarios activos
     - Tiempo de respuesta promedio
     - Tasa de errores

### Logs Locales (Auto-hospedaje)

```bash
# Ver logs en tiempo real
docker logs -f matriz-redes-prod

# Buscar errores en últimas 100 líneas
docker logs matriz-redes-prod --tail 100 | grep -i error

# Exportar logs a archivo
docker logs matriz-redes-prod > logs/release-v1.2.3.log 2>&1
```

### Salud del Servidor (Auto-hospedaje)

```bash
# Verificar uso de recursos del contenedor
docker stats matriz-redes-prod

# Salida esperada:
# CONTAINER        CPU %    MEM USAGE / LIMIT    MEM %    NET I/O
# matriz-redes     2.5%     250MB / 2GB          12.5%    1.2MB / 500KB

# Si CPU > 80% o MEM > 80%, considerar escalar
```

### Alertas Automatizadas (Avanzado)

```bash
# Configurar alertas con cron (Linux)
# Crear script de monitoreo
nano /usr/local/bin/check-matriz-health.sh
```

```bash
#!/bin/bash
# Script de monitoreo de salud de Matriz de Redes

# Verificar que el contenedor está corriendo
if ! docker ps | grep -q matriz-redes-prod; then
    echo "ALERTA: Contenedor matriz-redes-prod NO está corriendo" | \
    mail -s "ALERTA: Matriz Redes CAÍDO" admin@example.com
    exit 1
fi

# Verificar health endpoint
if ! curl -f http://localhost/_stcore/health > /dev/null 2>&1; then
    echo "ALERTA: Health check FALLÓ" | \
    mail -s "ALERTA: Matriz Redes NO RESPONDE" admin@example.com
    exit 1
fi

echo "OK: Matriz de Redes funcionando correctamente"
```

```bash
# Hacer ejecutable
chmod +x /usr/local/bin/check-matriz-health.sh

# Agregar a crontab (ejecutar cada 5 minutos)
crontab -e
# Agregar línea:
# */5 * * * * /usr/local/bin/check-matriz-health.sh
```

---

## 📝 Changelog Template

Mantén un archivo `CHANGELOG.md` en la raíz del proyecto:

```markdown
# Changelog

Todos los cambios notables de este proyecto serán documentados aquí.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- Cambios que se están desarrollando actualmente

## [1.2.3] - 2024-11-26

### Added
- Nueva funcionalidad de exportación de reportes a PDF
- Vista de comparación de múltiples cuentas

### Fixed
- Corrección en cálculo de engagement rate cuando seguidores = 0
- Fix en filtro de fechas que no respetaba zona horaria

### Changed
- Actualización de dependencias: pandas 2.3.2 → 2.3.3
- Mejora en performance de carga de datos (30% más rápido)

### Security
- Rotación de credenciales de Google Cloud Platform
- Actualización de gspread para parchar CVE-2024-XXXX

## [1.2.2] - 2024-11-20

### Fixed
- Bug crítico en guardado de métricas con caracteres especiales

## [1.2.1] - 2024-11-15

### Added
- Validación de entrada de usuarios en formularios

### Fixed
- Corrección en formato de fechas para Excel export

## [1.2.0] - 2024-11-10

### Added
- Nueva vista de Analytics con gráficos avanzados
- Soporte para TikTok además de Facebook e Instagram

### Changed
- Refactorización completa del código (monolítico → modular)
- Mejora en arquitectura de caché

## [1.1.0] - 2024-11-01

### Added
- Integración con Google Sheets
- Sistema de logging mejorado

## [1.0.0] - 2024-10-20

### Added
- Lanzamiento inicial
- Dashboard básico con métricas
- CRUD de cuentas y métricas
```

---

## 🎯 Comandos Rápidos de Referencia

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ejecutar app
streamlit run app.py

# Ejecutar tests
pytest tests/ -v

# Formatear código
black .

# Verificar estilo
flake8 . --max-line-length=120
```

### Build y Release
```bash
# Congelar dependencias
pip freeze > requirements-frozen.txt

# Crear tag de release
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Build Docker
docker build -t matriz-redes:v1.2.3 .
docker push tuusuario/matriz-redes:v1.2.3
```

### Troubleshooting
```bash
# Ver logs de Streamlit
tail -f ~/.streamlit/logs/*

# Limpiar caché de Streamlit
rm -rf ~/.streamlit/cache

# Limpiar caché de pip
pip cache purge

# Reinstalar desde cero
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## 📚 Referencias

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Semantic Versioning](https://semver.org/lang/es/)
- [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)

---

**Mantenido por:** Equipo de DevOps  
**Última actualización:** 26 de noviembre de 2024
