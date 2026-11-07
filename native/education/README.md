# Adaptador nativo de abandono interanual — v1.1.0

Implementación candidata. No publica ni reemplaza la base de la Defe. El contrato, resultados, mapeo de todos los indicadores de abandono y decisiones pendientes están en [REPORT_ROUND2.md](REPORT_ROUND2.md).

## Reproducir

Python 3.10+ y openpyxl según requirements.txt. Fuente oficial: https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip

```sh
python education_adapter.py \
  --source-zip /ruta/abandono.zip \
  --expected-sha256 18911b578fd943d3fa45fd37b5bd23d40f05543e2a0f4db325e239458c044204 \
  --reference-db /ruta/base_maestra.sqlite \
  --out /ruta/version-nueva

python -m unittest -v test_education_adapter.py

python investigate_period_rounding.py \
  --source-zip /ruta/abandono.zip \
  --reference-db /ruta/base_maestra.sqlite \
  --tableau-twb /ruta/workbook-original.twb \
  --out /ruta/evidencia-nueva.json
```

`--reference-db` y `--expected-sha256` son opcionales. El pin permite reproducir la edición revisada; no debe actualizarse sin controlar la nueva fuente. Destinos nuevos o vacíos; referencia SQLite en modo de solo lectura. En el runtime de esta sesión se utilizó `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`, también con `-O`.

## Salidas

- `native_candidate.json` / `.csv`: 5.265 celdas con ciclo inicial/final, geografía, estructura, nivel, grado acumulado, unidad, estado, precisión, valor y procedencia de archivo/hoja/celda.
- `reconciliation.json` / `.csv`: todas las 85 filas de abandono comparables de la base de referencia.
- `summary.json`, `reconciliation_summary.json`, `manifest.json`: resultados, hashes y versión.

Salida vigente de esta entrega: **output-v3/**. Las ejecuciones anteriores no son la entrega final.

Estado de cada observación: `candidate_not_approved`. Los estados de conciliación distinguen 69 coincidencias directas sin conflicto detectado, 15 filas bloqueadas por etiqueta temporal y 1 compatible con doble redondeo; ninguna comparación equivale por sí sola a publicación aprobada.

## Controles

El lector valida cabecera y dominios de estructura, geografía y grado; conserva negativos; diferencia missing/not_applicable; mantiene total nacional y provincias/subdivisiones separados; no suma ni promedia tasas. No selecciona secundaria, total o ámbito nacional por descarte de una etiqueta desconocida.

Redondeo Decimal HALF_UP explícito y sin epsilon. Se conserva el formato oficial de celda; las comparaciones de redondeo simple y doble tienen campos distintos. Los formatos de porcentaje que cambiarían la escala fallan hasta revisión. Manifest incluye SHA-256 de ZIP, miembro XLSX, referencia, código y salidas.

## Integración

Para Git, integrar código, tests, requirements, README, reporte y resumen; conservar archivos originales y outputs candidatos en respaldo. No se modificó el repo ni se abrió PR desde esta carpeta. No se revisó una interfaz renderizada ni se acredita equivalencia de UX.
