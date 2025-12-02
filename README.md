# CHAMPILYTICS - Maristas Analytics Platform

![Version](https://img.shields.io/badge/version-12.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-red)

---

## 📑 Índice de Documentación

1. [Descripción General](#descripción)
2. [Características Principales](#características-principales)
3. [Métricas Monitoreadas](#métricas-monitoreadas)
4. [Instalación](#instalación)
5. [Uso](#uso)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Recorrido de Desarrollo](#recorrido-de-desarrollo)
8. [Documentos Clave](#documentos-clave)

---

## 📊 Descripción

CHAMPILYTICS es una plataforma de inteligencia digital diseñada para la Red Marista, que permite el análisis y seguimiento de métricas de redes sociales de instituciones educativas maristas en México.

### ✨ Características Principales

- 📈 **Dashboard Global**: Visualización consolidada de métricas de toda la red
- 🏫 **Análisis Individual**: Vista detallada por institución educativa
- ✏️ **Captura de Datos**: Sistema de ingreso de métricas tipo Excel
- ⚙️ **Configuración**: Simulador de datos y gestión de instituciones
- 🎨 **UI Minimalista**: Diseño profesional con glassmorphism y animaciones

### 🏁 Métricas Monitoreadas

- Seguidores totales por plataforma
- Alcance de publicaciones
- Interacciones (likes, comentarios, shares)
- Engagement rate
- Tendencias mensuales y comparativas

## 🚀 Instalación

### Prerrequisitos

- Python 3.13+
- pip

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/David2000-mp/Matriz-repositorio.git
cd Matriz-repositorio
```

2. Crear entorno virtual:
```bash
python -m venv venv
```

3. Activar entorno virtual:
- Windows:
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

Ejecutar la aplicación:
```bash
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

## 📁 Estructura del Proyecto

```
social_media_matrix/
├── app.py                      # Aplicación principal
├── requirements.txt            # Dependencias Python
├── .gitignore                 # Archivos ignorados por git
├── data/                      # Datos CSV
│   ├── cuentas.csv           # Catálogo de cuentas
│   └── metricas.csv          # Métricas históricas
├── images/                    # Recursos visuales
```

---

## 🗺️ Recorrido de Desarrollo

Para entender la evolución y el estado actual del proyecto, consulta los siguientes documentos:

- [Roadmap de Desarrollo](ROADMAP.md): Sprints, objetivos y tareas completadas/pending.
- [Guía de Refactorización](REFACTORING_GUIDE.md): Migración a arquitectura modular y estado de cada módulo.
- [Resumen de Logging](LOGGING_IMPLEMENTATION_SUMMARY.md): Implementación y configuración del sistema de logs.
- [Guía de Build y Release](BUILD_RELEASE.md): Proceso de despliegue, testing y rollback.
- [Reporte QA](QA_REPORT.md): Estado de la cobertura de tests y calidad del código.

---

## 📚 Documentos Clave

- [ROADMAP.md](ROADMAP.md)
- [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)
- [LOGGING_IMPLEMENTATION_SUMMARY.md](LOGGING_IMPLEMENTATION_SUMMARY.md)
- [BUILD_RELEASE.md](BUILD_RELEASE.md)
- [QA_REPORT.md](QA_REPORT.md)
│   ├── banner_landing.jpg
│   └── icon_maristas.png
└── README.md                  # Este archivo
```

## 🏫 Instituciones Incluidas

- Centro Universitario México
- Colegio México Bachillerato
- Instituto México Secundaria/Primaria
- Instituto México Toluca
- Instituto Hidalguense
- Colegio México Orizaba
- Instituto Potosino
- Instituto Queretano San Javier
- Y más...

## 🛠️ Tecnologías

- **Streamlit** 1.51.0 - Framework web
- **Pandas** 2.3.3 - Manipulación de datos
- **Plotly** 6.5.0 - Visualizaciones interactivas
- **Python** 3.13 - Lenguaje base

## 📊 Funcionalidades Detalladas

### Dashboard Global
- KPIs consolidados de toda la red
- Gráficos de distribución por plataforma (Facebook, Instagram, TikTok)
- Tendencias de crecimiento temporal
- Ranking institucional con barras horizontales
- Filtros por mes con cálculo de variación MoM

### Análisis Individual
- Selector de institución
- Gráficos de evolución de seguidores
- Métricas de engagement por plataforma
- Tabla de datos históricos exportable

### Captura de Datos
- Editor interactivo estilo Excel
- Validación de datos
- Cálculo automático de engagement rate
- Sistema de guardado batch

### Configuración
- Simulador de datos demo (1-12 meses)
- Gestión de catálogo de instituciones
- Reset de base de datos

## 🎨 Diseño UI/UX

- **Paleta de Colores**: Azul Marista (#003696), fondos claros
- **Tipografía**: Montserrat (300-900 weights)
- **Efectos**: Glassmorphism, animaciones fadeIn, hover states
- **Responsive**: Adaptable a móvil y escritorio

## 📝 Versión

**v12.0 - UX Enhanced**
- Hero banner con glassmorphism
- Tabs con contraste corregido
- Responsive design mejorado
- Animaciones suaves

### Actualización 2025-12-02
- **Corrección de UI**: Se ajustaron los colores del menú desplegable para mejorar la visibilidad.
- **Gestión de Instituciones**: Ahora es posible agregar nuevas instituciones y redes sociales, con sincronización automática en Google Sheets.
- **Sincronización en Tiempo Real**: Las gráficas se actualizan automáticamente al agregar nuevas cuentas.

## 👨‍💻 Autor

**David Hernández**
- GitHub: [@David2000-mp](https://github.com/David2000-mp)

## 📄 Licencia

Este proyecto es de uso interno para la Red Marista.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o soporte, contactar al equipo de desarrollo de la Red Marista.

---

**CHAMPILYTICS** - Inteligencia Digital Marista 🎓
