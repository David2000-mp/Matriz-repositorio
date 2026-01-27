# Contributing to CHAMPILEAKS

¡Gracias por tu interés en contribuir a CHAMPILEAKS! Este documento proporciona guías y pautas para contribuir al proyecto.

## Código de Conducta

Todos los colaboradores deben respetar nuestro compromiso con un ambiente de trabajo respetuoso y profesional.

### Nuestros estándares:
- Trato respetuoso a todos los colaboradores
- Aceptación constructiva de crítica
- Enfoque en lo que es mejor para la comunidad
- Demostración de empatía hacia otros miembros

## ¿Cómo Contribuir?

### 1. Reportar Bugs

Antes de crear un reporte de bug, verifica que no exista ya. Cuando crees un reporte, incluye:

- **Título descriptivo**: Resumen claro del problema
- **Descripción detallada**: Qué pasó, qué esperabas
- **Pasos para reproducir**: Lista específica de pasos
- **Ejemplos específicos**: Proporciona ejemplos específicos para demostrar
- **Screenshots**: Si es relevante, captura de pantalla
- **Versión de Python**: Qué versión estás usando
- **OS y versión**: Windows, Mac, Linux, etc.

### 2. Sugerir Mejoras

Las sugerencias de mejora son siempre bienvenidas. Para sugerir mejoras:

- Usa un **título descriptivo**
- Proporciona una **descripción clara** de la mejora
- Explica **por qué** sería útil
- Lista algunos **ejemplos** de cómo usaría el usuario

### 3. Pull Requests

**Proceso:**

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

**Pautas para PRs:**

- Sigue los estilos de código existentes
- Incluye tests apropiados
- Actualiza la documentación si es necesario
- Mantén el historial de commits limpio
- Escribe mensajes de commit claros y descriptivos

## Guía de Estilo

### Python

```python
# Usa Black para formatear código
black .

# Usa Ruff para linting
ruff check .

# Usa MyPy para type checking
mypy utils/ views/ components/
```

### Commits

```
# Bueno
git commit -m "Add ID agnosticism validation"
git commit -m "Fix Google Sheets sync issue"

# Malo
git commit -m "fix stuff"
git commit -m "asdf"
```

### Ramas

```
# Features
git checkout -b feature/nueva-funcionalidad

# Bugs
git checkout -b bugfix/problema-especifico

# Hotfixes
git checkout -b hotfix/problema-critico
```

## Proceso de Review

1. **Automático**: GitHub Actions ejecutará tests
2. **Manual**: Al menos 1 revisor debe aprobar
3. **Changes**: Realiza cambios según feedback
4. **Merge**: Una vez aprobado, se mergea a develop/main

## Requisitos de Código

- ✅ Cobertura mínima: 75%
- ✅ Sin errores de linting (ruff, black)
- ✅ Pasar todos los tests: `pytest`
- ✅ Type hints correctos
- ✅ Documentación actualizada

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=utils --cov=views --cov=components

# Tests específicos
pytest tests/test_services.py::TestIDAgnosticism
```

## Documentación

- Actualiza README.md si cambias funcionalidad principal
- Agrega docstrings a nuevas funciones
- Comenta lógica compleja
- Actualiza CHANGELOG.md

## Estructura de Carpetas

```
social_media_matrix/
├── app.py              # Punto de entrada
├── utils/              # Lógica de negocio
├── views/              # Páginas/vistas
├── components/         # Componentes UI
├── data/               # Datos CSV
├── tests/              # Tests automáticos
└── .github/            # Configuración GitHub
```

## Stack Tecnológico

- **Framework**: Streamlit 1.28+
- **Data**: Pandas 2.0+, NumPy 1.24+
- **Testing**: Pytest 8.3+
- **Linting**: Ruff, Black, MyPy
- **Cloud**: Google Sheets API

## Preguntas?

- Abre un Issue para preguntas
- Revisa la documentación en `/docs`
- Contacta a los maintainers

---

**Gracias por contribuir a CHAMPILEAKS!** 🚀
