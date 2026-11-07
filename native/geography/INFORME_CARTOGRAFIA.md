# LADEFE — Evaluación de cartografía y estadística espacial

Corte: base maestra del 6/11/2026, lectura sin modificaciones. **Apto con reservas para diseñar mapas provinciales; no implica aprobación de comparabilidad, cartografía renderizada ni publicación.** Se inspeccionaron 71 tableros, 764 vínculos tablero–indicador, la geometría del demo, el código de proyección/colores y la preparación de mapas.

## Inventario verificable

| Comprobación | Resultado |
|---|---:|
| Tableros con al menos un indicador MAPA | 51 de 71 |
| Vínculos tablero–indicador con MAPA | 171 |
| Registros MAPA actuales | 4.065 |
| Cortes dimensionales MAPA identificados | 171 |
| Cortes con las 24 jurisdicciones | 154 |
| Cortes con menos de 24 jurisdicciones | 17 |
| Geometrías provinciales | 24 |
| Vínculos adicionales potencialmente cartografiables desde aperturas | 8 |
| Tableros nuevos que ganarían primer mapa solo con esos candidatos | 0 |

Los cortes agrupan todas las dimensiones originales salvo geocódigo/nombre, ID técnico, medidas y marca de sistema. No se supone que cada indicador con cobertura incompleta deba tener 24 jurisdicciones: el universo debe validarse. La matriz registra qué provincias faltan, no las rellena con cero.

Fuera de MAPA, los campos de geocódigo son nacionales o nulos: APERTURA y DISTRIBUCION tienen código00 y SERIE_TEMPORAL no tiene geocódigo. Sin embargo **no corresponde concluir que no hay geografía en esas vistas**. Hay provincias expresadas en categorías de aperturas. La búsqueda por coincidencia textual exacta, con alias controlados de CABA y TDF, detectó 184 filas en nueve vínculos; ocho de los nueve no tienen MAPA propio. Son candidatos de curación, no geocodificación aprobada.

## Geografía dentro de aperturas

- AUH217 y AUHD423: 24 provincias en MODALIDAD_APERTURA_NIVEL_2. Son participaciones de perceptores por jurisdicción en el total; no equivalen a cobertura dentro de cada provincia. AUH217 en Buenos Aires tiene37,64%, mientras AUH218 es otra definición y denominador. No asociar ambos por compartir grupo o unidad%.
- Protección614 (cantidad),613 y954 (proporciones): 24 provincias en MODALIDAD_APERTURA_NIVEL_1. Debe comprobarse población, gestión y fecha del relevamiento antes de proponer mapas o comparación longitudinal.
- Línea102263 y264: 20 provincias en categorías. Puede proponerse mapa con cuatro jurisdicciones sin dato, solo si el universo es nacional y la fuente confirma ausencia. No mostrarlas como cero llamados.
- Indígenas728 y972: categorías de seis jurisdicciones seleccionadas, con dos grupos por provincia. En728 existe además MAPA, por eso no aumenta el número de vínculos adicionales. No sumar grupos ni extender el resultado a24provincias; mapa de universo parcial con máscara explícita o preferencia por barras comparadas.

No hay coordenadas de establecimientos/equipamientos ni observaciones individuales en la selección nativa. Un mapa de puntos requerirá una fuente de localización independiente, con identificador y fecha. No se puede deducir localización puntual de un total provincial o de su centroide.

## Aptitud cartográfica y comparabilidad son dos decisiones distintas

| Puerta | Condiciones | Qué permite |
|---|---|---|
| Aptitud geográfica | Geografía identificada, correspondencia uno a uno de códigos, geometría disponible, período/dimensiones seleccionables, faltantes explícitos | Representar los datos en el nivel territorial que efectivamente poseen |
| Comparabilidad estadística | Mismo concepto, edad, población, período, unidad, denominador, método y edición; precisión suficiente y reglas de agregación documentadas | Comparar provincias, años o grupos sin sustituir indicadores |
| Publicación | Ambas puertas aprobadas, revisión de escala/leyenda/tooltip y accesibilidad, confidencialidad y aceptación temática | Habilitar vista pública correspondiente |

Una fila puede ser geográficamente apta y no comparable. Código00 no habilita un mapa provincial. Coincidencia textual de una categoría es evidencia de potencial, no aprobación de una transformación.

## Visualización recomendada

1. **Tasa, cobertura o proporción dentro de cada provincia:** coropleta secuencial cuando numerador/denominador y precisión son compatibles. Mostrar unidad, año, población, fuente y, cuando exista, intervalo de confianza. Con denominador cero, resultado nulo/no calculable y explicación, nunca0%.
2. **Cantidades absolutas:** ranking o símbolos proporcionales sobre una cartografía de referencia. No usar intensidad de color de grandes polígonos como opción principal para explicar volumen: provincias extensas dominan la lectura espacial. Si se ofrece coropleta de cantidades, declararlo y conservar ranking/table como alternativa.
3. **Participación en un total nacional:** barras ordenadas o símbolos proporcionales son preferibles como vista inicial. Un mapa opcional debe decir participación, no cobertura o riesgo provincial.
4. **Pocos territorios o muestra con dominios distintos:** barras/tablas y notas de universo. No convertir regiones o aglomerados EPH en provincias ni copiar a todos los departamentos el valor provincial.
5. **Series y distribuciones nacionales sin dimensión territorial real:** líneas, puntos, barras o tablas. No insertar un mapa vacío como decoración.
6. **Geolocalizaciones puntuales futuras:** ubicaciones de servicios públicamente difundidas y mantenidas; no ubicar domicilios de NNyA ni inferirlos de casos. Revisar riesgo de identificación de casos en celdas pequeñas antes de publicar desagregaciones sensibles.

Siempre ofrecer tabla accesible/CSV, búsqueda de territorio y selección por teclado. CABA necesita acceso equivalente mediante buscador/listado o detalle ampliado, porque su área es pequeña; no deformar toda la proyección para hacerla visible.

Escalas entre años deben permanecer fijas para el indicador/universo cuando la pregunta sea evolución o comparación; no recalcular cortes por el subconjunto filtrado sin advertirlo. Colores divergentes se reservan para una referencia con sentido (por ejemplo variación respecto a cero), no porque existan dos grupos. Evitar verde/rojo como único código. «Sin dato», «fuera del universo», «suprimido» y «no calculable» requieren estados distinguibles y texto explicativo; el cero es un dato válido.

## Geometría, proyección y dominio territorial

- El workflow obtiene `ign:provincia` del WFS del IGN, `srsName=EPSG:4326`; la geometría guardada contiene coordenadas lon/lat en24features. El código del demo usa una proyección Albers con escala uniforme para encajar el contenedor. Este control no certifica visualmente la proyección ni el aspecto del mapa.
- Se verificaron códigos mediante correspondencias explícitas de nombres: las24features pueden vincularse a los24códigos provinciales. El GeoJSON actual solo conserva nombres (`nam`, `fna`), no el identificador. El proceso nativo debe conservar el código IGN/INDEC y usarlo como clave principal; nombres son etiquetas.
- No se encontraron coordenadas no finitas, anillos sin cerrar ni anillos con menos de4puntos en el archivo simplificado. Esto **no prueba validez topológica**, conservación de superficies, ausencia de cruces o precisión de límites. Falta verificar topología y tolerancia de simplificación en CRS métrico.
- Tierra del Fuego es una feature con668anillos y2.895puntos; su bbox es[-68.609416,-55.063507,-57.687687,-50.996952]. Incluye la isla de Tierra del Fuego y polígonos en el ámbito de Malvinas bajo la misma feature/código94. No duplicar el dato provincial en una segunda provincia ficticia de Malvinas.
- El procesamiento actual filtra a longitudes[-74.5,-52.5] y latitudes[-56,-20]. Por diseño deja fuera otras partes del dominio integral de la provincia, incluyendo áreas antárticas y otras islas del Atlántico Sur. Por ello debe declararse el dominio de representación y diseñarse una versión/inset apropiado con cartografía oficial si se desea representación territorial integral. No cambiar silenciosamente el recorte ni deformar/trasladar geometrías.
- El simplificador usa tolerancia0,05grados y no verifica topología. La siguiente implementación debería conservar un original oficial y derivar niveles de detalle con tolerancias en metros y validación de agujeros/anillos/área. La conformidad numérica de los24features no sustituye la revisión visual supervisada exigida por el proyecto.

## Defecto comprobado en el tratamiento de faltantes

La función actual `discreteScale` convierte entradas con Number(). `Number(null)` y Number('') producen0. El test histórico usa una escala con mínimo18 y pasa accidentalmente porque el índice negativo se trata como faltante. En una escala que contiene0, null recibe un color de dato válido. Esto puede confundir ausencia y cero.

Se entregan `map-utils.proposed.js`, `map_scale_fix.patch` y `test_scale.js`. La propuesta valida nulos, undefined, NaN, strings vacías, infinitos y booleanos antes de convertir; preserva cero real, stringnumérica0 y negativos; maneja dominio completamente vacío; y acota valores numéricos fuera de dominio a los extremos. No cambia geometría, proyección ni otras funciones. El ensayo sobre el archivo actual falla con null y dominio[0,5,10]; sobre la propuesta pasa. El registro de fallo queda en `current_scale_failure.log`. No se aplicó el parche al repo ni se publicó.

Comandos:

```sh
python audit_geography.py
node test_scale.js
node test_scale.js /ruta/demo/map-utils.js
```

El último comando falla en el estado original inspeccionado, lo que demuestra la regresión faltante. Los caminos de entrada de audit_geography.py corresponden al entorno de esta revisión y pueden parametrizarse en la integración.

## Criterios de aceptación para un mapa nativo

- Geocódigo único y válido para la jurisdicción y nivel declarados; join reporta coincidencias/no coincidencias y evita doble conteo nacional+provincial.
- Una observación por territorio y combinación de todas las dimensiones seleccionadas; conflictos bloquean render.
- Unidad, cálculo, universo, período y denominador conservados y verificables. Una relación con otro indicador solo mediante configuración curada.
- Cobertura territorial explícita por corte, con estado de ausencia y motivo cuando exista; la prueba de24 solo se aplica si el universo es de24.
- Escala/leyenda coherentes con tipo de medida y comparación pretendida; cero y faltantes siempre distintos.
- Geometrías oficiales con procedencia, fecha, código, CRS y dominio espacial; topología y simplificación verificadas.
- En escritorio/móvil, verificar proyección, TDF/Malvinas, CABA, leyenda, tooltip, selección, zoom/detalle, tabla y teclado con una vista previa supervisada local. No se realizó esa prueba aquí porque no se alteró UI ni se generó una nueva página.

## Próximo paso

Integrar la corrección de faltantes en rama de revisión, ampliar las regresiones y preparar un piloto cartográfico con cantidad, porcentaje de cobertura y participación nacional como tres casos distintos. Acompañarlo de la revisión visual supervisada y aprobación de las relaciones semánticas.
