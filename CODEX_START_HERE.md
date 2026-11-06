# Codex Development Guide (v2) — MENTARI Grids Transmission Asset Inventory

Latest authorized scope: add the source `power_plant` layer as generation context, not individual generators or planned projects. There are 643 source footprints (633 not construction-tagged, ten construction-tagged), with no voltage/disused field or output unit. Preserve raw attributes and geometry; do not infer MW/COD/connections. Current publication is nine files, schema v3/pipeline v1.2.0. The original grid predicates and five prior GeoJSONs remain unchanged. See [the plant report](docs/POWER_PLANTS_REPORT.md).

Current implementation: the existing project publishes six GeoJSONs and three metadata files, including 32 optional point-only candidates and 1,070 uncounted polygon representatives after source QA. The original three-file MVP examples below describe the starting stage; use [the current data dictionary](docs/DATA_DICTIONARY.md) and [matching policy](docs/SUBSTATION_MATCHING.md) for the complete contract. The current UI has one default-closed Layers control inside a full-width map, with persistent layer choices, contextual symbols and folded voltage/status filters. The separate sidebar and Legend button were removed. Counts remain in cards/list. See [LAYERS_CONTROL_REFACTOR.md](docs/LAYERS_CONTROL_REFACTOR.md). Planned-data gaps remain in About; no speculative unused planned-asset interface is required. Follow [README](README.md#filters-and-legend) and [the simplification report](docs/SIMPLIFICATION_REPORT.md) for current UI/cleanup verification. The original source-selection predicates and data-integrity invariants remain unchanged. Do not deploy without user authorization.

**Project state:** Vue 3 + Vite + TypeScript is **already installed** in the repository. This guide supersedes the earlier prompt that assumed a new repo and Cloudflare Pages hosting.

**Target:** a functioning, static-first WebGIS deployed to **Vercel**, using the selected electricity-transmission spatial assets from `IDN.gpkg`. Do **not** start by scaffolding another Vue project. Do **not** implement Deliverable 1 or Deliverable 3.

## 0. Mandatory reading and input checks

Read, in order:
1. `AGENTS.md` (coding and data-integrity constraints).
2. `docs/DATA_FILTER_SPEC.md` (exact filtering logic, output schema and counts).
3. `docs/VERIFIED_DATA_AUDIT.md` (checked source attributes and caveats).
4. The original ToR and license, **if copied to the repo**, e.g. `docs/references/ToR_MENTARI_Grids.docx` and `docs/references/License.pdf`.
5. Inspect current `package.json`, lockfile, `src/`, current UI/styles/config and actual `data/raw/IDN.gpkg` before modifying anything.

If the GeoPackage is not present at `data/raw/IDN.gpkg`, stop data processing with a precise message about what is missing; don't fetch or make up replacement features. You can create skeleton code without generating fake output data. Do not publish the ToR or any internal reference documents to `public/`.

## 1. Authoritative functional scope

The MENTARI Grids Terms of Reference defines **Deliverable 2** as the inventory of **existing and planned transmission lines and substations, by power system, region and voltage level, with spatial layers where available**. It explicitly includes existing 70/150/275/500 kV HVAC lines, overhead/submarine/underground assets, GI/GITET, and future RUPTL 2025–2034/RUKN 2025–2060 projects including HVDC and converter stations.

The provided OSM/OpenInfraMap GeoPackage is **not** a complete approved grid registry. It does not reliably provide planned-RUPTL records, official electrical-system grouping, verified operational status, commissioning year, transformer MVA, circuit-km, thermal rating, or AIS/GIS type. Build UI extension points for these data **later**. Do not infer official status or region/system membership from the source geometries.

**Current MVP includes:**
- filtered transmission line segments (target voltage values only);
- high-confidence OSM-tagged transmission substation polygons;
- an explicitly labeled optional layer of substation candidates awaiting validation;
- filters, map, searchable feature details, honest asset counts/QA and attribution.

**Current MVP excludes:** towers, individual power generators, individual transformers, telecom, water, pipeline/petroleum layers, all non-target lines, point substations unless later validated; it does **not** invent planned spatial features.

## 2. Execution plan — implement in this order

### Phase A — inspect existing repo and data
- Record current package manager from lockfile (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`); do not switch package managers.
- Check existing Vue version and build scripts; keep existing working scaffold.
- Check the input GeoPackage with a Python GIS reader: layer names, CRS, geometry types, fields, nulls, status flags, and counts.
- Create an implementation checklist and compare verified numbers against `docs/VERIFIED_DATA_AUDIT.md`.
- Ensure `.gitignore` excludes the original `data/raw/IDN.gpkg`, venvs and processed intermediates.

### Phase B — data processing FIRST
Implement a CLI `scripts/prepare_data.py` with a companion `scripts/requirements.txt` (or a clearly documented equivalent). Suggested command:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py --input data/raw/IDN.gpkg --output public/data --qa-output data/qa
```

Make the CLI robust to missing inputs, different working directories and encoding. Use the exact classifications and output schema in `docs/DATA_FILTER_SPEC.md`.

Output **only filtered, publication-suitable datasets** to `public/data/`:

```text
public/data/
  transmission-lines.geojson        # all 4,374 in-scope lines; tagged statuses retained
  substations-primary.geojson       # 622 tagged transmission polygons of target voltage
  substations-review.geojson        # 448 clearly flagged review candidates, OPTIONAL toggle
  summary.json                      # computed counts/coverage, no hardcoded values
  data-catalog.json                 # provenance, field meanings, limitations
  qa-report.json                    # reproducible aggregate QA and excluded categories
```

Keep internal review artifacts **outside `public/`**, e.g. `data/qa/substation-points.geojson` for 68 points, `data/qa/exclusion-report.json` and any ambiguous high-voltage categories. Never silently drop records without an exclusion/review reason. Prefer not to publish complete raw tables or unneeded attributes.

**Before UI development, run:**
- raw layer/CRS/validity checks;
- count assertions for 4,374 lines, 622 primary substations, 448 review candidates;
- flag assertions: target lines 4,345 unflagged, 25 construction, 4 disused; primary substation 621 unflagged, 1 construction;
- no duplicate `feature_id`, no geometry null/empty/invalid, no published line outside 70/150/275/500 kV;
- check output size and valid GeoJSON/WGS84 coordinate order (longitude, latitude);
- verify source raw file was not modified.

If a source count has changed, **show the changed source finding** instead of forcing it to match historic expected counts.

### Phase C — frontend implementation
Work within the existing `src/` tree. Suggested modules (adapt to what's already there):

```text
src/
  components/
    AppHeader.vue
    MapLayersControl.vue
    MapCanvas.vue
    AssetDetailsDrawer.vue
    InventorySummary.vue
    DataProvenanceDialog.vue
  composables/useAssetFilters.ts
  services/assetData.ts
  types/assets.ts
  utils/filterAssets.ts
  utils/formatAssets.ts
  App.vue
```

- Install only necessary packages; `maplibre-gl` is expected. Existing Tailwind/PrimeVue may be used if already installed; otherwise avoid overengineering. Make the page polished with plain CSS if sufficient.
- Fetch the three small GeoJSONs from `/data/...` once; choose lazy loading for `substations-review.geojson` until user explicitly enables candidate layer.
- Add MapLibre GeoJSON sources/layers (lines classified by target kV, primary substation polygon fill/outline, optional review polygons with distinct stroke). Select a lawful, correctly attributed basemap; keep URL configurable via `VITE_BASEMAP_STYLE_URL` if needed. Provide a clear failure state if map assets fail.
- Default visible **line** category: the 4,345 `not_flagged_in_osm` records at 70/150/275/500 kV (never label them verified/operational). Optional controls to reveal 25 under-construction and 4 disused lines.
- Default visible **substation** category: 621 `not_flagged_in_osm` primary polygons, with one `construction=true` polygon under a separate optional construction toggle. Candidate polygons remain OFF by default.
- Provide voltage checkbox/multiselect for 500, 275, 150, 70 kV, search by name/ref/OSM source id/operator, asset-type toggles, tagged-status filter, legend and reset controls.
- KPI counts must derive from current filtered datasets or `summary.json`, NOT copied into Vue components. Label them **line segments** and **substation polygons** (not verified stations/corridors). Distinguish `selected records` from `features visible in current map viewport`.
- On click, open a detail drawer with available source values, normalized voltage, `source_id`, operator, `location`, circuits (if present), derived geometry length (if computed) and data-quality badges. Display `Not available` for unknown values. Clearly label a synthetic `display_name` as just an interface fallback.
- Provide an `About data` panel explaining OpenStreetMap source, data coverage, unverified operation, pending planned-RUPTL/RUKN assets, and ODbL attribution. Do not expose the original ToR or sensitive/licensed data through `/public`.
- Make mobile and desktop responsive; include loading, missing-file, and empty-filter states. Avoid fetching huge datasets or adding extra map libraries.

### Phase D — test, build, document and deploy
- Unit-test voltage parsing, subset selection, construction/disused status and fallback labels; integration/smoke-test map loading, filters, search, popups and candidate toggles.
- Verify data selection counts against the actual generated JSON, not merely the initial audit.
- Run the **existing package manager's** type-check/test/build scripts, or add minimal scripts as needed. A typical Vite app builds to `dist/`.
- Update **existing** `README.md` and create `docs/DATA_DICTIONARY.md`, `docs/DATA_COVERAGE_AND_LIMITATIONS.md`, `docs/DEPLOYMENT.md`, `docs/ARCHITECTURE.md` with actual implementation details and test results.
- Vercel: import current GitHub repository; framework Vite (auto-detected), build `npm run build` (or relevant existing package-manager equivalent), output `dist`. Ensure every `public/data/*` URL resolves in production and browser refresh works if client-side routing was introduced. Do not commit API keys.
- Verify source/attribution text and map-provider license, e.g. `© OpenStreetMap contributors` and appropriate ODbL reference. Publishing a derivative database can carry further ODbL obligations; verify reuse/redistribution requirements prior to public release.
- No PostGIS, Docker, backend server, Cloudflare R2, PMTiles, analytics service or login required for MVP.

## 3. ToR-to-feature traceability

| ToR Deliverable 2 requirement | MVP state | Codex behavior |
|---|---|---|
| Existing transmission lines by voltage | Partial via OSM | Filter exact target voltages; show source-tagged status, not official operation |
| Existing substations GI/GITET | Partial via OSM | Separate primary and review candidates; avoid false certainty |
| Existing assets by power system and region | Not in GPKG | No fabricated filter/options; document missing crosswalks/boundaries |
| Planned lines/substations under RUPTL/RUKN | Not identified in GPKG | Prepare empty interface/schema only; show `Data not yet provided` |
| HVDC/submarine/underground | `location` sometimes available, HVDC not verified | Display only original attributes; don't declare actual HVDC projects |
| Capacity, MVA, COD, circuit-km, AIS/GIS, costs | Mostly absent | Show `Not available` rather than imputing values |
| Source log/data dictionary | Required for usable inventory | Generate provenance, QA and documentation |

## 4. Definition of done

The first release is complete only when:
- The **original Vue + Vite + TS app** still builds, with no unnecessary re-scaffolding.
- Running the documented preprocessing command on the supplied GeoPackage reproducibly generates the filtered data and QA output.
- All three exported GeoJSONs contain the expected subsets, valid geometry, stable IDs, correct fields and proper attribution metadata.
- The real map displays default-filtered lines and primary substations, and filters/search/details really work.
- Candidate substations and source construction/disused flags are visually **separate and unambiguous**.
- No planned RUPTL/RUKN data or system/region membership is fabricated.
- Type checking, automated tests and production build pass (or blockers are clearly reported).
- Vercel deployment instructions are accurate for the existing repo; code contains no secret or raw GPKG.

## 5. Paste into Codex chat (single instruction)

> Read `AGENTS.md`, `CODEX_START_HERE.md`, `docs/DATA_FILTER_SPEC.md`, and `docs/VERIFIED_DATA_AUDIT.md`. This repository **already contains Vue 3 + Vite + TypeScript**: inspect and reuse the existing setup; do not scaffold it again. Implement MENTARI Grids Deliverable 2 incrementally, **starting with the Python GeoPackage filtering pipeline**. Run and validate the exported subsets and QA counts before implementing the real MapLibre dashboard, then tests, production build and Vercel documentation. Use actual data only; never invent source attributes, official operational status, electrical system/region assignments or planned RUPTL/RUKN projects. Do the implementation, not just an implementation plan. Report files changed, exact outputs/counts, commands executed and remaining gaps.
