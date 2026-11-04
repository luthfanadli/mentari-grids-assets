# Filters, legend and repository cleanup — 4 November 2026

Later user-authorized extension: [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md) documents 643 plant footprints, nine-file/schema-v3 publication and current tests. The stage-specific counts, hashes and UI descriptions below are preserved as history; the five earlier GeoJSONs and raw source remain unchanged.

The sidebar now contains simple controls without source totals, while the legend describes only original records matching the current filters. Confirmed unused starter files, obsolete CSS and an unused speculative type were removed. README and all 16 other existing project Markdown documents were refreshed; historical source findings, measurements and audit results were preserved with links to this current report. No data, preprocessing, dependencies, hosting configuration, commit, push or deployment changed.

## User-facing behavior

- **Filters:** Layers, Voltage and OSM status. Static source totals were removed from every checkbox; matching counts remain in the four cards and record list. The sidebar no longer needs summary metadata.
- **Candidates:** Review polygons and Point-only candidates share a compact optional group and short unvalidated/unknown-voltage hint. Both remain independently lazy, retryable and off by default. No point is promoted to primary inventory.
- **Voltage:** still applies to lines and substations. Unknown voltage appears when a candidate layer is enabled. Clearing it excludes all 32 source points and the 37 missing-voltage review polygons, subject to other active filters.
- **Legend:** derives from the same filtered original records as the cards/list, including search. Disabled or zero-match categories disappear. Empty selection shows **No matching records**. It describes selection, not the exact viewport.
- **Line colors:** only selected line voltages appear under **Transmission lines · kV**, ordered like the sidebar. All four voltage colors are unchanged.
- **Line pattern:** neutral solid/dashed/dotted samples explain OSM status without assigning a new voltage color. The section appears only when construction/disused lines match; it does not appear merely because a status checkbox is on.
- **Substations:** separate keys for ordinary primary, construction-tagged primary, review polygons and eligible source points. Polygon representatives use circles below zoom 10; local keys follow the footprint styling. A construction-tagged primary has an amber circle at overview or amber dashed outline at local zoom, instead of borrowing the construction-line key.

Names in cards and sidebar now consistently use **Primary substations** and **Review polygons**. Details and About retain source qualifications; OSM tags do not verify current operation. Layer/status/voltage predicates and representative counting are unchanged.

## Code and file cleanup

Modified frontend files:

- `src/App.vue`: removed the unused sidebar metadata binding.
- `src/components/FilterSidebar.vue`: simpler labels/grouping; removed total counters, metadata prop and unused formatter/type imports.
- `src/components/InventorySummary.vue`: consistent asset labels; live count computation is unchanged.
- `src/components/MapCanvas.vue`: passes the filtered original-feature array to the legend.
- `src/components/MapLegend.vue`: selection-driven groups, accurate pattern/category keys, empty state and bounded scrolling.
- `src/utils/substationPresentation.ts`: `selectedMapLegend` derives the key and ignores uncounted representative features.
- `src/types/assets.ts`: removed unused `FutureAuthoritativeAsset`; current publication/filter types remain.
- `src/style.css`: removed 27 obsolete rules, duplicate summary-grid declarations and an unused shadow token; added compact candidate-group styling.
- `tests/unit/inventory.test.ts`: real-data legend coverage for default/unknown-voltage/empty selections, source flags, construction-only polygons and ignored representatives.
- `tests/e2e/inventory.spec.ts`: updated labels and added the full legend/filter interaction scenario.

Reference searches confirmed these five files were confined to the unused starter component and were safe to remove:

| Removed file | Bytes |
| --- | ---: |
| `src/components/HelloWorld.vue` | 2,831 |
| `src/assets/hero.png` | 13,057 |
| `src/assets/vue.svg` | 496 |
| `src/assets/vite.svg` | 8,709 |
| `public/icons.svg` | 5,031 |
| **Total** | **30,124** |

Only the unused public sprite was previously copied to the build. The other demo assets were not part of the working app bundle. The source GeoPackage/license, analysis/preprocessing scripts, expected audit, matching QA, required data exports, live logo/favicon/font/license and historical reports were retained because they support current behavior or reproducibility.

## Documentation

Updated every existing project Markdown file: `AGENTS.md`, `CODEX_START_HERE.md`, `README.md`, and the 14 documents already under `docs/`. Current operating documentation describes the simple controls and selection-driven legend. The checklist now records the eight-file publication/current checks. Stale download-link and unused planned-type claims were corrected. Source/audit/history documents retain original evidence and explicitly distinguish historical stages from current UI. This report is the eighteenth project Markdown file. No third-party dependency documentation or font license text was rewritten.

## Verification

| Check | Result |
| --- | --- |
| `pnpm.cmd test` | **14 passed**, no skips |
| `pnpm.cmd typecheck` | **PASS** |
| `pnpm.cmd build` | **PASS**, strict data guard + Vue/TypeScript + Vite |
| Production-preview `pnpm.cmd test:e2e` | **8 passed**, 39.6 s, Edge |
| Desktop/mobile visual inspection | **PASS**, default/all-category legend and simpler sidebar; no document overflow at 390/320 px |
| All eight publication files vs `HEAD` Git blobs | **Byte-identical** |
| Raw source SHA-256 | **Unchanged** |
| Documentation local links and Markdown coverage | **PASS**, all 17 pre-existing Markdown files updated |
| `git diff --check` | **PASS** |

The browser suite was run against `pnpm.cmd preview --host 127.0.0.1 --port 5175 --strictPort`, with `PLAYWRIGHT_CHANNEL=msedge` and `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175`. It retains real MapLibre feature clicks, overview/footprint transitions, independent candidates/retries, missing voltage, search/details, baseline/status counts, basemap switching/attribution and mobile control bounds. The new scenario additionally checks removal of absent legend categories, unknown-voltage filtering, empty search, reset, source line patterns and construction-tagged station zoom behavior.

Publication validation checks all five GeoJSONs against catalog counts/hashes, schema and parent linkage. A separate byte comparison checked all eight files against committed Git blobs. `Get-FileHash -LiteralPath data/raw/IDN.gpkg -Algorithm SHA256` returned `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`. No Python/preprocessing code changed; the last 16-test source-dependent run remains documented in [the build-fix report](BUILD_FIX_GIT_LINE_ENDINGS.md), rather than being claimed as rerun here.

Internal screenshots: `data/qa/simple-sidebar-desktop.png`, `simple-sidebar-{390,320}.png`, `simple-legend-default.png`, `simple-legend-all.png` and `simple-legend-{390,320}.png`. Preview checks used plain background to isolate real inventory overlays from external raster availability. These QA artifacts are not public assets.

## Preserved data and output sizes

Publication remains 4,374 line segments, 622 primary polygons, 448 review polygons and 32 optional original points: **5,476 original inventory/review records** across all source flags. The **1,070 derived symbols** remain uncounted. Default selection is unchanged at **4,345 lines + 621 primary polygons**; both candidate layers remain off. Five GeoJSONs total **7,776,029 bytes** and all eight data files total **7,800,419 bytes**.

The final local `dist/` totals **9,760,026 bytes**. Main JS is 113,449 bytes, CSS 93,935 bytes, unchanged MapLibre vendor JS 1,104,231 bytes and worker 518,989 bytes. The existing nonfatal vendor-size warning remains; no threshold was raised. Package and lockfile are unchanged.

Remaining ToR/data gaps are unchanged: no authoritative planned RUPTL/RUKN infrastructure, official region/system membership, independently verified operation, COD, capacity/MVA, official circuit-km or AIS/GIS; physical station identity and source completeness remain uncertain. No values or infrastructure were fabricated. No deployment occurred.
