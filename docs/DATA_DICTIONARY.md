# Data dictionary

Publication schema **3**, pipeline **1.2.0**. GeoJSON uses RFC 7946 longitude/latitude in EPSG:4326, collection attribution/license notices and original signed source IDs. Selection rules belong to [the filter specification](DATA_FILTER_SPEC.md).

## Publication files

| File in `public/data/` | Records / role | Bytes |
| --- | ---: | ---: |
| `transmission-lines.geojson` | 4,374 original segments | 6,151,922 |
| `substations-primary.geojson` | 622 original polygons | 646,266 |
| `substations-review.geojson` | 448 original review polygons | 450,635 |
| `substations-point-candidates.geojson` | 32 unvalidated original points | 36,376 |
| `power-plants.geojson` | 643 original footprints | 1,111,875 |
| `substation-display-points.geojson` | 1,070 derived, uncounted symbols | 490,830 |
| `summary.json` | Counts/completeness | 5,017 |
| `data-catalog.json` | Provenance/policies/checksums | 10,799 |
| `qa-report.json` | Aggregate structural/source QA | 12,790 |

Six GeoJSONs total **8,887,904 bytes**; all nine files total **8,916,510 bytes**. There are **6,119 original records** across all flags. Symbols do not increase that count. The original line/primary/review geometry exports remain unchanged; points and plant footprints preserve full source coordinate precision.

## Original-record properties

| Property | Type | Meaning |
| --- | --- | --- |
| `feature_id` | string | `<source_layer>:<source_id>`, also the GeoJSON feature `id` |
| `source_layer`, `source_id` | string | Original layer and signed `id`, never GeoPackage `fid`; OSM element kind unknown |
| `asset_type` | string | `transmission_line`, `substation_polygon`, `substation_point` or `power_plant` |
| `display_name`, `display_name_is_fallback` | string, boolean | Source name or explicit synthetic label with original ID |
| `name`, `ref`, `operator` | string or null | Original attributes; no ownership/identity certification |
| `max_voltage_v`, `max_voltage_kv` | number or null | Source numeric volts and finite positive value / 1000 |
| `voltages_raw` | string or null | Unchanged source voltage text |
| `all_voltages_kv` | number[] | Valid positive semicolon tokens / 1000, unique in source order; not a selection predicate |
| `construction`, `disused` | boolean or null | Source flags; absent disused field remains null for substations/plants |
| `osm_tag_status` | string | `not_flagged_in_osm`, `tagged_construction`, `tagged_disused`; conflicting flags are quarantined, not published |
| `source_status_verified` | false | Source flags do not verify operation |
| `substation_type` | string or null | Original substation role, unchanged |
| `review_reason` | string or null | One of the three polygon reasons in the filter spec, or `point_only_unvalidated`; otherwise null |
| `location`, `circuits` | string / number or null | Original line attributes; no inferred location or default circuit count |
| `mapped_geometry_length_km` | number or null | WGS84 geodesic line length, not official circuit-km; null for other assets |

Original records include a geometry-derived `bbox=[west,south,east,north]`. Null means unavailable; invalid voltage tokens are ignored in parsing while raw text is retained.

## Point-candidate properties

| Property | Meaning |
| --- | --- |
| `geometry_role` | `original_point` |
| `matching_classification` | `distinct_point_only_candidate`, not certified physical identity |
| `matching_reason`, `matching_version` | QA decision and policy version |
| `nearest_polygon_feature_id` | Nearest raw polygon, potentially outside publication; context only |
| `nearest_polygon_distance_m` | Per-point WGS84 AEQD screening distance, not survey accuracy |

All 32 candidates retain null numeric voltage and exact source coordinates. Unknown-voltage filtering also controls the 37 missing-voltage review polygons. It starts enabled and is independent of numeric voltage choices. See [matching](SUBSTATION_MATCHING.md).

## Plant properties

Plants have `geometry_role=original_power_plant_footprint` and null voltage/disused fields. `plant_source`, `plant_method`, `plant_output_raw`, `plant_start_date_raw`, `plant_name_en`, `plant_description` and `plant_wikidata` preserve source attributes.

`plant_output_unit=null`: raw output is not assumed MW or verified capacity. Raw start date is not verified COD. `plant_representative_point=[longitude,latitude]` is a derived interior display location, not another source record.

## Substation display points

One interior Point per published primary/review polygon. Properties: `feature_id`, `source_id`, `represented_feature_id`, `inventory_group` (`primary`/`review`), `method`, `geometry_role=derived_polygon_representative_point` and `counts_as_inventory=false`.

Both feature ID and represented ID equal the parent polygon ID. Parent/symbol repetition is intentional; filtering, selection and statistics resolve the original record. Plant symbols follow the same counting rule at runtime.

## Metadata and private QA

- `summary.json`: source fingerprint/vintage, raw/per-subset counts, statuses, voltage distributions, missing values, fallback labels, review reasons, default selection, presentation/matching aggregates and GeoJSON byte sizes. Missing planned data has count null, not zero.
- `data-catalog.json`: source/license links, CRS, method, matching/plant policies, field meanings, limitations and each GeoJSON's role/count/bytes/SHA-256.
- `qa-report.json`: raw-layer inventory, geometry/attribute/ID checks, voltage inconsistencies, exclusions, audit actuals/differences, matching/plant QA and unchanged-source proof. PASS is structural/selection QA, not official asset validation.

`data_version` combines the source hash prefix with pipeline version; no current timestamp affects determinism. Use all nine files from one run.

Private `data/qa/` contains exclusion records, conflict quarantine, source-point review and reproducible full matching JSON/CSV. Raw source, reference documents and these internal evidence tables are not publication assets.
