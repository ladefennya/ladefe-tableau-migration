#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def distance(point, start, end):
    x, y = point
    x1, y1 = start
    x2, y2 = end
    if (x1, y1) == (x2, y2):
        return (x - x1) ** 2 + (y - y1) ** 2
    t = max(0, min(1, ((x-x1)*(x2-x1)+(y-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)))
    return (x-(x1+t*(x2-x1)))**2 + (y-(y1+t*(y2-y1)))**2


def simplify(points, tolerance=0.018):
    if len(points) <= 4:
        return points
    closed = points[0] == points[-1]
    work = points[:-1] if closed else points
    if len(work) <= 3:
        return points
    start, end = work[0], work[-1]
    distances = [distance(point, start, end) for point in work[1:-1]]
    maximum = max(distances, default=0)
    if maximum > tolerance * tolerance:
        index = distances.index(maximum) + 1
        result = simplify(work[:index+1], tolerance)[:-1] + simplify(work[index:], tolerance)
    else:
        result = [start, end]
    if closed:
        result.append(result[0])
    return result if len(result) >= 4 else points


def in_argentina(ring):
    return any(-74.5 <= point[0] <= -52.5 and -56 <= point[1] <= -20 for point in ring)


def clean_geometry(geometry):
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates", [])
    if kind == "Polygon":
        rings = [simplify(ring) for ring in coordinates if in_argentina(ring)]
        return {"type": "Polygon", "coordinates": rings}
    if kind == "MultiPolygon":
        polygons = []
        for polygon in coordinates:
            rings = [simplify(ring) for ring in polygon if in_argentina(ring)]
            if rings:
                polygons.append(rings)
        return {"type": "MultiPolygon", "coordinates": polygons}
    return geometry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    features = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = clean_geometry(feature.get("geometry") or {})
        if geometry.get("coordinates"):
            features.append({
                "type": "Feature",
                "properties": {"nam": props.get("nam") or props.get("nombre"), "fna": props.get("fna")},
                "geometry": geometry,
            })
    output = {"type": "FeatureCollection", "features": features}
    args.destination.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if len(features) < 23:
        raise SystemExit(f"Expected at least 23 province features, got {len(features)}")
    print(f"Prepared {len(features)} province features: {args.destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
