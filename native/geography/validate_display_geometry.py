#!/usr/bin/env python3
"""Valida una geometría provincial de visualización contra la referencia IGN recortada.

Comprueba, sin modificar ninguna de las dos entradas:
- 24 provincias presentes, con código `in1` único;
- validez GEOS de cada geometría;
- solapamientos entre pares de provincias (área en EPSG:6933, diagnóstica);
- desvío de superficie de cada provincia respecto de la referencia;
- presencia de las Islas Malvinas dentro de Tierra del Fuego, Antártida e Islas del Atlántico Sur;
- peso del archivo para uso web.

Uso:
  python native/geography/validate_display_geometry.py \
      --display demo/provincias.geojson --reference /ruta/ref_clipped.geojson --out /ruta/salida.json

Sale con código 1 si falla algún criterio obligatorio. Las áreas son métricas técnicas, no superficies oficiales.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

from pyproj import Transformer
import numpy as np
import shapely
from shapely.geometry import box, shape
from shapely.validation import explain_validity

# Criterios de aceptación (documentados en INFORME_GEOMETRIA_PILOTO.md).
MAX_OVERLAP_KM2 = 1.0  # por par de provincias
MAX_AREA_DRIFT_PCT = 3.0  # por provincia, salvo CABA
MAX_AREA_DRIFT_PCT_CABA = 6.0  # CABA es diminuta: el redondeo pesa más
MAX_BYTES = 250_000
MALVINAS_BOX = box(-61.6, -52.6, -57.5, -50.9)  # Gran Malvina, Soledad e islas adyacentes

_TR = Transformer.from_crs(4326, 6933, always_xy=True)


def transform(_, geom):
    return shapely.transform(geom, lambda xy: np.column_stack(_TR.transform(xy[:, 0], xy[:, 1])))


TO_EQUAL_AREA = None
NAME_TO_CODE = {
    "ciudad autonoma de buenos aires": "02", "buenos aires": "06", "catamarca": "10", "cordoba": "14",
    "corrientes": "18", "chaco": "22", "chubut": "26", "entre rios": "30", "formosa": "34", "jujuy": "38",
    "la pampa": "42", "la rioja": "46", "mendoza": "50", "misiones": "54", "neuquen": "58", "rio negro": "62",
    "salta": "66", "san juan": "70", "san luis": "74", "santa cruz": "78", "santa fe": "82",
    "santiago del estero": "86", "tucuman": "90", "tierra del fuego, antartida e islas del atlantico sur": "94",
}


def code_for(props):
    if props.get("in1"):
        return str(props["in1"])
    import unicodedata
    name = unicodedata.normalize("NFD", str(props.get("nam") or "")).encode("ascii", "ignore").decode().lower().strip()
    return NAME_TO_CODE.get(name)


def load(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for feature in data["features"]:
        props = feature["properties"]
        code = code_for(props)
        if code in out:
            raise SystemExit(f"Código in1 duplicado: {code}")
        out[code] = (props.get("nam"), shape(feature["geometry"]))
    return out


INSET_PARTS = {
    # Superficie mínima (km² en EPSG:6933) que debe conservar cada parte del recuadro.
    "Península Antártica": ((-70, -70, -55, -63), 50_000),
    "Islas Orcadas del Sur": ((-47, -61.2, -44, -60.3), 200),
    "Islas Georgias del Sur": ((-38.5, -55, -35.5, -53.9), 2_500),
    "Islas Sandwich del Sur": ((-28, -59.6, -26, -56.2), 100),
}
INSET_MAX_BYTES = 60_000


def check_inset(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    features = data.get("features", [])
    if len(features) != 1 or str(features[0]["properties"].get("in1")) != "94":
        failures.append("El recuadro debe tener un único elemento: Tierra del Fuego, Antártida e Islas del Atlántico Sur (in1 94)")
        return {"failures": failures}
    geom = shape(features[0]["geometry"])
    if not geom.is_valid:
        failures.append(f"Recuadro inválido ({explain_validity(geom)})")
    lon_min, lat_min, lon_max, lat_max = geom.bounds
    if lon_min < -74.01 or lon_max > -24.99 or lat_max > -53:
        failures.append(f"El recuadro excede el sector antártico argentino y las islas del Atlántico Sur: {geom.bounds}")
    parts = {}
    for name, (bbox, min_km2) in INSET_PARTS.items():
        km2 = transform(TO_EQUAL_AREA, shapely.make_valid(geom).intersection(box(*bbox))).area / 1e6
        parts[name] = round(km2, 1)
        if km2 < min_km2:
            failures.append(f"Recuadro: falta o está incompleta la parte {name} ({km2:.0f} km²)")
    size = path.stat().st_size
    if size > INSET_MAX_BYTES:
        failures.append(f"Recuadro de {size:,} bytes > {INSET_MAX_BYTES:,}")
    return {
        "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": size,
        "valid": geom.is_valid, "parts_km2_epsg6933": parts, "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inset", type=Path, help="Recuadro bicontinental (sector antártico e islas del Atlántico Sur)")
    args = parser.parse_args()

    display, reference = load(args.display), load(args.reference)
    failures: list[str] = []
    features = []

    if set(display) != set(reference) or len(display) != 24:
        failures.append(f"Códigos distintos o cantidad != 24: {sorted(set(display) ^ set(reference))}")

    projected = {}
    for code, (name, geom) in sorted(display.items()):
        valid = geom.is_valid
        ref_geom = reference[code][1]
        area = transform(TO_EQUAL_AREA, geom).area
        ref_area = transform(TO_EQUAL_AREA, ref_geom).area
        drift = (area - ref_area) / ref_area * 100
        limit = MAX_AREA_DRIFT_PCT_CABA if code == "02" else MAX_AREA_DRIFT_PCT
        if not valid:
            failures.append(f"{name}: geometría inválida ({explain_validity(geom)})")
        if abs(drift) > limit:
            failures.append(f"{name}: desvío de superficie {drift:.2f}% > {limit}%")
        projected[code] = transform(TO_EQUAL_AREA, geom)
        features.append({
            "in1": code, "name": name, "valid": valid,
            "area_km2_epsg6933": round(area / 1e6, 1),
            "reference_area_km2_epsg6933": round(ref_area / 1e6, 1),
            "area_drift_pct": round(drift, 3),
            "vertices": len(geom.exterior.coords) if geom.geom_type == "Polygon" else sum(len(p.exterior.coords) for p in geom.geoms),
        })

    overlaps = []
    for a, b in itertools.combinations(sorted(projected), 2):
        ga, gb = projected[a], projected[b]
        if not ga.intersects(gb):
            continue
        try:
            km2 = ga.intersection(gb).area / 1e6
        except shapely.errors.GEOSException:
            # Geometría inválida: se mide sobre una versión reparada solo para diagnosticar.
            km2 = shapely.make_valid(ga).intersection(shapely.make_valid(gb)).area / 1e6
        if km2 > 0.01:
            overlaps.append({"a": display[a][0], "b": display[b][0], "km2": round(km2, 3)})
        if km2 > MAX_OVERLAP_KM2:
            failures.append(f"Solapamiento {display[a][0]}–{display[b][0]}: {km2:.2f} km²")

    tdf = display.get("94", (None, None))[1]
    malvinas_km2 = 0.0
    if tdf is not None:
        malvinas_km2 = transform(TO_EQUAL_AREA, shapely.make_valid(tdf).intersection(MALVINAS_BOX)).area / 1e6
    if malvinas_km2 < 10_000:  # superficie aproximada ~12.000 km²
        failures.append(f"Islas Malvinas ausentes o incompletas en Tierra del Fuego ({malvinas_km2:.0f} km²)")

    inset_check = None
    if args.inset:
        inset_check = check_inset(args.inset)
        failures.extend(inset_check.pop("failures"))

    size = args.display.stat().st_size
    if size > MAX_BYTES:
        failures.append(f"Archivo de {size:,} bytes > {MAX_BYTES:,}")

    result = {
        "display": str(args.display.name),
        "display_sha256": hashlib.sha256(args.display.read_bytes()).hexdigest(),
        "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
        "bytes": size,
        "criteria": {
            "max_overlap_km2_per_pair": MAX_OVERLAP_KM2,
            "max_area_drift_pct": MAX_AREA_DRIFT_PCT,
            "max_area_drift_pct_caba": MAX_AREA_DRIFT_PCT_CABA,
            "max_bytes": MAX_BYTES,
            "malvinas_min_km2": 10_000,
        },
        "invalid_features": sum(not f["valid"] for f in features),
        "overlaps_over_0_01_km2": overlaps,
        "max_abs_area_drift_pct": max(abs(f["area_drift_pct"]) for f in features),
        "malvinas_km2_epsg6933": round(malvinas_km2, 1),
        "features": features,
        "inset": inset_check,
        "failures": failures,
        "status": "pass" if not failures else "fail",
        "limitations": [
            "Áreas en EPSG:6933 con fines diagnósticos; no son superficies oficiales.",
            "La referencia es la descarga IGN recortada al marco continental + Malvinas; no incluye el sector antártico ni Georgias/Sandwich del Sur.",
            "No reemplaza la revisión visual ni la validación cartográfica oficial.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "bytes", "invalid_features", "max_abs_area_drift_pct", "malvinas_km2_epsg6933")}, ensure_ascii=False))
    for failure in failures:
        print("FALLA:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
