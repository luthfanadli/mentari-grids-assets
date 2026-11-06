# MENTARI Grids — Transmission Asset Inventory

Deliverable 2 WebGIS, implemented in the existing Vue 3 + Vite + TypeScript repository with MapLibre GL JS. It presents **preliminary OpenStreetMap-based mapped features**, not a verified operational asset registry.

The working dashboard includes voltage, layer and OSM-status filters; name/ref/operator/source-ID search; map and table selection; source details; selected-record and rendered-viewport counts; optional unvalidated review polygons and point-only candidates; source power-plant footprints; attribution, loading/retry and empty states; and mobile layouts. At overview zooms, representative symbols locate polygon records; from zoom 10, their original footprints are displayed. Symbols never add inventory records.

## Run the application

Use the existing pnpm lockfile. Tested with Node 24.19.0 and pnpm 12.4.1. On PowerShell with script execution disabled, use `pnpm.cmd` for the commands below.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:5174. The preprocessed publication files are included under `public/data/`; Python and the raw GeoPackage are **not needed** to run or deploy the frontend. The default attributed OpenStreetMap basemap needs internet access. Copy `.env.example` to `.env.local` to supply a different public `VITE_BASEMAP_STYLE_URL`. Never put a secret in a `VITE_` variable.

## Filters and legend

- Open **Layers** at the top left inside the map. It starts closed on every screen size; there is no separate sidebar or Legend button.
- Toggle **Transmission lines**, **Primary substations** and **Power plants** directly. **Review polygons** and **Point-only candidates** are optional, unvalidated and off by default. All five choices remain available when switched off or when a search has no matches.
- Open **Voltage** for 500/275/150/70 kV and, when candidates are enabled, **Unknown voltage**. Grid voltage filters apply to lines and substations; power plants remain independent. Colored line samples explain line voltage.
- Open **OSM status** for source tags and solid/dashed/dotted line patterns. Tags do not verify operation. Layer symbols also distinguish overview markers, local footprints and matching construction styles.
- Layers stays open while selecting controls, panning, wheel zooming or using map navigation. Use **Layers**, Close or Escape to dismiss it, or click/focus outside the map. Opening the basemap menu closes Layers to avoid stacked menus. The panel scrolls within the map; Reset restores the same default filters and clears search as before.
- Search remains above the full-width map. The five compact cards and list count matching original records; **rendered in viewport** remains a separate map count. Layer controls have no source totals, and display symbols never add records.

## Dashboard map controls

The footer contains only centered source/license credits. Data information remains accessible through **About the data** in the header; close icons use centered SVGs.

- The zoom label sits 4 px above the single-line map attribution.
- **Layers** combines layer visibility, map symbols and folded voltage/status controls in one in-map panel. It stays inside the map on desktop and mobile.
- Extent icon: **Fit filtered records**, the single extent action. It fits the active selection and provides a tooltip, keyboard label and smooth camera transition that respects reduced-motion settings. Clear filters to fit the full selected inventory again.
- The header uses the supplied full-color MENTARI logo from `public/images`, with a white background for legibility and responsive sizing. **About the data** is its only action; the redundant Inventory link and active underline were removed.
- Basemap map icon: select **OpenStreetMap**, **Google Satellite** or **Plain background**. A configured custom style is retained as another choice. Click anywhere in a choice row (preview, text or padding) to select it; native radio keyboard controls remain available. Switching preserves camera, asset filters, selection and counts.
- Selecting a record opens **Asset details** as a floating card over the map, with rounded corners, inset margins and a shadow. On narrow maps the card floats near the bottom. The canvas stays full size and selected features are fitted clear of the card. The repeated footer note is omitted. Attributes scroll independently; the close button stays visible.
- The map always uses the full content width. The external Filters toggle and sidebar were removed; height, search, compact cards, selection and dataset counts retain their behavior.
- Extent and basemap controls float inside the map at the upper right, with zoom controls below them. The external toolbar has been removed. The dashboard fills the available viewport with small adaptive side gutters, so cards, search, map and table grow together; the compact responsive map height is retained and the basemap menu remains within the map on mobile.
- The dashboard shows five separate metrics, including power-plant footprints. Planned RUPTL/RUKN data gaps and official region/system limitations remain in **About the data**, alongside source scope and provenance.

Google Satellite uses the exact `mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}` endpoint supplied for this local implementation. Map attribution stays on one line on desktop and mobile, without clipping its links. The map uses compact linked credits: `© Google Maps | © OpenStreetMap contributors` for imagery, and one OSM credit for OpenStreetMap/plain backgrounds. Full OpenInfraMap and ODbL notices remain in the footer and publication metadata. This is a direct raster integration, without the key/session workflow or provider-specific metadata of the [documented Google Map Tiles API](https://developers.google.com/maps/documentation/tile/satellite). No offline tile download, proxy or prefetch was added. See [dashboard UI changes, verification and integration limits](docs/DASHBOARD_UX_UPDATE.md).

## Power plants

The user-authorized generation context layer reads only `power_plant`: 643 valid source footprints (632 Polygon, 11 MultiPolygon), with 633 not construction-tagged and ten construction-tagged. It is on by default, uses red diamonds below zoom 10 and original boundaries above it, and has its own count. Derived markers never add records. Grid voltage filters do not hide plants; OSM status, search and the layer toggle still apply.

Energy-source/method/output/start-date tags are preserved. The export supplies no output unit, so values are not assumed MW or verified capacity; source start dates are not verified COD. Generator layers remain excluded. Summary/catalog schema is v3, pipeline v1.2.0; all five earlier GeoJSONs are byte-identical. See [the power-plant report](docs/POWER_PLANTS_REPORT.md).

## Theme and typography

The interface uses the supplied MENTARI logo's blue (`#0d4c8f`) and red (`#d02030`), a soft blue-gray page background, white cards and matching map controls. Voltage colors and primary/review/point symbols retain their data meanings.

Plus Jakarta Sans is served locally as one 27,348-byte variable WOFF2 file, with a preload, `font-display: swap` and system fallbacks. There are no runtime Google Fonts requests. Hover/focus transitions and panel entrances are short; reduced-motion preferences disable animations. The logo artwork is unchanged. See [font sources and included license](docs/FONT_SOURCES.md) and the latest verification in [the dashboard report](docs/DASHBOARD_UX_UPDATE.md).

## Reproduce spatial preprocessing

Place the supplied `IDN.gpkg` at `data/raw/IDN.gpkg`. The original source, Python environments and internal QA are gitignored. No replacement data is downloaded or generated when the file is missing.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py --input data/raw/IDN.gpkg --output public/data --qa-output data/qa
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

Relative CLI paths resolve from the repository even when invoked from another directory. The pipeline uses GeoPandas/Pyogrio, Shapely and PyProj. It reads only four layers as features and uses a read-only SQLite connection for all-layer metadata/counts. The original GeoPackage is checked with SHA-256 before and after processing.

If `py` is unavailable but QGIS is installed, its Python can be used without changing the system installation. This session used:

```powershell
$env:PYTHONHOME='C:/Program Files/QGIS 3.44.15/apps/Python312'
$env:PYTHONIOENCODING='utf-8'
$env:GDAL_DATA='C:/Program Files/QGIS 3.44.15/apps/gdal/share/gdal'
$env:PROJ_DATA='C:/Program Files/QGIS 3.44.15/share/proj'
$env:PATH='C:/Program Files/QGIS 3.44.15/bin;'+$env:PATH
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p 'test_*.py' -v
```

`scripts/expected-audit.json` records the supplied-source audit, separate from filtering logic. A changed fingerprint or count writes the exact expected/actual differences to internal QA and exits nonzero **before publication writes**. After investigating a legitimate source update, `--allow-source-mismatch` explicitly permits actual results while preserving the reported differences. Existing publication files are retained after a rejected run; do not mistake them for the rejected source's output.

## Verified publication

| File in `public/data/` | Features | Bytes |
| --- | ---: | ---: |
| `transmission-lines.geojson` | 4,374 | 6,151,922 |
| `substations-primary.geojson` | 622 | 646,266 |
| `substations-review.geojson` | 448 | 450,635 |
| `substations-point-candidates.geojson` | 32 unvalidated point-only records | 36,376 |
| `substation-display-points.geojson` | 1,070 derived symbols; **not inventory** | 490,830 |
| `power-plants.geojson` | 643 source footprints | 1,111,875 |
| `summary.json` | Metadata, schema v3 | 5,017 |
| `data-catalog.json` | Metadata and dataset checksums | 10,799 |
| `qa-report.json` | Aggregate QA including plants | 12,790 |

The default selection is **4,345 line segments, 621 primary substation polygons and 633 power-plant footprints**, tagged neither construction nor disused where those flags exist. It excludes 25 construction-tagged lines, four disused-tagged lines, one construction-tagged primary polygon, ten construction-tagged plants, all 448 review polygons and all 32 point-only candidates. Absence of flags **does not verify operation**. Each candidate layer loads only after its own toggle is enabled. Unknown-voltage filtering applies explicitly to both candidate layers.

The six GeoJSONs total 8,887,904 bytes; all nine publication files total 8,916,510 bytes. The existing line and two polygon GeoJSONs are byte-identical to the original MVP exports. Their geometry is not simplified or dissolved; output uses seven coordinate decimals, valid RFC 7946 ring winding, longitude/latitude, and original IDs including negative IDs. Original source-point coordinates are retained at full precision. Representative points are computed inside the published footprints and retain their parent IDs. Lengths remain WGS84 geodesic mapped geometry lengths, **not official circuit-km**.

The same preprocessing command now audits **68 points × 2,753 raw polygons = 187,204 pairs**, using intersection, metric proximity, original IDs, distinctive names/references and available attributes. Results: **2 matched, 25 uncertain, 41 distinct point-only candidates** under the versioned screening policy. Matched is a supported correspondence, not official duplicate certification. Of the 41 distinct candidates, 32 are eligible for the separate optional layer; nine remain held for function/role review. Every point's structured voltage remains unknown; none is promoted to primary inventory.

Full evidence and all original point attributes/geometries are retained in `data/qa/substation-matching-report.json` and its 68-row CSV. Internal files also include all source points, exclusions and conflict quarantine. They remain outside publication. No raw GPKG, source license PDF, ToR or restricted reference material is a static asset. See [matching policy and schema](docs/SUBSTATION_MATCHING.md).

## Validate and build

```sh
pnpm check:data
pnpm test
pnpm typecheck
pnpm build
pnpm preview
```

`pnpm build` checks the nine data files, dataset checksums, version/count consistency, IDs, scope, representative-parent linkage and nonpublic-file exclusions before type checking and Vite compilation. It needs no raw data. Sixteen Node tests use the real generated datasets, including selection-driven legend cases and a Git staging/checkout regression for byte integrity. Nineteen Python tests cover real-source counts/geometry, matching rules, deterministic exports and matching reports, unchanged baseline exports, exact point coordinates, representative containment, source-point promotion rejection, source-version mismatches and platform-independent JSON serialization. Source-dependent tests skip explicitly when the private raw file is absent.

Generated JSON/GeoJSON uses canonical UTF-8/CRLF bytes to retain the original catalog checksums. `.gitattributes` disables Git text conversion for `public/data/`. Keep the rule and all nine outputs in the same commit; when upgrading an existing checkout, refresh tracked data with `git add --renormalize public/data/`. The strict size/hash checks remain enabled. See [the Windows-to-Vercel build fix](docs/BUILD_FIX_GIT_LINE_ENDINGS.md) and [deployment notes](docs/DEPLOYMENT.md).

Browser tests use Playwright and real MapLibre WebGL rendering:

```sh
pnpm exec playwright install chromium
pnpm test:e2e
```

On this Windows machine, installed Edge was used without a browser download:

```powershell
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e
```

For a production build, start `pnpm preview --host 127.0.0.1 --port 5175`, set `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175`, and run the eleven browser scenarios, including persistent Layers during pan/zoom, fluid laptop/wide-screen layout, unknown voltage, candidate loading, dashboard controls and basemap switching. See the [simplification and cleanup report](docs/SIMPLIFICATION_REPORT.md), [dashboard UI history](docs/DASHBOARD_UX_UPDATE.md) and [substation data report](docs/SUBSTATION_ENHANCEMENT_REPORT.md). No deployment or hosting configuration change is part of these enhancements.

## Data scope and documentation

- [Power-plant source audit and verification](docs/POWER_PLANTS_REPORT.md)
- [Unified in-map Layers control and verification](docs/LAYERS_CONTROL_REFACTOR.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Coverage, exclusions and remaining ToR gaps](docs/DATA_COVERAGE_AND_LIMITATIONS.md)
- [Architecture and filtering behavior](docs/ARCHITECTURE.md)
- [Substation matching policy and representation](docs/SUBSTATION_MATCHING.md)
- [Vercel deployment](docs/DEPLOYMENT.md)

Planned RUPTL/RUKN infrastructure, official region/system assignments, COD, capacity, AIS/GIS and verified HVDC are not supplied. About documents these gaps. An unused speculative planned-asset type was removed; any future integration needs sourced records and a reviewed schema. The original ToR was not present; traceability follows the supplied development guide.

## Repository maintenance

Unused Vue/Vite demo component, demo images/SVGs, sprite sheet, speculative type and obsolete CSS have been removed. The source GeoPackage, source license, expected audit, published datasets, reproducible analysis/preprocessing scripts, font license and historical audit reports are retained. Historical reports preserve their stage-specific findings and link to the [current simplification report](docs/SIMPLIFICATION_REPORT.md).

## Attribution and database license

Contains information from **© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)**, exported through [OpenInfraMap](https://openinframap.org/), available under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). The processed derivative database is distributed under ODbL 1.0 with attribution and license notices embedded in each GeoJSON and the catalog. The dashboard has no download section or dataset links. Its static `/data/` URLs remain publicly accessible because the map fetches them in the browser; removing UI links does not provide access control. Source/status caveats remain in filters, feature details and About rather than a dashboard banner. Retain attribution and license notices when redistributing.

Default basemap: OpenStreetMap tiles, subject to the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/). There is no bulk tile download or offline tile cache. A custom provider requires its own applicable terms and attribution; MapLibre retains style-source attribution alongside the inventory attribution.
