# Data filter specification

The OSM inventory uses the supplied `data/raw/IDN.gpkg` and `scripts/prepare_data.py`. Three IPM GeoJSON inputs form the separate planning publication. Source-version targets are recorded in [the audit](VERIFIED_DATA_AUDIT.md) and `scripts/expected-*.json`.

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

For the OSM inventory:

- Validate EPSG:4326, expected geometry families, required attributes, numeric values, flags, unique integral source IDs and valid nonempty geometry. Reject malformed inputs; quarantine conflicting flags.
- Preserve signed source `id`, never GeoPackage `fid`. Original feature IDs are `<source_layer>:<source_id>`. Equal numeric IDs in different layers do not establish OSM identity.
- Normalize polygon winding. Lines/substation polygons retain seven coordinate decimals without simplification or dissolve. Published original points and plant footprints retain full source precision.
- Derive interior polygon representatives with Shapely `representative_point`, validate containment and reuse parent IDs. Representatives are display-only, never additional inventory.
- Measure line geometry with WGS84 `pyproj.Geod`; label it mapped geometry length, not official route length or circuit-km.
- Preserve missing values as null. No official region/system, planned infrastructure, capacity or operational status is inferred.

## Planning projects

`scripts/prepare_planning.py` preserves one record per supplied source project in the transmission, substation and generation files. The source field identifies RUPTL or RUKN. A valid supplied project location or route is displayed at its original coordinates. A missing, invalid or explicitly unavailable route produces a register entry with null geometry. Null geometry contributes to register totals and is excluded from mapped and viewport counts.

The three project layers load independently when enabled. Filter projects by source, supplied stage and supplied target year. Search uses source project names, IDs, site IDs, province, system, endpoints and technology where available. The grid voltage selector reads the explicit project `voltage_kv` for transmission and substation projects. Generation projects are independent of the voltage selector. OSM status filters apply only to inventory records.

## Outputs and validation

The OSM inventory has six GeoJSON files and three metadata files with their source attribution and ODbL notices. The planning publication adds three GeoJSON files and a catalog with IPM attribution, CC BY-SA 4.0 and the notice for OSM-derived data. Both publications use deterministic ordering, UTF-8/CRLF serialization and checksums. Each pipeline checks the input SHA-256 before and after processing and reports audit differences before writing publication files. [Data dictionary](DATA_DICTIONARY.md)

Private QA under `data/qa/` contains exclusions, status conflicts, source-point review and all matching evidence. Do not copy raw data, source references or full internal review tables into `public/`.

The UI filters the published subsets without changing these rules. Its primary/review/point/plant counts remain separate; viewport counts canonicalize parent IDs across representations. Unknown voltage is an explicit candidate filter, not a guessed numeric value.
