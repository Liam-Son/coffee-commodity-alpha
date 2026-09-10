# Reproducibility

## Environment

- Python ≥ 3.11
- See `pyproject.toml` / `requirements.txt` for pinned *minimum* versions.
- For a frozen environment, after a successful run:

```bash
pip freeze > requirements.lock.txt
```

Commit that lockfile only when you intend to freeze a paper-submission snapshot.

## Seeds

| Component | Seed | Location |
|-----------|------|----------|
| Synthetic stress (demo only) | 42 | `src/data_loaders.py` |
| Moving-block bootstrap | 42 (default) | `src/block_bootstrap.py` |
| Unit tests | 0 | `tests/test_backtest.py` |

ERA5 pulls and KC=F downloads are deterministic *conditional on vendor revisions*. Reanalysis and Yahoo adjustments can change after the fact. Record `download_date` in any paper table.

## Data that is **not** in git

- Raw ERA5 extracts (regenerate via `src/weather_data.py`)
- KC=F history (regenerate via `src/data_loaders.load_coffee_futures`)

Reason: vendor licences and file size. See `data/README.md`.

## How to reproduce the registered engine test

```bash
pip install -e ".[dev]"
pytest -q
python strategies/weather_stress_long.py
```

Expected qualitative pattern (not bit-identical levels, because vendors revise):

- Strategy Sharpe near 0.4, BH Sharpe near 0.4
- Strategy MaxDD materially smaller than BH
- Strategy CAGR below BH
- Time-in-market well below 50%

If you obtain CAGR *above* BH with the *same* thresholds, treat that as a data-revision event and document the download date.

## Network

Tests under `tests/` do **not** require network access.  
The engine test **does**.

## Licence constraints

Open-Meteo historical API is free for non-commercial use under CC BY 4.0 for the underlying ERA5 fields (attribution: Copernicus / ECMWF via Open-Meteo). Commercial use requires checking current Open-Meteo terms.
