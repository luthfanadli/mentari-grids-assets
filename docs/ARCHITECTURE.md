# Architecture

## Data pipeline

`scripts/prepare_data.py` reads GeoPackage metadata through read-only SQLite and four feature layers through GeoPandas/Pyogrio. It checks CRS, required attributes, numeric voltage, flags, IDs and geometry before applying the [filter rules](DATA_FILTER_SPEC.md).

`scripts/substation_matching.py` performs all-pair source matching and generates interior substation representatives. The pipeline also derives plant representatives, measures WGS84 geodesic line length and validates publication geometry/counting roles. Source hashes are checked before and after processing.

Audit fixtures detect source changes and report exact differences before publication writes. JSON is deterministic UTF-8/CRLF, written through temporary-file replacement. Generated files contain source/license notices, policy/version metadata and checksums. Private evidence goes to `data/qa/`; only the nine [publication files](DATA_DICTIONARY.md) go to `public/data/`.

`scripts/check_public_data.mjs` runs before every build. It validates filenames, metadata consistency, checksums, scope, geometry families, original IDs, symbol/parent linkage and absence of restricted source/reference assets. It needs neither Python nor the raw GeoPackage.

## Frontend ownership

| Module | Responsibility |
| --- | --- |
| `services/assetData.ts` | Validated fetches; cache in-flight/successful requests; evict failures for retry |
| `composables/useAssetFilters.ts` | Shared filters, loading/errors, lazy candidates, computed selection and counts |
| `utils/filterAssets.ts` | Layer/status/voltage/search predicates, original-record deduplication and bounds |
| `utils/substationPresentation.ts` | Polygon style state, parent-symbol filtering and canonical viewport counts |
| `MapCanvas.vue` | MapLibre sources/layers, camera, selection and basemap lifecycle |
| `MapLayersControl.vue` | Five persistent choices, contextual symbols, voltage/status controls and retries |
| `MapBasemapPicker.vue` | Full-row basemap selection and native radio keyboard behavior |
| `AssetTable.vue`, `InventorySummary.vue` | Twenty-row pagination and matching original-record counts |
| `AssetDetailsDrawer.vue` | Floating source-attribute card with independent scrolling |
| `DataProvenanceDialog.vue`, `AppHeader.vue` | Native About dialog and branding |

Base loading fetches lines, primary polygons, plants, substation representatives and summary. Review polygons and point candidates are loaded independently on first enable. Large arrays use shallow refs. No separate filter state is kept in the map or table.

## Rendering and interaction

Below zoom 10, interior circles/diamonds represent substation/plant polygons. At local zoom, original fills and boundaries replace them. Original point candidates stay at source coordinates. Marker clicks resolve parent records, and viewport counts canonicalize IDs across tiled fragments and multiple layers. Filtering never counts representatives as additional assets.

Layers starts closed. Its fixed header and internally scrolling body remain inside the map. Panning, wheel zoom and navigation keep it open; explicit dismissal, outside-map activity or the basemap picker close it. Document listeners are removed on unmount. Escape respects an active asset-details card. Full-row label activation retains native checkbox/keyboard behavior.

The map remains full width behind an inset floating details card. A container query moves the card toward the bottom of narrow maps; measured popup bounds provide camera clearance. ResizeObserver handles container changes and interrupted fits. Camera animation and short UI transitions respect reduced-motion preferences.

Responsive CSS shares MENTARI colors and a locally hosted variable font. Small viewport-dependent gutters align header/content; map height is clamped separately for desktop/tablet/mobile. Table overflow stays inside its scroll container.

## Basemaps and failures

`utils/basemaps.ts` defines OSM raster, Google imagery, plain background and an optional public `VITE_BASEMAP_STYLE_URL`. Style reloads restore asset sources, plant images, selection and viewport calculations without resetting filters/camera. Provider credits and inventory attribution remain visible.

MapLibre and its Vite worker are bundled separately. Inventory rendering does not wait for raster tiles. Tile errors or a 12-second pending-tile timeout offer plain background. WebGL failure leaves the searchable table/details available; failed data requests show filename-specific retry messages.

## Delivery

This is a static application without a router, backend, database or tile archive. Six GeoJSONs total 8,887,904 bytes; the optional review and point files are lazy. MapLibre is a lazy vendor chunk and retains the existing Vite size warning. Profile before adding delivery infrastructure. See [deployment](DEPLOYMENT.md).
