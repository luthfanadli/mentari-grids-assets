# Substation matching policy

Policy **1.0.0**, implemented in `scripts/substation_matching.py` and run by the standard preprocessing command. It preserves primary/review polygon subsets and line rules. Matching supports source QA; it never certifies physical duplication, supplies voltage or promotes points into primary inventory.

## Inputs and evidence

Compare all **68 source points × 2,753 raw polygons = 187,204 pairs**, including polygons outside publication. Preserve signed IDs, original point attributes and coordinates. Validate CRS, geometry and layer IDs before matching.

Intersection uses original EPSG:4326 geometries. Each point gets a WGS84 azimuthal equidistant projection for metric distances to every polygon. Distances to projected stored edges are screening approximations, not survey measurements or electrical connectivity.

Evidence includes intersection, distance, signed numeric ID, distinctive names, meaningful references, operator, known numeric maximum voltage, source role and construction flag. OSM element kind is absent; equal numeric IDs across layers cannot establish the same OSM element.

## Decision rules

1. Normalize case, accents and punctuation; remove generic utility/station words and explicit kV text. Keep station-code numbers: PK 276 and PK 277 differ. Names use distinctive token-set equality, not fuzzy substrings.
2. A polygon is plausible if it intersects, lies within **500 m**, shares the signed numeric ID at any distance, or shares distinctive name/meaningful reference within **1,000 m**.
3. Support requires distinctive-name or meaningful-reference agreement within **100 m**, with no known voltage, operator, reference, distinctive-name, role or construction conflict. Missing values do not manufacture agreement.
4. **Matched**: exactly one plausible polygon and that polygon is supported. Another plausible polygon blocks automatic correspondence.
5. **Uncertain**: plausible evidence exists but the unique supported condition fails. Intersection alone stays uncertain.
6. **Distinct point-only candidate**: no plausible polygon under this policy. This does not prove a unique physical station or transmission function.

Neither source-ID equality, common operator nor spatial containment alone supports a match. Matching never transfers polygon attributes to points.

## Results and eligibility

| Classification | Points | Decision |
| --- | ---: | --- |
| `matched` | 2 | Withhold from point layer |
| `uncertain` | 25 | Withhold pending identity review |
| `distinct_point_only_candidate` | 41 | 32 eligible; nine held |
| **Total** | **68** | Every point accounted for |

Supported associations are Sandai (`14305665334` → `1175895912`) and Bukit Kemuning (`7973241708` → `931931107`). They are source correspondences, not certified duplicates. Six points intersect five footprints; four remain uncertain, including unnamed Toili/Bogor records and generic PLN evidence.

Only distinct candidates can be eligible. Hold known non-transmission roles, known non-target voltage, conflicting flags and office/park name or description clues for review. The nine held distinct records comprise five distribution, two minor-distribution, one generation and one office-name clue. All **32 eligible source points retain unknown numeric voltage** and unverified function/identity.

## Reproduce and review

Run [preprocessing and Python tests](../README.md#regenerate-data), followed by `pnpm check:data`.

Private `data/qa/substation-matching-report.json` records source fingerprint, policy, aggregate results and one row per point, including:

- Original attributes/geometry and compared-polygon count.
- Classification/reason, supported link if any, eligibility and hold reasons.
- Intersection/plausibility counts, nearest polygon and retained pair evidence.

Every pair is evaluated. Evidence retains plausible polygons, ID/name/reference matches (including distant contextual matches) and the nearest polygon; irrelevant distant pairs are counted without exporting 187,204 full rows. The UTF-8 BOM CSV provides a deterministic 68-row review index. Public metadata contains aggregate counts/policy rather than complete internal tables.

## Display and counting

Eligible points use original coordinates in a separate default-off/lazy layer at every zoom. Matched/uncertain points remain withheld even when related polygon layers are disabled.

Primary/review polygons use derived interior symbols below zoom 10 and original footprints at local zoom. Marker clicks resolve parent IDs/details. Symbols carry `counts_as_inventory=false`; KPIs/table use originals, and viewport queries canonicalize parent IDs across sources/layers/tiles.

Existing polygon overlaps and point-point identity remain unresolved; the 622 primary / 448 review records are not claimed as unique physical station totals. Power plants do not enter this matching comparison or these substation counts. See [coverage limitations](DATA_COVERAGE_AND_LIMITATIONS.md).
