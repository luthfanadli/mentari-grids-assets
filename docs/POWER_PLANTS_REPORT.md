# Power-plant context report — 4 November 2026

The user-authorized power-plant layer now appears in the map, Layers controls, legend, selected-record cards, list and source details. It is generation context alongside the transmission inventory; plants do not become transmission substations. No deployment, dependency, lockfile, hosting configuration or raw-source change was made.

## Source inspection and publication policy

The existing `data/raw/IDN.gpkg` contains **643 `power_plant` records**, all with valid, nonempty EPSG:4326 footprints and unique original IDs: **632 Polygon and 11 MultiPolygon**. All 643 are published, with **633 not construction-tagged** and **ten construction-tagged**. These flags do not certify operational status. This source layer has no voltage field, disused field or output-unit field.

| Source attribute | Missing records | Treatment |
| --- | ---: | --- |
| Name | 113 | Explicit fallback label with original ID |
| Operator | 428 | Unknown; no ownership inference |
| Energy source | 85 | Preserve the raw `source` tag where supplied |
| Method | 283 | Preserve supplied text |
| Output | 223 | Preserve 420 raw numeric values; unit remains null |
| Start date | 613 | Preserve 30 raw strings, including partial/approximate values |

Raw output is **not assumed to be MW**, converted, summed or presented as verified capacity. A raw start date is **not verified COD**. Repeated names or Wikidata references do not prove unique physical plants; no footprints are merged. Individual `power_generator_point` and `power_generator_polygon` layers remain excluded. No grid connections, voltage, official plant IDs, planned projects or power-system assignments were invented.

Preprocessing preserves original signed source IDs, source attributes used by the application and full coordinate precision. RFC 7946 ring orientation is normalized without rounding, simplifying, buffering or dissolving plant footprints. Tests compare every exported footprint with its oriented original at zero tolerance. The original GeoPackage remains unchanged.

The separate `scripts/expected-power-plant-audit.json` fixture records measured plant metrics. The historic `scripts/expected-audit.json` and transmission/substation predicates remain unchanged. Both audit comparisons return **zero differences**. Metadata now uses **schema 3**, pipeline **1.2.0**, data version `6ea22caaae9ef62a-pipeline-1.2.0`.

## Map, filtering and counting

- **Power plants** is a normal default-on checkbox. Default source flags show 633 plant footprints; enabling Tagged construction includes the other ten.
- Below zoom 10, red diamond symbols represent plants. At zoom 10 and above, original footprint fills and outlines replace them. Construction symbols are hollow; construction footprints use dashed boundaries.
- Each footprint has a Shapely interior `plant_representative_point`. Runtime marker features reuse the parent ID and carry `counts_as_inventory=false`; marker clicks resolve the original footprint/details.
- The plant card counts source footprints separately. Plants are not added to primary-substation counts, and derived symbols never add records. MultiPolygon parts remain one source record.
- Grid voltage filters apply to lines and substations. Plants have no source voltage and remain controlled by layer visibility, OSM status and search.
- The legend follows the current filtered selection and includes a separate Power plants group. Disabling the layer removes its key; construction keys appear only when relevant.
- Search includes plant name, English name, operator, ID, energy source and method. Details show source geometry and raw attributes with explicit unit/COD limitations.
- Basemap changes restore plant images, sources, layers and selection. Canvas-drawn icons require no new image, font or frontend dependency.

Viewport counts canonicalize parent IDs across symbols, footprint layers and tiled fragments, then intersect them with the active selection. Source-load events refresh counts; disabling symbol fading prevents stale symbols during rapid filter changes. Camera transitions and reduced-motion behavior remain available.

With default flags and optional candidates off, the selection is **5,599 original records**: 4,345 mapped line segments, 621 primary substation polygons and 633 plant footprints. Across all published flags/candidates, there are **6,119 original records**. The 1,070 substation representative symbols and 643 embedded plant display coordinates do not increase these totals. These are source-record counts, not certified unique physical assets.

## Exact outputs and preservation

| File in `public/data/` | Records / role | Bytes |
| --- | ---: | ---: |
| `transmission-lines.geojson` | 4,374 original mapped segments | 6,151,922 |
| `substations-primary.geojson` | 622 primary polygons | 646,266 |
| `substations-review.geojson` | 448 review polygons | 450,635 |
| `substations-point-candidates.geojson` | 32 optional source points | 36,376 |
| `substation-display-points.geojson` | 1,070 uncounted derived symbols | 490,830 |
| `power-plants.geojson` | 643 original plant footprints | 1,111,875 |
| `summary.json` | Counts, completeness, presentation | 5,017 |
| `data-catalog.json` | Provenance, policies, checksums | 10,799 |
| `qa-report.json` | Aggregate source/publication QA | 12,790 |

The six GeoJSONs total **8,887,904 bytes**; all nine publication files total **8,916,510 bytes**. Git attributes retain the existing deterministic byte/checksum behavior across Windows/Linux checkouts. The build guard validates all nine files without needing the raw GeoPackage.

All five pre-existing GeoJSONs are **byte-identical to `HEAD`**, including both optional-point and representative-symbol datasets. The original line/primary/review hashes remain:

| Export | SHA-256 |
| --- | --- |
| Lines | `1eed102bced3ca67d00660f764ee83eb608ba32239f5ba4e11ca06f6b3858c98` |
| Primary polygons | `930c23abd342797b27fd71435a3c7d32c5b838f06619206a7159df8bfaf6613f` |
| Review polygons | `e14432b41e7ce80def0f8edb3c5e0ac25b80ef6860129096cee071631522f038` |

The 30,412,800-byte source SHA-256 remains `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`. The 68-point/2,753-polygon substation matching remains **2 matched / 25 uncertain / 41 distinct candidates**, of which 32 are eligible. No station was promoted, merged or removed by adding plant context.

## Changed files

Preprocessing: modified `scripts/prepare_data.py`, `check_public_data.mjs` and `test_prepare_data.py`; added `expected-power-plant-audit.json` and `test_power_plants.py`. Added `public/data/power-plants.geojson` and updated the three metadata files. Existing five GeoJSONs regenerated identically.

Frontend: modified `src/types/assets.ts`, `src/utils/filterAssets.ts`, `src/utils/substationPresentation.ts`, `src/services/assetData.ts`, `src/composables/useAssetFilters.ts`, `src/style.css`, and components `MapCanvas.vue`, `FilterSidebar.vue`, `MapLegend.vue`, `InventorySummary.vue`, `AssetTable.vue`, `AssetDetailsDrawer.vue` and `DataProvenanceDialog.vue`. Extended `tests/unit/inventory.test.ts` and `tests/e2e/inventory.spec.ts`.

Updated README and all 17 other existing project Markdown documents. Current guides describe plant scope; historical reports retain their original measurements with a link to this extension. Added this report. No unused demo or new dependency was introduced.

## Commands and verification

The existing QGIS Python environment was reused with README's environment settings; no installation was needed.

```powershell
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p 'test_*.py' -v
pnpm.cmd check:data
pnpm.cmd test
pnpm.cmd typecheck
pnpm.cmd build
pnpm.cmd preview --host 127.0.0.1 --port 5175 --strictPort
$env:PLAYWRIGHT_CHANNEL='msedge'
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5175'
pnpm.cmd test:e2e
Get-FileHash -LiteralPath data/raw/IDN.gpkg -Algorithm SHA256
git diff --check
```

| Verification | Result |
| --- | --- |
| Source preprocessing and both expected/actual audits | PASS, zero differences |
| Full real-source Python suite | **19 passed**, no skips, 32.778 s |
| Node data/filter/presentation/repository suite | **16 passed** |
| Vue/TypeScript | PASS |
| Strict nine-file publication guard | PASS |
| Production build | PASS |
| Full local production browser suite, Microsoft Edge | **10 passed**, 54.3 s |
| All nine local production data URLs | HTTP 200; correct content types and byte-identical bodies |
| Original source and five prior GeoJSON fingerprints | Unchanged |
| Local links across all 19 project Markdown files | No broken links |
| Diff whitespace check | PASS |

The Python additions cover all 643 original geometries and source attributes, full precision, representative containment, signed IDs, missing-unit/voltage preservation and rejection of invalid output or inferred units. Existing deterministic publication, source audit and matching tests continue passing.

Browser coverage includes default 633 plants, toggle off/on, all 643 with construction enabled, voltage independence, search, marker clicks resolving original IDs, footprint transitions, source details, stable deduplicated counts, basemap reload and a plant-fetch 503/retry. Existing optional layers, source flags, responsive controls and errors remain covered. An initially discovered stale symbol-count race was corrected before the final passing suite.

Desktop overview/sidebar/details/local-footprint and mobile screenshots were captured and inspected under ignored `data/qa/power-*.png`. Real source plant `power_plant:-21724790` (Tarahan) demonstrates original MultiPolygon parts with one record. Manual browser inspection recorded no page errors and no horizontal overflow at 390 px. Plain-background captures isolate overlays from external raster availability; attributed basemap choices remain available.

Final local `dist/` size is **10,883,094 bytes**. Main JS is 119,944 bytes, CSS 94,417 bytes, MapLibre vendor 1,104,231 bytes and worker 518,989 bytes. The existing nonfatal vendor-size warning remains; its threshold was not increased. Private source/reference and QA files are not deployment assets. No deployment occurred.

## Remaining data and ToR gaps

This is an OSM-based footprint layer with unknown source vintage and unverified physical identity/operation. Output units, verified capacity/MW, COD, official plant/station identifiers, topology, generator-to-plant membership, plant-to-substation connections, official region/power-system attribution and planned RUPTL/RUKN infrastructure remain unavailable or unaudited. Existing transmission circuit-km, substation capacity and station-deduplication gaps remain. No missing value or planned feature was fabricated. OSM/ODbL attribution remains available; removing UI download links does not make static data private.
