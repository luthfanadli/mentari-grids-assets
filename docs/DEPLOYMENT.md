# Vercel deployment

The repository builds a static Vite app. Preprocessed data is committed; deployment needs no Python, GeoPackage, database or serverless function. Deployment is a separate authorized action.

## Build settings

| Setting | Value |
| --- | --- |
| Framework / root | Vite / repository root |
| Runtime | Node 24, pnpm 12 |
| Install | `pnpm install --frozen-lockfile` |
| Build | `pnpm build` |
| Output | `dist` |
| Optional public variable | `VITE_BASEMAP_STYLE_URL` |

`vercel.json` defines build settings and revalidation for stable `/data/` filenames. There is no router or catch-all rewrite; missing data URLs must fail normally. Never put private secrets in Vite public variables.

## Before deployment

Run `pnpm test` and `pnpm build`. Commit the complete nine-file `public/data/` set with its catalog and `.gitattributes`. The build validates bytes, checksums, versions, counts and symbol-parent linkage before compilation.

Generated JSON/GeoJSON has canonical UTF-8/CRLF bytes. `public/data/** -text` prevents Git newline conversion. A one-byte size/checksum failure can indicate older LF-normalized data paired with a CRLF catalog: regenerate the complete dataset using the documented pipeline and retain the attributes rule. Do not bypass the guard. Node tests verify staging and Windows/Linux checkout byte preservation.

`.gitignore` excludes raw/QA data and secrets; `.vercelignore` also excludes root `/data/`, environments, tests and private references from CLI uploads. The leading slash leaves `public/data/` included.

## Verify locally

```powershell
pnpm.cmd preview --host 127.0.0.1 --port 5175 --strictPort
```

In a second terminal:

```powershell
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5175'
# Optional: use installed Edge instead of Playwright Chromium.
$env:PLAYWRIGHT_CHANNEL='msedge'
pnpm.cmd test:e2e
```

The same suite can target an authorized Vercel preview by changing the base URL. It covers real map rendering, source flags/search/details, candidate loading/retry, overview-to-footprint transitions, deduplicated counts, basemap changes, persistent Layers while panning/zooming and responsive widths.

## Preview checks

- Default counts: 4,345 lines, 621 primary polygons, 633 plants, zero candidate records.
- All nine data URLs return JSON/GeoJSON with catalog-matching bytes; the MapLibre worker and real overlays load.
- Optional candidates and construction/disused flags remain separate. Point voltage and plant output units remain unknown.
- Search `-18678451` opens GITET Pedan with its original signed ID and geometry.
- Layers, extent/basemap controls, details, About, mobile scrolling and retry/fallback states work. Source/license/provider credits stay visible.
- Refresh works; data revalidates. Raw GPKG, references, internal QA and secrets are absent from the build.

The app fetches static data publicly even without download controls. External basemaps require provider availability and applicable usage terms; Google Satellite uses the supplied direct endpoint rather than a Map Tiles API session integration. Local tests do not verify a hosted account, domain, deployment protection or CDN settings.
