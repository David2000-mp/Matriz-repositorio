# Inventario de llaves y cruces — entrada para Fase 5

Estado: documento de diseño. No implementa el laboratorio de cruces.

## 1. Fuentes analíticas actuales

| Fuente | Grano observado | Columnas de enlace actuales | Identificador estable |
|---|---|---|---|
| `Base_Maestra_Colegios` | Métrica por fecha, colegio y plataforma | `fecha`, `colegio`, `plataforma`, `metrica` | No en esta base |
| `Base_Demografica_Colegios` | Valor demográfico por fecha de reporte, colegio, plataforma y criterio | `fecha_reporte`, `colegio`, `plataforma`, `criterio`, `sexo`, `edad`, `ubicacion` | No |
| Cuentas/engagement | Captura por cuenta y fecha | `id_cuenta`, `fecha`, `plataforma` | Sí: `id_cuenta` |
| Texto procesado | Comentario o bloque de comentarios procesado | Texto, sentimiento, categoría y tema | No existe `comentario_id` contractual |
| Contenido | Atributos de publicación almacenados en columnas operativas | Colegio/cuenta, fecha, plataforma y campos de contenido | No existe `publicacion_id` contractual |
| Audiencia y riesgo | Agregado por entidad/cuenta y periodo | `id_cuenta` cuando está disponible; si no, entidad/plataforma | Parcial |

Conclusión: hoy las bases nuevas se pueden unir de forma segura sólo en grano agregado por colegio, plataforma y periodo. El nombre de colegio sigue siendo una llave natural frágil.

## 2. Llaves objetivo

| Llave | Propósito | Regla propuesta |
|---|---|---|
| `colegio_id` | Identidad institucional única | Inmutable; catálogo central con alias de nombres |
| `cuenta_id` | Cuenta social específica | Reutilizar/migrar `id_cuenta`; FK a colegio y plataforma |
| `publicacion_id` | Publicación individual | ID de plataforma cuando exista; UUID estable como respaldo |
| `comentario_id` | Comentario individual | ID nativo o hash estable de publicación, autor anonimizado y fecha |
| `captura_id` | Snapshot de métricas | UUID; único por cuenta/publicación, métrica y fecha de captura |
| `segmento_id` | Sexo × edad y futuras dimensiones | Catálogo, no texto libre |
| `alerta_id` | Evento de riesgo | UUID con ventana temporal y entidades relacionadas |
| `fecha_id` | Calendario común | Fecha ISO; derivar mes, trimestre y año |

## 3. Clasificación de cruces

### Directos con la información actual

| Cruce | Grano seguro | Observación |
|---|---|---|
| Rendimiento × colegio × plataforma × tiempo | Colegio–plataforma–periodo | Interacciones y visualizaciones permanecen separadas |
| Demografía × sexo × edad | Colegio–plataforma–fecha de reporte | Distribución observada en la fuente demográfica |
| Ciudades × plataforma | Colegio–plataforma–fecha de reporte | Usa filas explícitas con criterio Ciudad |
| Engagement × riesgo institucional | `id_cuenta`–periodo | Recalcular engagement desde numerador/denominador cuando sea posible |
| Texto × sentimiento × categoría | Registro textual procesado | Directo dentro del mismo registro, no todavía por publicación |

### Estimados y obligatoriamente etiquetados

| Cruce | Método actual | Riesgo de interpretación |
|---|---|---|
| Ciudad × interacciones/visualizaciones | Distribuir el rendimiento de cada colegio/plataforma según su participación por ciudad | No representa geolocalización real de usuarios |
| Ciudad × género | Distribuir el volumen del género dentro del mismo colegio/plataforma según pesos de ciudad | No prueba género individual por ciudad |
| Segmento demográfico × rendimiento | Rendimiento observado × participación del segmento en el mismo corte | Asociación ecológica, no atribución individual |
| Demografía × tendencia de contenido | Alineación por colegio, plataforma y mes | Puede ocultar cambios dentro del mes |

### Bloqueados hasta incorporar nuevas llaves

| Cruce solicitado | Llave faltante principal |
|---|---|
| Comentario × publicación | `comentario_id`, `publicacion_id` |
| Sentimiento × tipo de contenido por publicación | `publicacion_id` |
| Riesgo × publicación detonante | `alerta_id`, `publicacion_id` |
| Género/edad × comentario individual | Identificador de audiencia compatible; no debe inferirse de datos agregados |
| Ciudad × interacción individual | Geografía o evento individual con consentimiento/anonimización |
| Cohorte real de usuarios | Identificador anónimo longitudinal; hoy sólo existen cohortes agregadas |

## 4. Reglas de unión y agregación

1. Prohibir uniones por nombre de colegio sin pasar por el catálogo de alias a `colegio_id`.
2. Declarar y validar la cardinalidad de cada `merge` (`one_to_one`, `one_to_many` o `many_to_one`).
3. Rechazar `many_to_many` salvo tablas puente explícitas y pruebas de conservación de totales.
4. Alinear snapshots demográficos y rendimiento por una política temporal documentada.
5. No sumar interacciones con visualizaciones.
6. Recalcular engagement como razón de sumas: `sum(interacciones) / sum(denominador)`; nunca promedio simple de porcentajes con bases distintas.
7. Conservar numerador, denominador, cobertura y tamaño de muestra en toda tabla derivada.
8. Marcar cada resultado como `directo`, `estimado` o `no_disponible`.

## 5. Modelo central propuesto

Hechos:

- `fact_rendimiento`
- `fact_publicacion`
- `fact_comentario`
- `fact_demografia_snapshot`
- `fact_riesgo`

Dimensiones:

- `dim_colegio`
- `dim_cuenta`
- `dim_plataforma`
- `dim_fecha`
- `dim_segmento`
- `dim_tipo_contenido`
- `dim_tema`

Puentes explícitos:

- `bridge_publicacion_comentario`
- `bridge_alerta_publicacion`
- `bridge_colegio_alias`

## 6. Criterios de entrada para implementar Fase 5

- Catálogo inicial de `colegio_id` aprobado y con alias.
- Contrato de `publicacion_id` y `comentario_id` definido.
- Política temporal para snapshots aprobada.
- Catálogo de métricas con numeradores y denominadores.
- Pruebas automáticas de cardinalidad y conservación de totales.
- Etiquetado visible de resultados directos frente a estimados.
- Filtros globales compartidos definidos antes de construir el laboratorio.
