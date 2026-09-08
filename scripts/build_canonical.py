#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

HEX_SUFFIX = re.compile(r"_[0-9A-F]{16,}$", re.I)


def logical_table(value: str) -> str:
    leaf = value.rsplit(".", 1)[-1].strip('"')
    return HEX_SUFFIX.sub("", leaf).lstrip("_")


def clean_name(value: Any) -> str:
    return str(value).strip('"')


def scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def row_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def safe_file_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._").lower() or "table"


def iter_payloads(db: sqlite3.Connection, table_name: str):
    query = "SELECT payload, occurrences FROM canonical_rows WHERE table_name=? ORDER BY payload"
    for payload, occurrences in db.execute(query, (table_name,)):
        yield json.loads(payload), occurrences


def to_map(headers: list[str], values: list[Any]) -> dict[str, Any]:
    return {headers[index]: values[index] if index < len(values) else None for index in range(len(headers))}


def as_text(value: Any) -> str:
    return "" if value is None else str(value)


def as_number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--demo-workbook", default="1_1Aspectosdemogrficos_Informacincensal")
    parser.add_argument("--demo-out", type=Path, default=Path("demo/data.json"))
    args = parser.parse_args()

    try:
        from tableauhyperapi import Connection, HyperProcess, Telemetry
    except Exception as exc:
        raise SystemExit(f"tableauhyperapi unavailable: {exc}")

    canonical_dir = args.out / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = canonical_dir / "canonical.sqlite"
    if sqlite_path.exists():
        sqlite_path.unlink()

    db = sqlite3.connect(sqlite_path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")
    db.execute(
        """
        CREATE TABLE canonical_rows (
            table_name TEXT NOT NULL,
            row_hash TEXT NOT NULL,
            payload TEXT NOT NULL,
            first_source TEXT NOT NULL,
            occurrences INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (table_name, row_hash, payload)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE source_rows (
            table_name TEXT NOT NULL,
            row_hash TEXT NOT NULL,
            payload TEXT NOT NULL,
            source_workbook TEXT NOT NULL,
            PRIMARY KEY (table_name, row_hash, payload, source_workbook)
        )
        """
    )

    schemas: dict[str, list[str]] = {}
    schema_variants: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    input_counts: dict[str, int] = defaultdict(int)
    workbook_counts: dict[str, int] = defaultdict(int)

    hyper_paths = sorted((args.out / "unpacked").rglob("*.hyper"))
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as process:
        for hyper_path in hyper_paths:
            workbook = hyper_path.relative_to(args.out / "unpacked").parts[0]
            with Connection(endpoint=process.endpoint, database=str(hyper_path)) as connection:
                for schema in connection.catalog.get_schema_names():
                    for table in connection.catalog.get_table_names(schema):
                        name = logical_table(str(table))
                        definition = connection.catalog.get_table_definition(table)
                        headers = [clean_name(column.name) for column in definition.columns]
                        schema_variants[name].add(tuple(headers))
                        schemas.setdefault(name, headers)
                        if schemas[name] != headers:
                            name = f"{name}__schema_{hashlib.sha256(json.dumps(headers).encode()).hexdigest()[:8]}"
                            schemas.setdefault(name, headers)
                        rows = connection.execute_list_query(f"SELECT * FROM {table}")
                        input_counts[name] += len(rows)
                        workbook_counts[workbook] += len(rows)
                        for row in rows:
                            values = [scalar(value) for value in row]
                            payload = json.dumps(values, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
                            digest = row_hash(payload)
                            db.execute(
                                """
                                INSERT INTO canonical_rows
                                    (table_name, row_hash, payload, first_source, occurrences)
                                VALUES (?, ?, ?, ?, 1)
                                ON CONFLICT(table_name, row_hash, payload)
                                DO UPDATE SET occurrences=occurrences+1
                                """,
                                (name, digest, payload, workbook),
                            )
                            db.execute(
                                """
                                INSERT OR IGNORE INTO source_rows
                                    (table_name, row_hash, payload, source_workbook)
                                VALUES (?, ?, ?, ?)
                                """,
                                (name, digest, payload, workbook),
                            )
            db.commit()

    stats: list[dict[str, Any]] = []
    for name in sorted(schemas):
        unique_rows = db.execute(
            "SELECT COUNT(*) FROM canonical_rows WHERE table_name=?", (name,)
        ).fetchone()[0]
        source_links = db.execute(
            "SELECT COUNT(*) FROM source_rows WHERE table_name=?", (name,)
        ).fetchone()[0]
        max_occurrences = db.execute(
            "SELECT COALESCE(MAX(occurrences),0) FROM canonical_rows WHERE table_name=?", (name,)
        ).fetchone()[0]
        stats.append({
            "table": name,
            "columns": len(schemas[name]),
            "input_rows": input_counts[name],
            "unique_rows": unique_rows,
            "duplicate_rows_removed": input_counts[name] - unique_rows,
            "deduplication_pct": round(
                100 * (input_counts[name] - unique_rows) / input_counts[name], 2
            ) if input_counts[name] else 0,
            "source_links": source_links,
            "max_occurrences": max_occurrences,
            "schema_variants": len(schema_variants[name]),
        })

        destination = canonical_dir / f"{safe_file_name(name)}.csv.gz"
        with gzip.open(destination, "wt", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([*schemas[name], "_OCCURRENCES"])
            for values, occurrences in iter_payloads(db, name):
                writer.writerow([*values, occurrences])

    with (canonical_dir / "canonical_stats.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stats[0]))
        writer.writeheader()
        writer.writerows(stats)

    (canonical_dir / "schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    def records(name: str) -> list[dict[str, Any]]:
        headers = schemas.get(name, [])
        return [to_map(headers, values) for values, _ in iter_payloads(db, name)]

    tableros = records("Tableros")
    indicadores = records("Indicadores")
    grupos = records("Grupos Indicadores")
    datos = records("Datos")

    target = next(
        (
            row for row in tableros
            if as_text(row.get("TABLERO_NOMBRE")).startswith("1.1.")
        ),
        None,
    )
    if target is None:
        raise SystemExit("Could not identify demographic census dashboard in canonical Tableros")
    target_id = as_text(target.get("TABLERO_ID"))

    indicators_by_id = {
        as_text(row.get("INDICADOR_ID")): row
        for row in indicadores
        if row.get("INDICADOR_ID") is not None
    }
    groups_by_id = {
        as_text(row.get("GRUPO_INDICADOR_ID")): row
        for row in grupos
        if row.get("GRUPO_INDICADOR_ID") is not None
    }

    demo_rows: list[dict[str, Any]] = []
    used_indicators: set[str] = set()
    used_groups: set[str] = set()
    for row in datos:
        if as_text(row.get("TABLERO_ID")) != target_id:
            continue
        indicator_id = as_text(row.get("INDICADOR_ID"))
        group_id = as_text(row.get("GRUPO_INDICADOR_ID"))
        if indicator_id in ("", "0"):
            continue
        used_indicators.add(indicator_id)
        if group_id:
            used_groups.add(group_id)
        demo_rows.append({
            "indicatorId": indicator_id,
            "groupId": group_id,
            "type": row.get("TIPO_DE_DATO"),
            "year": row.get("ANIO"),
            "month": row.get("MES"),
            "geoCode": row.get("UNIDAD_GEOGRAFICA_CODIGO"),
            "geoName": row.get("UNIDAD_GEOGRAFICA_NOMBRE"),
            "subGeo": row.get("SUB_UNIDAD_GEOGRAFICA"),
            "opening": row.get("APERTURA_DESCRIPCION"),
            "level1": row.get("APERTURA_NIVEL_1"),
            "mode1": row.get("MODALIDAD_APERTURA_NIVEL_1"),
            "level2": row.get("APERTURA_NIVEL_2"),
            "mode2": row.get("MODALIDAD_APERTURA_NIVEL_2"),
            "value": as_number(row.get("VALOR")),
            "aux": row.get("VALOR_AUXILIAR"),
        })

    demo_indicators = []
    for indicator_id in sorted(used_indicators, key=lambda value: int(value) if value.isdigit() else value):
        row = indicators_by_id.get(indicator_id, {})
        demo_indicators.append({
            "id": indicator_id,
            "code": row.get("INDICADOR_CODIGO"),
            "name": row.get("INDICADOR_NOMBRE") or f"Indicador {indicator_id}",
            "unit": row.get("INDICADOR_UNIDAD_MEDIDA_NOMBRE"),
            "unitCode": row.get("INDICADOR_UNIDAD_MEDIDA_CODIGO"),
            "definition": row.get("INDICADOR_DEFINICION"),
            "methodology": row.get("INDICADOR_DESC_METODOLOGICA"),
        })

    demo_groups = []
    for group_id in sorted(used_groups, key=lambda value: int(value) if value.isdigit() else value):
        row = groups_by_id.get(group_id, {})
        demo_groups.append({
            "id": group_id,
            "code": row.get("GRUPO_INDICADOR_CODIGO"),
            "name": row.get("GRUPO_INDICADOR_NOMBRE") or f"Grupo {group_id}",
            "sources": row.get("GRUPO_INDICADOR_FUENTES"),
            "definition": row.get("GRUPO_INDICADOR_DEFINICION"),
            "methodology": row.get("GRUPO_INDICADOR_DESC_METODOLOGICA"),
        })

    demo_payload = {
        "generatedFrom": "71 Tableau workbooks",
        "workbook": args.demo_workbook,
        "dashboard": {
            "id": target_id,
            "name": target.get("TABLERO_NOMBRE"),
            "description": target.get("TABLERO_DESCRIPCION"),
            "lastDataLoad": target.get("TABLERO_FECHA_ULT_CARGA_DATOS"),
        },
        "indicators": demo_indicators,
        "groups": demo_groups,
        "rows": demo_rows,
    }
    args.demo_out.parent.mkdir(parents=True, exist_ok=True)
    args.demo_out.write_text(
        json.dumps(demo_payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    total_input = sum(row["input_rows"] for row in stats)
    total_unique = sum(row["unique_rows"] for row in stats)
    lines = [
        "# LADEFE — Canonical backend",
        "",
        f"- Hyper files processed: **{len(hyper_paths)}**",
        f"- Physical input rows: **{total_input:,}**",
        f"- Canonical unique rows: **{total_unique:,}**",
        f"- Duplicate rows removed: **{total_input - total_unique:,}**",
        f"- Global deduplication: **{100 * (total_input-total_unique)/total_input:.2f}%**",
        f"- Canonical tables: **{len(stats)}**",
        f"- Demo dashboard: **{target.get('TABLERO_NOMBRE')}** (ID {target_id})",
        f"- Demo indicators: **{len(demo_indicators)}**",
        f"- Demo data rows: **{len(demo_rows)}**",
        "",
        "## Tables",
        "",
        "| Table | Input | Unique | Removed | Deduplication |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in stats:
        lines.append(
            f"| {row['table']} | {row['input_rows']:,} | {row['unique_rows']:,} | "
            f"{row['duplicate_rows_removed']:,} | {row['deduplication_pct']:.2f}% |"
        )
    (canonical_dir / "CANONICAL_SUMMARY.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    db.commit()
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
