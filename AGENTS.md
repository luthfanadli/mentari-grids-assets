# Codex Repository Instructions — MENTARI Grids D2

## Context
This is an **existing Vue 3 + Vite + TypeScript** repository. DO NOT scaffold Vue/Vite again, replace `package.json`, regenerate the lockfile unnecessarily, or rewrite the app without inspecting the current project.

Build **MENTARI Grids — Transmission Asset Inventory** for **Deliverable 2 only**. Read `CODEX_START_HERE.md`, `docs/DATA_FILTER_SPEC.md` and `docs/VERIFIED_DATA_AUDIT.md` before making changes. Read the actual source ToR and license if present under `docs/references/`. Inspect the real `data/raw/IDN.gpkg` before implementing the pipeline.

## Invariants
1. Data provenance first. NEVER invent grid features, verified operational status, RUPTL/RUKN planned projects, COD, official circuit-km, capacity, power-system membership or official province attribution.
2. Stage the work: **inspect raw data -> implement & test preprocessing -> run it -> verify counts/QA -> implement UI -> build/test -> document Vercel deployment**.
3. Preserve original GeoPackage unchanged and gitignore `data/raw/`, Python virtual environments, temporary files and secrets.
4. Filter at preprocessing time. Publish only the intended lines, substation datasets and user-authorized power-plant context dataset to `public/data/`; do not load or deploy all 26 GeoPackage layers.
5. The default WebGIS represents a **preliminary OSM-based inventory**. `construction=false` and `disused=false` mean **not flagged**, not independently verified existing/operational.
6. Only `500, 275, 150, 70 kV` are in the default transmission-voltage scope; numeric source `max_voltage` is in **volts**. Use `max_voltage / 1000` strictly for display.
7. Distinguish substations selected by explicit transmission tags from substations needing manual validation. Review candidates are OFF by default.
8. Substation polygons, not individual transformers or power plants, form the primary substation layer. Point substations require QA first.
9. Honor OSM/ODbL attribution. Do not expose the original ToR, restricted BNEF material or other potentially internal reference documents as static assets.
10. Keep the interface in English, accessible and responsive. Make real functionality work before extra styling. No backend, database, PMTiles or object storage for this MVP unless profiling proves necessary.

## Development and reporting
- Reuse the package manager and lockfile already in the repository.
- New frontend dependencies should be few and justified (MapLibre GL JS is expected).
- Implement the deterministic filter and metadata scripts in Python (GeoPandas/Pyogrio or Fiona, Shapely and PyProj are appropriate).
- Add programmatic tests for counts, voltage normalization, status categorization and candidate selection.
- Show exact QA differences rather than silently updating expected counts.
- Update the existing README and provide `docs/DATA_DICTIONARY.md`, `docs/DATA_COVERAGE_AND_LIMITATIONS.md` and `docs/DEPLOYMENT.md` as implementation outputs.
- Final Codex report must state changed files, output sizes/counts, commands executed, test/build results, and remaining ToR gaps.

## Current UI and maintenance
- Follow the current [Layers and filter behavior](README.md#filters-and-legend): one in-map Layers panel, no sidebar or standalone legend. Keep all five layer choices available, including when off/empty; derive contextual swatches and counts from matching original records. See [LAYERS_CONTROL_REFACTOR.md](docs/LAYERS_CONTROL_REFACTOR.md).
- Power plants are user-authorized context: publish source footprints, preserve output units as unknown, and keep them independent of grid voltage filters. Do not import generator layers or infer MW/COD/connections. See [the plant report](docs/POWER_PLANTS_REPORT.md).
- Keep line-voltage colors separate from source-status patterns. Candidate layers stay optional/default-off, and missing voltage never becomes an inferred value.
- Retain data/source QA and historical evidence during cleanup. Remove confirmed unused demo assets/styles/types; do not recreate starter components or speculative planned records. See [the cleanup report](docs/SIMPLIFICATION_REPORT.md).
