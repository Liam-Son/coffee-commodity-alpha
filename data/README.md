# Data provenance

This folder holds *notes and schemas*, not vendor dumps.

## Series used by the engine test

| Series | Vendor | Access | Stored in git? |
|--------|--------|--------|----------------|
| Daily Tmax / Tmin / precip at 5 BR points | Open-Meteo archive (ERA5) | HTTP, no key (non-commercial) | No |
| KC=F daily close | Yahoo Finance via `yfinance` | HTTP | No |

## Series specified but not yet ingested

| Series | Intended source | Used for |
|--------|-----------------|----------|
| Brazil Arabica yield / production | CONAB; IBGE SIDRA | RQ2 yield regressions |
| Stocks / USDA WASDE revisions | USDA FAS / PSD | Price-model controls |
| Front-month KC with explicit roll | Exchange calendar + Barchart/QI | Research-grade futures |
| Municipal weather weights | CONAB area or IBGE planted area | Production-weighted stress |

## Attribution

- ERA5: Copernicus Climate Change Service (C3S) / ECMWF.
- Access layer: Open-Meteo (https://open-meteo.com), CC BY 4.0.
- Futures: ICE Arabica (KC) as redistributed by Yahoo Finance; not an official ICE series.

## Ethical / legal

Do not commit raw vendor extracts if the licence forbids redistribution. Cache locally under `data/raw/` (gitignored).
