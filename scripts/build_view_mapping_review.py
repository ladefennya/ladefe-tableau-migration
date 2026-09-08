#!/usr/bin/env python3
"""Build a review queue for related views without applying heuristic mappings."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", type=Path, default=Path("demo"))
    parser.add_argument("--out", type=Path, default=Path("output/view_mapping_candidates.csv"))
    args = parser.parse_args()
    catalog = json.loads((args.demo / "catalog.json").read_text(encoding="utf-8"))["dashboards"]
    output = []
    statuses = defaultdict(int)

    for board in catalog:
        data = json.loads((args.demo / board["data"]).read_text(encoding="utf-8"))
        indicators = {str(row["id"]): row for row in data["indicators"]}
        types = defaultdict(set)
        groups = defaultdict(set)
        for row in data["rows"]:
            indicator_id = str(row["indicatorId"])
            types[indicator_id].add(str(row.get("type") or ""))
            if row.get("groupId") not in (None, ""):
                groups[indicator_id].add(str(row["groupId"]))
        for indicator_id, indicator in indicators.items():
            for wanted in ("MAPA", "SERIE_TEMPORAL"):
                if wanted in types[indicator_id]:
                    continue
                candidates = [
                    candidate_id for candidate_id in indicators
                    if candidate_id != indicator_id
                    and wanted in types[candidate_id]
                    and groups[indicator_id].intersection(groups[candidate_id])
                ]
                same_unit = [candidate_id for candidate_id in candidates if indicators[candidate_id].get("unitCode") == indicator.get("unitCode")]
                if not candidates:
                    status = "no_candidate"
                elif len(candidates) == 1 and len(same_unit) == 1:
                    status = "review_single_same_unit"
                elif same_unit:
                    status = "review_ambiguous"
                else:
                    status = "blocked_unit_mismatch"
                statuses[status] += 1
                output.append({
                    "workbook": board["workbook"], "dashboard_slug": board["slug"],
                    "source_indicator_id": indicator_id, "source_indicator_name": indicator.get("name"),
                    "source_unit": indicator.get("unitCode"), "requested_view": wanted,
                    "group_ids": "|".join(sorted(groups[indicator_id])), "candidate_count": len(candidates),
                    "same_unit_candidate_count": len(same_unit), "candidate_ids": "|".join(candidates),
                    "candidate_names": "|".join(str(indicators[candidate_id].get("name") or "") for candidate_id in candidates),
                    "candidate_units": "|".join(str(indicators[candidate_id].get("unitCode") or "") for candidate_id in candidates),
                    "review_status": status, "approved_indicator_id": "", "reviewer": "", "review_note": "",
                })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} review rows to {args.out}: {dict(sorted(statuses.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
