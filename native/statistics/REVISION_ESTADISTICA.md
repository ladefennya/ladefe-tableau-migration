# Revisión estadística crítica de la base maestra LADEFE

Evaluación del 6 de noviembre de2026. Fuente examinada: SQLite de solo lectura /workspace/scratch/e1753b36d366/ladefe-master-v1/base_maestra.sqlite, instantánea2026-11-06; XML descargados del mismo corte, documentos y código del repo371aaae89c8a91b499d6fac20aec6ff49da376e3. Veredicto: **apta para desarrollo y preservación; no equivale todavía a base semántica certificada para publicación de71 tableros**.

## Hallazgos principales

| Prioridad | Hallazgo | Evidencia reproducible | Decisión |
|---|---|---|---|
| Bloquea vista temporal afectada | La alerta de seis años futuros oculta un problema de contrato temporal más amplio | evidence.json contiene20 filas APERTURA de dos indicadores. Salud789: ANIO2022…2029 secuencial pero dimensión explícita Año Censal2010/2022. Comedores465: ANIOvaría con nivel/ámbito, no como serie | No tratar ANIO como reference_period universal. No llamar pronósticos a esos registros. Conservar datos y derivación curada pendiente. |
| Bloquea agregaciones no definidas | Coincidencia por fila no demuestra equivalencia de las marcas Tableau | Los XML de71 workbooks usan AVG(VALOR) en vistas de datos directos. Ver evidence.json/tableau_avg_shelves | Validar LOD, dimensiones y filtros. No escalar AVG a territorios o categorías; permitir dato directo solo al nivel aprobado. |
| Bloquea mezcla global | Identificador de indicador no es globalmente inequívoco |164 IDs tienen distintas versiones de metadata_json entre workbooks | La separación por workbook/snapshot actual es acertada; falta aprobar correspondencias conceptuales entre versiones. |
| Revisión temática focalizada | Suma101% en migraciones urbanas | Indicador1048, año2025, distribución Población urbana:87,3+10,1+3,6. El control alternativo con tolerancia de redondeo0,05×3 mantiene el mismo único candidato entre277 conjuntos | Si categorías son exhaustivas/excluyentes, el exceso no es redondeo. Reproducir EPHU del mismo período y universo. No reescalar automáticamente. |
| Riesgo de interpretación | El porcentaje de alertas no es porcentaje de errores |239 alertas de revisión pueden solaparse;190 son saltos exploratorios. Los533 casos índice/variación se clasificaron por texto | Mantener estados y decisiones por regla/observación; no afirmar que533 índices quedaron certificados. |
| Límite de comprobación | Total nacional vs24 provincias no fue reconciliado | La auditoría reporta0 comparaciones. No hay total nacional compatible en las combinaciones MAPA seleccionadas | No declarar el control aprobado; buscar fuente/indicador de total solo mediante relación explícita aprobada. |
| Límite de preservación | El hash de dimensiones de la base cambia ante cambios de etiqueta | observation_key incluye todas las etiquetas de las dimensiones | La procedencia es estable dentro del corte, pero alta/baja de la comparación no implica alta/baja de una observación conceptual. Añadir identidad semántica curada. |

## Qué sí sostiene la evidencia

-71 workbooks y14.156 observaciones en el corte seleccionado.
- No se repite ID_DATO_SM dentro de cada workbook en la selección; la lista reproducible de duplicados está vacía.
- La distribución de vistas del corte actual es APERTURA2847, DISTRIBUCION939, MAPA4065 y SERIE_TEMPORAL6305.
- Hay15 filas no MAPA con auxiliar. Tener ese dato no autoriza un ratio; el tratamiento directo por vista actual evita recalcular índices o magnitudes ya expresadas.
- No hay denominadores no positivos en las filas clasificadas ratio_mapa del corte actual.
- EPH/EPHU, censos, registros administrativos y encuestas especiales no comparten automáticamente población, período, edad o dominio territorial.

Las cifras anteriores corresponden a la base actual, no a los4017registrosMAPA del demo histórico que se compararon en la auditoría inicial. No mezclar denominadores entre esas versiones.

## Correcciones necesarias a la interpretación de auditorías previas

1. «Tiene toda la información necesaria» debe limitarse al contenido recuperado de71 workbooks conocidos; no acredita todos los insumos primarios, incertidumbre muestral ni criterios editoriales. Es evidencia de factibilidad, no certificación estadística completa.
2. «Seis años futuros» es una descripción de raw_year, no de período estadístico real. Son seis filas dentro de20registros cuya semántica temporal merece resolución. En salud hay prueba interna explícita de años censales2010/2022; no hay evidencia de proyecciones2027–2029.
3. Las comparaciones por fila de mapa y reglas internas no son validación renderizada de todas las combinaciones ni verificación de todas las fuentes primarias. La etapa de equivalencia funcional sigue pendiente.
4. Tasas negativas de abandono o índices superiores a100no son errores por definición; el equipo educativo ya encontró explicación y valores oficiales para tres casos. Deben registrarse como corroborados con nota, no como corregidos.
5. Los controles de campos vacíos evolucionaron a campos sin información útil; usar las métricas más recientes213 definiciones,127 metodologías y13 fórmulas, especificando que son incidencias por vínculo/campo, no cifras de indicadores únicos.

## Propuesta de resolución de los dos casos temporales

**Salud789:** proponer una regla versionada de comparación categórica: reference_period←modalidad de Año Censal (2010 o 2022), edad←modalidad de Grupo de edad; raw_year se preserva como atributo fuente, sin eje ni filtro de período científico. Estado actual: propuesta respaldada por estructura interna, pendiente de contraste con publicación censal y Tableau. El valor numérico no se altera.

**Comedores465:** preparar un caso con las12 filas completas y su corte de carga. La estructura es un cruce de nivel y ámbito, no una serie temporal. La secuencia de raw_year sugiere carga secuencial de categorías; esa hipótesis no identifica el año de los datos. Estado actual: bloquea presentación temporal hasta contrastar cuadro/corte de RA. Mantener la vista categórica solo si el período puede documentarse y aprobarse.

## Alcance de esta revisión

No se modificó ni corrigió la base; no se presentó esta revisión automática como aprobación de responsables humanos. No se ejecutó comparación visual de Tableau ni de una versión nativa. No se reconstruyó EPHU para resolver el101%. El informe aporta un contrato, evidencias y reglas de decisión que deben integrarse al motor nativo.

Reproducibilidad: ejecutar review_statistics.py con --database, --repo, --twb-root y --out. La conexión SQLite usa mode=ro. El resultado evidence.json preserva consultas derivadas,20casos temporales completos, conteos y referencias de shelvesAVG de Tableau.
