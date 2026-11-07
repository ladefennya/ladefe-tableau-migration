# LADEFE — Segunda ronda de revisión cruzada

Estado: refinamiento técnico y prototipo supervisado; no es aprobación temática ni publicación del observatorio. El código y las decisiones siguen en el PR2 en borrador. Los seis agentes completaron una segunda ronda y la coordinación revisó la integración.

## Cambios de mayor impacto

### 1. Se confirmó un defecto propio de la cartografía del demo

La descarga IGN actual tiene24/24 geometrías GEOSválidas. Ejecutar `prepare_map.py` vigente sobre ese insumo reproduce el GeoJSON del demo byte por byte, con el mismo SHA-256. La salida tiene solo16/24 geometrías válidas y genera superposiciones entre provincias que no están en la fuente.

Los casos de SanLuis–Córdoba y SanLuis–Mendoza tienen ambas geometrías simplificadas válidas pero solapamientos diagnósticos de142,29 km²y70,00 km², respectivamente, frente a0 en la fuente. En el footprint común, CABA pierde13,53%de superficie respecto del archivo original. Son métricas técnicas en EPSG6933, **no áreas oficiales**. Otros cálculos con polígonos inválidos se identifican con cautela.

Esto es un defecto introducido por la simplificación cartográfica del proyecto; no demuestra corrupción de las bases estadísticas ni que Tableau tenga esos mismos polígonos. Por eso se conserva el insumo original, se registra una referencia no simplificada de24 geometrías válidas (solo para validación, demasiado pesada para un frontend móvil) y se bloquea el mapa del prototipo. Próxima corrección: simplificación que respete fronteras compartidas, topología y tolerancia de error documentada. No basta reparar polígonos individualmente o colorear una geometría inválida.

No se reemplazó la geometría del demo ni se modificó su dominio territorial automáticamente. El caso de TDF/Malvinas y el recorte utilizado están documentados; la referencia no debe presentarse como validación integral de cartografía oficial.

El refinamiento de escala sí queda preparado en la rama: rechaza objetos y arrays en vez de convertirlos a0; conserva el cero real y los negativos; usa una sola clase cuando todos los valores son iguales y permite dominio fijo explícito para comparaciones entre años. Las pruebas fallan con la versión anterior y pasan con la propuesta.

### 2. Educación: diferencia de redondeo explicable, sin aprobación ficticia

El registro8,1 de secundaria nacional2023 es compatible con un doble redondeo: la celda oficialK12 contiene8,0471945354, tiene formato0.00 y muestra8,05; esa cifra visible, redondeada con HALF_UPa una decimal, produce8,1. El XML de Tableau declara una decimal. Esto documenta una ruta compatible, **no prueba cómo se realizó la carga histórica**.

Las85 referencias quedan clasificadas:69 coincidencias directas,15 bloqueadas por conflicto temporal y1 compatible con doble redondeo. No se amplió la tolerancia. Ninguno de los15 valores coincide con el ciclo2023/2024 de su etiqueta; sí coinciden con2024–2025.

Se eliminaron asignaciones por descarte de nivel, grado o geografía. Las26 celdas nacionales de grado7 ahora distinguen estructura7-5 en primario y6-6 en secundario; las medidas no cambian, pero el esquema sube a1.1 y esas claves se versionan. Hay15 pruebas, incluyendo precisión Decimal, persistencia de resultados y esquema inválido bajo Python -O.

### 3. Salud: evidencia primaria y límites más precisos

El anuario DEIS2024 confirma explícitamente el denominador de peso especificado. Se mantienen121/121 casos coincidentes en componentes, separando97 con documentación pertinente de24 de pretérmino cuya política porcentual de denominador sigue pendiente de aprobación. Coincidencia empírica no sustituye la ficha.

Se agregó una comprobación anual2024 de razón de mortalidad materna:183 muertesM,81 tardíasT excluidas y413.135 nacidos vivos; resultado4,4295 por 10.000, compatible con4,4 de Tableau. No se equipara esta observación anual con el trienio2022–2024.

Los CSV contienenSEXO=3 en6 nacimientos y10 defunciones, mientras los diccionarios descargados solo documentan1/2/9. Se preserva el código sin inventar etiqueta; se bloquea el desglose semántico afectado, manteniendo los totales. Se reemplazaron exclusiones genéricas «distinto de no especificado» por conjuntos positivos de categorías y validación estricta. Contrato de edición, hashes permitidos, dominios y manifiesto de salidas son obligatorios.16 pruebas aprobadas.

### 4. EPHU: se evaluaron dos ediciones justificadas

La terna del Tableau87,3/10,1/3,6 suma101%. La EPH total urbano3T2025 da aproximadamente86,4703/9,9735/3,5562 para población total y respuestas válidas. La edición3T2024 da85,7181/10,5021/3,7798; tampoco la reproduce. Comparar2024 con un registro2025 se marca explícitamente como período no equivalente, no como validación alternativa.

El código de edad−1 sigue sin etiqueta explícita encontrada en las fuentes primarias consultadas. Se conserva y se mantiene el cálculo infantil como sensibilidad bloqueada; la discrepancia de población total es independiente de esa decisión. Los14 casos sin respuesta tampoco explican el101%.

El adaptador incorpora perfiles de edición con hash, tamaño, esquema, filas y población ponderada; no permite aceptar otro archivo mediante un simple override de hash. Incluye dominio e incertidumbre por fila, estados infantiles bloqueados, precisión Decimal y publicación de manifiesto de finalización al terminar.14 pruebas aprobadas, con ejecuciones reales de2024 y2025.

### 5. Reglas ejecutables por vista

`native/statistics/publication_gate.py` convierte el contrato en reglas comprobables. Por defecto rechaza vistas no registradas; bloquea períodos desconocidos, agregaciones implícitas, denominadores incompatibles, campos/checks desconocidos y aprobaciones correspondientes a otra edición. Exige topología aprobada para mapas; no bloquea por eso una tabla o barras del mismo dato.

La decisión requiere alcance de fuente y período, evidencia y aprobación temática explícita. No se creó ni simuló ninguna aprobación humana. Este módulo **valida configuración, no autentica personas**: el servicio que lo integre deberá autenticar y autorizar a quien registre decisiones. Nunca debe aceptar desde el navegador un objeto de aprobación como si fuera una credencial.

Las20 filas temporales originales siguen intactas. Ocho de salud admiten una propuesta trazable2010/2022 desde «Año Censal», pendiente de aprobación; doce de comedores continúan sin período acreditado. Los XML muestran ANIO en filtros, aunque no en los ejes de esas aperturas: no corresponde afirmar que el Tableau ya muestra proyecciones.15 pruebas normales y optimizadas aprobadas.

### 6. Prototipo de consulta y validación supervisada

`prototypes/native-review/index.html` es autocontenido y usa agregados reales candidatos:312 observaciones de abandono (24 provincias×13 ciclos),24 de nacimientos y4 categorías nacionales de migración. No incluye microdatos ni depende de APIs o recursos externos.

Se probó con sites-preview y el navegador integrado mediante cua_repl:

- Selección de provincia y comparación sincronizadas entre barras, tabla, detalle y URL.
- Período del cuadro separado de ventana de serie; Atrás restaura el estado.
- Una URL inválida no carga datos ni sustituye versión/universo silenciosamente.
- Activación por teclado de una barra actualiza la selección.
- Escenarios de salud, migración y cartografía muestran sus límites.
- Ancho390 pxmedianteiframe (documento375 pxpor scrollbar), sin desborde horizontal observado; no equivale a emulación de teléfono real.

Se corrigieron mensajes de comparación cuando ya había dos provincias seleccionadas, instrucciones provinciales en un escenario nacional, identificadores técnicos expuestos sin contexto y singular/plural. La edición es legible y el hash queda como detalle técnico. Los filtros móviles todavía ocupan demasiado espacio inicial: queda pendiente compactar la jerarquía antes de considerar aprobado el diseño. No se probaron320 px, lectores de pantalla, exportación en navegador ni personas usuarias.

La preparación de payload y la construcción de HTML están separadas y tienen entradas configurables. El payload congelado y el HTML se reproducen byte por byte; el manifiesto registra recursos y procedencia. El contrato de estado rechaza campos, versiones o universos no soportados. No habilita mapas ni publicación por cambiar parámetros de URL.

## Verificación de integración

Las pruebas integradas suman60 casosPython (15 educación,16 salud,14EPHUy15 gates), siete archivos de regresión JavaScript del proyecto y un contrato de estado adicional. Todos pasaron. Se ejecutó también validate_demo.py sobre su instantánea histórica de14.016 filas, sin intercambiarla con la base maestra de14.156. La validación de geometría se ejecutó con GDAL/GEOSdel entorno y quedó registrada aparte. Los scripts de auditoría agregados se parametrizaron al integrar para no depender de rutas personales.

## Prioridades que quedan abiertas

1. Sustituir la simplificación cartográfica por una geometría compartida, válida y suficientemente liviana; repetir topología y revisión visual.
2. Resolver y aprobar reglas temporales de comedores, ciclos educativos y comparación censal por vista.
3. Incorporar la decisión temática sobre denominador de pretérmino, código de sexo no documentado y universo infantil EPHU.
4. Cerrar la discrepancia de migraciones con la receta/edición usada por la Defe, sin normalizar el101%.
5. Compactar controles móviles y probar el prototipo con tareas reales y accesibilidad antes de aplicar la reorganización al observatorio completo.

La ronda entrega refinamientos probados, evidencia reproducible y una propuesta interactiva revisada. No equivale a migración terminada de71 tableros, certificación de todas sus estadísticas ni despliegue del rediseño.
