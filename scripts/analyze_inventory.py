#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HEX_SUFFIX = re.compile(r"_[0-9A-F]{16,}$", re.I)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def logical_table(name: str) -> str:
    leaf = name.rsplit(".", 1)[-1].strip('"')
    return HEX_SUFFIX.sub("", leaf)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    out = args.out

    table_names = [
        "workbooks", "worksheets", "dashboards", "fields", "filters",
        "parameters", "connections", "relations", "actions",
        "hyper_tables", "hyper_columns",
    ]
    tables = {name: read_csv(out / f"{name}.csv") for name in table_names}
    books = [row["workbook"] for row in tables["workbooks"]]

    by_book: dict[str, dict[str, list[dict[str, str]]]] = {}
    for book in books:
        by_book[book] = {
            name: [row for row in rows if row.get("workbook") == book]
            for name, rows in tables.items()
        }

    hyper_files: list[dict[str, Any]] = []
    for path in sorted((out / "unpacked").rglob("*.hyper")):
        rel = path.relative_to(out / "unpacked")
        book = rel.parts[0]
        hyper_files.append({
            "workbook": book,
            "hyper_file": path.name,
            "bytes": path.stat().st_size,
            "sha256": file_sha256(path),
        })
    write_csv(out / "hyper_files.csv", hyper_files)

    signatures: list[dict[str, Any]] = []
    raw_family_signatures: dict[str, str] = {}
    for book in books:
        groups = by_book[book]
        record = next(row for row in tables["workbooks"] if row["workbook"] == book)
        fields = groups["fields"]
        hyper_tables = groups["hyper_tables"]
        hyper_columns = groups["hyper_columns"]

        schema = sorted(
            (
                logical_table(row.get("table", "")),
                int(row.get("ordinal") or 0),
                row.get("column", ""),
                row.get("sql_type", ""),
                row.get("nullability", ""),
            )
            for row in hyper_columns
        )
        parameters = sorted(
            (
                row.get("caption", ""),
                row.get("datatype", ""),
                row.get("param_domain_type", ""),
                row.get("members_json", ""),
            )
            for row in groups["parameters"]
        )
        worksheet_names = sorted(row.get("worksheet", "") for row in groups["worksheets"])
        dashboard_names = sorted(row.get("dashboard", "") for row in groups["dashboards"])
        formulas = sorted(row.get("formula", "") for row in fields if row.get("formula"))
        connection_classes = sorted(row.get("attr_class", "") for row in groups["connections"])
        logical_tables = sorted(
            (logical_table(row.get("table", "")), row.get("columns", ""))
            for row in hyper_tables
        )

        family_basis = {
            "worksheets": worksheet_names,
            "dashboards": dashboard_names,
            "parameters": parameters,
            "schema": schema,
            "connection_classes": connection_classes,
            "field_count": len(fields),
            "calculated_field_count": len(formulas),
            "filter_count": len(groups["filters"]),
            "action_count": len(groups["actions"]),
        }
        family_signature = digest(family_basis)
        raw_family_signatures[book] = family_signature

        signatures.append({
            "workbook": book,
            "view": record.get("view", ""),
            "tema": record.get("tema", ""),
            "status": record.get("status", ""),
            "package_type": record.get("package_type", ""),
            "bytes": record.get("bytes", ""),
            "worksheets": len(groups["worksheets"]),
            "dashboards": len(groups["dashboards"]),
            "fields": len(fields),
            "calculated_fields": len(formulas),
            "filters": len(groups["filters"]),
            "parameters": len(groups["parameters"]),
            "connections": len(groups["connections"]),
            "relations": len(groups["relations"]),
            "actions": len(groups["actions"]),
            "hyper_tables": len(hyper_tables),
            "hyper_columns": len(hyper_columns),
            "hyper_rows": sum(int(row["rows"]) for row in hyper_tables if row.get("rows", "").isdigit()),
            "worksheet_signature": digest(worksheet_names),
            "dashboard_signature": digest(dashboard_names),
            "parameter_signature": digest(parameters),
            "formula_signature": digest(formulas),
            "schema_signature": digest(schema),
            "logical_tables": " | ".join(name for name, _ in logical_tables),
            "family_signature": family_signature,
        })

    unique_signatures = sorted(set(raw_family_signatures.values()))
    family_ids = {signature: f"F{index:02d}" for index, signature in enumerate(unique_signatures, 1)}
    for row in signatures:
        row["family_id"] = family_ids[row["family_signature"]]
    write_csv(out / "workbook_signatures.csv", signatures)

    families: list[dict[str, Any]] = []
    for signature in unique_signatures:
        members = sorted(book for book, sig in raw_family_signatures.items() if sig == signature)
        sample = next(row for row in signatures if row["workbook"] == members[0])
        families.append({
            "family_id": family_ids[signature],
            "workbooks": len(members),
            "members": " | ".join(members),
            "worksheets": sample["worksheets"],
            "dashboards": sample["dashboards"],
            "fields": sample["fields"],
            "calculated_fields": sample["calculated_fields"],
            "filters": sample["filters"],
            "parameters": sample["parameters"],
            "hyper_tables": sample["hyper_tables"],
            "hyper_columns": sample["hyper_columns"],
            "family_signature": signature,
        })
    write_csv(out / "families.csv", families)

    exact_extract_groups: dict[str, list[str]] = defaultdict(list)
    for row in hyper_files:
        exact_extract_groups[row["sha256"]].append(row["workbook"])
    exact_duplicates = [
        {
            "sha256": sha,
            "workbooks": len(members),
            "members": " | ".join(sorted(members)),
        }
        for sha, members in exact_extract_groups.items()
        if len(members) > 1
    ]
    write_csv(out / "duplicate_extracts.csv", exact_duplicates)

    sample_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    sample_root = out / "hyper_samples"
    if sample_root.exists():
        for path in sorted(sample_root.rglob("*.csv")):
            book = path.relative_to(sample_root).parts[0]
            table = logical_table(path.stem)
            sample_groups[(table, file_sha256(path))].append(book)
    sample_duplicates = [
        {
            "logical_table": table,
            "sample_sha256": sha,
            "workbooks": len(members),
            "members": " | ".join(sorted(members)),
        }
        for (table, sha), members in sample_groups.items()
        if len(members) > 1
    ]
    write_csv(out / "duplicate_samples.csv", sample_duplicates)

    ok = sum(row.get("status") == "ok" for row in tables["workbooks"])
    failed = len(tables["workbooks"]) - ok
    family_counts = Counter(row["family_id"] for row in signatures if row["status"] == "ok")
    lines = [
        "# LADEFE — Full Tableau census",
        "",
        f"- Workbooks requested: **{len(tables['workbooks'])}**",
        f"- Successfully downloaded/parsed: **{ok}**",
        f"- Failed: **{failed}**",
        f"- Structural families: **{len(family_counts)}**",
        f"- Exact duplicate Hyper groups: **{len(exact_duplicates)}**",
        f"- Repeated table-sample groups: **{len(sample_duplicates)}**",
        "",
        "## Structural families",
        "",
    ]
    for family_id, count in sorted(family_counts.items()):
        lines.append(f"- {family_id}: **{count}** workbooks")
    if failed:
        lines += ["", "## Failed workbooks", ""]
        lines += [
            f"- {row.get('workbook')}: {row.get('error', 'unknown error')}"
            for row in tables["workbooks"] if row.get("status") != "ok"
        ]
    (out / "SCALE_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
