# First Strategy + Backtest Framework

**Minimal weather-stress long strategy on Arabica coffee futures (KC)**

## Goal
Provide a clean, runnable skeleton so we can produce a real equity curve and performance table, then swap in genuine weather indices.

## Components

| File | Role |
|------|------|
| `src/data_loaders.py` | Load KC=F daily prices (yfinance) + synthetic stress placeholder |
| `src/backtest.py` | Vectorized long/flat backtester + performance stats |
| `strategies/weather_stress_long.py` | First strategy: long when stress > threshold |

## How to run

```bash
# from repo root
pip install yfinance pandas numpy matplotlib
python strategies/weather_stress_long.py
```

This will:
1. Download daily KC=F from 2015 onward
2. Build a **synthetic** monthly stress series (demo only)
3. Go long when stress > 1.0, otherwise flat
4. Apply 5 bp transaction costs on turnover
5. Print CAGR / Vol / Sharpe / MaxDD / Hit-Rate for strategy vs buy-and-hold
6. Save an equity-curve chart to `artifacts/first_strategy_equity.png`

## Sample output (framework demo)

Because the stress series is synthetic/random, the strategy is **not** expected to beat buy-and-hold. Typical demo numbers look roughly like:

```
         CAGR    Vol  Sharpe  MaxDD  HitRate
Strategy 0.03   0.14    0.22  -0.30     0.09
BuyHold  0.13   0.34    0.38  -0.52     0.49
```

The chart shows:
- Top panel: growth of $1 (strategy vs buy-and-hold)
- Middle: stress index with the 1.0 threshold line
- Bottom: position (0/1)

## Next upgrades (in priority order)

1. **Replace synthetic stress** with real output from `src/weather_indices.py` (EHD, soil-moisture anomaly, composite stress) once ERA5 / yield data are loaded.
2. Add lag alignment so that weather observed in month *t* only affects positions from month *t+1* onward (no look-ahead).
3. Test alternative thresholds, long/short versions, and volatility targeting.
4. Move from daily continuous futures to a proper front-month roll series if desired.
5. Add walk-forward or simple out-of-sample split.

## Design principles

- Signal is lagged by one bar → realistic next-day execution.
- Costs are applied on absolute position change.
- Everything is vectorized and dependency-light.
- The same `run_backtest` function can accept any future signal (price-based, weather-based, or hybrid).
