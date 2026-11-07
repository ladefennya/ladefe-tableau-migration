# LADEFE: validación de disponibilidad para tableros nativos

Fecha de consulta y descarga: 6 de noviembre de 2026. Veredicto: **APTO CON RESERVAS para construir tableros nativos; no certifica equivalencia integral ni habilita publicación automática.**

## Respuesta principal

Disponemos de la información pública incorporada en los 71 workbooks inventariados: datos numéricos, valores auxiliares, períodos, territorios, aperturas, unidades, fórmulas, catálogos y reglas de Tableau. Se volvieron a descargar los 71 paquetes y se abrieron sus 71 extractos Hyper (497 tablas). Se preservan en este paquete las seis tablas no geométricas por workbook, sin perder su procedencia. La geometría se incluye una sola vez, desde GitHub: sus 24 filas coinciden exactamente con la fuente actual.

La copia de GitHub no estaba completamente actualizada: hay diferencias en 10 de los 71 conjuntos del demo. Los 61 restantes coinciden exactamente en todos los campos presentes en el demo, normalizando únicamente nulos y representación textual de tipos. No se afirma identidad byte por byte de paquetes ni que todo campo omitido por el demo haya sido validado en esa comparación.

## Evidencia cuantitativa

- Descarga y apertura: 71/71, sin fallos.
- Filas físicas actuales, incluidas repeticiones entre paquetes y metadatos: 975.218. La extracción histórica registraba 961.554.
- Tabla Datos actual, unión de filas completas distintas: 28.448; histórica: 25.792. Respecto de la unión actual, 2.702 filas no estaban en la copia anterior y 46 filas históricas ya no aparecen. No son necesariamente altas/bajas de observaciones: un cambio de un valor o metadato produce una fila distinta.
- Datos seleccionados para los 71 tableros: 14.156 filas actuales frente a 14.016 del demo guardado. La diferencia neta de 140 no resume todos los cambios de valores.
- Valores nulos en las 14.156 filas seleccionadas: 0.
- Referencias a indicadores o grupos inexistentes: 0.
- Claves dimensionales con más de una fila, excluyendo ID técnico y medidas: 0.
- Fórmulas vacías entre los vínculos tablero–indicador utilizados: 0. Hay 89 vínculos sin descripción metodológica textual; es una carencia de documentación de la fuente, no pérdida de valores.
- Cálculo territorial: los 4.017 registros MAPA del demo coinciden, a tolerancia 1e-9, con la regla de Tableau: cantidad directa o cociente de sumas con el factor de porcentaje/tasa correspondiente, a la granularidad de cada fila.
- Los valores de las 9.999 filas no MAPA del demo no se alteran por su función de cálculo actual. Las definiciones XML de los 71 Tableau usan AVG(VALOR) en las hojas de series, características y cruces inspeccionadas; no corresponde trasladar ese promedio a poblaciones o aperturas distintas sin replicar los filtros.
- Validación existente: validate_demo.py aprobado; cinco archivos de pruebas Node aprobados. Son regresiones internas, no una prueba independiente de fidelidad de toda la interfaz.

## Hallazgos y condiciones

| Severidad | Hallazgo | Consecuencia y cierre |
|---|---|---|
| Error | 10 tableros difieren de GitHub | Usar las tablas actuales por workbook incluidas y regenerar la salida nativa antes de publicar. |
| Bloqueante para integrar globalmente | Indicadores con mismo ID y distintas versiones de metadatos en la tabla consolidada histórica | Conservar workbook + ID y procedencia de cada fila. No construir un diccionario global por INDICADOR_ID que sobrescriba versiones. Las tablas por workbook actuales no tienen IDs de indicadores duplicados internamente. |
| Advertencia | Los JSON del demo omiten fórmula, sección, ID técnico y otros metadatos | El backend debe partir de las tablas completas conservadas, no solamente del demo. |
| Advertencia | 89 vínculos sin descripción metodológica | Completar o explicitar con responsables temáticos antes de certificar interpretación. |
| Bloqueante para declarar equivalencia integral | No se certificó interacción por interacción contra Tableau renderizado | Validar selecciones, filtros, agregaciones, años, aperturas y relaciones entre vistas en los seis arquetipos documentados. |
| Advertencia | Los paquetes contienen datos repetidos de otros tableros | No sumar la totalidad de todos los Hyper. Seleccionar el tablero y preservar la versión de su workbook. |
| Advertencia | Datos futuros/proyecciones presentes | Identificar proyecciones con su metodología; no tratarlas como observaciones realizadas. |

## Qué está verificado y qué no

Está verificada la disponibilidad, lectura, estructura, cobertura de los 71 workbooks conocidos, integridad referencial de sus datos seleccionados, ausencia de colisiones dimensionales en esa selección y el cálculo de mapa del demo a nivel de registro. La comparación se hizo contra una nueva descarga de Tableau Public, no solo contra archivos generados por nuestro propio sistema.

No se verificó que el sitio institucional actual no haya agregado otros workbooks fuera del inventario de 71; tampoco todas las combinaciones interactivas, agregados regionales/nacionales, filtros, orden editorial, relaciones entre indicadores y descargas renderizadas. No se certifica validez sustantiva de las estadísticas oficiales ni actualización posterior al momento de descarga. No se dispone necesariamente de microdatos o planillas internas previas a Tableau. La extracción permite reconstruir lo que los workbooks públicos contienen, no recuperar registros que nunca fueron incluidos en ellos.

La geometría provincial existente sigue siendo un recurso de partida: su coincidencia física no certifica por sí sola proyección, límites o presentación cartográfica. No se modificó ni publicó el sitio ni el repositorio.

## Próximo paso

Construir el backend nativo desde las tablas por workbook actuales, con claves compuestas y reglas explícitas por tipo de vista. Luego cerrar la matriz de equivalencia de los seis arquetipos (AUH, censo, índice base 100, migraciones censales, vivienda F02 y mortalidad F02) sobre la salida efectivamente renderizada. La aprobación temática requiere intervención de responsables de la Defe.

## Contenido del respaldo

- source_tables/: seis tablas completas por cada workbook, JSON comprimido; incluye Datos, Indicadores, Grupos Indicadores, Tableros, Temas y Configuracion. No se incluyen 71 copias de la geometría.
- canonical_github/: siete tablas históricas, esquema y resumen, para conservar la comparación y la geometría validada.
- definitions/: XML de los 71 Tableau descargados, con atributos de posibles credenciales redactados y sin miniaturas ni imágenes decorativas embebidas. Se preservan filtros, acciones, relaciones y fórmulas para reconstrucción funcional.
- evidence/: resultados completos, hashes SHA-256 de las descargas, matriz de 71 tableros y reglas de hojas inspeccionadas.
- scripts/: programas de comprobación y scripts del repositorio necesarios. Para reproducir: instalar requests y tableauhyperapi; adaptar las rutas /tmp/ladefe-check y /tmp/ladefe-validation; ejecutar download.py, audit.py, semantic_rules.py y quality.py. Hyper se inició con use_tcp_port=auto por limitación local de sockets Unix.

Repositorio examinado: https://github.com/ladefennya/ladefe-tableau-migration
Commit: 371aaae89c8a91b499d6fac20aec6ff49da376e3.
Procedencia histórica: results/latest/PROVENANCE.md, run 34201432535, fuente e4b8f3dd435a7c777347dfcb1924b2d9f10f0556, 2026-09-08T07:58:02Z. La consulta de artifacts de ese run devolvió lista vacía; no se infiere de ello el motivo.

## Tableros con diferencias

- 2_1aTasasdepobreza
- 3_2bEstablecimientosOfertayciclosNI
- 3_2cEstablecimientoselectricidad
- 3_2dEstablecimientosAccesoainternet
- 3_2eEstablecimientosLaboratorioinformtica
- 3_2eEstablecimientosEntregadealimentos
- 3_3aMatrculaECCaractersticas
- 3_3bMatrculaECNivelInicial
- 8_3bNNyAmigrantes_Losmigrantesenlasreasurbanas
- 8_3cNNyAmigrantes_Losmigrantesenlosregistrosadministrativos
