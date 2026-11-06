# Repository instructions — MENTARI Grids D2

This is an existing Vue 3 + Vite + TypeScript application. Inspect and reuse it; do not scaffold, replace package.json or regenerate the pnpm lockfile unnecessarily.

Read [the maintenance guide](CODEX_START_HERE.md), [filter specification](docs/DATA_FILTER_SPEC.md) and [source audit](docs/VERIFIED_DATA_AUDIT.md) before changes. Inspect the real GeoPackage before changing preprocessing. Read source ToR/license documents if present; keep them outside public assets.

## Data invariants

- Never invent features, operational status, planned RUPTL/RUKN projects, COD, capacity, circuit-km, electrical connectivity or official region/system membership.
- Preserve the source GeoPackage unchanged. Keep raw data, QA, virtual environments, secrets and restricted references out of publication.
- Read only the four approved spatial layers. Select lines by numeric max_voltage in {70000, 150000, 275000, 500000} volts; divide by 1000 for display only.
- Keep 622 primary substation polygons distinct from 448 review polygons and 32 optional point candidates. Candidate layers are off by default. Missing-voltage points never enter primary inventory.
- Matching must evaluate all source points against all raw polygons. Intersection/proximity/ID equality alone does not prove duplicate identity or supply voltage.
- Publish source power-plant footprints as separate generation context. Do not import individual generators or infer output units, MW, COD or connections.
- Not flagged means neither construction nor disused is tagged where those fields exist; it does not verify operation.
- Preserve original IDs, geometry, source attribution and ODbL notices. Derived symbols reuse parent IDs and never inflate statistics.

## Development

Use the existing pnpm scripts and Python GIS pipeline. For data changes: inspect source, update/test preprocessing, generate to a temporary directory, review exact QA differences, then update all nine publication files together. Do not weaken checksum checks or silently rewrite expected audit fixtures.

Keep the English UI accessible and responsive. Maintain one in-map Layers panel, persistent off/empty choices, independent candidate loading, and separate inventory/viewport counts. Preserve map-interaction and keyboard behavior.

Keep dependencies few. No backend, database, object store or PMTiles without demonstrated need. Deployment requires user authorization.

Maintain the focused documents linked from README; update facts in their owning document instead of adding repetitive change reports. Remove confirmed unused code/assets while retaining provenance, audit fixtures, reproducible matching and meaningful tests.

Run relevant tests and the production build. Final reports should state changes, commands/results, unchanged or changed data counts/sizes, and unresolved scope gaps.
