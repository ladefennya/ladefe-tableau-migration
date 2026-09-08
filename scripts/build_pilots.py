#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

PILOTS = [
    {
        "slug": "censo-demografico",
        "workbook": "1_1Aspectosdemogrficos_Informacincensal",
        "name_prefix": "1.1.",
        "family": "F01",
    },
    {
        "slug": "condiciones-habitacionales",
        "workbook": "2_5aViviviendaCFCHabitacionales",
        "name_prefix": "2.5a",
        "family": "F02",
    },
]


def text(value: Any) -> str:
    return "" if value is None else str(value)


def number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sort_id(value: str):
    return (0, int(value)) if value.isdigit() else (1, value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=Path("output/canonical"))
    parser.add_argument("--demo", type=Path, default=Path("demo"))
    args = parser.parse_args()

    schema = json.loads((args.canonical / "schema.json").read_text(encoding="utf-8"))
    db = sqlite3.connect(args.canonical / "canonical.sqlite")

    def source_records(table: str, workbook: str) -> list[dict[str, Any]]:
        headers = schema[table]
        rows = db.execute(
            """
            SELECT payload
            FROM source_rows
            WHERE table_name=? AND source_workbook=?
            ORDER BY payload
            """,
            (table, workbook),
        )
        return [dict(zip(headers, json.loads(payload))) for (payload,) in rows]

    args.demo.mkdir(parents=True, exist_ok=True)
    data_dir = args.demo / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    catalog = []
    report = ["# LADEFE — Cross-family pilots", ""]

    for pilot in PILOTS:
        workbook = pilot["workbook"]
        dashboards = source_records("Tableros", workbook)
        target = next(
            (row for row in dashboards if text(row.get("TABLERO_NOMBRE")).lower().startswith(pilot["name_prefix"].lower())),
            None,
        )
        if target is None:
            available = ", ".join(text(row.get("TABLERO_NOMBRE")) for row in dashboards)
            raise SystemExit(f"Dashboard {pilot['name_prefix']} not found in {workbook}. Available: {available}")

        dashboard_id = text(target.get("TABLERO_ID"))
        indicators = source_records("Indicadores", workbook)
        groups = source_records("Grupos Indicadores", workbook)
        data = source_records("Datos", workbook)
        indicator_map = {text(row.get("INDICADOR_ID")): row for row in indicators}
        group_map = {text(row.get("GRUPO_INDICADOR_ID")): row for row in groups}

        rows = []
        used_indicators: set[str] = set()
        used_groups: set[str] = set()
        for row in data:
            if text(row.get("TABLERO_ID")) != dashboard_id:
                continue
            indicator_id = text(row.get("INDICADOR_ID"))
            group_id = text(row.get("GRUPO_INDICADOR_ID"))
            if indicator_id in ("", "0"):
                continue
            used_indicators.add(indicator_id)
            if group_id:
                used_groups.add(group_id)
            rows.append({
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
                "value": number(row.get("VALOR")),
                "aux": row.get("VALOR_AUXILIAR"),
            })

        payload_indicators = []
        for indicator_id in sorted(used_indicators, key=sort_id):
            row = indicator_map.get(indicator_id, {})
            payload_indicators.append({
                "id": indicator_id,
                "code": row.get("INDICADOR_CODIGO"),
                "name": row.get("INDICADOR_NOMBRE") or f"Indicador {indicator_id}",
                "unit": row.get("INDICADOR_UNIDAD_MEDIDA_NOMBRE"),
                "unitCode": row.get("INDICADOR_UNIDAD_MEDIDA_CODIGO"),
                "definition": row.get("INDICADOR_DEFINICION"),
                "methodology": row.get("INDICADOR_DESC_METODOLOGICA"),
            })

        payload_groups = []
        for group_id in sorted(used_groups, key=sort_id):
            row = group_map.get(group_id, {})
            payload_groups.append({
                "id": group_id,
                "code": row.get("GRUPO_INDICADOR_CODIGO"),
                "name": row.get("GRUPO_INDICADOR_NOMBRE") or f"Grupo {group_id}",
                "sources": row.get("GRUPO_INDICADOR_FUENTES"),
            })

        payload = {
            "generatedFrom": workbook,
            "family": pilot["family"],
            "dashboard": {
                "id": dashboard_id,
                "name": target.get("TABLERO_NOMBRE"),
                "description": target.get("TABLERO_DESCRIPCION"),
                "lastDataLoad": target.get("TABLERO_FECHA_ULT_CARGA_DATOS"),
            },
            "indicators": payload_indicators,
            "groups": payload_groups,
            "rows": rows,
        }
        destination = data_dir / f"{pilot['slug']}.json"
        destination.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        catalog.append({
            "slug": pilot["slug"],
            "family": pilot["family"],
            "workbook": workbook,
            "name": target.get("TABLERO_NOMBRE"),
            "description": target.get("TABLERO_DESCRIPCION"),
            "data": f"data/{pilot['slug']}.json",
            "indicators": len(payload_indicators),
            "rows": len(rows),
        })
        report.extend([
            f"## {target.get('TABLERO_NOMBRE')}",
            "",
            f"- Structural family: **{pilot['family']}**",
            f"- Workbook: `{workbook}`",
            f"- Dashboard ID: **{dashboard_id}**",
            f"- Indicators: **{len(payload_indicators)}**",
            f"- Data rows: **{len(rows)}**",
            "",
        ])

    (args.demo / "catalog.json").write_text(
        json.dumps({"pilots": catalog}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (args.canonical / "PILOT_SUMMARY.md").write_text("\n".join(report), encoding="utf-8")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
