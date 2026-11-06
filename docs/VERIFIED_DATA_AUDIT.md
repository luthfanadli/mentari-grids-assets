# Verified source audit

These are feature counts from the supplied GeoPackage, not unique or operational PLN assets. The expected metrics are enforced by `scripts/expected-audit.json` and `scripts/expected-power-plant-audit.json`.

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

## Recheck

Run the [documented preprocessing and Python tests](../README.md#regenerate-data). Public `qa-report.json` records actual metrics, exact audit differences, exclusions and structural validation. Full point evidence stays in private QA. Source/status, topology and completeness limitations are documented [separately](DATA_COVERAGE_AND_LIMITATIONS.md); structural QA does not validate official asset identity.
