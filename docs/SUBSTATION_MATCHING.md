# Reproducible substation matching and representation

This user-authorized enhancement preserves the 622 primary polygons, 448 review polygons and all transmission-line rules/exports. It adds a reviewed, optional point-only candidate dataset and representative display symbols. Nothing is deployed. Source data remains preliminary OSM, with unknown vintage and unverified physical/operational identity.

## Reproduce

Current UI: optional layers are named **Review polygons** and **Point-only candidates**; both remain off by default. The sidebar contains no dataset totals. Matching counts are shown in cards/list, and the legend is derived from that same filtered original-record selection. Unknown-voltage points produce no transmission-voltage legend item; derived representatives add no legend categories or inventory records. Matching thresholds, 2/25/41 classifications, eligibility and geometries are unchanged. See [the cleanup report](SIMPLIFICATION_REPORT.md).

Use the GIS environment described in `README.md`:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_data.py --input data/raw/IDN.gpkg --output public/data --qa-output data/qa
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
pnpm.cmd check:data
```

`scripts/substation_matching.py` is called by the existing preprocessing CLI. No alternate data source, frontend dependency or package-manager change is required. Missing/malformed source data and source-version mismatches still fail explicitly. The original `expected-audit.json` remains unchanged.

## Inputs and all-pair audit

The supplied 30,412,800-byte GeoPackage has SHA-256
`6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`.
All 68 source points and **all 2,753 raw polygons**, including polygons outside publication, are compared: **187,204 pair evaluations**. Each report row records `compared_polygon_count=2753`. Records sort by original ID string; negative polygon IDs retain their sign. Source IDs are never replaced with GeoPackage `fid`.

Source validity, nonempty geometry, EPSG:4326, expected geometry families and unique layer IDs are checked. Original point attributes and geometry are preserved in the internal report. Distances are calculated in a separate point-centered WGS84 azimuthal equidistant projection for each point, against every polygon. This avoids treating degrees as meters or choosing one UTM zone for Indonesia. Distance to stored projected edges is a screening approximation; it is not survey accuracy or electrical connectivity.

Intersection is computed on original geometries. Proximity thresholds are transparent policy choices, not official duplication tolerances. The source has no explicit OSM element-kind field: equal numeric IDs across layers cannot establish the same OSM element. No absolute-value conversion or node/way/relation inference is made from IDs.

## Matching policy v1.0.0

The policy is embedded in the full QA report, aggregate public QA and catalog.

1. Compare intersection, meter distance, signed numeric ID, distinctive name, meaningful reference, operator, numeric maximum voltage, source substation type and construction flag.
2. Normalize names for case, accents and punctuation. Remove generic utility/station terms such as PLN, Gardu Induk and GI, plus explicit numeric kV text. **Retain station-code numbers**: PK 276 and PK 277 are different. Use distinctive token-set equality rather than fuzzy substring matching. Generic names alone provide no identity evidence.
3. A plausible polygon is any intersecting polygon, any within **500 m**, an equal signed numeric source ID at any distance, or a distinctive-name/meaningful-reference match within **1,000 m**.
4. A supported correspondence requires distinctive-name or meaningful-reference agreement within **100 m**, without available attribute conflicts. Known voltage, role, operator, reference, distinctive name or construction differences block support. Unknown values do not manufacture agreement; numeric IDs and common operator alone never establish support.
5. Classify as **matched** only when exactly one plausible polygon exists and is supported. More than one plausible candidate blocks automatic correspondence even if one looks stronger. Matched means a policy-supported source correspondence, not a certified physical duplicate.
6. Classify as **uncertain** when plausible evidence exists but the unique supported condition fails. Intersection alone remains uncertain.
7. Classify as **distinct_point_only_candidate** when no plausible polygon exists under these rules. Distinct describes this export/policy, not proof of a unique station, a transmission role, or absence of an unmapped polygon.

Names or proximity never supply missing voltage. No candidate is promoted into primary inventory. Neither a spatial intersection nor source-ID equality alone triggers deletion or merging.

## Actual result

| Classification | Source points | Publication decision |
| --- | ---: | --- |
| matched | 2 | Held outside the point-only layer; association recorded |
| uncertain | 25 | Held outside the point-only layer pending review |
| distinct_point_only_candidate | 41 | 32 eligible; nine held for role/function review |
| Total | 68 | All accounted for |

The supported correspondences are point `14305665334` (Sandai) to polygon `1175895912`, and point `7973241708` (Bukit Kemuning) to polygon `931931107`. Name and geographic evidence support these associations; their raw point voltages remain null and duplicate identity remains unverified. Bukit Kemuning's polygon stays in the original missing-type review subset.

Six source points intersect five footprints. Four of those points remain uncertain: two unnamed points inside GI Toili, an unnamed point inside GI Bogor Baru with conflicting operator evidence, and a generically named PLN point inside an excluded unnamed polygon. They are not converted into confirmed duplicates by containment.

Of the 41 distinct candidates, nine are held: five distribution-tagged records, two minor-distribution records, one generation record, and one office-name clue (`Kantor Layanan PLN Unit Kopang`). These are retained in QA with explicit hold reasons, not deleted. Office/park name or description clues trigger manual review rather than a claim that tagging is wrong. The remaining 32 have unknown/unspecified roles or a transmission tag; **all 32 still have unknown numeric voltage**. They are exploratory source locations, not 32 verified additional transmission stations.

Changing name normalization to preserve code numbers avoids falsely matching PK 274 and PK 277 merely because both begin with PK. The fixture counts above reflect that rule; historic raw-source audit metrics are not changed to accommodate matching outcomes.

## QA artifacts and public datasets

Internal, gitignored `data/qa/substation-matching-report.json` contains source fingerprint, policy/version, aggregate classifications, eligible/held counts, null unique-station count, and one row per source point. Each row includes original attributes/geometry, source ID/kind uncertainty, classification/reason, matched polygon link when supported, publication holds, all-pair count, nearest polygon, intersection count and retained polygon evidence.

Evidence retains every plausible polygon, numeric-ID or distinctive-name/reference match (including far-away contextual matches), and the nearest polygon even for distinct points. Every pair is evaluated; irrelevant far-away pairs are counted rather than expanded into a large public table. `substation-matching-report.csv` provides a reproducible 68-row review index with original names/type/voltage, decision/reason, matched link, holds, distances and comparison counts. Both reports are deterministic for the same source and environment.

Public additions:

- `substations-point-candidates.geojson`: 32 eligible **original** Point geometries, full source coordinate precision, source-derived properties, `asset_type=substation_point`, `review_reason=point_only_unvalidated`, original signed ID, matching policy/reason and nearest polygon context. No inherited voltage, operator, capacity, system or province assignment.
- `substation-display-points.geojson`: one derived interior point per published polygon, 1,070 total. `geometry_role=derived_polygon_representative_point`, `counts_as_inventory=false`, `represented_feature_id` equals the parent polygon ID. These are presentation symbols, not source point substations. They are computed from the unchanged published footprints using Shapely `representative_point`/`point_on_surface`, verified inside the parent geometry, and retained at full generated precision.

The three existing inventory GeoJSONs are **byte-identical** to their previous exports. Schema-v2 summary/catalog/QA metadata includes the additions, counts, role distinctions, checksums and policy. All eight publication files must be generated/used together. Full raw point/polygon tables and internal review evidence are not copied into public assets.

## Map and counting behavior

- **Zoom < 10:** selected primary and enabled review polygons are represented by interior point symbols. Primary symbols are teal (amber for construction); review symbols have an amber outline. Parent voltage/status/search/layer filters determine visibility.
- **Zoom >= 10:** original polygon fills/boundaries replace their representative symbols. No buffered or replacement footprint is created.
- **Point-only layer:** separately toggleable, off initially, lazily fetched on enable, and drawn as pink outlined circles at original locations at both scales. Unknown-voltage filtering applies explicitly. A failed request is retryable without enabling or altering primary inventory.
- A marker click resolves the parent feature ID and opens the **original polygon** details; fitting/selection uses the parent footprint. Point-only details identify original Point geometry, unknown voltage and QA context.
- KPIs and table rows derive only from original inventory/review feature arrays, not symbol features. IDs deduplicate accidental repeated records; `counts_as_inventory=false` symbols are excluded. Point-only counts are separate from both polygon groups.
- Rendered viewport counts canonicalize `represented_feature_id`/`feature_id` across sources, tile fragments and multiple style layers. Changing zoom does not change selected-record counts.
- Matched and uncertain raw points never enter the candidate GeoJSON or visible statistics, including when their related polygon layer is switched off. A supported source association is therefore not counted as an additional point record.

Counts describe mapped records, not confirmed unique physical stations. Existing polygon–polygon overlap cases from the earlier audit remain review issues; this enhancement does not silently change the requested 622/448 subsets or claim physical deduplication of those polygons.

The UI uses MapLibre [minzoom/maxzoom layer rules](https://maplibre.org/maplibre-style-spec/layers/) for the scale transition. Interior markers follow [Shapely point_on_surface semantics](https://shapely.readthedocs.io/en/stable/reference/shapely.point_on_surface.html). Current references were consulted; the installed pinned GIS environment remains unchanged.

## Validation and remaining gaps

Tests cover generic/intersection-only uncertainty; distinctive supported matches; conflicting operators/construction and ambiguous polygons; signed IDs with unknown element type; distance thresholds; meaningful code numbers; candidate holds; full 68×2753 coverage; exact original point coordinates; representative containment including concave footprints; unchanged line/polygon file hashes; deterministic publication and full matching reports; independent toggles, unknown voltage, retries, symbol clicks and zoom transitions; viewport/statistic deduplication and mobile layout.

Operational status, authoritative GI/GITET identifiers, complete transmission scope, point-point physical deduplication, official station counts, COD/MVA/circuit-km/AIS–GIS, planned RUPTL/RUKN assets and system/region assignment remain unverified or unavailable. No hosting action is part of this enhancement.
