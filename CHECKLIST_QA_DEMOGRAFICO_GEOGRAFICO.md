# Checklist de QA: Modulo Demografico y Geografico (Chammpileaks)

Este documento define el proceso estandarizado de aseguramiento de calidad (QA) para la pestana de Analisis Demografico y Geografico. Debe ejecutarse localmente o en el entorno de staging antes de cualquier despliegue a produccion.

## Ejecucion automatizada (pre-release)
- Script Python: `python scripts/run_pre_release_qa_demogeo.py`
- Script PowerShell: `./scripts/run_pre_release_qa_demogeo.ps1`
- Incluir validacion de Google Sheets real: `./scripts/run_pre_release_qa_demogeo.ps1 -WithSheets`

## 1. Preparacion del Entorno
- [ ] Verificar que el entorno virtual esta activo (`.venv`).
- [ ] Confirmar la instalacion de dependencias criticas en `requirements.txt`:
  - [ ] `streamlit`
  - [ ] `pandas`
  - [ ] `plotly`
  - [ ] `openpyxl >= 3.1.5` (requerido para exportacion a Excel).

## 2. Pruebas de Humo (Smoke Tests)
- [ ] Ejecutar la aplicacion con `streamlit run app_refactored.py`.
- [ ] Navegar al menu lateral y hacer clic en **Analisis Demografico y Geografico**.
- [ ] Confirmar que la vista carga sin arrojar errores de compilacion (`Traceback`) o de importacion de modulos en pantalla o consola.

## 3. Validacion de Filtros Cruzados y Cache
- [ ] Seleccionar un `Colegio` diferente al inicial. Comprobar que los KPIs principales (Registros filtrados, Valor total) se actualizan en menos de 3 segundos (validacion de `st.cache_data`).
- [ ] Cambiar la `Plataforma` (ej. de Facebook a Instagram). Confirmar que los datos de las graficas cambian.
- [ ] Ajustar el `Rango de Fechas` seleccionando un periodo corto (ej. una sola semana). Comprobar que el volumen de datos disminuye en el reporte numerico.

## 4. Front-End y Experiencia de Usuario (UX)
- [ ] **Manejo de Estados Vacios (Empty States):** Filtrar por una combinacion de fechas o plataforma que no tenga datos. Verificar que la aplicacion muestra un mensaje amigable (ej. `st.info("No hay datos para esta seleccion")`) en lugar de romperse o mostrar graficas vacias rotas.
- [ ] **Indicadores de Carga:** Al aplicar un filtro que requiera procesamiento pesado, validar que exista un feedback visual (como el spinner nativo de Streamlit) indicando al usuario que la app esta pensando y no congelada.
- [ ] **Responsividad de Graficas:** Cambiar el tamano de la ventana del navegador. Confirmar que los contenedores (`st.columns`) se colapsan correctamente y que las graficas de Plotly se redimensionan sin cortar los ejes X/Y.
- [ ] **Legibilidad (Tooltips y Etiquetas):** Pasar el cursor sobre la grafica de Edad vs Sexo y sobre el mapa. Confirmar que los tooltips muestran numeros formateados correctamente (sin excesos de decimales) y textos claros.

## 5. Verificacion de Geolocalizacion y Reportes Tabulares
- [ ] **Mapa de Calor (Mexico):** Confirmar que el mapa renderiza los puntos sobre las ciudades geograficas esperadas. Los tamanos y/o colores deben diferenciar visualmente los volumenes mayores de los menores.
- [ ] **Control de Ciudades No Mapeadas:** Revisar la parte inferior de la tabla de reporte numerico y la consola. Si aparecen ciudades relevantes con la etiqueta No mapeada, levantar un ticket para anadirlas al diccionario estatico de `utils/demographics_geo.py`.
- [ ] **Exportacion Funcional:**
  - [ ] Hacer clic en el boton de descarga **CSV**. Verificar que el archivo descargado tiene datos y columnas correctas.
  - [ ] Hacer clic en el boton de descarga **Excel**. Abrir el archivo generado y verificar su integridad.

## 6. Auditoria de la Regla de Negocio (Critica)
Esta prueba garantiza que el colegio analizado no se autocompare.
- [ ] En el **Bloque 3 (Comparacion de Red)**, seleccionar una metrica demografica especifica (ej. porcentaje de Mujeres de 18-24).
- [ ] Observar la barra/metrica del Promedio General de la Red.
- [ ] Cambiar radicalmente los datos del colegio actualmente seleccionado (o subir un CSV de prueba inyectando un pico anormal solo a esa cuenta).
- [ ] **Resultado Esperado:** El Promedio General de la Red no debe inmutarse ni alterarse ante los picos de la cuenta seleccionada, demostrando que la exclusion del filtro (`network_total_excluding_selected`) funciona a nivel motor.

## 7. Evidencia de Ejecucion QA (Plantilla Rapida)
- Fecha de ejecucion:
- Entorno: Local / Staging
- Version/commit probado:
- Responsable QA:
- Resultado global: Aprobado / Rechazado
- Hallazgos:
  - Severidad alta:
  - Severidad media:
  - Severidad baja:
- Tickets creados:
- Recomendacion de despliegue: Si / No
