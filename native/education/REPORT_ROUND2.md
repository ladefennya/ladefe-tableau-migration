# Educación — segunda revisión estadística y del adaptador

**Resultado:** adaptador fortalecido y discrepancia numérica acotada. No se modificó ninguna base original ni se aprobaron sustituciones. Salida vigente: `output-v3/`.

## 1. Cierre del caso secundaria 2023: lo comprobado y lo que sigue abierto

El origen oficial inspeccionado es el XLSX por división político-territorial del ZIP de tasas de abandono. La hoja `2023-2024` tiene fecha de realización **20/08/2025**, fuente RA 2023 y 2024 y el total secundario en la celda **K12**:

| Etapa | Valor |
|---|---:|
| Valor numérico subyacente del Excel | 8,04719453540115 |
| Formato declarado por la celda | `0.00` |
| Valor visible de la celda, dos decimales | 8,05 |
| Redondeo directo del valor subyacente a una decimal | 8,0 |
| Redondeo del valor ya mostrado a una decimal | 8,1 |
| Valor conservado en Tableau (indicador 384, ANIO 2023) | 8,1 |

El XML original de Tableau declara para `[VALOR]` `default-format='*####.0'`. Existe, por tanto, una explicación determinista de **doble redondeo** compatible con los formatos publicados. Esto **no demuestra que esa haya sido la ruta histórica de carga de Defe**, ni excluye otra edición previa del dato. No se encontró evidencia para afirmar una revisión oficial del valor específico o un error de transcripción.

El estado dejó de ser una diferencia sin explicación y pasó a `compatible_with_double_rounding`, que sigue pendiente de decisión metodológica. No se convirtió el valor oficial a 8,1 ni se reemplazó el legado: se guardan el valor subyacente, el formato y el valor visible, y ambas comparaciones.

Regla propuesta para los tableros nuevos: calcular y conservar precisión original, y redondear **una sola vez al final** para mostrar. Si se decide priorizar identidad con la publicación visible anterior, versionar esa decisión como excepción; no propagar el doble redondeo como fórmula general.

## 2. Las 15 etiquetas temporales: evidencia más fuerte

Los ocho registros de apertura primaria 380 y los siete de apertura secundaria 382 tienen `ANIO=2024` y texto que identifica **2023/2024**. Los resultados son:

- **15/15** coinciden, a una decimal, con la hoja oficial **2024-2025**.
- **0/15** coinciden, a una decimal, con los valores equivalentes de la hoja **2023-2024**.
- No hay inferencia a partir de un valor aislado: se contrastó el vector completo de categorías y los totales de ambos niveles.

Esto acota el problema a una **inconsistencia de etiqueta temporal del legado**, con evidencia numérica completa a favor del ciclo 2024–2025. La nueva salida nativa ya conserva `period_start=2024`, `period_end=2025`, tomados de la hoja oficial, pero no sobrescribe ni corrige por detrás el texto del Tableau. La equivalencia del legado queda bloqueada en esas 15 filas hasta que se apruebe la regla temporal.

## 3. Alcance total de conciliación de abandono

Se concilió **todo el universo comparable de abandono** en el workbook de referencia: cinco indicadores y 85 registros. Los otros cinco indicadores de ese workbook corresponden a promoción efectiva y no están cubiertos por este archivo de abandono; no se mezclaron fuentes por parecido del nombre.

| Indicador | Vista / mapeo explícito | Filas | Resultado |
|---|---|---:|---|
| 380 | Nacional, primaria, grados 1–7 y total; C12/J12 y celdas intermedias de la hoja del ciclo | 8 | Igualdad numérica, conflicto temporal en las 8 |
| 381 | Provincia, primaria total; columna C | 24 | 24 igualdades a una decimal |
| 382 | Nacional, secundaria, grados acumulados 7–12 y total; columna K y L–Q | 7 | Igualdad numérica, conflicto temporal en las 7 |
| 383 | Provincia, secundaria total; columna K | 24 | 24 igualdades a una decimal |
| 384 | Nacional, series primaria/secundaria; columnas C/K, ciclos 2014–2015 a 2024–2025 | 22 | 21 igualdades directas y 1 compatible con doble redondeo |

Resultado consolidado: **69 coincidencias directas sin conflicto detectado, 15 igualdades numéricas bloqueadas por período y 1 caso de doble redondeo**. No se resume como «85 aprobados» ni como «70 publicables».

La fuente completa produce 5.265 celdas: 4.927 observadas, 338 no aplicables estructurales y cero vacías aplicables; 13 ciclos y 27 unidades territoriales por ciclo. Los 767 valores numéricos subyacentes negativos se conservan, incluidos residuos muy próximos a cero que el formato visible puede mostrar como cero; el conteo no equivale a 767 errores.

## 4. Corrección de contrato: estructuras educativas y grados

Se mantiene el grado acumulado del sistema de doce años, tal como figura en las columnas oficiales. Un séptimo año no se reclasifica automáticamente como un primer año local de secundaria:

- Primaria de siete años: grado 7 aplicable a estructura 7-5; no aplicable a 6-6.
- Secundaria: grado acumulado 7 aplicable a 6-6; no aplicable a 7-5.
- Grados acumulados 8–12 de secundaria pueden tener años locales distintos según 6-6/7-5.
- Total nacional puede mezclar estructuras; no se promedia entre ellas.

Se corrigió la estructura efectiva de **26 celdas nacionales** (dos grados por trece ciclos): antes figuraban como `mixed`, ahora primaria grado 7 se identifica como `7-5` y secundaria grado 7 como `6-6`. Se preserva `geo_education_structure='mixed'` para expresar que el territorio nacional contiene ambas estructuras. **No cambiaron los valores.** Esta mejora cambia las claves de esas 26 observaciones porque corrige una dimensión: se versiona como esquema **1.1.0**, no como una revisión de la tasa.

Conurbano y resto de Buenos Aires conservan claves locales `06-CON`/`06-REST`; no se presentan como códigos INDEC. No se suman junto con Buenos Aires. El total nacional es el publicado, no un promedio de tasas provinciales.

## 5. Fortalecimiento del código y controles

- Sustitución de tolerancia aproximada ±0,05 por **comparación exacta de Decimal con ROUND_HALF_UP** a una decimal. Los empates positivos y negativos tienen política explícita. Se distinguen el redondeo del valor original y el del valor previamente formateado.
- El registro de referencia debe tener realmente una decimal declarada: no se redondea una nueva precisión inesperada para ocultar diferencias.
- Whitelist de modalidades de la serie 384; etiqueta nueva o vacía ya no cae en secundaria por descarte.
- Whitelist de grados de 380/382; una etiqueta no reconocida ya no se convierte en total.
- Ámbito nacional ausente solo se admite en la serie 384 mediante su metadato original que dice total del país y un contrato explícito, no como valor por defecto general. Se guarda la evidencia del alcance; los demás indicadores requieren geografía acorde a la vista. La metodología de 384 menciona primaria mientras las modalidades incluyen secundaria: es documentación imperfecta que requiere revisión, no una nueva fuente.
- Se verifica que el lookup no colisione entre estructuras antes de conciliar. Nunca sobrescribe una fila por otra.
- Formato porcentual inesperado (`0.00%`) falla para impedir error de escala. Se conservan formatos decimales y valor visible; un formato General no autoriza comparación por doble redondeo.
- Hashes de ZIP fuente, miembro XLSX, base de referencia, código de adaptador y todos los archivos de salida en manifest.
- Destino nuevo o vacío; base de referencia abierta con `mode=ro`; no hay escrituras remotas.

## 6. Revisión cruzada independiente de salud

Se revisó el adaptador de salud de la primera ronda. Los denominadores conocidos se definían por exclusión de un único código (`IPESONAC != 9`, `ITIEMGEST != 8`), lo que podía admitir silenciosamente códigos nuevos o no reconocidos al autorizar otra edición. Se notificó al agente de salud; está cerrando whitelists de dominios y conjuntos positivos de categorías. **No se demostró que ese defecto afecte los 121 casos de la edición DEIS 2024 ya conciliados**: el problema es la admisión de futuros cambios sin bloqueo.

También se señaló que el adaptador de salud es un contrato explícito 2024: cambiar únicamente el hash para otra edición no alcanza para actualizar el año o la metodología. No se modificaron archivos ajenos.

## 7. Evidencia y reproducción

- `education_adapter.py`: entrada principal, portable por argumentos.
- `test_education_adapter.py`: 15 pruebas unitarias; todas pasan, incluyendo ejecución optimizada `-O`, rechazo de esquema/categorías/alcance ambiguos, estructura, precisión, hash de salidas y preservación de destino.
- `investigate_period_rounding.py`: genera evidencia a partir de ZIP, TWB y SQLite originales, sin escribir sobre ellos.
- `period_rounding_evidence.json`: evidencia del original fuente y XML, caso K12, fechas y 15 pares de períodos.
- `output-v3/`: salida final de esta ronda. `output-v1/` y `output-v2/` son resultados intermedios.

Las fuentes y base originales ya están en el respaldo de la primera ronda. No se requiere cuenta, API paga ni servicios externos para repetir el procesamiento. Los paths absolutos se usan solo al invocar los comandos; el código no los fija.

La próxima decisión concreta es aprobar que la salida nueva use el ciclo oficial completo 2024–2025, y definir si las series nuevas muestran el redondeo directo desde la precisión original. No se necesita inventar un dato ni ensanchar tolerancias para avanzar.
