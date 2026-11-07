# LADEFE — Evaluación de verificación pública y actualización de tableros nativos

Corte de consulta: 6 de noviembre de 2026 (Argentina). Evaluación sobre 71 workbooks y 764 vínculos tablero–indicador de la base maestra v1. **Resultado: estrategia mixta viable; no corresponde prometer automatización integral ni equivalencia por el solo hecho de encontrar una fuente.**

## Qué se evaluó

Se cruzaron las fuentes declaradas de todos los tableros con publicaciones oficiales. La matriz adjunta cubre 71/71 tableros y agrupa el potencial por familia. Es una clasificación de factibilidad, no certificación individual de cada indicador. Se distingue: referencia institucional localizada, recurso abierto localizado, descarga y lectura comprobadas, valores contrastados y adaptador productivo. No se implementaron ni programaron actualizaciones, ni se cambió la base maestra.

## Comprobación independiente ya realizada

Los tres registros negativos de abandono interanual en el Tableau (año inicial 2024, indicador 381, nivel primario) coinciden con la planilla oficial **Tasa de Abandono Interanual 2025-2012 según división político-territorial.xlsx**, hoja **2024-2025**, columna C (Primaria — Total):

| Provincia | Valor de Tableau | Valor del archivo oficial | Coincidencia |
|---|---:|---:|---|
| Jujuy | -0,1 | -0,0500745554 | Sí, redondeado a un decimal |
| La Pampa | -0,1 | -0,1299132904 | Sí, redondeado a un decimal |
| Neuquén | -0,3 | -0,2763459852 | Sí, redondeado a un decimal |

La hoja Limitaciones explica que el modelo de flujo presupone un sistema cerrado; reincorporaciones y transferencias entre cohortes, territorios o instituciones pueden generar abandonos negativos o promoción superior a 100 %. Por lo tanto, estos tres casos quedan corroborados con la fuente; conservar valores y mostrar nota metodológica. Esto no aprueba automáticamente los otros 22 porcentajes educativos ni el conjunto de la interfaz.

Fuente: https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores
Archivo: https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip
La comparación de 2023-2024 se conserva también como evidencia de que el período importa: sus valores no son intercambiables con los de 2024-2025.

## Fuentes probadas por descarga y lectura

Se obtuvieron HTTP 200 y estructuras legibles para seis recursos oficiales. Los hashes SHA-256, URL y resultados están en pruebas_descarga.json.

| Recurso | Comprobación | Alcance y límite |
|---|---|---|
| Anuario Estadístico Educativo 2025 ZIP | Archivos XLSX de niveles, educación especial y otros capítulos presentes | No se reconciliaron todos sus cuadros con los 16 tableros RA. |
| DEIS defunciones 2024 CSV | Cabecera PROVRES, SEXO, CAUSA, MAT, GRUPEDAD, CUENTA | 54.251 filas de datos; edades agrupadas pueden impedir ciertos cortes exactos. |
| DEIS nacidos vivos 2024 CSV | Cabecera PROVRES, TIPPARTO, SEXO, IMEDAD, ITIEMGEST, IMINSTRUC, IPESONAC, CUENTA | 21.966 filas; no contiene edad materna simple para todo corte posible. |
| ISPI 2016–2024 XLSX | Paquete Excel válido y hojas presentes | Edición de octubre 2026; falta mapear cuadro y metodología de cada indicador. |
| GPSdN 2001–2024 XLSX | Paquete Excel válido y hojas presentes | Gasto social dirigido a niñez no equivale a gasto consolidado general. |
| Abandono interanual ZIP | Workbook, hojas de períodos y Limitaciones leídos | Tres valores cotejados; adaptador completo pendiente. |

## Matriz de viabilidad por familia

| Familia | Tableros | Verificación pública | Actualización propuesta |
|---|---:|---|---|
| RA e indicadores educativos | 16 | Alta: anuarios y series Excel oficiales; algunas aperturas necesitan acceso adicional | Candidata alta, anual por publicación; cambios de cuadros y microdatos restringidos requieren control. |
| Estadísticas vitales | 14 | Alta para cortes publicados; tasas requieren denominadores | Candidata alta, anual por edición; versionar residencia, causas y revisiones. |
| EPH / EPH total urbano y mixtos | 9 | Microdatos y documentación oficiales; hace falta reproducir universos y ponderadores | Media-alta condicionada: trimestre para EPH o tercer trimestre anual para EPHU; no sustituir una por otra. |
| Censo y cruces censales | 9 | Cuadros publicados y REDATAM, según cruce | Actualización eventual ante nuevos cuadros/revisiones/censo; no generar años nuevos por interpolación. |
| ANSES/BESS | 5 | Publicaciones nacionales y por jurisdicción | Media: conciliar personas, titulares, prestaciones, liquidaciones y distinta frecuencia territorial. |
| Encuestas especiales | 4 | EANNA 2016–2017, ENNyS2 2018–2019, discapacidad 2018 | Automatizar reprocesamiento y búsqueda de nuevas ediciones, no prometer una encuesta anual. |
| Cuidados y medidas de protección | 2 | Informes/relevamientos, incluyendo información propia de Defe/CNPT | Manual o semiautomática; aprobación temática y posible entrega institucional. |
| Justicia juvenil | 2 | Informes y algunos CSV históricos abiertos | Semiautomática; el CSV de flujo de aprehensión no sustituye stock de todos los dispositivos. |
| Inversión consolidada en niñez/primera infancia | 2 | Planillas oficiales GPSdN/ISPI | Media-alta por nueva edición; revisar imputaciones, población objetivo y series revisadas. |
| CUD / seguridad social | 2 | Referencias y tableros oficiales; equivalencia de cada corte no comprobada | Parcial, media-baja; puede requerir tabla institucional por edad y provincia. |
| Prestaciones alimentarias | 1 | Fuentes de programas/Mapa de Inversión Social | Media-baja hasta probar exportación y definición equivalente. |
| PAE | 1 | Portal actual con indicadores mensuales y catálogo histórico CSV | Media condicionada; comprobar exportación actual y revisar historia modificada. |
| Línea 102 | 1 | Portal actual mensual y catálogo histórico | Media condicionada; ausencias provinciales y homologación gradual deben conservarse. |
| Presupuesto nacional/infancia | 1 | Descargas abiertas y posibilidad de API | Media-alta: versionar clasificadores, marcado de infancia, etapa del gasto y deflactores. |
| Progresar | 1 | Referencia institucional; no se confirmó recurso abierto equivalente al tablero completo | Manual hasta encontrar descarga/entrega con cortes necesarios. |
| Migración administrativa / matrícula | 1 | RENAPER y RA | Media; población identificada no es población censada; edades quinquenales pueden impedir 0–17. |

Los **30 tableros** de RA/indicadores educativos y estadísticas vitales son el primer grupo de candidatos para diseñar adaptadores comunes. No significa que sus indicadores estén todos automatizados o puedan reproducirse desde una única tabla pública. La matriz contiene las condiciones de cada workbook.

## Qué hacer con las alertas de calidad

1. **Suma 101 % en migraciones EPHU:** chequeable en principio mediante microdatos del mismo tercer trimestre, universo y ponderador. Recalcular lugar de nacimiento y denominador, incluir faltantes como corresponda y comparar antes de sustituir. La EPH de 31 aglomerados no es una validación equivalente. No se calculó todavía este caso.
2. **Seis registros con años 2027–2029:** contrastar la rama de comedores con el RA y la rama de salud censal con cuadros del Censo. Los años futuros no quedan justificados por encontrar valores parecidos: debe coincidir el conjunto de dimensiones. Si la documentación no identifica el período, pedir aclaración a Defe. No se propuso un año sustituto.
3. **25 porcentajes educativos:** tres abandonos negativos corroborados con la planilla oficial. Los restantes requieren escolarización/egreso y documentación del indicador. Evitar reglas generales de recorte al intervalo 0–100.
4. **190 saltos interanuales:** automatizar comparación contra archivo oficial, detección de revisiones y cambios de denominador. El salto por sí solo no es error; prestar atención a cambios de programa, cobertura y clasificación.
5. **17 coberturas territoriales incompletas:** contrastar dominios de la fuente, regiones vs provincias, omisiones y confidencialidad. No exigir 24 jurisdicciones a cualquier encuesta ni convertir faltantes en cero.
6. **Documentación faltante:** las fichas públicas pueden completar definiciones y fórmulas, siempre vinculando fuente, edición y aprobación. Cuando el indicador es propio de Defe, una definición externa no lo reemplaza. No hay base para completar automáticamente los 353 campos faltantes de la auditoría.

## Diseño operativo recomendado

Separar dos niveles de automatización:

- **Adquisición y preparación:** descubrir novedades, descargar, conservar originales con hash, validar esquema y cobertura, calcular indicadores con reglas aprobadas y generar una versión candidata y su diferencia contra la anterior. Esto puede automatizarse ampliamente.
- **Publicación:** permitir avance automático solo para adaptadores ya validados, esquemas estables y controles aprobados. Cambios metodológicos, archivos inesperados, alertas o nuevas categorías deben quedar pendientes de revisión. Una descarga correcta no alcanza para publicar.

Controles de aceptación por adaptador: universo y edad explícitos; año/subperíodo correctos; geografía compatible; unidad y denominador documentados; conciliación contra una edición de Tableau y contra la fuente primaria; pruebas de revisiones históricas; ausencia de duplicados y huérfanos; conservación de faltantes; tolerancia de redondeo; manual de operación y responsable designado por la Defe. La licencia y condiciones de uso se deben registrar por recurso; acceso público no asegura licencia declarada.

Frecuencias candidatas: revisar fuentes mensuales al publicarse su período, EPH con cada entrega, EPHU una vez por edición anual, vitales y educación con cada edición anual; censos y encuestas especiales con nuevas publicaciones. Se puede comprobar semanalmente si hay archivos nuevos, pero esa frecuencia técnica no cambia la periodicidad de la estadística. No se creó ninguna tarea programada en esta evaluación.

Preservar un importador agregado CSV/XLSX para las entregas institucionales que no tengan publicación abierta. También puede mantenerse como respaldo la extracción de los Tableau públicos, identificándola como fuente derivada; no cuenta como validación independiente y no debe ser la dependencia principal del reemplazo nativo.

## Evidencias y límites de acceso

Los intentos de consulta al catálogo nacional a través del conector dieron errores de servidor o tamaño; se utilizaron páginas oficiales y descargas directas. No se concluyó que una fuente no exista solo porque falló el catálogo. No se solicitaron cuentas, tokens, accesos adicionales, servicios pagos ni se enviaron mensajes.

Las páginas actuales de PAE y Línea 102 describen periodicidad mensual, mientras que los registros históricos de Datos Argentina presentan otra periodicidad y cortes antiguos. Por eso se debe usar la edición y recurso realmente comprobados, sin confiar solo en la frecuencia declarada en un catálogo. ENNyS2 etiqueta actualización anual en el catálogo, pero el operativo localizado corresponde a 2018–2019; no se interpretó como una encuesta anual.

La ficha RENAPER localizada utiliza grupos quinquenales: no permite separar automáticamente 15–17 de 18–19. No se estimó esa separación. El acceso a algunas bases escolares finas está sujeto a mecanismos institucionales; los cuadros abiertos agregados no garantizan todas las aperturas del Tableau.

## Fuentes oficiales principales

- Educación: https://www.argentina.gob.ar/educacion/evaluacion-informacion-educativa/anuarios
- Indicadores educativos y metodología: https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores
- Acceso a datos educativos: https://www.argentina.gob.ar/capital-humano/educacion/informacion-y-evaluacion-educativa/datos-abiertos
- DEIS defunciones: https://www.argentina.gob.ar/salud/deis/datos/defunciones
- DEIS nacimientos: https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos
- INDEC bases: https://www.indec.gob.ar/Institucional/Indec/BasesDeDatos
- Censo: https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165?lang=es
- BESS: https://www.argentina.gob.ar/trabajo/seguridadsocial/bess
- ENNyS2: https://datos.salud.gob.ar/dataset/ennys2
- Inversión en niñez y primera infancia: https://www.argentina.gob.ar/node/230449 — documento 12, octubre 2026, hojas hasta 2024.
- Presupuesto abierto: https://www.presupuestoabierto.gob.ar/sici/datos-abiertos
- RENAPER: https://www.argentina.gob.ar/interior/renaper/transparencia/datosabiertos
- Detalle del recurso RENAPER: https://www.datos.gob.ar/ar/dataset/renaper-estructura-poblacion-origen-extranjero/archivo/renaper_4.1
- PAE actual: https://www.argentina.gob.ar/node/451503
- PAE histórico: https://www.datos.gob.ar/dataset/desarrollo-social-programa-acompanamiento-para-egreso-jovenes-sin-cuidados-parentales
- Línea 102 actual: https://www.argentina.gob.ar/capital-humano/familia/analisis-de-la-informacion-social/area-central-linea-102
- Línea 102 histórico: https://www.datos.gob.ar/dataset/desarrollo-social-linea-102
- CUD: https://www.argentina.gob.ar/andis/estadisticas/datos-estadisticos
- Protección: https://www.argentina.gob.ar/noticias/el-ministerio-de-capital-humano-comienza-el-relevamiento-federal-de-ninos-y-adolescentes
- Justicia juvenil: https://datos.gob.ar/fr/dataset/desarrollo-social-dispositivos-aprehension-especializados-para-adolescentes-presuntos-infractores

## Prioridad y próximo paso

Primero desarrollar un adaptador de indicadores educativos con el caso de abandono ya cotejado. Segundo, vitales DEIS, cerrando denominadores y edades. Tercero, EPHU para reconstruir el 101 % de migraciones con el universo correcto. Después BESS e inversión en niñez, dejando las fuentes institucionales y encuestas discontinuas con un flujo editorial.

El próximo paso concreto es implementar y validar el adaptador educativo sobre el Excel oficial y una muestra equivalente de Tableau. Esta entrega es la evaluación y especificación previa, no la puesta en producción del adaptador.
