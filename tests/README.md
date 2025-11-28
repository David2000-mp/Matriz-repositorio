# 🧪 TESTING GUIDE - CHAMPILYTICS

## 📋 RESUMEN RÁPIDO

**Estado actual**: 0% → Target 80% coverage  
**Framework**: pytest 8.3.3  
**Estrategia**: Unit tests con mocking completo de Google Sheets

---

## 🚀 INSTALACIÓN

```powershell
# 1. Activar entorno virtual
.\venv_local\Scripts\Activate.ps1

# 2. Instalar dependencias de testing
pip install -r requirements-dev.txt

# 3. Verificar instalación
pytest --version
```

---

## 🎯 EJECUTAR TESTS

### Comandos básicos

```powershell
# Ejecutar TODOS los tests
pytest

# Ejecutar con verbosidad (muestra cada test)
pytest -v

# Ejecutar tests de un archivo específico
pytest tests/test_data_manager.py

# Ejecutar un test específico
pytest tests/test_data_manager.py::test_load_data_conexion_exitosa_devuelve_dos_dataframes

# Ejecutar tests que coincidan con un patrón
pytest -k "load_data"

# Ejecutar solo tests rápidos (excluir lentos)
pytest -m "not slow"

# Ejecutar solo tests unitarios
pytest -m unit

# Modo verbose con output de prints
pytest -v -s
```

### Comandos de cobertura

```powershell
# Ejecutar tests con reporte de cobertura
pytest --cov=utils --cov=components --cov=views

# Reporte de cobertura en HTML (abre htmlcov/index.html)
pytest --cov=utils --cov-report=html
start htmlcov/index.html

# Reporte de cobertura en terminal con líneas faltantes
pytest --cov=utils --cov-report=term-missing

# Generar XML para CI/CD (Codecov, etc.)
pytest --cov=utils --cov-report=xml
```

### Comandos avanzados

```powershell
# Ejecutar tests en paralelo (más rápido)
pytest -n auto

# Parar en el primer fallo
pytest -x

# Mostrar tests más lentos
pytest --durations=10

# Modo watch (re-ejecuta al guardar archivos)
pytest-watch

# Debugger interactivo en fallos
pytest --pdb
```

---

## 📂 ESTRUCTURA DE TESTS

```
tests/
├── __init__.py                    # Marca directorio como paquete
├── conftest.py                    # Fixtures globales (★ MÁS IMPORTANTE)
├── test_data_manager.py           # Tests de utils/data_manager.py
├── test_helpers.py                # Tests de utils/helpers.py (TODO)
├── test_styles.py                 # Tests de components/styles.py (TODO)
├── test_views_landing.py          # Tests de views/landing.py (TODO)
└── test_views_dashboard.py       # Tests de views/dashboard.py (TODO)
```

---

## 🎓 CONCEPTOS CLAVE DE MOCKING

### ¿Qué es un Mock?

**Mock** = Objeto falso que simula el comportamiento de uno real

```python
# ❌ SIN MOCK (llama API real)
def test_sin_mock():
    df = load_data()  # ← Llama a Google Sheets (lento, requiere internet)

# ✅ CON MOCK (usa datos falsos)
def test_con_mock(mock_conectar_sheets):
    df = load_data()  # ← No llama a Google, usa fixture (rápido, offline)
```

### ¿Cómo funciona el mocking?

```
TU CÓDIGO REAL:
1. conectar_sheets() → Google Sheets API
2. get_all_records() → [{"id": "CTA-001", ...}, ...]
3. pd.DataFrame(...) → DataFrame real

CON MOCK (en tests):
1. conectar_sheets() → ❌ INTERCEPTADO → Devuelve mock object
2. get_all_records() → ❌ INTERCEPTADO → Devuelve datos de prueba
3. pd.DataFrame(...) → DataFrame con datos de prueba

TU CÓDIGO NO SABE QUE USA MOCKS. Es transparente.
```

### Fixtures importantes en conftest.py

| Fixture | Qué hace | Cuándo usarlo |
|---------|----------|---------------|
| `mock_streamlit_secrets` | Simula st.secrets | Cuando tu función lee secrets.toml |
| `mock_conectar_sheets` | Reemplaza conectar_sheets() | Para load_data(), guardar_datos() |
| `sample_cuentas_df` | DataFrame de prueba (cuentas) | Para verificar estructura de datos |
| `sample_metricas_df` | DataFrame de prueba (metricas) | Para verificar estructura de datos |
| `disable_streamlit_cache` | Desactiva @st.cache_* | Automático (autouse=True) |

---

## ✍️ ESCRIBIR TU PRIMER TEST

### Estructura básica (AAA Pattern)

```python
import pytest
from utils.data_manager import load_data

@pytest.mark.unit
def test_load_data_devuelve_dataframes(mock_conectar_sheets):
    """TEST: load_data() devuelve dos DataFrames"""
    
    # ARRANGE (preparar)
    # Ya hecho por fixture mock_conectar_sheets
    
    # ACT (ejecutar)
    df_cuentas, df_metricas = load_data()
    
    # ASSERT (verificar)
    assert df_cuentas is not None
    assert df_metricas is not None
    assert len(df_cuentas) > 0
    assert len(df_metricas) > 0
```

### Nomenclatura de tests

```python
# Formato: test_<función>_<escenario>_<resultado_esperado>

def test_load_data_conexion_exitosa_devuelve_dataframes():
    pass

def test_load_data_con_error_devuelve_dataframes_vacios():
    pass

def test_guardar_datos_engagement_invalido_devuelve_false():
    pass
```

### Markers (etiquetas)

```python
@pytest.mark.unit          # Test unitario (rápido, sin I/O)
@pytest.mark.integration   # Test de integración (lento, con API real)
@pytest.mark.slow          # Test lento (> 1 segundo)
@pytest.mark.skip          # Saltar este test
@pytest.mark.parametrize   # Test parametrizado (múltiples casos)
```

---

## 🐛 DEBUGGING DE TESTS

### Ver por qué falló un test

```powershell
# Modo verbose con traceback completo
pytest -v --tb=long

# Entrar en debugger interactivo en fallos
pytest --pdb

# Ver output de prints (incluso si test pasa)
pytest -s
```

### Ejecutar solo tests fallidos

```powershell
# Ejecutar solo los que fallaron la última vez
pytest --lf

# Ejecutar fallidos primero, luego el resto
pytest --ff
```

---

## 📊 INTERPRETAR REPORTE DE COBERTURA

### Reporte en terminal

```
---------- coverage: platform win32, python 3.13.1-final-0 -----------
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
utils/data_manager.py       517    120    77%   89-102, 234-256
utils/helpers.py            279    200    28%   12-45, 67-89
-------------------------------------------------------
TOTAL                       796    320    60%
```

**Interpretación:**
- **Stmts**: Líneas de código ejecutables
- **Miss**: Líneas NO ejecutadas por tests
- **Cover**: % de cobertura
- **Missing**: Números de línea sin cubrir

### Reporte HTML

```powershell
pytest --cov=utils --cov-report=html
start htmlcov/index.html
```

**Beneficios:**
- Visual (líneas verdes = cubiertas, rojas = no cubiertas)
- Click en archivo para ver detalles
- Identifica ramas if/else no probadas

---

## 🎯 ESTRATEGIA DE TESTING

### Fase 1: Unit Tests (Esta semana)
```
✓ tests/test_data_manager.py (HECHO)
☐ tests/test_helpers.py
☐ tests/test_styles.py

Target: 80% coverage en utils/
```

### Fase 2: Integration Tests (Próxima semana)
```
☐ tests/integration/test_sheets_real_api.py
☐ tests/integration/test_end_to_end_flow.py

Target: Flujo completo (load → process → save)
```

### Fase 3: E2E Tests (Siguiente mes)
```
☐ tests/e2e/test_streamlit_ui.py
☐ tests/e2e/test_navigation.py

Target: Probar UI de Streamlit
```

---

## 🚨 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'utils'"

```powershell
# Solución: Asegúrate de estar en la raíz del proyecto
cd "F:\MATRIZ DE REDES\social_media_matrix"
pytest
```

### Error: "fixture 'mock_conectar_sheets' not found"

```powershell
# Solución: conftest.py debe estar en tests/
# Verificar:
ls tests/conftest.py
```

### Tests muy lentos

```powershell
# Solución: Ejecutar en paralelo
pytest -n auto

# Ver tests más lentos
pytest --durations=10
```

### Mock no funciona

```python
# ❌ INCORRECTO: Importar antes de mockear
from utils.data_manager import conectar_sheets
def test_algo(mock_conectar_sheets):
    # conectar_sheets ya fue importada, mock no funciona

# ✅ CORRECTO: Importar dentro del test
def test_algo(mock_conectar_sheets):
    from utils.data_manager import load_data
    # Ahora load_data() usa el mock
```

---

## 📚 RECURSOS ADICIONALES

### Documentación oficial
- [Pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Tutoriales recomendados
- [Real Python - Pytest Guide](https://realpython.com/pytest-python-testing/)
- [Effective Python Testing With Pytest](https://realpython.com/python-testing/)

### Cheat Sheet
```python
# Assertions comunes
assert x == y                  # Igualdad
assert x != y                  # Desigualdad
assert x > y                   # Mayor que
assert x in y                  # Pertenencia
assert x is None               # Identidad
assert isinstance(x, list)     # Tipo

# Verificar excepciones
with pytest.raises(ValueError):
    funcion_que_falla()

# Verificar warnings
with pytest.warns(UserWarning):
    funcion_con_warning()

# Verificar llamadas a mocks
mock.assert_called()           # Llamado al menos 1 vez
mock.assert_called_once()      # Llamado exactamente 1 vez
mock.assert_called_with(x, y)  # Llamado con args específicos
mock.assert_not_called()       # Nunca llamado
```

---

## 🎉 SIGUIENTE PASO

```powershell
# 1. Instalar dependencias
pip install -r requirements-dev.txt

# 2. Ejecutar tests
pytest -v

# 3. Ver cobertura
pytest --cov=utils --cov-report=html
start htmlcov/index.html

# 4. Escribir más tests (objetivo: 80% coverage)
```

**¡Éxito! Ahora tienes testing profesional configurado.** 🚀
