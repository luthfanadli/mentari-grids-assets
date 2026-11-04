# Dashboard UI update — 4 November 2026

The existing dashboard now has a collapsible legend, compact map controls and a Google Satellite basemap choice. The changes address the five supplied screenshots/requests. No preprocessing, data export, matching policy, package/lockfile, hosting configuration or deployment was changed in this update. Existing header and introduction edits were preserved.

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
