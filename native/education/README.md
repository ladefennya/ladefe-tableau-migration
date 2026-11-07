# Adaptador educativo LADEFE: abandono interanual

Estado: implementación candidata, validada técnicamente y conciliada en los alcances indicados. No reemplaza la base publicada ni acredita equivalencia visual/interactiva, ni aprobación temática. Repositorio de referencia: `ladefennya/ladefe-tableau-migration`; no se modificó.

## Fuente y contrato

- Fuente oficial: Secretaría de Educación de la Nación, [Indicadores Educativos](https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores).
- [ZIP de tasas de abandono](https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip), descargado en la evaluación del 6/11/2026.
- SHA-256 de la descarga evaluada: `18911b578fd943d3fa45fd37b5bd23d40f05543e2a0f4db325e239458c044204`.
- Selección exacta del miembro: el XLSX con `división político-territorial` en el nombre. No se concatena con la otra estructura nacional homogénea del ZIP: sería un cambio de universo y una doble contabilización.
- Ciclos explícitos 2012–2013 a 2024–2025; 13 hojas. `period_start` y `period_end` son los años lectivos inicial y siguiente, tomados del nombre de hoja y guardados juntos. La convención de un año escalar de Tableau no se usa como contrato temporal universal.
- Las hojas cambian de posición de cabecera: el parser detecta una cabecera semántica única y valida columnas. Un diseño inesperado falla con diagnóstico; no selecciona datos por posición sin validar.
- Se conservan tasas publicadas, sin calcularlas a partir de población y sin sumar/promediar territorios. El denominador administrativo no está disponible en esta planilla de tasas. `aggregation=published_value_do_not_average_or_sum`.

## Resultado real de la ejecución

| Control | Resultado |
|---|---:|
| Celdas nativas | 5.265 |
| Observadas | 4.927 |
| Estructuralmente no aplicables | 338 |
| Celdas aplicables faltantes en esta edición | 0 |
| Valores negativos conservados | 767 |
| Ciclos | 13 |
| Unidades territoriales por ciclo | 27 |
| Filas de referencia Tableau conciliadas | 85 |
| Coinciden a una decimal (incluye 15 con conflicto temporal) | 84 |
| Coinciden sin conflicto temporal detectado | 69 |
| Conflictos temporales explícitos | 15 |
| Diferencia numérica adicional | 1 |

Las 27 unidades incluyen total nacional, 24 provincias/CABA y dos subdivisiones de Buenos Aires. Los 767 negativos no son 767 errores: la fuente explica el comportamiento del modelo; se conservan con su nota. Las celdas no aplicables no se convierten en ceros.

## Conciliación y hallazgos

Referencia de solo lectura: base maestra v1, workbook `3_3fMatrculaIEPromocinyabandono`, indicadores 380/381/382/383/384.

1. **MAPA primario (381) y secundario (383): 48/48 coincidencias** con el total provincial del ciclo 2024–2025, a precisión de un decimal.
2. **APERTURA 380 y 382: 15/15 valores coinciden numéricamente con 2024–2025, pero sus etiquetas dicen 2023/2024.** La referencia también tiene `ANIO=2024`. El adaptador registra el valor de ambos ciclos y clasifica `blocked_temporal_label_conflict`. No corrige la etiqueta ni aprueba la publicación basándose en coincidencia numérica.
3. **SERIE_TEMPORAL 384:** 21/22 filas coinciden al decimal. Para secundaria en 2023, la referencia dice 8,1 y el archivo oficial actual 2023–2024 contiene 8,04719453540115, que redondea a 8,0. Diferencia: -0,0528054646 puntos porcentuales. No se amplió la tolerancia para obtener un resultado verde. Puede tratarse de revisión/edición o transcripción; requiere confirmar la versión usada por Defe.

La comparación usa valor de visualización calculado desde `VALOR/VALOR_AUXILIAR *100` solo si la vista de referencia es MAPA; en las otras conserva VALOR. Tolerancia de media unidad del último decimal publicado: 0,05 puntos porcentuales. Esto es conciliación a precisión publicada, no identidad de numeradores, precisión original ni equivalencia estadística integral.

## Esquema nativo

Campos principales: `metric`, `period_start`, `period_end`, `period_label`, `geo_code`, `geo_level`, `geo_name`, `education_structure`, `level`, `grade_system`, `unit=percent`, `value`, `cell_status`, `observation_key` y procedencia de archivo/hoja/fila/columna/hash.

- `education_structure`: 6-6, 7-5 o mixed para el total nacional.
- `grade_system`: total, o grado/año acumulado del sistema de 12 años tal como en la hoja oficial. Primaria 7 solo es aplicable a 7-5; secundaria 7 solo a 6-6. Se preserva la estructura en cada territorio y período, sin convertir automáticamente a un año local de secundaria.
- `geo_code`: códigos provinciales INDEC como texto con ceros iniciales; `00` identifica el agregado nacional. `06-CON` y `06-REST` son claves **locales explícitas**, no códigos INDEC: Conurbano y Resto de Buenos Aires. Nunca se suman Buenos Aires y sus dos subdivisiones.
- `cell_status`: observed, missing o not_applicable. El archivo de esta edición no contiene celdas aplicables vacías; el esquema conserva esa posibilidad para ediciones futuras.
- `observation_key`: hash de métrica/ciclo/geografía/estructura/nivel/grado. Una revisión del valor conserva la identidad; un cambio dimensional produce otra clave.
- `release_status=candidate_not_approved`: todo registro es candidato. Aun las 69 coincidencias técnicas necesitan aprobación de reglas/uso.
- Se conservan las notas de cada hoja y las limitaciones del modelo. En 2024–2025 hay una nota específica sobre el nuevo régimen académico de Buenos Aires; debe mostrarse como cambio de comparabilidad, no omitirse en las series.

## Uso reproducible

Python 3.10+ y openpyxl 3.1 o compatible. No necesita pandas, Tableau, APIs pagas ni cuenta de servicio. El archivo original se descarga y conserva en la capa de adquisición; el adaptador consume la ruta local y no solicita credenciales ni realiza escrituras remotas.

```sh
python education_adapter.py \
  --source-zip /ruta/abandono.zip \
  --expected-sha256 18911b578fd943d3fa45fd37b5bd23d40f05543e2a0f4db325e239458c044204 \
  --reference-db /ruta/base_maestra.sqlite \
  --out /ruta/version-nueva

python -m unittest -v test_education_adapter.py
```

`--reference-db` y `--expected-sha256` son opcionales. Para reconciliar la edición evaluada, se recomienda fijar el hash. Un archivo nuevo requiere revisión y nuevo hash: no actualizar el pin silenciosamente. El destino debe ser nuevo o vacío para preservar salidas anteriores. La base de referencia se abre mediante URI `mode=ro`.

En el runtime usado aquí, el ejecutable es `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

Salidas: `native_candidate.json`, `native_candidate.csv`, `reconciliation.json`, `reconciliation.csv`, `summary.json` y `reconciliation_summary.json`. La salida vigente de esta entrega es `output-v2/`, producida también con Python optimizado (`-O`). `output/` y `output-v1/` son ejecuciones intermedias y no deben usarse como entrega definitiva.

## Pruebas

Seis pruebas unitarias con workbook sintético independiente: preservación de negativo/no-aplicable, rechazo de cabecera modificada, rechazo de dato en grado imposible, estabilidad de identidad ante revisión de medida bloqueo de conflicto temporal con detección de diferencia superior a la tolerancia y rechazo de esquema inválido con Python optimizado (`-O`). Las validaciones externas usan ValueError y no desaparecen con la optimización. Todas pasan. La ejecución completa con la fuente real también pasó controles de 27 unidades por ciclo, cabeceras, unicidad y tipos.

No se revisó una interfaz web ni se cambió su visualización, por lo que no se afirma aprobación de UX o cartografía. Para un mapa de este indicador usar `geo_level=province` y nivel/ciclo explícitos; el total nacional es el publicado, no promedio de las provincias. Grados y estructuras deben acompañar el tooltip y las comparaciones.

## Cierre y siguiente paso

Antes: descarga localizada y tres valores negativos comprobados manualmente. Después: adaptador ejecutable, 13 ciclos extraídos, 85 filas conciliadas y 16 bloqueos/diferencias explícitos. No hay PR ni despliegue en esta subentrega; el coordinador integrará código en una rama de trabajo.

Siguiente paso: acordar y versionar con Defe el período de las 15 aperturas y la edición histórica del único valor divergente, y recién entonces habilitar la publicación candidata del módulo de abandono.
