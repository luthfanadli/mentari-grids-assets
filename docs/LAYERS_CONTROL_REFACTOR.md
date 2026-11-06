# Unified Layers control — 6 November 2026

The dashboard now has one **Layers** control inside the map instead of a sidebar, external Filters toggle and separate legend. The map always uses the full content width; its compact responsive height, search, five KPI cards, table and floating asset details are retained. No data, preprocessing, dependency, package/lockfile or hosting change was made, and no deployment occurred.

## Persistent map interaction and fluid width follow-up

The initial panel's document-level outside handler also treated the map canvas as outside, so dragging or focusing the map dismissed Layers. `MapLayersControl.vue` now uses the containing map card as the interaction boundary, with matching pointer/focus rules and cleaned-up document listeners. Pan, wheel zoom, native zoom buttons and extent actions leave Layers open. Escape remains available after focus moves to the map; explicit basemap-menu opening and activity outside the map still dismiss it. Filter values never change merely because the panel closes.

`src/style.css` removes the fixed 1360 px content cap. Small adaptive gutters let the five cards, search, map and table expand together at normal browser zoom. At viewport widths 1366/1440/1920/2560, the measured map-frame widths are approximately 1332/1404/1872/2496 px. Mobile retains 12 px gutters. Map heights and compact card typography are retained.

The current production Edge suite (`pnpm.cmd test:e2e`) passes **11 tests, approximately 1.8 minutes**. It includes a real mouse drag, wheel zoom, zoom-button click, subsequent layer off/on without reopening the panel, Escape from a map control, and aligned content/no overflow at 1366, 1440, 1920, 2560, 390 and 320 px. Additional real touch emulation confirmed map panning followed by a layer toggle with Layers still open. A 1920 px screenshot was visually inspected under ignored `data/qa/layers-pinned-fluid-laptop.png`. `pnpm.cmd build` passes with Vue/TypeScript and the unchanged publication guard. These results supersede the original ten-case browser result below. No source-data or deployment change occurred.

## Interaction and visual design

- Layers starts closed on desktop and mobile. The stack icon opens a bounded floating panel at the map's upper left. Its fixed header provides Reset and Close; the body scrolls inside the map without covering the bottom attribution.
- All five layer choices remain available when disabled, when their filters produce no matches and when the whole selection is empty. The empty-state hint does not remove controls. Layer opening/closing changes no filter value.
- Transmission lines, primary substations and power plants start enabled. Review polygons and point-only candidates remain off and independently lazy. Their loading/error/retry messages appear beside the corresponding controls.
- Voltage and OSM status are folded initially. Voltage colors explain line colors; source-status samples show solid/dashed/dotted line patterns. Power plants retain voltage independence, and candidate unknown voltage remains explicit.
- Primary/review/plant symbols match overview versus local-footprint presentation. Matching construction-tagged substations retain amber overview symbols and green footprints with amber outlines; plant construction symbols remain distinct. Contextual swatches use filtered original records, while layer choices remain persistent.
- Whole-row text, symbol and padding clicks/taps work without closing the panel, allowing several changes. Pointer focus stays inside the panel before native label activation; this avoids the outer focusable main element closing the panel prematurely. Native checkbox keyboard behavior is retained.
- Panning, wheel zoom, native zoom buttons and extent actions keep the panel open. Layers, Close, Escape, or pointer/focus moving outside the map dismiss it. Opening the basemap picker also closes Layers so the two menus do not overlap on small screens. Explicit dismissal restores focus to Layers, including Escape after interacting with the canvas. Native disclosure controls support keyboard access to advanced filters. Reset retains the previous behavior: restore defaults and clear search.
- The basemap button now uses a folded-map icon to distinguish it from Layers. Basemap choices, camera, filtering, selection, cached datasets and layer-panel state remain independent of MapLibre style reloads.

The sidebar space is reclaimed and the former 1360 px dashboard cap is removed. The map frame measures approximately **1404 px at a 1440 px viewport**, **1872 px at 1920 px**, and **2496 px at 2560 px**. Cards, search and table span the same width with 16-32 px desktop gutters. Desktop panel width is 288 px; it adapts to 274 px within the 320 px viewport. Default panel heights measured about 365 px on desktop and 375 px on mobile, contained within the map. Source totals are not repeated in controls.

## State and cleanup

App keeps the existing `useAssetFilters` model, candidate-loading watchers and selection/count calculations. A named `layers` slot in MapCanvas supplies the overview/local state to MapLayersControl. No duplicate filter model was introduced. The existing `selectedMapLegend` helper remains a contextual style resolver; it does not determine whether a layer choice is available. Representative features still resolve to original parent IDs and never inflate counts.

Added `src/components/MapLayersControl.vue`. Modified `src/App.vue`, `src/components/MapCanvas.vue`, `src/components/MapBasemapPicker.vue` and `src/style.css`. Removed `src/components/FilterSidebar.vue` and `src/components/MapLegend.vue`, plus their obsolete sidebar grid, toggle, candidate-row and standalone-legend CSS. Removed the obsolete docked-details class binding. The search field now spans the content row.

Updated `tests/e2e/inventory.spec.ts` for the new interaction. README, AGENTS, development guide, architecture, filter specification UI note, dictionary, coverage/limitations, deployment smoke checks and implementation checklist describe the current control. Earlier UI/simplification reports retain their historical evidence with a link here.

## Data preservation

All **nine `public/data/` files are byte-identical to HEAD**, directly compared using Git's stored bytes: **8,916,510 bytes** total, including **8,887,904 GeoJSON bytes**. Schema 3 / pipeline 1.2.0 is unchanged. No raw-source write or regeneration was performed.

| Original source-record subset | All published flags | Default selection |
| --- | ---: | ---: |
| Transmission line segments | 4,374 | 4,345 |
| Primary substation polygons | 622 | 621 |
| Review polygons | 448 | 0 |
| Point-only candidates | 32 | 0 |
| Power-plant footprints | 643 | 633 |
| **Original records** | **6,119** | **5,599** |

The 1,070 substation representative symbols and 643 embedded plant display locations remain uncounted presentations. Matching outcomes (2 matched / 25 uncertain / 41 distinct, 32 eligible) and unknown source voltages/output units remain unchanged. No point enters primary inventory, no feature is invented, and no station identity or operational status is certified. OSM/ODbL and basemap attribution remain visible.

## Verification

Commands executed locally:

```powershell
pnpm.cmd typecheck
pnpm.cmd test
pnpm.cmd build
pnpm.cmd preview --host 127.0.0.1 --port 5175 --strictPort
$env:PLAYWRIGHT_CHANNEL='msedge'
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5175'
pnpm.cmd test:e2e
pnpm.cmd exec playwright test --grep 'Layers combines'
git diff --check
```

| Check | Result |
| --- | --- |
| Node data/filter/presentation/repository tests, preceding Layers refactor | **16 passed**; unchanged logic in this follow-up |
| TypeScript/Vue and production build | PASS |
| Strict publication count/hash/version guard | PASS |
| Current full production-preview Edge browser suite | **11 passed**, approximately 1.8 minutes |
| Earlier focused construction-swatch regression | **1 passed**, 16.6 s; also covered in the current full suite |
| Real touch text/padding selection and internal swipe scrolling | PASS |
| Escape focus restoration and mobile document overflow | PASS; no overflow |
| All nine publication files compared to HEAD | Byte-identical |
| Local links across 20 project Markdown files | PASS |
| Diff whitespace check | PASS |

Browser scenarios retain actual MapLibre rendering, polygon/plant representative clicks and footprint transitions, stable source counts, independent/lazy/cached point candidates, unknown-voltage filtering, 503 retries, source flags, search/reset/details, basemap switching and attribution. New checks verify full map width, closed-by-default Layers, folded groups, persistent off/empty choices, native text-row activation, keyboard opening/closing, construction styles and recovery from all layers being off. The original label-focus failure was fixed before the passing full suite.

Additional Edge touch emulation at 390 px verified tapping label text, tapping row padding, swiping the expanded panel body and Escape focus restoration. Default panel containment/no-overflow was measured at 1440, 768, 390 and 320 px. Desktop and mobile captures were visually inspected under ignored `data/qa/layers-*.png`. QA captures are not public assets. Preprocessing tests were not rerun because source data and pipeline code did not change.

The existing nonfatal MapLibre vendor-size warning remains; its threshold was not raised. The application still bundles the MapLibre worker, uses no new service/backend and requires no new dependency.

Final local `dist/` totals **10,884,671 bytes**. Main JS is **121,051 bytes**, CSS **94,887 bytes**, MapLibre vendor **1,104,231 bytes** and worker **518,989 bytes**. Internal QA, raw source and reference files are not deployment assets.

## Remaining scope gaps

Source vintage, verified operational status, authoritative RUPTL/RUKN planned projects, official region/power-system assignments, verified COD/capacity/output units, circuit-km, topology and physical-asset deduplication remain unresolved as documented in the [coverage and limitations](DATA_COVERAGE_AND_LIMITATIONS.md). This UI refactor does not change the source dataset's coverage or certainty.
