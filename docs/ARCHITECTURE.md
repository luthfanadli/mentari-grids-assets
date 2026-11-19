# Architecture

## Data pipeline

`scripts/prepare_data.py` reads GeoPackage metadata through read-only SQLite and four feature layers through GeoPandas/Pyogrio. It checks CRS, required attributes, numeric voltage, flags, IDs and geometry before applying the [filter rules](DATA_FILTER_SPEC.md).

`scripts/substation_matching.py` performs all-pair source matching and generates interior substation representatives. The pipeline also derives plant representatives, measures WGS84 geodesic line length and validates publication geometry/counting roles. Source hashes are checked before and after processing.

Audit fixtures detect source changes and report exact differences before publication writes. Nine OSM files are generated in `public/data/`. The separate `scripts/prepare_planning.py` stages the three IPM project collections, validates their source hashes and attributes, and writes the collections with a catalog in `public/data/planning/`. Null routes remain inspectable as register entries. See the [data dictionary](DATA_DICTIONARY.md) for file roles and sizes. Both pipelines keep detailed QA in `data/qa/`.

`scripts/check_public_data.mjs` runs before every build. It validates filenames, metadata consistency, checksums, scope, geometry families, original IDs, symbol/parent linkage and absence of restricted source/reference assets. It needs neither Python nor the raw GeoPackage.

## Frontend ownership

| Module | Responsibility |
| --- | --- |
| `services/assetData.ts` | Validated fetches; cache in-flight/successful requests; evict failures for retry |
| `composables/useAssetFilters.ts` | Shared filters, loading/errors, lazy candidates, computed selection and counts |
| `composables/usePlanning.ts`, `utils/planning.ts` | Independent project layer loads, plan filters, register and map selections |
| `utils/filterAssets.ts` | Layer/status/voltage/search predicates, original-record deduplication and bounds |
| `utils/substationPresentation.ts` | Polygon style state, parent-symbol filtering and canonical viewport counts |
| `MapCanvas.vue` | MapLibre sources/layers, camera, selection and basemap lifecycle |
| `MapLayersControl.vue` | Responsive sidebar, search results, layer toggles, filter groups and retries |
| `MapBasemapPicker.vue` | Full-row basemap selection and native radio keyboard behavior |
| `AssetTable.vue`, `InventorySummary.vue` | Twenty-row pagination and matching original-record counts |
| `ProjectRegister.vue`, `PlanFilterFields.vue` | Project register pagination, target-year, source and stage controls |
| `AssetDetailsDrawer.vue` | Floating source-attribute card with independent scrolling |
| `DataProvenanceDialog.vue`, `AppHeader.vue` | Native About dialog and branding |

The map loads the OSM baseline and the small planning catalog independently. Each optional OSM or planning layer loads on first enable. Opening the project register loads all three planning layers. Shared promises cache successful requests and allow retries after failed validation or fetch. Large arrays use shallow refs.

## Rendering and interaction

Below zoom 10, interior circles/diamonds represent substation/plant polygons. At local zoom, original fills and boundaries replace them. Original point candidates stay at source coordinates. Marker clicks resolve parent records, and viewport counts canonicalize IDs across tiled fragments and multiple layers. Filtering never counts representatives as additional assets.

The navbar selects Map, Summary or RUPTL plans via URL hashes. The map stays mounted while reading a register so returning to it preserves the camera, layers and filters. Both registers retain their page and controls while inspecting a record on the map. The sidebar occupies its own column on desktop and opens over the map on smaller screens. Its scrollable contents support native checkboxes, disclosure controls, keyboard search and Escape. Panning, zooming and empty selections preserve layer choices.

The map fills the available viewport beneath the navbar. Reading a row or clicking a map feature opens its source details. The drawer shows other selected projects at the exact same coordinates when multiple point records overlap. A container query places the drawer at the bottom of narrow maps. Measured drawer bounds provide camera clearance. ResizeObserver handles sidebar changes and interrupted fits.

Project rendering uses amber dashed lines for routes, hollow squares for substation works and hollow circles for generation. The WebGL source carries only drawable geometry and stable feature identifiers. Full project attributes and entries without geometry are available in the register. Selected and viewport counts are calculated separately for OSM and plans.

## Basemaps and failures

`utils/basemaps.ts` defines OSM raster, Google imagery, plain background and an optional public `VITE_BASEMAP_STYLE_URL`. The OSM style places a local Natural Earth outline and labels below the tile layer. Style reloads restore asset sources, planning overlays, symbols, selection and viewport calculations. Provider and data attribution are available on the map.

MapLibre and its Vite worker are bundled separately. Inventory rendering does not wait for raster tiles. Two consecutive tile failures from an active raster/vector basemap show "Tiles unavailable" beneath its selected menu option. Inventory/general map errors and slow requests alone do not trigger it. Successful tile loading, a view change or a basemap switch clears the status; no banner covers the map and no automatic fallback changes the selection. WebGL failure leaves the searchable table/details available; failed data requests show filename-specific retry messages.

## Delivery

Vite produces a static site. The map uses a lazy MapLibre vendor chunk and bundled worker. Its asset data, project publications and regional cartography ship as ordinary static files. See [deployment](DEPLOYMENT.md).
