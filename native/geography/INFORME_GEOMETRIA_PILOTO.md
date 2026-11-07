# Geometría provincial para visualización — v2

Resultado: **la nueva geometría pasa todos los criterios; la del demo actual falla en 40 controles**. Se reemplaza solo en el piloto; el demo publicado no se modifica en este cambio.

| Criterio | Demo actual (`demo/provincias.geojson`) | v2 (`display/provincias_v2.geojson`) |
|---|---|---|
| Geometrías válidas (GEOS) | 16 de 24 | 24 de 24 |
| Pares de provincias superpuestas (> 1 km²) | 30 (máx. Chaco–Formosa 185 km²) | 0 |
| Desvío máximo de superficie vs. IGN | 13,5 % (CABA) | 1,2 % (CABA) |
| Islas Malvinas | presentes, geometría inválida | presentes, ~11.800 km² |
| Peso | 137.873 bytes | 117.767 bytes |

Detalle completo: `display/validacion_provincias_demo_actual.json` y `display/validacion_provincias_v2.json`.

## Causa del defecto anterior

`scripts/prepare_map.py` simplificaba cada anillo por separado (Douglas-Peucker). Dos provincias vecinas comparten frontera, pero cada una la simplificaba distinto: aparecían superposiciones, huecos y autointersecciones.

## Método nuevo

`build_display_geometry.sh` usa mapshaper: arma primero la topología (arcos compartidos) y simplifica cada frontera una sola vez, de modo que las provincias vecinas siguen encajando. Pasos: verificación del SHA-256 de la descarga IGN → recorte al marco del demo (continente + Malvinas) → simplificación ponderada al 0,5 % → limpieza → precisión ~100 m. Es reproducible: la ejecución produce un archivo idéntico byte a byte.

`validate_display_geometry.py` verifica 24 códigos únicos, validez, superposiciones, desvío de superficie (≤ 3 %; ≤ 6 % para CABA), presencia de Malvinas y peso (≤ 250 KB). Sale con error si falla cualquiera.

## Límites

- Las áreas se calculan en EPSG:6933 con fines de diagnóstico; no son superficies oficiales.
- El sector antártico argentino y las islas Georgias, Sandwich y Orcadas del Sur van en un recuadro aparte (`display/antartida_recuadro_v1.geojson`, 31 KB), en proyección polar, para cumplir con el mapa bicontinental (Ley 26.651). El validador exige que estén las cuatro partes.
- No reemplaza la validación cartográfica oficial ni la revisión visual de un responsable.
- La descarga IGN original (111 MB) no se versiona en Git: está en la entrega `LADEFE_refinamiento_ronda2_evidencias_2026-11-06` del PR #3.
