# Maintenance guide

Start with [README](README.md) for setup and controls, [AGENTS.md](AGENTS.md) for constraints, and the [filter specification](docs/DATA_FILTER_SPEC.md) / [source audit](docs/VERIFIED_DATA_AUDIT.md) for data rules. This application is already implemented; no scaffolding is needed.

## Frontend changes

Inspect the relevant Vue component and shared state before editing. Filtering lives in `useAssetFilters` and pure utilities; the map, table, metrics and Layers panel consume that selection. Keep derived symbols separate from original records.

Run `pnpm test`, `pnpm build` and relevant `pnpm test:e2e` scenarios. Update the existing documentation page that owns the changed behavior. Do not add UI history or per-change implementation reports.

## Data changes

1. Obtain the supplied `data/raw/IDN.gpkg` and inspect its fields, CRS, flags and geometry. The source license is local; the original ToR has not been supplied.
2. Run the [README preprocessing setup](README.md#regenerate-data). CLI paths resolve from the repository regardless of the working directory. Defaults are `data/raw/IDN.gpkg`, `public/data/` and `data/qa/`.
3. Generate into a temporary publication directory first:
   ```powershell
   .\.venv\Scripts\python.exe scripts/prepare_data.py --output data/interim/publication --qa-output data/qa
   ```
4. Review QA and compare with `scripts/expected-audit.json` and `scripts/expected-power-plant-audit.json`. Mismatches report exact expected/actual values and stop before publication writes. `--allow-source-mismatch` is an explicit override after investigating a legitimate new source; it does not hide differences.
5. Run the Python tests, regenerate all nine publication files together, then run frontend validation. Keep `public/data/** -text` in .gitattributes: generated UTF-8/CRLF bytes and catalog hashes must survive Git checkout unchanged.

Internal QA includes exclusions, status conflicts, source points and complete point/polygon matching reports. It is not a static asset. Individual publication files are replaced atomically; the nine-file set must be reviewed and committed together.

## QGIS Python fallback on Windows

An installed QGIS GIS environment can replace the virtual environment. Adjust the installation paths to your machine; this repository has been tested with:

```powershell
$env:PYTHONHOME='C:/Program Files/QGIS 3.44.15/apps/Python312'
$env:PYTHONIOENCODING='utf-8'
$env:GDAL_DATA='C:/Program Files/QGIS 3.44.15/apps/gdal/share/gdal'
$env:PROJ_DATA='C:/Program Files/QGIS 3.44.15/share/proj'
$env:PATH='C:/Program Files/QGIS 3.44.15/bin;'+$env:PATH
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' scripts/prepare_data.py
& 'C:/Program Files/QGIS 3.44.15/bin/python.exe' -m unittest discover -s scripts -p 'test_*.py' -v
```

Do not commit raw data, internal QA, reference documents or environment files. [Deployment](docs/DEPLOYMENT.md) is a separate, explicitly authorized action.
