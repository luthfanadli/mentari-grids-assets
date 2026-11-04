# Vercel deployment

The repository has a Vercel Vite configuration. No hosted deployment was created during implementation or the substation enhancement. The enhancement explicitly does not deploy or change hosting configuration; the notes below describe preparation for a future authorized deployment.

## Prepare the repository

1. Run preprocessing locally on the supplied private GeoPackage, then verify `pnpm check:data`, `pnpm test` and `pnpm build`.
2. Include all eight generated files under `public/data/` together: four inventory/review GeoJSONs, one representative-symbol GeoJSON and three metadata files. Python and the raw data must not be fetched during a Vercel build. Full point-matching evidence/CSV stays under ignored root `data/qa/`.
3. Keep `data/raw/`, `data/qa/`, virtual environments, `.env*`, restricted references and secrets excluded. `.gitignore` protects local source/QA; `.vercelignore` also excludes root `/data/` for CLI uploads. The leading slash is intentional: **`public/data/` remains included**. Do not upload the original ToR or license PDF.

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

- `/` loads with 4,345 line segments, 621 primary polygons and zero review candidates under the defaults.
- All eight `/data/...` paths return JSON/GeoJSON, matching the catalog checksums. Download the four original inventory/review datasets and separate representative symbols through About. Derived symbols are not inventory records.
- `/assets/` includes the bundled MapLibre worker; the map actually renders features, rather than only initializing a canvas. Construction/disused flags and review candidates have separate styles and controls.
- Search `-18678451` to find the source's `GITET Pedan` polygon; details retain the negative ID and original multi-voltage tag. Test list selection and clicking the zoomed footprint.
- Enable construction/disused and verify the resulting 4,374 lines and 622 primary polygons. Enable review and verify 448 separate candidates; their source distribution/unknown tags remain visible in details.
- Enable point-only candidates and verify 32 separate records with unknown voltage, with primary/review polygon counts unchanged. Both candidate layers are initially off. At overview zoom, click a representative symbol to inspect the original polygon; zoom 10 and above must show footprints instead of those symbols. Selected-record counts must stay constant through zoom changes. Matched/uncertain raw points must not appear as additional records.
- Test a narrow mobile viewport, keyboard navigation, About dialog, empty search, retries and basemap failure. OSM/ODbL and map-provider attribution must remain visible.
- Refresh `/` and inspect the Network panel: review must not download before it is enabled; no raw GPKG, internal point layer or restricted reference document is served. Stable data requests should revalidate after a deployment.

The existing Playwright suite can target a Vercel preview without launching a local dev server:

```powershell
$env:PLAYWRIGHT_BASE_URL='https://your-preview-domain.vercel.app'
# Optional if using an installed Edge browser:
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e
```

Local production verification uses `pnpm preview --host 127.0.0.1 --port 5175` and the same five-scenario suite with that local base URL. Current results are in `SUBSTATION_ENHANCEMENT_REPORT.md`; the initial MVP also verified actual OSM tiles. Local verification does not verify a future Vercel account, domain, protection setting or CDN response.

## Updating the source later

Run preprocessing locally, review exact audit differences, matching evidence and exclusions, and keep all eight outputs together. The source-version override is explicit; do not edit the historic expected audit merely to make changes disappear. Add authoritative planned assets or region/system membership only when a properly sourced dataset/crosswalk is supplied and reviewed. Keep provenance and ODbL notices with derivatives. This enhancement does not authorize any hosting action.
