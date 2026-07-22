# Reporte técnico: Demografía y geografía / Inteligencia cruzada

Fecha de revisión: 22 de julio de 2026  
Alcance: análisis de arquitectura, flujo de datos, reglas de cálculo, interfaz, extensibilidad, pruebas y fallos detectados.

## 1. Resumen ejecutivo

Las dos pestañas están activas en la navegación principal de Streamlit y consultan dos hojas de Google Sheets:

- `Base_Maestra_Colegios`: rendimiento por fecha, colegio, plataforma y métrica.
- `Base_Demografica_Colegios`: audiencia por fecha de reporte, colegio, plataforma, criterio, sexo, edad, ubicación y valor.

La pestaña **Demografía y geografía** analiza estructura de audiencia, ciudades y comparación contra la red. La pestaña **Inteligencia cruzada** combina rendimiento con audiencia, agrega tendencias históricas, rankings, estimaciones por ciudad y comparaciones contra la red.

La separación entre interfaz y funciones analíticas es una buena base para agregar funciones. Sin embargo, antes de ampliar el sistema conviene corregir cuatro problemas centrales:

1. La etiqueta “promedio de la red” no corresponde al cálculo demográfico implementado: se calcula la distribución de toda la audiencia agregada, no el promedio de los porcentajes de cada colegio.
2. “Correlación Rendimiento-Audiencia” no calcula ninguna correlación; únicamente superpone series en dos ejes.
3. La pestaña demográfica y la de inteligencia cruzada tienen cargadores y normalizaciones duplicados, con manejo de errores diferente.
4. El contrato de negocio de `valor` no está documentado. Sin saber si representa personas, alcance estimado, porcentaje o una fotografía acumulable, algunos totales e históricos pueden ser engañosos.

También se reprodujeron fallos concretos en edades no previstas, fecha final con horas, geocodificación ambigua y pruebas automatizadas.

## 2. Archivos y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `app_refactored.py` | Registra las rutas `demografia` e `inteligencia-cruzada` y ejecuta las vistas. |
| `views/demographic_geographic_analysis.py` | Interfaz completa de Demografía y geografía; además carga directamente Google Sheets. |
| `utils/demographics_geo.py` | Filtros y cálculos puros de demografía, ciudades y comparación de red. Contiene catálogos de coordenadas. |
| `views/cross_intelligence_view.py` | Interfaz completa de Inteligencia cruzada. |
| `utils/cross_intelligence.py` | Carga normalizada, filtros, KPIs, series, rankings y comparaciones de Inteligencia cruzada. |
| `utils/data_loader.py` | Cargador compartido usado por Inteligencia cruzada. |
| `utils/schema_columns.py` | Contratos mínimos de columnas de las dos hojas. |
| `utils/sheets_validator.py` | Comprueba existencia de hojas y encabezados. |
| `tests/test_demographics_geo.py` | Tres pruebas unitarias del módulo demográfico. |
| `scripts/run_pre_release_qa_demogeo.py` | Verificación previa a liberación del módulo demográfico. |

### Flujo actual

```text
app_refactored.py
├─ Demografía y geografía
│  └─ view carga Google Sheets directamente
│     ├─ normalización local
│     └─ utils/demographics_geo.py
│        ├─ filtros
│        ├─ distribución edad/sexo
│        ├─ ciudades/coordenadas
│        └─ comparación contra red
└─ Inteligencia cruzada
   └─ utils/cross_intelligence.py
      └─ utils/data_loader.py
         └─ Google Sheets
      ├─ normalización adicional
      ├─ filtros por mes
      ├─ KPIs y series
      ├─ estimaciones y rankings
      └─ comparaciones contra red
```

Consecuencia: las dos páginas pueden interpretar de forma distinta una variación de encabezado o un error de conexión, aunque consulten la misma fuente.

## 3. Contrato de datos actual

### 3.1 Base maestra

Columnas obligatorias:

| Columna | Uso |
|---|---|
| `fecha` | Corte temporal del rendimiento. |
| `colegio` | Identidad del colegio/cuenta. |
| `plataforma` | Red social. |
| `metrica` | Nombre de la métrica. |
| `valor` | Valor numérico de la métrica. |

Inteligencia cruzada sólo reconoce como rendimiento:

- Interacciones: `interaccion`, `interacciones`.
- Visualizaciones: `visualizacion`, `visualizaciones`, `views`, `vistas`.

Otras métricas como alcance, impresiones o reproducciones se ignoran, aunque estén presentes en la hoja.

### 3.2 Base demográfica

Columnas obligatorias:

| Columna | Uso |
|---|---|
| `fecha_reporte` | Fecha del corte demográfico. |
| `colegio` | Colegio/cuenta. |
| `plataforma` | Red social. |
| `criterio` | Dimensión analítica. Actualmente se esperan `Demografia base` o `Ciudad`. |
| `sexo` | Categoría de sexo para demografía base. |
| `edad` | Rango de edad para demografía base. |
| `ubicacion` | Ciudad para el criterio Ciudad. |
| `valor` | Cantidad usada en agregaciones y participaciones. |

El código no define:

- unidad de `valor`;
- si cada fecha es una fotografía o un incremento;
- clave única de una fila;
- si se permiten negativos;
- si debe sumar 100 por reporte cuando representa porcentaje;
- si los criterios representan universos independientes de la misma audiencia.

Este contrato debe definirse antes de agregar cálculos históricos. Por ejemplo, sumar fotografías mensuales de audiencia no equivale necesariamente a audiencia acumulada.

## 4. Pestaña Demografía y geografía

### 4.1 Carga y normalización

La vista ejecuta dos cargadores locales con caché de cinco minutos:

- `_load_sheet_base_maestra()`;
- `_load_sheet_base_demografica()`.

Ambos llaman a `get_sheets_connection()`, leen todos los registros, convierten encabezados a minúsculas, completan columnas faltantes con texto vacío, convierten fechas y convierten `valor` a número. Un valor inválido se sustituye silenciosamente por cero.

La base maestra sólo se usa para ampliar el catálogo de colegios del filtro; todos los cálculos de esta pestaña salen de la base demográfica.

Si ocurre cualquier excepción al localizar o leer una hoja, el cargador devuelve un DataFrame vacío sin registrar la causa. La interfaz no puede distinguir entre una hoja realmente vacía, credenciales inválidas, pérdida de conexión, cambio de nombre o error de API.

### 4.2 Filtros

El lateral agrega:

1. Colegio: unión de colegios encontrados en ambas bases; no existe opción “Todos”.
2. Plataforma: `Todas` más las plataformas presentes para el colegio elegido en la base demográfica.
3. Rango de fechas: mínimo y máximo global de `fecha_reporte`.

Los filtros comparan colegio y plataforma con igualdad exacta. Sólo se eliminan espacios laterales; no se unifican mayúsculas, acentos ni alias. `Instagram`, `instagram` e `Instagram ` pueden terminar como categorías diferentes, salvo el espacio final que sí se elimina en algunos cargadores.

La pestaña crea además un alcance de red con todos los colegios, conservando plataforma y fechas. Esto permite que la comparación excluya al colegio seleccionado.

Los filtros globales que aparecen arriba en el mismo sidebar de la aplicación (`filtro_entidad` y `filtro_mes`) no controlan esta pestaña. El usuario ve dos juegos de filtros independientes.

### 4.3 Indicadores superiores

- **Registros filtrados**: número de filas, no personas, publicaciones ni colegios.
- **Valor total**: suma de `valor` de todos los criterios del colegio y periodo.

El segundo indicador puede contar el mismo universo más de una vez. Si una audiencia está descrita por edad/sexo y también por ciudad, sumar ambos criterios no produce un total de audiencia válido. Debe separarse por criterio o eliminarse hasta definir la unidad.

### 4.4 Estructura de audiencia

`build_demography_base()`:

1. Normaliza `criterio` y conserva `demografia base`.
2. Elimina filas sin sexo o edad.
3. Suma `valor` por edad y sexo.
4. Calcula participación: `valor_segmento / suma_total * 100`.
5. Ordena la edad con el catálogo fijo `13-17`, `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65+`.

La vista presenta barras agrupadas por sexo; el eje vertical es valor y el tooltip incorpora participación.

### 4.5 Mapa y reporte de ciudades

La pestaña permite:

- mapa general de la red;
- mapa de un colegio;
- ranking tabular;
- descarga CSV con BOM UTF-8;
- descarga XLSX con `openpyxl`.

`build_city_report()` filtra `criterio == ciudad`, suma por texto exacto de ubicación, calcula participación y busca latitud/longitud en dos diccionarios estáticos. Lo no encontrado se separa como “no mapeado”. La vista vuelve a aplicar un segundo diccionario de recuperación, parcialmente duplicado.

El mapa usa `scatter_mapbox`, tamaño y color basados en `valor_total`, centro fijo en México y zoom 4.4. Aunque el título dice México, el catálogo también contiene Maracaibo y Monasterio de Yuste.

### 4.6 Comparación con red

`build_network_comparison()`:

1. Conserva sólo demografía base.
2. Divide el conjunto entre colegio seleccionado y todos los demás.
3. Suma cada segmento edad/sexo en el colegio.
4. Suma cada segmento en toda la red restante.
5. Normaliza ambos lados a 100%.
6. Calcula `delta_pp = colegio_pct - red_pct`.

La exclusión del colegio seleccionado sí está implementada. Sin embargo, el resultado de red es una distribución agregada ponderada por volumen, no un promedio aritmético de colegios.

Ejemplo reproducido:

- Colegio B: 1000 hombres, 0 mujeres.
- Colegio C: 0 hombres, 10 mujeres.
- Distribución agregada actual: 99.01% hombres, 0.99% mujeres.
- Promedio igualitario de los dos colegios: 50% hombres, 50% mujeres.

Ambas medidas pueden ser válidas, pero responden preguntas distintas. La interfaz debe llamarla “perfil agregado de la red” o implementar primero porcentajes por colegio y después promediarlos.

## 5. Pestaña Inteligencia cruzada

### 5.1 Carga y filtros

Esta vista usa los cargadores compartidos de `utils/data_loader.py`, agrega normalización y descarta fechas inválidas. Todo se cachea durante cinco minutos.

Filtros:

- Colegio: `Todos` más la unión de ambas bases.
- Plataforma: `Todas` más la unión de ambas bases.
- Mes/año: `Histórico completo` y la unión de meses disponibles.

Colegio, plataforma y mes no son filtros encadenados. Es posible elegir una combinación inexistente. El catálogo de periodos siempre contiene el centinela histórico, por lo que la rama “No hay periodos disponibles” es prácticamente inalcanzable incluso con las dos bases vacías.

### 5.2 Bloque 1: rendimiento y audiencia

Presenta:

- interacciones del periodo;
- visualizaciones del periodo;
- diferencia absoluta y porcentual contra el mes calendario anterior;
- acumulado histórico;
- segmento edad/sexo dominante;
- ciudad dominante.

Fórmulas:

```text
total_métrica = suma(valor de aliases reconocidos)
delta_absoluto = actual - anterior
delta_porcentual = (actual - anterior) / anterior × 100
participación_dominante = valor_segmento_mayor / total_segmentos × 100
```

Si el mes calendario anterior no tiene datos, se muestra “Sin base previa”; no busca el último mes disponible. En modo histórico, el valor actual y el acumulado histórico son el mismo total, por lo que se repite información y no existe comparación previa.

El título “Correlación Rendimiento-Audiencia” es incorrecto: no se calcula Pearson, Spearman, regresión, significancia, tamaño de muestra ni desfase temporal.

### 5.3 Bloque 2: histórico y microscopio del mes

Construye:

- suma mensual de visualizaciones;
- suma mensual de interacciones;
- porcentaje mensual de los dos segmentos demográficos con mayor volumen en todo el periodo;
- sombreado del mes elegido.

Las métricas de volumen comparten el eje izquierdo y las participaciones usan un eje derecho fijo de 0 a 100. Iniciar ambos ejes en cero reduce distorsión, pero una superposición visual no demuestra relación estadística.

### 5.4 Bloque 3: desglose multidimensional

#### Ciudad

No existen métricas de contenido observadas por ciudad. El sistema estima:

```text
participación_ciudad = audiencia_ciudad / audiencia_total_ciudades
interacciones_estimadas = participación_ciudad × interacciones_totales
visualizaciones_estimadas = participación_ciudad × visualizaciones_totales
```

Esto supone que rendimiento y audiencia se distribuyen exactamente en la misma proporción geográfica. La vista usa la palabra “estimado”, lo cual ayuda, pero falta explicar el supuesto y evitar que se interprete como medición real.

#### Colegio

Suma interacciones y visualizaciones por colegio y define:

```text
volumen_total = interacciones + visualizaciones
aporte_pct = volumen_total_colegio / volumen_total_red × 100
```

Sumar visualizaciones e interacciones combina unidades y etapas distintas del embudo. Como las visualizaciones suelen ser mucho mayores, dominan el ranking. Sería mejor seleccionar una métrica, normalizar ambas o construir un índice con ponderaciones documentadas.

#### Segmento

Suma `valor` por sexo/edad dentro de demografía base y muestra distribución porcentual.

### 5.5 Bloque 4: cuenta contra red

Sólo se habilita al seleccionar un colegio concreto.

- Rendimiento: total del colegio contra la media de los totales de los demás colegios.
- Demografía: distribución del colegio contra la distribución agregada de todos los demás colegios.

En rendimiento, el promedio de una métrica sólo incluye colegios que tienen al menos una fila de esa métrica. Un colegio sin registro no entra como cero. Se debe decidir si ausencia significa cero, dato faltante o métrica no aplicable.

La comparación demográfica repite el problema de “agregado ponderado” presentado como “promedio”.

## 6. Fallos y riesgos detectados

### Prioridad alta

| ID | Hallazgo | Evidencia/impacto | Recomendación |
|---|---|---|---|
| A-01 | “Promedio de red” demográfico no es promedio por colegio. | Caso reproducido: 99.01/0.99 actual frente a 50/50 por promedio igualitario. Afecta ambas pestañas. | Definir la regla de negocio; renombrar como agregado ponderado o calcular porcentajes por colegio y promediarlos. |
| A-02 | “Correlación” no calcula correlación. | Sólo se trazan series en dos ejes. Puede conducir a inferencias falsas. | Renombrar a “evolución conjunta” o implementar correlación real con `n`, método, desfase y advertencias. |
| A-03 | `Valor total` demográfico mezcla criterios. | Suma filas de demografía base y ciudad, potencialmente dos descripciones del mismo universo. | Mostrar totales separados por criterio/unidad. |
| A-04 | Contrato de `valor` y granularidad sin definir. | Las funciones suman fechas, plataformas y fotografías. Una suma histórica puede no tener significado. | Crear diccionario de datos y validación de grano/clave única antes de nuevas métricas. |
| A-05 | Edades nuevas se convierten en `nan`. | Reproducido con `18-20`; `pd.Categorical` elimina etiquetas fuera de `AGE_ORDER`. | Conservar categorías desconocidas, añadir “Otros” o construir orden dinámico validado. |
| A-06 | Geocodificación aproximada puede asignar una ciudad equivocada. | Reproducido: `Victoria` se asigna a Victoria de Durango mediante inclusión de texto. | Eliminar coincidencia ambigua; usar catálogo con ID, estado y coordenadas explícitas. |
| A-07 | Los errores de carga demográfica se silencian. | La vista captura cualquier excepción y devuelve vacío. Un corte de API parece “sin información”. | Registrar excepción, mostrar estado técnico resumido y distinguir vacío/error. |
| A-08 | Fixture global de pruebas escribe CSV reales. | `tests/conftest.py` sobrescribe `data/cuentas.csv` y `data/metricas.csv` antes de cada prueba y no los restaura. | Usar `tmp_path` y monkeypatch de rutas; nunca escribir fuentes reales desde un fixture autouse. |

### Prioridad media

| ID | Hallazgo | Impacto | Recomendación |
|---|---|---|---|
| M-01 | Fecha final se compara con medianoche. | Un registro `2026-01-31 15:00` queda fuera al elegir fin `2026-01-31`. Caso reproducido. | Comparar por fecha normalizada o usar fin exclusivo del día siguiente. |
| M-02 | Dos rutas de carga para las mismas hojas. | Duplicación, resultados y errores inconsistentes. | Crear un único repositorio/cargador compartido. |
| M-03 | Valores inválidos pasan a cero. | Oculta errores de captura y altera porcentajes. | Separar filas inválidas y mostrar contador de calidad. |
| M-04 | No se rechazan negativos. | Puede romper tamaños del mapa y generar porcentajes sin sentido. | Validar `valor >= 0` salvo métricas expresamente firmadas. |
| M-05 | Filtros de Inteligencia cruzada no encadenados. | Muchas combinaciones vacías evitables. | Recalcular plataforma y periodo según selección previa. |
| M-06 | Filtros globales no afectan estas páginas. | Dos contextos simultáneos en el sidebar confunden al usuario. | Integrarlos o esconder los globales en estas rutas. |
| M-07 | El rendimiento estimado por ciudad parece más preciso de lo que es. | Propaga una hipótesis, no observación. | Mostrar metodología, intervalo/advertencia y opción para ocultarlo. |
| M-08 | Ranking suma visualizaciones e interacciones. | Métrica compuesta dominada por la escala de visualizaciones. | Selector de métrica o índice normalizado documentado. |
| M-09 | Media de rendimiento omite colegios sin la métrica. | El denominador cambia entre métricas. | Contabilizar faltantes explícitamente y mostrar cobertura. |
| M-10 | Coordenadas duplicadas en utilidad y vista. | Riesgo de divergencia al agregar ciudades. | Un solo catálogo externo versionado. |
| M-11 | El procesamiento de comas y guiones en ciudades es código muerto. | La puntuación se elimina antes de intentar dividirla. | Parsear componentes antes de normalizar. |
| M-12 | Mapa titulado México contiene ubicaciones internacionales. | Puntos fuera del encuadre y semántica inconsistente. | Separar país/estado o ajustar encuadre automáticamente. |
| M-13 | Exportación XLSX se calcula en cada render. | Trabajo innecesario aun sin descargar. | Cachear bytes o generar bajo acción diferida. |
| M-14 | `scatter_mapbox` es una ruta técnica antigua en Plotly. | Futuras actualizaciones pueden exigir migración. | Planear migración a la API de mapas vigente de Plotly. |

### Prioridad baja / experiencia de usuario

| ID | Hallazgo | Recomendación |
|---|---|---|
| B-01 | En histórico, KPI actual y acumulado repiten el mismo valor. | Diseñar una tarjeta histórica específica. |
| B-02 | El mensaje “No hay periodos disponibles” casi no puede alcanzarse por el centinela histórico. | Comprobar meses reales antes de insertar el centinela. |
| B-03 | La comparación usa tablas con nombres técnicos (`red_pct`, `delta_pp`). | Aplicar configuración de columnas y explicación de puntos porcentuales en ambas vistas. |
| B-04 | No hay indicador explícito de frescura de los datos. | Mostrar última fecha, tiempo desde sincronización y cobertura. |
| B-05 | El checklist exige spinner, pero estas vistas no tienen uno explícito. | Añadir estado de carga a consultas y exportaciones largas. |

## 7. Estado de pruebas y verificaciones

### Pruebas existentes

`tests/test_demographics_geo.py` contiene seis pruebas, incluyendo las
regresiones de la Fase 1:

1. distribución demográfica suma 100%;
2. ciudad conocida/desconocida;
3. exclusión del colegio seleccionado;
4. fecha final inclusiva con horas;
5. edades desconocidas agrupadas como `Otros`;
6. coordenadas exactas y rechazo de negativos.

`tests/test_cross_intelligence_reliability.py` agrega dos pruebas de los
normalizadores de Inteligencia cruzada: rechazo de valores inválidos/negativos
y límites completos del mes. Todavía no existen pruebas de las vistas ni de
todos los cálculos de `utils/cross_intelligence.py`.

### Ejecución realizada

- Script pre-release demográfico: **5/6 checks exitosos**.
- Dependencias, archivos y lógica sintética: aprobados.
- Wiring de navegación: falló porque el script busca el router anterior con `elif`, mientras la aplicación ya usa `st.navigation` y registra correctamente las páginas.
- Google Sheets real: omitido porque el modo `--with-sheets` no se ejecutó.
- Pytest enfocado con `--noconftest`: **8/8 pruebas aprobadas**. La ejecución
  normal con el `conftest.py` completo se queda activa después de reportar
  `100%`, por lo que se validó el conjunto puro sin cargar fixtures globales.
- Inspección visual interactiva: no disponible porque no había una sesión de navegador conectable; el endpoint de salud local sí respondió.

Además, el script QA exige `openpyxl >= 3.1.5`, mientras `requirements.txt` permite `openpyxl >= 3.1.0`. Un entorno puede cumplir requisitos y fallar el gate.

### Cobertura que falta

- normalización de encabezados y valores de dimensión;
- errores de conexión/hoja ausente;
- fechas con hora y límites inclusivos;
- edades desconocidas;
- valores cero, negativos, nulos y texto inválido;
- promedio ponderado frente a promedio por colegio;
- colegios con métricas faltantes;
- alias de métricas;
- ciudades ambiguas y homónimas;
- todos los cálculos de Inteligencia cruzada;
- caché e invalidación;
- exportaciones CSV/XLSX;
- pruebas de vista con widgets y estados vacíos.

Los logs locales muestran además errores `UnicodeEncodeError` al escribir símbolos Unicode en la consola de Windows. No son exclusivos de estas páginas, pero degradan el diagnóstico de cualquier fallo del módulo.

## 8. Cómo agregar nuevas funciones con seguridad

### Paso 1: definir la pregunta y unidad

Antes de programar, documentar:

- pregunta de negocio;
- unidad de cada entrada y salida;
- grano mínimo de la fila;
- dimensiones permitidas;
- regla de faltantes y ceros;
- método de agregación temporal;
- método de comparación de red;
- mínimo de observaciones requerido.

### Paso 2: unificar acceso a datos

Crear un único servicio, por ejemplo `utils/demographic_repository.py`, que:

- cargue ambas hojas;
- normalice encabezados, colegio, plataforma, criterio, sexo, edad y ubicación;
- valide fechas y valores;
- entregue datos válidos y un reporte de errores;
- exponga una única política de caché;
- registre fallos de conexión sin ocultarlos.

Las dos vistas deberían consumir ese servicio y no llamar Google Sheets directamente.

### Paso 3: mantener cálculos puros

Agregar la lógica en `utils/`, con funciones que reciban DataFrames y devuelvan DataFrames o estructuras tipadas. La vista sólo debería seleccionar filtros, llamar funciones y renderizar resultados.

Ejemplos:

- nuevo criterio demográfico: función `build_<criterio>()` y nueva subpestaña;
- nueva métrica de rendimiento: catálogo central de aliases y selector de métrica;
- nueva comparación: función pura que reciba explícitamente `aggregation="equal_school"` o `aggregation="audience_weighted"`;
- nuevo mapa: fuente geográfica separada con `city_id`, municipio, estado, país, latitud y longitud.

### Paso 4: evitar hardcodear dimensiones

Mover a catálogos configurables:

- métricas y aliases;
- criterios demográficos;
- orden y etiquetas de edad;
- sexos/categorías;
- ubicaciones y coordenadas;
- pesos de índices compuestos.

Si se agregan columnas, actualizar de forma coordinada:

1. `utils/schema_columns.py`;
2. cargador compartido;
3. `utils/sheets_validator.py`;
4. generadores/importadores;
5. pruebas y documentación.

### Paso 5: escribir pruebas antes de conectar la UI

Cada función nueva debe cubrir:

- caso nominal;
- DataFrame vacío;
- columna/dimensión inválida;
- fechas límite;
- nulos y negativos;
- varias plataformas/colegios;
- definición matemática esperada;
- invariantes: porcentajes suman 100, el colegio no entra en su red y los denominadores son explícitos.

Los fixtures deben vivir en memoria o en `tmp_path`, nunca en `data/`.

### Paso 6: observabilidad y UX

Cada bloque debería mostrar:

- fuente y fecha de actualización;
- filtros activos;
- número de colegios/periodos/filas válidas;
- porcentaje de datos descartados;
- metodología y unidad;
- estado vacío distinto de estado de error;
- descarga de los datos exactos que originaron la gráfica.

## 9. Funciones nuevas sugeridas

### P0: necesarias antes de ampliar análisis

1. **Panel de calidad de datos**: fechas inválidas, valores no numéricos/negativos, duplicados, categorías nuevas, ciudades no mapeadas y cobertura por colegio/plataforma.
2. **Selector de método de red**: agregado ponderado por audiencia frente a promedio igualitario por colegio, con definición visible.
3. **Catálogo geográfico administrable**: hoja o archivo con IDs, municipio, estado, país y coordenadas; revisión manual de coincidencias.
4. **Metodología visible**: glosario de `valor`, criterios, fórmulas y última actualización.

### P1: alto valor analítico

1. **Correlación real**: Pearson/Spearman entre rendimiento mensual y participación demográfica, tamaño de muestra, significancia orientativa y análisis con desfases de 0–3 meses.
2. **Selector de métrica**: interacciones, visualizaciones, alcance, impresiones o reproducciones, sin sumarlas automáticamente.
3. **Índices normalizados**: índice 0–100 por percentil o z-score para comparar colegios con escalas distintas.
4. **Evolución de cohortes**: cambios mensuales por edad/sexo y alertas de variaciones inusuales.
5. **Cobertura de red**: cuántos colegios aportan datos a cada barra, KPI y mes.
6. **Drill-through**: clic en segmento, ciudad o colegio para ver registros fuente y metodología.

### P2: experiencia y operación

1. **Exportación integral** de cada bloque a CSV/XLSX y reporte consolidado.
2. **Vistas guardadas** de filtros frecuentes.
3. **Comparación multiselección** de varios colegios y plataformas.
4. **Alertas de frescura** por colegio cuando un reporte no se actualiza a tiempo.
5. **Mapa con encuadre automático** y filtros de país/estado/municipio.

## 10. Roadmap recomendado

### Fase 1: confiabilidad

- Definir contrato de datos y cálculo de red.
- Corregir edades, fechas y geocodificación ambigua.
- Separar errores de carga de estados vacíos.
- Aislar fixtures de pruebas y actualizar el script QA.

### Fase 2: arquitectura

- Unificar los cargadores.
- Centralizar catálogos.
- Eliminar duplicación de coordenadas.
- Integrar o simplificar filtros globales/locales.
- Añadir reporte de calidad y cobertura.

### Fase 3: análisis nuevo

- Implementar selector de métricas.
- Implementar comparación ponderada/igualitaria.
- Sustituir “correlación” visual por estadística verificable.
- Añadir cohortes, anomalías, drill-through y exportación.

## 11. Criterios de aceptación para la siguiente versión

- Una única ruta de carga alimenta ambas pestañas.
- Los errores de Google Sheets no aparecen como “sin datos”.
- La unidad y granularidad de `valor` están documentadas.
- El usuario puede saber si la red es ponderada o igualitaria.
- Categorías nuevas nunca se convierten en `nan` silenciosamente.
- El rango final incluye todo el día seleccionado.
- Ninguna ciudad se asigna por coincidencia ambigua sin estado/ID.
- Cada métrica muestra cobertura y periodo.
- No se suman unidades diferentes sin un índice documentado.
- Inteligencia cruzada tiene pruebas unitarias propias.
- Las pruebas no escriben ni modifican datos reales.
- El pre-release valida el router actual y pasa en un entorno limpio.

## 12. Conclusión

El módulo ya tiene componentes útiles y una separación razonable entre cálculo y presentación, especialmente en `utils/cross_intelligence.py` y `utils/demographics_geo.py`. Es posible agregar funciones sin rehacer toda la aplicación. La prioridad, sin embargo, debe ser fijar las definiciones matemáticas y el contrato de datos: hoy varias visualizaciones son técnicamente correctas respecto a su código, pero su etiqueta permite una interpretación distinta de lo calculado.

La extensión más segura consiste en unificar la carga, exponer calidad/cobertura, hacer configurables las dimensiones y asegurar cada nueva regla con funciones puras y pruebas aisladas. Después de esa base, la correlación real, cohortes, anomalías y comparaciones configurables aportarían valor sin aumentar la deuda actual.
