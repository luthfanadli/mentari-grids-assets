"""Read-only point/polygon source audit. Writes internal QA only; no publication changes."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod, Transformer
import shapely
from shapely.geometry import Point

from prepare_data import ROOT, TARGET_V, polygon_bucket, scalar, sha256, write_json

GEOD = Geod(ellps="WGS84")
THRESHOLDS = [25, 100, 250, 500, 1000, 5000]


def normalized_name(value):
    value = scalar(value)
    if not value:
        return None
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKD", value).casefold()) or None


def basic_profile(frame):
    fields = [name for name in frame.columns if name != "geometry"]
    return {
        "count": len(frame), "crs": frame.crs.to_string(),
        "geometry_types": frame.geom_type.value_counts().to_dict(),
        "invalid_geometry": int((~frame.geometry.is_valid).sum()),
        "empty_geometry": int(frame.geometry.is_empty.sum()),
        "null_geometry": int(frame.geometry.isna().sum()),
        "duplicate_ids": int(frame.id.duplicated().sum()),
        "duplicate_coordinate_or_geometry_rows": int(frame.geometry.to_wkb().duplicated().sum()),
        "negative_ids": int((frame.id < 0).sum()),
        "fields": fields,
        "nonnull": {name: int(frame[name].notna().sum()) for name in fields},
        "nonblank": {name: int(frame[name].fillna("").astype(str).str.strip().ne("").sum())
                     for name in fields if pd.api.types.is_string_dtype(frame[name])},
        "substation_types": frame.substation_type.fillna("(null)").value_counts().to_dict(),
        "construction_true": int(frame.construction.fillna(False).sum()),
        "has_disused_field": "disused" in frame,
        "voltage_v": {"(null)" if np.isnan(key) else str(int(key)): int(value)
                      for key, value in frame.max_voltage.value_counts(dropna=False).items()},
    }


def polygon_details(record):
    return {"id": str(int(record["id"])), "name": scalar(record["name"]),
            "substation_type": scalar(record["substation_type"]),
            "max_voltage_v": scalar(record["max_voltage"]),
            "bucket": polygon_bucket(record)}


def area_m2(geometry):
    # Normalize hole/exterior winding before geodesic signed-area aggregation.
    return abs(GEOD.geometry_area_perimeter(shapely.orient_polygons(geometry))[0])


def distribution(values):
    return {"min": float(np.min(values)), "median": float(np.median(values)),
            "p95": float(np.percentile(values, 95)), "max": float(np.max(values))}


def audit(source, output):
    fingerprint = sha256(source)
    points = gpd.read_file(source, layer="power_substation_point", engine="pyogrio")
    polygons = gpd.read_file(source, layer="power_substation_polygon", engine="pyogrio")
    lines = gpd.read_file(source, layer="power_line", engine="pyogrio")
    lines = lines[lines.max_voltage.isin(TARGET_V)].reset_index(drop=True)
    point_records, polygon_records = points.to_dict("records"), polygons.to_dict("records")
    for frame, allowed in ((points, {"Point"}), (polygons, {"Polygon", "MultiPolygon"}),
                           (lines, {"LineString", "MultiLineString"})):
        assert frame.crs.to_epsg() == 4326
        assert frame.geom_type.isin(allowed).all()
        assert frame.geometry.notna().all() and frame.geometry.is_valid.all() and not frame.geometry.is_empty.any()
        assert not frame.id.duplicated().any()
    polygon_geometries = polygons.geometry.to_numpy()
    tree = shapely.STRtree(polygon_geometries)
    names = defaultdict(list)
    for index, record in enumerate(polygon_records):
        normalized = normalized_name(record["name"])
        if normalized:
            names[normalized].append(index)
    endpoints = []
    for geom in lines.geometry:
        for part in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
            endpoints.extend([part.coords[0], part.coords[-1]])
    endpoints = np.array(endpoints)
    point_rows = []
    for record in point_records:
        point = record["geometry"]
        covering = sorted(int(index) for index in tree.query(point, predicate="intersects"))
        exact_inside = [index for index in covering if polygon_geometries[index].contains(point)]
        # A point-centered ellipsoidal AEQD is used rather than one national UTM or degree distances.
        transformer = Transformer.from_crs(4326, f"+proj=aeqd +lat_0={point.y} +lon_0={point.x} +datum=WGS84 +units=m", always_xy=True)
        projected_polygons = shapely.transform(polygon_geometries, transformer.transform, interleaved=False)
        distances = shapely.distance(projected_polygons, Point(0, 0))
        nearest = int(np.argmin(distances))
        nearest_line_distances = shapely.distance(shapely.transform(lines.geometry.to_numpy(), transformer.transform, interleaved=False), Point(0, 0))
        nearest_line = int(np.argmin(nearest_line_distances))
        _, _, endpoint_distances = GEOD.inv(np.full(len(endpoints), point.x), np.full(len(endpoints), point.y), endpoints[:, 0], endpoints[:, 1])
        normalized = normalized_name(record["name"])
        matching_names = sorted(names.get(normalized, []), key=lambda index: distances[index]) if normalized else []
        nearest_same_name = matching_names[0] if matching_names else None
        text = scalar(record["name"]) or ""
        gi_name_hint = bool(re.search(r"\b(?:GI|GITET)\b|gardu\s+induk", text, re.IGNORECASE))
        flags = []
        if record.get("substation_type") == "transmission":
            flags.append("explicit_transmission_tag_requires_voltage_validation")
        if gi_name_hint:
            flags.append("name_mentions_gi_gitet_or_gardu_induk_not_certification")
        if re.search(r"kantor|office|taman|public\s+park", text + " " + (scalar(record.get("description")) or ""), re.IGNORECASE):
            flags.append("name_or_description_suggests_non_substation_function_review_only")
        point_rows.append({
            "source_id": str(int(record["id"])), "name": scalar(record["name"]),
            "substation_type": scalar(record["substation_type"]), "operator": scalar(record["operator"]),
            "ref": scalar(record["ref"]), "description": scalar(record["description"]),
            "max_voltage_v": scalar(record["max_voltage"]), "voltages_raw": scalar(record["voltages"]),
            "longitude": point.x, "latitude": point.y,
            "review_flags": flags, "name_voltage_mentions_only": re.findall(r"\b\d+(?:[.,]\d+)?\s*k[vV]\b", text, re.IGNORECASE),
            "covering_polygon_count": len(covering), "strictly_inside_polygon_count": len(exact_inside),
            "covering_polygons": [polygon_details(polygon_records[index]) for index in covering],
            "nearest_polygon": polygon_details(polygon_records[nearest]),
            "nearest_polygon_distance_m": float(distances[nearest]),
            "exact_normalized_name_matches": len(matching_names),
            "nearest_same_name_polygon": polygon_details(polygon_records[nearest_same_name]) if nearest_same_name is not None else None,
            "nearest_same_name_distance_m": float(distances[nearest_same_name]) if nearest_same_name is not None else None,
            "nearest_target_line_id": str(int(lines.iloc[nearest_line].id)),
            "nearest_target_line_distance_m": float(nearest_line_distances[nearest_line]),
            "nearest_target_line_endpoint_distance_m": float(np.min(endpoint_distances)),
            "spatial_match_is_confirmed_duplicate": False,
            "line_proximity_is_verified_electrical_connection": False,
        })
    polygon_pairs = []
    for index, geometry in enumerate(polygon_geometries):
        for other in tree.query(geometry, predicate="intersects"):
            other = int(other)
            if other <= index:
                continue
            intersection = geometry.intersection(polygon_geometries[other])
            overlap = area_m2(intersection) if intersection.geom_type in ("Polygon", "MultiPolygon", "GeometryCollection") else 0
            polygon_pairs.append({"a": polygon_details(polygon_records[index]), "b": polygon_details(polygon_records[other]),
                                  "equals": bool(geometry.equals(polygon_geometries[other])),
                                  "one_covers_other": bool(geometry.covers(polygon_geometries[other]) or polygon_geometries[other].covers(geometry)),
                                  "intersection_area_m2": overlap})
    areas = np.array([area_m2(geometry) for geometry in polygon_geometries])
    buckets = np.array([polygon_bucket(record) for record in polygon_records])
    area_profiles = {}
    for key, mask in (("all", np.full(len(areas), True)), ("primary", buckets == "primary"),
                      ("review", np.isin(buckets, ["transmission_missing_voltage", "high_voltage_unknown_type", "high_voltage_distribution_tag"]))):
        subset = areas[mask]
        area_profiles[key] = {"count": int(mask.sum()), "area_m2": distribution(subset),
                              "below_25_m2": int((subset < 25).sum()), "below_100_m2": int((subset < 100).sum()),
                              "below_1000_m2": int((subset < 1000).sum()), "above_100000_m2": int((subset > 100000).sum())}
    point_distances = np.array([row["nearest_polygon_distance_m"] for row in point_rows])
    covered_polygon_ids = {polygon["id"] for row in point_rows for polygon in row["covering_polygons"]}
    review_buckets = {"transmission_missing_voltage", "high_voltage_unknown_type", "high_voltage_distribution_tag"}
    published_buckets = review_buckets | {"primary"}
    profile = {
        "source_file": source.name, "source_sha256": fingerprint,
        "source_bytes": source.stat().st_size, "source_unchanged": sha256(source) == fingerprint,
        "method": "Read-only source audit. Exact EPSG:4326 topology for intersections. Point-centered WGS84 AEQD distances to polygon/line geometries (no national UTM or degree-as-meter distances); stored-edge chord approximation. WGS84 geodesic line-endpoint distances and polygon areas. Distances are screening evidence, not survey distances or electrical connectivity. No automatic deduplication, voltage inheritance, classification or publication changes.",
        "point_profile": basic_profile(points), "polygon_profile": basic_profile(polygons),
        "same_attribute_columns": list(points.drop(columns="geometry").columns) == list(polygons.drop(columns="geometry").columns),
        "shared_numeric_ids_across_point_polygon": sorted(set(str(int(v)) for v in points.id) & set(str(int(v)) for v in polygons.id)),
        "polygon_buckets": dict(Counter(buckets)),
        "point_polygon_spatial_screen": {
            "points_covered_by_any_polygon": sum(row["covering_polygon_count"] > 0 for row in point_rows),
            "distinct_polygons_covering_points": len(covered_polygon_ids),
            "points_strictly_inside_any_polygon": sum(row["strictly_inside_polygon_count"] > 0 for row in point_rows),
            "points_covered_by_multiple_polygons": sum(row["covering_polygon_count"] > 1 for row in point_rows),
            "covered_points_by_polygon_bucket": {bucket: sum(any(p["bucket"] == bucket for p in row["covering_polygons"]) for row in point_rows)
                                                for bucket in sorted(set(buckets))},
            "points_with_nearest_polygon_within_m_cumulative": {str(t): int((point_distances <= t).sum()) for t in THRESHOLDS},
            "points_outside_all_polygons_with_nearest_within_m_cumulative": {str(t): sum(row["covering_polygon_count"] == 0 and row["nearest_polygon_distance_m"] <= t for row in point_rows) for t in THRESHOLDS},
            "nearest_polygon_distance_m": distribution(point_distances),
            "points_with_exact_normalized_name_match_anywhere": sum(row["exact_normalized_name_matches"] > 0 for row in point_rows),
            "points_with_exact_normalized_name_match_within_100m": sum(row["nearest_same_name_distance_m"] is not None and row["nearest_same_name_distance_m"] <= 100 for row in point_rows),
        },
        "point_line_spatial_screen": {
            "line_count": len(lines),
            "points_with_nearest_line_within_m_cumulative": {str(t): sum(row["nearest_target_line_distance_m"] <= t for row in point_rows) for t in THRESHOLDS},
            "points_with_nearest_endpoint_within_m_cumulative": {str(t): sum(row["nearest_target_line_endpoint_distance_m"] <= t for row in point_rows) for t in THRESHOLDS},
        },
        "polygon_topology_screen": {
            "intersecting_pairs": len(polygon_pairs),
            "positive_area_overlap_pairs": sum(row["intersection_area_m2"] > 0 for row in polygon_pairs),
            "overlap_above_1m2_pairs": sum(row["intersection_area_m2"] > 1 for row in polygon_pairs),
            "exact_equal_geometry_pairs": sum(row["equals"] for row in polygon_pairs),
            "nested_positive_overlap_pairs": sum(row["one_covers_other"] and row["intersection_area_m2"] > 0 for row in polygon_pairs),
            "primary_primary_positive_overlap_pairs": sum(row["a"]["bucket"] == "primary" and row["b"]["bucket"] == "primary" and row["intersection_area_m2"] > 0 for row in polygon_pairs),
            "primary_review_positive_overlap_pairs": sum({row["a"]["bucket"], row["b"]["bucket"]} <= published_buckets and
                                                        "primary" in {row["a"]["bucket"], row["b"]["bucket"]} and
                                                        (row["a"]["bucket"] in review_buckets or row["b"]["bucket"] in review_buckets) and
                                                        row["intersection_area_m2"] > 0 for row in polygon_pairs),
            "review_review_positive_overlap_pairs": sum(row["a"]["bucket"] in review_buckets and row["b"]["bucket"] in review_buckets and
                                                       row["intersection_area_m2"] > 0 for row in polygon_pairs),
            "geographic_centroid_outside_own_polygon": sum(not geom.covers(geom.centroid) for geom in polygon_geometries),
            "centroid_note": "Centroids computed in source coordinates for a display QA screen only, not geodesic survey centers. Representative points are safer for markers inside concave/multipart footprints.",
        },
        "polygon_area_screen": area_profiles,
        "point_priority_hints": {
            "explicit_transmission_tag": sum(row["substation_type"] == "transmission" for row in point_rows),
            "gi_name_hint": sum(any(flag.startswith("name_mentions_gi") for flag in row["review_flags"]) for row in point_rows),
            "name_description_anomaly_hint": sum(any(flag.startswith("name_or_description") for flag in row["review_flags"]) for row in point_rows),
        },
        "confirmed_unique_station_count": None,
        "point_rows": sorted(point_rows, key=lambda row: row["source_id"]),
        "polygon_intersection_pairs": polygon_pairs,
    }
    assert profile["source_unchanged"]
    assert profile["point_profile"]["count"] == len(profile["point_rows"])
    assert len(set(row["source_id"] for row in point_rows)) == len(point_rows)
    assert profile["point_polygon_spatial_screen"]["points_covered_by_any_polygon"] <= len(points)
    write_json(output / "analysis.json", profile)
    csv_fields = ["source_id", "name", "substation_type", "operator", "max_voltage_v", "voltages_raw", "longitude", "latitude", "covering_polygon_count",
                  "nearest_polygon_id", "nearest_polygon_name", "nearest_polygon_bucket", "nearest_polygon_voltage_v", "nearest_polygon_distance_m",
                  "nearest_same_name_distance_m", "nearest_target_line_id", "nearest_target_line_distance_m", "nearest_target_line_endpoint_distance_m", "review_flags"]
    with (output / "point-review.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=csv_fields)
        writer.writeheader()
        for row in profile["point_rows"]:
            values = {key: row.get(key) for key in csv_fields}
            values.update(nearest_polygon_id=row["nearest_polygon"]["id"], nearest_polygon_name=row["nearest_polygon"]["name"],
                          nearest_polygon_bucket=row["nearest_polygon"]["bucket"], nearest_polygon_voltage_v=row["nearest_polygon"]["max_voltage_v"],
                          review_flags=";".join(row["review_flags"]))
            writer.writerow(values)
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/IDN.gpkg")
    parser.add_argument("--output", type=Path, default=ROOT / "data/qa/substation-analysis")
    args = parser.parse_args()
    source = (args.input if args.input.is_absolute() else ROOT / args.input).resolve()
    output = (args.output if args.output.is_absolute() else ROOT / args.output).resolve()
    if output.is_relative_to(ROOT / "public") or output == source.parent or output.is_relative_to(source.parent):
        parser.error("Analysis output must stay outside public/ and the raw source directory")
    result = audit(source, output)
    print(json.dumps({key: value for key, value in result.items() if key not in ["point_rows", "polygon_intersection_pairs"]}, ensure_ascii=False, indent=2))
