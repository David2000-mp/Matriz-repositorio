# 🚀 Integración Continua (CI/CD) - Matriz de Redes Sociales

## 📋 Resumen

Este proyecto cuenta con **integración continua automatizada** que se ejecuta en cada push y pull request.

### ✅ Checks Automatizados

| Check | Descripción | Estado |
|-------|-------------|--------|
| **Tests** | Ejecuta 26+ tests unitarios e integración | ✅ Activo |
| **Cobertura** | Valida cobertura mínima de 75% | ✅ Activo |
| **Linting** | Análisis de código con Ruff | ✅ Activo |
| **Security** | Scan de vulnerabilidades en dependencias | ⚠️ Opcional |

---

## 🔧 Configuración Local

### Requisitos Previos

- Python 3.11, 3.12 o 3.13
- Git
- Cuenta de GitHub (para CI)

### Instalación de Dependencias

```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (testing, linting, etc.)
pip install -r requirements-dev.txt
```

---

## 🧪 Ejecutar Tests Localmente

### Tests Completos

```bash
# Ejecutar todos los tests con cobertura
pytest

# Tests específicos
pytest tests/test_data_manager.py

# Tests con output detallado
pytest -v -s

# Tests en paralelo (más rápido)
pytest -n auto
```

### Cobertura de Código

```bash
# Generar reporte de cobertura
pytest --cov=utils --cov=views --cov=components --cov-report=html

# Ver reporte en navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux

# Validar cobertura mínima (75%)
pytest --cov-fail-under=75
```

### Linting

```bash
# Ejecutar ruff (linting)
ruff check .

# Auto-fix de issues
ruff check . --fix

# Verificar formato
ruff format --check .

# Formatear código
ruff format .
```

---

## 🔄 Workflow de CI/CD

### Triggers (Cuándo se Ejecuta)

El CI se ejecuta automáticamente en:

1. **Push a `main` o `develop`** que modifique:
   - Archivos `.py`
   - `requirements.txt` o `requirements-dev.txt`
   - Tests en `tests/`
   - El workflow `.github/workflows/ci.yml`

2. **Pull Requests** hacia `main` o `develop`

3. **Manual** (desde GitHub Actions tab)

### Proceso del CI

```mermaid
graph TD
    A[Git Push] --> B[GitHub Actions Trigger]
    B --> C[Setup Python 3.11/3.12/3.13]
    C --> D[Instalar Dependencias]
    D --> E[Ejecutar Tests]
    E --> F{Tests Pasan?}
    F -->|Sí| G[Verificar Cobertura ≥75%]
    F -->|No| H[❌ CI FALLA]
    G -->|Sí| I[Linting con Ruff]
    G -->|No| H
    I --> J[Security Scan]
    J --> K[✅ CI PASA]
```

### Jobs del Workflow

#### 1. **Tests** (Matriz Multi-Python)
- Ejecuta en Python 3.11, 3.12 y 3.13
- Corre todos los tests de `tests/`
- Genera reporte de cobertura
- **FALLA si cobertura < 75%**
- Sube artefactos (htmlcov, coverage.xml)

#### 2. **Linting**
- Ejecuta `ruff check` para detectar errores
- Verifica formato de código
- No bloquea el merge (continue-on-error)

#### 3. **Security Scan**
- Usa `safety` para detectar vulnerabilidades
- Escanea todas las dependencias
- Genera advertencias pero no falla

#### 4. **Reporte Final**
- Consolida resultados de todos los jobs
- **FALLA si tests no pasan**
- Genera resumen en GitHub Actions

---

## 📊 Métricas de Cobertura

### Estado Actual

```
utils/data_manager.py:    75%  (191/255 líneas)
utils/logger.py:          56%  (40/72 líneas)
utils/helpers.py:         20%  (14/69 líneas)
components/styles.py:      0%  (0/10 líneas)
views/*:                   0%  (0/376 líneas)
-------------------------------------------
TOTAL:                    32%  (249/787 líneas)
```

### Meta de Cobertura

| Módulo | Actual | Meta | Estrategia |
|--------|--------|------|------------|
| `data_manager.py` | 75% | **80%** | ✅ Agregar 5 tests más |
| `logger.py` | 56% | 70% | Tests de error handling |
| `helpers.py` | 20% | 50% | Tests de funciones utilitarias |
| `views/` | 0% | 30% | Tests de integración UI |

---

## 🚨 Qué Hacer Si el CI Falla

### ❌ Tests Fallan

```bash
# 1. Ver qué test falló en el log de GitHub Actions
# 2. Reproducir localmente
pytest tests/ -v --tb=short

# 3. Si es un test específico
pytest tests/test_data_manager.py::test_nombre_del_test -v

# 4. Debuggear con ipdb
import ipdb; ipdb.set_trace()
```

### ❌ Cobertura < 75%

```bash
# 1. Ver qué líneas no están cubiertas
pytest --cov-report=term-missing

# 2. Ver reporte HTML detallado
pytest --cov-report=html
start htmlcov/index.html

# 3. Agregar tests para líneas sin cubrir
# 4. Re-run tests
pytest --cov-fail-under=75
```

### ❌ Linting Issues

```bash
# 1. Ver errores
ruff check .

# 2. Auto-fix (la mayoría se arreglan solos)
ruff check . --fix

# 3. Formatear código
ruff format .

# 4. Re-run
ruff check .
```

---

## 🔐 Configuración de Secrets

Para que el CI funcione correctamente con Google Sheets, necesitas configurar secrets:

### GitHub Secrets

1. Ve a: `Settings` → `Secrets and variables` → `Actions`
2. Agrega estos secrets:

```yaml
GCP_SERVICE_ACCOUNT: |
  {
    "type": "service_account",
    "project_id": "tu-proyecto",
    "private_key_id": "...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "...",
    "client_id": "...",
    "auth_uri": "...",
    "token_uri": "...",
    "auth_provider_x509_cert_url": "...",
    "client_x509_cert_url": "..."
  }
```

### Actualizar Workflow

Si necesitas secrets en CI, descomenta en `.github/workflows/ci.yml`:

```yaml
env:
  GCP_SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

---

## 📈 Badges para README

Agrega estos badges al `README.md` principal:

```markdown
[![Tests](https://github.com/David2000-mp/Matriz-repositorio/actions/workflows/ci.yml/badge.svg)](https://github.com/David2000-mp/Matriz-repositorio/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-75%25-yellow)](https://github.com/David2000-mp/Matriz-repositorio/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
```

---

## 🎯 Próximos Pasos

### Mejoras Sugeridas

1. **Aumentar Cobertura a 80%**
   - Agregar 5 tests más para `data_manager.py`
   - Cubrir líneas 401, 418, 436, 439-440, 448

2. **Codecov Integration**
   - Conectar con https://codecov.io
   - Ver trends de cobertura en PRs

3. **Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Tests de Integración UI**
   - Tests para `views/` con Streamlit
   - Uso de `streamlit.testing.v1`

5. **Performance Testing**
   - Benchmarks con `pytest-benchmark`
   - Alertas si tests se vuelven lentos

---

## 📚 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Docs](https://coverage.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)

---

## 🤝 Contribuir

Al hacer un PR, asegúrate de:

1. ✅ Todos los tests pasan (`pytest`)
2. ✅ Cobertura ≥ 75% (`pytest --cov-fail-under=75`)
3. ✅ Código formateado (`ruff format .`)
4. ✅ Sin errores de linting (`ruff check .`)
5. ✅ Documentación actualizada

---

**Última actualización**: 26 de noviembre de 2025  
**Versión CI**: 1.0  
**Autor**: David (con GitHub Copilot)
