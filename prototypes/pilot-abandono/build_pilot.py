#!/usr/bin/env python3
"""Construye el HTML autocontenido del piloto a partir del payload congelado. Sin red ni base de datos."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data", type=Path, required=True)
parser.add_argument("--template", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()

data_bytes = args.data.read_bytes()
payload = json.loads(data_bytes)
for field in ("observations", "geometry", "periods", "provinces", "source", "geometryCheck"):
    if field not in payload:
        raise SystemExit(f"Payload inválido: falta {field}")
if payload["geometryCheck"]["invalid"] or payload["geometryCheck"]["overlaps"]:
    raise SystemExit("La geometría del payload no está validada: no se construye el mapa.")
template = args.template.read_text(encoding="utf-8")
if template.count("__DATA__") != 1:
    raise SystemExit("La plantilla debe tener exactamente un __DATA__")
html = template.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(html, encoding="utf-8")
manifest = {
    "entrypoint": args.out.name,
    "external_dependencies": [],
    "network_requests_required": False,
    "html_sha256": hashlib.sha256(html.encode()).hexdigest(),
    "inputs_sha256": {"payload": hashlib.sha256(data_bytes).hexdigest(), "template": hashlib.sha256(args.template.read_bytes()).hexdigest()},
    "approval_status": "pilot_candidate_not_approved",
}
args.out.with_name("resources_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(args.out, len(html.encode()), "bytes")
