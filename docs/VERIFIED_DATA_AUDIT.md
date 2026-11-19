# Verified source audit

The OSM tables count source features from the supplied GeoPackage. The planning audit counts project rows from three separate GeoJSONs. Reference metrics are recorded in `scripts/expected-audit.json`, `scripts/expected-power-plant-audit.json` and `scripts/expected-planning-audit.json`.

| Source property | Value |
| --- | --- |
| File | `data/raw/IDN.gpkg` |
| Bytes | 30,412,800 |
| SHA-256 | `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba` |
| Spatial layers | 26 |
| CRS | EPSG:4326 |
| OSM snapshot date | Unknown |

## Inspected layers

| Layer | Raw records | Use |
| --- | ---: | --- |
| `power_line` | 5,396 | Voltage-filtered segments |
| `power_substation_polygon` | 2,753 | Primary/review predicates |
| `power_substation_point` | 68 | All-pair matching before candidate eligibility |
| `power_plant` | 643 | Generation context |
| `power_transformer` | 950 | Excluded |
| `power_tower` | 121,396 | Excluded |

The four published-source layers have valid, nonempty geometries and unique IDs within each layer. Three substation polygon IDs are negative and retained. Source polygons/lines use their original geometry families; plants comprise 632 Polygon and 11 MultiPolygon records.

## Grid audit

- Target-voltage lines: **4,374** = 4,345 not flagged + 25 construction + 4 disused.
- Maximum voltage counts: 500 kV **342**, 275 kV **170**, 150 kV **3,497**, 70 kV **365**.
- Excluded lines: **1,022** = 458 at 20 kV + 522 null voltage + 42 other voltage. Of six raw disused lines, two are outside target scope.
- Raw line missing values: name **4,772**, circuits **4,452**, start date **5,396**.
- Primary polygons: **622** = 621 not construction-tagged + one construction-tagged.
- Review polygons: **448** = 37 transmission/missing voltage + 239 target voltage/missing type + 172 target voltage/distribution type.
- Excluded polygons: 19 target voltage/other type + 32 transmission/non-target voltage + 1,632 other records.
- Raw polygons: **1,655** missing numeric voltage; **691** transmission tags; **1,555** distribution tags.
- All **68 points** lack numeric voltage; only one is explicitly transmission-tagged.

The [matching audit](SUBSTATION_MATCHING.md) evaluates 187,204 pairs: two supported associations, 25 uncertain and 41 distinct candidates, of which 32 are eligible for the separate layer. This does not certify physical deduplication.

## Plant audit

All 643 footprints are published: 633 not construction-tagged, ten construction-tagged. The source has no voltage, disused or output-unit field.

| Attribute | Missing |
| --- | ---: |
| Name | 113 |
| Operator | 428 |
| Energy source | 85 |
| Method | 283 |
| Output | 223 |
| Start date | 613 |

The 420 nonnull output values retain unknown units; 30 start-date strings are not verified commissioning dates.

## RUPTL and RUKN planning files

The three supplied files match IPM's open planning downloads byte for byte. The committed planning audit records each input SHA-256 and the expected counts. The separate catalog lists all input and prepared file fingerprints. [IPM v2.0.0 data collection](https://github.com/sandro71626/ipm-model)

| Source file | Source bytes | RUPTL records | RUKN records | Drawable projects |
| --- | ---: | ---: | ---: | ---: |
| `ruptl_transmission.geojson` | 4,979,759 | 1,251 | 7 | 1,248 |
| `ruptl_substations.geojson` | 857,650 | 1,740 | 0 | 1,740 |
| `ruptl_generators.geojson` | 494,548 | 1,058 | 1 | 1,059 |
| **Total** | **6,331,957** | **4,049** | **8** | **4,047** |

All 4,057 rows have a unique source ID within their file. The generation projects occupy 796 distinct coordinate pairs. Substation projects occupy 877 pairs and reference 870 distinct source site IDs. They comprise 457 new works, 1,095 extensions and 188 uprates. All point records credit manual mapping by IPM. IPM labels 512 generator and 404 substation locations with medium confidence.

Raw transmission geometries comprise 1,239 LineStrings and 19 MultiLineStrings. Seven LineStrings collapse to a single coordinate. Three other LineStrings have distinct endpoints and a source route status of `none`. These ten rows retain their planning properties with null publication geometry. The private `data/qa/planning-qa.json` records their IDs and individual reasons. The 1,248 drawable routes comprise 1,077 tagged `drawn`, 142 `schematic` and 29 `assumed`.

Eight records credit RUKN 2025–2060 and carry source stage `Study`. Source target years range from 2025 to 2045, including projections beyond 2034. One substation project has no target COD year. Source labels and scenario years describe published plans.

## Recheck

Run the [documented preprocessing and Python tests](../README.md#regenerate-data). Public `qa-report.json` records actual metrics, exact audit differences, exclusions and structural validation. Full point evidence stays in private QA. Source/status, topology and completeness limitations are documented [separately](DATA_COVERAGE_AND_LIMITATIONS.md); structural QA does not validate official asset identity.

Run `python scripts/prepare_planning.py --output data/interim/planning-preview` for a planning candidate release. Inspect `data/qa/planning-qa.json`, then regenerate the four planning files together and run `pnpm check:data`. Source-version mismatches report expected and actual values before any publication writes.
