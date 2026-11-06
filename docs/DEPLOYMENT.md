# Vercel deployment

The repository has a Vercel Vite configuration. No hosted deployment was created during implementation or the substation enhancement. The enhancement explicitly does not deploy or change hosting configuration; the notes below describe preparation for a future authorized deployment.

## Prepare the repository

1. Run preprocessing locally on the supplied private GeoPackage, then verify `pnpm check:data`, `pnpm test` and `pnpm build`.
2. Include all nine generated files under `public/data/` together: five original-record inventory/review GeoJSONs, one representative-symbol GeoJSON and three metadata files. Python and the raw data must not be fetched during a Vercel build. Full point-matching evidence/CSV stays under ignored root `data/qa/`.
3. Keep `data/raw/`, `data/qa/`, virtual environments, `.env*`, restricted references and secrets excluded. `.gitignore` protects local source/QA; `.vercelignore` also excludes root `/data/` for CLI uploads. The leading slash is intentional: **`public/data/` remains included**. Do not upload the original ToR or license PDF.
4. Include `.gitattributes` **and all nine `public/data/` files in the same commit**. These generated files use canonical UTF-8/CRLF bytes to retain the original catalog hashes. The `-text` rule prevents Git from normalizing those bytes. When adding this rule to an older checkout, use `git add .gitattributes` and `git add --renormalize public/data/` to refresh already-tracked files; adding the rule alone does not restore bytes already normalized in an earlier commit. The Python writer explicitly emits the same bytes on Windows and Linux.

If the data guard reports `6151921` actual versus `6151922` expected bytes for `transmission-lines.geojson`, the older commit contains LF-normalized data but Windows-generated catalog hashes. All five GeoJSONs lose one byte this way. Restore the original generated files and commit them with the attributes rule; keep the strict byte/checksum checks enabled. The Git round-trip regression in `pnpm test` verifies staged bytes and clean checkouts with both `core.autocrlf=false` and `true`. See [the build-fix report](BUILD_FIX_GIT_LINE_ENDINGS.md).

## Import the existing repository

Import this GitHub repository into the intended Vercel account/project. Use its existing Vue/Vite source and pnpm lockfile.

| Setting | Value |
| --- | --- |
| Framework preset | Vite |
| Root directory | Repository root |
| Node | 24.x recommended; implementation tested with 24.19.0 |
| Install command | `pnpm install --frozen-lockfile` |
| Build command | `pnpm build` |
| Output directory | `dist` |
| Optional environment | `VITE_BASEMAP_STYLE_URL` = public style URL, otherwise leave unset |

The local package manager was pnpm 12.4.1; retain the checked-in lockfile and confirm the selected pnpm version in Vercel's install log. Build dependencies include TypeScript/Vue type checking. The build first validates data versions, checksums and counts and fails for missing/tampered publication files; it does not need Python or `IDN.gpkg`.

The default OSM raster style needs no token. A custom style's public token, if any, must be restricted according to that provider's rules; never put a private secret into a `VITE_` variable. Confirm service terms and visible attribution for any replacement provider. See the [official Vercel Vite guide](https://vercel.com/docs/frameworks/frontend/vite), [MapLibre Vite worker setup](https://maplibre.org/maplibre-gl-js/docs/), and [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/).

No client-side router is used. The app is served at `/`; no catch-all rewrite is configured. This also lets absent `/data/` files fail normally instead of returning index HTML. Existing data paths use `Cache-Control: public, max-age=0, must-revalidate`, with normal hosting compression. Data filenames are stable, so do not set immutable year-long caching on them.

## Verify a preview deployment before production promotion

- `/` loads with 4,345 line segments, 621 primary polygons, 633 power-plant footprints and zero review candidates under the defaults.
- All nine `/data/...` paths return JSON/GeoJSON, matching the catalog checksums. The map fetches these public assets directly; the About download section and dataset links have been removed. Removing those controls does not restrict access to the static data URLs. Derived symbols are not inventory records.
- `/assets/` includes the bundled MapLibre worker; the map actually renders features, rather than only initializing a canvas. Construction/disused flags and review candidates have separate styles and controls.
- Search `-18678451` to find the source's `GITET Pedan` polygon; details retain the negative ID and original multi-voltage tag. Test list selection and clicking the zoomed footprint.
- Enable construction/disused and verify the resulting 4,374 lines and 622 primary polygons. Enable review and verify 448 separate candidates; their source distribution/unknown tags remain visible in details.
- Enable point-only candidates and verify 32 separate records with unknown voltage, with primary/review polygon counts unchanged. Both candidate layers are initially off. At overview zoom, click a representative symbol to inspect the original polygon; zoom 10 and above must show footprints instead of those symbols. Selected-record counts must stay constant through zoom changes. Matched/uncertain raw points must not appear as additional records.
- Open Layers inside the full-width map. Check all five choices remain available when off or empty; Voltage and OSM status start folded. Opening Layers must not fetch candidates. Exercise Reset, whole-row clicks/taps, internal scrolling, Escape/outside-map dismissal, focus restoration and basemap switching. Pan, wheel-zoom and use native zoom buttons with Layers open, then toggle another layer without reopening it. Verify full-width cards/search/map/table at laptop and large-screen widths. Test mobile at 320 px, About, retries and basemap failure. OSM/ODbL and provider attribution must remain visible.
- Refresh `/` and inspect the Network panel: review must not download before it is enabled; no raw GPKG, internal point layer or restricted reference document is served. Stable data requests should revalidate after a deployment.

The existing Playwright suite can target a Vercel preview without launching a local dev server:

```powershell
$env:PLAYWRIGHT_BASE_URL='https://your-preview-domain.vercel.app'
# Optional if using an installed Edge browser:
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e
```

Local production verification uses `pnpm preview --host 127.0.0.1 --port 5175` and the eleven-scenario suite with that local base URL. Check that Layers starts closed, keeps all five choices available when off/empty, and combines voltage colors and source-status patterns without a separate sidebar or legend. Matching counts remain in the cards/list. Current interaction results are in [LAYERS_CONTROL_REFACTOR.md](LAYERS_CONTROL_REFACTOR.md); schema-v3 publication/source QA remains in [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md) and `SUBSTATION_ENHANCEMENT_REPORT.md`. Local verification does not verify a future Vercel account, domain, protection setting or CDN response.

## Updating the source later

Run preprocessing locally, review exact audit differences, matching evidence and exclusions, and keep all nine outputs together. The source-version override is explicit; do not edit the historic expected audit merely to make changes disappear. Add authoritative planned assets or region/system membership only when a properly sourced dataset/crosswalk is supplied and reviewed. Keep provenance and ODbL notices with derivatives. This enhancement does not authorize any hosting action.
