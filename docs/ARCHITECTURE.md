# Architecture

## Data first

`scripts/prepare_data.py` reads GeoPackage metadata with read-only SQLite and spatial records with Pyogrio/GeoPandas. It validates required fields, numeric voltage, flags, EPSG:4326, geometry families, valid/nonempty geometry, coordinate bounds and original IDs before classification. It applies the exact predicates from `DATA_FILTER_SPEC.md`, quarantines conflicting source flags, and records exclusions rather than expanding scope from names or string voltage tags.

The pipeline normalizes properties, measures line geometry with WGS84 `pyproj.Geod`, normalizes polygon winding and rounds existing line/polygon coordinates to seven decimals. The original three GeoJSONs remain byte-identical. Eligible point-only candidates retain full source coordinate precision; their voltage stays null. Representative symbols are generated inside the published footprint with parent IDs and a non-inventory role. The pipeline validates geometry and original-record IDs separately from symbol linkage before writing. UTF-8 JSON uses explicit nulls, rejects NaN/Infinity, and uses temporary-file replacement. The source is hashed before and after; no source writes occur. Individual files are replaced atomically; use all eight outputs from one run together. No deployment is performed by preprocessing.

Historic audit comparisons live in `scripts/expected-audit.json`. A mismatch emits exact differences under internal QA and stops before publication unless explicitly overridden. QA artifacts contain the excluded line/polygon ID inventory, point-substation review layer and status-conflict quarantine. The public report is aggregate only. Metadata is computed, versioned by source/pipeline, deterministic, and includes per-GeoJSON checksums.

`scripts/substation_matching.py` evaluates all 68×2,753 point/polygon pairs, retaining intersection/proximity/ID/name/reference/attribute evidence. Policy-supported matches, uncertain associations and distinct candidates are recorded for every point. Matched/uncertain and role/function-held points never enter the optional point dataset. Full reproducible JSON/CSV stay under internal QA; public metadata contains aggregate results/policy. See `SUBSTATION_MATCHING.md`.

`scripts/check_public_data.mjs` is the build-time guard. It needs no raw data or Python; it checks all eight generated files, version/hash/count consistency, unique original IDs, scope, one-to-one symbol/parent linkage, symbol non-inventory roles and nonpublic-file exclusions.

## Vue application

- `services/assetData.ts`: validated fetches, cached successful/in-flight requests and retryable failures. Base lines, primary polygons, representative symbols and summary load once. Polygon-review and point-only candidates are independently lazy.
- `composables/useAssetFilters.ts`: data/error/loading state, filter state, on-demand candidate loading and computed selection/counts. Large feature arrays use shallow refs.
- `utils/filterAssets.ts`: pure layer, status, voltage and name/ref/operator/ID filtering; independent candidate visibility; missing-voltage control; geometry bounds.
- `types/assets.ts`: publication schema and a future authoritative planned-asset contract. The latter creates no records, statistics or official assignments.
- `AppHeader`, `InventorySummary`, `FilterSidebar`: workspace navigation, computed KPIs and accessible controls.
- `utils/substationPresentation.ts`: representative-parent filtering and canonical deduplicated rendered-record counts. Representative symbols never enter the selected inventory array.
- `MapCanvas`: dynamically imported MapLibre GL JS 6, original-record source plus filtered representative-symbol source. Voltage-colored line styling/filtering is unchanged. Below zoom 10, polygon records use interior symbols; at local zoom, original primary/review footprints replace symbols. Eligible original points use distinct pink outlined symbols when enabled. All representations select the original feature ID and preserve counts.
- `AssetTable`: paginated searchable records, keyboard buttons and selection shared with the map.
- `AssetDetailsDrawer`: source-only details, fallback-label and uncertainty notices, geodesic measurement meaning and explicit unknowns. Escape closes the drawer and returns focus.
- `DataProvenanceDialog`: native modal/focus handling, source attribution, coverage and source-status caveats. The download section and dataset links have been removed; ODbL attribution remains in the map/footer and publication metadata. Static data requests remain public and are not protected by removing UI links.

The same deduplicated original-feature array drives the map, list and KPI counts, with separate point-only and polygon-review metrics. Source-layer totals/voltage counts come from generated metadata. Viewport counts canonicalize `represented_feature_id` or `feature_id` across sources/layers/tile fragments; they are not national totals or exact geometric intersections. Changes close details if a record no longer matches. Unknown-voltage filtering applies explicitly to both candidate groups. Candidate data load failures are separately retryable.

## Map delivery and failure behavior

The default inline raster style uses `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, visible OpenStreetMap attribution and standard browser caching/referrer behavior. No prefetch or offline tile download is provided. `VITE_BASEMAP_STYLE_URL` allows another lawful MapLibre style; its provider attribution is preserved alongside source attribution. Vite public variables are visible to all users, so secrets are unsuitable.

`utils/basemaps.ts` defines OpenStreetMap, the user-supplied Google Satellite tile endpoint, plain background and optional configured style. `MapBasemapPicker.vue` provides a compact radio popover with outside-click/Escape dismissal and focus restoration. A full style reload reattaches the current filtered inventory/symbol sources and selected feature, while preserving camera and Vue filter state. Google imagery has separate **Basemap: © Google Maps** attribution; **Inventory: © OpenStreetMap contributors** remains independent. Satellite-only line casing improves contrast without changing features or filters. Direct-endpoint service limitations are documented in README; this is not an official Google key/session integration.

`MapLegend.vue` starts collapsed and keeps its state through style/zoom changes. Its compact key retains voltage, asset and status symbols; longer geometry/counting explanations stay in About/details. The single extent control uses a frame SVG icon to fit the active filtered records, with a tooltip and accessible name. Camera moves use an eased transition with zero duration under reduced-motion preference; minimum zoom 2 allows the national view to fit narrow screens. The removed Current scope sidebar block and planned-data KPI are documented in About; four inventory metrics remain on the dashboard. `AppHeader.vue` displays the supplied full-color MENTARI PNG from `public/images` at responsive dimensions on a white background.

Map tools are positioned inside `.map-body`, above the MapLibre canvas in an isolated stacking context. The external toolbar is removed. The extent/basemap group has z-index 4; its popover sits above the legend and native map controls. Native zoom controls are offset below the group. Main content now uses the full page width with 24 px desktop, 16 px tablet and 12 px mobile side padding. Map height uses `clamp(600px, 72vh, 900px)` on desktop, `clamp(560px, 70vh, 800px)` on tablet and `clamp(520px, 72svh, 760px)` on mobile. The existing ResizeObserver keeps MapLibre sized to its canvas.

`style.css` defines shared MENTARI blue/red, surface, text, border, shadow and motion tokens. Header, cards, tables, dialogs, legend and basemap picker use the same palette. MapLibre's plain background matches the cool neutral canvas color; voltage and asset-symbol colors are unchanged. Plus Jakarta Sans is a local variable WOFF2 asset, preloaded by `index.html` and loaded with `font-display: swap`; no external font service is needed at runtime. Short color/shadow transitions and panel entrance animations respect `prefers-reduced-motion`. Font provenance, checksum and bundled OFL notice are recorded in `FONT_SOURCES.md`.

MapLibre 6 requires a bundled worker URL. `MapCanvas.vue` imports `maplibre-gl-worker.mjs?worker&url` and sets it before constructing the map, following the [official Vite integration](https://maplibre.org/maplibre-gl-js/docs/). This makes the worker and its imports available in both dev and production builds.

Inventory rendering/viewport counts do not wait for external raster requests. Map errors or tiles still pending after 12 seconds offer a **Use plain background** action; overlays and records remain usable. WebGL initialization failure leaves the searchable list/details available with an explicit message. Missing or malformed inventory files show a retryable filename-specific error; mixed dataset counts show a redeployment message.

## Performance and hosting

The five intended GeoJSONs total 7,776,029 bytes. Review polygons (450,635 bytes) and point-only candidates (36,376 bytes) are lazy; representative display symbols add 490,830 bytes without adding inventory records. MapLibre remains a separate lazy chunk, and a 20-row table limits DOM work. Browser tests cover actual symbols/footprints, zoom transitions, selection, candidate retries, unknown voltage and mobile controls. No new dependency, backend, database, object store, PMTiles or analytics was added. This enhancement is local-only; hosting configuration is unchanged.

The production build reports a MapLibre vendor chunk above Vite's 500 kB warning threshold (about 1.10 MB, 298 kB gzip), plus a bundled worker of about 519 kB. The warning is retained and documented. Splitting MapLibre internals would add complexity without reducing bytes needed by the map; no threshold was raised to hide it. Further measurements on slower/mobile devices should precede architectural changes.

Vercel builds the existing Vite app to `dist/`; only static artifacts are served. Preprocessing remains local. No router or serverless function was added, so no catch-all rewrite is needed. Data paths revalidate to avoid holding stable filenames indefinitely. See `DEPLOYMENT.md`.
