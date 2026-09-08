# Revisión de relaciones entre vistas de los seis pilotos

Fecha: 2026-09-08  
Fuente: `view_mapping_candidates.csv` generado a partir del catálogo canónico.

## Decisión ejecutiva

El motor común puede escalar a los 71 tableros, pero la asociación entre indicadores de distribución, mapa y serie **no puede escalarse por inferencia automática**. Compartir grupo, tablero y unidad reduce candidatos, pero no garantiza que coincidan el concepto, el universo, el denominador ni la periodicidad.

Para el demo se habilitaron tres relaciones de alta confianza y se dejaron fuera todas las alternativas conceptualmente ambiguas. Las relaciones habilitadas siguen siendo provisionales hasta la validación temática.

## Resultado de la cola de revisión

Los seis pilotos generan 127 solicitudes de vistas relacionadas.

| Tablero piloto | Solicitudes | Candidato único de igual unidad | Ambiguas | Sin candidato | Unidad incompatible |
|---|---:|---:|---:|---:|---:|
| Información censal | 33 | 17 | 3 | 12 | 1 |
| AUH | 21 | 9 | 6 | 4 | 2 |
| Vivienda y hacinamiento | 17 | 7 | 5 | 5 | 0 |
| Establecimientos educativos | 16 | 6 | 3 | 4 | 3 |
| Mortalidad adolescente por suicidios | 11 | 0 | 2 | 8 | 1 |
| Migrantes en censos nacionales | 29 | 5 | 13 | 11 | 0 |
| **Total** | **127** | **44** | **32** | **44** | **7** |

“Candidato único de igual unidad” es una señal para revisar, no una aprobación. Puede seguir existiendo una diferencia de población o significado.

## Relaciones habilitadas provisionalmente

| Tablero | Relación | Miembros | Serie | Mapa | Control técnico |
|---|---|---|---|---|---|
| Información censal | Participación de NNyA en la población | 488, 489, 490, 501, 504 | 489 | 504 | Porcentaje; serie multianual; 24 jurisdicciones sin duplicados |
| Información censal | Residencia rural | 512, 513, 516, 519 | 519 | 516 | Porcentaje; serie multianual; 24 jurisdicciones sin duplicados |
| Vivienda y hacinamiento | Hacinamiento | 813, 814, 815 | 815 | 814 | Porcentaje; serie 2001–2022; 24 jurisdicciones sin duplicados |

Estas asociaciones viven en `demo/view-relations.json`, se muestran explícitamente en la interfaz y son verificadas por `tests/view_relations.test.js`.

## Relaciones diferidas

| Piloto | Motivo de bloqueo |
|---|---|
| AUH | El mapa disponible representa cobertura o perceptores por jurisdicción, mientras las series alternativas representan promedios anuales, trimestrales, valores base 100 o titulares. La unidad por sí sola no preserva el concepto. |
| Establecimientos educativos | Para cada nivel existen mapas alternativos de gestión estatal y ámbito rural. La serie base 100 combina aperturas y no determina cuál mapa debe acompañarla. |
| Mortalidad por suicidios | Las series alternativas cambian grupos de edad, sexo y, en un caso, el factor de la tasa (por 10.000 frente a por 100.000). |
| Migrantes | Los candidatos alternan población nacida en otro país, migración interna, población total, NNyA y distintos denominadores territoriales. |

## Camino de escalamiento

1. Mantener desactivada toda relación no registrada explícitamente.
2. Revisar candidatos por familia conceptual, no sólo por coincidencia de unidad o grupo Tableau.
3. Registrar para cada relación: universo, numerador, denominador, unidad, períodos, aperturas y justificación.
4. Exigir controles automáticos de existencia, tipo de vista, unidad, cobertura temporal y unicidad territorial.
5. Obtener validación temática y cambiar el estado de provisional a aprobado.
6. Recién entonces ampliar la curaduría por lotes a los 71 tableros.

## Gate actualizado

- **Arquitectura y extracción:** aptas para escalar a 71/71.
- **Renderizado configurable:** apto, con relaciones explícitas y módulos adaptativos.
- **Equivalencia semántica integral:** todavía condicionada a la curaduría y validación temática.
- **Inferencia automática de vistas relacionadas:** descartada como estrategia de producción.
