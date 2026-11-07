# Contrato estadístico para la migración nativa LADEFE

Estado: propuesta técnica verificable, pendiente de aprobación temática. No certifica equivalencia visual ni valida automáticamente los 71 tableros. La base de 14.156 observaciones conserva la fuente; se exige una capa semántica explícita antes de publicar.

## Identidad y granularidad

Cada observación conserva snapshot, workbook, ID_DATO_SM, ID de tablero, grupo e indicador, vista, dimensiones originales, valor, auxiliar y JSON original. El identificador local fuente ID_DATO_SM no se repite dentro de cada workbook en la selección actual; no se supone unicidad entre archivos. Usar workbook + source_id para trazabilidad y una clave conceptual curada para comparación histórica. El hash actual incorpora etiquetas y por eso un cambio de texto puede parecer alta/baja; esas cifras no son automáticamente altas/bajas estadísticas.

No usar INDICADOR_ID como identidad global: la base contiene 164 IDs con más de una variante de metadatos entre archivos. Una equivalencia entre versiones necesita tabla de correspondencia con fechas, fuente y decisión, no un diccionario que elija la última fila.

## Contrato mínimo por indicador y vista

Campos obligatorios antes de publicación:

- universo y exclusiones; unidad de observación; población de referencia y rango de edad;
- fuente primaria, edición, fecha de publicación, fecha de extracción y versión de metodología;
- fecha/período estadístico real, período de recolección y período de referencia, separados de raw_year y de la fecha de actualización del tablero;
- geografía de referencia, geografía de residencia/hecho cuando corresponda, nivel territorial y versión de códigos/límites;
- magnitud: conteo, proporción, tasa, índice base 100, variación, media/mediana o importe; stock/flujo; unidad física y factor;
- valor directo o numerador/denominador, fórmula y regla de agregación permitida;
- peso y diseño muestral, dominio estimable y limitaciones de precisión cuando corresponda;
- categorías válidas, tratamiento de faltantes/sin especificar, exhaustividad y exclusión mutua;
- relaciones explícitas entre vistas y entre indicadores; procedimiento de revisión y estado de aprobación.

El código PORCENTAJE de la fuente no basta para inferir una proporción: hay índices base 100 y tasas de variación. La clasificación por palabras del nombre o fórmula es un candidato, nunca aprobación semántica.

## Reglas de cálculo

1. Guardar numerador y auxiliar tal como vienen de origen, sin recortar rangos ni imputar ceros.
2. Aplicar la fórmula de la vista, no una regla universal por unidad. La instantánea actual usa ratios en MAPA y valores directos en otras vistas; hay 15 filas no MAPA con auxiliar. No recalcularlas por tener ese campo.
3. Para agregados de tasas/proporciones: ratio de sumas solo cuando los numeradores y denominadores sean aditivos, de universo compatible y sin solapamiento. Un denominador repetido por categoría no puede sumarse sin regla explícita.
4. No promediar porcentajes ni tasas entre territorios. No sumar índices, stocks de meses sucesivos, personas repetidas, promedios o medianas. Los flujos solo se suman cuando unidad, período y deduplicación sean compatibles.
5. Los XML de Tableau contienen AVG(VALOR) en las vistas directas. Se debe reproducir el nivel de detalle y los filtros que determinan cada marca. Que el registro individual coincida no prueba que AVG sea válido al juntar edades, sexos, modalidades o períodos. Para una marca con una sola observación semántica, AVG equivale al valor directo; si hay varias, bloquear hasta contar con agregación explícita o mostrar series separadas.
6. Un valor de abandono negativo o una escolarización superior a 100 no se corrige a cero/cien sin consultar la metodología. Los tres abandonos contrastados por el equipo con Educación son consistentes con las limitaciones del modelo de flujo.
7. Los datos ponderados de EPH/EPHU requieren definición de ponderador por magnitud y período, dominio muestral compatible y tratamiento de no respuesta. No presentar errores estándar o precisión inventados. Las diferencias entre puntos estimados no prueban diferencias estadísticamente significativas.

## Contrato temporal y casos observados

Crear campos separados: raw_year, raw_period, reference_period, comparison_period, collection_period y period_role. reference_period no se llena ciegamente con ANIO ni con texto de APERTURA_DESCRIPCION.

Salud, workbook 4_1Coberturadesalud, indicador 789: ocho filas APERTURA tienen ANIO2022…2029 secuencial, mientras APERTURA_NIVEL_2 dice Año Censal y su modalidad indica explícitamente2010 o2022. Propuesta de normalización: representar el período de comparación desde la dimensión Año Censal y conservar raw_year como atributo fuente no usado como eje. Esta regla específica exige cotejo con Tableau y ficha primaria antes de aprobarse. No son ocho observaciones de una serie2022–2029 ni seis pronósticos.

Comedores, workbook3_2eEstablecimientosEntregadealimentos, indicador465: doce filas APERTURA combinan nivel y ámbito. En inicial y primario, ANIO2024/2025/2026 coincide con modalidades Total/Urbano/Rural; para secundario avanza2027/2028/2029. El patrón sugiere un problema de carga/orden, pero no acredita un año común sustituto. No asignar2024 o2025 por inferencia. Mantener período pendiente hasta comprobar cuadro fuente y versión.

Una actualización o etiqueta vieja tampoco debe usarse sin contraste: el equipo educativo revisa casos de ciclos2023/2024 vs2024–2025. Guardar año inicial, año final y tipo de ciclo por separado cuando la fuente mide transiciones escolares.

## Reglas cartográficas estadísticas

Usar coropletas para magnitudes relativas comparables con denominador compatible y leyenda fija al comparar períodos; representar cantidades con símbolos o barras cuando el área no sea magnitud. No forzar mapa en indicadores nacionales o muestras cuyo dominio no permita provincias. Ningún agregado territorial se construye con promedios implícitos ni se geocodifica a una resolución más fina que la fuente. Separar sin dato, no aplicable, secreto estadístico y cero. No convertir ausencia de provincia en cero.

## Estados y puertas de publicación

- Preservado: descargado y conservado sin pérdida; no autoriza uso interpretativo.
- Verificado técnicamente: esquema, claves, conteos, tipos y conservación aprobados.
- Mapeado semánticamente: universo, períodos, geografía y fórmula documentados.
- Contrastado con fuente: valores reproducidos en recurso primario equivalente.
- Contrastado con Tableau: filtros, marcas, cálculos y descargas comparados en casos definidos.
- Aprobado temáticamente: decisión registrada por responsable designado.
- Publicable: todas las puertas pertinentes y revisión UX/cartográfica aprobadas.

Bloquea la publicación de la vista afectada: período sin resolver, unidad/cálculo incompatible, referencia de indicador inexistente, clave dimensional ambigua, denominador imposible, falta de dominio para un mapa o relación inferida entre indicadores. Se conserva la observación original y una última versión aprobada de la vista.

No bloquea automáticamente todo el producto: falta de una definición descriptiva complementaria si universo y cálculo están acreditados; salto interanual sin defecto demostrado; ausencias territoriales justificadas; valores fuera de0–100 permitidos por la metodología. La advertencia visible y la decisión deben quedar vinculadas a la observación/indicador.

## Pruebas de aceptación

Por cada arquetipo: un conteo, un ratio, un índice, un período, una apertura y una combinación territorial cuando existan; luego reconciliar el conjunto completo de marcas bajo los filtros aprobados. Guardar corte, dimensiones, archivo/hoja/celda fuente, valor sin redondear, regla, tolerancia y resultado. No aplicar la misma tolerancia a conteos exactos y a estimaciones redondeadas.

Para una suma porcentual de k categorías exhaustivas/no solapadas publicadas a un decimal, la discrepancia atribuible a redondeo no supera0,05×k puntos. La suma101,0 de tres categorías excede0,15puntos; no es atribuible solo a redondeo si se confirma ese universo. No normalizar automáticamente a100.

Las alertas temporales mayores al50% son cribado exploratorio. Su uso debe tener umbrales y dominio declarados, revisión de cambios de método/base y un registro de decisiones; no llamarlas outliers estadísticos confirmados ni pruebas de error.

Cada cambio de fuente debe comparar historia completa o ventana de revisión documentada, no únicamente anexar un nuevo período. Una revisión oficial se conserva como nueva versión, con manifiesto y delta revisable.

## Decisiones metodológicas cruzadas del equipo

### Denominador elegible y datos no especificados

Para cada tasa guardar `population_total`, `eligible_denominator`, `excluded_unknown` y la regla de elegibilidad cuando esas cantidades existan. No llamar genéricamente «nacidos vivos» al denominador si se excluyen pesos o edades gestacionales sin especificar. La selección se hace por variable/indicador y edición: no se eliminan por defecto todas las filas con algún campo desconocido.

El agente de salud comunicó validación empírica de componentes para bajo peso y pretérmino usando códigos de CSV DEIS y fórmulas de Tableau. Esto sostiene una candidata técnica; no reemplaza la ficha oficial inequívoca. Los resultados iniciales discrepantes incluían un defecto del parser ya corregido, por lo que no deben difundirse como defectos de los datos originales. Toda discrepancia debe pasar primero por el control de lectura, clasificación, códigos y tratamiento de nulos del adaptador.

### Período escolar

Una tasa de transición 2024–2025 requiere guardar ambos extremos del ciclo. Un valor puede coincidir con el archivo oficial del ciclo nuevo aunque su etiqueta de APERTURA quede en «2023/2024». Esa coincidencia numérica no autoriza a publicar con la etiqueta vieja ni a cambiar el año sin registrar una decisión curada. El agente educativo reporta 15 casos de esta clase y una discrepancia residual que no se resolvió relajando la tolerancia. Se requiere conservar la comparación y revisar edición/recálculo de la fuente.

### Reconstrucción de EPHU

La reconstrucción de lugar de nacimiento debe registrar CH15, ponderador, universo, edad y códigos de no respuesta. Que una estimación pública sume 100 % no prueba que reproduzca el indicador de la Defe. El equipo social comunicó valores alternativos compatibles con una reconstrucción bajo una regla declarada, pero distintos del archivo de Tableau. Su uso queda como candidato hasta cotejar el contrato completo; no se reemplazan 87,3/10,1/3,6 solamente por forzar una suma100.
