# Revisión especializada de salud — segunda ronda

## Fuentes primarias incorporadas

Se descargaron y leyeron el Anuario DEIS2024 v2 y los dos diccionarios oficiales. URLs, tamaños y SHA-256 figuran en `evidence/official_methodology_2024.json`. El PDF pesa11.867.228 bytes. Se extrajo texto con Poppler y se inspeccionó visualmente la página46 para verificar el encabezado, denominador y nota del Cuadro6.

- **Peso:** Cuadro6,p46: porcentajes sobre nacidos vivos de peso especificado. El numerador de bajo peso es<2.500 gramos, incluyendo2.000–2.499. Respalda exactamente los24 denominadores conciliados.
- **Gestación:** Cuadro7,p47 y Cuadro8,p48 publican subtotales pretérmino y no especificados. Coinciden los24 componentes de Tableau con el denominador de gestación conocida. No se halló una nota inequívoca sobre el porcentaje en esta publicación; no se interpreta la mera coincidencia como aprobación de la fórmula.
- **Materna:** PDFp29–30 define razón anual por10.000 nacidos vivos y excluye muertes maternas tardías. `descdef1.xlsx`,hojaMAT distingueM,T,S yNulo. Se conservan por separado.
- **Edad infantil NS:** CSVcontiene031.Menorde1 año,sin especificar; Cuadro21,p61 identifica un caso de menor de un año de edad precisa ysexo no especificados. Se incluye en infantil global; no se atribuye a neonatal/postneonatal.
- **Tiempo:** PDFp12 define nacimientos registrados, incluyendo ocurrencias del año inmediato anterior que se registran en el año de referencia; no equivalen a «todos ocurridos2024».
- **Diccionarios incompletos:** SEXO3 está en losCSV, pero no se define en las fichas descargadas (solo1,2,9). Se preservan6 nacimientos/10 defunciones sin label semántico. Los totales pueden incluirlo; el desglose categorizado queda bloqueado.

No se copiaron los archivos fuente grandes al repo; las referencias permiten recuperarlos y verificar su edición.

## Conciliación y condiciones de aceptación

121/121 comparaciones exactas de componentes permanecen. No es una certificación de14 tablerosni de visualizaciones. Solo97 casos están respaldados aquí por conciliación y documentación primaria pertinente (72 infantiles+24 peso+1 nacimiento);24 pretérmino requieren decisión del denominador. Los primeros97 tampoco tienen aprobación temática humana ni interfaz aprobada, por lo que siguen candidatos.

Se agregó una comparación separada de razón materna anual2024:183 M,81 Tseparadas y413.135 nacidos vivos;183/413135×10000=4,4295448219, equivalente al4,4 de Tableau a1 decimal. No se suma como coincidencia exacta de componentes porque Tableau conserva aquí el valor final anual. Esta prueba sí evita incluir tardías: conM+T la razón sería distinta.

## Extensiones estrictas

| Medida | Qué hace falta | Qué no se puede hacer |
|---|---|---|
| Natalidad por provincia/año | Población total por residencia y año, edición de proyecciones y método de tasa idénticos; conservar versión del denominador | Usar nacimientos como población o sustituir sin declarar proyecciones2010 por 2022. |
| Fecundidad10–14/15–19 | Nacimientos por edad materna compatible y población femenina del mismo grupo/año/jurisdicción; nota que defina menores15 vs10–14 | Desagregar mujeres15–17 de15–19; asignar todos los nacimientos de menores15 a10–14 sin validación. |
| Razón materna trianual2022–2024 | Archivos2022,2023,2024, códigosMAT y registro compatibles; suma deM/suma de nacidos vivos×10000 | Promediar tres razones anuales o usar solo2024; el nombre de Tableau«(%)»no modifica su factor10000. |
| Causas adolescentes | Clasificación CIE versionada, edades exactas, inclusión/exclusión de secuelas y denominador | Suponer que todoX60–X84 resuelve por sí solo todas las fichas de suicidio; repartir grupos15–19 a0–17. |
| Prevalencia de encuestas ENNyS | Pesos, dominios, módulos y puntos de corte aprobados para la edición | Aplicar frecuencia anual de registros administrativos ni dibujar mapas provinciales fuera de la representatividad muestral. |

## Mejoras implementadas

- Contrato de versión2024 ylista de hashes aprobados: parámetro de hash no puede habilitar una revisión distinta sin versionar contrato.
- Whitelist de categorías completas de peso, gestación, edad y otros campos; falla ante códigonuevo. Resuelve el riesgo observado por educación,social yestadística: la lógica anterior«distintoNS»podía admitir un desconocido como válido.
- Conservación por separado de maternaM/tardíaT/secuelaS; sin razón trianual fabricada.
- Proveniencia conhash del adaptador, contrato y base comparada y manifest de outputs; directorio de salida nuevo/vacío obligatorio.
-16 tests unitarios aprobados, incluyendo `python -O`, límite2499, códigos desconocidos, fuente vacía, override de hash, no redistribuciónNSy no fabricación de tasa poblacional.

## Revisión cruzada de otros adaptadores (repo previo, solo lectura)

**Educación:** el reconciliador de indicador384 usaba«si contieneprimari ->primaria;enotrocasosecundaria». Una etiqueta nueva/vacía podría asignarse a secundaria. Se informó a educación para failclosed. También el lookup usaba período/geo/nivel/grado sin estructura educativa mientras la clave nativa sí la incluye: exigir unicidad de esa proyección o pasar estructura para impedir sobrescritura futura. No se afirma error en los resultados ya cotejados. Los conflictos de rótulo temporal ya se bloquean correctamente y no deben resolverse por coincidencia numérica.

**SocialEPHU:** reconoce año 2025/T3 ycategorías explícitasCH15; es correcto comparar el mismo universo. El caso0–17 no debe aprobarse si el códigoCH06=-1 no está definido por la ficha2025; conservar sensibilidad1–17 vs-1–17 y faltantes. Nunca proyectar la agregación nacional como representativa de cada provincia sin revisar diseño. El denominador de respuestas válidas vs total con NSes una decisión metodológica explícita, no un arreglo para obtener100%. La identificación de personas evita duplicados, pero no equivale a tener varianzas/diseño completos para inferencia.

## Próximo paso

Cerrar decisión semántica de gestación y código SEXO3 con ficha/DEIS o responsable temático; después comparar las cinco medidas y razón materna anual en la interfaz nativa renderizada, conservando los122 casos como121 componentes+1 valor redondeado, y ampliar historia mediante contratos por edición. No hubo publicación ni modificación de la base original.
