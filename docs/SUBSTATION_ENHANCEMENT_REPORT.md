# Substation enhancement report — 4 November 2026

Subsequent dashboard-only layout, legend, extent-control and basemap updates are recorded in [DASHBOARD_UX_UPDATE.md](DASHBOARD_UX_UPDATE.md). The matching outputs, source counts and preservation proof in this report remain unchanged.

The existing WebGIS now audits source point/polygon associations reproducibly, exposes a separate optional point-only candidate layer, and switches polygon substations between overview symbols and original footprints. Transmission-line filtering and the original primary/review polygon inventories are preserved. No deployment, hosting configuration change, package/lockfile update or new dependency was made for this enhancement. Existing header/intro presentation edits were retained.

## Matching and eligibility result

The preprocessing pipeline evaluates **all 68 source points against all 2,753 raw polygons**, including polygons outside the published subsets: **187,204 pair evaluations**. Evidence includes exact intersection, metric proximity, signed original IDs, distinctive names, meaningful references, operators, known maximum voltages, source role and construction flag. OSM element kind is unknown, so equal numeric IDs alone do not establish identity.

| Classification | Points | Decision |
| --- | ---: | --- |
| matched | 2 | Supported source correspondences; withheld from point layer |
| uncertain | 25 | Withheld pending identity review |
| distinct_point_only_candidate | 41 | 32 eligible for optional layer; nine held for role/function review |
| Total | 68 | Every original point retained in QA |

The two supported associations are Sandai and Bukit Kemuning, using distinctive name and geographic evidence. They are **not certified physical duplicates**. Intersection alone is insufficient: the unnamed Toili/Bogor records and generic PLN point remain uncertain. Matching does not transfer a polygon's voltage or role to a point.

The nine distinct-but-held records comprise five distribution, two minor distribution, one generation and one office-name clue. The 32 eligible records all retain missing numeric voltage; no point enters primary inventory. Distinct means no plausible polygon correspondence under this policy, not a verified unique transmission station. Full policy and limitations: [SUBSTATION_MATCHING.md](SUBSTATION_MATCHING.md).

Name normalization retains code numbers: PK 274/PK 277 do not become an identical generic PK name. This avoids the overly broad association that would otherwise change the screening split to 2/27/39; the final documented policy produces **2/25/41**. Historic source counts and `scripts/expected-audit.json` were not changed.

## Geometry and counting

- **Zoom below 10:** selected polygon records use interior representative symbols derived from the unchanged published footprints.
- **Zoom 10 and above:** original polygon fills/outlines replace those symbols. Source geometries are not buffered, dissolved or replaced by a marker.
- Eligible point-only records retain **exact original point coordinates**, use separate pink outlined symbols at both scales, and load only after their default-off toggle is enabled.
- Primary/review filters and search determine the parent symbol set. Selecting a symbol resolves to its original polygon ID/details/footprint.
- Representative symbols carry `counts_as_inventory=false` and reuse the parent ID. KPIs/table count original records only; viewport counts canonicalize parent IDs across sources/layers/tiles. Matched/uncertain source points never enter the visible point layer, even if their polygon layer is disabled.
- The original 622 primary and 448 review polygons remain separate record counts. Prior polygon–polygon overlap cases are not silently merged or claimed as unique physical stations.

At the reviewed national overview with both candidate layers enabled and only default source status, the map rendered **1,069 polygon symbols** (621 baseline primary + 448 review) and **32 source-point candidate locations**. The selected-record total was **5,446** (4,345 lines + 621 primary + 448 review + 32 points). The one construction-tagged primary is still off under default flags. Overview/local transitions keep selected-record counts unchanged.

## Exact publication outputs

Data version: `6ea22caaae9ef62a-pipeline-1.1.0`; metadata schema v2; matching policy v1.0.0.

| File in `public/data/` | Records / role | Bytes |
| --- | ---: | ---: |
| `transmission-lines.geojson` | 4,374 original mapped segments | 6,151,922 |
| `substations-primary.geojson` | 622 original primary polygons | 646,266 |
| `substations-review.geojson` | 448 original review polygons | 450,635 |
| `substations-point-candidates.geojson` | 32 optional unvalidated original points | 36,376 |
| `substation-display-points.geojson` | 1,070 derived, **uncounted** symbols | 490,830 |
| `summary.json` | Counts/completeness/matching/presentation | 4,267 |
| `data-catalog.json` | Provenance/policy/field meanings/checksums/roles | 8,860 |
| `qa-report.json` | Aggregate source/publication/matching QA | 11,263 |

Five GeoJSONs total **7,776,029 bytes**. Eight publication files total **7,800,419 bytes**. There are **5,476 original inventory/review records** across all flags; the 1,070 derived symbols are not added to this count. Final local `dist/` size is **9,629,689 bytes**, including app/vendor/worker/static assets. No GPKG, PDF, DOCX or environment file occurs in the build.

Internal outputs under ignored root `data/qa/`:

- `substation-matching-report.json`: **191,697 bytes**, one evidence-rich row for each of 68 source points; all raw point attributes/geometry and every decision/hold retained. All pairs are evaluated; relevant associations and nearest/contextual evidence are retained rather than exporting 187,204 irrelevant full rows.
- `substation-matching-report.csv`: **14,947 bytes**, 68 review rows plus header, UTF-8 BOM for spreadsheet readability.
- `substation-enhancement-baseline.json`: original three GeoJSON fingerprints recorded before modifications.
- Desktop overview, local footprint and mobile screenshots; no screenshots or internal matching tables are public assets.

## Preservation proof

The original raw GeoPackage remains 30,412,800 bytes with SHA-256:
`6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`.

The following original exports remain byte-identical, verified against the pre-change baseline and in programmatic tests:

| Export | SHA-256 |
| --- | --- |
| Lines | `1eed102bced3ca67d00660f764ee83eb608ba32239f5ba4e11ca06f6b3858c98` |
| Primary polygons | `930c23abd342797b27fd71435a3c7d32c5b838f06619206a7159df8bfaf6613f` |
| Review polygons | `e14432b41e7ce80def0f8edb3c5e0ac25b80ef6860129096cee071631522f038` |

All historic audit metrics still match with **zero expected/actual differences**. The new classification fixture records matching outcomes separately from raw-source audit expectations. Original line predicates, voltage scope, flag categorization, primary selection and three polygon-review predicates are unchanged.

## Files changed for this enhancement

Preprocessing and validation:

- Modified `scripts/prepare_data.py`: integrate matching; export eligible source points and derived symbols; schema-v2 metadata/provenance; preserve original outputs; reject point geometry from polygon inventory.
- Added `scripts/substation_matching.py`: all-pair matching, evidence, classifications, eligibility, deterministic matching CSV and representative points.
- Modified `scripts/check_public_data.mjs`: eight-file checksums/counts/schema checks; separate original and presentation ID scopes; parent linkage, candidate classifications and geometry-family guards.
- Modified `scripts/test_prepare_data.py`; added `scripts/test_substation_matching.py`.

Frontend:

- `src/components/MapCanvas.vue`: representative/footprint zoom transition, original point layer, source/parent selection, deduplicated viewport counts and map legend.
- `src/components/FilterSidebar.vue`, `InventorySummary.vue`: independently lazy/default-off point controls, loading/retry, explicit unknown voltage and separate counts.
- `src/components/AssetDetailsDrawer.vue`, `AssetTable.vue`, `DataProvenanceDialog.vue`: original geometry, candidate identity/voltage uncertainty, matching context and complete download/provenance links.
- `src/App.vue`, `src/composables/useAssetFilters.ts`, `src/services/assetData.ts`: source loading/validation, point-layer state, parent-filtered symbols and selection.
- `src/types/assets.ts`, `src/utils/filterAssets.ts`, `src/utils/formatAssets.ts`; added `src/utils/substationPresentation.ts` for canonical parent filtering/counting.
- `src/style.css`: five-metric layout and separate candidate/symbol styling with responsive mobile layout.
- `tests/unit/inventory.test.ts`, `tests/e2e/inventory.spec.ts`: new layer, matching exclusions, count/zoom invariants, symbol clicks, retry and mobile coverage.

Generated data/documentation:

- Added two publication GeoJSONs and updated the three metadata files; the original three GeoJSONs were regenerated identically.
- Updated `README.md`, `docs/DATA_DICTIONARY.md`, `DATA_COVERAGE_AND_LIMITATIONS.md`, `ARCHITECTURE.md`, and `DEPLOYMENT.md`.
- Added `docs/SUBSTATION_MATCHING.md` and this report; appended a user-authorized supplement to `DATA_FILTER_SPEC.md`.
- Marked `SUBSTATION_POINT_POLYGON_ANALYSIS.md` and the initial `IMPLEMENTATION_REPORT.md` as historical stages, retaining their source findings/results.

No dependency/package-manager change, raw source edit, source-audit rewrite, new backend, storage service, or hosting mutation was made. Existing user changes were preserved.

## Commands and verification

The installed QGIS Python environment was reused with the environment variables documented in README. No pip/dependency installation was needed.

```powershell
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p 'test_*.py' -v
pnpm.cmd check:data
pnpm.cmd test
pnpm.cmd typecheck
pnpm.cmd build

pnpm.cmd dev --host 127.0.0.1
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e

pnpm.cmd preview --host 127.0.0.1 --port 5175
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5175'
pnpm.cmd test:e2e

Get-FileHash -LiteralPath data/raw/IDN.gpkg -Algorithm SHA256
Get-FileHash -LiteralPath public/data/transmission-lines.geojson,public/data/substations-primary.geojson,public/data/substations-review.geojson -Algorithm SHA256
git diff --check
```

| Check | Result |
| --- | --- |
| All real-source Python tests | **15 passed**, final full run 39.457 s, no skips |
| Node data/filter/presentation/repository tests | **10 passed** |
| Vue/TypeScript check | **PASS** |
| Publication guard | **PASS**, 5,476 original records + 1,070 uncounted symbols, eight files |
| Production build | **PASS** |
| Development browser suite | **5 passed**, 24.2 s |
| Local production browser suite | **5 passed**, 24.7 s, including latest mobile point controls |
| Eight local production data URLs | **HTTP 200**, JSON/GeoJSON content types and byte-identical responses |
| Source and baseline export fingerprints | **Unchanged** |
| Diff whitespace check | **PASS**, with normal Windows LF/CRLF notices only |

Python tests include exhaustive pair accounting, intersection-only uncertainty, meaningful names/references, preserved numeric site codes, signed-ID uncertainty, attribute/status conflicts, ambiguity and distance thresholds, scope holds, point promotion rejection, exact raw point coordinates, interior markers for concave/real footprints, source audit, deterministic eight-file publication and full matching reports, and unchanged line/polygon exports.

Browser tests verify nonzero real MapLibre rendering; representative clicks resolve original negative-ID polygon records; footprint transition at local zoom; stable selected and deduplicated viewport counts; default/lazy/cached point loading, 503 retry, independent visibility, unknown-voltage controls and withholding matched points; existing line flags/polygon-review/search/details; basemap fallback; and mobile controls without document overflow. Screenshots were inspected; overview capture intentionally used the plain-background fallback to isolate the real inventory overlays from external raster availability. The existing attributed OSM basemap configuration remains unchanged.

The final production bundle retains the existing nonfatal MapLibre vendor-size warning: approximately **1,104.23 kB / 298.14 kB gzip**. Main JS is **108.92 kB / 39.41 kB gzip**, CSS **91.09 kB / 15.29 kB gzip**, worker **518.98 kB**. The warning limit was not raised.

## Remaining ToR/data gaps

Point/polygon correspondence is a conservative source QA classification, not authoritative station deduplication. Unknown point voltages and functions, point-point physical identity, source polygon overlaps, source vintage, operational validation, official station IDs, COD, capacity/MVA, circuit-km, AIS/GIS, verified HVDC/converter stations, planned RUPTL/RUKN infrastructure and official region/power-system assignments remain unresolved. No values or spatial projects were fabricated. The original ToR was not supplied; the source license was already reviewed. OSM/ODbL attribution and derivative downloads remain available. No deployment occurred.
