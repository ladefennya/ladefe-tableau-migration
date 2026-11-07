# Cartografía LADEFE — Segunda ronda técnica

## Dictamen

**No aprobar como cartografía de publicación el GeoJSON simplificado actual.** Los datos admiten mapas provinciales candidatos, pero se comprobó que el procesamiento cartográfico vigente introduce defectos topológicos. Esto es diferente de las anomalías estadísticas que ya estaban en los datos de los Tableau.

La corrección de faltantes de la primera ronda mejora un problema real, pero aún admite coerción de objetos/arrays y produce una leyenda engañosa cuando todos los valores son iguales. Se entrega un parche adicional, sin aplicarlo al repositorio.

## 1. Topología y comparación con la fuente

Se utilizó GDAL 3.10.3 con GEOS 3.13.1, disponibles en `/usr/bin/python3`, para verificar la geometría y medir áreas en EPSG:6933. Los resultados son diagnósticos de archivos, **no superficies oficiales**. No hubo reparación automática.

| Control | Fuente IGN WFS descargada | GeoJSON simplificado del demo |
|---|---:|---:|
| Features provinciales | 24 | 24 |
| Geometrías válidas GEOS | 24 | 16 |
| Geometrías inválidas | 0 | 8 |
| Identificador provincial en propiedades | `in1`,24 códigos distintos | Omitido por preparación; se conserva solo nombre |

Los ocho casos inválidos son Chubut, Río Negro, Misiones, Buenos Aires, Tierra del Fuego/Antártida/Islas del Atlántico Sur, Entre Ríos, Corrientes y Santa Cruz. Hay autointersecciones y, en Misiones, shells anidados. El archivo numéricamente podía tener anillos cerrados y coordenadas finitas y aun así ser topológicamente inválido: la primera ronda solo había verificado esas condiciones limitadas.

Se ejecutaron 276 intersecciones por pares del demo; 28 pares arrojaron intersección de área mayor a1m². En 21 de esos 28 pares ambas geometrías son válidas; los demás resultados son diagnósticos que requieren especial cautela. Ocho intersecciones emitieron diagnósticos de GEOS. El umbral de1m² evita ruido numérico en el listado; **no es una tolerancia de calidad aceptada**.

### Atribución reproducible

Se volvió a descargar el mismo endpoint y parámetros del workflow:

`https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ign:provincia&outputFormat=application/json&srsName=EPSG:4326`

La respuesta tiene111.718.447 bytes y24 features, SHA-256 `9afccbbc3862d7943d9f6d83ace934f16f716eb78fb3abe1a0ad058da3c0dccc`. Está disponible localmente en `/tmp/ladefe-ign-original.geojson`; no se incluye esa copia de111MB en esta entrega. Se conserva URL/hash en `ign_download.json` y script de descarga.

Al ejecutar el `prepare_map.py` vigente sobre esa respuesta se obtuvo un archivo byte por byte idéntico al demo: SHA-256 `3ad4209856ec265ffb100edd596a412ed461612f5b57c17935db7a9c1ce519e3`,137.873 bytes. Por tanto, el defecto de simplificación se reproduce con una fuente válida; no es necesario atribuirlo a un problema del IGN.

### Casos de frontera comprobados

| Par | Intersección en fuente original | Intersección en simplificado | Cautela |
|---|---:|---:|---|
| San Luis–Córdoba | 0km² | 142,29km² | Ambas geometrías de ambos archivos son válidas. Evidencia de desajuste de frontera compartida. |
| San Luis–Mendoza | 0km² | 70,00km² | Ambas geometrías de ambos archivos son válidas. |
| CABA–Buenos Aires | 0km² | 3,56km² | Buenos Aires simplificada es inválida; el área se informa solo como diagnóstico. |

En el mismo footprint de comparación y CRS de área, CABA pasa de205,62km² en la fuente a177,80km² en la geometría simplificada (−13,53%). Tierra del Fuego dentro del frame pasa de32.820,40 a31.731,90km²(−3,32%). Estos porcentajes cuantifican diferencias entre archivos; **no redefinen superficies oficiales ni prueban error en las estadísticas**, que no usan esas áreas como denominador en los datos inspeccionados.

La simplificación actual usa Douglas–Peucker independiente por anillo con tolerancia0,05grados. No preserva coherencia de límites compartidos ni verifica topología. El siguiente pipeline deberá construir/usar topología compartida, conservar códigos y probar validez, solapamientos y desviación, antes de fijar niveles de detalle. Reducir la tolerancia o ejecutar MakeValid por provincia no prueba que se hayan resuelto los límites compartidos.

## 2. Geometría candidata de referencia

Se generó `reference_geometry_candidate.geojson.gz`(7,28MB;26,61MB descomprimida). Contiene24 geometrías válidas, sin simplificación ni reparación, con código provincial explícito y fuente. Se aplicó únicamente la intersección con **el frame ya usado por el demo**[-74.5,-56,-52.5,-20].

Es una referencia para validación y comparación; **no es una versión web aprobada**: falta evaluar peso, carga móvil, accesibilidad y vista supervisada, además de revisar cobertura integral del país. No se editó ni sustituyó `demo/provincias.geojson`.

### TDF y Malvinas

En el archivo simplificado, la feature de TDF tiene668 anillos;584 componentes intersectan un bbox diagnóstico del área de Malvinas[-62.5,-53,-57,-50]. No significa584unidades estadísticas ni una clasificación oficial de islas; es una comprobación de presencia geométrica. Tierra del Fuego/Malvinas comparte código94; no debe duplicarse el valor provincial ni crearse otra jurisdicción.

El frame existente conserva esa región pero excluye Antártida y otras islas del Atlántico Sur. La geometría candidata de referencia utiliza el mismo frame para permitir comparación explícita, no introduce una decisión territorial nueva. Si el producto requiere representación integral, debe diseñar una composición/insets con cartografía oficial y rotulación clara. No se presenta este frame parcial como mapa oficial integral.

## 3. Escala, coerción y leyenda

El archivo actual de `map-utils.js` ya distingue null/undefined/booleanos de cero. Sin embargo, `Number([])`, `Number([0])`, `Number([5])`, `Number(new Number(0))` y objetos con conversión numérica se siguen interpretando como medidas. Un error de forma en JSON puede convertirse en un valor válido, y `Symbol` puede provocar una excepción. Esta capa no debe invocar `valueOf` sobre un objeto desconocido.

`map_scale_round2.patch` acepta solo números finitos o strings decimales finitos. Objetos, arrays, booleanos, BigInt, Symbol, strings vacías y formatos no decimales son faltantes de visualización; un validador de adquisición debe además registrar/bloquear el error de tipo, no ocultarlo silenciosamente como ausencia legítima.

Para un dominio constante, la propuesta produce **un solo intervalo y el color realmente utilizado**, en vez de cinco rangos idénticos con cinco colores. Para un dominio completamente vacío devuelve una escala sin intervalos. Cero real y negativos siguen siendo medidas.

Se agregó un tercer argumento opcional `{domain:[min,max]}`: permite que una escala aprobada permanezca estable al cambiar de año o filtro. Los llamados anteriores no cambian. Un dominio explícito no finito, invertido o mal formado bloquea con TypeError; no se ajusta silenciosamente. La función no decide qué dominio o paleta son estadísticamente adecuados: eso corresponde a la configuración aprobada del indicador.

Pruebas:

- `node test_scale_round2.js`: PASS con propuesta.
- Mismo test contra archivo actual: FAIL porque un array recibe un color de dato válido; registro en `current_scale_round2_failure.log`.
- `node /tmp/ladefe-check/tests/map_missing_values.test.js ./map-utils.proposed.js` usando ruta absoluta: PASS. Conserva los casos de la primera ronda.
- Los casos de dominio constante y fijo entre dos conjuntos verifican efectos visibles de leyenda/comparación; no son tests que se limiten a repetir las líneas de implementación.

No se modificaron proyección, selección territorial ni otras funciones del archivo original.

## 4. Configuración por indicador y corte

`map_policy_by_slice.json` contiene171 políticas candidatas para los171 cortes MAPA. Cada una incluye dimensiones exactas, período declarado, códigos presentes/ausentes, nivelprovincial, tipo de mapa candidato, alternativa de barras/tabla, reglas de faltantes, escala y estado de aprobación.

-171 cortes tienen aptitud **geográfica de datos**: códigos provinciales identificados, al menos dos territorios, sin duplicación por territorio y valores visualizables en la selección.
-0tienen comparabilidad temática aprobada por esta ronda.
-0se consideran listos para publicar con la geometría simplificada actual.
-Se excluyen10.091observaciones no elegibles como MAPA directo: nacionales, series sin código y otras vistas. Entre ellas20 filas de los indicadores789y465 con ANIOambiguo; quedan fuera de toda configuración de mapa directo y de filtros temporales derivados de ANIO.
-No se transformó código00 en provincia. Los ocho indicadores adicionales identificados desde aperturas en la ronda anterior siguen siendo candidatos que requieren transformación curada; no se activaron.

Aptitud cartográfica no significa comparabilidad. Por ejemplo, participación de AUH nacional por provincia y cobertura dentro de cada provincia no pueden usar la misma etiqueta ni sustituirse por compartir unidad%.

## 5. Coordinación UX y criterio de prototipo

Se recomendó a UX mantener barras/tabla como interfaz funcional y **mapa opcional desactivado o claramente candidato** mientras se reemplaza la geometría defectuosa. El piloto de abandono381 admite tasas negativas justificadas; si se habilita mapa debe considerar escala divergente respecto a0 y nota metodológica, con la aprobación semántica pertinente.

No se generó HTML/SVG presentado como validado. No se certificó visualmente el mapa ni el prototipo. Cualquier cambio de UI o cartografía debe revisarse con vista previa supervisada según las instrucciones del proyecto.

## Archivos y reproducción

-`check_topology.py`, `topology_results.json`: GEOS y superposiciones del demo.
-`fetch_ign.py`, `ign_download.json`: fuente oficial/hash; descarga original fuera del paquete.
-`compare_source_geometry.py`, `source_geometry_comparison.json`: validez, códigos y áreas en footprint común.
-`check_boundary_cases.py`, `boundary_case_comparisons.json`: tres pares de frontera comparados.
-`build_reference_geometry.py`, `reference_geometry_candidate.geojson.gz`, `reference_geometry_manifest.json`: referencia no simplificada.
-`map_scale_round2.patch`, `map-utils.proposed.js`, `test_scale_round2.js`, log de falloactual.
-`build_map_policy.py`, `map_policy_by_slice.json`, `excluded_observations.json`, `map_policy_summary.json`: elegibilidad técnica por corte.

Los scripts GDAL se ejecutan con `/usr/bin/python3`; los de SQLite/JSON usan Python estándar. Las rutas de entrada documentan este entorno y se pueden parametrizar al integrarlos. Los recursos originales, base maestra y repo no se modificaron.
