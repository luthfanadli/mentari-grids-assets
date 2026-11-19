# MENTARI Grids

A Vue 3, Vite, TypeScript and MapLibre WebGIS for Deliverable 2. Explore Indonesia’s mapped electricity network alongside the supplied IPM planning projects. The inventory and project register retain the source IDs, attributes and units of each publication.

## Run

Use Node 24 and pnpm 12 with the checked-in lockfile:

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:5174. Windows PowerShell users can run the commands with `pnpm.cmd`. The repository includes the prepared map data. Python and the private inputs are needed for regeneration. Optional basemap configuration is in [.env.example](.env.example).

## Use the dashboard

- **Map** fills the space below the navbar. The left sidebar is open on desktop. On a phone, use **Layers** to open it. Panning and zooming preserve the panel and your selections.
- In the sidebar, toggle mapped assets and project layers by asset type. Planning layers are **Transmission projects**, **Substation projects** and **Generation projects**. Open **Review candidates** for the two optional substation layers. Grid voltage applies to lines and substations. **OSM status** applies to the baseline. **Project filters** appears when at least one project layer is enabled and starts collapsed. It controls the plan source, stage and target COD year, shares its values with **RUPTL plans**, and retains those values when project layers are switched off.
- Search the enabled layers by name or source ID and select a result to inspect it. Plan search also accepts provinces, systems and source site IDs. Select an overlapping project point to browse the matching projects at those coordinates.
- **Summary** opens a modal over the map with filtered OSM record counts and the paginated asset table. Its search updates the shared map selection. It distinguishes the selected inventory from the records drawn in the viewport. Polygon symbols below zoom 10 and original footprints at local zoom represent the same records.
- **RUPTL plans** opens the project register in the same modal, including RUKN studies and entries without a drawable route. Filter the register, use **Show results on map**, or select a row to close the modal and inspect one project. The map sidebar can load any one planning layer independently.
- Close a report using its close button, Escape or the desktop backdrop, and open reports from the navbar. Tables show ten records per page with pagination at the bottom of the visible table. Reports fill the screen on phones. Reopening preserves search, filter choices, table pages and scroll positions. The map camera stays in place while reading a report. Existing `#summary` and `#plans` links and browser Back/Forward open the corresponding report.
- The basemap picker offers OpenStreetMap, Google Satellite, plain background and an optional custom style. Natural Earth cartography provides regional context while OSM tiles load. Source attribution and the dated data comparison are available under **About the data**.

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

The separate planning publication adds **4,057 project records**, of which **4,047** have map geometry. Its three GeoJSONs and catalog total **6,507,622 bytes**. Planning overlays start off. The combined data publications occupy **15,424,132 bytes**. See [the comparison with Indonesia Power Map](docs/DATA_COVERAGE_AND_LIMITATIONS.md#comparison-with-indonesia-power-map) for differences in baseline units, coverage and source dates.

## Regenerate data

Place the supplied `IDN.gpkg`, `ruptl_transmission.geojson`, `ruptl_substations.geojson` and `ruptl_generators.geojson` in `data/raw/`. After reviewing a staging run as described in [the maintenance guide](CODEX_START_HERE.md), use:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe scripts/prepare_planning.py
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

The pipeline reads four spatial layers, verifies the source fingerprint and writes publication files plus private QA under `data/qa/`. Missing inputs or unexpected source metrics fail explicitly; existing publication files are retained after rejection. CLI paths, source-update handling and the QGIS fallback are in [the maintenance guide](CODEX_START_HERE.md).

## Validate

```sh
pnpm test
pnpm build
pnpm test:e2e
```

Build runs the publication checksum/count guard, Vue/TypeScript checking and Vite. Node tests cover filters, counting, request caching/retry and Git byte preservation. Python tests cover source selection, geometry, matching, inherited planning-file access permissions on Windows and deterministic exports. Source-dependent cases report skips when their required private inputs are absent.

Browser tests use real MapLibre rendering and start the local dev server automatically. They cover modal dismissal, focus restoration, browser history, shared map filters, candidate retries, project selection and responsive layouts. Install Chromium with `pnpm exec playwright install chromium`, or set `PLAYWRIGHT_CHANNEL=msedge` to use installed Edge. Production-preview commands are in [deployment](docs/DEPLOYMENT.md). The MapLibre vendor-size warning is nonfatal.

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

Planning data credit Sitompul, S. A. (2026), *Indonesia Power Map: Data Collection* v2.0.0, under CC BY-SA 4.0, with ODbL for OSM-derived material. The prepared files add source-namespaced identifiers and mark unusable route geometries as absent. [Source and citation](https://github.com/sandro71626/ipm-model) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

The local outline and labels occupy 324,563 bytes outside the asset inventory. They use public-domain Natural Earth cartography. Input versions and reproduction steps are in [the basemap generator](scripts/prepare_basemap.py).

The supplied MENTARI logo is unchanged. [Plus Jakarta Sans](https://github.com/tokotype/PlusJakartaSans) is served locally with its [SIL OFL notice](public/fonts/PlusJakartaSans-OFL.txt), without runtime font-service requests. The Latin variable WOFF2 was obtained from [Google Fonts v12](https://fonts.gstatic.com/s/plusjakartasans/v12/LDIoaomQNQcsA88c7O9yZ4KMCoOg4Ko20yw.woff2); SHA-256: `153fc85b70298beeb1d61a5f723331649e7f23bb77302a66e61cb3e2fbdb5e79`.

Basemap credits remain separate from data attribution. OSM tiles follow the [OSMF tile policy](https://operations.osmfoundation.org/policies/tiles/). Google imagery uses the supplied direct raster endpoint, not a Google Map Tiles API key/session integration; provider terms and imagery attribution still apply. No offline tile download, proxy or prefetch is implemented.
