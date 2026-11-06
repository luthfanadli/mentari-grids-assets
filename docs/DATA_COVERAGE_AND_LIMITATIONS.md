# Coverage and limitations

This is a preliminary OpenInfraMap/OpenStreetMap inventory with **unknown source vintage**, not an independently verified national asset registry. The original ToR has not been supplied; Deliverable 2 scope follows the supplied project brief.

## What the counts mean

The [source audit](VERIFIED_DATA_AUDIT.md) records raw metrics and [the dictionary](DATA_DICTIONARY.md) lists publication totals.

- Lines are mapped segments, not unique routes, circuits or corridors. Multi-voltage records are classified once by numeric maximum voltage.
- Primary substations have explicit transmission tags and target voltage; they are not certified GI/GITET stations.
- Review polygons and point-only candidates remain separate, unvalidated and off by default.
- Plants are source footprints, not individual generators or verified unique power stations. Repeated names, overlapping geometries and Wikidata tags are not automatically merged.
- Overview symbols represent the same polygon records. Selected counts do not change with zoom; viewport counts describe deduplicated rendered records.

"Not flagged in OSM" means no construction/disused tag is true where those fields exist. It does **not** verify present existence or operation. Substations and plants have no disused field; their zero disused category is not evidence that none are disused.

## Missing attributes

| Published subset | Missing source values |
| --- | --- |
| 4,374 lines | Name 3,794; operator 3,269; reference 4,319; circuits 3,736 |
| 622 primary polygons | Name 22; operator 81; reference 595 |
| 448 review polygons | Name 34; operator 100; reference 446; numeric voltage 37 |
| 32 point candidates | Numeric voltage 32; physical identity/function unverified |
| 643 plants | Name 113; operator 428; energy source 85; method 283; output 223; start date 613 |

All raw lines lack start dates. Unknown details display **Not available**; fallback names are identified as interface labels. Operator strings do not establish ownership. Plant output units are unspecified: values are not converted to MW or summed as capacity, and raw start-date strings are not verified COD.

## Selection and identity limitations

The exact [filter rules](DATA_FILTER_SPEC.md) intentionally exclude non-target/missing-voltage lines and polygons outside the primary/review predicates. They cannot establish complete national transmission coverage.

For example, polygon `943539373` (GITET Aur Duri Baru) has raw voltage text `500000/275000/150000`, null numeric maximum voltage and null type. It remains excluded rather than guessed or silently repaired.

[Point/polygon matching](SUBSTATION_MATCHING.md) screens every point against every polygon, but a supported correspondence is not certified duplicate identity. Unknown point voltages never inherit nearby/containing polygon values. Point-point identity, existing polygon overlaps, topology, route identity and plant/substation connections remain unresolved. No official unique-station total or coverage percentage is claimed.

## Remaining Deliverable 2 gaps

| Requirement | Missing evidence |
| --- | --- |
| Official existing line/station inventory | Authoritative asset IDs, registry validation and deduplication |
| Region and power-system grouping | Agreed boundaries and an authoritative electrical-system crosswalk |
| RUPTL 2025–2034 / RUKN 2025–2060 plans | Approved project records and spatial layers |
| HVDC, converter stations and interconnections | Verified technology/project classifications |
| Overhead/submarine/underground coverage | Validation of supplied location tags and route sections |
| COD, capacity/MVA, thermal rating, circuit-km, AIS/GIS and costs | Authoritative values with units, dates and provenance |

No planned infrastructure or geographic membership is fabricated. Geodesic line geometry length is not official circuit-km. New source versions require reviewed audit differences rather than edits that conceal changes.

## Publication

The local source `License.pdf` identifies OSM data under ODbL. Source attribution, derivative license notices and basemap credits remain visible; [README](../README.md#attribution-and-assets) records attribution and font provenance. Static data URLs are publicly fetched by the app even without download controls. Raw/reference files, restricted materials and internal QA are not static assets.
