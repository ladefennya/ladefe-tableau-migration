# Paso 2 — Ingeniería inversa de los cinco workbooks piloto

Fecha: 2026-09-08  
Fuente técnica: run 34180503202 (repetición verificada del run 34132131132).

## Decisión

**Sí: la ingeniería inversa puede escalarse a los 71 workbooks únicos.**

La decisión se refiere a la descarga, apertura de TWB/TWBX, inventario técnico y extracción de datos Hyper. Los cinco pilotos demostraron una arquitectura común y totalmente legible. No significa todavía que los 71 tableros puedan reconstruuirse visualmente sin revisión: primero hay que ejecutar el inventario completo y detectar excepciones.

## Evidencia del piloto

- 5/5 workbooks descargados y parseados; 0 fallas.
- Cada descarga es un TWBX con un TWB y un extracto Hyper.
- 295 worksheets, 20 dashboards, 1.460 campos, 410 cálculos, 1.235 filtros, 105 parámetros y 35 tablas Hyper.
- Los cinco repiten exactamente la misma huella estructural: 59 worksheets, 4 dashboards, 292 campos, 82 cálculos, 247 filtros, 21 parámetros, 4 conexiones, 30 relaciones, 7 tablas Hyper y 73 columnas Hyper.
- Las siete tablas físicas también son comunes: Datos, Grupos Indicadores, Tableros, provincia.shp, Temas, Configuracion e Indicadores.
- La tabla Datos conserva una estructura canónica de 22 columnas para tema, tablero, sección, indicador, tipo de dato, tiempo, geografía, aperturas y valores.
- Las conexiones observadas son federated, excel-direct, ogrdirect y hyper. El TWBX contiene el extracto Hyper, por lo que no depende de acceder a las rutas locales Windows que quedaron como metadatos históricos.
- Los workbooks comparten la plantilla de navegación y visualización, incluidos los parámetros p_tablero, p_seccion, p_codigo_indicador, p_grafico y los selectores de evolución temporal, distribución territorial, cruces y características.

## Volumen por piloto

| Workbook | Filas Hyper totales | Filas en Datos |
|---|---:|---:|
| Información censal | 12.983 | 12.164 |
| Pobreza monetaria | 12.951 | 12.132 |
| Matrícula secundaria | 13.296 | 12.462 |
| Natalidad | 13.050 | 12.225 |
| Justicia juvenil | 13.050 | 12.225 |

Los tamaños y algunas muestras coincidentes indican que cada workbook incluye una porción amplia —y parcialmente duplicada— del modelo de datos institucional. Esto favorece una migración hacia un único backend canónico, en vez de reproducir 71 paquetes aislados.

## Riesgos todavía abiertos

1. Los cinco pilotos pertenecen a la misma familia de plantilla. Falta comprobar si los otros 66 contienen variantes o excepciones.
2. El inventario XML describe cálculos, filtros y acciones, pero la equivalencia visual debe validarse por componentes y no por conteo bruto.
3. Justicia juvenil tiene automatización de fuente estimada como baja; esto afecta la actualización futura, no la posibilidad de migrar el tablero actual.
4. Deben deduplicarse los datos repetidos entre extractos antes de diseñar almacenamiento y pipelines.
5. Hace falta clasificar los campos calculados en: lógica sustantiva, formato, navegación y compatibilidad Tableau. No corresponde portar los 410 cálculos ciegamente.

## Criterio de escalado

Avanzar con los 71 mediante un inventario completo, automático y por lotes. Para cada workbook se debe calcular una firma con:

- éxito de descarga y tipo de paquete;
- nombres y esquema de tablas Hyper;
- cantidad de worksheets, dashboards, campos, cálculos, filtros, parámetros, acciones y relaciones;
- conjunto de parámetros;
- columnas de Datos e Indicadores;
- tamaño y conteo de filas;
- hash o firma de las tablas para medir duplicación;
- anomalías frente a la plantilla común.

Después, agrupar los 71 por firma. Los que coincidan con la familia piloto pueden migrarse con el mismo adaptador; las excepciones pasan a revisión manual.

## Próxima ejecución recomendada

1. Incorporar al repositorio el catálogo de los 71 workbooks únicos.
2. Ejecutar el probe completo con límite de concurrencia y registro de fallas por workbook.
3. Generar una matriz de clustering y deduplicación.
4. Elegir un workbook de cada familia estructural y construir el adaptador canónico.
5. Recién entonces estimar con precisión el esfuerzo de réplica visual y de pipelines de actualización.

## Conclusión operativa

El resultado elimina el principal riesgo técnico: los TWBX y sus datos no son cajas negras. El escalado del análisis a 71 es viable ahora. La decisión prudente es **escalar el inventario completo**, no asumir aún que los 71 son idénticos ni empezar 71 reconstrucciones separadas.
