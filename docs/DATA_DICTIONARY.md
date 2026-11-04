# Data dictionary

The four inventory/review GeoJSONs are RFC 7946 FeatureCollections in EPSG:4326 longitude/latitude. The original three line/polygon exports remain unchanged, without simplification or dissolve, at seven coordinate decimals and normalized ring winding. Point-only candidates retain exact original point coordinates. Each original inventory/review feature has a string `id`, identical to `properties.feature_id`, and geometry-derived `[west,south,east,north]` `bbox`. A fifth GeoJSON contains derived polygon display points, separately identified and excluded from inventory counts. Each collection embeds attribution and the ODbL URI.

| Property | Type | Meaning |
| --- | --- | --- |
| `feature_id` | string | `<source_layer>:<source_id>`, unique across original inventory/review exports. Derived display symbols intentionally reuse their parent's ID. |
| `source_layer` | string | Original `power_line` or `power_substation_polygon`. |
| `source_id` | string | Original `id`, never GeoPackage `fid`. Negative IDs preserved. OSM element kind is not verified. |
| `asset_type` | string | `transmission_line`, `substation_polygon` or `substation_point`. Candidate status does not establish physical asset identity. |
| `display_name` | string | Original nonblank name, otherwise `Unnamed line/substation · OSM ID …`. |
| `display_name_is_fallback` | boolean | Synthetic interface label flag; a fallback is not an official name. |
| `name`, `ref`, `operator` | string or null | Original source values, without ownership verification or label-based inference. |
| `max_voltage_v` | number or null | Original numeric `max_voltage`, in **volts**. |
| `max_voltage_kv` | number or null | Finite positive numeric `max_voltage_v / 1000`; display only. |
| `voltages_raw` | string or null | Original `voltages`, including empty/multi-value strings. |
| `all_voltages_kv` | number[] | Distinct finite positive numeric semicolon tokens / 1000, in source order. Invalid tokens are not coerced; raw value is retained. Never widens the numeric maximum-voltage filter. |
| `construction` | boolean or null | Original flag. All supplied core-layer records have a nonnull value. |
| `disused` | boolean or null | Original line flag. Null for polygons, whose source layer has no such field. |
| `osm_tag_status` | string | Source flag category below; not official project or operational status. |
| `source_status_verified` | false | Always false for these datasets. |
| `substation_type` | string or null | Original polygon type; null for lines. `distribution` remains unchanged in review records. |
| `review_reason` | string or null | One of three polygon reasons below or `point_only_unvalidated`; null for lines/primary polygons. |
| `location` | string or null | Original line location (e.g. overhead/underwater); null for polygons. Not an HVDC classifier. |
| `circuits` | number or null | Original known line value; null when absent and for polygons. No default of one. |
| `mapped_geometry_length_km` | number or null | WGS84 ellipsoidal line geometry length via `pyproj.Geod`; full calculation precision in export, two decimals in UI. Not official route length or circuit-km. Null for polygons. |

## Source flag categories

| Value | Predicate | Application behavior |
| --- | --- | --- |
| `not_flagged_in_osm` | Neither flag true; absent polygon disused field is not asserted false in output. | Default visible; unverified operation. |
| `tagged_construction` | Construction true, disused not true. | Optional; dashed map styling, explicit details. |
| `tagged_disused` | Disused true, construction not true. | Optional; dotted/faded lines. |
| `conflicting_tags` | Both true. | Internal quarantine; never published or included in map filters. Supplied source has zero conflicts. |

## Polygon selection

Primary: `substation_type == 'transmission'` and numeric `max_voltage` in `{70000,150000,275000,500000}`. Review is the disjoint union:

| `review_reason` | Exact predicate | Supplied-source count |
| --- | --- | ---: |
| `transmission_missing_voltage` | Transmission type and null numeric maximum voltage | 37 |
| `high_voltage_unknown_type` | Target numeric maximum voltage and null type | 239 |
| `high_voltage_distribution_tag` | Target numeric maximum voltage and distribution type | 172 |

The two candidate toggles are independent of primary-substation visibility. With either enabled, **Unknown voltage** controls the 37 missing-voltage polygon candidates and all 32 point-only candidates. It is enabled initially; selecting only a numeric voltage still includes unknowns until this checkbox is cleared. No value is guessed from a name, nearby line or containing polygon.

## Point-only candidates and representative symbols

`substations-point-candidates.geojson` contains only eligible `distinct_point_only_candidate` source points under the [versioned matching policy](SUBSTATION_MATCHING.md). It never contains the two matched or 25 uncertain source points. Nine additional distinct records remain held for role/function review. All published source points retain unknown voltage and `source_status_verified=false`.

| Additional point property | Meaning |
| --- | --- |
| `geometry_role` | `original_point`; original source location retained. |
| `matching_classification` | `distinct_point_only_candidate`, relative to the policy and export, not verified physical-station identity. |
| `matching_reason` | Deterministic QA decision reason. |
| `matching_version` | Matching policy version (`1.0.0`). |
| `nearest_polygon_feature_id` | Nearest raw source polygon, possibly outside publication; contextual link only. |
| `nearest_polygon_distance_m` | Point-centered WGS84 AEQD screening distance to polygon geometry, not official survey accuracy. |

`substation-display-points.geojson` contains 1,070 derived Point features, one per published polygon. Its smaller presentation-only properties are `feature_id`, `source_id`, `represented_feature_id`, `inventory_group` (`primary`/`review`), `geometry_role=derived_polygon_representative_point`, `counts_as_inventory=false` and `method`. Both feature `id` and `represented_feature_id` equal the parent polygon's ID; repeated IDs across a parent and its symbol are intentional, not additional inventory records. Symbols are generated inside the published footprint with Shapely point_on_surface, without changing the footprint. They use the parent's filtered attributes at render time and do not inherit a separate source point's identity.

## Metadata

Metadata totals describe complete published subsets across source flags. They are not filter results. The sidebar no longer repeats these totals; cards and the list count matching original records, and the legend is derived from those records. `Unknown voltage` covers 37 review polygons and all 32 optional source points when those layers are enabled. No data property or serialized output changed for the sidebar/legend simplification; see [SIMPLIFICATION_REPORT.md](SIMPLIFICATION_REPORT.md).

Schema-v2 `summary.json` contains raw counts for all layers, actual per-subset counts, statuses, maximum-voltage distributions, missing-value metrics, fallback-label counts, review reasons, default selection and GeoJSON byte sizes. `datasets.point_candidates` is separate from `datasets.review`; `substation_point_matching` contains 2/25/41 classification counts and eligibility totals. `substation_presentation` holds symbol count, zoom threshold and its non-inventory role. `planned_assets.count` is null, not zero: no authoritative dataset was provided.

`data-catalog.json` provides source/licensing, unknown source vintage, input SHA-256, original/output CRS, transformation description, matching policy, field meanings, limitations and each GeoJSON's role/count/bytes/SHA-256. Presentation datasets are not added to inventory counts. `data_version` combines source hash prefix and pipeline version (`1.1.0`); no current timestamp is inserted, so identical processing is byte deterministic.

`qa-report.json` contains all-layer metadata/counts; core-layer fields/nulls, validity, bounds, geometry types and duplicate/negative IDs; voltage-tag inconsistencies; exclusion counts; conflict/point counts; actual audit metrics; exact expected/actual differences; publication validation and unchanged-source checks. QA PASS covers structural and selection checks, not official asset validation. Frontend/backend test execution results live in the implementation report, not a fabricated test stamp in generated data.

Internal `data/qa/exclusion-report.json` records the layer, original ID, voltage, type, status and exclusion reason for every excluded line/polygon. Other layers have counted scope exclusions; points are held separately. The original ToR and license PDF are not public assets.

Internal `substation-matching-report.json` and CSV account for all 68 points and all 187,204 comparisons, retaining original point attributes/geometries, matching evidence, classifications, publication holds and policy. Public aggregate QA includes the policy/counts and representative-symbol containment check. The source audit in `expected-audit.json` remains unchanged; no station voltage or official identity is inferred.
