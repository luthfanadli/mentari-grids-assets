# Spatial Data Filter Specification — MENTARI Grids D2

Current publication note: exact line/primary/review predicates and historic source counts below are unchanged. The later matching supplement adds the optional 32-point dataset and 1,070 non-inventory symbols, for five GeoJSONs plus three metadata files; see [DATA_DICTIONARY.md](DATA_DICTIONARY.md) and [SUBSTATION_MATCHING.md](SUBSTATION_MATCHING.md). Three-file examples retain the starting MVP contract. The simplified sidebar has no source totals; matching-record cards/list and selection-driven legend use the existing filter result without changing preprocessing. See [SIMPLIFICATION_REPORT.md](SIMPLIFICATION_REPORT.md).

**Status:** approved starting logic for the MVP; source-tag categories are preliminary, **not** confirmation by PLN/DJK ESDM. **Input:** `data/raw/IDN.gpkg`. **Reference:** ToR Deliverable 2 and verified audit in `VERIFIED_DATA_AUDIT.md`.

## A. Single source of truth

Only source layers below may contribute to the production map:

| Source layer | Input features | Decision |
|---|---:|---|
| `power_line` | 5,396 | Filter to 500/275/150/70 kV |
| `power_substation_polygon` | 2,753 | Filter to primary transmission-tagged polygons; candidate polygons separate |
| `power_substation_point` | 68 | Review/QA only; zero default map features |
| `power_tower`, `power_transformer`, `power_plant`, generators, all non-power layers | Varies | Exclude from MVP |

Retain raw GPKG at `data/raw/` locally; do not publish or git-track that directory. Avoid a `SELECT *` export of all layers.

## B. Transmission lines: exact predicate and buckets

**Primary transmission voltage classes:** `{500000, 275000, 150000, 70000}` **volts**, using the numeric `max_voltage` field, **not** string matching of the `voltages` field. `max_voltage_kv = max_voltage / 1000` only when numeric, finite, positive and reliable. Preserve both `max_voltage` and `voltages` raw fields; optionally parse semicolon-separated `voltages` into `all_voltages_kv` for details, but do not use this to silently widen the initial filter.

Pseudocode:

```python
TARGET_V = {500_000, 275_000, 150_000, 70_000}
transmission_lines = power_line[power_line["max_voltage"].isin(TARGET_V)].copy()

def osm_status(record):
    if record["construction"] and record["disused"]:
        return "conflicting_tags"          # quarantine/manual review
    if record["disused"]:
        return "tagged_disused"
    if record["construction"]:
        return "tagged_construction"
    return "not_flagged_in_osm"             # NOT verified existing/operational
```

From the supplied GPKG:

| Output group | Count | On first load? |
|---|---:|---|
| `not_flagged_in_osm` | **4,345** | **YES** (OSM baseline; unverified status) |
| `tagged_construction` | **25** | NO, optional status filter |
| `tagged_disused` | **4** | NO, optional status filter |
| **All target-voltage lines** | **4,374** | In `transmission-lines.geojson` |

**Outside target voltage:** 1,022 line features = 5,396 - 4,374; exclude from production GeoJSON but account for them in QA. This includes 458 with `max_voltage=20000`, 522 with null voltage, and 42 with other voltage values. Two additional source `disused=true` features exist outside target voltage and **must not be accidentally included** in the 4,374 total.

**Special cases:** If `voltages` lists multiple values (e.g. `500000;150000`), retain that information, but classify the segment **once** using `max_voltage` for MVP. Avoid double-counting. Retain `location=overhead/underground/underwater/...` as supplied; don't infer HVDC from `location`. The source `circuits` field is sometimes null: preserve its known value and never assume one circuit.

## C. Substation polygons: selection and uncertainty

Primary inventory: `power_substation_polygon` with BOTH `substation_type == "transmission"` AND numeric `max_voltage` in `TARGET_V`. **Count: 622**. One of these has `construction=true`; default map should show the other **621**, with one separately selectable as tagged construction. They are *source-tagged preliminary transmission substations*, not officially validated GI/GITET.

Do not accidentally drop high-voltage GI/GITET candidates just because OSM says `distribution` or omits the type. Export these separately as *review candidates*:

| Candidate reason | Exact predicate | Count |
|---|---|---:|
| `transmission_missing_voltage` | type `transmission` AND numeric `max_voltage` is null | **37** |
| `high_voltage_unknown_type` | `max_voltage` in `TARGET_V` AND `substation_type` null | **239** |
| `high_voltage_distribution_tag` | `max_voltage` in `TARGET_V` AND type `distribution` | **172** |
| **Total review candidates** | Non-overlapping union | **448** |

The candidates are not counted in the primary inventory and **must be OFF by default**. Render them only when the user enables a clearly labeled `Review candidates (unvalidated)` layer. Show `review_reason` in the details; use different styling from primary polygons. Do not replace any original `substation_type` with `transmission` just to include them.

Further QA-only categories, to be counted but not automatically included:
- 19 polygon features have target voltage but another (non-`transmission`/`distribution`/null) substation type, e.g. `transition`, `generation`, `industrial`, `traction`.
- 32 type=`transmission` polygons have **non-target, non-null** voltage. Keep excluded, document potential other-voltage assets.
- 68 `power_substation_point` features all lack numeric `max_voltage`; only one is explicitly tagged `transmission`. Store for point-versus-polygon duplicate review, **not** production default. Their missing voltage must not be guessed from name or proximity.
- Substation names can contain `GI`/`GITET`, but names are review clues, **not a sufficient automatic certification** of voltage, substation function or status.

Preserve `construction` flags for polygons. `start_date`, `transformer_capacity_mva`, `insulation_type`, `commissioning_year`, and official project status are not available/reliable in the supplied source; show `Not available` rather than guessed attributes.

## D. Output data contract

Use **three production GeoJSONs**:

```text
public/data/transmission-lines.geojson
public/data/substations-primary.geojson
public/data/substations-review.geojson
```

Each GeoJSON is a valid `FeatureCollection` with EPSG:4326 geometries (RFC 7946 longitude/latitude). Do not simplify aggressively: preserve geometry fidelity and provide zoom/performance tests. Use lightweight, purpose-specific properties, not all unused source fields. Suggested normalized common properties (null when unavailable):

| Key | Definition |
|---|---|
| `feature_id` | Globally unique string `<source_layer>:<source_id>`; source id **as-is**, including negative IDs where present |
| `source_layer`, `source_id` | Original GeoPackage layer and original `id` converted to string; not GeoPackage `fid` |
| `asset_type` | `transmission_line` or `substation_polygon` |
| `display_name` | Original `name` or UI fallback such as `Unnamed line · OSM ID 123` (fallback is NOT official name) |
| `name`, `ref`, `operator` | Preserved original strings/null |
| `max_voltage_v`, `max_voltage_kv` | Original `max_voltage` and reliable normalized kV |
| `voltages_raw`, `all_voltages_kv` | Raw `voltages` and optional parsed kV list; don't force invalid values |
| `osm_tag_status` | `not_flagged_in_osm` / `tagged_construction` / `tagged_disused` / `conflicting_tags` |
| `source_status_verified` | Always false for this source (or explicit `null` for not reviewed), never `true` without evidence |
| `substation_type` | Original type for polygons; null for lines |
| `review_reason` | Candidate reason only; null in primary datasets |
| `location`, `circuits` | Original line attributes; null for substations |
| `mapped_geometry_length_km` | Optional, geodesically measured segment length; **NOT official circuit-km** |

Metadata files in `public/data/`:

- `summary.json`: actual raw counts, subset counts, current source-tag group counts, voltage distributions, completeness metrics and data version. **Generate from data, not hand-entered constants.**
- `data-catalog.json`: source `OpenInfraMap / OpenStreetMap`, file and layer info, license `ODbL`, original CRS, processing method, data limitations, `source_data_vintage: unknown` unless verified externally. The GeoPackage file modification date is not the OSM data vintage.
- `qa-report.json`: input counts, excluded counts by reason, missing values, geometry errors, duplicate IDs, source tag inconsistencies and test summary.

Other QA artifacts belong under `data/qa/`, outside deployable `public/`, and may include a rejected-feature inventory and the 68 point substations. Do not export any synthetic planned projects into production data.

## E. Determinism, QA and validation

- Confirm expected layer names, EPSG:4326, expected geometry families, valid/nonempty geometries and numeric fields; fail with clear exceptions if absent or malformed.
- Sort output consistently by `source_id` as string or stable numeric sort with deterministic ties; write UTF-8 JSON with null-safe serializers.
- Duplicate `source_id` **within a layer** should raise QA; distinct source layers may legally use the same numeric OSM ID.
- Verify classified subsets are mutually exclusive, have no duplicated `feature_id`, and every published line is one of the four target voltages.
- **Don't dissolve lines:** a feature is an OSM mapped segment, not necessarily a unique electrical transmission circuit or corridor.
- If reporting geometry length, use geodesic ellipsoidal measurement (WGS84, `pyproj.Geod` or equivalent), round for display only, preserve precision in source calculations; call it `mapped line geometry length`, not `circuit-km` or verified route length.
- If reporting KPI totals, disclose filters and status tags, not claims of verified national coverage.
- Add tests reproducing expected numbers from this exact GPKG; if another version is supplied, emit actual counts and a source-version mismatch instead of hiding changes.

## F. Planned projects and geographic grouping — intentionally deferred

The ToR also requires RUPTL 2025–2034/RUKN 2025–2060 planned lines/substations, project COD/status, HVDC interconnections and categorization by region/system. These are **not identifiable from the supplied GeoPackage**. Design TypeScript types/extension points for `planned_line`, `planned_substation`, and future `region`/`power_system` fields, but do not fabricate placeholder spatial features, create fake statistics or infer official network-system membership from coordinate proximity. Display `Planned assets — data not yet provided` as needed.

## G. Legal publishing checklist

- The supplied `License.pdf` identifies OpenStreetMap source data under **ODbL**; provide appropriate map/data notices and attribution with links.
- OSM derivative database redistribution may trigger share-alike/database accessibility requirements. Review ODbL obligations before publicly publishing the processed datasets; include the license notice, data source link and transformation methodology.
- Credit OpenInfraMap appropriately (appreciated, not mandatory per supplied export notice).
- Do not publicly deploy the original ToR or BNEF-licensed data. Check basemap service terms separately.

## H. User-authorized substation enhancement

The subsequent enhancement request authorizes an optional, default-off point-only candidate layer after full point–polygon matching QA and derived overview symbols for polygons. It preserves all existing line predicates, 622 primary polygons and 448 review polygons, including their original export bytes. No missing-voltage point enters primary inventory. The versioned policy, all 68 source-point classifications, eligibility rules, eight-file publication schema and counting/representation behavior are documented in [SUBSTATION_MATCHING.md](SUBSTATION_MATCHING.md). This supplement does not authorize deployment or change the historic source audit.
