# Coverage and limitations

This is the supplied OpenInfraMap/OpenStreetMap export's preliminary inventory. It is not independently verified by PLN/DJK ESDM, and no national coverage percentage can be established. The source's OSM data vintage is **unknown**; its file modification date is not a data observation date.

## Verified scope

The 30,412,800-byte GeoPackage has 26 layers. Only 5,396 line records, 2,753 substation polygons, 68 point substations and 643 power-plant footprints are read as spatial records. All have EPSG:4326, valid nonempty geometry and unique IDs within their layer. Three polygon IDs are negative and remain unchanged.

| Published subset | Total | Not flagged | Tagged construction | Tagged disused |
| --- | ---: | ---: | ---: | ---: |
| Target-voltage line segments | 4,374 | 4,345 | 25 | 4 |
| Primary transmission-tagged polygons | 622 | 621 | 1 | 0 |
| Separate review polygons | 448 | 448 | 0 | 0 |
| Separate eligible point-only candidates | 32 | 32 | 0 | 0 |
| Power-plant context footprints | 643 | 633 | 10 | 0 |

Substation and power-plant layers have no `disused` field. The zero disused category is a computed source-category count, not proof that no substation is disused. Both candidate layers are off by default. Primary polygons are explicitly tagged transmission and at target numeric voltage; this does not certify GI/GITET identity or operation. Point-only candidates retain unknown voltage and unverified function and are never included in the primary count.

| Maximum line voltage | Segments across all flags |
| --- | ---: |
| 500 kV | 342 |
| 275 kV | 170 |
| 150 kV | 3,497 |
| 70 kV | 365 |

Each source line is counted once using numeric maximum voltage. Multi-voltage tags remain available in details. Segments are not dissolved into corridors, circuits or unique routes. Source circuits are known on only 638 of the published 4,374 segments; no circuit-km is calculated.

## Explicit exclusions and review

| Exclusion reason | Count |
| --- | ---: |
| Lines at 20 kV | 458 |
| Lines missing numeric voltage | 522 |
| Other non-target line voltages | 42 |
| Polygon target voltage, other substation type | 19 |
| Transmission polygons, non-target nonnull voltage | 32 |
| Other polygons outside primary/review predicates | 1,632 |
| Source points audited (32 optional candidates; 36 held from publication) | 68 |

These reconcile exactly: 5,396 = 4,374 + 1,022 lines; 2,753 = 622 + 448 + 19 + 32 + 1,632 polygons. Two of the six raw disused lines lie outside the target scope and stay excluded. The 68 points all lack numeric maximum voltage; only one is tagged transmission. Point voltage is not inferred, and geographic associations do not certify shared station identity.

The versioned matching enhancement compares all 68 points against all 2,753 raw polygons: 187,204 pair evaluations. It records two supported matches, 25 uncertain and 41 distinct candidates under conservative thresholds. Supported source associations do not certify duplication. Of the 41 distinct candidates, 32 pass optional-layer eligibility; nine remain held for source-role or office-name review. Matched/uncertain points are withheld regardless of polygon-layer visibility. Original point coordinates and null voltage are retained. See [matching policy](SUBSTATION_MATCHING.md) and internal `data/qa/substation-matching-report.json`/CSV.

The 448 candidates comprise 37 transmission-tagged/missing-voltage polygons, 239 target-voltage/missing-type polygons and 172 target-voltage/distribution-tagged polygons. Original tags remain unchanged. Towers (121,396), transformers (950), individual generators and all telecom/water/pipeline/petroleum layers are excluded. The aggregate QA report lists every excluded layer's actual count.

Additional source QA found one unparseable voltage string: polygon ID `943539373`, name `GITET Aur Duri Baru`, raw `voltages='500000/275000/150000'`, with null numeric maximum voltage and null type. It remains excluded by the exact predicates, even though its name is a review clue. Its voltage is not guessed or silently repaired. This illustrates why an OSM-tag subset is incomplete.

## Power-plant source coverage

The context layer publishes all 643 footprints, including 11 MultiPolygons; this is not a verified unique-plant registry. Name is missing on 113, operator on 428, energy source on 85, method on 283, output on 223 and start date on 613. No voltage, disused field or output unit is supplied. The 420 known output values retain unspecified units and are not summed or converted to MW. Start dates include partial/approximate strings and are not verified COD. Repeated names/Wikidata tags and multiple footprints are not automatically merged. Generator layers remain excluded. See [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md).

## Attribute completeness

Within publication subsets:

- Line names are missing on 3,794/4,374 segments, operators on 3,269, references on 4,319, and circuits on 3,736. Every raw line lacks `start_date`.
- Primary polygon names are missing on 22/622, operators on 81 and references on 595.
- Review polygon names are missing on 34/448, operators on 100, references on 446 and numeric voltage on 37.

The source includes one populated raw polygon `start_date`; it is not used as a verified commissioning year. Unknown details display **Not available**. UI fallback names are marked as such. Operator names are source strings, not verified ownership.

## Remaining Deliverable 2 requirements

| ToR requirement from the supplied guide | Current implementation | Needed evidence/data |
| --- | --- | --- |
| Existing 70/150/275/500 kV lines | Preliminary OSM subset, status unverified | Authoritative route/asset registry, validation and crosswalk |
| GI/GITET substations | Tagged primary polygons plus separate review queue | Official station identifiers, scope and deduplication |
| By power system and region | No fabricated grouping or filter | Authoritative electrical-system crosswalk and agreed regional/province boundaries/attribution |
| RUPTL 2025–2034 / RUKN 2025–2060 planned lines/substations | Missing data documented in About; no records or speculative runtime type | Approved project inventory and available spatial layers |
| HVDC, converter stations and interconnections | No verified classification/projects | Authoritative technology/project records |
| Overhead/submarine/underground | Original `location` shown where supplied | Validation of asset technology and route sections |
| COD, capacity/MVA, thermal ratings, official circuit-km, AIS/GIS, costs | Not available | Authoritative values, units, dates and source references |
| Source log and dictionary | Published catalog, QA, hashes, method and dictionary; download UI removed | Source vintage remains unknown |

The original ToR document was not present in the repository, so its text could not be independently inspected. Traceability follows `CODEX_START_HERE.md`. The supplied `data/raw/License.pdf` was read. No restricted BNEF material was supplied or published.

Point–polygon source matching is now screened reproducibly; physical duplicate identity, point–point station identity, electrical connectivity, route identity and official status remain unvalidated. The prior audit also found polygon–polygon overlaps, including two primary–review pairs and a review–review pair; their original feature subsets remain unchanged. No official unique-station total is claimed. Geodesic lengths are not official route lengths or circuit-km.

The map displays derived interior symbols for the same selected polygon records below zoom 10, then original footprints from zoom 10. Symbols are not counted as additional records. Separate point-only symbols retain original source locations. The deduplicated **rendered in viewport** count can differ from selected-record counts because of view extent and scale-dependent rendering; the list retains all matching original records.

## Data reuse

The processed derivative database is distributed under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) with [OpenStreetMap attribution](https://www.openstreetmap.org/copyright) and OpenInfraMap credit. Each GeoJSON embeds the license URI and attribution. The About download section is removed; all nine static `/data/` files remain accessible for browser rendering. Source/reference documents and internal QA stay outside static publication. Basemap reuse follows the configured provider's terms.

## Reading the filters and legend

Sidebar layer/voltage checkboxes do not display source totals. The cards and list count original records matching all active filters; map viewport counts remain separate. Power plants have their own count/key and do not use grid voltage controls. The legend describes this same filtered selection, not national completeness or exact contents of the viewport. It hides categories without matches and separates line voltage colors from source-status patterns. Review/point candidates remain unvalidated, and unknown voltage is not guessed. See [current UI and cleanup verification](SIMPLIFICATION_REPORT.md).
