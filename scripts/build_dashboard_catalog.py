#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


UNIT_FACTORS = {
    "PORCENTAJE": 100,
    "TASA_X_CIEN": 100,
    "TASA_X_MIL": 1_000,
    "RAZON_X_DIEZMIL": 10_000,
    "TASA_X_CIENMIL": 100_000,
    "TASA_X_MILLON": 1_000_000,
}


def txt(value: Any) -> str:
    return "" if value is None else str(value)


def num(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sort_id(value: str):
    return (0, int(value)) if value.isdigit() else (1, value)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def display_value(value: Any, auxiliary: Any, unit_code: Any) -> float | None:
    numerator = num(value)
    denominator = num(auxiliary)
    factor = UNIT_FACTORS.get(txt(unit_code))
    if numerator is None:
        return None
    if factor is not None and denominator not in (None, 0):
        derived = numerator / denominator * factor
        # Some base-100 series store the already-calculated index in VALOR and
        # the baseline count in VALOR_AUXILIAR. They are not proportions.
        if txt(unit_code) == "PORCENTAJE" and not 0 <= derived <= 100:
            return numerator
        return derived
    return numerator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=Path("output/canonical"))
    parser.add_argument("--config", type=Path, default=Path("config/all_workbooks.csv"))
    parser.add_argument("--families", type=Path, default=Path("output/workbook_signatures.csv"))
    parser.add_argument("--demo", type=Path, default=Path("demo"))
    args = parser.parse_args()

    schema = json.loads((args.canonical / "schema.json").read_text(encoding="utf-8"))
    db = sqlite3.connect(args.canonical / "canonical.sqlite")
    with args.config.open(encoding="utf-8-sig", newline="") as handle:
        config = {row["workbook"]: row for row in csv.DictReader(handle)}
    with args.families.open(encoding="utf-8-sig", newline="") as handle:
        families = {row["workbook"]: row["family_id"] for row in csv.DictReader(handle)}

    def source_records(table: str, workbook: str) -> list[dict[str, Any]]:
        headers = schema[table]
        rows = db.execute(
            "SELECT payload FROM source_rows WHERE table_name=? AND source_workbook=? ORDER BY payload",
            (table, workbook),
        )
        return [dict(zip(headers, json.loads(payload))) for (payload,) in rows]

    data_dir = args.demo / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for old in data_dir.glob("*.json"):
        old.unlink()

    catalog = []
    report = ["# LADEFE — Generated dashboard catalog", ""]
    family_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    total_rows = 0
    total_indicators = 0
    empty_dashboards = []

    for workbook in config:
        dashboards = source_records("Tableros", workbook)
        indicators = source_records("Indicadores", workbook)
        groups = source_records("Grupos Indicadores", workbook)
        data = source_records("Datos", workbook)
        by_dashboard: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in data:
            board_id = txt(row.get("TABLERO_ID"))
            indicator_id = txt(row.get("INDICADOR_ID"))
            if board_id and indicator_id not in ("", "0"):
                by_dashboard[board_id].append(row)
        named_dashboards = [
            row for row in dashboards
            if txt(row.get("TABLERO_NOMBRE")).strip().lower() not in ("", "seleccione")
        ]
        named_ids = {
            txt(row.get("TABLERO_ID")) for row in named_dashboards
            if txt(row.get("TABLERO_ID")) in by_dashboard
        }
        if named_ids:
            dashboard_id = max(named_ids, key=lambda key: len(by_dashboard[key]))
        elif by_dashboard:
            dashboard_id = max(by_dashboard, key=lambda key: len(by_dashboard[key]))
        else:
            dashboard_id = txt(named_dashboards[0].get("TABLERO_ID")) if named_dashboards else (txt(dashboards[0].get("TABLERO_ID")) if dashboards else "")
            empty_dashboards.append(workbook)
        target = next((row for row in dashboards if txt(row.get("TABLERO_ID")) == dashboard_id), None)
        if target is None:
            target = dashboards[0] if dashboards else {
                "TABLERO_ID": dashboard_id,
                "TABLERO_NOMBRE": workbook,
                "TABLERO_DESCRIPCION": "Sin metadatos de tablero",
                "TABLERO_FECHA_ULT_CARGA_DATOS": None,
            }

        indicator_map = {txt(row.get("INDICADOR_ID")): row for row in indicators}
        group_map = {txt(row.get("GRUPO_INDICADOR_ID")): row for row in groups}
        rows = []
        used_indicators: set[str] = set()
        used_groups: set[str] = set()
        views_by_indicator: dict[str, set[str]] = defaultdict(set)
        for row in by_dashboard[dashboard_id]:
            indicator_id = txt(row.get("INDICADOR_ID"))
            group_id = txt(row.get("GRUPO_INDICADOR_ID"))
            used_indicators.add(indicator_id)
            if group_id:
                used_groups.add(group_id)
            row_type = row.get("TIPO_DE_DATO")
            if row_type:
                type_counts[txt(row_type)] += 1
                views_by_indicator[indicator_id].add(txt(row_type))
            indicator = indicator_map.get(indicator_id, {})
            raw_value = num(row.get("VALOR"))
            auxiliary = num(row.get("VALOR_AUXILIAR"))
            rows.append({
                "indicatorId": indicator_id, "groupId": group_id, "type": row_type,
                "sectionId": row.get("SECCION_ID"), "sectionName": row.get("SECCION_NOMBRE"),
                "sourceDataId": row.get("ID_DATO_SM"), "systemData": row.get("DATO_DE_SISTEMA"),
                "year": row.get("ANIO"), "month": row.get("MES"),
                "geoCode": row.get("UNIDAD_GEOGRAFICA_CODIGO"),
                "geoName": row.get("UNIDAD_GEOGRAFICA_NOMBRE"),
                "subGeo": row.get("SUB_UNIDAD_GEOGRAFICA"),
                "opening": row.get("APERTURA_DESCRIPCION"),
                "level1": row.get("APERTURA_NIVEL_1"),
                "mode1": row.get("MODALIDAD_APERTURA_NIVEL_1"),
                "level2": row.get("APERTURA_NIVEL_2"),
                "mode2": row.get("MODALIDAD_APERTURA_NIVEL_2"),
                "value": display_value(raw_value, auxiliary, indicator.get("INDICADOR_UNIDAD_MEDIDA_CODIGO")),
                "rawValue": raw_value, "aux": auxiliary,
            })

        payload_indicators = []
        for indicator_id in sorted(used_indicators, key=sort_id):
            row = indicator_map.get(indicator_id, {})
            payload_indicators.append({
                "id": indicator_id, "code": row.get("INDICADOR_CODIGO"),
                "name": row.get("INDICADOR_NOMBRE") or f"Indicador {indicator_id}",
                "order": row.get("INDICADOR_ORDEN"),
                "unit": row.get("INDICADOR_UNIDAD_MEDIDA_NOMBRE"),
                "unitCode": row.get("INDICADOR_UNIDAD_MEDIDA_CODIGO"),
                "unitDescription": row.get("INDICADOR_UNIDAD_MEDIDA_DESCRIPCION"),
                "formula": row.get("INDICADOR_FORMULA"),
                "definition": row.get("INDICADOR_DEFINICION"),
                "methodology": row.get("INDICADOR_DESC_METODOLOGICA"),
                "views": sorted(views_by_indicator[indicator_id]),
            })
        payload_groups = []
        for group_id in sorted(used_groups, key=sort_id):
            row = group_map.get(group_id, {})
            payload_groups.append({
                "id": group_id, "code": row.get("GRUPO_INDICADOR_CODIGO"),
                "name": row.get("GRUPO_INDICADOR_NOMBRE") or f"Grupo {group_id}",
                "order": row.get("GRUPO_INDICADOR_ORDEN"),
                "sources": row.get("GRUPO_INDICADOR_FUENTES"),
                "definition": row.get("GRUPO_INDICADOR_DEFINICION"),
                "methodology": row.get("GRUPO_INDICADOR_DESC_METODOLOGICA"),
            })

        family = families.get(workbook, "unknown")
        family_counts[family] += 1
        board_slug = slug(workbook)
        payload = {
            "generatedFrom": workbook, "family": family,
            "dashboard": {
                "id": dashboard_id, "name": target.get("TABLERO_NOMBRE"),
                "description": target.get("TABLERO_DESCRIPCION"),
                "lastDataLoad": target.get("TABLERO_FECHA_ULT_CARGA_DATOS"),
            },
            "indicators": payload_indicators, "groups": payload_groups, "rows": rows,
        }
        (data_dir / f"{board_slug}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        item = {
            "slug": board_slug, "family": family, "workbook": workbook,
            "topic": config[workbook].get("tema", ""), "url": config[workbook].get("ladefe_url", ""),
            "name": target.get("TABLERO_NOMBRE"), "description": target.get("TABLERO_DESCRIPCION"),
            "data": f"data/{board_slug}.json", "indicators": len(payload_indicators), "rows": len(rows),
        }
        catalog.append(item)
        total_rows += len(rows)
        total_indicators += len(payload_indicators)

    catalog.sort(key=lambda row: txt(row["name"]))
    (args.demo / "catalog.json").write_text(
        json.dumps({"generatedFrom": len(catalog), "dashboards": catalog}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    report.extend([
        f"- Workbooks configured: **{len(config)}**",
        f"- Dashboards generated: **{len(catalog)}**",
        f"- Dashboard datasets: **{len(list(data_dir.glob('*.json')))}**",
        f"- Indicator links: **{total_indicators:,}**",
        f"- Data rows published: **{total_rows:,}**",
        f"- Families: **{dict(sorted(family_counts.items()))}**",
        f"- Dashboards without valid data rows: **{len(empty_dashboards)}**",
        "", "## Data types", "",
    ])
    report.extend(f"- {name}: **{count:,}**" for name, count in type_counts.most_common())
    report.extend(["", "## Quality checks", "", "- Every configured workbook produced one dashboard dataset.", f"- Empty dashboards: **{', '.join(empty_dashboards) if empty_dashboards else 'none'}**.", "- Dashboard selection is based on the largest valid data partition within each source workbook.", "- Rows are isolated by source workbook, preventing collisions from reused dashboard IDs.", ""])
    (args.canonical / "CATALOG_SUMMARY.md").write_text("\n".join(report), encoding="utf-8")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
