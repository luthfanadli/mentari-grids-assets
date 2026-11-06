# MENTARI Grids — Transmission Asset Inventory

A Vue 3, Vite, TypeScript and MapLibre WebGIS for Deliverable 2. It displays preliminary OpenStreetMap records for Indonesia, with search, map/table selection and source attributes. Counts describe mapped records, not verified operational assets.

## Run

Use Node 24 and pnpm 12 with the checked-in lockfile:

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:5174. Published data is included in `public/data/`; Python and the private GeoPackage are needed only to regenerate it. Optional public basemap configuration is in [.env.example](.env.example).

## Use the dashboard

- **Layers** inside the map controls lines, primary substations, power plants and two default-off candidate layers. Voltage and OSM-status filters are folded inside it.
- Layers stays open during panning and zooming. Close it with its button, Close, Escape or an action outside the map. Opening the basemap menu also closes it.
- Search by name, reference, operator or source ID. Plant search also includes energy source and method. Reset restores defaults and clears search.
- Below zoom 10, polygon records use interior symbols; zooming in shows original footprints. Selecting either opens the same source record. Pink outlined circles represent separate unvalidated source points.
- Cards and the table count all matching original records. The viewport count deduplicates visible representations. Symbols never add records.
- Basemaps: OpenStreetMap, Google Satellite, plain background and an optional configured MapLibre style. The extent button fits filtered records. Failed tiles can fall back to the plain background.

The layout fills the viewport with small responsive margins. Candidate data loads only when enabled; requests are cached and failures can be retried. **About the data** explains provenance and missing coverage.

## Published scope

| Original records | All flags | Default selection |
| --- | ---: | ---: |
| Line segments, 70 / 150 / 275 / 500 kV | 4,374 | 4,345 |
| Transmission-tagged substation polygons | 622 | 621 |
| Review polygons | 448 | 0 |
| Point-only candidates | 32 | 0 |
| Power-plant footprints | 643 | 633 |
| **Total** | **6,119** | **5,599** |

Six GeoJSONs and three metadata files total **8,916,510 bytes**. The 1,070 substation symbols and embedded plant display coordinates are excluded from inventory totals. Power plants ignore voltage filters because no plant voltage field is supplied.

"Not flagged in OSM" does not verify operation. Point-candidate voltages and plant output units are unknown. Planned RUPTL/RUKN projects, official region/system assignments, verified capacity and COD are unavailable. See [coverage and limitations](docs/DATA_COVERAGE_AND_LIMITATIONS.md).

## Regenerate data

Place the supplied, unchanged `IDN.gpkg` in `data/raw/`, then:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

The pipeline reads four spatial layers, verifies the source fingerprint and writes publication files plus private QA under `data/qa/`. Missing inputs or unexpected source metrics fail explicitly; existing publication files are retained after rejection. CLI paths, source-update handling and the QGIS fallback are in [the maintenance guide](CODEX_START_HERE.md).

## Validate

```sh
pnpm test
pnpm build
pnpm test:e2e
```

Build runs the publication checksum/count guard, Vue/TypeScript checking and Vite. Node tests cover filters, counting, request caching/retry and Git byte preservation. Python tests cover source selection, geometry, matching and deterministic exports; source-dependent cases explicitly skip if the private GeoPackage is absent.

Browser tests use real MapLibre rendering and start the local dev server automatically. Install Chromium with `pnpm exec playwright install chromium`, or set `PLAYWRIGHT_CHANNEL=msedge` to use installed Edge. Production-preview commands are in [deployment](docs/DEPLOYMENT.md). The existing MapLibre vendor-size warning is nonfatal; it is not suppressed.

## Documentation

| Document | Purpose |
| --- | --- |
| [Maintenance guide](CODEX_START_HERE.md) | Change workflow and preprocessing commands |
| [Filter specification](docs/DATA_FILTER_SPEC.md) | Exact selection rules |
| [Source audit](docs/VERIFIED_DATA_AUDIT.md) | Fingerprint and measured source metrics |
| [Data dictionary](docs/DATA_DICTIONARY.md) | Files, schemas and field meanings |
| [Substation matching](docs/SUBSTATION_MATCHING.md) | Matching policy, eligibility and QA evidence |
| [Coverage and limitations](docs/DATA_COVERAGE_AND_LIMITATIONS.md) | Missing data and interpretation |
| [Architecture](docs/ARCHITECTURE.md) | Runtime modules and rendering |
| [Deployment](docs/DEPLOYMENT.md) | Static Vercel build and verification |

These documents describe the current implementation. Superseded implementation reports and UI change diaries are available through Git history.

## Attribution and assets

Data: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), exported through [OpenInfraMap](https://openinframap.org/), distributed under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Preserve attribution and license notices when redistributing. Static `/data/` URLs are public because the browser fetches them; the app has no download controls.

The supplied MENTARI logo is unchanged. [Plus Jakarta Sans](https://github.com/tokotype/PlusJakartaSans) is served locally with its [SIL OFL notice](public/fonts/PlusJakartaSans-OFL.txt), without runtime font-service requests. The Latin variable WOFF2 was obtained from [Google Fonts v12](https://fonts.gstatic.com/s/plusjakartasans/v12/LDIoaomQNQcsA88c7O9yZ4KMCoOg4Ko20yw.woff2); SHA-256: `153fc85b70298beeb1d61a5f723331649e7f23bb77302a66e61cb3e2fbdb5e79`.

Basemap credits remain separate from data attribution. OSM tiles follow the [OSMF tile policy](https://operations.osmfoundation.org/policies/tiles/). Google imagery uses the supplied direct raster endpoint, not a Google Map Tiles API key/session integration; provider terms and imagery attribution still apply. No offline tile download, proxy or prefetch is implemented.
