# Data filter specification

Input: the supplied `data/raw/IDN.gpkg`. Source-version targets are recorded in [the audit](VERIFIED_DATA_AUDIT.md) and `scripts/expected-*.json`. Rules run in `scripts/prepare_data.py`; counts are validation targets, not selection predicates.

## Spatial scope

Only `power_line`, `power_substation_polygon`, `power_substation_point` and `power_plant` are read as features. Other layers are counted in QA but excluded, including towers, transformers and individual generators.

Numeric target voltage is **{70000, 150000, 275000, 500000} volts**. Use numeric `max_voltage` for selection. Display `max_voltage / 1000` in kV; raw multi-value `voltages` tags never widen the filter.

## Lines

Select `power_line.max_voltage` in the target set: **4,374 segments**. Each feature is counted once, without dissolving routes or multiplying by circuits.

| Source status | Predicate | Count | Default |
| --- | --- | ---: | --- |
| `not_flagged_in_osm` | Neither construction nor disused true | 4,345 | On |
| `tagged_construction` | Construction true, disused not true | 25 | Off |
| `tagged_disused` | Disused true, construction not true | 4 | Off |
| `conflicting_tags` | Both true | 0 | Quarantine |

The 1,022 excluded lines comprise 458 at 20 kV, 522 with null numeric voltage and 42 at other voltages. Two raw disused lines are outside target scope and remain excluded. Preserve source location/circuits when supplied; do not infer HVDC or assume one circuit.

## Substation polygons

Primary: `substation_type == "transmission"` **and** numeric maximum voltage in the target set: **622 polygons**, including one construction-tagged record. Default selection: 621.

Review is the disjoint union below, independently toggleable and **off by default**:

| Review reason | Predicate | Count |
| --- | --- | ---: |
| `transmission_missing_voltage` | Transmission type, null numeric maximum voltage | 37 |
| `high_voltage_unknown_type` | Target numeric voltage, null type | 239 |
| `high_voltage_distribution_tag` | Target numeric voltage, distribution type | 172 |
| **Total** | | **448** |

Keep original type tags unchanged. Exclude 19 target-voltage polygons with other types, 32 transmission polygons with non-target nonnull voltage and 1,632 other polygons. Names containing GI/GITET are review clues, never automatic voltage/function certification.

## Source points

Audit **all 68 points against all 2,753 raw polygons**, including excluded polygons, using the [matching policy](SUBSTATION_MATCHING.md). Publish only the 32 eligible distinct point-only candidates in a separate default-off layer. Hold matched, uncertain and ineligible records in private QA. All source points lack numeric voltage; none enters the primary polygon inventory or inherits polygon attributes.

## Power plants

Publish all **643** valid `power_plant` footprints separately: 633 not construction-tagged and ten construction-tagged. The layer is on by default; construction remains optional. Status and search apply, but grid voltage filters do not: the source has no voltage field.

Preserve energy-source, method, raw output, raw start-date, English-name, description and Wikidata tags. Output units remain null; do not infer MW, aggregate capacity, verified COD, generator membership or grid connections.

## Geometry, IDs and counting

- Validate EPSG:4326, expected geometry families, required attributes, numeric values, flags, unique integral source IDs and valid nonempty geometry. Reject malformed inputs; quarantine conflicting flags.
- Preserve signed source `id`, never GeoPackage `fid`. Original feature IDs are `<source_layer>:<source_id>`. Equal numeric IDs in different layers do not establish OSM identity.
- Normalize polygon winding. Lines/substation polygons retain seven coordinate decimals without simplification or dissolve. Published original points and plant footprints retain full source precision.
- Derive interior polygon representatives with Shapely `representative_point`, validate containment and reuse parent IDs. Representatives are display-only, never additional inventory.
- Measure line geometry with WGS84 `pyproj.Geod`; label it mapped geometry length, not official route length or circuit-km.
- Preserve missing values as null. No official region/system, planned infrastructure, capacity or operational status is inferred.

## Outputs and validation

Publish the six GeoJSONs and three metadata files listed in [the dictionary](DATA_DICTIONARY.md), with attribution and ODbL notices. Deterministic ordering, UTF-8/CRLF serialization and checksums must remain stable across platforms. Check source SHA-256 before/after processing and report exact audit differences before writing publication files.

Private QA under `data/qa/` contains exclusions, status conflicts, source-point review and all matching evidence. Do not copy raw data, source references or full internal review tables into `public/`.

The UI filters the published subsets without changing these rules. Its primary/review/point/plant counts remain separate; viewport counts canonicalize parent IDs across representations. Unknown voltage is an explicit candidate filter, not a guessed numeric value.
