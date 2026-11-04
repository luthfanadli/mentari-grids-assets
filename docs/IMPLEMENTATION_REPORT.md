# Implementation report — 4 November 2026 (Asia/Jakarta)

Historical initial-MVP report. Current substation matching, eight-file publication, zoom-dependent symbols and point-only candidates are documented in [the enhancement report](SUBSTATION_ENHANCEMENT_REPORT.md). Initial counts/results below record that earlier implementation stage.

The existing Vue 3 + Vite + TypeScript project now implements the Deliverable 2 MVP using the actual supplied GeoPackage. Data inspection, preprocessing tests, preprocessing, count/geometry QA, UI implementation and browser/production checks were completed in that order. The original scaffold configuration and pnpm lockfile were reused; no new app was scaffolded.

## Inputs and preservation

- Read `AGENTS.md`, `CODEX_START_HERE.md`, `docs/DATA_FILTER_SPEC.md` and `docs/VERIFIED_DATA_AUDIT.md` before implementation.
- Read the actual `data/raw/License.pdf` using the installed Python PDF reader. No original ToR, `docs/references/` directory or restricted BNEF document was present.
- Inspected all 26 layer names/counts/CRS metadata and the three core spatial layers' actual fields, nulls, flags, geometry types, bounds, IDs and validity.
- Original input: 30,412,800 bytes; SHA-256 `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`. Preprocessing confirmed the file unchanged. Raw data, QA, virtual environments and secrets remain ignored.
- Existing user changes and supplied instruction/audit documents were preserved. The user's existing `.gitignore` raw-data exclusion was retained and extended.

## Changed files

Modified existing files:

- `.gitignore`: retain raw exclusion; add QA/intermediate/environment/secret/test-artifact exclusions.
- `package.json`, `pnpm-lock.yaml`: retain project and original dependencies; add MapLibre, GeoJSON types, Playwright and test/type/data-check scripts; guard the existing build.
- `index.html`, `public/favicon.svg`: inventory title, description and application icon.
- `src/App.vue`, `src/main.ts`, `src/style.css`: application composition, MapLibre CSS and responsive dashboard styling.
- `README.md`: actual setup, preprocessing, counts/bytes, tests, attribution and documentation links.

Added preprocessing and validation:

- `scripts/prepare_data.py`
- `scripts/requirements.txt`
- `scripts/expected-audit.json`
- `scripts/test_prepare_data.py`
- `scripts/check_public_data.mjs`

Added frontend modules:

- `src/components/AppHeader.vue`
- `src/components/FilterSidebar.vue`
- `src/components/InventorySummary.vue`
- `src/components/MapCanvas.vue`
- `src/components/AssetTable.vue`
- `src/components/AssetDetailsDrawer.vue`
- `src/components/DataProvenanceDialog.vue`
- `src/composables/useAssetFilters.ts`
- `src/services/assetData.ts`
- `src/types/assets.ts`
- `src/utils/filterAssets.ts`
- `src/utils/formatAssets.ts`

Added tests/configuration/documentation:

- `tests/unit/inventory.test.ts`, `tests/e2e/inventory.spec.ts`, `playwright.config.ts`
- `.env.example`, `.vercelignore`, `vercel.json`
- `docs/DATA_DICTIONARY.md`, `docs/DATA_COVERAGE_AND_LIMITATIONS.md`
- `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`
- `docs/IMPLEMENTATION_CHECKLIST.md`, this report

Added generated publication files listed below. Local ignored artifacts include `data/qa/qa-report.json`, `exclusion-report.json`, `substation-points.geojson`, `conflicting-status.geojson` and desktop/mobile/production screenshots. Existing starter assets are unused; no source/reference documents were copied into `public/`.

## Exact output

Data version: `6ea22caaae9ef62a-pipeline-1.0.0`.

| Publication file | Features | Bytes | Local gzip bytes |
| --- | ---: | ---: | ---: |
| `transmission-lines.geojson` | 4,374 | 6,151,922 | 1,233,763 |
| `substations-primary.geojson` | 622 | 646,266 | 79,411 |
| `substations-review.geojson` | 448 | 450,635 | 50,030 |
| `summary.json` | Metadata | 3,216 | 952 |
| `data-catalog.json` | Metadata | 4,756 | 2,052 |
| `qa-report.json` | Aggregate QA | 8,519 | 1,885 |

Three GeoJSONs: **5,444 features, 7,248,823 bytes**; about 1,363,204 bytes using local gzip. Six publication files: **7,265,314 bytes**. The built `dist/` contains 9,085,074 bytes including the app, bundled worker and starter static icons, with exactly these six data files and no GPKG/PDF/DOCX/environment file. These are disk measurements, not a claim about Vercel CDN transfer encoding.

## QA results

All historic audit metrics matched, with **zero expected/actual differences**. All core layers and all transformed published geometries are valid/nonempty; published IDs are globally unique; primary/review subsets are disjoint; no out-of-scope line or primary voltage is published. No conflicting flags are present.

- Lines: 4,345 not flagged, 25 tagged construction, four tagged disused. Defaults show 4,345.
- Primary polygons: 621 not flagged and one tagged construction. Defaults show 621.
- Review: 37 transmission/missing-voltage + 239 target-voltage/missing-type + 172 target-voltage/distribution = 448, all off initially.
- Excluded lines: 458 at 20 kV + 522 missing voltage + 42 other voltage = 1,022. Two excluded lines are disused-tagged.
- Excluded polygons: 19 target-voltage/other-type + 32 transmission/non-target voltage + 1,632 other excluded = 1,683.
- All 68 points stay in internal QA. Other source layers are counted/excluded without spatial export.
- One slash-delimited raw polygon voltage string is flagged as unparseable and remains excluded by the approved numeric/type rules. No source value was repaired by inference; see coverage documentation.

Byte-for-byte deterministic outputs were verified by processing the real source into two temporary directories and comparing all six files. A simulated source-fingerprint mismatch verified that exact expected/actual differences are reported and publication remains unwritten. The historical audit file was not adjusted to mask discrepancies.

## Commands executed and results

The Windows default Python alias was unavailable. The installed QGIS 3.44.15 Python 3.12.15 already provided the pinned GeoPandas 1.1.4, Pyogrio 0.13.0, Shapely 2.1.2 and PyProj 3.8.0, so no Python installation was needed. Environment setup is recorded in the README.

```powershell
# Dependency additions, using the existing package manager:
pnpm.cmd add maplibre-gl
pnpm.cmd add -D @types/geojson @playwright/test

# Source inspection used read-only SQLite, GeoPandas/Pyogrio and SHA-256.
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py --input data/raw/IDN.gpkg --output public/data --qa-output data/qa
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p test_prepare_data.py -v
pnpm.cmd test
pnpm.cmd check:data
pnpm.cmd typecheck
pnpm.cmd build

# Development browser checks:
pnpm.cmd dev --host 127.0.0.1
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e

# Production browser checks:
pnpm.cmd preview --host 127.0.0.1 --port 5175
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5175'
pnpm.cmd test:e2e

# Final review:
git diff --check
git check-ignore data/raw/IDN.gpkg data/raw/License.pdf data/qa/substation-points.geojson .venv/example .env.local
Get-FileHash -LiteralPath data/raw/IDN.gpkg -Algorithm SHA256
```

| Check | Result |
| --- | --- |
| Python classifications, real-source export/audit, determinism and mismatch guard | **7 passed**, no skips in final run |
| Node tests using actual exports, filters/search/unknowns/counts/caching/retry | **8 passed** |
| Build-time publication guard | **PASS**, 5,444 features, six files, matching checksums/counts/versions |
| Vue/TypeScript checking | **PASS** |
| Vite production build | **PASS** |
| Development browser scenarios | **3 passed**, final run 10.2 s |
| Production browser scenarios | **3 passed**, 10.1 s |
| Network-enabled production visual check | **15 successful real OSM tiles, zero failed requests** at capture |
| All six production-preview data URLs | **HTTP 200**, correct JSON/GeoJSON content types and byte-for-byte matches to publication files |
| Final independent source SHA-256 | **Unchanged**, matches the original fingerprint above |
| Diff whitespace check | **PASS**; Git only reports normal Windows LF/CRLF conversion notices |

The three browser scenarios cover actual nonzero MapLibre feature rendering, sidebar bounds, defaults, source flags, lazy/cached review loading, numeric voltage filters, negative-ID search, source details, list and map-footprint clicks, reset/empty state, About/download links, missing-file retry, basemap failure/plain background and a 390-pixel mobile viewport without document overflow. Desktop/mobile screenshots were visually inspected.

Browser QA identified and fixed the MapLibre 6 Vite worker path, viewport counts waiting on external raster requests, and the first filter-row layout around native legends. The successful production build bundles the worker explicitly, following MapLibre's current Vite guidance.

Vite retains a nonfatal size warning for the lazy MapLibre chunk: **1,104.23 kB, 298.14 kB gzip**. The worker is **518.98 kB**; main JS is **99.94 kB, 37.28 kB gzip**; CSS is **90.56 kB, 15.17 kB gzip**. No backend/tileset infrastructure was introduced, and the warning threshold was not raised.

## Deployment and remaining scope

`vercel.json` configures a frozen pnpm install, guarded Vite build, `dist/` output and revalidating data headers. `.vercelignore` excludes root raw/internal data while retaining `public/data/`. Vercel setup and preview verification are documented. **No hosted Vercel deployment or production promotion occurred**; account/domain/CDN behavior remains to be verified after import.

The implementation fulfills the supplied-source MVP, not every substantive ToR requirement. Remaining gaps are authoritative existing-asset validation; planned RUPTL/RUKN lines/substations; official region/power-system assignments; verified HVDC/converter stations; COD, capacity/MVA, thermal ratings, official circuit-km and AIS/GIS; point/polygon deduplication and topology; unknown source vintage; and review-candidate validation. No such values or projects were fabricated. The original ToR's absence is documented. Source attribution and ODbL derivative access/notices are included in the UI, exports and documentation.
