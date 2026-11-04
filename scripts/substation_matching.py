"""Conservative, deterministic source-point matching; no asset promotion or geometry edits."""
from __future__ import annotations

from collections import Counter
import csv
import re
import unicodedata

import numpy as np
import pandas as pd
from pyproj import Transformer
import shapely
from shapely.geometry import Point, mapping, shape

MATCHING_VERSION = "1.0.0"
POLICY = {
    "version": MATCHING_VERSION,
    "proximity_review_m": 500,
    "name_review_m": 1000,
    "supported_match_m": 100,
    "definitions": {
        "matched": "One supported source correspondence within 100 m, with distinctive name/reference evidence and no attribute conflict. Not an authoritative duplicate certification.",
        "uncertain": "Intersection, proximity within 500 m, numeric-ID evidence, or a distinctive name/reference association within 1 km without one unambiguous supported match.",
        "distinct_point_only_candidate": "No plausible polygon correspondence under this policy. Distinct is relative to this export and these thresholds, not verified physical-station identity or transmission function.",
    },
    "identifier_policy": "Preserve original id and sign. Numeric IDs compared across layers; absent OSM element-kind fields prevent treating equal numeric IDs as confirmed shared OSM identity.",
    "name_policy": "Case/accent/punctuation normalization; strip generic utility/station words and explicit kV text; retain site-code numbers (PK 276 differs from PK 277). Distinctive token-set equality only; no fuzzy substring or arbitrary place-name inference.",
    "eligibility_policy": "Only distinct candidates; missing voltage stays null. Hold known distribution/minor_distribution/generation/other non-transmission roles, non-target known numeric voltage, conflicting status flags, and office/park function clues outside the map layer for manual review. These holds do not delete source records.",
    "distance_method": "Per-point WGS84 azimuthal equidistant projection against every raw polygon; projected stored-edge chord approximation in meters. Intersection uses original EPSG:4326 geometry. Thresholds are QA rules, not surveyed boundaries or network connectivity.",
}
GENERIC_WORDS = frozenset("pt persero perusahaan listrik negara pln gardu induk gi gitet gistet gis substation sub station electrical electric power transmisi transmission distribusi distribution unit kv layanan kantor".split())
CLASSES = ("matched", "uncertain", "distinct_point_only_candidate")


def nullable(value):
    if value is None or pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def words(value):
    text = nullable(value) or ""
    text = "".join(c for c in unicodedata.normalize("NFKD", str(text).casefold()) if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", text)


def name_tokens(value):
    # Voltage text is generic; equipment/site code numbers (PK 276 vs PK 277) are identity evidence.
    text = re.sub(r"\b\d+(?:[.,]\d+)?\s*kv\b", " ", nullable(value) or "", flags=re.IGNORECASE)
    return sorted({token for token in words(text) if token not in GENERIC_WORDS})


def normalized_operator(value):
    tokens = words(value)
    if not tokens:
        return None
    if "pln" in tokens or {"perusahaan", "listrik", "negara"}.issubset(tokens):
        return "pln"
    return " ".join(token for token in tokens if token not in {"pt", "persero"}) or None


def meaningful_ref(value):
    tokens = words(value)
    if not any(token not in GENERIC_WORDS for token in tokens):
        return None
    return "".join(tokens) or None


def pair_evidence(point, polygon, distance, intersects):
    left_name, right_name = name_tokens(point.get("name")), name_tokens(polygon.get("name"))
    left_ref, right_ref = meaningful_ref(point.get("ref")), meaningful_ref(polygon.get("ref"))
    left_operator, right_operator = normalized_operator(point.get("operator")), normalized_operator(polygon.get("operator"))
    left_voltage, right_voltage = nullable(point.get("max_voltage")), nullable(polygon.get("max_voltage"))
    left_type, right_type = nullable(point.get("substation_type")), nullable(polygon.get("substation_type"))
    conflicts = []
    if left_voltage is not None and right_voltage is not None and left_voltage != right_voltage:
        conflicts.append("different_source_max_voltage")
    if left_operator and right_operator and left_operator != right_operator:
        conflicts.append("different_source_operator")
    if left_ref and right_ref and left_ref != right_ref:
        conflicts.append("different_source_reference")
    if left_name and right_name and left_name != right_name:
        conflicts.append("different_distinctive_name_tokens")
    if left_type not in (None, "yes") and right_type not in (None, "yes") and left_type != right_type:
        conflicts.append("different_source_substation_type")
    left_construction, right_construction = nullable(point.get("construction")), nullable(polygon.get("construction"))
    if left_construction is not None and right_construction is not None and left_construction != right_construction:
        conflicts.append("different_source_construction_flag")
    distinctive_name = bool(left_name and left_name == right_name)
    reference_match = bool(left_ref and left_ref == right_ref)
    return {
        "polygon_feature_id": f"power_substation_polygon:{int(polygon['id'])}",
        "polygon_source_id": str(int(polygon["id"])), "polygon_name": nullable(polygon.get("name")),
        "polygon_substation_type": right_type, "polygon_max_voltage_v": right_voltage,
        "polygon_operator": nullable(polygon.get("operator")), "polygon_ref": nullable(polygon.get("ref")),
        "polygon_construction": right_construction,
        "distance_m": float(distance), "intersects": bool(intersects),
        "same_numeric_source_id": int(point["id"]) == int(polygon["id"]),
        "osm_element_identity_verified": False,
        "distinctive_name_match": distinctive_name, "meaningful_reference_match": reference_match,
        "operator_agrees": bool(left_operator and left_operator == right_operator),
        "attribute_conflicts": conflicts,
        "supported": bool(distance <= POLICY["supported_match_m"] and (distinctive_name or reference_match) and not conflicts),
    }


def classify_pairs(pairs):
    plausible = [pair for pair in pairs if pair["intersects"] or pair["distance_m"] <= POLICY["proximity_review_m"]
                 or pair["same_numeric_source_id"]
                 or ((pair["distinctive_name_match"] or pair["meaningful_reference_match"]) and pair["distance_m"] <= POLICY["name_review_m"])]
    supported = [pair for pair in plausible if pair["supported"]]
    # Any other nearby/identifier/name candidate blocks automatic correspondence.
    if len(supported) == 1 and len(plausible) == 1:
        return "matched", supported[0]["polygon_feature_id"], "unique_nearby_name_or_reference_supported_correspondence", plausible
    if plausible:
        return "uncertain", None, "multiple_or_insufficient_or_conflicting_polygon_evidence", plausible
    return "distinct_point_only_candidate", None, "no_plausible_polygon_correspondence_under_matching_policy", []


def eligibility(record, classification, target_voltages):
    holds = []
    if classification != "distinct_point_only_candidate":
        holds.append("matched_or_uncertain_point_held_out_to_avoid_double_counting")
    kind, voltage = nullable(record.get("substation_type")), nullable(record.get("max_voltage"))
    if kind not in (None, "yes", "transmission"):
        holds.append("source_role_not_in_transmission_candidate_scope")
    if voltage is not None and voltage not in target_voltages:
        holds.append("source_numeric_voltage_outside_scope")
    text = " ".join(words(record.get("name")) + words(record.get("description")))
    if re.search(r"\b(kantor|office|taman|park)\b", text):
        holds.append("office_or_park_function_clue_requires_manual_review")
    if bool(nullable(record.get("construction"))) and bool(nullable(record.get("disused"))):
        holds.append("conflicting_status_tags")
    return not holds, holds


def match_substations(points, polygons, source_sha256, target_voltages):
    for frame, types in ((points, {"Point"}), (polygons, {"Polygon", "MultiPolygon"})):
        if frame.crs is None or frame.crs.to_epsg() != 4326 or not frame.geom_type.isin(types).all():
            raise ValueError("Substation matching requires valid EPSG:4326 Point and Polygon/MultiPolygon layers")
        if frame.geometry.isna().any() or frame.geometry.is_empty.any() or not frame.is_valid.all() or frame.id.isna().any() or frame.id.duplicated().any():
            raise ValueError("Substation matching source geometry/ID validation failed")
    point_records = sorted(points.to_dict("records"), key=lambda row: str(int(row["id"])))
    polygon_records = sorted(polygons.to_dict("records"), key=lambda row: str(int(row["id"])))
    polygon_geometries = np.array([row["geometry"] for row in polygon_records], dtype=object)
    rows = []
    for record in point_records:
        point = record["geometry"]
        projection = Transformer.from_crs(4326, f"+proj=aeqd +lat_0={point.y} +lon_0={point.x} +datum=WGS84 +units=m", always_xy=True)
        distances = shapely.distance(shapely.transform(polygon_geometries, projection.transform, interleaved=False), Point(0, 0))
        intersections = shapely.intersects(polygon_geometries, point)
        pairs = [pair_evidence(record, polygon, distances[index], intersections[index]) for index, polygon in enumerate(polygon_records)]
        classification, linked_id, reason, plausible = classify_pairs(pairs)
        eligible, holds = eligibility(record, classification, target_voltages)
        nearest = min(pairs, key=lambda pair: (pair["distance_m"], pair["polygon_source_id"]))
        retained_pairs = [pair for pair in pairs if pair in plausible or pair["same_numeric_source_id"] or pair["distinctive_name_match"] or pair["meaningful_reference_match"]]
        # Keep nearest evidence even for otherwise distinct points; full pair count is recorded.
        if nearest not in retained_pairs:
            retained_pairs.append(nearest)
        rows.append({
            "point_feature_id": f"power_substation_point:{int(record['id'])}",
            "source_id": str(int(record["id"])), "source_layer": "power_substation_point",
            "original_attributes": {key: nullable(value) for key, value in record.items() if key != "geometry"},
            "original_geometry": mapping(point), "osm_element_type": "unknown",
            "classification": classification, "classification_reason": reason,
            "matched_polygon_feature_id": linked_id,
            "eligible_for_point_candidate_layer": eligible, "publication_hold_reasons": holds,
            "source_status_verified": False, "duplicate_identity_verified": False,
            "compared_polygon_count": len(pairs), "plausible_polygon_count": len(plausible),
            "intersecting_polygon_count": int(intersections.sum()),
            "nearest_polygon_feature_id": nearest["polygon_feature_id"], "nearest_polygon_distance_m": nearest["distance_m"],
            "polygon_evidence": sorted(retained_pairs, key=lambda pair: (pair["distance_m"], pair["polygon_source_id"])),
        })
    counts = Counter(row["classification"] for row in rows)
    return {"matching_version": MATCHING_VERSION, "source_sha256": source_sha256, "policy": POLICY,
            "point_count": len(rows), "polygon_count": len(polygons),
            "pair_comparisons": len(rows) * len(polygons),
            "classifications": {key: counts[key] for key in CLASSES},
            "eligible_point_candidates": sum(row["eligible_for_point_candidate_layer"] for row in rows),
            "held_distinct_candidates": sum(row["classification"] == "distinct_point_only_candidate" and not row["eligible_for_point_candidate_layer"] for row in rows),
            "missing_point_numeric_voltage": int(points.max_voltage.isna().sum()),
            "confirmed_unique_station_count": None,
            "records": rows}


def write_matching_csv(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["source_id", "name", "substation_type", "max_voltage_v", "classification", "classification_reason",
               "matched_polygon_feature_id", "eligible_for_point_candidate_layer", "publication_hold_reasons",
               "compared_polygon_count", "plausible_polygon_count", "intersecting_polygon_count",
               "nearest_polygon_feature_id", "nearest_polygon_distance_m"]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in report["records"]:
            values = {key: row.get(key) for key in columns}
            values.update(name=row["original_attributes"].get("name"), substation_type=row["original_attributes"].get("substation_type"),
                          max_voltage_v=row["original_attributes"].get("max_voltage"), publication_hold_reasons=";".join(row["publication_hold_reasons"]))
            writer.writerow(values)


def representative_features(datasets):
    result = []
    for key in ("primary", "review"):
        for feature in datasets[key]:
            polygon = shape(feature["geometry"])
            point = polygon.representative_point()
            if not polygon.covers(point):
                raise ValueError(f"Representative point outside its published footprint: {feature['id']}")
            result.append({"type": "Feature", "id": feature["id"],
                           "properties": {"feature_id": feature["id"], "source_id": feature["properties"]["source_id"],
                                          "represented_feature_id": feature["id"], "inventory_group": key,
                                          "geometry_role": "derived_polygon_representative_point", "counts_as_inventory": False,
                                          "method": "Shapely point_on_surface of published footprint"},
                           "geometry": mapping(point)})
    return sorted(result, key=lambda feature: feature["id"])
