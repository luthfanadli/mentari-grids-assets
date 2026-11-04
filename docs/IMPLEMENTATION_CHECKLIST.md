# Deliverable 2 implementation checklist

- [x] Preserve the existing Vue 3 / Vite / TypeScript project and pnpm lockfile.
- [x] Inspect the supplied GeoPackage and license; preserve the private original unchanged.
- [x] Validate exact transmission-line and primary/review polygon predicates against the source audit.
- [x] Audit all 68 points against 2,753 polygons; retain complete QA and publish 32 optional unvalidated points.
- [x] Publish six GeoJSONs plus three metadata files, with original geometries and stable IDs.
- [x] Keep 1,070 derived polygon symbols outside inventory totals; retain overview/footprint transitions.
- [x] Keep optional candidate layers independently lazy, retryable and off by default.
- [x] Simplify Layers, Voltage and OSM status controls; remove static sidebar totals.
- [x] Derive legend items from matching original records; separate line colors from status patterns.
- [x] Handle unknown voltage, empty searches, optional layers and construction-tagged substations in the key.
- [x] Remove confirmed unused demo component/assets, speculative interface and obsolete CSS.
- [x] Update every project Markdown document and validate local documentation links.
- [x] Run 16 Node tests, Vue/TypeScript checks, production build and ten production-browser scenarios.
- [x] Inspect/publish 643 original power-plant footprints, preserve source units as unknown and add independent markers/counts.
- [x] Verify power-plant toggle, grid-voltage independence, status/search, marker clicks, footprints, retry and basemap switching.
- [x] Preserve attribution, font license, audit evidence, dataset hashes and existing deployment configuration.

The 30,412,800-byte source retains SHA-256:
`6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`.
Raw source counts remain 5,396 lines, 2,753 substation polygons, 68 substation points and 643 power-plant footprints across 26 layers.
Published totals are 4,374 lines, 622 primary polygons, 448 review polygons, 32 optional points and 643 power-plant footprints.
The 1,070 representative symbols are not additional inventory records.

The current full source-dependent Python suite passed 19 tests, including exact plant geometry/attributes, representative containment, unknown output-unit guards and source audit.
Current plant audit, commands, sizes, checks and remaining gaps: [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md). No deployment or push occurred.
