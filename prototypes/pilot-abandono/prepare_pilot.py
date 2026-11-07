#!/usr/bin/env python3
"""Prepara el payload del piloto de abandono interanual (tablero 3.3f, indicadores D.1 a D.5).

Entradas explícitas, sin red:
- salida del adaptador educativo (`native_candidate.json`, `reconciliation.json`);
- geometría provincial de visualización validada (`provincias_v2.geojson` + su validación).

Reglas que aplica (contrato de native/integration/migration_contract.json):
- el período es el ciclo de la fuente (p. ej. 2024-2025), nunca el año de carga;
- valores tal como los publica la fuente; el redondeo a un decimal es HALF_UP explícito;
- negativos conservados; no se suma, promedia ni recorta entre territorios;
- Conurbano y Resto de Buenos Aires quedan como subdivisiones: no se mapean ni se suman a la provincia;
- cada valor lleva su estado de verificación contra la copia de Tableau, cuando existe.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

LEVELS = {"primary": "Primario", "secondary": "Secundario"}
TABLEAU_INDICATORS = {
    ("primary", "province"): ("381", "D.2 · Abandono interanual del nivel primario por jurisdicción"),
    ("secondary", "province"): ("383", "D.4 · Abandono interanual del nivel secundario por jurisdicción"),
    ("national_series", None): ("384", "D.5 · Evolución de la tasa de abandono interanual por nivel"),
    ("primary", "grade"): ("380", "D.1 · Abandono interanual por grado · nivel primario"),
    ("secondary", "grade"): ("382", "D.3 · Abandono interanual por año · nivel secundario"),
}
STATUS_LABELS = {
    "matched_at_one_decimal": "Coincide con Tableau",
    "compatible_with_double_rounding": "Coincide con doble redondeo",
    "blocked_temporal_label_conflict": "Bloqueado: Tableau lo rotula con otro ciclo",
}
NAMES = {
    "00": "Total país", "02": "CABA", "06": "Buenos Aires", "06-CON": "Conurbano bonaerense",
    "06-REST": "Resto de Buenos Aires", "10": "Catamarca", "14": "Córdoba", "18": "Corrientes",
    "22": "Chaco", "26": "Chubut", "30": "Entre Ríos", "34": "Formosa", "38": "Jujuy", "42": "La Pampa",
    "46": "La Rioja", "50": "Mendoza", "54": "Misiones", "58": "Neuquén", "62": "Río Negro", "66": "Salta",
    "70": "San Juan", "74": "San Luis", "78": "Santa Cruz", "82": "Santa Fe", "86": "Santiago del Estero",
    "90": "Tucumán", "94": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def round1(value: float) -> float:
    return float(Decimal(repr(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True, help="native_candidate.json del adaptador")
    parser.add_argument("--reconciliation", type=Path, required=True, help="reconciliation.json del adaptador")
    parser.add_argument("--geometry", type=Path, required=True, help="provincias_v2.geojson validado")
    parser.add_argument("--geometry-validation", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    reconciliation = json.loads(args.reconciliation.read_text(encoding="utf-8"))
    geometry = json.loads(args.geometry.read_text(encoding="utf-8"))
    geo_validation = json.loads(args.geometry_validation.read_text(encoding="utf-8"))

    if geo_validation.get("status") != "pass":
        raise SystemExit("La geometría no pasó la validación: el piloto no se prepara con un mapa defectuoso.")
    if geo_validation.get("display_sha256") != sha256(args.geometry):
        raise SystemExit("La validación no corresponde a este archivo de geometría.")

    # Un mismo valor de la fuente puede aparecer en más de una vista de Tableau (p. ej. el total
    # nacional 2024-2025 está en la serie D.5 y en el gráfico por grado D.1). La verificación es por
    # vista: se conservan todas las comparaciones de cada valor.
    checks_by_key: dict[str, list] = {}
    for row in reconciliation:
        checks_by_key.setdefault(row["native_key"], []).append(row)

    status_index = list(STATUS_LABELS)
    observations = []
    for obs in candidate["observations"]:
        if obs["metric"] != "interannual_dropout_rate" or obs["cell_status"] != "observed":
            continue
        checks = [
            [rec["indicator_id"], status_index.index(rec["status"]), rec["tableau_value"], rec["explicit_label"] or None]
            for rec in checks_by_key.get(obs["observation_key"], [])
        ]
        # Fila compacta: nivel, grado, estructura, código geográfico, ciclo, valor, valor visible oficial, comparaciones.
        observations.append([
            obs["level"], obs["grade_system"], obs["education_structure"], obs["geo_code"],
            obs["period_label"], obs["value"], obs["source_display_value"], checks,
        ])

    keys = Counter((o[0], o[1], o[3], o[4], o[2]) for o in observations)
    duplicates = [k for k, n in keys.items() if n > 1]
    if duplicates:
        raise SystemExit(f"Claves duplicadas en el candidato: {duplicates[:3]}")

    periods = sorted({o[4] for o in observations})
    provinces = sorted({o[3] for o in observations if len(o[3]) == 2 and o[3] != "00"})
    if len(provinces) != 24:
        raise SystemExit(f"Se esperaban 24 provincias, hay {len(provinces)}")
    geo_codes = {f["properties"]["in1"] for f in geometry["features"]}
    if set(provinces) != geo_codes:
        raise SystemExit("Los códigos provinciales de los datos y de la geometría no coinciden.")

    # Escala de color fija por nivel para todos los ciclos (política: dominio compartido entre años).
    scale = {}
    for level in LEVELS:
        values = [o[5] for o in observations if o[0] == level and o[1] == "total" and o[3] in provinces]
        # Cortes por quintiles de los valores no negativos de todos los ciclos (dominio común entre años),
        # redondeados a 0,1 para que la leyenda sea legible. Los negativos van en una clase propia.
        nonneg = sorted(v for v in values if v >= 0)
        cuts = []
        for q in (0.2, 0.4, 0.6, 0.8):
            cut = round1(nonneg[int(q * (len(nonneg) - 1))])
            if not cuts or cut > cuts[-1]:
                cuts.append(cut)
        scale[level] = {"min": min(values), "max": max(values), "negatives": sum(v < 0 for v in values), "cuts": cuts}

    status_counts = Counter(status_index[c[1]] for o in observations for c in o[7])
    payload = {
        "schema": "ladefe-pilot-abandono/1",
        "title": "Abandono escolar interanual",
        "dashboard": {
            "id": "73",
            "name": "3.3f. Matrícula de la Educación común. Indicadores educativos: Promoción efectiva y abandono escolar",
            "scope": "Sección de abandono interanual: indicadores D.1 a D.5. La sección de promoción efectiva (C.1 a C.5) queda para la siguiente iteración.",
            "indicators": {f"{k[0]}|{k[1]}": {"id": v[0], "name": v[1]} for k, v in TABLEAU_INDICATORS.items()},
        },
        "source": {
            "name": "Secretaría de Educación · Tasa de abandono interanual 2025–2012 según división político-territorial",
            "url": candidate["observations"][0]["source_url"],
            "landing": "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores",
            "sha256": candidate["observations"][0]["source_sha256"],
            "snapshot": "2026-11-06",
        },
        "levels": LEVELS,
        "periods": periods,
        "defaultPeriod": periods[-1],
        "names": NAMES,
        "provinces": provinces,
        "scale": scale,
        "statusLabels": [STATUS_LABELS[k] for k in status_index],
        "statusKeys": status_index,
        "rowFields": ["level", "grade", "structure", "geo", "period", "value", "officialDisplay", "tableauChecks[indicator, status, tableauValue, tableauLabel]"],
        "observations": observations,
        "geometry": geometry,
        "geometryCheck": {
            "sha256": geo_validation["display_sha256"],
            "invalid": geo_validation["invalid_features"],
            "overlaps": len(geo_validation["overlaps_over_0_01_km2"]),
            "maxAreaDriftPct": geo_validation["max_abs_area_drift_pct"],
            "malvinasKm2": geo_validation["malvinas_km2_epsg6933"],
        },
        "summary": {
            "observations": len(observations),
            "statusCounts": dict(status_counts),
            "valuesWithTableauCounterpart": sum(1 for o in observations if o[7]),
            "tableauComparisons": sum(status_counts.values()),
        },
        "releaseStatus": "candidate_not_approved",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    provenance = {
        "status": "prepared_candidate_not_approved",
        "network_requests_required": False,
        "inputs_sha256": {
            "candidate": sha256(args.candidate),
            "reconciliation": sha256(args.reconciliation),
            "geometry": sha256(args.geometry),
            "geometry_validation": sha256(args.geometry_validation),
        },
        "output_sha256": sha256(args.out),
        "observations": len(observations),
        "status_counts": dict(status_counts),
    }
    args.out.with_name("pilot_data_provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"observations": len(observations), "periods": len(periods), "status": dict(status_counts), "bytes": args.out.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
