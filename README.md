# Coffee Commodity Alpha

**Working paper repository** for quantitative research on weather-driven supply risk and price discovery in Arabica coffee futures.

This is an *empirical research codebase*, not a trading product. Headline backtest numbers are **not** claims of tradable alpha. They document a reproducible pipeline from reanalysis weather → lagged stress indices → futures positions → risk-adjusted performance, with explicit identification assumptions and limitations.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Research questions

1. **RQ1 (measurement).** Can publicly available reanalysis weather (ERA5) be aggregated into a coffee-relevant stress index (extreme heat + drought) for the Brazilian Arabica belt?
2. **RQ2 (yield channel).** Do those indices enter yield-response functions with the theoretically expected signs (heat negative, moisture positive, interaction amplifying heat damage)?
3. **RQ3 (price channel).** Does lagged weather stress contain incremental information for ICE Arabica (KC) returns after controlling for own lags and a simple supply proxy?
4. **RQ4 (risk transfer).** Can the same indices serve as underlyings for parametric insurance / weather-derivative structures, and how large is basis risk?
5. **RQ5 (portfolio overlay).** Conditional on a lagged weather signal, does a simple long/short overlay with EWMA volatility targeting improve *risk-adjusted* characteristics relative to unlevered buy-and-hold? (Not: does it beat BH on raw CAGR.)

Formal hypotheses, identification, and threats to validity: [`docs/RESEARCH_DESIGN.md`](docs/RESEARCH_DESIGN.md).

---

## What this repository is — and is not

| This repository **is** | This repository **is not** |
|------------------------|----------------------------|
| A reproducible measurement + inference + backtest pipeline | A claim of statistically significant tradable alpha |
| An identification-aware research design | A complete PhD dissertation |
| Honest about look-ahead, basis risk, and sparse signals | A substitute for CONAB/IBGE yield panels or official crop calendars |
| A starting point for a job-market / thesis chapter | Production trading infrastructure |

The 2015–2025 engine test finds a **higher Sharpe and lower max drawdown** than buy-and-hold under a *sparse* weather overlay, and **lower raw CAGR**. That pattern is consistent with a selective risk-on overlay, not with a dominant alpha process. See [`results/engine_test_2015_2025.md`](results/engine_test_2015_2025.md) and [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

---

## Latest registered engine test (2015–2025, KC=F)

| Metric | Vol-target 10% | No vol target | Buy & hold |
|--------|----------------|---------------|------------|
| CAGR | +1.8% | +5.8% | +12.7% |
| Volatility | 4.6% | 13.0% | 33.6% |
| Sharpe | 0.40 | 0.45 | 0.38 |
| Max drawdown | −14.8% | −29.9% | −51.9% |
| Hit rate | 14.2% | 14.2% | 49.4% |
| Terminal multiple | 1.21× | 1.72× | 2.17× |
| Time long / short / flat | 8.9% / 19.3% / 71.7% | same signal | 100% long |

Pre-registered caveats: continuous contract (no official roll), single-country weather, uncalibrated weights, no multiple-testing correction, no walk-forward in the headline table.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python strategies/weather_stress_long.py
```

Requirements: Python 3.11+, network access for Open-Meteo (ERA5) and Yahoo Finance (KC=F).

---

## Repository map

```
coffee-commodity-alpha/
├── docs/                 Research design, methodology, limitations, identification
├── research/             Literature notes (weather–yield, tea comparison, parametric insurance)
├── src/                  Measurement, models, inference, backtest
├── strategies/           Runnable signal + execution layer
├── tests/                Unit tests (no network required)
├── results/              Registered engine-test outputs
├── notebooks/            Pipeline walkthroughs
├── data/                 Provenance notes only (raw series not committed)
├── CITATION.cff          How to cite this work
└── pyproject.toml        Package metadata and dependencies
```

### Core modules

| Module | Role |
|--------|------|
| `src/weather_data.py` | Multi-point ERA5 fetch; EHD / HDD / precip anomaly; lagged stress |
| `src/weather_indices.py` | Index library (thresholds, GDD, composite stress) |
| `src/yield_price_models.py` | Yield-response OLS + HAC; baseline vs weather-augmented price models |
| `src/block_bootstrap.py` | Moving-block bootstrap SEs and percentile CIs |
| `src/backtest.py` | Vectorized execution, costs, EWMA vol targeting |
| `src/robustness.py` | Threshold / lag / vol-target sensitivity helpers |
| `src/evaluation.py` | Deflated Sharpe, hit-rate, turnover, exposure |

---

## Identification in one paragraph

Weather is treated as **predetermined** relative to next-month futures returns after a **one-month publication lag**. Positions use **next-bar execution**. Volatility weights are lagged one day. This blocks contemporaneous look-ahead from weather *measurement*, but does **not** identify a causal treatment effect of weather on prices: KC embeds global supply, inventories, USD, positioning, and news. The object of inference is *incremental predictive content* of a Brazilian weather-stress proxy, not a structural supply elasticity.

---

## Academic documents

- [Research design](docs/RESEARCH_DESIGN.md) — questions, hypotheses, identification, threats
- [Methodology](docs/METHODOLOGY.md) — data, indices, models, bootstrap, backtest protocol
- [Limitations](docs/LIMITATIONS.md) — what a referee will attack first
- [Reproducibility](docs/REPRODUCIBILITY.md) — seeds, versions, data licences
- [Robustness protocol](docs/ROBUSTNESS.md) — pre-specified sensitivity grid
- [Literature notes](research/)

---

## Citation

If you use this repository, please cite the CITATION.cff file or:

> Son, L. (2026). *Coffee Commodity Alpha: weather-stress measurement and futures overlays* (working paper repository). https://github.com/Liam-Son/coffee-commodity-alpha

---

## Licence

Code: MIT (see `LICENSE`).  
Weather data: Open-Meteo / ERA5 — CC BY 4.0; attribution required.  
Price data: Yahoo Finance terms of use apply; series are **not** redistributed in this repo.

---

Lab status: [STATUS.md](STATUS.md)
