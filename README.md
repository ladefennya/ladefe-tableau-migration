# LADEFE — Migración de Tableau

Prueba de factibilidad y demo técnico en validación. La cobertura 71/71 demuestra que la arquitectura común es viable; no implica todavía equivalencia estadística ni preparación para producción.

Runner de ingeniería inversa para los tableros Tableau Public actualmente embebidos en el Sistema de Monitoreo de LADEFE.

## Qué hace

1. Descarga el workbook público desde `https://public.tableau.com/workbooks/{workbook}.twb`.
2. Detecta si la respuesta es un `.twb` XML o un paquete `.twbx` ZIP.
3. Extrae la definición del workbook y los extractos `.hyper` incluidos.
4. Inventaría worksheets, dashboards, campos, cálculos, filtros, parámetros, conexiones, relaciones y acciones.
5. Abre los `.hyper` y lista schemas, tablas, columnas, cantidad de filas y una muestra pequeña de datos públicos.
6. Publica todo como artifact de GitHub Actions.

## Casos testigo

- Demografía censal
- Pobreza monetaria
- Matrícula secundaria
- Natalidad
- Justicia juvenil

## Ejecución sin Python local

Subir esta carpeta a un repositorio de GitHub y ejecutar **Actions → LADEFE Tableau probe → Run workflow**.

Al finalizar, descargar el artifact `ladefe-tableau-probe`. El archivo principal de lectura rápida es `SUMMARY.md` y las matrices detalladas son CSV.

## Salidas principales

- `workbooks.csv`: éxito/error de cada descarga y composición del paquete.
- `worksheets.csv`: hojas internas reales.
- `dashboards.csv`: dashboards y referencias de zonas/hojas.
- `fields.csv`: variables y campos calculados.
- `filters.csv`: filtros por worksheet.
- `parameters.csv`: parámetros y dominios detectados.
- `connections.csv` / `relations.csv`: metadatos útiles para identificar la fuente original.
- `hyper_tables.csv` / `hyper_columns.csv`: estructura física del extracto.
- `hyper_samples/`: muestras limitadas para interpretar semántica y granularidad.

El script redacta atributos que parezcan credenciales (`password`, `token`, `secret`, etc.).

## Contrato semántico del demo

- Cada mapa y serie utiliza exclusivamente el indicador seleccionado; no se infieren indicadores “compañeros” en el navegador.
- Porcentajes y tasas con denominador se calculan como ratio de sumas y conservan numerador y valor auxiliar.
- No se admiten promedios implícitos entre territorios, aperturas o modalidades.
- Los módulos temporal y territorial sólo aparecen cuando existe una vista propia.
- `scripts/validate_demo.py` bloquea la publicación si falla la cobertura, la integridad referencial, el cálculo testigo de AUH o el presupuesto cartográfico.

El siguiente gate del proyecto es validar una muestra arquetípica contra Tableau y con responsables temáticos antes de escalar la certificación a los 71 tableros.

## Matriz previa de los cinco pilotos

`docs/piloto_5_matriz.csv` resume la fuente de reemplazo probable y los filtros/variables que esperamos contrastar contra el `.twb/.hyper`. Sirve para distinguir qué metadatos son sustantivos y cuáles son elementos administrativos del dashboard.
