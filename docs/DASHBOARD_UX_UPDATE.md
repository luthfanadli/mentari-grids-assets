# Dashboard UI update — 4 November 2026

6 November 2026 follow-up: Layers now remains open during map panning, wheel zoom and navigation controls. The dashboard also fills the viewport with small responsive gutters instead of a 1360 px content cap; cards, search, map and table expand together. Build and the **11-case** production-browser suite passed. Current behavior, responsive measurements, touch verification and the map-boundary dismissal policy are recorded in [LAYERS_CONTROL_REFACTOR.md](LAYERS_CONTROL_REFACTOR.md). Earlier sizing/dismissal behavior below is historical. Data, output counts/sizes and remaining ToR gaps are unchanged; no deployment occurred.

Latest UI refactor (6 November 2026): [LAYERS_CONTROL_REFACTOR.md](LAYERS_CONTROL_REFACTOR.md) replaces the sidebar, external Filters toggle and standalone legend with one default-closed Layers panel inside the full-width map. Earlier layouts, screenshots and measurements below are retained as history.

## Compact summary cards and grouped filter control — 6 November 2026

The five statistic cards are shorter: desktop padding is 12 by 14 px, internal gaps 5 px and values 28 px; wide-screen padding is 14 by 16 px. Mobile padding is 10 px, gaps 4 px, values 25 px and minimum card height 108 px instead of 133 px. Descriptions, values, icons and candidate distinctions remain available. Card-grid gaps and the space below cards are smaller. The desktop header-to-title gap is now 18 px instead of 34 px, the title-to-cards margin 12 px instead of 22 px, and mobile top padding is 16 px instead of 26 px.

Moved Filters before the search field in `src/App.vue` and removed its auto left margin. It now sits on the left next to search, with 10 px desktop / 9 px mobile spacing. DOM order matches the visual/keyboard order. Sidebar toggling, expanded state, active filters and selected counts retain their behavior.

Changed `src/App.vue`, `src/style.css`, the existing toolbar browser assertion, README, architecture notes and this report. `pnpm.cmd build` passed, including TypeScript and strict nine-file data checks. Production-preview Edge `pnpm.cmd exec playwright test --grep 'MENTARI logo|real map, flags|mobile filters'` passed **3 tests in 24.4 s**, covering toolbar adjacency, sidebar toggling, live counts, filter/search/details and mobile controls. Screenshots at 1440, 390 and 320 px were inspected with no horizontal overflow; the first card measured approximately 102, 108 and 114 px high respectively. Internal captures are `data/qa/compact-cards-toolbar-{1440,390,320}.png`.

No dataset, map dimensions, preprocessing, dependency or hosting change was made. Source counts, provenance and remaining ToR gaps are unchanged: nine publication files / 8,916,510 bytes, 6,119 original records and 1,070 uncounted substation symbols. No deployment occurred.

## Compact sidebar spacing — 5 November 2026

Reduced checkbox-row minimum height from 36 to 28 px on desktop and from 39 to 34 px on mobile. Sidebar section padding is now 12 px vertically, section-title gaps are 8 px, and outer padding, candidate-group gaps and helper-note spacing are tighter. Sidebar typography and all source controls remain available; map dimensions are unchanged. Scoped section/note rules avoid affecting popup text or the basemap picker.

Changed `src/style.css`, README, architecture notes and this report. `pnpm.cmd build` passed with TypeScript and strict publication checks. Production-preview Edge `pnpm.cmd exec playwright test --grep 'real map, flags|mobile filters'` passed **2 tests in 16.9 s**, covering desktop filter hit areas, flags/candidates/reset/search and mobile controls. Screenshot inspection confirmed a compact readable list; the default desktop sidebar measured about 629 px high, with no mobile document overflow. Internal captures are `data/qa/sidebar-compact-desktop.png` and `sidebar-compact-mobile.png`. Data, output sizes/counts and ToR gaps remain unchanged (nine files / 8,916,510 bytes; 6,119 original records and 1,070 uncounted symbols). No deployment occurred.

## Smaller map dimensions — 5 November 2026

Reduced both map dimensions after the enlarged version. `src/style.css` now centers the dashboard within a 1360 px maximum width, with 24 px desktop / 16 px tablet / 12 px mobile side padding. Map height is `clamp(520px,66vh,720px)` on desktop, `clamp(500px,64vh,680px)` on tablet and `clamp(480px,62svh,620px)` on mobile. The floating popup, scrollable attributes, camera clearance, single-line attribution, close buttons and collapsible filters are retained.

At a 1440 by 844 viewport, the default map is approximately **1060 by 557 px**, reduced from 1164 by 720 px. At 390 by 844, it is approximately **364 by 523 px**, reduced from 372 by 692 px. Measurements at 1920, 1440, 768, 390 and 320 px confirmed popup containment and no document overflow. Desktop/mobile screenshots (`data/qa/map-compact-1440.png` and `map-compact-390.png`) were visually inspected using the real PLTU Pacitan footprint and a plain background.

Changed for this adjustment: `src/style.css`, existing size assertions in `tests/e2e/inventory.spec.ts`, README, architecture notes and this report. `pnpm.cmd build` passed, including TypeScript and publication validation. The full local production Edge suite (`pnpm.cmd test:e2e`) passed **10 tests in 43.9 s**, including popup positioning, the selected polygon remaining visible above the mobile card, scrolling, feature selection, filters, counts and basemap controls. Data and existing source/ToR limitations are unchanged: nine publication files / 8,916,510 bytes, 6,119 original records and 1,070 uncounted substation symbols. No deployment occurred.

## Floating map popup — 5 November 2026

The current asset details are a floating card over the map, replacing the attached panel iteration below. The full canvas retains its width and height when a feature is selected. The card has inset margins, rounded corners and a shadow; on wide maps it sits below the toolbar and left of the zoom controls, while narrow maps place it above the bottom copyright strip. Its fixed header/close button and scrollable attributes remain accessible. The map camera measures the actual card bounds and fits the selected original geometry into the unobscured space. Closing the card recenters the feature.

Design reference examined: [Mapbox's clicked-feature popup example](https://docs.mapbox.com/mapbox-gl-js/example/popup-on-click/). The application adapts the in-map information pattern to its existing Vue slot and MapLibre implementation, with no Mapbox dependency. The repeated footer note has been removed entirely, including its unused CSS; the popup ends after its attributes. This final text-only follow-up passed `pnpm.cmd build` and `git diff --check`; the browser assertion now checks that the note is absent. The full browser-suite result below precedes this follow-up. Source attributes, badges, raw output-unit/date cautions and detailed metadata/About notices remain available.

Changed for this refinement: `src/components/AssetDetailsDrawer.vue`, `src/components/MapCanvas.vue`, `src/style.css`, `tests/e2e/inventory.spec.ts`, README, architecture notes and this report. Resize handling now tracks the container dimensions independently of MapLibre's own window listener so responsive camera fitting is not skipped after a native window resize. Larger map dimensions and collapsible filters are retained.

Verification: `pnpm.cmd build` passed with TypeScript and strict publication checks. Local production-preview Edge `pnpm.cmd test:e2e` passed **10 tests in 55.0 s**. Assertions cover floating-card containment, a full-height mobile canvas, keyboard attribute scrolling and the selected polygon's projected interior point remaining above the card at both 390 and 320 px. Previous selection, close/reopen, source-flag/filter/count, basemap and retry coverage remains passing. Screenshots of PLTU Pacitan at 1440, 768, 390 and 320 px were inspected with no document overflow; ignored QA images are `data/qa/map-popup-floating-final-*.png` and `map-popup-short-note.png`. A plain background isolates the real source footprint from external tiles.

No dataset, source geometry, provenance, inventory count, package, lockfile or hosting change occurred. Publication remains nine files / **8,916,510 bytes**, with **6,119 original records** and **1,070 uncounted substation symbols**. Remaining ToR gaps are unchanged; no deployment occurred.

## Earlier attached-panel iteration — 5 November 2026

Asset attributes are now part of the map frame rather than a fixed panel floating over the page. App selection supplies `AssetDetailsDrawer.vue` through a named `MapCanvas.vue` slot. Wide maps use an attached 340 px right column; a container query at 760 px map width moves the panel below the canvas. The canvas and details share one border/boundary and do not cover each other or the table. Closing details restores the space to the canvas. The ASSET DETAILS header and centered close button stay visible while a separate, keyboard-focusable attributes region scrolls. Changing records resets that region to the top. Source attributes, uncertainty notices and provenance remain unchanged.

The map frame height increases from desktop `clamp(600px,72vh,900px)` to `clamp(720px,84vh,1120px)`, tablet `clamp(660px,82vh,1000px)`, and mobile `clamp(600px,82svh,900px)`. Main side padding is now 12 px desktop/tablet and 8 px mobile. The filter sidebar is narrower; Filters is available on desktop as well as mobile and can hide the sidebar to expand the map to the full content width. Hiding controls does not reset their filters. Default visibility remains desktop open / mobile closed.

MapLibre resizes after the panel layout changes and fits the selected original feature against the available canvas. An initially detected camera offset during quick closing was corrected by stopping and restarting an interrupted fit using the new canvas dimensions. Resize also refits a selected footprint on narrow screens; extent, symbol selection, source flags, zoom transitions, counts and basemap restoration remain functional. Attributes remain available through the table if WebGL cannot initialize.

Changed for this extension: `src/App.vue`, `src/components/MapCanvas.vue`, `src/components/AssetDetailsDrawer.vue`, `src/style.css`, `tests/e2e/inventory.spec.ts`, README, architecture notes and this report. Existing header, About-content, footer and attribution edits were retained. No package/lockfile, dependency, preprocessing, raw-source or generated-data edit was made.

Verification: `pnpm.cmd build` passed with Vue/TypeScript and strict nine-file publication checks. After the camera fix, local production Edge `pnpm.cmd test:e2e` passed **all 10 scenarios in 41.6 s**. Existing scenarios now assert desktop panel attachment/non-overlap, containment below the mobile canvas, keyboard attribute scrolling with an accessible close action, larger map height, and over 200 px additional map width when hiding desktop filters. All prior feature/filter/count/symbol/footprint/retry/basemap checks remain covered.

Additional production screenshots at 1440, 768, 390 and 320 px confirmed an internally scrolling panel and no document overflow. Real source feature `power_plant:270788980` (PLTU Pacitan) was used. At 1440 by 1000, the default frame measured 1164 by 840 px; hiding filters widened it further. At 390 by 844, the details panel fits below the canvas within the larger frame. Desktop/expanded and mobile screenshots were visually inspected; QA images remain ignored under `data/qa/map-details-*.png`, including `map-details-docked-mobile-final.png`. Plain background was used to isolate the actual source footprint from external tile availability.

All nine published data files remain **8,916,510 bytes**, including **6,119 original records**, **1,070 uncounted substation symbols** and embedded display coordinates for 643 plants. Historic line/substation filters, matching results, source geometries, attribution and ToR/data gaps are unchanged. No deployment occurred.

## Earlier refinements

Footer and close-button cleanup — 5 November 2026: removed the footer's MENTARI Grids / Deliverable 2 label and Coverage & limitations button from `src/App.vue`. The remaining OSM/OpenInfraMap/ODbL credits are centered. The redundant `Data:` label was subsequently removed; copyright text and all source/license links remain. Removed obsolete footer branding/button and responsive layout rules. Replaced font-dependent multiplication signs in `DataProvenanceDialog.vue` and `AssetDetailsDrawer.vue` with matching 18 px SVG crosses; shared `.icon-button` now has zero padding, fixed dimensions and no flex shrinking. Accessible button names and close behavior are preserved, as are the user's existing About-content edits.

README and architecture notes were updated. `pnpm.cmd build` passed, including TypeScript and strict publication checks. A local production Edge check at 1440, 390 and 320 px confirmed both footer removals, retained license links, working About/details close actions and exactly zero horizontal/vertical SVG center offset in both buttons. No tests were added for these low-impact presentation changes. Data, record counts, output sizes and remaining ToR gaps are unchanged; no deployment occurred.

Header cleanup — 5 November 2026: removed the redundant Inventory link and red active underline from `AppHeader.vue`. About the data is now a direct header button aligned to the right. Removed its unused navigation wrapper, active-link CSS and obsolete responsive navigation rules from `src/style.css`; README and architecture notes reflect the simpler header. `pnpm.cmd build` passed, including TypeScript and publication checks. A local production Edge check at 1440 and 320 px confirmed that Inventory is absent, About opens/closes correctly and its button fits inside the viewport. Existing user edits to `DataProvenanceDialog.vue` were preserved. Data, counts, publication sizes and ToR gaps are unchanged; no deployment occurred.

Zoom spacing refinement — 5 November 2026: `src/style.css` moves `.zoom-label` from `bottom: 38px` to `20px`, leaving a 4 px gap above the 16 px-high attribution row. README records the placement. `pnpm.cmd build` passed, including TypeScript and the publication guard; a local production Edge check measured a 4 px gap at viewport widths 1280 and 320 px. No new tests were added for this spacing-only change. Data, output counts/sizes and remaining ToR gaps are unchanged; no deployment occurred.

Update — 5 November 2026: map attribution is now constrained to a single line. The previous 75% desktop / 85% mobile maximum widths squeezed MapLibre's attribution control and wrapped its text. `src/style.css` removes those percentage caps and applies `white-space: nowrap`, retaining the existing linked credits and mobile font size. README and architecture notes describe the layout; the existing browser scenario checks one-line height, map-boundary fit and visible copyright links at widths 1280, 1024, 768, 390 and 320 px.

Verification: `pnpm.cmd build` passed, including TypeScript and strict nine-file publication checks. Production-preview Edge command `pnpm.cmd exec playwright test --grep 'Google basemap switch|mobile filters'` passed **2 tests in 15.9 s**. An additional 320 px screenshot (`data/qa/attribution-single-line-320.png`, ignored internal QA) was inspected: the credit is one 16 px-high row and does not overlap the scale. `git diff --check` passed. No data, record counts, output sizes, preprocessing, dependencies or hosting changed; publication remains nine files / 8,916,510 bytes and existing ToR gaps remain unchanged. No deployment occurred.

Latest basemap interaction fix: every choice row now selects its basemap when its preview, text, radio or padding is clicked. Pointer-down focus loss previously allowed `focusout` to close the popup before a label's native activation. `MapBasemapPicker.vue` now keeps pointer focus inside the picker and handles the row click once, then closes the popup and restores focus to the Layers button. Native radio changes preserve arrow-key navigation; Space on an already selected radio retains its standard behavior. Outside-click/Escape dismissal remains available.

Updated the existing production-browser scenarios to exercise preview clicks, text clicks, row-padding clicks, selected-row clicks, radio arrow/Space behavior, focus restoration and mobile selection. `pnpm.cmd build` passed with TypeScript and strict publication checks. `pnpm.cmd exec playwright test --grep 'Google basemap switch|mobile filters'` against local production preview with Edge passed **2 tests in 17.6 s**. README and architecture notes describe the expanded hit area. Source data, published counts/sizes and remaining ToR gaps are unchanged; no deployment occurred.

A separate Edge touch-emulation check (`hasTouch: true`, mobile viewport 390 by 844) passed real `tap()` actions on the imagery preview, plain-background text and OSM row padding. It recorded no page errors or horizontal overflow. Changed files for this interaction fix are `src/components/MapBasemapPicker.vue`, `tests/e2e/inventory.spec.ts`, README and these architecture/UI notes; preceding attribution changes remain intact.

Latest attribution refinement: the map now shows **© Google Maps | © OpenStreetMap contributors** for imagery, or one OSM credit on the OpenStreetMap/plain background. The `Basemap:`/`Inventory:` prefixes and repeated OpenInfraMap/ODbL links were removed from the map control. Full source and license links remain in the footer and publication metadata; map copyright credits remain linked and visible. Shared `OSM_ATTRIBUTION` prevents duplicate OSM credits. Earlier attribution examples below describe their historical stage.

Changed `src/utils/basemaps.ts`, `src/components/MapCanvas.vue`, the existing basemap browser assertions, README and architecture notes. `pnpm.cmd build` passed, including TypeScript and nine-file publication checks. Production-preview Edge checks (`pnpm.cmd exec playwright test --grep 'Google basemap switch|mobile filters'`) passed **2 tests in 19.0 s**, including exact imagery/plain/OSM credit text, copyright links, OSM deduplication, footer notices and mobile layout. No dataset, count, preprocessing, dependency or hosting change occurred; remaining ToR gaps are unchanged. All nine publication files remain 8,916,510 bytes, including 6,119 original records and 1,070 uncounted substation symbols.

Later user-authorized extension: [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md) documents 643 plant footprints, nine-file/schema-v3 publication and current tests. The stage-specific counts, hashes and UI descriptions below are preserved as history; the five earlier GeoJSONs and raw source remain unchanged.

Current state: this document preserves the sequence of earlier dashboard updates and their measured results. The latest simple sidebar, selection-driven legend, confirmed unused-file cleanup and current checks are documented in [SIMPLIFICATION_REPORT.md](SIMPLIFICATION_REPORT.md); those UI descriptions supersede earlier static-key/sidebar examples below.

The existing dashboard now has a collapsible legend, compact map controls and a Google Satellite basemap choice. The changes address the five supplied screenshots/requests. No preprocessing, data export, matching policy, package/lockfile, hosting configuration or deployment was changed in this update. Existing header and introduction edits were preserved. The later logo and single-extent refinement is recorded at the end of this report and supersedes the original two-control arrangement.

## Presentation decisions

| Request | Implemented behavior |
| --- | --- |
| Legend obscures the map | Starts collapsed as a small **Legend** button. Opens a compact voltage/asset/status key and closes with the same control. Keyboard activation, expanded state, focus styling and reduced-motion support are retained. Its state survives map style and zoom changes. |
| Remove Current scope | Removed the entire explanatory sidebar block. Voltage controls, source-status caveats and source scope in About remain available. |
| Smooth icon extent controls | Globe icon returns to Indonesia; extent-frame icon fits the current filtered records. Both have distinct tooltips and accessible names, use a 700 ms eased camera move, and move immediately under reduced-motion preference. Empty selections disable the fit control. Minimum zoom 2 accommodates Indonesia on narrow screens. |
| Planned-assets card | Removed from the KPI row because it is a data gap rather than a record metric. Its useful RUPTL/RUKN and official grouping limitations remain in **About the data**. Four computed inventory/review metrics remain. No planned features were added. |
| Google imagery | Added **Google Satellite** to a layers-icon basemap picker, alongside default OpenStreetMap, plain background and an optional configured custom style. Uses the exact supplied tile URL. |

The basemap popover supports native radio controls, outside-click dismissal, Escape and focus restoration. It fits a 390 px mobile viewport. Changing the basemap preserves camera, selected record, filters and inventory counts; a style reload reattaches the current filtered inventory and representative symbols. Satellite-only line casing improves contrast without changing records, voltage colors, filtering or counting. Existing plain-background fallback remains available after raster errors.

Long representative-symbol/counting explanations remain in About and feature details rather than covering the map. Polygon-to-symbol zoom behavior, candidate-layer defaults and all data qualifications are unchanged. The interface remains in English.

## Google integration and provenance

Configured raster URL:

```text
https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}
```

Google basemap attribution is displayed separately as **Basemap: © Google Maps**. Inventory attribution remains **Inventory: © OpenStreetMap contributors · OpenInfraMap · ODbL**. Imagery provides visual context and does not verify source geometry or operational status.

This implements the requested direct endpoint. It does not implement the key/session workflow or provider-specific copyright metadata of the documented [Google satellite Map Tiles API](https://developers.google.com/maps/documentation/tile/satellite). Account entitlements and a public-release attribution review are outside this local UI update; [Google's attribution documentation](https://developers.google.com/maps/documentation/tile/policies) describes that API's requirements. No tile proxy, bulk download, offline cache or prefetch was added. No deployment occurred.

## Files changed in this UI update

- Added `src/components/MapLegend.vue`, `src/components/MapBasemapPicker.vue` and `src/utils/basemaps.ts`.
- Updated `src/components/MapCanvas.vue` for icons, camera transitions, style switching, attribution and imagery contrast.
- Updated `src/components/FilterSidebar.vue`, `InventorySummary.vue`, `DataProvenanceDialog.vue` and `src/style.css` for the simplified layout and source information.
- Updated `tests/e2e/inventory.spec.ts` with disclosure/extent/basemap checks and mobile popover coverage.
- Updated `README.md`, `docs/ARCHITECTURE.md` and the historical `docs/SUBSTATION_ENHANCEMENT_REPORT.md` pointer; added this report.

## Verification

Commands executed for this update:

```powershell
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
git diff --check
```

| Check | Result |
| --- | --- |
| Existing Node data/filter/presentation tests | **10 passed** |
| Vue/TypeScript | **PASS** |
| Build-time publication guard | **PASS**, eight files, 5,476 original records plus 1,070 uncounted symbols |
| Production build | **PASS** |
| Development browser suite | **7 passed** |
| Local production browser suite | **7 passed** |
| Real Google imagery in local production preview | **25 HTTP 200 image/jpeg tiles** across desktop/mobile checks; no page JavaScript errors |
| Mobile layout | **PASS**, no document overflow at 390 px; picker stays within viewport |
| Raw GeoPackage fingerprint | **Unchanged**, SHA-256 `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba` |
| Diff whitespace check | **PASS**, normal Windows line-ending notices only |

The Google browser regression intercepts external imagery requests so it remains independent of provider availability. A separate live Edge check loaded actual Google imagery, verified separate attribution, and captured desktop/mobile views after pending requests settled. Canceled requests during viewport/camera changes are expected; the successful imagery responses and absence of page errors were checked. Screenshots were visually inspected and remain internal under ignored `data/qa/`:

- `dashboard-ux-google-production.png`
- `dashboard-ux-legend-production.png`
- `dashboard-ux-mobile-production.png`
- `dashboard-ux-basemaps-mobile.png`

The seven browser scenarios also retain the existing inventory/search/details, source flags, lazy/retryable candidates, parent-symbol selection, count invariants and failure fallback coverage. New assertions cover default-collapsed/keyboard legend operation, four KPI cards, removed scope block, extent icon behavior, preserved RUPTL/grouping information in About, basemap state/camera/count preservation and separate attribution. GIS preprocessing tests were not rerun because this update makes no preprocessing or data changes; their prior results remain in the substation enhancement report.

## Output sizes and unchanged data

| File in `public/data/` | Records / role | Bytes |
| --- | ---: | ---: |
| `transmission-lines.geojson` | 4,374 original segments | 6,151,922 |
| `substations-primary.geojson` | 622 original polygons | 646,266 |
| `substations-review.geojson` | 448 original review polygons | 450,635 |
| `substations-point-candidates.geojson` | 32 optional original points | 36,376 |
| `substation-display-points.geojson` | 1,070 uncounted display symbols | 490,830 |
| `summary.json` | Metadata | 4,267 |
| `data-catalog.json` | Provenance/checksums | 8,860 |
| `qa-report.json` | Aggregate QA | 11,263 |

These eight publication files remain **7,800,419 bytes** in total. The build guard verifies the five GeoJSON checksums against the unchanged catalog. The default selection remains **4,345 lines + 621 primary polygons**, with both candidate layers off. No point/symbol is added to primary counts. The primary/review inventories remain 622/448 across all source flags, and line filtering is unchanged.

The final local `dist/` totals **9,637,945 bytes**. Main JavaScript is 115,166 bytes, CSS 93,144 bytes, MapLibre vendor JavaScript 1,104,231 bytes and worker 518,989 bytes. The existing nonfatal Vite vendor-size warning remains; its threshold was not raised. No dependencies were added.

## Remaining data gaps

Authoritative planned RUPTL/RUKN assets, official regional/power-system membership, verified operation, source vintage, COD, capacity/MVA, circuit-km, AIS/GIS and unresolved physical station identity remain unavailable or unverified. This presentation update supplies no replacement values or infrastructure. See [the substation report](SUBSTATION_ENHANCEMENT_REPORT.md) for the source QA and preservation evidence.

## Follow-up: MENTARI logo and one extent action

Replaced the hand-drawn header icon with the existing `public/images/Mentari Logo_Tagline Revamp_Color.png` (96,120 bytes), preserving its full-color artwork and tagline. A white background maintains contrast with the green header; responsive dimensions and a narrow-screen spacing adjustment keep the logo, application title and navigation within 320 px. The source image was not edited or regenerated.

Removed **Zoom to Indonesia** and its unused handler. **Fit filtered records** is now the only extent action; it fits the current filters and fits the full selected inventory again after clearing them. The initial map still opens over Indonesia. The icon, tooltip, accessible name, smooth/reduced-motion behavior and empty-selection disabling remain. Basemap and zoom-in/out controls remain available.

Changed files for this follow-up: `src/components/AppHeader.vue`, `src/components/MapCanvas.vue`, `tests/e2e/inventory.spec.ts`, `README.md`, `docs/ARCHITECTURE.md` and this report. Concurrent user edits in `src/App.vue` were preserved. No dependency, data, preprocessing or deployment change was made.

Verification:

- `pnpm.cmd build`: **PASS**, including the unchanged publication guard and Vue/TypeScript checks.
- Production-preview Edge checks: **2 passed** using `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175` and `pnpm.cmd exec playwright test --grep 'MENTARI logo|mobile filters'`. They verify the actual image loads, one extent action, fitting a searched polygon and the full filtered inventory, legend controls and existing mobile flows.
- Header screenshots inspected at **1440, 390 and 320 px**; no document overflow. Internal screenshots: `data/qa/mentari-header-{1440,390,320}.png` and `mentari-single-extent.png`.
- `git diff --check`: **PASS**.

All eight publication files remain **7,800,419 bytes** with the same features, original geometries and checksums. The follow-up production bundle totals **9,733,642 bytes**: main JS 114,301 bytes, CSS 93,586 bytes, unchanged MapLibre vendor JS 1,104,231 bytes and worker 518,989 bytes. The existing nonfatal vendor-size warning remains. ToR/source gaps above remain unresolved; no values or infrastructure were fabricated. No deployment occurred.

## Follow-up: remove dashboard notice and download section

Removed the yellow **Source tags, unverified operation** banner from `src/App.vue`. Removed the entire **Download the published derivative database** section from `DataProvenanceDialog.vue`, including all five dataset links, three metadata links, processing note and version footer shown in the supplied screenshot. Removed the unused banner/download/version CSS. Source qualification remains in About, filters and feature details; source and ODbL attribution remain in the footer, map and publication metadata.

There are no download controls or `/data/` links in the application UI. This is a UI removal, not access control: the static WebGIS still fetches publicly accessible `/data/` URLs to render its map. No endpoint, original feature, attribute, geometry, metadata or checksum was changed. No backend or download-blocking claim was introduced.

Changed for this follow-up: `src/App.vue`, `src/components/DataProvenanceDialog.vue`, `src/style.css`, `tests/e2e/inventory.spec.ts`, `README.md`, `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md` and this report. Earlier header, extent and concurrent user edits were preserved.

Verification: `pnpm.cmd build` **passed**, including publication checks and Vue/TypeScript. The production-preview Edge command `pnpm.cmd exec playwright test --grep 'real map, flags|mobile filters'` with the previously documented environment variables returned **2 passed** (18.2 s). The existing inventory/search/details/candidate/mobile flow checks now also assert the banner, download heading and every dataset/download link are absent, while footer attribution remains. Desktop and 390 px About screenshots were inspected; no mobile document overflow was observed. Screenshots remain internal under `data/qa/dashboard-without-banner.png`, `about-without-downloads-desktop.png` and `about-without-downloads-mobile.png`. `git diff --check` passed.

The eight publication files remain **7,800,419 bytes**, with the same 4,374 lines, 622 primary polygons, 448 review polygons, 32 optional points and 1,070 uncounted symbols. Current `dist/` totals **9,730,988 bytes**: main JS 112,464 bytes, CSS 92,769 bytes and unchanged MapLibre/worker assets. The nonfatal vendor-size warning and remaining ToR/data gaps are unchanged. No deployment occurred.

## Follow-up: map controls inside a larger canvas

Moved the extent and basemap buttons into the upper-right corner of the map as a compact overlay. Removed the entire external toolbar, including its empty placeholder. The map body creates an isolated stacking context: the canvas is at z-index 0, the tool group at 4, and the basemap popover remains above other map overlays. Native zoom buttons sit below the group with a visible gap. Keyboard labels, tooltips, Escape dismissal and focus restoration remain functional.

Expanded the page to use its available width and reduced horizontal padding to 24 px on desktop, 16 px on tablet and 12 px on mobile. The sidebar retains its usable width. Increased map height to `clamp(600px, 72vh, 900px)` on desktop, `clamp(560px, 70vh, 800px)` on tablet and `clamp(520px, 72svh, 760px)` on mobile. The existing ResizeObserver updates the MapLibre canvas after layout changes.

Measured canvas sizes in local production preview:

| Browser viewport | Map width × height |
| --- | ---: |
| 1440 × 1100 | 1110 × 792 px |
| 1024 × 1100 | 737 × 770 px |
| 390 × 844 | 364 × approximately 608 px |
| 320 × 844 | 294 × approximately 608 px |

All four layouts had no document overflow. The basemap popover remains inside the map on narrow screens and above its zoom controls. Desktop/mobile screenshots were inspected using the plain-background option to keep verification independent of external imagery availability. Internal captures and measurements are under `data/qa/map-overlay-*.png`, `map-overlay-picker-*.png` and `map-overlay-verification.json`.

Changed files: `src/components/MapCanvas.vue`, `src/style.css`, `tests/e2e/inventory.spec.ts`, `README.md`, `docs/ARCHITECTURE.md` and this report. Browser assertions now check that the external toolbar is absent, map tools are inside the map, zoom controls do not overlap them, and the mobile picker stays within map bounds.

Verification: `pnpm.cmd build` **passed**, including publication integrity and Vue/TypeScript checks. With Edge and `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175`, `pnpm.cmd test:e2e` returned **7 passed** (52.6 s). This retains real feature clicks, zoom/presentation transitions, candidate retry/visibility, filters/search/details, basemap state/count preservation and mobile coverage. `git diff --check` passed. No dependency, package/lockfile, preprocessing, data, attribution or deployment configuration changed.

The eight data files remain **7,800,419 bytes** with all prior counts and checksums. Current `dist/` totals **9,730,859 bytes**: main JS 112,434 bytes, CSS 92,670 bytes, unchanged MapLibre vendor JS 1,104,231 bytes and worker 518,989 bytes. The existing nonfatal vendor-size warning and remaining ToR/data gaps are unchanged. No deployment occurred.

## Follow-up: MENTARI colors and typography

Replaced the green interface palette with blue `#0d4c8f` and red `#d02030` sampled from the supplied MENTARI logo. The header uses a blue gradient with a red active-navigation accent. Page surfaces use a subtle blue-gray background, white cards, softer borders and shadows. Filters, tables, dialogs, map buttons, legend and basemap picker share color tokens. The plain map background is now a cool neutral `#edf2f8`; voltage colors, primary/review/point symbols and source-status geometry styles are unchanged.

Added local **Plus Jakarta Sans** variable typography, including a font preload, `font-display: swap` and system fallbacks. The font is an application choice that complements the logo, not a claim about an official MENTARI brand typeface. The original logo remains unedited. The WOFF2 is 27,348 bytes; its included OFL notice is 4,402 bytes. Exact source URLs and font checksum are in [FONT_SOURCES.md](FONT_SOURCES.md). No npm dependency or external runtime font request was added.

Hover/focus colors and shadows transition over 180 ms. Basemap, About and feature panels have short 160–180 ms entrance animations. Reduced-motion preference disables animations and makes transitions effectively immediate. The header keeps a white keyboard-focus outline against its blue background. Narrow-screen logo/text sizing was adjusted for the new font without changing navigation behavior or the larger map layout.

Changed files: `src/style.css`, `src/components/AppHeader.vue`, `MapLegend.vue`, `MapBasemapPicker.vue`, `src/utils/basemaps.ts`, `index.html`, the two assets under `public/fonts/`, `README.md`, `docs/ARCHITECTURE.md`, `docs/FONT_SOURCES.md` and this report.

Verification:

- `pnpm.cmd build`: **PASS**, including the unchanged data guard and Vue/TypeScript checks.
- Production-preview Edge suite, `PLAYWRIGHT_CHANNEL=msedge`, `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175`, `pnpm.cmd test:e2e`: **7 passed** (50.4 s).
- Font request: **HTTP 200**, `font/woff2`, same-origin `/fonts/PlusJakartaSans-Latin-Variable.woff2`. Both regular and bold font checks passed. Only the local font was requested.
- Desktop/tablet/mobile checks at **1440, 1024, 390 and 320 px**: no document overflow; header, navigation and controls remain usable. Screenshots were inspected. Internal files are `data/qa/mentari-theme-*.png` and `mentari-theme-verification.json`.
- Reduced-motion check: panel animation is `none`; button transition is `0.00001s`.
- Sample text contrast ratios: body **11.52:1**, card notes **5.16:1**, metric labels **6.38:1**, white header text **8.58:1**, About text **5.66:1** and About caveat text **5.26:1**. These are sampled color pairs, not a complete accessibility audit.
- Publication hashes and byte counts remain unchanged. `git diff --check` passed.

The eight publication files remain **7,800,419 bytes**, with 4,374 line segments, 622 primary polygons, 448 review polygons, 32 optional source points and 1,070 uncounted symbols. The final local `dist/` totals **9,765,135 bytes**: main JS 112,434 bytes, CSS 95,028 bytes, unchanged MapLibre vendor JS 1,104,231 bytes and worker 518,989 bytes, plus the local font and notice. The existing nonfatal MapLibre size warning remains. No preprocessing, feature geometry, filtering, matching policy, source attribution, hosting configuration or deployment changed. Remaining ToR/data gaps are unchanged.
