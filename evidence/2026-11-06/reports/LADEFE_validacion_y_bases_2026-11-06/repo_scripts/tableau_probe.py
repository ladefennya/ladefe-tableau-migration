#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import shutil
import sys
import traceback
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET

import requests

UA = "LADEFE-Tableau-Migration-Probe/0.3 (+technical inventory; public Tableau content)"
SENSITIVE_KEYS = {"password", "passwd", "pwd", "token", "secret", "credential", "oauth", "apikey", "api_key"}


def local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


def elements(root: ET.Element, tag: str) -> Iterable[ET.Element]:
    for el in root.iter():
        if local(el.tag) == tag:
            yield el


def clean_attrs(attrs: dict[str, str]) -> dict[str, str]:
    out = {}
    for k, v in attrs.items():
        kl = k.lower()
        if any(s in kl for s in SENSITIVE_KEYS):
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def safe_name(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("._")
    return s[:150] or "unnamed"


def download_workbook(session: requests.Session, workbook: str, dest: Path) -> tuple[Path, dict[str, Any]]:
    # Tableau Public community-documented download route. It can return XML (.twb)
    # or a packaged ZIP (.twbx) despite the .twb suffix.
    url = f"https://public.tableau.com/workbooks/{workbook}.twb"
    r = session.get(url, timeout=90, allow_redirects=True)
    meta = {
        "download_url": url,
        "final_url": r.url,
        "http_status": r.status_code,
        "content_type": r.headers.get("content-type", ""),
        "content_disposition": r.headers.get("content-disposition", ""),
        "bytes": len(r.content),
    }
    r.raise_for_status()
    if len(r.content) < 500:
        raise RuntimeError(f"Download too small ({len(r.content)} bytes): {r.text[:300]!r}")
    dest.write_bytes(r.content)
    return dest, meta


def unpack_download(downloaded: Path, workdir: Path) -> tuple[list[Path], list[Path], str]:
    workdir.mkdir(parents=True, exist_ok=True)
    head = downloaded.read_bytes()[:4]
    if head[:2] == b"PK":
        with zipfile.ZipFile(downloaded) as z:
            z.extractall(workdir)
        kind = "twbx_zip"
    else:
        # Raw TWB XML
        twb = workdir / (downloaded.stem + ".twb")
        shutil.copy2(downloaded, twb)
        kind = "twb_xml"
    twbs = sorted(workdir.rglob("*.twb"))
    hypers = sorted(workdir.rglob("*.hyper"))
    if not twbs:
        raise RuntimeError("No .twb definition found after download/unpack")
    return twbs, hypers, kind


def parse_twb(twb: Path, workbook: str, view: str) -> dict[str, list[dict[str, Any]]]:
    root = ET.parse(twb).getroot()
    base = {"workbook": workbook, "requested_view": view, "twb_file": twb.name}
    out: dict[str, list[dict[str, Any]]] = {
        "worksheets": [], "dashboards": [], "fields": [], "filters": [],
        "parameters": [], "connections": [], "relations": [], "actions": []
    }

    # Datasources + fields + connections + relations
    for ds in elements(root, "datasource"):
        dsname = ds.attrib.get("caption") or ds.attrib.get("name") or ""
        ds_internal = ds.attrib.get("name", "")
        is_param_ds = "parameter" in dsname.lower() or "parameter" in ds_internal.lower()
        for col in [x for x in ds.iter() if local(x.tag) == "column"]:
            calc = next((x for x in col.iter() if local(x.tag) == "calculation"), None)
            attrs = clean_attrs(col.attrib)
            row = {
                **base,
                "datasource": dsname,
                "datasource_internal": ds_internal,
                "field_name": attrs.get("name", ""),
                "caption": attrs.get("caption", ""),
                "datatype": attrs.get("datatype", ""),
                "role": attrs.get("role", ""),
                "type": attrs.get("type", ""),
                "aggregation": attrs.get("aggregation", ""),
                "semantic_role": attrs.get("semantic-role", ""),
                "hidden": attrs.get("hidden", ""),
                "param_domain_type": attrs.get("param-domain-type", ""),
                "calculation_class": calc.attrib.get("class", "") if calc is not None else "",
                "formula": calc.attrib.get("formula", "") if calc is not None else "",
            }
            out["fields"].append(row)
            if is_param_ds or attrs.get("param-domain-type"):
                members = []
                for m in [x for x in col.iter() if local(x.tag) == "member"]:
                    members.append(clean_attrs(m.attrib))
                out["parameters"].append({**row, "members_json": json.dumps(members, ensure_ascii=False)})
        for conn in [x for x in ds.iter() if local(x.tag) == "connection"]:
            out["connections"].append({
                **base, "datasource": dsname,
                **{f"attr_{k}": v for k, v in clean_attrs(conn.attrib).items()}
            })
        for rel in [x for x in ds.iter() if local(x.tag) == "relation"]:
            out["relations"].append({
                **base, "datasource": dsname,
                **{f"attr_{k}": v for k, v in clean_attrs(rel.attrib).items()}
            })

    # Worksheets, their datasource deps and filters
    for ws in elements(root, "worksheet"):
        wsname = ws.attrib.get("name", "")
        deps = []
        for dep in [x for x in ws.iter() if local(x.tag) == "datasource-dependencies"]:
            deps.append(dep.attrib.get("datasource", ""))
        filters = [x for x in ws.iter() if local(x.tag) == "filter"]
        out["worksheets"].append({
            **base, "worksheet": wsname,
            "datasources": " | ".join(sorted(set(filter(None, deps)))),
            "filters_count": len(filters),
        })
        for fil in filters:
            fattrs = clean_attrs(fil.attrib)
            group_filters = [clean_attrs(x.attrib) for x in fil.iter() if local(x.tag) == "groupfilter"]
            out["filters"].append({
                **base, "worksheet": wsname,
                "column": fattrs.get("column", ""),
                "class": fattrs.get("class", ""),
                "filter_attrs_json": json.dumps(fattrs, ensure_ascii=False),
                "group_filters_json": json.dumps(group_filters, ensure_ascii=False),
            })

    # Dashboards and sheet references in zones
    for db in elements(root, "dashboard"):
        dbname = db.attrib.get("name", "")
        zones = []
        for z in [x for x in db.iter() if local(x.tag) == "zone"]:
            za = clean_attrs(z.attrib)
            zones.append(za)
        candidate_refs = sorted({
            v for z in zones for k, v in z.items()
            if k in {"name", "sheet", "param"} and isinstance(v, str) and v
        })
        out["dashboards"].append({
            **base, "dashboard": dbname,
            "zone_count": len(zones),
            "candidate_sheet_refs": " | ".join(candidate_refs),
            "zones_json": json.dumps(zones, ensure_ascii=False),
        })

    # Actions (dashboard filter/highlight/url actions are often revealing)
    for actions in elements(root, "actions"):
        for child in list(actions):
            out["actions"].append({
                **base,
                "action_tag": local(child.tag),
                "attrs_json": json.dumps(clean_attrs(child.attrib), ensure_ascii=False),
            })

    return out


def inspect_hyper(hyper_path: Path, workbook: str, outdir: Path, sample_rows: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        from tableauhyperapi import HyperProcess, Connection, Telemetry
    except Exception as e:
        return ([{"workbook": workbook, "hyper_file": hyper_path.name, "error": f"tableauhyperapi unavailable: {e}"}], [])

    table_rows: list[dict[str, Any]] = []
    column_rows: list[dict[str, Any]] = []
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(endpoint=hp.endpoint, database=str(hyper_path)) as cx:
            for schema in cx.catalog.get_schema_names():
                for table in cx.catalog.get_table_names(schema):
                    tdef = cx.catalog.get_table_definition(table)
                    try:
                        count = cx.execute_scalar_query(f"SELECT COUNT(*) FROM {table}")
                    except Exception as e:
                        count = f"ERROR: {e}"
                    table_rows.append({
                        "workbook": workbook,
                        "hyper_file": hyper_path.name,
                        "schema": str(schema),
                        "table": str(table),
                        "rows": count,
                        "columns": len(tdef.columns),
                    })
                    for ordinal, col in enumerate(tdef.columns, 1):
                        column_rows.append({
                            "workbook": workbook,
                            "hyper_file": hyper_path.name,
                            "schema": str(schema),
                            "table": str(table),
                            "ordinal": ordinal,
                            "column": str(col.name),
                            "sql_type": str(col.type),
                            "nullability": str(col.nullability),
                        })
                    # Small public-data sample for schema/semantic inspection.
                    sample_dir = outdir / "hyper_samples" / safe_name(workbook)
                    sample_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        rows = cx.execute_list_query(f"SELECT * FROM {table} LIMIT {int(sample_rows)}")
                        sample_path = sample_dir / f"{safe_name(str(schema))}__{safe_name(str(table))}.csv"
                        with sample_path.open("w", newline="", encoding="utf-8-sig") as f:
                            w = csv.writer(f)
                            w.writerow([str(c.name) for c in tdef.columns])
                            for row in rows:
                                w.writerow(["" if v is None else str(v) for v in row])
                    except Exception as e:
                        err = sample_dir / f"{safe_name(str(schema))}__{safe_name(str(table))}.error.txt"
                        err.write_text(str(e), encoding="utf-8")
    return table_rows, column_rows


def load_config(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    needed = {"workbook", "view"}
    if not rows or not needed.issubset(rows[0]):
        raise ValueError(f"Config must include {sorted(needed)}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("output"))
    ap.add_argument("--sample-rows", type=int, default=25)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw_dir = args.out / "raw"
    unpack_dir = args.out / "unpacked"
    raw_dir.mkdir(exist_ok=True)
    unpack_dir.mkdir(exist_ok=True)

    config = load_config(args.config)
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "*/*"})

    tables: dict[str, list[dict[str, Any]]] = {k: [] for k in [
        "workbooks", "worksheets", "dashboards", "fields", "filters", "parameters",
        "connections", "relations", "actions", "hyper_tables", "hyper_columns"
    ]}

    for i, item in enumerate(config, 1):
        wb, view = item["workbook"].strip(), item["view"].strip()
        print(f"[{i}/{len(config)}] {wb}/{view}", flush=True)
        rec = {
            "workbook": wb, "view": view, "tema": item.get("tema", ""),
            "ladefe_url": item.get("ladefe_url", ""),
            "status": "started"
        }
        try:
            dl = raw_dir / f"{safe_name(wb)}.download"
            _, meta = download_workbook(session, wb, dl)
            twbs, hypers, kind = unpack_download(dl, unpack_dir / safe_name(wb))
            rec.update(meta)
            rec.update({"package_type": kind, "twb_count": len(twbs), "hyper_count": len(hypers)})
            for twb in twbs:
                parsed = parse_twb(twb, wb, view)
                for k, rows in parsed.items():
                    tables[k].extend(rows)
            for hp in hypers:
                tr, cr = inspect_hyper(hp, wb, args.out, args.sample_rows)
                tables["hyper_tables"].extend(tr)
                tables["hyper_columns"].extend(cr)
            rec["status"] = "ok"
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["traceback"] = traceback.format_exc(limit=8)
            print(rec["error"], file=sys.stderr, flush=True)
        tables["workbooks"].append(rec)

    for name, rows in tables.items():
        write_csv(args.out / f"{name}.csv", rows)

    # Machine-readable full report.
    report = {
        "config": str(args.config),
        "counts": {k: len(v) for k, v in tables.items()},
        "workbooks": tables["workbooks"],
    }
    (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Human summary focused on migration feasibility.
    ok = [r for r in tables["workbooks"] if r.get("status") == "ok"]
    fail = [r for r in tables["workbooks"] if r.get("status") != "ok"]
    formulas = sum(1 for r in tables["fields"] if r.get("formula"))
    param_names = [r.get("caption") or r.get("field_name") for r in tables["parameters"]]
    lines = [
        "# LADEFE — Tableau probe", "",
        f"- Workbooks requested: **{len(config)}**",
        f"- Successfully downloaded/parsed: **{len(ok)}**",
        f"- Failed: **{len(fail)}**",
        f"- Worksheets found: **{len(tables['worksheets'])}**",
        f"- Dashboards found: **{len(tables['dashboards'])}**",
        f"- Fields found: **{len(tables['fields'])}**",
        f"- Calculated fields found: **{formulas}**",
        f"- Filters found: **{len(tables['filters'])}**",
        f"- Parameters found: **{len(tables['parameters'])}**",
        f"- Hyper tables found: **{len(tables['hyper_tables'])}**", "",
        "## Parameters", "",
        *(f"- {p}" for p in sorted(set(filter(None, param_names))))
    ]
    if fail:
        lines += ["", "## Failures", ""] + [f"- {r['workbook']}: {r.get('error','unknown')}" for r in fail]
    (args.out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Done. Results in {args.out}")
    # Do not fail the workflow merely because one workbook is unavailable; the report records it.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
