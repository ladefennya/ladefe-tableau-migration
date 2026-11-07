# Propuesta UX e información para los tableros nativos LADEFE

Fecha: 6 de noviembre de 2026. Estado: propuesta de diseño y revisión estática de código/datos; no es auditoría visual, prueba con personas ni declaración de conformidad accesible.

## Decisión propuesta

Conviene revisar la organización de la experiencia, manteniendo como referencia editorial los ocho ejes actuales y la trazabilidad de los 71 tableros. El reemplazo no debería reproducir la secuencia obligatoria Tema → Tablero → Indicador → Vista técnica para todas las personas. Propongo tres entradas al mismo catálogo semántico: **Temas**, **Territorios** y **Preguntas**. Las rutas no crean indicadores nuevos ni fusionan los existentes. La certificación de datos es independiente del diseño de navegación.

La mejora central es pasar de elegir un archivo de Tableau a resolver una pregunta con un conjunto de datos explícito. La novedad útil sería un **comparador que explique qué se puede comparar y por qué**, acompañado por una **ficha de consulta reproducible** que preserve fuente, período, universo, filtros y versión en una URL y en la descarga. No se propone un asistente que improvise relaciones ni una narración automática que pueda atribuir causalidad.

## Evidencia observada

Consulta a la base maestra v1: 71 workbooks, 764 vínculos tablero–indicador, 14.156 observaciones. MAPA está presente en 51 tableros, serie en 68, APERTURA en 59 y DISTRIBUCION en 56. Los ocho ejes del catálogo contienen 20, 14, 11, 8, 7, 6, 3 y 2 tableros, respectivamente. La inexistencia de MAPA no demuestra que el tema no sea territorial: las aperturas AUH217/AUHD423 tienen 24 categorías provinciales, pero requieren curación antes de volverlas geografía.

| Hallazgo estático | Evidencia | Consecuencia | Cambio propuesto |
|---|---|---|---|
| El acceso principal exige conocer la jerarquía editorial | index.html:29–33; app.js:25–31 | Dificulta llegar desde una pregunta o provincia | Conservar navegación temática y añadir buscador de indicadores con sinónimos curados y entrada territorial. |
| No hay selectores de aperturas, territorio o subperíodo | index.html y app.js:109–116, bind:56–64 | El mensaje de KPI pide seleccionar apertura, pero no hay control para hacerlo; una tabla no sustituye un filtro | Añadir controles derivados del contrato de cada indicador y mostrar siempre universo/periodicidad. |
| Distribuciones y cruces no tienen una gráfica dedicada | render:138–142 y capabilityMessage; solo drawLine/drawMap/drawTable | Temas sustantivos quedan relegados a tabla si carecen de mapa/serie | Barras/pequeños múltiplos para APERTURA y DISTRIBUCION cuando las categorías sean compatibles. |
| Serie limitada a seis grupos sin selección | app.js:151 | Esconde del gráfico otras series; la nota remite a aperturas que no son seleccionables | Selección explícita y búsqueda de grupos; máximo legible como regla de presentación, nunca truncamiento silencioso. |
| Tabla corta en 250 filas | app.js:174 | La vista parcial no se identifica ni pagina; CSV contiene selección completa | Contador «1–250 de N», paginación accesible y descarga completa con filtros. |
| El «Valor nacional» se reconoce mediante regex de nombres/aperturas | app.js:136–137 | Un texto «total» no certifica población ni agregado nacional | KPI solo si existe aggregate_role explícito, universo compatible y un único registro; ofrecer explicación cuando no. |
| El mapa prioriza nombre normalizado y omite provincias ambiguas | app.js:161–163 | Una ambigüedad puede parecer ausencia de datos | Geocódigo curado como clave y estado diferenciado: sin dato, no aplica, no publicado, retenido por ambigüedad. |
| La fecha mostrada como actualización de fuente procede de lastDataLoad | app.js:106 e index.html:24 | Puede confundirse carga del workbook con período estadístico o edición oficial | Separar «Datos de», «Fuente publicada el» y «Consulta actualizada el». Si desconocido, decirlo. |
| Los filtros solo actúan sobre la tabla en algunos modos | filtered:116; render:138–142 usa ownRows para gráficos | No queda explícito que el mapa usa último año propio y la serie todos los años | Alcance de filtros por panel documentado: año de corte del mapa y ventana de serie diferenciados, con resumen visible. |
| El historial de consulta solo usa replaceState | app.js:117–120; sin popstate en archivo inspeccionado | El botón Atrás no recorre necesariamente el análisis | Navegación de página/tablero con historial; ajustes continuos reemplazables; restauración íntegra del estado. |
| Elementos gráficos pueden recibir foco pero no hay selección territorial implementada | paintMap:169–171; no listeners de click/keydown de provincias en app.js | No asumir que pasar foco equivale a mapa filtrable | Si se incorpora selección, implementar botón/control semántico y alternativa de lista; si no, mantener mapa informativo. |
| Mensaje aria-live se oculta antes de actualizarse | render:132 y 143 | Riesgo de que el lector de pantalla no anuncie actualizaciones | Región de estado persistente; verificar anuncio real con lector de pantalla. No inferir cumplimiento desde presencia de ARIA. |

También hay bases positivas que conviene conservar: enlace de salto al contenido, etiquetas nativas de selectores, caption y th scope en tabla, foco visible CSS, CSV con valor calculado/raw/auxiliar, reglas de relaciones curadas, estados de carga y disposición responsive definida. Estas son observaciones de implementación; no equivalen a una prueba de uso o contraste en pantalla.

## Modelo de información

1. **Tema/derecho**: taxonomía editorial de ocho ejes; mantener URL heredada y redirección cuando cambie etiqueta.
2. **Tablero/colección**: agrupación editorial de indicadores, independiente del archivo de origen. La primera versión conserva las 71 colecciones como referencia; cualquier fusión editorial tendrá un registro de decisión y URL antigua resoluble.
3. **Indicador**: concepto, universo, unidad, numerador/denominador, población de referencia y vigencia. Clave por procedencia/versionado hasta que se apruebe una identidad estable común.
4. **Vista**: representación autorizada de un indicador propio o relación semántica aprobada. Mapa, serie y composición no se asocian por semejanza de nombre/unidad.
5. **Consulta**: indicador + período estadístico + territorio + aperturas + versión de fuente + modo de comparación. Se comparte y se descarga con la misma definición.
6. **Estado de evidencia**: fuente vigente, fecha, cobertura, faltantes, revisión metodológica y aprobación. No exponer al público logs del pipeline ni siglas internas.

Las Preguntas son accesos editoriales curados: «¿Cómo cambió?», «¿Cómo se distribuye?», «¿Qué diferencia hay entre provincias?» y «¿A quiénes alcanza?». Cada acceso lista únicamente indicadores con vistas aptas y describe alcance; no inventa una respuesta cuando no hay datos.

## Arquitectura de pantallas

| Pantalla | Contenido y decisiones |
|---|---|
| Inicio del monitoreo | Buscador único; accesos a ocho temas, territorio y preguntas; novedades de datos con fecha y alcance; enlace visible a metodología. Sin mosaico de 71 cifras inconexas. |
| Explorar tema | Subtemas editoriales y lista de indicadores con definición breve, población, fuente, período y capacidades. Filtros por edad, territorio disponible y fuente solo si son semánticamente válidos. |
| Perfil territorial | Provincia elegida mediante lista o mapa nacional; indicadores disponibles y advertencias. No equiparar un aglomerado EPH con toda la provincia. Cada ficha identifica su dominio real. |
| Ficha de indicador | Pregunta/título, dato y contexto; filtros; gráfico principal; cambios/comparación; tabla y descarga; definición y método; procedencia y estado. La explicación del universo nunca queda exclusivamente en un acordeón. |
| Comparar | Dos o más territorios compatibles para un mismo indicador, período y edición. Para comparar conceptos diferentes, mostrarlos como paneles separados con sus unidades y universos; no combinarlos automáticamente en un ranking o puntaje. |
| Fuentes y cambios | Ediciones disponibles, fechas, correcciones y advertencias relevantes; acceso a ficha metodológica y originales públicos. |

## Wireframe funcional de ficha (sin decidir estética)

| Orden | Escritorio | Móvil |
|---|---|---|
| 1 | Ruta temática, título claro, universo y período | Igual; título sin códigos técnicos largos. |
| 2 | Dato principal y comparación autorizada; fuente/corte visibles | Dato y universo primero; alternativa de dato no calculable con explicación. |
| 3 | Barra de contexto: territorio, período, dimensiones seleccionadas y Restablecer | Resumen compacto siempre visible + botón «Modificar filtros» que abre panel con aplicar/cancelar y foco controlado. |
| 4 | Gráfico principal junto a tabla/comparación según tarea | Una representación principal a la vez; cambiar entre Gráfico, Mapa y Tabla cuando existan. No reducir tres gráficos hasta volverlos ilegibles. |
| 5 | Comparación contextual y distribución/serie disponibles | Secciones sucesivas con títulos y resumen. Evitar scrolls anidados como única vía a todas las provincias. |
| 6 | Tabla completa paginada y descarga | Tabla accesible con desplazamiento horizontal delimitado; no ocultar columnas sustantivas. |
| 7 | Ficha de método, fuentes, calidad y cambios | Igual, con detalles desplegables; alertas de interpretación pertinentes permanecen visibles arriba. |

El selector Año se renombra según el contrato: «Año censal», «Ciclo lectivo 2024–2025», «Trimestre» o «Mes». Cuando el año bruto no representa tiempo estadístico, no construir slider ni una serie con ese campo.

## Tres recorridos para validar

### 1. Gestión/ciudadanía: cobertura de AUH por provincia

1. Buscar «AUH» o entrar en Condiciones de vida → Seguridad social.
2. Elegir la pregunta «¿Qué proporción de NNyA recibe AUH en cada provincia?» que lleva a indicador218 del workbook2_2bAUH, no al217.
3. Ver población de referencia 0–17 y denominador estimado; elegir período disponible.
4. Seleccionar Buenos Aires y otra provincia mediante lista accesible o mapa. La comparación conserva indicador, período y denominador metodológico.
5. Alternar mapa de coberturas y puntos/barras ordenadas; descargar consulta y fuente.
6. Si desea «dónde se concentran perceptores», navegar explícitamente a217 con advertencia: participación del total país, no cobertura provincial. El mapa adicional de217 es candidato curado, no aprobado por esta propuesta.

Criterio: 8 de10 participantes deben identificar correctamente diferencia entre concentración y cobertura y no confundir titulares con NNyA. No se ha ejecutado la prueba.

### 2. Periodismo/investigación: abandono escolar primario

1. Buscar «abandono»; elegir primaria por provincia, indicador381.
2. Mostrar ciclo 2024–2025 completo; indicar fuente y convención del año inicial cuando el archivo histórico conserva2024.
3. Comparar Jujuy, La Pampa y Neuquén. Mantener tasas negativas con nota metodológica; no tratarlas como valores imposibles ni llevarlas a cero.
4. Elegir distribución provincial de tasas; eje de barras con cero visible. Para una serie histórica, permitirla solo si adaptador y correspondencia indicador-período fueron aprobados; no sustituir381 por384 silenciosamente.
5. Copiar enlace/cita de consulta y descargar tabla con valores oficiales originales, unidades, ciclo y versión.

Criterio: participantes pueden explicar el período, encontrar la limitación del modelo y exportar exactamente la selección. No se ha probado.

### 3. Ciudadanía/investigación: composición de migraciones urbanas

1. Entrar por Preguntas → «¿Cómo se distribuye?» → lugar de nacimiento, indicador1048.
2. Seleccionar el universo «Población urbana» o «NNyA urbanos» antes de dibujar barras. Son denominadores distintos, no una sola distribución.
3. Ver las tres categorías del mismo universo y año. Si la versión de fuente mantiene suma101%, mostrar alerta de consistencia pendiente, conservar números y ofrecer método/fuente.
4. No presentar un mapa provincial: este indicador de composición es nacional y su universo es EPH total urbano. Ofrecer barras y tabla; un territorio administrativo adicional no está justificado por estar disponible en otra fuente.
5. Si abre evolución de extranjeros1049, mostrar explícitamente el cambio de concepto y no enlazar como si fuera la misma medida por un parecido temático.

Criterio: 8 de10 participantes distinguen universo y no interpretan un dato nacional urbano como su provincia. No se ha probado.

## Reglas de visualización

| Datos y pregunta | Representación inicial | Condiciones |
|---|---|---|
| Evolución con períodos comparables | Línea con puntos y fechas reales | Brechas visibles; sin unir cambios de definición ni interpolar años ausentes. Un solo dato → punto/tabla, no falsa serie. |
| Distribución de tasas territoriales | Mapa coroplético + barras o puntos + tabla | Denominador y dominio comparables; escala fija entre años cuando se compara evolución, con límites y versión documentados. |
| Cantidades territoriales | Barras o símbolos proporcionales; mapa si aporta | No privilegiar grandes provincias con una coropleta de cantidades como si representara intensidad. |
| Composición porcentual de un universo | Barras ordenadas; apilado100% solo si categorías exhaustivas/excluyentes | No normalizar sumas inconsistentes para hacerlas llegar a100. Si categorías se solapan, mostrarlas como tasas separadas. |
| Cruces de edad/sexo/sector | Barras agrupadas o pequeños múltiplos | Máximo de grupos legibles explícito y selección, nunca seis grupos arbitrarios ocultando el resto. |
| Dos años comparables por provincia | Gráfico de puntos enlazados o tabla de cambios | Diferencia en puntos porcentuales vs cambio relativo rotulados de forma distinta. |
| Fuentes/medidas incompatibles | Paneles separados | No eje dual por defecto, ranking compuesto ni semáforo de «mejor/peor» sin norma sustantiva aprobada. |

Títulos incluyen qué, quiénes, dónde y cuándo. Tooltips aportan valor exacto, unidad, denominador/población y fecha; su contenido también existe en tabla. La incertidumbre y los faltantes se muestran cuando la fuente permita cuantificarlos; no inventar intervalos. El texto de resumen es determinista y trazable; no presenta causas a partir de correlaciones.

## Accesibilidad y estados

Objetivo de implementación: WCAG2.2 nivelAA, comprobado mediante revisión automática y manual. Esto es una meta, no conformidad certificada.

- Todos los controles operables con teclado; foco visible y sin quedar oculto por barras fijas; orden de foco coherente. El mapa no es la única forma de elegir un territorio.
- Tamaño de objetivos como mínimo24×24CSSpx o separación equivalente cuando aplique WCAG2.5.8; para controles principales móviles objetivo de producto44×44CSSpx. Respetar excepciones de la norma sin usarlas para achicar innecesariamente la interacción.
- Gráficos con título, resumen textual, descripción contextual y tabla equivalente; no depender exclusivamente de color, hover o SVGaria-label genérico. Series diferenciadas también por trazos/marcadores.
- Uso de pantalla angosta y zoom sin perder controles esenciales; alternativas de tabla y lista. Un contraste escrito enCSS no certifica contraste real de texto/gráficos.
- Estados separados: cargando, error de red, sin observaciones para filtros, no aplica, sin publicación, revisión pendiente y último dato válido. No todos se traducen a «sin datos». Incluir acción útil («Restablecer filtros», «Ver último período publicado») y no activar cambio silencioso de universo.
- Anunciar actualizaciones breves en región de estado; evitar leer el gráfico entero después de cada cambio. No mover foco al actualizar una cifra salvo navegación explícita.
- URL y exportación reproducen todas las dimensiones seleccionadas y versión. La descarga incluye fuente y consulta para que una planilla no pierda el significado de las cifras.

Fuentes primarias consultadas: https://www.w3.org/TR/WCAG22/ ; https://www.w3.org/WAI/tutorials/images/complex/ ; https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum . La página de imágenes complejas respalda la combinación de descripción y equivalente textual/tabular; la guía de tamaño de objetivo distingue24px mínimo y44px mejorado.

## Plan de evaluación y criterios de decisión

Primero una prueba moderada de concepto con8–10 personas (ciudadanía, periodismo/investigación y gestión; incluir usuarias de teclado/lector de pantalla y móvil). Esta muestra sirve para detectar problemas, no para estimar porcentajes poblacionales ni demostrar superioridad estadística. Segundo, repetir tareas equivalentes en interfaz actual y prototipo, contrabalanceando orden para reducir aprendizaje. Evaluar:

| Métrica | Meta provisional de aceptación |
|---|---|
| Encontrar indicador correcto sin conocer nombre del tablero | ≥80% de éxito en tareas del piloto; registrar desvíos. |
| Identificar universo, período y fuente | ≥90%; cero confusiones graves que cambien la interpretación en el cierre de prueba. |
| Comparar provincias de la misma medida | ≥80% sin asistencia; toda incompatibilidad debe explicarse. |
| Recuperar consulta por enlace/exportación | 100% de los casos automatizados reproducen selección y versión; validar una muestra con personas. |
| Uso sin ratón | 100% de acciones esenciales de tres recorridos completables; cero trampas de foco. |
| Uso móvil/zoom | Ningún control esencial fuera del flujo; tabla puede desplazar horizontalmente de forma delimitada. |
| Tiempo de resolución | Medir línea de base; proponer reducción mediana≥25% solo si ambas interfaces tienen tareas equivalentes. No prometer mejora antes de medir. |
| Carga de datos | Medir red móvil y un equipo institucional; proponer presupuesto tras línea de base, no inventar rendimiento observado. |

La innovación se acepta si mejora comprensión, finalización o reproducibilidad. No se adopta por novedad visual. La revisión gráfica futura debe preparar salida pública completa y usar primero sites-preview con navegador integrado vía cua_repl, según instrucción del usuario. No validar diseño mirando solo la web publicada ni instalar un navegador local como primera vía.

## Prioridad

**P0 — corrección semántica visible:** dimensiones seleccionables, período estadístico correcto, KPI basado en roles explícitos, estados de calidad, tabla completa, procedencia en exportación. **P1 — descubrimiento y comparación:** buscador, entradas Temas/Territorios/Preguntas, comparador compatible, rutas persistentes. **P2 — exploración avanzada:** consultas guardadas/locales, pequeños múltiplos, vistas editoriales y perfiles territoriales con cobertura explícita.

Próximo paso único: convertir la ficha de abandono escolar381 en prototipo supervisado con filtros, ciclo2024–2025, comparación y nota metodológica, y ejecutar sus pruebas técnicas y de uso antes de extender el patrón. La presente entrega no modificó el repositorio ni la web y no valida todavía ese prototipo.
