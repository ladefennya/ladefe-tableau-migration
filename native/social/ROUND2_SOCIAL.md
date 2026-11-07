# Revisión social/económica — Segunda ronda

## Decisión

Se sostiene el bloqueo de sustitución automática del indicador 1048. La discrepancia del 101 % fue contrastada con dos ediciones oficiales justificadas por la fecha del indicador y la posibilidad de rezago de publicación: EPH total urbano 3T2025 y la edición inmediatamente anterior 3T2024. Ninguna reproduce la terna del Tableau. No se buscó un conjunto arbitrario de filtros/ponderadores que hiciera coincidir los valores.

## Evidencia independiente

| Fuente y población total, respuestas válidas a CH15 | Misma provincia | Otra provincia | Otro país |
|---|---:|---:|---:|
| Tableau: año declarado 2025 | 87,3 % | 10,1 % | 3,6 % |
| EPHU 3T2025, PONDERA | 86,470277 % | 9,973530 % | 3,556193 % |
| EPHU 3T2024, PONDERA | 85,718137 % | 10,502053 % | 3,779809 % |

2025: 71.322 registros de personas; expansión total 43.337.370. 2024: 75.211 registros; expansión total 42.936.914. Las dos fuentes son EPH total urbano, no EPH de 31 aglomerados. Las políticas de Ns/Nr fueron definidas antes de la comparación: mantener la categoría explícita o excluirla del denominador de las tres categorías conocidas. Ambas están publicadas como candidatas; ninguna política explica el 101 %. La terna del Tableau excede también el error máximo de redondeo a un decimal de una partición de tres categorías (0,15 puntos).

Los valores de 2024 se entregan solamente como **diagnóstico entre períodos distintos**. Aunque algún valor coincidiera, eso no aprobaría equivalencia con un registro etiquetado 2025. El adaptador lo deja como `not_equivalent_period` en cada comparación.

## CH15, ponderador y edad

El diseño oficial de 2025 documenta CH15: 1/2 son localidades dentro de la provincia de residencia; 3 otra provincia; 4/5 extranjero; 9 Ns/Nr. La sección de factores de expansión indica PONDERA para variables no monetarias; los ponderadores de ingresos no se utilizaron para esta composición.

Se descargó además el **XLSX oficial del diseño de registros 2025**, 59.996 bytes. La hoja Personas, fila 126, describe CH06 como años cumplidos, sin una etiqueta explícita para el código -1. El PDF consultado tampoco la explicita. Un material educativo externo interpreta -1 como menor de un año, pero no se utilizó para cerrar el requisito de fuente primaria pedido por esta revisión.

Por lo tanto, el significado de -1 queda **pendiente de confirmación documental primaria**; no se lo considera un faltante ni se lo imputa automáticamente a cero. Las salidas infantiles quedan marcadas `child_age_semantics=sensitivity_not_approved`, `domain_status=age_semantics_pending`. Se entregan sensibilidades con y sin ese código. La comparación de población total no depende de esa decisión. No se deduce edad exacta de fechas de nacimiento incompletas ni se hace una corrección por parecido de valores.

## Endurecimiento del adaptador

El adaptador copiado del repo fue revisado en un directorio aparte, sin modificar repo ni SQLite original. Nuevas garantías:

1. `source_registry.json` fija edición, URL, SHA-256, cantidad de bytes, nombre del miembro de personas, hash del orden de columnas, cantidad de registros y expansión total para 2024/2025. Un archivo distinto requiere revisar y versionar el perfil; no se asigna procedencia oficial a cualquier ZIP que tenga un nombre compatible.
2. Validaciones explícitas `ValueError`, activas también con Python `-O`: año/trimestre, estructura, columnas duplicadas o filas incompletas, claves vacías/duplicadas, provincia, código CH15, edad, entero y positividad del peso, denominador y partición de numeradores.
3. CH15 desconocido, NA o fuera de dominio falla; no se recodifica como cero. Edad 999 es un estado separado soportado como potencial desconocido del formato de tres dígitos, no una edad infantil. En las dos ediciones examinadas no aparece. No se interpreta 99 automáticamente como faltante en un campo de tres dígitos.
4. La conciliación exige las seis combinaciones conocidas de población/categoría del Tableau y valida alcance nacional, vista y período. Una etiqueta nueva no se asigna por `else` a otro universo.
5. Tolerancia de comparación de un decimal calculada mediante Decimal y medio intervalo de 0,05 puntos; sin `round()` binario ni ajuste oportunista. Coincidencia numérica y elegibilidad metodológica son estados distintos.
6. Cada registro candidato incluye año real, URL y hash de la edición, dominio, estado de incertidumbre y aprobación. `uncertainty_status=not_estimated_design_required`: este adaptador no estima errores de muestreo ni habilita mapas provinciales.
7. El destino debe ser un directorio nuevo, incluso si uno existente está vacío. Todos los controles de fuente y referencia preceden a crear el destino. Escrituras exclusivas y `completion.json` al final distinguen resultado completo de una eventual ejecución interrumpida. No hay publicación automática.

## Pruebas

- 14 pruebas unitarias aprobadas.
- Incluyen pesos y faltantes, sensibilidad etaria explícita, rechazo de políticas desconocidas, códigos nuevos, pesos cero/negativos/no enteros, identidad duplicada, año/trimestre incompatibles, conteos/pesos del perfil, SHA cambiado, directorio existente y bordes exactos de tolerancia decimal.
- Prueba de falla bajo Python `-O` sobre un archivo no registrado: falla antes de crear salida.
- Corrida real 2025 con Python `-O`: 71.322 registros, 21 agregados candidatos, 12 comparaciones; 6 coincidencias de un decimal, ninguna aprobación de publicación.
- Corrida real 2024 con Python `-O`: 75.211 registros, 21 agregados, 12 comparaciones con la referencia 2025; cero coincidencias y todos los casos `not_equivalent_period`.

Las cifras del adaptador no son estimaciones de precisión muestral; son verificaciones de composición y procedencia. No se publicaron microdatos ni se guardaron personas identificables en las salidas de revisión.

## Revisión cruzada de otros adaptadores

### Educación

Se observó que la versión del repo asignaba nivel secundario por descarte para ciertas etiquetas del indicador 384 y que una geografía ausente podía transformarse en código nacional 00. Se comunicó el riesgo al agente educativo: corresponde una lista explícita de modalidades y evidencia de alcance nacional antes del reemplazo. El agente informó la incorporación de whitelist de grados/modalidades y validación de alcance. No se editaron sus archivos ni se certifica aquí su revisión final.

La convención de período educativo debe conservar año inicial y final y separar la coincidencia de valor de una contradicción en la etiqueta. No ampliar tolerancia para ocultar la diferencia. Un doble redondeo solo es una explicación aceptable si el formato/valor visible de la fuente lo demuestra; debe registrarse como tal y no equipararse a igualdad de los componentes originales.

### Salud

Se observó que las condiciones `!=9` para peso y `!=8` para gestación podían contar una categoría nueva/desconocida como denominador válido. También una nueva codificación de edad infantil podía omitirse. Se propusieron conjuntos positivos de categorías conocidas, fail-closed de dominios, validación de archivos no vacíos y conservación de desconocidos. El agente de salud informó que incorpora esos controles y distingue sexo observado no documentado sin atribuirle género.

La igualdad de numeradores/denominadores es evidencia más fuerte que la semejanza de porcentajes. Los 120+1 casos conciliados no certifican la totalidad de los 14 tableros, ni permiten desagregar 15–19 a 15–17.

## Fuentes y trazabilidad

- Portal oficial: https://www.indec.gob.ar/Institucional/Indec/BasesDeDatos
- EPHU 2025: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_Tot_Urbano_3T_2025.zip
- EPHU 2024: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_Tot_Urbano_3T_2024.zip
- Diseño PDF: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_tot_urbano_estructura_bases_2025.pdf
- Diseño XLSX: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_tot_urbano_estructura_bases_2025.xlsx

Los hashes del ZIP2024/2025 y los perfiles están en `source_registry.json`; la descarga del XLSX está registrada en `codebook2025_source.json`. Las fuentes originales de trabajo permanecen en scratch, fuera del entregable agregado.

## Reproducción

```sh
python -m unittest discover -s . -p 'test_*.py'
python -O ephu_migration_adapter.py --input /ruta/EPH_Tot_Urbano_3T_2025.zip --source-year 2025 --database /ruta/base_maestra.sqlite --out /ruta/nueva-salida-2025
python -O ephu_migration_adapter.py --input /ruta/EPH_Tot_Urbano_3T_2024.zip --source-year 2024 --reference-year 2025 --database /ruta/base_maestra.sqlite --out /ruta/nueva-salida-2024-diagnostica
```

Próximo paso: recuperar de la Defe el procesamiento/versión original del indicador 1048 y una documentación primaria de la convención de edad. No se reemplaza la terna de Tableau ni se asigna un año distinto por inferencia.
