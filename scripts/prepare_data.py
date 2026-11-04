"""Deterministic, read-only OSM GeoPackage -> D2 publication subsets.

Relative CLI paths are resolved from the repository, independently of cwd.
Historic audit values are comparison targets, never selection predicates.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import sqlite3
import sys

import geopandas as gpd
import pandas as pd
import pyogrio
from pyproj import Geod
import shapely
from shapely.geometry import mapping, shape

ROOT = Path(__file__).resolve().parents[1]
TARGET_V = frozenset({500_000, 275_000, 150_000, 70_000})
STATUSES = ("not_flagged_in_osm", "tagged_construction", "tagged_disused", "conflicting_tags")
PIPELINE_VERSION = "1.2.0"
GEOD = Geod(ellps="WGS84")
LICENSE_URL = "https://opendatacommons.org/licenses/odbl/1-0/"
ATTRIBUTION = "© OpenStreetMap contributors; export via OpenInfraMap. ODbL 1.0."
LIMITATIONS = [
    "Preliminary OSM-based inventory; source-tagged transmission is not official GI/GITET validation.",
    "Not flagged in OSM does not establish existing or operational status.",
    "Source data vintage is unknown; file modification time is not an OSM snapshot date.",
    "Features are mapped segments/polygons, not unique circuits, corridors or verified stations.",
    "Power plants are OSM footprints, not generators or verified unique stations. Source output has no supplied unit; start_date is not verified COD. Plants have no voltage/disused field.",
    "Review candidates are unvalidated, separate from primary inventory and off by default.",
    "Source points are matched against all polygons; only eligible distinct point-only candidates are published separately, off by default. Voltage/function/identity remain unverified.",
    "No authoritative planned RUPTL/RUKN projects, region or power-system crosswalk was supplied.",
    "COD, official circuit-km, MVA, capacity, thermal rating, AIS/GIS and verified HVDC are unavailable.",
    "Cross-layer duplicates, electrical topology and registry completeness have not been validated.",
]
FIELD_MEANINGS = {
    "plant_source": "Original power_plant.source energy-source tag; not a new dataset attribution.",
    "plant_method": "Original generation method tag, unverified.",
    "plant_output_raw": "Original numeric output; unit unspecified in this export. Not assumed MW or verified capacity.",
    "plant_output_unit": "Null: no output unit supplied by the source export.",
    "plant_start_date_raw": "Original start_date string, including approximate/partial dates; not verified COD.",
    "plant_name_en": "Original English-name tag or null.",
    "plant_description": "Original description or null.",
    "plant_wikidata": "Original Wikidata identifier or null; not an authoritative station ID.",
    "plant_representative_point": "Derived point_on_surface coordinates inside the original footprint; display only, never another inventory record.",
    "feature_id": "Unique original inventory/review record <source_layer>:<original id>; negative IDs preserved. A derived display symbol reuses its parent ID and is not another record.",
    "source_layer": "Original GeoPackage layer.",
    "source_id": "Original id as a string, never GeoPackage fid. OSM element kind is not verified.",
    "asset_type": "transmission_line, substation_polygon, separately reviewed substation_point, or source power_plant.",
    "display_name": "Original nonblank name, otherwise interface fallback, not an official name.",
    "display_name_is_fallback": "True when display_name is a synthetic interface label.",
    "name": "Original name or null.", "ref": "Original ref or null.", "operator": "Original operator or null.",
    "max_voltage_v": "Numeric original max_voltage in volts; null if unavailable.",
    "max_voltage_kv": "max_voltage_v / 1000, only for finite positive numeric values.",
    "voltages_raw": "Unchanged source voltages string, including empty or multi-value strings.",
    "all_voltages_kv": "Unique valid numeric semicolon tokens / 1000; never used to widen selection.",
    "construction": "Original boolean flag.",
    "disused": "Original line flag; null for polygon layers where field is absent.",
    "osm_tag_status": "not_flagged_in_osm, tagged_construction, tagged_disused, conflicting_tags.",
    "source_status_verified": "Always false. Source flags do not verify operation.",
    "substation_type": "Original polygon tag, never coerced to transmission.",
    "review_reason": "One of three disjoint candidate reasons; null for primary features.",
    "location": "Original line location; null for substations. Does not establish HVDC.",
    "circuits": "Original line circuit count when known; no assumption of one circuit.",
    "mapped_geometry_length_km": "WGS84 geodesic line geometry length, not official circuit-km.",
    "geometry_role": "original_power_plant_footprint for plant polygons, original_point for point-only candidates; derived_polygon_representative_point for display symbols, which do not count as inventory.",
    "matching_classification": "Point-only publication requires distinct_point_only_candidate under the versioned QA policy; not verified physical-station identity.",
    "matching_reason": "Explanation of the source matching decision; no voltage or function is inherited from polygons.",
    "matching_version": "Version of reproducible point/polygon matching policy.",
    "nearest_polygon_feature_id": "Nearest raw polygon ID, for QA context only; does not establish identity or membership.",
    "nearest_polygon_distance_m": "Point-centered WGS84 AEQD screening distance to a raw polygon, not surveyed accuracy.",
    "represented_feature_id": "Parent polygon feature_id for a derived display symbol. Join to parent for selection/counts.",
    "counts_as_inventory": "Always false for derived representative symbols; original inventory features counted separately.",
}


def scalar(value):
    if value is None or pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def normalize_voltage(value):
    value = scalar(value)
    if isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value) and value > 0:
        return float(value) / 1000
    return None


def parse_voltages(value):
    result = []
    for token in (value or "").split(";"):
        try:
            number = float(token.strip())
        except ValueError:
            continue
        kv = normalize_voltage(number)
        if kv is not None and kv not in result:
            result.append(kv)
    return result


def flag(value):
    value = scalar(value)
    if value is None or value is False or value == 0:
        return False
    if value is True or value == 1:
        return True
    raise ValueError(f"Malformed boolean source flag: {value!r}")


def osm_status(record):
    construction, disused = flag(record.get("construction")), flag(record.get("disused"))
    if construction and disused:
        return "conflicting_tags"
    if disused:
        return "tagged_disused"
    return "tagged_construction" if construction else "not_flagged_in_osm"


def polygon_bucket(record):
    voltage, kind = scalar(record.get("max_voltage")), scalar(record.get("substation_type"))
    if kind == "transmission" and voltage in TARGET_V:
        return "primary"
    if kind == "transmission" and voltage is None:
        return "transmission_missing_voltage"
    if voltage in TARGET_V and kind is None:
        return "high_voltage_unknown_type"
    if voltage in TARGET_V and kind == "distribution":
        return "high_voltage_distribution_tag"
    if voltage in TARGET_V:
        return "polygon_target_other_type"
    if kind == "transmission":
        return "transmission_non_target_voltage"
    return "polygon_outside_selection"


def line_bucket(record):
    voltage = scalar(record.get("max_voltage"))
    if voltage in TARGET_V:
        return "lines"
    if voltage is None:
        return "line_missing_voltage"
    return "line_20_kv" if voltage == 20_000 else "line_other_voltage"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value, *, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    text = json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":") if compact else None,
                      indent=None if compact else 2) + "\n"
    # Retain the original Windows publication bytes/checksums on every OS.
    # Binary writes avoid platform-dependent text-mode newline translation.
    temporary.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    temporary.replace(path)


def round_coordinates(value):
    if isinstance(value, (tuple, list)):
        return [round_coordinates(v) for v in value]
    return round(value, 7)


def output_geometry(geometry):
    # RFC 7946 ring winding; centimeter-scale precision, no simplification/dissolve.
    geometry = shapely.orient_polygons(geometry)
    result = mapping(geometry)
    result["coordinates"] = round_coordinates(result["coordinates"])
    converted = shape(result)
    if not converted.is_valid or converted.is_empty:
        raise ValueError("Coordinate rounding produced an invalid/empty geometry")
    return result


def feature(record, layer, reason=None):
    is_line = layer == "power_line"
    is_point = layer == "power_substation_point"
    is_plant = layer == "power_plant"
    source_id = str(int(record["id"]))
    original_name = scalar(record.get("name"))
    fallback = not original_name or not original_name.strip()
    display_name = (f"Unnamed {'line' if is_line else 'power plant' if is_plant else 'substation'} · OSM ID {source_id}"
                    if fallback else original_name)
    voltage = scalar(record.get("max_voltage"))
    properties = {
        "feature_id": f"{layer}:{source_id}", "source_layer": layer, "source_id": source_id,
        "asset_type": "transmission_line" if is_line else "power_plant" if is_plant else "substation_point" if is_point else "substation_polygon",
        "display_name": display_name, "display_name_is_fallback": fallback,
        **{key: scalar(record.get(key)) for key in ("name", "ref", "operator")},
        "max_voltage_v": voltage, "max_voltage_kv": normalize_voltage(voltage),
        "voltages_raw": scalar(record.get("voltages")),
        "all_voltages_kv": parse_voltages(scalar(record.get("voltages"))),
        "construction": scalar(record.get("construction")), "disused": scalar(record.get("disused")),
        "osm_tag_status": osm_status(record), "source_status_verified": False,
        "substation_type": scalar(record.get("substation_type")), "review_reason": reason,
        "location": scalar(record.get("location")) if is_line else None,
        "circuits": scalar(record.get("circuits")) if is_line else None,
        "mapped_geometry_length_km": GEOD.geometry_length(record["geometry"]) / 1000 if is_line else None,
    }
    geometry = mapping(shapely.orient_polygons(record["geometry"])) if is_plant else output_geometry(record["geometry"])
    if is_plant:
        properties.update({f"plant_{key}": scalar(record.get(source)) for key, source in (
            ("source", "source"), ("method", "method"), ("output_raw", "output"),
            ("start_date_raw", "start_date"), ("name_en", "name_en"), ("description", "description"), ("wikidata", "wikidata"))})
        output = properties["plant_output_raw"]
        if output is not None and (not isinstance(output, Real) or isinstance(output, bool) or not math.isfinite(output) or output < 0):
            raise ValueError(f"Invalid power-plant source output: {source_id}")
        properties.update(plant_output_unit=None, geometry_role="original_power_plant_footprint",
                          plant_representative_point=list(shape(geometry).representative_point().coords[0]))
    return {"type": "Feature", "id": properties["feature_id"], "properties": properties,
            "bbox": list(shape(geometry).bounds), "geometry": geometry}


def collection(features):
    return {"type": "FeatureCollection", "attribution": ATTRIBUTION, "license": LICENSE_URL,
            "features": sorted(features, key=lambda f: f["properties"]["source_id"])}


def layer_qa(frame, allowed):
    errors = {
        "null_geometry": int(frame.geometry.isna().sum()),
        "empty_geometry": int(frame.geometry.is_empty.sum()),
        "invalid_geometry": int((~frame.geometry.is_valid).sum()),
        "unexpected_geometry_type": int((~frame.geom_type.isin(allowed)).sum()),
        "duplicate_source_ids": int(frame.id.duplicated().sum()),
        "null_source_ids": int(frame.id.isna().sum()),
    }
    for record in frame.to_dict("records"):
        source_id = scalar(record["id"])
        if source_id is not None and (not isinstance(source_id, Real) or int(source_id) != source_id):
            raise ValueError(f"Nonintegral source id: {source_id!r}")
        voltage = scalar(record.get("max_voltage"))
        if voltage is not None and normalize_voltage(voltage) is None:
            raise ValueError(f"Invalid numeric max_voltage for {source_id}: {voltage!r}")
        osm_status(record)  # Reject malformed booleans, including truthy strings.
    bounds = frame.total_bounds.tolist()
    if not all(math.isfinite(v) for v in bounds) or not (-180 <= bounds[0] <= bounds[2] <= 180
                                                     and -90 <= bounds[1] <= bounds[3] <= 90):
        raise ValueError("Coordinates outside longitude/latitude limits")
    voltage_tags = Counter()
    for record in frame.to_dict('records'):
        raw = scalar(record.get('voltages'))
        parsed = parse_voltages(raw)
        numeric = normalize_voltage(record.get('max_voltage'))
        if raw and any(normalize_voltage_token(token) is None for token in raw.split(';')):
            voltage_tags['records_with_unparseable_voltage_tokens'] += 1
        if numeric is not None and parsed and max(parsed) != numeric:
            voltage_tags['numeric_max_differs_from_parsed_tags'] += 1
        if numeric is not None and not parsed:
            voltage_tags['numeric_max_without_parseable_voltage_tags'] += 1
    return {"count": len(frame), "crs": frame.crs.to_string(), "bounds": bounds,
            "geometry_types": frame.geom_type.value_counts().to_dict(), "errors": errors,
            "voltage_tag_qa": dict(voltage_tags),
            "missing_values": {c: int(frame[c].isna().sum()) for c in frame.columns if c != "geometry"},
            "negative_source_ids": int((frame.id < 0).sum())}


def normalize_voltage_token(token):
    try:
        return normalize_voltage(float(token.strip()))
    except ValueError:
        return None


def dataset_summary(features):
    statuses = Counter(f["properties"]["osm_tag_status"] for f in features)
    voltages = Counter(str(int(f["properties"]["max_voltage_kv"]))
                       if f["properties"]["max_voltage_kv"] is not None else "unknown" for f in features)
    return {"count": len(features), "statuses": {s: statuses[s] for s in STATUSES},
            "voltage_kv": dict(sorted(voltages.items())),
            "missing_values": {key: sum(f["properties"][key] is None or f["properties"][key] == ""
                                        for f in features)
                               for key in ("name", "ref", "operator", "max_voltage_kv", "circuits", "location")},
            "fallback_names": sum(f["properties"]["display_name_is_fallback"] for f in features)}


def validate_publication(datasets):
    ids = []
    for key, features in datasets.items():
        for item in features:
            props, geom = item["properties"], shape(item["geometry"])
            ids.append(props["feature_id"])
            if not geom.is_valid or geom.is_empty or props["source_status_verified"] is not False:
                raise ValueError(f"Invalid published feature {item['id']}")
            if props["osm_tag_status"] == "conflicting_tags":
                raise ValueError("Conflicting status tags must remain in QA quarantine")
            if key == "lines" and (geom.geom_type not in ("LineString", "MultiLineString") or props["asset_type"] != "transmission_line"):
                raise ValueError("Transmission line dataset requires original line geometry")
            if key in ("primary", "review") and (geom.geom_type not in ("Polygon", "MultiPolygon") or props["asset_type"] != "substation_polygon"):
                raise ValueError("Primary/review substation datasets require polygon geometry; source points cannot be promoted")
            if key in ("lines", "primary") and props["max_voltage_v"] not in TARGET_V:
                raise ValueError("Out-of-scope primary voltage")
            if key == "primary" and props["substation_type"] != "transmission":
                raise ValueError("Primary substation is not source-tagged transmission")
            if key == "review" and not props["review_reason"]:
                raise ValueError("Review candidate has no reason")
            if key == "point_candidates" and (geom.geom_type != "Point" or props.get("matching_classification") != "distinct_point_only_candidate"
                                               or props.get("review_reason") != "point_only_unvalidated"):
                raise ValueError("Only eligible distinct point-only candidates may enter the separate point layer")
            if key == "power_plants":
                if geom.geom_type not in ("Polygon", "MultiPolygon") or props["asset_type"] != "power_plant":
                    raise ValueError("Power plants require original source footprints")
                if props["max_voltage_v"] is not None or props.get("plant_output_unit") is not None:
                    raise ValueError("Power-plant voltage/output unit must not be inferred")
                from shapely.geometry import Point
                if not geom.covers(Point(props["plant_representative_point"])):
                    raise ValueError("Power-plant representative must be inside its original footprint")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate global feature_id / overlapping publication subsets")
    return {"features_validated": len(ids), "duplicate_feature_ids": 0,
            "geometry_errors": 0, "voltage_scope_errors": 0, "subset_overlaps": 0,
            "coordinate_precision_decimals": 7, "simplified": False,
            "coordinate_precision_scope": "Existing line/substation polygon exports only; source point candidates and power-plant footprints preserve original coordinate precision. Representatives are derived interior locations.",
            "coordinate_order": "longitude, latitude", "crs": "EPSG:4326"}


def prepare(input_path, output, qa_output, allow_source_mismatch=False):
    input_path, output, qa_output = (Path(p).resolve() for p in (input_path, output, qa_output))
    if not input_path.is_file():
        raise FileNotFoundError(f"Source GeoPackage is missing: {input_path}; no replacement data generated")
    if output == input_path.parent or output.is_relative_to(input_path.parent):
        raise ValueError("Publication output cannot be inside the raw source directory")
    if qa_output.is_relative_to(ROOT / "public") or qa_output.is_relative_to(output):
        raise ValueError("Internal QA output must be outside public/ and publication output")
    before_hash, before_size = sha256(input_path), input_path.stat().st_size
    # SQLite read-only connection enumerates metadata/counts without loading excluded layers.
    with sqlite3.connect(input_path.as_uri() + "?mode=ro", uri=True) as connection:
        layers = []
        for name, srs in connection.execute("SELECT table_name,srs_id FROM gpkg_contents WHERE data_type='features' ORDER BY table_name"):
            safe_name = '"' + name.replace('"', '""') + '"'
            count = connection.execute(f"SELECT COUNT(*) FROM {safe_name}").fetchone()[0]
            layers.append({"name": name, "count": count, "srs_id": srs})
    frames, raw_qa = {}, {}
    for layer, allowed in (("power_line", {"LineString", "MultiLineString"}),
                           ("power_substation_polygon", {"Polygon", "MultiPolygon"}),
                           ("power_substation_point", {"Point", "MultiPoint"}),
                           ("power_plant", {"Polygon", "MultiPolygon"})):
        if layer not in {entry["name"] for entry in layers}:
            raise ValueError(f"Required source layer missing: {layer}")
        frame = gpd.read_file(input_path, layer=layer, engine="pyogrio")
        required = {"id", "name", "ref", "operator", "construction"}
        if layer == "power_plant":
            required |= {"source", "method", "output", "start_date", "name_en", "description", "wikidata"}
        else:
            required |= {"max_voltage", "voltages"}
            required |= {"disused", "location", "circuits"} if layer == "power_line" else {"substation_type"}
        if required - set(frame.columns):
            raise ValueError(f"{layer} missing fields: {sorted(required - set(frame.columns))}")
        if frame.crs is None or frame.crs.to_epsg() != 4326:
            raise ValueError(f"{layer}: expected EPSG:4326, found {frame.crs}")
        raw_qa[layer] = layer_qa(frame, allowed)
        if any(raw_qa[layer]["errors"].values()):
            write_json(qa_output / "failed-geometry-qa.json", raw_qa)
            raise ValueError(f"{layer} failed source QA: {raw_qa[layer]['errors']}")
        frames[layer] = frame
    datasets = {key: [] for key in ("lines", "primary", "review")}
    excluded, buckets, quarantined = [], Counter(), []
    for layer in ("power_line", "power_substation_polygon"):
        for record in frames[layer].to_dict("records"):
            bucket = line_bucket(record) if layer == "power_line" else polygon_bucket(record)
            buckets[bucket] += 1
            if osm_status(record) == "conflicting_tags":
                quarantined.append(feature(record, layer, "conflicting_status_tags"))
                bucket = "conflicting_status_tags"
            if bucket in ("lines", "primary"):
                datasets[bucket].append(feature(record, layer))
            elif bucket in ("transmission_missing_voltage", "high_voltage_unknown_type", "high_voltage_distribution_tag"):
                datasets["review"].append(feature(record, layer, bucket))
            else:
                excluded.append({"source_layer": layer, "source_id": str(int(record["id"])),
                                 "reason": bucket, "max_voltage_v": scalar(record["max_voltage"]),
                                 "substation_type": scalar(record.get("substation_type")),
                                 "osm_tag_status": osm_status(record)})
    line_frame, polygon_frame, point_frame = (frames[k] for k in ("power_line", "power_substation_polygon", "power_substation_point"))
    from substation_matching import match_substations, representative_features, write_matching_csv
    matching = match_substations(point_frame, polygon_frame, before_hash, TARGET_V)
    matching_summary = {key: value for key, value in matching.items() if key != "records"}
    matching_by_id = {row["source_id"]: row for row in matching["records"]}
    datasets["point_candidates"] = []
    for record in point_frame.to_dict("records"):
        match = matching_by_id[str(int(record["id"]))]
        if not match["eligible_for_point_candidate_layer"]:
            continue
        item = feature(record, "power_substation_point", "point_only_unvalidated")
        # Preserve the original point coordinates exactly; never replace them by a polygon center.
        item["geometry"] = mapping(record["geometry"])
        item["bbox"] = list(record["geometry"].bounds)
        item["properties"].update(geometry_role="original_point", matching_classification=match["classification"],
                                  matching_reason=match["classification_reason"], matching_version=matching["matching_version"],
                                  nearest_polygon_feature_id=match["nearest_polygon_feature_id"],
                                  nearest_polygon_distance_m=match["nearest_polygon_distance_m"])
        datasets["point_candidates"].append(item)
    display_points = representative_features(datasets)
    datasets["power_plants"] = [feature(record, "power_plant") for record in frames["power_plant"].to_dict("records")]
    summaries = {key: dataset_summary(value) for key, value in datasets.items()}
    plant_frame = frames["power_plant"]
    plant_audit = {"raw_count": len(plant_frame), "published_count": len(datasets["power_plants"]),
                   "not_flagged": summaries["power_plants"]["statuses"]["not_flagged_in_osm"],
                   "construction": summaries["power_plants"]["statuses"]["tagged_construction"],
                   "polygons": int((plant_frame.geom_type == "Polygon").sum()),
                   "multipolygons": int((plant_frame.geom_type == "MultiPolygon").sum()),
                   **{f"missing_{key}": int(plant_frame[key].isna().sum()) for key in ("name", "operator", "source", "method", "output", "start_date")},
                   "voltage_field_available": "max_voltage" in plant_frame.columns,
                   "disused_field_available": "disused" in plant_frame.columns,
                   "output_unit": None}
    actual = {
        "source_bytes": before_size, "source_sha256": before_hash, "layer_count": len(layers),
        "raw_lines": len(line_frame), "raw_polygons": len(polygon_frame), "raw_points": len(point_frame),
        **{k: len(v) for k, v in datasets.items()},
        **{f"{k}_{s}": v for k in ("lines", "primary") for s, v in summaries[k]["statuses"].items()},
        **{f"lines_{k}_kv": v for k, v in summaries["lines"]["voltage_kv"].items()},
        **{k: buckets[k] for k in ("transmission_missing_voltage", "high_voltage_unknown_type", "high_voltage_distribution_tag",
                                  "line_missing_voltage", "line_20_kv", "line_other_voltage",
                                  "polygon_target_other_type", "transmission_non_target_voltage")},
        "excluded_disused_lines": sum(e["source_layer"] == "power_line" and e["osm_tag_status"] == "tagged_disused" for e in excluded),
        "raw_polygon_missing_voltage": int(polygon_frame.max_voltage.isna().sum()),
        "raw_polygon_transmission": int((polygon_frame.substation_type == "transmission").sum()),
        "raw_polygon_distribution": int((polygon_frame.substation_type == "distribution").sum()),
        "raw_line_missing_name": int(line_frame.name.isna().sum()),
        "raw_line_missing_circuits": int(line_frame.circuits.isna().sum()),
        "raw_line_missing_start_date": int(line_frame.start_date.isna().sum()) if "start_date" in line_frame else None,
        "point_missing_voltage": int(point_frame.max_voltage.isna().sum()),
        "point_transmission": int((point_frame.substation_type == "transmission").sum()),
    }
    expected = json.loads((Path(__file__).parent / "expected-audit.json").read_text(encoding="utf-8"))
    differences = [{"metric": k, "expected": v, "actual": actual.get(k)} for k, v in expected.items() if actual.get(k) != v]
    plant_expected = json.loads((Path(__file__).parent / "expected-power-plant-audit.json").read_text(encoding="utf-8"))
    differences += [{"metric": f"power_plants.{k}", "expected": v, "actual": plant_audit.get(k)} for k, v in plant_expected.items() if plant_audit.get(k) != v]
    validation = validate_publication(datasets)
    after_hash = sha256(input_path)
    if after_hash != before_hash:
        raise ValueError("Raw source changed during processing; publication aborted")
    data_version = f"{before_hash[:16]}-pipeline-{PIPELINE_VERSION}"
    qa = {"data_version": data_version, "source_sha256": before_hash, "source_unchanged": True,
          "raw_layers": layers, "core_layer_qa": raw_qa, "audit_actual": actual,
          "audit_comparison": {"matches": not differences, "differences": differences},
          "excluded_counts": dict(sorted(Counter(e["reason"] for e in excluded).items())),
          "excluded_layer_counts": {e["name"]: e["count"] for e in layers if e["name"] not in frames},
          "quarantined_conflicts": len(quarantined), "qa_only_points": len(point_frame) - len(datasets["point_candidates"]),
          "substation_point_matching": matching_summary,
          "power_plant_audit": plant_audit,
          "representative_symbols": {"count": len(display_points), "outside_parent_footprint": 0, "counts_as_inventory": False},
          "publication_validation": validation,
          "validation_summary": "PASS" if not differences else "SOURCE_VERSION_MISMATCH",
          "scope": "Structural, attribute and subset QA; not official operational or topology validation."}
    write_json(qa_output / "qa-report.json", qa)
    write_json(qa_output / "substation-matching-report.json", matching)
    write_matching_csv(qa_output / "substation-matching-report.csv", matching)
    write_json(qa_output / "exclusion-report.json", {"excluded": sorted(excluded, key=lambda e: (e["source_layer"], e["source_id"])),
                                                   "excluded_layers": qa["excluded_layer_counts"],
                                                   "point_reason": "Matched, uncertain and ineligible distinct points held outside publication; see substation-matching-report.json"})
    points = [{"type": "Feature", "id": f"power_substation_point:{int(r['id'])}",
               "properties": {"source_id": str(int(r["id"])), "name": scalar(r["name"]),
                              "substation_type": scalar(r["substation_type"]), "max_voltage_v": scalar(r["max_voltage"]),
                              "review_reason": "point_voltage_and_polygon_duplicate_review"},
               "geometry": output_geometry(r["geometry"])} for r in point_frame.to_dict("records")]
    write_json(qa_output / "substation-points.geojson", collection(points), compact=True)
    write_json(qa_output / "conflicting-status.geojson", collection(quarantined), compact=True)
    if differences and not allow_source_mismatch:
        raise ValueError("Source-version mismatch; no publication files written. Exact differences: " + json.dumps(differences))
    filenames = {"lines": "transmission-lines.geojson", "primary": "substations-primary.geojson", "review": "substations-review.geojson",
                 "point_candidates": "substations-point-candidates.geojson", "power_plants": "power-plants.geojson"}
    output_sizes = {}
    for key, filename in filenames.items():
        write_json(output / filename, collection(datasets[key]), compact=True)
        output_sizes[filename] = (output / filename).stat().st_size
    display_filename = "substation-display-points.geojson"
    write_json(output / display_filename, collection(display_points), compact=True)
    output_sizes[display_filename] = (output / display_filename).stat().st_size
    summary = {"schema_version": 3, "data_version": data_version, "source_data_vintage": "unknown",
               "source_sha256": before_hash, "raw_counts": {e["name"]: e["count"] for e in layers},
               "datasets": summaries,
               "review_reasons": dict(Counter(f["properties"]["review_reason"] for f in datasets["review"])),
               "default_selection": {"lines": summaries["lines"]["statuses"]["not_flagged_in_osm"],
                                     "primary": summaries["primary"]["statuses"]["not_flagged_in_osm"], "review": 0, "points": 0,
                                     "plants": summaries["power_plants"]["statuses"]["not_flagged_in_osm"]},
               "substation_point_matching": {key: matching_summary[key] for key in ("matching_version", "classifications", "eligible_point_candidates", "held_distinct_candidates", "pair_comparisons")},
               "substation_presentation": {"representative_symbol_count": len(display_points), "footprint_min_zoom": 10, "counts_as_inventory": False},
               "power_plant_presentation": {"representative_symbol_count": len(datasets["power_plants"]), "footprint_min_zoom": 10,
                                            "counts_as_inventory": False, "coordinates_field": "plant_representative_point"},
               "output_bytes": output_sizes, "planned_assets": {"state": "data_not_provided", "count": None},
               "official_region_and_power_system": "data_not_provided"}
    catalog = {"schema_version": 3, "data_version": data_version, "source": "OpenInfraMap / OpenStreetMap",
               "source_url": "https://openinframap.org/", "osm_url": "https://www.openstreetmap.org/copyright",
               "license": "ODbL-1.0", "license_url": LICENSE_URL, "attribution": ATTRIBUTION,
               "source_file": "IDN.gpkg", "source_bytes": before_size, "source_sha256": before_hash,
               "source_data_vintage": "unknown", "original_crs": "EPSG:4326", "output_crs": "EPSG:4326",
               "pipeline_version": PIPELINE_VERSION,
               "processing_method": "Unchanged exact numeric max_voltage line filter in 70000/150000/275000/500000 V; unchanged transmission-tagged primary polygons and three review predicates. Conflicting flags quarantined. Existing line/polygon exports retain seven coordinate decimals and RFC7946 winding, without simplification/dissolve. WGS84 geodesic line lengths. All raw substation points matched against all polygons under the versioned policy; eligible distinct candidates retain original point coordinates and unknown voltage. Polygon point_on_surface symbols preserve parent IDs and do not count as inventory. Power-plant footprints retain original precision, source attributes and derived interior coordinates; no voltage, output unit, official capacity or COD is inferred.",
               "substation_matching_policy": matching["policy"],
               "power_plant_policy": {"source_layer": "power_plant", "default_visible": True, "grid_voltage_filter_applies": False,
                                      "full_precision_footprints": True, "overview_marker": "derived point_on_surface; not another record",
                                      "output_unit": None, "source_start_date_is_verified_cod": False, "generator_layers_published": False},
               "database_license_notice": "The processed derivative database and presentation symbols are available under ODbL 1.0. Retain attribution and license notices on redistribution.",
               "datasets": [{"key": k, "url": f"/data/{v}", "source_layer": "power_line" if k == "lines" else "power_plant" if k == "power_plants" else "power_substation_point" if k == "point_candidates" else "power_substation_polygon",
                             "role": "inventory", "count": len(datasets[k]), "bytes": output_sizes[v], "sha256": sha256(output / v)} for k, v in filenames.items()] + [
                                 {"key": "display_points", "url": f"/data/{display_filename}", "source_layer": "power_substation_polygon", "role": "presentation",
                                  "count": len(display_points), "bytes": output_sizes[display_filename], "sha256": sha256(output / display_filename), "counts_as_inventory": False}],
               "fields": FIELD_MEANINGS, "limitations": LIMITATIONS}
    for filename, value in (("summary.json", summary), ("data-catalog.json", catalog), ("qa-report.json", qa)):
        write_json(output / filename, value)
    return {"data_version": data_version, "counts": {k: len(v) for k, v in datasets.items()},
            "output_bytes": {p.name: p.stat().st_size for p in sorted(output.iterdir()) if p.is_file()},
            "audit_differences": differences, "source_unchanged": True}


def repo_path(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=repo_path, default=ROOT / "data/raw/IDN.gpkg")
    parser.add_argument("--output", type=repo_path, default=ROOT / "public/data")
    parser.add_argument("--qa-output", type=repo_path, default=ROOT / "data/qa")
    parser.add_argument("--allow-source-mismatch", action="store_true", help="Explicitly publish actual new-source results; differences remain in QA")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.input, args.output, args.qa_output, args.allow_source_mismatch), indent=2))
    except (ValueError, FileNotFoundError, pyogrio.errors.DataSourceError) as error:
        print(f"Data preparation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
