#!/usr/bin/env python3
"""Fail CI when the published demo violates its semantic contract."""
from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from pathlib import Path

from shapely.geometry import box, shape


FACTORS = {
    "PORCENTAJE": 100,
    "TASA_X_CIEN": 100,
    "TASA_X_MIL": 1_000,
    "RAZON_X_DIEZMIL": 10_000,
    "TASA_X_CIENMIL": 100_000,
    "TASA_X_MILLON": 1_000_000,
}


def check_map_topology(geo):
    """El mapa provincial debe ser válido, sin superposiciones entre provincias y con las Islas Malvinas.

    La geometría es un archivo versionado y validado (native/geography/INFORME_GEOMETRIA_PILOTO.md);
    este control impide que una versión con fronteras simplificadas por separado vuelva al demo.
    """
    shapes = {}
    for feature in geo["features"]:
        props = feature["properties"]
        code = props.get("in1")
        assert code and code not in shapes, f"Province map needs unique in1 codes: {props.get('nam')}"
        geom = shape(feature["geometry"])
        assert geom.is_valid, f"Invalid province geometry: {props.get('nam')}"
        shapes[code] = geom
    codes = sorted(shapes)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            if shapes[a].intersects(shapes[b]):
                # ~1e-4 grados² ≈ 1 km² en estas latitudes: tolera solo el redondeo de vértices.
                overlap = shapes[a].intersection(shapes[b]).area
                assert overlap < 1e-4, f"Provinces {a} and {b} overlap ({overlap:.5f} deg²)"
    malvinas = shapes["94"].intersection(box(-61.6, -52.6, -57.5, -50.9)).area
    assert malvinas > 1.0, "The province map must include the Islas Malvinas (Ley 26.651)"


def check_bicontinental_inset(path):
    """Mapa bicontinental (Ley 26.651): recuadro con el sector antártico argentino e islas del Atlántico Sur."""
    assert path.is_file(), "Missing demo/antartida.geojson (bicontinental inset)"
    inset = json.loads(path.read_text(encoding="utf-8"))
    features = inset.get("features", [])
    assert len(features) == 1 and features[0]["properties"].get("in1") == "94", "Inset must be Tierra del Fuego, Antártida e Islas del Atlántico Sur"
    geom = shape(features[0]["geometry"])
    assert geom.is_valid, "Invalid bicontinental inset geometry"
    parts = {
        "Península Antártica": (-70, -70, -55, -63),
        "Islas Orcadas del Sur": (-47, -61.2, -44, -60.3),
        "Islas Georgias del Sur": (-38.5, -55, -35.5, -53.9),
        "Islas Sandwich del Sur": (-28, -59.6, -26, -56.2),
    }
    for name, bbox in parts.items():
        assert geom.intersection(box(*bbox)).area > 0.005, f"Bicontinental inset is missing {name}"
    assert path.stat().st_size < 60_000, "Bicontinental inset too large"


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def is_direct_index(indicator):
    metadata = " ".join(str(indicator.get(key) or "") for key in ("name", "definition", "formula"))
    normalized = "".join(char for char in unicodedata.normalize("NFD", metadata.lower()) if unicodedata.category(char) != "Mn")
    return bool(re.search(r"base\s*100|indice|variacion porcentual", normalized))


def display_value(row, indicator):
    raw = number(row.get("rawValue", row.get("value")))
    auxiliary = number(row.get("aux"))
    factor = FACTORS.get(indicator.get("unitCode"))
    if raw is None:
        return None
    if is_direct_index(indicator):
        return number(row.get("value", raw))
    if factor and auxiliary not in (None, 0):
        derived = raw / auxiliary * factor
        if indicator.get("unitCode") != "PORCENTAJE" or 0 <= derived <= 100:
            return derived
    return number(row.get("value", raw))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", type=Path, default=Path("demo"))
    parser.add_argument("--expected-dashboards", type=int, default=71)
    args = parser.parse_args()
    catalog = json.loads((args.demo / "catalog.json").read_text(encoding="utf-8"))
    dashboards = catalog.get("dashboards", [])
    assert len(dashboards) == args.expected_dashboards, f"Expected {args.expected_dashboards} dashboards, got {len(dashboards)}"

    total_rows = 0
    derived_rows = 0
    for item in dashboards:
        path = args.demo / item["data"]
        assert path.is_file(), f"Missing dataset: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("rows"), f"Empty dataset: {path}"
        indicators = {str(row["id"]): row for row in data.get("indicators", [])}
        assert indicators, f"No indicators: {path}"
        for row in data["rows"]:
            total_rows += 1
            indicator = indicators.get(str(row.get("indicatorId")))
            assert indicator is not None, f"Orphan indicator in {path}: {row.get('indicatorId')}"
            value = display_value(row, indicator)
            assert value is not None, f"Non-numeric display value in {path}"
            if FACTORS.get(indicator.get("unitCode")) and number(row.get("aux")) not in (None, 0) and value != number(row.get("value")):
                derived_rows += 1

    geo_path = args.demo / "provincias.geojson"
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    assert len(geo.get("features", [])) == 24, "Province map must contain 24 jurisdictions"
    assert geo_path.stat().st_size < 250_000, f"Province map too large: {geo_path.stat().st_size:,} bytes"
    check_map_topology(geo)
    check_bicontinental_inset(args.demo / "antartida.geojson")

    auh = json.loads((args.demo / "data/2-2bauh.json").read_text(encoding="utf-8"))
    indicators = {str(row["id"]): row for row in auh["indicators"]}
    buenos_aires = next(row for row in auh["rows"] if str(row["indicatorId"]) == "218" and row.get("geoName") == "BUENOS AIRES")
    actual = display_value(buenos_aires, indicators["218"])
    assert math.isclose(actual, 34.15, abs_tol=0.02), f"AUH coverage regression: {actual}"

    app = (args.demo / "app.js").read_text(encoding="utf-8")
    assert "function companion" not in app, "Heuristic companion views must not return"
    assert "/a.length" not in app and "/items.length" not in app, "Implicit arithmetic means must not return"
    assert "currentIndicator()?.id)!==indicatorId" not in app, "Related maps must not be discarded after geometry loads"
    assert (args.demo / "view-relations.json").is_file(), "Missing explicit curated view relations"
    assert "view-relations.json" in app, "Demo must load explicit curated view relations"
    assert (args.demo / "map-utils.js").is_file(), "Missing tested map projection utilities"
    assert "LadefeMap" in app, "Demo must use the tested map projection utilities"
    assert "antartida.geojson" in app and "paintInset" in app, "Demo maps must draw the bicontinental inset"
    assert (args.demo / "ui-utils.js").is_file(), "Missing tested navigation utilities"
    assert "LadefeUI" in app, "Demo must use the tested navigation utilities"
    html = (args.demo / "index.html").read_text(encoding="utf-8")
    assert 'id="mapOnly"' in html, "Demo must expose the map-only indicator filter"
    assert 'id="capabilities"' in html, "Demo must explain indicator capabilities"
    print(f"Validated {len(dashboards)} dashboards, {total_rows:,} rows, {derived_rows:,} derived display values and a {geo_path.stat().st_size:,}-byte map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
