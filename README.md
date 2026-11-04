# MENTARI Grids — Transmission Asset Inventory

Deliverable 2 WebGIS, implemented in the existing Vue 3 + Vite + TypeScript repository with MapLibre GL JS. It presents **preliminary OpenStreetMap-based mapped features**, not a verified operational asset registry.

The working dashboard includes voltage, layer and OSM-status filters; name/ref/operator/source-ID search; map and table selection; source details; selected-record and rendered-viewport counts; optional unvalidated review polygons and point-only candidates; data downloads, attribution, loading/retry and empty states; and mobile layouts. At overview zooms, representative symbols locate polygon records; from zoom 10, their original footprints are displayed. Symbols never add inventory records.

## Run the application

Use the existing pnpm lockfile. Tested with Node 24.19.0 and pnpm 12.4.1. On PowerShell with script execution disabled, use `pnpm.cmd` for the commands below.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:5174. The preprocessed publication files are included under `public/data/`; Python and the raw GeoPackage are **not needed** to run or deploy the frontend. The default attributed OpenStreetMap basemap needs internet access. Copy `.env.example` to `.env.local` to supply a different public `VITE_BASEMAP_STYLE_URL`. Never put a secret in a `VITE_` variable.

## Dashboard map controls

- The legend starts collapsed. **Legend** opens/closes a compact symbol key without a permanent overlay obscuring the map.
- Globe icon: **Zoom to Indonesia**. Extent icon: **Fit filtered records**. Both have tooltips, keyboard labels and smooth camera transitions that respect reduced-motion settings.
- Layers icon: select **OpenStreetMap**, **Google Satellite** or **Plain background**. A configured custom style is retained as another choice. Switching preserves camera, asset filters, selection and counts.
- The dashboard shows four actual inventory/review metrics. Planned RUPTL/RUKN data gaps and official region/system limitations remain in **About the data**, alongside source scope and provenance.

Google Satellite uses the exact `mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}` endpoint supplied for this local implementation. The basemap receives separate Google Maps attribution; inventory attribution remains OSM/OpenInfraMap. This direct endpoint is not the documented Google Map Tiles API key/session integration. No Google account entitlement or provider-specific copyright metadata was verified. Before a public Google imagery release, use a service permitted by the applicable Google agreement and implement its provider attribution requirements; see [official satellite API documentation](https://developers.google.com/maps/documentation/tile/satellite) and [attribution policies](https://developers.google.com/maps/documentation/tile/policies). No offline tile download, proxy or prefetch was added. See [dashboard UI changes and verification](docs/DASHBOARD_UX_UPDATE.md).

## Reproduce spatial preprocessing

Place the supplied `IDN.gpkg` at `data/raw/IDN.gpkg`. The original source, Python environments and internal QA are gitignored. No replacement data is downloaded or generated when the file is missing.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py --input data/raw/IDN.gpkg --output public/data --qa-output data/qa
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

Relative CLI paths resolve from the repository even when invoked from another directory. The pipeline uses GeoPandas/Pyogrio, Shapely and PyProj. It reads only three layers as features and uses a read-only SQLite connection for all-layer metadata/counts. The original GeoPackage is checked with SHA-256 before and after processing.

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
| `summary.json` | Metadata, schema v2 | 4,267 |
| `data-catalog.json` | Metadata and dataset checksums | 8,860 |
| `qa-report.json` | Aggregate QA and matching policy/counts | 11,263 |

The default selection is **4,345 line segments and 621 primary substation polygons**, tagged neither construction nor disused where those flags exist. It excludes 25 construction-tagged lines, four disused-tagged lines, one construction-tagged primary polygon, all 448 review polygons and all 32 point-only candidates. Absence of flags **does not verify operation**. Each candidate layer loads only after its own toggle is enabled. Unknown-voltage filtering applies explicitly to both candidate layers.

The five GeoJSONs total 7,776,029 bytes. The existing line and two polygon GeoJSONs are byte-identical to the original MVP exports. Their geometry is not simplified or dissolved; output uses seven coordinate decimals, valid RFC 7946 ring winding, longitude/latitude, and original IDs including negative IDs. Original source-point coordinates are retained at full precision. Representative points are computed inside the published footprints and retain their parent IDs. Lengths remain WGS84 geodesic mapped geometry lengths, **not official circuit-km**.

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

`pnpm build` checks the eight data files, dataset checksums, version/count consistency, IDs, scope, representative-parent linkage and nonpublic-file exclusions before type checking and Vite compilation. It needs no raw data. Ten Node tests use the real generated datasets. Fifteen Python tests cover real-source counts/geometry, matching rules, deterministic exports and matching reports, unchanged baseline exports, exact point coordinates, representative containment, source-point promotion rejection and source-version mismatches. Source-dependent tests skip explicitly when the private raw file is absent.

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

For a production build, start `pnpm preview --host 127.0.0.1 --port 5175`, set `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175`, and run the seven browser scenarios, including dashboard controls and basemap switching. See the [dashboard UI report](docs/DASHBOARD_UX_UPDATE.md) and [substation data report](docs/SUBSTATION_ENHANCEMENT_REPORT.md). No deployment or hosting configuration change is part of these enhancements.

## Data scope and documentation

- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Coverage, exclusions and remaining ToR gaps](docs/DATA_COVERAGE_AND_LIMITATIONS.md)
- [Architecture and filtering behavior](docs/ARCHITECTURE.md)
- [Substation matching policy and representation](docs/SUBSTATION_MATCHING.md)
- [Vercel deployment](docs/DEPLOYMENT.md)

Planned RUPTL/RUKN infrastructure, official region/system assignments, COD, capacity, AIS/GIS and verified HVDC are not supplied. The UI displays this gap and the TypeScript extension contract has no fabricated records. The original ToR was not present; traceability follows the supplied development guide.

## Attribution and database license

Contains information from **© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)**, exported through [OpenInfraMap](https://openinframap.org/), available under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). The processed derivative database is distributed under ODbL 1.0 with attribution and license notices embedded in each GeoJSON and the catalog. The About panel links all four inventory/review subsets and the separate presentation symbols for free download, along with metadata and transformation methodology. Retain these notices when redistributing.

Default basemap: OpenStreetMap tiles, subject to the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/). There is no bulk tile download or offline tile cache. A custom provider requires its own applicable terms and attribution; MapLibre retains style-source attribution alongside the inventory attribution.
