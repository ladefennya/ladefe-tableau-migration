# LADEFE — Matriz de validación de pilotos

La cobertura técnica de 71/71 workbooks no equivale a fidelidad estadística. Esta matriz define el gate previo a certificar el escalamiento.

| Arquetipo | Tablero | Riesgo que debe probarse | Evidencia de aceptación |
|---|---|---|---|
| Cantidad, porcentaje, mapa y serie | `2-2bauh` | Ratio numerador/denominador, selección de indicador, escalas muy diferentes | Cobertura de Buenos Aires `34,15 %`; mapa, ranking, KPI y tabla comparten indicador, año y unidad |
| Censo territorial | `1-1aspectosdemogrficos-informacincensal` | Porcentaje provincial y agregado nacional | Participación de NNyA calculada con población total; 24 jurisdicciones y total reconciliados |
| Índice base 100 | `3-2aestablecimientoscaracteristicas` | No confundir denominador auxiliar con fórmula de porcentaje | Año base conserva `100`; serie completa coincide con Tableau |
| Dimensiones temporales múltiples | `8-3annyamigrantes-losmigrantesenloscensosnacionales` | No promediar grupos 0–17 y 0–19 ni otras aperturas | Cada combinación dimensional produce una serie separada o exige selección explícita |
| Familia F02 territorial | `2-5aviviviendacfchabitacionales` | Fórmula porcentual, hacinamiento y compatibilidad F02 | Hacinamiento de Buenos Aires reconciliado; sin conteos rotulados como porcentaje |
| Familia F02, mortalidad | `7-3emortalidadadolescentesuicidios` | Tasas, causas, escalas y ausencia de vistas | Tasa y denominador reconciliados; la UI sólo muestra módulos válidos |

## Criterios obligatorios por tablero

1. Nombre, orden editorial, definición, unidad, fuente, metodología y fecha de actualización identificados.
2. Fórmula documentada y clasificada como valor directo, índice o ratio con factor.
3. Conteos de filas, períodos, aperturas y jurisdicciones reconciliados.
4. Ningún promedio o asociación entre indicadores implícito.
5. Mapa, ranking, KPI, serie, tabla y CSV identifican el indicador y la unidad que utilizan; cualquier asociación entre indicadores es explícita y auditable.
6. Comparación automática de valores testigo y revisión humana del responsable temático.
7. Captura de referencia y resultado de aceptación versionados con el commit y run de extracción.

## Relaciones de vistas provisionales

`demo/view-relations.json` contiene únicamente tres asociaciones de alta confianza: participación de NNyA en la población, residencia rural y hacinamiento. Cada asociación enlaza indicadores de la misma unidad con una serie temporal y un mapa de 24 jurisdicciones. Son relaciones técnicas provisionales: permiten evaluar el comportamiento integral del demo, pero requieren validación temática antes de considerarse equivalentes a la navegación editorial de Tableau.

Los demás candidatos permanecen fuera del demo cuando difieren en unidad, población de referencia o definición, o cuando existe más de una asociación plausible.

## Decisión de escalamiento

- **Avanzar:** seis pilotos sin defectos críticos y con diferencias dentro de la tolerancia documentada.
- **Corregir:** cualquier diferencia explicable por fórmula, dimensión, filtro o período.
- **Bloquear:** unidad incorrecta, agregado implícito, indicador sustituido o pérdida de trazabilidad.
