#!/usr/bin/env python3
"""Generate a compact, reproducible semantic audit for the published datasets."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from validate_demo import FACTORS, display_value, is_direct_index, number


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", type=Path, default=Path("demo"))
    parser.add_argument("--out", type=Path, default=Path("output/SEMANTIC_AUDIT.md"))
    args = parser.parse_args()
    catalog = json.loads((args.demo / "catalog.json").read_text(encoding="utf-8"))["dashboards"]
    totals = Counter()
    modes = Counter()
    no_map = []
    no_series = []
    missing = Counter()
    ambiguous_map_keys = 0
    ambiguous_series_keys = 0

    for item in catalog:
        data = json.loads((args.demo / item["data"]).read_text(encoding="utf-8"))
        indicators = {str(row["id"]): row for row in data["indicators"]}
        types = {row.get("type") for row in data["rows"]}
        if "MAPA" not in types:
            no_map.append(item["slug"])
        if "SERIE_TEMPORAL" not in types:
            no_series.append(item["slug"])
        totals["dashboards"] += 1
        totals["rows"] += len(data["rows"])
        totals["indicators"] += len(indicators)
        for indicator in indicators.values():
            if str(indicator.get("definition") or "").strip() in ("", ".", "---"):
                missing["definition"] += 1
            if str(indicator.get("methodology") or "").strip() in ("", ".", "---"):
                missing["methodology"] += 1
        map_keys = defaultdict(int)
        series_keys = defaultdict(int)
        for row in data["rows"]:
            indicator = indicators[str(row["indicatorId"])]
            raw = number(row.get("rawValue", row.get("value")))
            auxiliary = number(row.get("aux"))
            factor = FACTORS.get(indicator.get("unitCode"))
            if is_direct_index(indicator):
                mode = "direct-index"
            elif factor and auxiliary not in (None, 0):
                candidate = raw / auxiliary * factor if raw is not None else None
                mode = "ratio" if indicator.get("unitCode") != "PORCENTAJE" or candidate is not None and 0 <= candidate <= 100 else "direct-outlier"
            else:
                mode = "direct"
            modes[mode] += 1
            assert display_value(row, indicator) is not None
            dims = tuple(row.get(key) for key in ("geoCode", "geoName", "subGeo", "opening", "level1", "mode1", "level2", "mode2"))
            if row.get("type") == "MAPA":
                map_keys[(row["indicatorId"], row.get("year"), row.get("geoName"), dims)] += 1
            if row.get("type") == "SERIE_TEMPORAL":
                series_keys[(row["indicatorId"], row.get("year"), row.get("month"), dims)] += 1
        ambiguous_map_keys += sum(value > 1 for value in map_keys.values())
        ambiguous_series_keys += sum(value > 1 for value in series_keys.values())

    lines = [
        "# LADEFE — Semantic audit", "",
        "## Coverage", "",
        f"- Dashboards: **{totals['dashboards']}**",
        f"- Indicator links: **{totals['indicators']:,}**",
        f"- Published rows: **{totals['rows']:,}**",
        f"- Dashboards without MAPA data: **{len(no_map)}**",
        f"- Dashboards without SERIE_TEMPORAL data: **{len(no_series)}**", "",
        "## Calculation modes", "",
        f"- Ratio calculated from numerator and denominator: **{modes['ratio']:,}**",
        f"- Direct values: **{modes['direct']:,}**",
        f"- Base-100/direct indexes: **{modes['direct-index']:,}**",
        f"- Percentage ratios rejected as outliers and kept direct: **{modes['direct-outlier']:,}**", "",
        "## Blocking checks", "",
        f"- Duplicate full-dimensional MAPA keys: **{ambiguous_map_keys}**",
        f"- Duplicate full-dimensional SERIE_TEMPORAL keys: **{ambiguous_series_keys}**",
        f"- Indicators without usable definition: **{missing['definition']}**",
        f"- Indicators without usable methodology: **{missing['methodology']}**", "",
        "The browser does not infer companion indicators and does not average dimensional collisions.", "",
        "## Remaining gate", "",
        "Calculation rules must be reconciled against Tableau for the six archetypal pilots listed in `docs/PILOT_VALIDATION.md` before statistical equivalence is claimed.", "",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
