# Substation point versus polygon — source analysis

Historical read-only analysis. The subsequent user-authorized [matching and visualization enhancement](SUBSTATION_MATCHING.md) implements a conservative matching policy and a separate optional 32-record point-only layer. Source findings below remain valid; statements about application behavior describe the earlier analysis stage. Current implementation/results are in `SUBSTATION_ENHANCEMENT_REPORT.md`.

Analysis date: 4 November 2026 (Asia/Jakarta). This is a read-only analysis of the supplied export, not a change to publication filters or an authoritative asset validation. The application, expected audit and six `public/data/` files remain unchanged.

## Interpretation

Point and polygon describe **geometric representation**, independently of voltage, network function, capacity and operational status. A point records a mapped location without a facility boundary. A polygon records a mapped footprint; that footprint may be a whole site, a building or a smaller mapped portion, depending on source practice. Neither geometry certifies an official GI/GITET asset.

OSM permits substation nodes and areas, while recommending areas for most substations. A transformer is a device, normally mapped separately from its containing substation. Thus a substation point must not automatically be interpreted as an individual transformer, and a substation polygon must not automatically be interpreted as a transmission station. See [OSM substation mapping](https://wiki.openstreetmap.org/wiki/Tag:power=substation) and [transformer mapping](https://wiki.openstreetmap.org/wiki/Tag:power=transformer).

Network role is another dimension. OSM distinguishes transmission switching/interconnection functions from distribution functions; distribution substations can be fed from transmission grids. The 172 target-voltage polygons tagged distribution are review candidates under the repository specification, not automatically proven OSM errors. Local definitions and project scope matter. The D2 target scope remains 70/150/275/500 kV. See [transmission tagging](https://wiki.openstreetmap.org/wiki/Tag:substation=transmission) and [distribution tagging](https://wiki.openstreetmap.org/wiki/Tag:substation=distribution).

## Source and methods

Input: `data/raw/IDN.gpkg`, 30,412,800 bytes, SHA-256:
`6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`.

`scripts/analyze_substations.py` reads the raw point/polygon layers and target-voltage source lines. It compares attributes, validates source geometry, checks point coverage and polygon intersections, measures proximity, screens names, and calculates mapped polygon areas. It writes internal QA under `data/qa/substation-analysis/`; it does not repair tags, assign voltage/system/province, merge records or publish features.

- Topological tests use the actual EPSG:4326 geometries, with points on boundaries included by the intersection test. All six covered points are strictly inside, not merely on a boundary.
- Nearest polygon/line distances use a separate point-centered WGS84 azimuthal equidistant projection for each of the 68 points. No single national UTM zone or longitude/latitude degree distances are used as meters. Distances to projected stored edges are a screening approximation, not survey accuracy.
- Line-endpoint distances and polygon areas use WGS84 ellipsoidal measurements with PyProj. Areas use normalized exterior/hole winding. Area is mapped geometry area, not official land area or a capacity estimate.
- Name normalization removes case/punctuation differences; it does not infer identity from generic names or remove words until a match is forced.
- An independent GeoPandas spatial join reproduced the six points/five footprints result. Source hashes match before/after the audit.

The source data vintage remains unknown. Current OSM documentation was consulted for semantics; no live OSM geometry was substituted for the supplied snapshot.

## Actual layer comparison

Both layers have the same **13 attribute columns**: `id`, `name`, `name_en`, `description`, `substation_type`, `construction`, `ref`, `operator`, `wd_operator`, `voltages`, `max_voltage`, `frequency`, `start_date`. The schema is the same; population and geometry differ.

| Metric | `power_substation_point` | `power_substation_polygon` |
| --- | ---: | ---: |
| Source records | 68 | 2,753 |
| Actual geometry | 68 Point | 2,753 Polygon |
| CRS | EPSG:4326 | EPSG:4326 |
| Invalid, empty or null geometries | 0 | 0 |
| Duplicate IDs within layer | 0 | 0 |
| Exact duplicate stored geometries within layer | 0 | 0 |
| Negative original IDs | 0 | 3 |
| Nonblank name | 43 | 2,381 |
| Nonblank operator | 33 | 2,430 |
| Nonblank reference | 1 | 37 |
| Nonblank substation type | 23 | 2,373 |
| Numeric maximum voltage present | **0** | **1,098** |
| Nonblank raw `voltages` string | **0** | **1,099** |
| Numeric maximum voltage in D2 target scope | 0 | 1,052 |
| Construction flag true | 0 | 1 |
| Populated `start_date` | 0 | 1 |

Every point's `voltages` is the empty string, not SQL null. A null-only completeness metric would mistakenly report this column as complete. Missing point voltage is therefore not explained by a numeric parser failing to recognize an otherwise populated voltage field. A value mentioned in `name` is still only a name clue.

The one polygon with a nonblank raw voltage string but null numeric maximum has raw `500000/275000/150000`, ID `943539373`, name `GITET Aur Duri Baru`. It lacks substation type too and remains outside the exact publication predicates. No slash-based repair was applied.

Neither substation layer contains a `disused` field. Unset construction flags do not establish operational status; populated `start_date` does not certify COD.

### Network-role source tags

| `substation_type` | Points | Polygons |
| --- | ---: | ---: |
| transmission | 1 | 691 |
| distribution | 18 | 1,555 |
| minor_distribution | 2 | 88 |
| generation | 1 | 4 |
| yes (unspecified role) | 1 | 5 |
| Missing | 45 | 380 |
| Other types | 0 | 30 |

The other polygon types include transition, industrial, traction and nonstandard values. Geometry alone does not resolve them. In particular, the raw polygon layer contains many distribution-tagged records, so rendering all polygons as GI/GITET would misrepresent the available evidence.

## Point–polygon spatial relationships

Six of 68 points lie inside **five distinct polygon footprints**. The other 62 are outside all supplied substation polygons. Zero points lie in multiple polygons, and no numeric IDs are shared across the two layers. Different record IDs do not prove different physical stations.

| Point original ID | Point source name | Containing polygon original ID / name | Current polygon subset |
| --- | --- | --- | --- |
| `11078010994` | Missing | `950292848` / Gardu Induk Toili | Primary, source maximum 150 kV |
| `11078010995` | Missing | `950292848` / Gardu Induk Toili | Same primary footprint |
| `12730004982` | Missing | `628259420` / Gardu Induk Bogor Baru | Primary, source maximum 150 kV |
| `14305665334` | PLN Gardu induk 150 kV Sandai | `1175895912` / Gardu Induk Sandai | Primary, source maximum 150 kV |
| `7973241708` | Gardu Induk PLN Bukit Kemuning | `931931107` / Gardu Induk Bukit Kemuning | Review: target voltage, missing type |
| `4145890616` | PLN | `413233112` / missing name | Outside publication predicates |

These are **spatial association / possible duplicate candidates**, not six confirmed duplicate records. Two separate point geometries inside GI Toili also coincide with source target-line endpoints, but this does not establish whether they represent a whole station, connection locations or inconsistent tagging. They cannot safely be counted as two new stations.

Point Sandai's name mentions 150 kV and lies inside a source-tagged 150 kV primary footprint, yet its own structured voltage fields remain empty. Linking it to a validated station record later could preserve both sources, but overwriting its raw voltage or counting the marker as a second station would be inappropriate.

### Distance to any substation polygon

The following categories are mutually exclusive. Distance is to the polygon footprint, not its centroid.

| Relationship | Points |
| --- | ---: |
| Strictly inside a footprint | 6 |
| Outside, within 100 m | 2 |
| Outside, over 100 through 250 m | 12 |
| Outside, over 250 through 500 m | 7 |
| Outside, over 500 through 1,000 m | 7 |
| More than 1,000 m from all supplied footprints | 34 |
| Total | 68 |

Thus eight are within 100 m **including the six inside**, and 34 are within 1 km including those inside. The median nearest-footprint distance is about 1.20 km; the maximum is about 56.94 km. A 100 m threshold is an exploratory review distance, not an approved deduplication rule. Neither the 62 outside points nor the 34 beyond 1 km are automatically transmission stations absent from the polygon inventory.

The two outside points within 100 m are ID `12672403731` (`Sub Station 20 kv`, about 67.5 m) and unnamed ID `5050327050` (about 72.8 m). The first's name is an especially clear reason not to inherit the voltage of a nearby transmission line.

Six points have an exact normalized name matching some polygon somewhere in the export; **none** has such a match within 100 m. Generic names such as PLN and Gardu Listrik produce distant matches. Conversely, Sandai and Bukit Kemuning have differing names despite footprint containment. Name-only and proximity-only joins both require review.

## Relationship with transmission lines

Distances were measured against all 4,374 in-scope source segments, including source construction/disused flags, solely as QA context.

- Nine points are within 100 m of a target-voltage segment; only six are within 100 m of a target-segment endpoint.
- At 25 m, the corresponding counts are five and three.
- A line passing near/through a point is not evidence of an electrical connection or the point's voltage. Source endpoint proximity strengthens a review clue but still does not validate bus, circuit or station identity.
- No line voltage, network membership, commissioning status or official region was transferred to a point.

## Priority point records

There is one explicit transmission point and five points with GI/GITET/Gardu Induk name clues. These are six distinct review priorities, not an approved six-station addition.

| Point ID / name | Evidence and spatial context | Appropriate interpretation |
| --- | --- | --- |
| `4465682088` / Gardu Listrik | Only point tagged transmission; voltage absent. Nearest supplied polygon about 9.07 km; nearest target line about 8.80 km. | Validate source tag, position, voltage and identity; do not inherit nearest polygon properties. |
| `1743289266` / GI Hittu | Type and voltage absent; nearest supplied footprint about 4.62 km. | Potential missing/offset record or another context; a name clue only. |
| `5232177554` / Gardu Induk | Type and voltage absent; nearest footprint about 706 m. | Generic name and proximity are insufficient to establish identity. |
| `6081633811` / GARDU INDUK | Type and voltage absent; nearest footprint about 648 m. | Manual identity review. |
| `7973241708` / Gardu Induk PLN Bukit Kemuning | Inside a target-voltage review polygon. | Association/possible double representation review before any station count. |
| `14305665334` / PLN Gardu induk 150 kV Sandai | Inside a primary polygon; structured point voltage absent. | Association/possible double representation review; name text is not structured voltage. |

Two other point records have attribute-anomaly clues: `Kantor Layanan PLN Unit Kopang` (`1763309063`) and `Taman Pakuwon` (`7657518367`, description `Public Park`). These labels suggest reviewing whether the recorded function is really a substation. They do not, by themselves, prove incorrect tagging or authorize deletion.

## Polygon quality also requires review

Valid polygon geometry and distinct IDs do not establish a one-to-one mapping to physical stations.

- 23 polygon pairs intersect. Fifteen have positive area overlap, all above 1 m²; eight only touch. Fourteen of the 15 overlapping pairs are nested. No pair has exactly equal geometry.
- There are **zero overlapping primary–primary pairs**, **two primary–review overlapping pairs**, and **one review–review overlapping pair**. Other overlaps involve excluded polygons.
- Source IDs `615868418` and `943309151` are both named Gardu Induk Lolak, both in the missing-type review group, and overlap by approximately 19,789 m². This is a strong duplicate/inconsistent-footprint review candidate, not an automatic merge.
- `GISTET Kembangan` / `GIS Kembangan` and `GIS 150 Kv` / `GIS Pantai Indah Kapuk` are the two primary–review nested pairs. They may represent differing site extents or components; no official station linkage was established.
- A larger footprint containing a smaller one may represent multiple source modeling levels, a real colocated facility, or a duplicate. Nesting alone does not determine which.

Raw mapped area statistics further show why polygons are not uniformly large transmission facilities:

| Polygon group | Median mapped area | Additional screen |
| --- | ---: | --- |
| All 2,753 polygons | 71.6 m² | 1,450 footprints below 100 m² |
| 622 primary polygons | 19,455.8 m² (about 1.95 ha) | Six below 1,000 m² |
| 448 review polygons | 14,525.7 m² (about 1.45 ha) | 15 below 1,000 m² |

Areas are QA clues only; they do not validate function, legal boundary, transformer MVA or capacity. Across all raw polygons, three planar geographic centroids fall outside their own geometry. A simple centroid is therefore not always suitable for an inside-footprint map marker.

## Consequences for the current D2 application

The present selection is conservative **because of source tags, numeric voltage and the approved QA rules**, not because point geometry is inherently invalid:

- Primary: 622 polygons explicitly tagged transmission at numeric 70/150/275/500 kV; 621 visible by default and one construction-tagged polygon optional.
- Review: 448 polygons under three documented predicates, off by default. Their record count is not a confirmed count of distinct additional stations.
- Source points: all 68 held outside publication. None passes a target-numeric-voltage test with its own attributes. The single transmission point is still missing voltage.
- Other polygons: remain excluded with their recorded reasons. Polygon geometry alone does not justify widening the inventory.

The existing `MapCanvas.vue` renders published footprints; it does not load the 68 raw substation points. Polygon selection uses their original IDs. A small footprint can look like a dot at national zoom, and the OSM basemap can contain its own symbols independently of inventory overlays. Visual appearance is not proof of source geometry type.

If better national-zoom visibility is later wanted, derive **display markers from the selected polygons**, preferably with an interior representative point. Preserve the polygon feature/station linkage and keep marker count separate from source feature count. Those display markers must not be confused with the independent `power_substation_point` records or counted as extra substations.

If point records are later introduced, retain them as a separately labeled unvalidated review layer until identity, voltage and role are supported. A future station entity can link multiple source point/polygon records without overwriting their raw values; authoritative IDs and validation evidence should control the physical-station count. The present TypeScript contract would also need explicit Point geometry support for such a layer. No such application changes were made during this analysis.

## Reproduction and verification

Use the Python GIS environment documented in `README.md`:

```powershell
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/analyze_substations.py
pnpm.cmd check:data
```

Internal outputs:

- `data/qa/substation-analysis/analysis.json`: 104,875 bytes; aggregate screens, all 68 point review records and polygon intersection pairs.
- `data/qa/substation-analysis/point-review.csv`: 14,150 bytes; 68 rows plus header, original attributes, nearest-footprint/line evidence and explicitly unvalidated review hints.

The analysis script validates geometry families, CRS, IDs, source immutability and row consistency. Independent spatial-join/count checks passed; `pnpm check:data` still verifies the unchanged 5,444 published features, six files, counts, versions and checksums. No frontend build/test rerun was necessary for an analysis-only addition. Existing source vintage, operational status, official voltage validation, authoritative station identity, planned projects, capacity and power-system/region gaps remain unresolved.
