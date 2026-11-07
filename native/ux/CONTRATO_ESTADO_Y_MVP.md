# UX nativa — contrato implementable y prototipo supervisado

Versión de propuesta: 0.2.0-review. Corte de datos: 6/11/2026. Este documento refina, sin aprobar, native/ux y los contratos estadístico e integración. No reemplaza las decisiones de estadística ni temática. No se modificó el repositorio.

## MVP y límites

Una ficha reutilizable, no 71 aplicaciones. Conservar ocho ejes, colecciones y rutas heredadas; el piloto implementa tres entradas de datos: abandono primario, nacidos vivos y composición migratoria. El futuro buscador/entrada por pregunta/territorio se apoya en el mismo catálogo semántico. El prototipo no implementa navegación completa de los 71 tableros ni la presenta como resuelta.

La publicación requiere los gates del contrato de integración. «Candidato técnicamente legible» no implica «estadísticamente reconciliado», «aprobado por responsables temáticos» ni «listo para publicar». Una versión candidata puede visualizarse en revisión supervisada con su estado explícito; no integra por eso la API o el sitio público.

El prototipo index.html es autocontenido: CSS, JavaScript y los datos agregados están embebidos; no hace fetch ni necesita imágenes, fuentes o servicios externos. Los enlaces de fuente son enlaces de navegación, no dependencias de carga. El manifiesto identifica recursos, fuentes y hashes. El padre realizará vista previa supervisada con sites-preview + cua_repl; este agente no la considera ejecutada.

## Contrato de contexto compartible

Distinguir estas capas:

| Capa | Campo | Semántica | Ejemplo |
|---|---|---|---|
| Identidad de consulta | qv | Versión del esquema de URL; desconocida → rechazo | 1 |
| Catálogo | dataset / indicator_ref | Indicador/configuración autorizada. En producción: clave canónica + namespace hasta aprobación de identidad común | education → abandono primario publicado por fuente |
| Evidencia | snapshot | Instantánea técnica incluida y accesible | 2026-11-06 |
| Evidencia | release | Identificador/hash de edición de la fuente | SHA-256 del ZIP de indicadores educativos |
| Cuadro | period | Período estadístico mostrado en tabla/barras/mapa/detalle, no fecha de carga | 2024-2025 |
| Serie | series_from / series_to | Ventana temporal del mismo indicador/universo; no modifica el período del cuadro | 2012-2013 … 2024-2025 |
| Geografía | territory | Código incluido en el dominio admitido; all solo si la fuente permite las unidades listadas | 38 = Jujuy |
| Comparación | compare | Segundo territorio distinto dentro del mismo dominio | 42 = La Pampa |
| Universo | universe | Identificador controlado que fija población y filtros sustantivos | primary_total; births_residence; all |
| Aperturas futuras | dimensions | Mapa de dimensión→categoría autorizadas, basado en catálogo y contrato | education_level=primary, sex=total |
| Vista futura | view | Representación autorizada por capabilities | table, bars, map, time_series |

El MVP mantiene universos únicos por dataset, por lo que no inventa dimensiones seleccionables que no estén validadas. El esquema de producción puede reemplazar universe por un conjunto explícito de dimensiones sin perder su identidad de contrato; no deben admitirse claves libres ni nombres inferidos del texto de una columna. El objeto de consulta debe contener códigos, nunca fórmulas ejecutables.

URL legible y determinista del prototipo:

```
?qv=1&dataset=education&snapshot=2026-11-06&release=18911b578fd943d3fa45fd37b5bd23d40f05543e2a0f4db325e239458c044204&period=2024-2025&series_from=2012-2013&series_to=2024-2025&territory=38&compare=42&universe=primary_total
```

### Lectura y restauración

1. Una URL sin parámetros inicia una consulta nueva predeterminada y escribe su contexto explícito.
2. Una URL con parámetros debe ser completa, versión conocida, sin duplicados y con campos admitidos. No es una solicitud de «hacer lo mejor posible» con valores parecidos.
3. Si versión, fuente, territorio, período o universo no están incluidos: mostrar error contextual, no cargar datos y no sustituir silenciosamente. Ofrecer acción explícita «Abrir una consulta nueva»; recién esa acción inicia los valores predeterminados.
4. Escape de todo texto en HTML; códigos de fuente son allowlist, no URLs introducidas por la persona. No evaluar contenido de URL como código.
5. Cada cambio discreto de consulta utiliza historial. Atrás/Adelante restaura exactamente el contexto admitido. Se puede usar replaceState solo para canonicalizar el estado inicial o controles continuos claramente definidos.
6. Cambiar de dataset reinicia territorio, comparación, período y universo al contexto del nuevo indicador. No se hereda provincia en un indicador nacional ni ventana temporal inválida.
7. El estado restaurado debe ser el mismo usado por representación, tabla, detalle y exportación. Los parámetros que solo afectan la serie se identifican explícitamente como tales.

## Filtros y sincronización

- Period controla solo el cuadro territorial/composición y su tabla. Su etiqueta indica ciclo, año censal, trimestre o mes según contrato.
- Series_from/to controla solo la serie y su tabla temporal. La interfaz explicita que no cambia el período del cuadro. Requiere una selección territorial válida; all no produce un promedio nacional.
- La comparación exige el mismo indicador, fuente/edición, unidad, universo, periodicidad, método y niveles de geografía. Las dos unidades territoriales son la única diferencia sustantiva autorizada.
- Un segundo territorio deshabilita la interacción cuando el primero es all o cuando el dominio es nacional. Seleccionar una provincia por lista/barra/mapa debe llamar a la misma transición de estado, no un filtro paralelo oculto.
- Geometrías y datos tienen gates separados. Si el mapa está bloqueado, barras y tabla siguen disponibles sin sugerir que la geometría es válida.
- Para futura selección por mapa: click y teclado deben invocar la misma acción de territorio que el selector; la tabla y el detalle deben devolver idénticas claves de observación. No se implementó ni validó ese flujo en esta ronda porque GIS detectó problemas de geometría.

## Compatibilidad del comparador

| Solicitud | Resultado |
|---|---|
| Abandono primario 2024–2025: Jujuy frente a La Pampa, misma fuente | Permitido como exploración candidata, con nota sobre tasas negativas y estado sin aprobación temática. |
| AUH218: cobertura 0–17 entre dos provincias, misma edición y denominador metodológico | Permitido solo cuando mapping/denominadores estén aprobados. Las tasas no se promedian al seleccionar varias provincias. |
| AUH217 participación en el total país junto a AUH218 cobertura provincial | No es la misma comparación; ofrecer cambio explícito de indicador o paneles separados en una etapa posterior. Nunca sustituirlos por compartir %. |
| Abandono381 territorial junto a384 serie nacional | Requiere relación curada; no se enlaza por nombre, unidad o tema. |
| Lugar de nacimiento1048 nacional urbano con filtro provincial | Denegado: el agregado no respalda ese territorio. Ofrecer mantener total urbano o buscar otro indicador de dominio válido. |
| Nacidos vivos absolutos frente a tasa de mortalidad infantil | Denegado como serie/escala común; son medidas/universos diferentes. |
| Salud con bajo peso respecto a todos los nacidos vivos vs respecto a peso conocido | Requiere identificar denominador; se deniega mezclar ambos como una misma medida. |

## Estados de dato, evidencia y operación

No usar un único «sin datos» para todo. El backend debe devolver status y reason_code separados de value. Nunca serializar ausencia como0.

| Estado | Representación | Acción y publicación |
|---|---|---|
| observed / candidate | Valor y procedencia + estado de evidencia | Puede revisarse internamente; publicación solo con gate completo. |
| source_missing | «Fuente no publicó este valor» | Consultar otro período sin sustituirlo automáticamente. |
| not_applicable | «No corresponde a este universo» | No ofrecer filtro ni incluirlo en denominador. |
| suppressed | «Dato no difundido por confidencialidad» | No inferir mediante diferencias ni mostrar localización individual. |
| zero_denominator | «No calculable: denominador cero» | Bloquear cálculo y describir método. |
| unknown_reference_period | «Período estadístico sin resolver» | Sin eje temporal ni filtro de período automático. |
| temporal_label_conflict | «El período de la fuente y la copia histórica no coinciden» | Retener sustitución; mostrar evidencia, no reasignar por conveniencia. |
| statistical_difference | «Conciliación pendiente» | Valores originales y candidatos separados en revisión, sin normalizar para forzar acuerdo. |
| blocked_geometry_review | Mapa no habilitado; lista/barras/tabla disponibles | No publicar mapa validado hasta pasar revisión GIS. |
| network_error | Error de carga con fecha de último dato válido si existe | No mostrar un dato viejo como actual; reintento explícito. |
| invalid_query | No mostrar valores | Rechazo por defecto; nueva consulta solo con acción explícita. |

En migraciones el prototipo presenta cuatro categorías del cálculo candidato con faltantes conservados y, en tabla, la copia de Tableau disponible. La diferencia pendiente impide su sustitución pública; se muestra a propósito como caso de revisión. No se utiliza ese cálculo para fabricar equivalencia con101%.

## Recursos y datos reales del prototipo

| Dataset | Observaciones embebidas | Fuente y restricción |
|---|---:|---|
| Abandono primario | 312 =24 provincias×13ciclos | Salida education/output-v2; solo nivel provincia, primary,total. Se excluyeron Conurbano y RestoBsAs para no mezclar escalas con provincias. |
| Nacidos vivos | 24 provincias, año2024 | Salida health/output_v2; no se convierten códigos98/99 a provincias. Cantidades, sin inferir tasa. |
| Migraciones urbanas | 4 categorías,2025T3 | Salida social/results, all +show_unknown. Incluye sininformación; candidato no conciliado. |

No se copiaron datos individuales ni se requirió geolocalización de personas. Los datos son agregados provenientes de adaptadores del equipo y siguen sin aprobación temática.

El mapa se mantiene bloqueado tras el hallazgo GIS de geometrías simplificadas inválidas y superposiciones. No se usa una silueta decorativa ni un mapa inventado para aparentar funcionalidad. Este bloqueo debe permanecer visible en la versión revisada hasta sustituir/validar el recurso geométrico.

## Tareas de implementación y aceptación

| Prioridad | Tarea | Criterio comprobable |
|---|---|---|
| P0 | Estado canónico único y URL versionada | Roundtrip exacto; todos los valores de tablas/gráficos/exportación provienen del mismo estado; no se acepta release desconocido. |
| P0 | Cuadro vs ventana temporal | Cambiar ventana no cambia filas del cuadro; cambiar período del cuadro no cambia ventana; rótulos siempre distinguen ambos. |
| P0 | Resolver períodos según estadística | Los indicadores789 y465 no se dibujan usando raw_year como tiempo mientras su contrato lo bloquee. |
| P0 | Comparador compatible | Pruebas positivas y negativas de la tabla anterior; ninguna ruta de UI puede saltarse validación. |
| P0 | Ausencias y calidad | Cero visible distinto de ausencia; estados no calculables sin ceros inventados; alertas críticas no pueden cerrarse por UI. |
| P0 | Geografía en una sola transición | Lista/barra cambia consulta, detalle y tabla; futura acción mapa produce exactamente el mismo resultado. |
| P0 | Aprobación por vista | Botón/endpoint de publicación bloqueado si falta aprobación; un match estadístico no habilita por sí solo el release. |
| P1 | Catálogo y taxonomía | Mantener8ejes y rutas; indicador por clave estable, alias curados, entradas porpregunta/territorio como vistas del catálogo. |
| P1 | Accesibilidad real | Teclado completo, foco visible, estados anunciados, nombres/roles claros, lectura tabular equivalente y sin dependencia de color/hover. Verificar con navegador y lector, no inferir desdeARIA. |
| P1 | Exportación reproducible | Archivo contiene consulta, universo, unidad, fuente, release, snapshot y aprobación; exactamente las observaciones del cuadro. Serie exportable separadamente con su ventana. |
| P2 | Comparación de rendimiento/usabilidad | Medir tareas equivalentes y éxito/interpretación; no afirmar mejora sin línea de base ni pruebas con personas. |

## Comprobaciones técnicas realizadas por este agente

- test_state_contract.js pasa con roundtrip; esquema inválido; período desconocido; snapshot incorrecto; parámetro duplicado; ventana invertida; comparación sin territorio; cambio de indicador que reinicia dominio; universo no admitido.
- El script de generación verifica de forma determinista los archivos embebidos y registra su manifest. Los scripts embebidos se analizaron sintácticamente con Node.
- No se ejecutó todavía una prueba de interfaz en navegador por este agente. El padre coordina la vista previa supervisada en escritorio/móvil y debe registrar sus resultados por separado.
- No hubo pruebas con personas ni declaración de conformidad WCAG. El prototipo es un insumo revisable, no un producto terminado.

## Próximo paso único

Ejecutar los escenarios de aceptación en la vista previa supervisada del prototipo y corregirlos antes de trasladar el patrón de ficha/estado a la implementación nativa. La publicación de mapas permanece bloqueada por el gate GIS; la aprobación estadística/temática de datos sigue un proceso independiente.
