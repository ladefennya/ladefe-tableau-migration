#!/usr/bin/env bash
# Construye la geometría provincial liviana para visualización web a partir de la descarga IGN.
#
# Diferencia con scripts/prepare_map.py: aquel simplificaba cada anillo por separado con
# Douglas-Peucker, de modo que dos provincias vecinas quedaban con fronteras distintas
# (superposiciones y huecos) y 8 geometrías inválidas. Acá mapshaper construye primero la
# topología (arcos compartidos) y simplifica cada frontera una sola vez, así las provincias
# vecinas siguen encajando.
#
# Marco: continente + Islas Malvinas (lon -74.5..-52.5, lat -56..-20), el mismo que usa el demo.
# El sector antártico y las islas Georgias y Sandwich del Sur quedan fuera de este marco: ver
# INFORME_GEOMETRIA_PILOTO.md (decisión pendiente sobre el mapa bicontinental).
#
# Uso:
#   npm i mapshaper@0.6
#   native/geography/build_display_geometry.sh /ruta/ign_original_24_features.geojson /ruta/salida
#
# Requisitos de la entrada: SHA-256 9afccbbc3862d7943d9f6d83ace934f16f716eb78fb3abe1a0ad058da3c0dccc
# (descarga IGN WFS ign:provincia del 6/11/2026, ver ign_download.json).
set -euo pipefail

SRC="${1:?Falta la ruta de la geometría IGN original}"
OUT="${2:?Falta el directorio de salida}"
MAPSHAPER="${MAPSHAPER:-npx mapshaper}"
EXPECTED_SHA="9afccbbc3862d7943d9f6d83ace934f16f716eb78fb3abe1a0ad058da3c0dccc"
FRAME="-74.5,-56,-52.5,-20"
SIMPLIFY="0.5%"

actual_sha="$(sha256sum "$SRC" | cut -d' ' -f1)"
if [[ "$actual_sha" != "$EXPECTED_SHA" ]]; then
  echo "La geometría de entrada no es la edición revisada (SHA $actual_sha). Revisar antes de continuar." >&2
  exit 1
fi
mkdir -p "$OUT"
export NODE_OPTIONS="--max-old-space-size=8000"

# Referencia recortada sin simplificar: solo para validar, demasiado pesada para la web.
$MAPSHAPER -i "$SRC" snap -clip bbox="$FRAME" -clean -filter-fields in1,nam,fna \
  -o "$OUT/referencia_recortada.geojson"

# Versión de visualización: topología compartida, simplificación ponderada y precisión ~100 m.
$MAPSHAPER -i "$SRC" snap -clip bbox="$FRAME" -simplify "$SIMPLIFY" weighted keep-shapes -clean \
  -filter-fields in1,nam,fna -o "$OUT/provincias.geojson" precision=0.001

python "$(dirname "$0")/validate_display_geometry.py" \
  --display "$OUT/provincias.geojson" --reference "$OUT/referencia_recortada.geojson" \
  --out "$OUT/validacion_geometria.json"
