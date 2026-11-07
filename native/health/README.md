# Salud: adaptador DEIS y conciliación independiente

Estado: **prueba técnica validada para un subconjunto de 2024; datos candidatos, no publicación ni equivalencia integral.** Los datos fuente y la base maestra permanecen sin modificaciones.

## Resultado reproducido

Se leyeron 21.966 filas de nacidos vivos y 54.251 de defunciones de los CSV oficiales 2024. Totales de los archivos completos: 413.135 nacidos vivos, 376.405 defunciones y 3.513 defunciones de menores de un año. Son sumas de registros agregados; incluyen los códigos territoriales no provinciales 98 y 99. Se conservan fuera del mapa, no se redistribuyen ni se convierten a cero.

**121 de 121 comparaciones coinciden exactamente en sus componentes**:

- 24 provincias × 3 indicadores de mortalidad infantil/neonatal/postneonatal (86, 87, 102; workbook `4_3 aMortalidadinfantilTasas`): 72 numeradores y denominadores.
- 24 provincias × 2 indicadores de bajo peso y pretérmino (23, 24; workbook `4_2 bNatalidadNacidosvivos`): 48 numeradores y denominadores, usando denominadores válidos para cada variable.
- Total nacional de nacimientos 2024, indicador 474 de `4_2 aNatalidad`: 413.135 (solo la apertura Cantidad de nacimientos, no el índice base 100).

En ronda 2 se cotejó además la razón materna anual 2024: 183 muertes M/413.135 nacidos vivos ×10.000 =4,4295448, que coincide con4,4 de Tableau al redondear a un decimal; las81 maternas tardías T no ingresan al numerador. Este caso se reporta separado de los121 componentes. No se cotejaron los demás años o interacciones. El total de muertes del CSV es una suma reproducida, no una cifra validada aquí contra el cuadro oficial publicado. El nombre de archivo no permite concluir automáticamente si los datos corresponden al año de registro u ocurrencia; esa metadata debe completarse desde las consideraciones DEIS.

## Hallazgo semántico relevante

La fórmula textual de los indicadores 23 y 24 en Tableau menciona «total de nacidos vivos». Sin embargo, sus auxiliares coinciden exactamente con:

- Bajo peso: nacidos vivos con **peso especificado**, excluyendo `IPESONAC=9.Sin especificar`.
- Pretérmino: nacidos vivos con **gestación especificada**, excluyendo `ITIEMGEST=8.Sin especificar`.

Ejemplo CABA: 21.454 nacidos vivos totales; 21.408 con peso conocido; 21.405 con gestación conocida. Los dos denominadores no son intercambiables. La prueba empírica no sustituye una aprobación temática de la definición; el adaptador entrega ambos tipos de porcentaje (sobre todos y sobre especificados) y la conciliación declara el denominador usado. Debe incorporarse la ficha/metodología oficial de la edición 2024 antes de promover el candidato. Se preserva el antecedente 2023, pero ahora la nota de peso está documentada también en la edición oficial 2024.

Durante el desarrollo, el contraste detectó un error del parser experimental: inicialmente omitía 2.000–2.499 gramos del numerador de bajo peso. Se corrigió; un test de borde lo cubre. No se modificó ninguna fuente para hacerla coincidir. Esto muestra por qué la conciliación debe comparar numeradores/denominadores y no solo porcentajes redondeados.

## Contrato de datos y restricciones

- `PROVRES` se mantiene como texto de dos caracteres. Geografía: residencia; no confundir con lugar del evento o establecimiento. Los códigos no provinciales no son polígonos del mapa.
- `CUENTA` es un conteo agregado no negativo. No se interpreta cada fila como una persona.
- Defunciones: se preservan sexo, grupo de edad original, `CAUSA` CIE-10 de tres caracteres y marca materna original `MAT`. No se inventa el cuarto carácter CIE ni se agrupan causas sin una clasificación aprobada/versionada. El diccionario descargado identifica MAT=M materna,T tardía,S secuela,Nulo no materna; PDF2024 página29 excluye T de la razón materna.
- Menores de un año incluye el grupo de edad infantil no especificado; este último no se asigna a neonatal o postneonatal. Se comprueba `infantil = neonatal + postneonatal + infantil_sin_edad_precisa`.
- Las edades 15–19 no permiten producir un corte 15–17. Del mismo modo, «menores de 15» materno no se declara automáticamente idéntico a 10–14 sin definición explícita.
- Bajo peso incluye todas las categorías bajo 2.500 gramos, incluidas 2.000–2.499. Pretérmino comprende menos de 37 semanas. Se conserva el faltante como una dimensión de calidad.
- Tasa de natalidad requiere población total del mismo año y jurisdicción. Fecundidad adolescente requiere población femenina por edad compatible. Esos denominadores no se infieren de nacimientos ni se fabrican en esta prueba.
- Mortalidad materna anual y trianual son medidas distintas. El indicador 72 de Tableau usa trienio 2022–2024, por lo que no se lo compara con un único CSV 2024. Su nombre incluye «(%)» pero la unidad/formula es razón por 10.000 nacidos vivos: debe revisarse el rótulo.
- La unidad genérica de Tableau «por 1.000 habitantes» no describe correctamente el denominador de las tasas infantil/neonatal/postneonatal: la fórmula usa nacidos vivos. El modelo nativo necesita un campo `denominator_universe`, no solo un código numérico de unidad.
- No se propone localizar domicilios de niñas/os, madres o eventos individuales. La salida es agregada por jurisdicción; denominadores pequeños y eventos raros requieren advertencia, estabilidad temporal y/o agrupación aprobada.

## Ejecución portable

Python 3, solo biblioteca estándar. El CLI no necesita conexión de red y recibe rutas explícitas. La salida debe ser nueva o vacía; nunca pisa otra versión. Las verificaciones usan excepciones explícitas y funcionan también bajo `python -O`.

```sh
python vital_adapter.py \
  --births /ruta/nacimientos_2024.csv \
  --deaths /ruta/defunciones_2024.csv \
  --reference-db /ruta/base_maestra.sqlite \
  --expected-births-sha256 ac0 ac5 ff8794 f73 c57 a02 b494 b97401431 ce901 d4 f5 f0 a5 df877 f372 da9 d85 d2 \
  --expected-deaths-sha256 9 b31 baa9 fb577 f7 c95 fd5 b159695 a1 b970 fa2 a2 b1811 f5 cd5015 cd03370 bae5 a \
  --out /ruta/candidato-deis-2024-nuevo
python -m unittest -v test_vital_adapter.py
```

Está fijado a la estructura y categorías 2024. Para otro año hay que revisar contrato, diccionario y fecha, en lugar de cambiar silenciosamente el año. El lector rechaza esquema, geografía, conteos y codificación CIE inesperados. Los hashes 2024 se fijan por defecto: un CSV distinto (incluso de otro año con igual esquema) se rechaza antes de crear salida. Los argumentos esperados no permiten saltar la lista de hashes aprobados del contrato: una nueva revisión requiere versionar y revisar release_contract_2024.json; cambiar el parámetro esperado por sí solo falla.

Salidas: `candidate.json` (agregados provinciales); `province_aggregates_2024.csv`; `death_dimensions_2024.csv` (grupos completos, no recomendado para Git); `reconciliation.csv`; `reconciliation_summary.json`. La evidencia compacta para versionar está en `evidence/`: resumen y muestra, no los CSV completos. El esquema primario es una fila por `year + province_code` para los agregados, y por `year + province_code + sex_code + age_group_source + cause_icd10_3 + maternal_flag_source` para defunciones dimensionales.

Pruebas: 16 unitarias aprobadas; cubren peso de borde, faltantes, edad infantil no especificada, geografía no mapeable, ausencia de tasa poblacional fabricada y rechazo de esquema normal/optimizado y rechazo de archivo no fijado antes de etiquetarlo 2024. La prueba con datos reales y DB es adicional: 121/121 componentes exactos. No son pruebas visuales ni aceptación de producción.

## Propuesta de organización y visualización de salud

1. Organizar por pregunta: nacimientos y condiciones perinatales; mortalidad infantil; salud materna; adolescencias; nutrición/lactancia. Evitar mezclar en un único selector medidas de población, eventos y factores de riesgo.
2. Separar «cuántos eventos» de «qué riesgo/tasa»: conteos con símbolos proporcionales o barras; tasas/proporciones con mapa coroplético y escala común entre períodos, acompañados por numerador, denominador y calidad del dato.
3. Para mortalidad materna y causas raras no ofrecer ranking de provincias como lectura por defecto. Mostrar intervalos/estabilidad temporal cuando sea metodológicamente posible, trienios claramente rotulados y advertencia para conteos pequeños.
4. Nutrición y lactancia ENNyS2: vistas por dominio de representatividad de encuesta, no mapa provincial inventado. El enlace territorial debe inhabilitarse si la muestra no lo respalda.
5. Mostrar siempre edad exacta o grupo, fecha de referencia, denominador y exclusión de faltantes; ofrecer alternancia tasas/conteos solo cuando exista misma medida y universo.

## Fuentes y aceptación pendiente

- CSV nacimientos 2024: https://www.argentina.gob.ar/sites/default/files/2021/03/datos_sobre_nacidos_vivos_2024.csv
- CSV defunciones 2024: https://www.argentina.gob.ar/sites/default/files/2021/03/datos_sobre_defunciones_2024.csv
- Páginas y diccionarios: https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos y https://www.argentina.gob.ar/salud/deis/datos/defunciones
- Antecedente metodológico 2023, Cuadro 6: https://www.argentina.gob.ar/sites/default/files/serie_5_nro_67_anuario_vitales_2023-version_final.pdf
- ENNyS2: https://datos.salud.gob.ar/dataset/ennys2

Siguiente paso: aprobar temáticamente los denominadores explícitos (peso ya respaldado por nota2024; gestación pendiente), resolver la semántica de SEXO=3 y luego extender conciliación a series históricas y probar estas cinco medidas sobre la interfaz nativa renderizada. No hay PR ni publicación desde este subtrabajo. La ronda2 solo modifica la copia ladefe-team-round2/health.


## Segunda ronda: contrato v2 y puertas de publicación

`release_contract_2024.json` es obligatorio junto al script. Incluye los dominios completos observados en la edición fijada y el MAT=S documentado. Se rechazan nuevos códigos/cadenas de peso, gestación, edad, sexo o localidad; los denominadores válidos usan conjuntos positivos de códigos, nunca «todo salvo NS». Los códigos de edad infantilsin especificar no se redistribuyen. Dos archivos diccionario oficiales presentan omisiones: no definen el SEXO=3 observado (6 nacimientos y10 defunciones) y describen separador coma, mientras estosCSV usan punto ycoma. La salida conserva código3 sin asignarle identidad ni excluirlo de totales; los desgloses por sexo requieren aclaración. No se identifica esta diferencia como una falla del registro original por sí sola.

`provenance.json` añade hashes de adapter, contrato y base de comparación; `output_manifest.json` contiene hashes de todos los archivos emitidos, salvo sí mismo. El conjunto de salida es inmutable por versión. Las salidas completas finales de esta ronda se generaron en `/tmp/ladefe-deis-round2-final`, fuera del repo; evidencia compacta en `evidence/`.

Puertas: 97 casos (72 componentes infantiles,24 de peso y1 nacimiento nacional) tienen conciliación más documentación primaria pertinente, pero aún requieren revisión temática y de la interfaz;24 porcentajes pretérmino tienen conciliación empírica y permanecen pendientes de aprobación del denominador. La razón materna anual es1 comparación adicional a un decimal, no se agrega como si fuera otro match exacto de numerador/denominador de Tableau. Nada queda marcado publicado.
