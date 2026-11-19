"""Build the planning overlays from the three supplied Indonesia Power Map GeoJSONs."""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

from shapely.geometry import shape

from prepare_data import ROOT, repo_path, sha256, write_json


EXPECTED = ROOT / "scripts/expected-planning-audit.json"
ATTRIBUTION = "Sitompul, S. A. (2026). Indonesia Power Map: Data Collection (v2.0.0). Plan attributes from PLN/ESDM. Mapping by IPM."
SOURCE_URL = "https://github.com/sandro71626/ipm-model"
LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"
OSM_NOTICE = "© OpenStreetMap contributors. ODbL 1.0 applies to OSM-derived material."
OSM_LICENSE = "https://opendatacommons.org/licenses/odbl/1-0/"
ADAPTATION = "MENTARI Grids adds project feature IDs and withholds geometry for unusable routes. Valid source coordinates and planning attributes retain their supplied values."

COMMON_FIELDS = (
    "id", "name", "source", "status", "province", "system",
    "target_cod_year", "cod_re_base", "cod_ared", "ruptl_page", "ruptl_row",
)
FIELDS = {
    "transmission": (
        "from_substation", "to_substation", "voltage_kv", "hvdc", "scope", "circuits",
        "length_km", "circuit_km", "line_type", "conductor", "geometry_source", "route_status",
    ),
    "substations": (
        "site_id", "scope", "voltage_kv", "voltage_label", "capacity_mva",
        "location_source", "location_confidence",
    ),
    "generators": (
        "technology", "type", "technology_label", "capacity_mw", "storage_mwh", "developer",
        "location_source", "location_confidence",
    ),
}


def map_geometry(kind, geometry, properties):
    """Keep the source geometry verbatim when there is a usable location or route."""
    if geometry is None:
        return None, "missing_geometry"
    families = ("LineString", "MultiLineString") if kind == "transmission" else ("Point",)
    if geometry.get("type") not in families:
        raise ValueError(f"{properties['id']} requires {families}, got {geometry.get('type')}")
    spatial = shape(geometry)
    if spatial.is_empty or not spatial.is_valid:
        return None, "invalid_geometry"
    west, south, east, north = spatial.bounds
    if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
        raise ValueError(f"{properties['id']} has coordinates outside longitude/latitude bounds")
    if kind == "transmission" and properties.get("route_status") == "none":
        return None, "route_status_none"
    return geometry, None


def build_collection(kind, source):
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise ValueError(f"{kind}: expected a GeoJSON FeatureCollection")
    if source.get("crs") is not None:
        raise ValueError(f"{kind}: unexpected CRS declaration; review the input before export")
    features = []
    seen = set()
    sources, statuses, confidence, route_status = Counter(), Counter(), Counter(), Counter()
    withheld = []
    fields = COMMON_FIELDS + FIELDS[kind]
    for row in source["features"]:
        properties = row.get("properties")
        if row.get("type") != "Feature" or not isinstance(properties, Mapping):
            raise ValueError(f"{kind}: expected a feature with source properties")
        for key in ("id", "name", "source", "status"):
            if not isinstance(properties.get(key), str) or not properties[key].strip():
                raise ValueError(f"{kind}: missing or invalid {key}")
        source_id = properties["id"]
        if source_id in seen:
            raise ValueError(f"{kind}: duplicate source ID {source_id}")
        seen.add(source_id)
        attributes = {key: properties[key] for key in fields if key in properties}
        for key, value in attributes.items():
            if isinstance(value, (dict, list)) or isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"{kind}: invalid {key} on {source_id}")
        geometry, reason = map_geometry(kind, row["geometry"], properties)
        if reason:
            withheld.append({"source_id": source_id, "reason": reason})
        features.append({
            "type": "Feature", "id": f"planning:{kind}:{source_id}",
            "properties": attributes, "geometry": geometry,
        })
        sources[properties["source"]] += 1
        statuses[properties["status"]] += 1
        if "location_confidence" in attributes:
            confidence[attributes["location_confidence"]] += 1
        if "route_status" in attributes:
            route_status[attributes["route_status"]] += 1

    features.sort(key=lambda item: item["id"])
    collection = {
        "type": "FeatureCollection", "attribution": ATTRIBUTION, "license": LICENSE,
        "source_url": SOURCE_URL, "osm_notice": OSM_NOTICE, "osm_license": OSM_LICENSE,
        "adaptation": ADAPTATION, "features": features,
    }
    metrics = {
        "count": len(features), "mapped": len(features) - len(withheld),
        "source_counts": dict(sorted(sources.items())),
        "geometry_issues": dict(sorted(Counter(row["reason"] for row in withheld).items())),
        "statuses": dict(sorted(statuses.items())),
    }
    if confidence:
        metrics["location_confidence"] = dict(sorted(confidence.items()))
    if route_status:
        metrics["route_status"] = dict(sorted(route_status.items()))
    return collection, metrics, withheld


def prepare(input_dir, output, qa_output):
    expected = json.loads(EXPECTED.read_bytes())
    catalog = {
        "schema_version": 1,
        "attribution": ATTRIBUTION, "source_url": SOURCE_URL, "license": LICENSE,
        "osm_notice": OSM_NOTICE, "osm_license": OSM_LICENSE, "adaptation": ADAPTATION,
        "coverage": "Project rows retain the supplied plan, status, target years, geographical labels, capacity units and geometry precision. Multiple rows can describe work at one site. Status and target years describe plans; actual commissioning requires separate evidence.",
        "datasets": {},
    }
    differences = []
    withheld = {}
    source_files = {}
    sources, statuses, target_years = set(), set(), set()
    unknown_year = False
    with tempfile.TemporaryDirectory() as directory:
        staged = Path(directory)
        for kind in FIELDS:
            path = input_dir / f"ruptl_{kind}.geojson"
            raw = path.read_bytes()
            collection, metrics, withheld[kind] = build_collection(kind, json.loads(raw))
            sources.update(metrics["source_counts"])
            statuses.update(metrics["statuses"])
            for feature in collection["features"]:
                year = feature["properties"].get("target_cod_year")
                if year is None:
                    unknown_year = True
                elif type(year) is int:
                    target_years.add(year)
                else:
                    raise ValueError(f"{feature['id']}: expected a numeric target COD year")
            digest = hashlib.sha256(raw).hexdigest()
            source_files[path] = digest
            entry = {
                "url": f"/data/planning/{kind}.geojson",
                "input": path.name,
                "input_url": f"https://indonesiapowermap.com/data/open/geojson/{path.name}",
                "source_bytes": len(raw), "source_sha256": digest, **metrics,
            }
            for key, reference in expected[kind].items():
                if entry[key] != reference:
                    differences.append({"dataset": kind, "metric": key, "expected": reference, "actual": entry[key]})
            asset = staged / f"{kind}.geojson"
            write_json(asset, collection, compact=True)
            catalog["datasets"][kind] = {**entry, "bytes": asset.stat().st_size, "sha256": sha256(asset)}

        for path, before in source_files.items():
            after = sha256(path)
            if after != before:
                raise ValueError(f"{path.name} changed during preparation: {before} -> {after}")
        write_json(qa_output / "planning-qa.json", {
            "source_unchanged": True, "audit_differences": differences,
            "withheld_geometries": withheld, "datasets": catalog["datasets"],
        })
        if differences:
            raise ValueError("Planning source-version mismatch: " + json.dumps(differences, ensure_ascii=False))
        catalog["filters"] = {
            "sources": sorted(sources), "statuses": sorted(statuses),
            "target_years": sorted(target_years), "unknown_year": unknown_year,
        }
        write_json(staged / "catalog.json", catalog)
        # Validate and serialize all three inputs before replacing any publication file.
        # Sibling temporary files inherit the output directory's Windows permissions.
        # Moving files out of TemporaryDirectory would retain its owner-only ACL.
        output.mkdir(parents=True, exist_ok=True)
        files = [f"{kind}.geojson" for kind in FIELDS] + ["catalog.json"]
        pending = []
        try:
            for filename in files:
                with tempfile.NamedTemporaryFile(dir=output, prefix=f".{filename}.", suffix=".tmp", delete=False) as temporary:
                    temporary_path = Path(temporary.name)
                    pending.append((temporary_path, output / filename))
                    temporary.write((staged / filename).read_bytes())
            for temporary_path, destination in pending:
                temporary_path.replace(destination)
        finally:
            for temporary_path, _ in pending:
                temporary_path.unlink(missing_ok=True)
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=repo_path, default=ROOT / "data/raw")
    parser.add_argument("--output", type=repo_path, default=ROOT / "public/data/planning")
    parser.add_argument("--qa-output", type=repo_path, default=ROOT / "data/qa")
    args = parser.parse_args()
    try:
        catalog = prepare(args.input_dir, args.output, args.qa_output)
    except (ValueError, OSError) as error:
        print(f"Planning preparation failed: {error}", file=sys.stderr)
        return 1
    for kind, entry in catalog["datasets"].items():
        print(f"{kind}: {entry['count']} project records, {entry['mapped']} mapped, {entry['bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
