# Verified Source Audit — `IDN.gpkg`

Source-audit preservation note: all recorded source counts and qualifications below remain unchanged. The initial audit did not exhaustively match point/polygon records; the later [matching policy and QA](SUBSTATION_MATCHING.md) now account for all 68 × 2,753 pairs and publish 32 optional unvalidated points. The [current sidebar/legend simplification](SIMPLIFICATION_REPORT.md) changes presentation only and preserves all source/publication fingerprints. Source totals in this document must not be interpreted as filtered UI counts.

Audited against the uploaded 30,412,800-byte GeoPackage (30.41 MB) during preparation of these instructions. Numbers are **feature counts in the provided file**, not verified unique PLN assets. The input is EPSG:4326, and contains 26 layers, many outside electricity transmission. The three core layers are valid/nonnull geometric features in the checks performed, but cross-layer duplicates, network topology, true commissioning status and asset registry completeness have **not** been validated.

## Important source layer counts

| Source layer | Features | Scope |
|---|---:|---|
| `power_line` | 5,396 | Voltage filtering required |
| `power_substation_polygon` | 2,753 | Substation type and voltage filtering required |
| `power_substation_point` | 68 | QA only until validated |
| `power_transformer` | 950 | Exclude |
| `power_tower` | 121,396 | Exclude |
| `power_plant` | 643 | User-authorized generation context |

## Transmission line filtered results

- **4,374** line segments have `max_voltage` in `70000, 150000, 275000, 500000` volts.
- Target voltage counts: 150 kV **3,497**; 70 kV **365**; 500 kV **342**; 275 kV **170**.
- Target-voltage status groups are mutually exclusive: **4,345** `construction=false AND disused=false`, **25** `construction=true`, **4** `disused=true`.
- Outside the target group: 1,022 records, comprising **458** at 20 kV, **522** null-voltage and **42** other-voltage records. Of all 5,396 raw records, **6** are disused; therefore **2** disused records lie outside the target group.
- `name` missing: **4,772** raw lines. `circuits` populated: **944**, null: **4,452**. No line has a populated `start_date` in this export.
- Note: `voltages` values are strings and can contain semicolon-separated voltages; `max_voltage` is numeric in volts and is the deterministic primary filter.

## Substation polygon filtered results

- Primary: `substation_type='transmission' AND max_voltage IN target` = **622**; **621** not construction-tagged and **1** tagged construction.
- Review: type transmission + missing `max_voltage` = **37**; type null + target voltage = **239**; type distribution + target voltage = **172**. Total **448** distinct review candidates.
- Other type + target voltage = **19** (QA only). Type transmission + non-null voltage outside target = **32** (QA only).
- Of the raw 2,753 polygon records, **1,655** have missing `max_voltage`; **691** are tagged transmission in total and **1,555** distribution in total.
- `power_substation_point`: **68** records, all with null `max_voltage`; **1** is tagged transmission. Point/polygon duplicates were not exhaustively checked.

## Interpretation/limits

- `not_flagged_in_osm` = not marked construction/disused in source; **not** evidence of verified operation, ownership, COD or present existence.
- `substation_type` is an OSM tag and may be inconsistent with names containing “Gardu Induk”, “GI” or “GITET”. This is why the review candidate layer exists.
- No authoritative RUPTL/RUKN planned-project dataset, official power-system membership, line route identity, circuit-km, MVA capacity or AIS/GIS classification is included.
- Only source-derived geometries and selected properties should go to the frontend; preserve the raw source in a local nonpublic data directory.
- OSM/ODbL attribution, notices and share-alike/access rules apply as described in the supplied OpenInfraMap License.pdf.

## Recheck in the working repository

The code assistant must **inspect the actual mounted `IDN.gpkg`** and recompute these figures. These verified numbers are reproducibility targets for this specific upload, not constants to blindly insert in source code.

## Power-plant audit extension

The same unchanged GeoPackage contains 643 valid, nonempty plant footprints in EPSG:4326: 632 Polygon and 11 MultiPolygon. Construction is false on 633 and true on ten. The layer supplies no voltage, disused field or output unit. Missing values: name 113, operator 428, source 85, method 283, output 223, start date 613. These findings are captured separately from the historic grid audit in `scripts/expected-power-plant-audit.json`; no historic source count was replaced. See [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md).
