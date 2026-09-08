#!/usr/bin/env python3
"""Fail CI when the published demo violates its semantic contract."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


FACTORS = {
    "PORCENTAJE": 100,
    "TASA_X_CIEN": 100,
    "TASA_X_MIL": 1_000,
    "RAZON_X_DIEZMIL": 10_000,
    "TASA_X_CIENMIL": 100_000,
    "TASA_X_MILLON": 1_000_000,
}


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def display_value(row, indicator):
    raw = number(row.get("rawValue", row.get("value")))
    auxiliary = number(row.get("aux"))
    factor = FACTORS.get(indicator.get("unitCode"))
    if raw is None:
        return None
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

    auh = json.loads((args.demo / "data/2-2bauh.json").read_text(encoding="utf-8"))
    indicators = {str(row["id"]): row for row in auh["indicators"]}
    buenos_aires = next(row for row in auh["rows"] if str(row["indicatorId"]) == "218" and row.get("geoName") == "BUENOS AIRES")
    actual = display_value(buenos_aires, indicators["218"])
    assert math.isclose(actual, 34.15, abs_tol=0.02), f"AUH coverage regression: {actual}"

    app = (args.demo / "app.js").read_text(encoding="utf-8")
    assert "function companion" not in app, "Heuristic companion views must not return"
    assert "/a.length" not in app and "/items.length" not in app, "Implicit arithmetic means must not return"
    print(f"Validated {len(dashboards)} dashboards, {total_rows:,} rows, {derived_rows:,} derived display values and a {geo_path.stat().st_size:,}-byte map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
