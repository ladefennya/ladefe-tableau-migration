# LADEFE — Base maestra y control de calidad, versión 1.0.0

**Veredicto: apta con reservas para desarrollar los 71 tableros nativos; pendiente de revisión estadística y temática para publicación.** Corte de extracción: 6 de noviembre de 2026. Versión del repositorio de comparación: 371aaae89c8a91b499d6fac20aec6ff49da376e3.

## Resultado

Se creó una base SQLite consultable con 71 tableros, 14.156 observaciones seleccionadas y 764 vínculos tablero–indicador. Se preservan los valores y auxiliares originales, la sección, período, geografía y todas las aperturas. Las claves incluyen workbook y dimensiones: ningún ID de indicador de otro archivo sobrescribe su versión. Los seis catálogos/tablas originales por workbook se conservan mediante 973.514 asociaciones de procedencia a payloads JSON deduplicados, recuperables sin pérdida. La deduplicación física no altera la multiplicidad por workbook/tabla.

El esquema separa valor original, auxiliar y valor de visualización. Solo para MAPA aplica la regla de Tableau documentada (cantidad o ratio con factor). Las otras vistas conservan el valor de la fuente; no se mezclan dimensiones ni se suman porcentajes. La compatibilidad de un índice o tasa y la agregación entre varias observaciones requieren configuración explícita y validación. No se reconstruye por heurística qué serie acompaña a qué mapa.

La versión es una instantánea identificada por fecha, versión, hashes de los 71 archivos de extracción y commit de comparación. Las futuras ejecuciones deben producir otra carpeta; el constructor rechaza sobrescribir una base existente. Se entrega el registro de diferencias contra el demo histórico, no un historial completo de todas las versiones que haya publicado la Defe.

## Cambios respecto de GitHub

Hay diferencias en 10 tableros. La reconciliación por dimensiones identifica 326 modificaciones de valor o auxiliar, 1.288 altas y 1.148 bajas. Las altas/bajas son diferencias entre conjuntos: también pueden corresponder a cambios en etiquetas, aperturas o períodos, y no equivalen necesariamente a nuevas observaciones estadísticas. La diferencia neta es de 140 filas (14.016 a 14.156). No se fusionaron series heterogéneas ni se borró la copia anterior.

## Hallazgos concretos

| Estado | Resultado | Tratamiento |
|---|---|---|
| Revisión temática | 1 combinación de categorías suma 101 % | Migraciones urbanas, indicador 1048, año 2025, apertura «Población urbana»: 87,3 % en la provincia donde vive + 10,1 % en otra provincia + 3,6 % en otro país. Diferencia de 1 punto; verificar fuente y universo. No ajustar a 100. |
| Revisión temática | 25 observaciones porcentuales fuera de 0–100 | Indicadores educativos: 17 de escolarización, 5 de egreso y 3 de abandono. La fuente explica que ciertas tasas pueden superar 100 por diferencias entre numerador y denominador; no se consideran automáticamente errores. Revisar cada familia y conservar nota explicativa. |
| Revisión temática | 190 cambios interanuales superiores a 50 % | Solo se comparan años consecutivos de la misma combinación dimensional y subperíodo. Son alertas exploratorias, no pruebas de error ni estimación de significación. No se imputan años ausentes. |
| Revisión temática | 17 combinaciones de mapa tienen menos de 24 jurisdicciones | Revisar si el universo corresponde a todo el país, si hay provincias sin dato o si se trata de una exclusión legítima. Nunca convertir ausencia en cero. |
| Revisión temática | 6 registros con años 2027–2029 | Aparecen en establecimientos que entregan comidas y en cobertura de salud censal. No hay en este control acreditación de que sean proyecciones: requieren aclaración del período y no deben presentarse como observaciones realizadas. |
| Advertencia documental | 213 vínculos sin definición útil, 127 sin metodología útil y 13 sin fórmula útil | Control semántico: cadenas como «---» no son documentación. Son 353 incidencias de campos, no 353 indicadores distintos. Conservar texto original, registrar faltantes y solicitar aclaración temática. |
| Informativo | 533 valores fuera de 0–100 corresponden a índices/variaciones según el nombre o fórmula | Se separaron de las alertas de porcentajes. Esta clasificación textual solo orienta la revisión: no aprueba fórmulas ni cambia la unidad declarada por la fuente. |

La revisión anterior de campos vacíos había informado cero fórmulas faltantes. Al comprobar también contenido formado únicamente por signos, se detectaron 13 fórmulas sin información útil. La misma mejora explica el aumento de faltantes metodológicos respecto del control anterior. Este informe reemplaza esas métricas preliminares.

Las alertas de revisión suman 239 y pueden solaparse en una observación. No se encontró un error estructural que obligue a descartar los datos; eso no certifica que todas las estadísticas sean correctas.

## Pruebas ejecutadas y límites

- Integridad SQLite y claves foráneas: aprobadas.
- Conservación exacta de los valores originales y auxiliares en las 14.156 observaciones: aprobada.
- Igualdad de las seis tablas originales por cada uno de los 71 workbooks contra los JSON de extracción, y hashes de los 71 archivos: verificación independiente en verification.json.
- No hay claves dimensionales duplicadas en la selección; el índice primario bloquea su inserción.
- No hubo valores no finitos ni cálculos MAPA imposibles en las reglas ejecutadas.
- Se evaluaron 277 conjuntos candidatos de categorías porcentuales; uno excede la tolerancia exploratoria de suma (máximo entre 0,5 puntos y 0,01 por categoría). La tolerancia no reemplaza la precisión real de publicación ni demuestra exhaustividad de categorías.
- **No se pudo cerrar la reconciliación de total nacional contra 24 provincias:** las combinaciones MAPA seleccionadas no contienen simultáneamente ambas cosas. Se informa cero comparaciones realizadas; no se declara este control aprobado. No se vincularon otros indicadores por parecido de nombres para suplirlo.
- El diccionario conserva fuente, definición, fórmula, metodología y unidad por vínculo; ausencia documental no se completó por inferencia.
- No se revisaron todos los filtros renderizados ni se cerró la equivalencia funcional de los seis arquetipos. No se auditó si el sitio institucional incorporó workbooks fuera del inventario de 71. No se publicaron cambios en GitHub o en el sitio.

## Archivos y uso

- base_maestra.sqlite: fuente de desarrollo y evidencia; tablas snapshots, boards, indicators, groups_catalog, observations, source_payloads, source_records (vista de procedencia) y findings; vista native_data con nombre, unidad y fórmula.
- diccionario_indicadores.csv: 764 vínculos, con fuentes y faltantes explícitos.
- diccionario_campos.md: significado de las 22 columnas de Datos y reglas de cálculo.
- cobertura_71.csv: tablero, períodos, cantidad de indicadores y registros.
- cambios_vs_github.csv: diferencias con valores y dimensiones de antes/después.
- hallazgos.csv: regla, clasificación, tablero, indicador, clave y evidencia.
- manifest.json, resumen.json, verification.json: versión, procedencia y resultados.
- build_master.py, finalize_audit.py y verify_master.py: controles reproducibles con Python estándar, sin servicios pagos.
- source_downloads.json y config_workbooks.csv: hashes de los paquetes públicos descargados e inventario de origen.
- geometria/: geometría provincial histórica validada contra la extracción actual en el respaldo previo; no se certifica aquí la presentación cartográfica.

Consulta de ejemplo:

```sql
SELECT workbook, indicator_name, view_type, year, period, geo_name,
       value_raw, auxiliary, value_display, unit
FROM native_data
WHERE workbook = '2_2bAUH' AND indicator_id = '218';
```

Para reproducir con los JSON originales del respaldo de extracción anterior:

```sh
python build_master.py --sources /ruta/source_tables --repo /ruta/ladefe-tableau-migration --out /ruta/nueva-version
python finalize_audit.py /ruta/nueva-version
python compact_master.py /ruta/nueva-version
python verify_master.py /ruta/nueva-version /ruta/source_tables
```

Se requieren el repo en el commit de comparación y los 71 JSON comprimidos originales. También pueden reconstruirse los objetos JSON desde source_records JOIN source_payloads, aunque la recompresión puede cambiar el hash binario del gzip sin alterar sus datos. No se requieren los 311 MB de paquetes originales para consultar esta base. Estos paquetes y las reglas XML están referenciados o preservados en el respaldo de validación anterior.

## Criterio de publicación y próximo paso

Mantener las alertas abiertas hasta documentar explicación, corrección de fuente o exclusión explícita del uso publicado. No ocultarlas para obtener controles verdes. Prioridad: aclarar los seis períodos futuros y el 101 %; después revisar los 25 porcentajes y completar los 13 casos sin fórmula. El próximo paso técnico es cerrar los seis arquetipos contra Tableau renderizado y trasladar las reglas aprobadas al motor nativo, con supervisión temática de la Defe.
