# Coverage and limitations

The baseline inventory uses an OpenInfraMap/OpenStreetMap export of **unknown snapshot date**. The planning layers use three GeoJSON files from Indonesia Power Map (IPM), with source labels for RUPTL 2025–2034 and RUKN 2025–2060. The original ToR has not been supplied. Deliverable 2 scope follows the supplied project brief.

## What the counts mean

The [source audit](VERIFIED_DATA_AUDIT.md) records raw metrics and [the dictionary](DATA_DICTIONARY.md) lists publication totals.

- Lines are mapped segments, not unique routes, circuits or corridors. Multi-voltage records are classified once by numeric maximum voltage.
- Primary substations have explicit transmission tags and target voltage; they are not certified GI/GITET stations.
- Review polygons and point-only candidates remain separate, unvalidated and off by default.
- Plants are source footprints, not individual generators or verified unique power stations. Repeated names, overlapping geometries and Wikidata tags are not automatically merged.
- Each planning record represents one source project entry. Extensions and upgrades can share a site with each other or with a baseline feature. Report project entries separately from baseline asset records.
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

All baseline lines lack start dates. Unknown details display **Not available** and fallback names are identified as interface labels. Operator strings do not establish ownership. The GeoPackage omits plant output units. Its raw output cannot be summed as MW and its start dates require independent confirmation. The planning files supply units for their own capacity fields and distinguish RE Base and ARED target years. Confirmation of commissioning requires separate evidence.

## Selection and identity limitations

The exact [filter rules](DATA_FILTER_SPEC.md) intentionally exclude non-target/missing-voltage lines and polygons outside the primary/review predicates. They cannot establish complete national transmission coverage.

For example, polygon `943539373` (GITET Aur Duri Baru) has raw voltage text `500000/275000/150000`, null numeric maximum voltage and null type. It remains excluded rather than guessed or silently repaired.

Of 1,555 raw polygons tagged `distribution`, 172 have a target maximum voltage and appear in the review layer. The other 1,383 retain polygons in the source GeoPackage. Of those, 1,378 lack numeric voltage, four have 20 kV and one has 44 kV.

[Point/polygon matching](SUBSTATION_MATCHING.md) screens every point against every polygon, but a supported correspondence is not certified duplicate identity. Unknown point voltages never inherit nearby/containing polygon values. Point-point identity, existing polygon overlaps, topology, route identity and plant/substation connections remain unresolved. No official unique-station total or coverage percentage is claimed.

## Comparison with Indonesia Power Map

The table compares all baseline records in MENTARI with IPM’s **15 November 2026** data release. We counted the six GeoJSON downloads linked from IPM’s map on 19 November 2026. The three supplied planning inputs had the same SHA-256 digests as IPM’s corresponding downloads. [IPM open data](https://indonesiapowermap.com/#data) · [IPM release and methodology](https://github.com/sandro71626/ipm-model)

| Data | MENTARI Grids | IPM open data |
| --- | --- | --- |
| Baseline transmission | 4,374 OSM line segments selected by numeric maximum voltage of 70, 150, 275 or 500 kV | 1,947 transmission sections with endpoint, route length and circuit fields |
| Baseline substations | 622 primary polygons, 448 review polygons and 32 point candidates | 1,158 substation and switchyard entries with source IDs and capacity fields |
| Baseline generation | 643 plant footprints, with no source unit for output | 3,199 generation entries, including captive plants, rooftop aggregates and electricity imports |
| Planning inputs | 1,258 transmission entries, 1,740 substation projects and 1,059 generation entries | Same three input files and counts |

IPM combines PLN/ESDM planning material, OSM and its own mapping. Its release covers 38 provinces and reports across eight regions. The three planning files contain 34 distinct province labels and seven `system` values, with `NUSA_TENGGARA` covering both NTB and NTT. MENTARI retains the labels supplied for each project. The baseline GeoPackage supplies no official regional/system membership. Differences between baseline totals cannot quantify missing assets without matching and validating the underlying records. IPM counts rooftop aggregates and imports in its tables, although its map omits those points. [IPM data dictionary](https://indonesiapowermap.com/data/open/README.md) · [IPM publication policy](https://indonesiapowermap.com/docs/publication_policy.md)

The reference map’s older **About** text, dated 22 September 2026, quotes 4,053 lines, about 990 substations (931 with coordinates), and 593 plants. The November downloads linked from that same page yield the comparison above. [Reference map and About](https://indonesiapowermap.com/web/preview_indonesia)

Of the 4,057 planning records, 4,049 cite RUPTL and eight cite RUKN (seven transmission studies and one generation study). Substation projects comprise 457 new works, 1,095 extensions and 188 uprates. IPM attributes all supplied point locations and line geometries to its manual mapping. Some locations or routes are indicative. In particular, line records carry `drawn`, `schematic`, `assumed` or `none` route status. A map symbol or line cannot verify exact siting, electrical connectivity or an operating date.

## Remaining Deliverable 2 gaps

| Requirement | Missing evidence |
| --- | --- |
| Official existing line/station inventory | Authoritative asset IDs, registry validation and deduplication |
| Region and power-system grouping | Agreed boundaries and a verified crosswalk for the baseline assets |
| RUPTL 2025–2034 / RUKN 2025–2060 plans | Independent confirmation of planning table entries, route accuracy and current status. RUKN coverage is limited to the eight supplied studies. |
| HVDC, converter stations and interconnections | Verified technology/project classifications |
| Overhead/submarine/underground coverage | Validation of supplied location tags and route sections |
| COD, capacity/MVA, thermal rating, circuit-km, AIS/GIS and costs | Verified as-built values, units, dates and provenance. Selected planning fields have source-reported values. |

No planned infrastructure or geographic membership is fabricated. Geodesic line geometry length is not official circuit-km. New source versions require reviewed audit differences rather than edits that conceal changes.

## Publication

The local `License.pdf` identifies the OpenInfraMap export as OSM data under ODbL. The planning data credit Sitompul, S. A. (2026), *Indonesia Power Map: Data Collection*, v2.0.0. IPM publishes its data under CC BY-SA 4.0 and identifies ODbL obligations for OSM-derived material. [IPM licence and citation](https://github.com/sandro71626/ipm-model#lisensi)

Source attribution, derivative license notices and basemap credits remain visible. [README](../README.md#attribution-and-assets) records attribution and font provenance. Static data URLs are publicly fetched by the app even without download controls. Raw/reference files, restricted materials and internal QA stay outside the publication directory.
