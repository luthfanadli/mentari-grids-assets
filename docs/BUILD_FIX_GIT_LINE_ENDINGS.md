# Build fix: publication bytes changed by Git — 4 November 2026

Later user-authorized extension: [POWER_PLANTS_REPORT.md](POWER_PLANTS_REPORT.md) documents 643 plant footprints, nine-file/schema-v3 publication and current tests. The stage-specific counts, hashes and UI descriptions below are preserved as history; the five earlier GeoJSONs and raw source remain unchanged.

Current status: the byte-preserving Git/serialization fix below remains active. The later sidebar/legend and unused-file cleanup leaves all eight data files and checksums unchanged; its current test counts are in [SIMPLIFICATION_REPORT.md](SIMPLIFICATION_REPORT.md). Historical build-fix results below describe that earlier stage.

The Vercel build failure in commit `5d1c0a2` is reproducible directly from its Git blobs. `scripts/check_public_data.mjs:24` rejects a line GeoJSON of **6,151,921 bytes**, while the catalog expects **6,151,922 bytes**. This occurs before Vue/TypeScript/Vite compilation.

## Confirmed cause

The original Python JSON writer used platform-dependent text-mode newlines. Windows generated CRLF files and computed their byte counts/SHA-256 hashes. Git's `core.autocrlf=true`, without an overriding attributes rule, stored LF-normalized content. Vercel then checked out those normalized bytes. Each compact GeoJSON has one trailing newline, so conversion removes exactly one byte:

| GeoJSON | Broken committed bytes | Original/catalog bytes |
| --- | ---: | ---: |
| Lines | 6,151,921 | 6,151,922 |
| Primary polygons | 646,265 | 646,266 |
| Review polygons | 450,634 | 450,635 |
| Point-only candidates | 36,375 | 36,376 |
| Representative symbols | 490,829 | 490,830 |

Adding CR back before the final LF in each original commit blob reproduces its catalog SHA-256 exactly. This establishes newline conversion as the cause; no geographic data corruption or Node version change is needed to explain the failure. The exact original assertion was reproduced under local Node 24.19.0 as well as the supplied Vercel log's Node 26.13.0.

## Fix

- Added `.gitattributes` with `/public/data/** -text whitespace=cr-at-eol`. Git now preserves all eight publication files as exact bytes, independent of checkout newline settings. This does not disable JSON diffs or integrity checks.
- Restored the original publication bytes in the working files so the next commit includes them. Their differences from the old Git blobs are line endings only; JSON values, geometries, attributes, IDs, metadata, counts and catalog hashes are unchanged.
- Changed `scripts/prepare_data.py:write_json` to write explicit UTF-8/CRLF bytes on every OS. CRLF is intentional here: it preserves the already audited export fingerprints rather than changing the catalog or baseline expectations. JSON string values containing escaped newlines remain intact.
- Added a Python compact/pretty/unicode serialization regression in `scripts/test_prepare_data.py`.
- Added `tests/unit/publication-git.test.ts`. It first reproduces the one-byte loss in a temporary Git repository, applies the fix and restages the data, then verifies exact staged and checked-out bytes under both `core.autocrlf=false` and `true`. Both checkouts execute the unchanged production publication guard.
- Updated `README.md` and `docs/DEPLOYMENT.md` with the serialization policy and commit requirements. Added this report.

The strict size and SHA-256 assertions in `scripts/check_public_data.mjs` remain unchanged. No dependencies, lockfile, Node setting, source audit fixture, filter predicate, UI or hosting configuration changed for this fix. Existing uncommitted dashboard documentation edits were retained.

## Commit together

The attributes rule alone cannot repair an LF blob already stored in an older commit. Include **`.gitattributes` and all eight restored `public/data/` files** in the same next commit, alongside the writer/test/documentation changes. For an existing index, these commands explicitly refresh the data:

```powershell
git add .gitattributes
git add --renormalize public/data/
```

This fix has not created a commit, pushed or triggered a deployment. No original GeoPackage or internal QA file should be staged. The working publication files have been refreshed so their restored bytes are visible as modified files in Git.

## Verification

| Check | Result |
| --- | --- |
| Reproduce failure using original HEAD blobs | **Confirmed**, same 6,151,921/6,151,922 assertion |
| Node tests, including real Git round trip | **11 passed**, no skips |
| Python real-source suite, including serialization | **16 passed**, no skips, 46.960 s |
| Current working-tree `pnpm.cmd build` | **PASS**, publication guard + Vue/TypeScript + Vite |
| Fresh snapshot checkout with `core.autocrlf=false` | **PASS**, publication guard + Vue/TypeScript + Vite |
| Preprocessing with updated writer | **PASS**, zero source-audit differences |
| All eight regenerated files vs original working exports | **Byte-identical** |
| `git diff --ignore-space-at-eol --exit-code -- public/data` | **PASS**, no data/content changes from old HEAD |
| Raw source SHA-256 | **Unchanged** |
| `git diff --check` | **PASS** |

The clean snapshot staged the current source and fixed publication files into an isolated Git repository and extracted a fresh checkout with automatic newline conversion disabled. Its build reused the installed dependencies from this workspace; it did not perform a Linux-hosted build or a Vercel redeployment. An initial snapshot `pnpm build` attempted automatic dependency installation and encountered the environment's restricted network; the verification then ran the same three build steps directly with the existing Vue/TypeScript/Vite executables. The resulting build passed. No dependency installation or lockfile update was needed for the fix.

Commands executed include:

```powershell
pnpm.cmd test
pnpm.cmd build
# QGIS Python environment variables as documented in README:
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p 'test_*.py' -v
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py --output data/qa/build-fix-regenerated-public --qa-output data/qa/build-fix-regenerated-qa

# Same build steps, from the isolated Git checkout, using installed dependencies:
node scripts/check_public_data.mjs
node 'C:/IESR/MENTARI Grids/mentari-grids-assets/node_modules/vue-tsc/bin/vue-tsc.js' -b
node 'C:/IESR/MENTARI Grids/mentari-grids-assets/node_modules/vite/bin/vite.js' build

git diff --ignore-space-at-eol --exit-code -- public/data
git diff --check
Get-FileHash -LiteralPath data/raw/IDN.gpkg -Algorithm SHA256
```

The restored outputs remain 4,374 line segments, 622 primary polygons, 448 review polygons, 32 optional point-only candidates and 1,070 uncounted representative symbols. Five GeoJSONs total **7,776,029 bytes**; all eight publication files total **7,800,419 bytes**. The current local production build totals **9,734,065 bytes**, including the static assets from the latest commit, with the existing nonfatal MapLibre chunk-size warning. Publication counts and sizes are also detailed in [the dashboard report](DASHBOARD_UX_UPDATE.md).

Raw source fingerprint remains `6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba`. Original line, primary and review hashes remain `1eed102bced3ca67d00660f764ee83eb608ba32239f5ba4e11ca06f6b3858c98`, `930c23abd342797b27fd71435a3c7d32c5b838f06619206a7159df8bfaf6613f` and `e14432b41e7ce80def0f8edb3c5e0ac25b80ef6860129096cee071631522f038` respectively.

Planned RUPTL/RUKN data, official system/region membership and other source gaps are unaffected. See [the substation report](SUBSTATION_ENHANCEMENT_REPORT.md) for the remaining ToR/data limitations.
