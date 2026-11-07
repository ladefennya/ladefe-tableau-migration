# LADEFE — Decisiones del equipo para la migración nativa

Corte: 6 de noviembre de 2026. Estado: trabajo técnico de agentes especializados, con revisión cruzada y pruebas reproducibles; no equivale a aprobación de responsables temáticos ni a un producto listo para publicar.

## Decisión central

Es conveniente construir un motor nativo común, con fuentes y reglas explícitas por indicador/vista, en lugar de copiar los 71 archivos como aplicaciones separadas. También conviene revisar la organización de la experiencia: mantener los ocho ejes de derechos y las 71 colecciones/rutas como referencia, y añadir acceso por pregunta, territorio y búsqueda. La migración de datos, la organización editorial y el diseño visual tienen criterios de aceptación separados.

El equipo no recomienda una migración masiva publicada sin cerrar los arquetipos, ni poner un mapa en todas las pantallas. La unidad de liberación debe ser una vista/indicador con reglas aprobadas: una inconsistencia temporal en dos indicadores no necesita bloquear todo el observatorio, pero sí las representaciones que podrían interpretarla mal.

## Equipo y trabajo concreto

| Enfoque | Responsabilidad | Trabajo realizado |
|---|---|---|
| Estadística y ciencia de datos | Granularidad, cálculos, tiempo, validación | Contrato metodológico, revisión de los 71 XML y base, clasificación de incertidumbres y de versiones de IDs. |
| Estadística educativa / ingeniería de datos | Fuente oficial y reconciliación | Adaptador ejecutable de abandono interanual, pruebas de esquema, ciclos, estructuras educativas y diferencias con Tableau. |
| Estadísticas vitales / ingeniería de datos | Denominadores, causas, edades | Adaptador DEIS de nacimientos y defunciones 2024, agregados y conciliación de cinco indicadores provinciales y nacimientos nacionales. |
| Estadística social y económica | Encuestas, programas, gasto y fuentes mixtas | Reproceso EPH total urbano 3T2025; contratos para stock/flujo, edades, programas, discapacidad y presupuesto. |
| GIS / estadística espacial | Aptitud territorial y cartografía | Matrices para 71 tableros y 764 vínculos indicador–tablero; cobertura, candidatos geográficos y parche de faltantes en escala. |
| UX / arquitectura de información | Recorridos, comparación y accesibilidad | Revisión estática y propuesta con tres recorridos reales, decisiones y criterios de evaluación. No se hicieron pruebas con personas. |

La coordinación revisó código y ejecutó las pruebas de los adaptadores y regresiones existentes. Los agentes se comunicaron sobre conflictos de período, denominadores y geografía, en vez de aprobar sus piezas de forma aislada.

## Resultados implementados y comprobados

### Educación

El adaptador extrae 5.265 celdas oficiales de abandono: 4.927 observadas y 338 estructuralmente no aplicables; 13 ciclos de 2012–2013 a 2024–2025, con 27 unidades territoriales por ciclo. Esas 27 no son 27 provincias: incluyen el nacional y subdivisiones bonaerenses, que se mantienen separadas y no se suman con Buenos Aires.

Conciliación de 85 registros de Tableau: 84 coincidencias numéricas a una decimal. Entre esas coincidencias, 15 tienen conflicto de etiqueta temporal: el texto señala 2023/2024 mientras los valores coinciden con 2024–2025. Quedan 69 coincidencias sin ese conflicto detectado, aún candidatas. Un registro nacional de secundaria conserva diferencia: 8,1 en Tableau frente a 8,0471945354 en la fuente, que redondea a 8,0. No se amplió la tolerancia para hacerlo coincidir. Los 48 valores provinciales de mapas cotejados coinciden.

Se conservan los negativos, la nota sobre modelo de flujos, período inicial/final, estructura 6-6/7-5, grado, celda y hash. Se bloquean cambios de esquema y poblaciones inesperadas. El adaptador no publica resultados.

### Salud

Se reconciliaron 121 casos con DEIS 2024: 24 provincias por cinco indicadores (bajo peso, pretérmino, mortalidad infantil, neonatal y postneonatal) más nacimientos nacionales (413.135). Los componentes cotejados coinciden exactamente.

La reconstrucción confirma una regla relevante: el denominador de bajo peso excluye nacimientos sin peso especificado, y el de pretérmino excluye gestación no especificada. El texto genérico «total de nacimientos» no describe completamente el cálculo efectivo. La regla debe quedar en la ficha; no debe generalizarse a otras tasas.

Las pruebas encontraron un error en el parser experimental de bajo peso —omisión del intervalo 2000–2499 g— y lo corrigieron antes de aceptar los resultados. La prueba de borde impide repetirlo. Esto es un defecto del adaptador en desarrollo, no evidencia de error del dato original.

Se conservan códigos98/99 fuera del mapa, edad infantil no especificada y causa/sexo/grupo de edad. No se desagrega 15–19 en 15–17, ni se inventan tasas sin población de referencia. El adaptador es de edición2024; nuevas ediciones requieren configuración y nueva conciliación.

### Migraciones y estadística social

Se descargó la EPH **total urbano** del tercer trimestre de2025, con71.322 registros individuales y ponderado total43.337.370. No se sustituyó por la EPH de31 aglomerados. Para población total, CH15 y PONDERA, excluyendo no respuesta del denominador, producen aproximadamente86,4703% misma provincia,9,9735% otra provincia y3,5562% otro país. No reproducen87,3/10,1/3,6 del Tableau, que suma101%.

Esto demuestra una discrepancia reproducible respecto de esa edición y política de faltantes; no establece todavía si la Defe usó otra edición, filtro o denominador. Se conserva la terna original y se bloquea su sustitución automática. El adaptador ofrece sensibilidad con/sin no respuesta y políticas de edad explícitas. El código de edad−1 no se aprobó como parte del corte infantil por falta de confirmación inequívoca en la documentación consultada. La conclusión sobre población total es independiente de ese problema de edad.

## Correcciones de interpretación respecto de la auditoría preliminar

1. **No hay evidencia de seis proyecciones2027–2029.** La revisión detecta20 filas con contrato temporal problemático: ocho de salud789 y doce de comedores465. En salud hay dimensión explícita Año Censal2010/2022 mientras ANIO recorre2022–2029; en comedores el año avanza con categorías de ámbito/nivel. No se construye eje cronológico desde ANIO ni se asigna un año sustituto sin validación.
2. Los164IDs con variantes de metadatos entre archivos se mantienen por procedencia y versión; una unificación conceptual necesita curaduría.
3. Hay355 referencias a AVG(VALOR) en los XML. Reproducir una fila no prueba que promediar varias aperturas sea correcto. Las marcas y filtros necesitan validación explícita.
4. La suma101% supera la tolerancia de redondeo de tres categorías a una decimal (0,15 puntos) si las categorías son una partición exhaustiva y excluyente. No debe normalizarse a100 para ocultar el problema.
5. Las alertas no son todas errores. Abandono negativo, índices superiores a100, ausencia territorial o saltos temporales pueden ser legítimos. Se separan diagnóstico, evidencia, propuesta de corrección y decisión temática.

## Cartografía: dónde aporta y dónde no

- 51 de 71 tableros tienen datosMAPA en la extracción actual:171 indicadores,4.065 filas y171 cortes;154 cortes con24 jurisdicciones y17 incompletos.
- Ocho indicadores adicionales tienen categorías provinciales en aperturas, con184 filas candidatas. No añaden ocho tableros completos ni habilitan mapas automáticamente. AUH217 (participación en total nacional) y AUH218 (cobertura) no son intercambiables aunque ambos usen%.
- Para proporciones/tasas comparables, coropleta con denominador y escala explícitos; para cantidades, barras o símbolos proporcionales, según la tarea. Al comparar años, dominio de color común y explicación visible de cualquier cambio.
- Los20 tableros sinMAPA necesitan buenas series, barras, distribuciones y tablas; no deben quedar como productos de segunda categoría.
- No se infieren puntos a partir de provincias ni se geolocalizan registros individuales de niños/as. Un futuro mapa de equipamientos requiere fuente pública de establecimientos y coordenadas, no estimaciones derivadas de estos agregados.
- La geometría actual tiene24 features provinciales y TDF incluye Malvinas bajo la misma feature. El recorte cartográfico actual y la integridad topológica requieren revisión específica; no se certificó cartografía oficial ni aspecto visual.

Se preparó y probó un arreglo de `discreteScale`: el código original convertía null en0 y podía asignarle un color de dato. La corrección conserva la distinción entre ausencia, cero real y negativos, con prueba que falla en el original y pasa con el parche. Se mantiene en rama de revisión.

## Organización y experiencia propuestas

| Cambio | Beneficio | Condición para implementarlo |
|---|---|---|
| Conservar ocho ejes y rutas existentes; añadir Preguntas/Territorios/buscador | Permite encontrar información sin conocer archivos de Tableau | Taxonomía y sinónimos curados; no fusionar conceptos por parecido. |
| Comparador con compatibilidad explícita | Evita comparar poblaciones o unidades distintas | Validar universo, edad, período, geografía, fuente y metodología; explicar por qué una comparación no está habilitada. |
| Consulta compartible y descargable con versión y filtros | Reproducibilidad para prensa/investigación/gestión | URL y CSV deben representar el mismo conjunto de datos; preservar historial y referencias de fuente. |
| Filtros de aperturas, territorio y subperíodo | Resuelve selecciones hoy solicitadas pero no disponibles | Controles derivados del contrato por indicador; filtros de mapa y ventana de serie explícitos. |
| Gráficos de barras/pequeños múltiplos para composición y cruces | Da utilidad a indicadores sin mapa o serie | Solo categorías compatibles; no truncar sin avisar ni sumar particiones no exhaustivas. |
| Tabla paginada, contador y descarga completa | Evita ocultar filas después del corte actual de250 | Teclado, lector de pantalla, estado vacío y conservación de filtros. |
| KPI nacional desde rol de agregado, no desde texto «total» | Menor riesgo de presentar un agregado equivocado | Rol semántico explícito; mostrar ausencia cuando no hay dato comparable. |
| Separar período del dato, edición de fuente y fecha de carga | Evita atribuir actualidad ficticia | Nunca sustituir un dato desconocido por la fecha del archivo. |

La revisiónUX es estática: no acredita que el rediseño funcione con usuarios ni certifica accesibilidad. Antes de publicar cambios de interfaz se exige preparar la salida completa y revisar una vista previa supervisada con sites-preview y el navegador integrado mediante cua_repl, además de escritorio/móvil/teclado y casos sin datos. No se presentó la web publicada como validación de una propuesta nueva.

## Arquitectura de migración recomendada

1. **Originales inmutables:** URL, edición y hash; registrar revisiones sin sobrescribir historia. Microdatos se procesan en entorno de trabajo y solo se publican agregados autorizados.
2. **Adaptadores por fuente:** Python y dependencias acotadas (openpyxl para Excel); esquema esperado, dominios y cortes explícitos; error claro ante cambios de formato. Las fuentesCSVno necesitan motor de base remoto para esta escala.
3. **Base de trabajo:** SQLite versionada para trazabilidad, reconciliación y consultas; separar datos fuente, dimensiones, reglas y decisiones. El público recibe exportaciones de solo las vistas aprobadas.
4. **Capa semántica:** universo, magnitud, denominador elegible, período real, geografía, agregación permitida, relaciones entre vistas y estados de calidad. No usar ANIO, unidad%o nombres para inferir todo automáticamente.
5. **Publicación por versión:** resultados candidatos y diferencias; revisión estadística/temática cuando corresponda; última versión aprobada intacta si falla una fuente. Automatizar preparación no implica aprobar publicación.
6. **Motor de visualización común:** componentes nativos de serie, barras, distribución, mapa y tabla, configurados por metadatos aprobados. No es necesario crear71 aplicacionesniuna plataforma de edición visual completa para el primer lanzamiento.

Esta opción aprovecha la infraestructura existente, reduce dependencias y facilita la transferencia a Sistemas. No se contrataron servicios, crearon cuentas ni habilitaron suscripciones o despliegues. Los adaptadores de esta entrega son pruebas de migración con salidas candidatas; la arquitectura completa aún debe implementarse e integrarse al motor público.

## Orden de implementación y aceptación

| Etapa | Alcance | Aceptación verificable |
|---|---|---|
| 1. Contratos y bloqueos | Resolver tiempo, universos y denominadores de pilotos | Cada vista tiene referencia temporal y regla de cálculo documentadas; no hay sustituciones implícitas. |
| 2. Pilotos desde fuente primaria | Abandono, vitales y migraciones | Reconciliación por registro y componente; conflictos visibles; pruebas de esquema/revisión/bordes. |
| 3. Pilotos cartográficos | Cantidad, cobertura y participación nacional | Geocódigos válidos, denominadores, escalas, faltantes y alternativa accesible; validación visual supervisada. |
| 4. Prototipo de experiencia | Tres recorridos reales y comparación compatible | Tareas completables sin conocer IDs, filtros coherentes, URLreproducible, sin truncamientos ocultos, pruebas con personas y accesibilidad. |
| 5. Escala por familia | F01/F02 yfuentes adicionales | Criterios de los arquetipos cerrados antes de aprobar indicadores en lote; fechas y manual de mantenimiento. |

Los casos actuales no cubren todavía todos los seis arquetipos de certificación del repositorio ni todas las reglas de las71 colecciones. No se aprobaron indicadores o datos solo por contar con una descarga o un test verde. La aprobación temática debe quedar registrada por responsables designados de la Defe.

## Estado de la entrega

Implementado/probado: tres adaptadores candidatos, pruebas unitarias de ingestión, conciliaciones puntuales, inventarios estadísticos/GIS/UXycorrección de escala faltantes. Propuesto: contratos, arquitectura, reorganización y recorridos. Pendiente: aclaraciones semánticas, certificación de filtros/renderizado, prototipoUXypublicación. No fusionado ni desplegado.

Próximo paso concreto: aplicar el contrato temporal y de denominadores a un piloto nativo de abandono/vitales y preparar su vista previa supervisada, con mapa, barras/serie y tabla coherentes. La terna de migraciones no debe sustituirse mientras su discrepancia siga sin explicación.

## Verificación de integración

Se ejecutaron desde la raíz del repositorio 20 pruebas Python (6 educación, 8 salud y 6 EPHU), seis archivos de regresión JavaScript y validate_demo.py. Todos aprobaron tras la integración. También se repitieron los tres adaptadores con los recursos reales y la base de referencia en modo de solo lectura: se reproducen los resúmenes informados. El demo conserva su instantánea histórica de 14.016 filas; las 14.156 corresponden a la base maestra actual, no se intercambiaron ni se publicó una actualización. No se ejecutaron workflows de escritura.
