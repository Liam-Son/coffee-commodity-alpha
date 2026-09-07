# First Strategy + Backtest Framework

**Weather-stress long/short strategy on Arabica coffee futures (KC)**

## Goal
Clean, runnable skeleton that produces a real equity curve and performance table.  
Synthetic stress is used only so the framework can be validated end-to-end.  
Real weather indices will replace it later.

## Components

| File | Role |
|------|------|
| `src/data_loaders.py` | KC=F daily prices (yfinance) + improved seasonal synthetic stress |
| `src/backtest.py` | Vectorized long/flat (or long/short) backtester + stats |
| `strategies/weather_stress_long.py` | Long when stress high, light short when stress low |

## How to run

```bash
# from repo root
pip install yfinance pandas numpy matplotlib
python strategies/weather_stress_long.py
```

Output:
1. Annualised performance table (Strategy vs Buy & Hold)
2. Equity-curve chart saved to `artifacts/stress_ls_equity.png`

### Chart panels (easy to check)
- **Top** – Growth of $1 (log scale): Stress L/S vs Buy & Hold KC
- **Middle** – Stress index with long (green) and short (purple) thresholds
- **Bottom** – Position over time (−0.5 / 0 / +1)

## Strategy logic (current demo)

- **Long (+1)** when stress > 1.2
- **Light short (−0.5)** when stress < −0.2
- Flat otherwise
- Next-bar execution, 5 bp cost on turnover

Synthetic stress includes:
- Higher base level in Brazil frost window (May–Aug) and flowering period (Sep–Dec)
- Realised volatility component
- Occasional strong positive shocks

## Important caveat

Because the stress series is still synthetic, the performance numbers are **not** evidence of alpha.  
They only prove that the backtest plumbing works.

## Next upgrades (priority)

1. Replace `synthetic_stress()` with real EHD / soil-moisture / composite indices from `src/weather_indices.py`.
2. Enforce proper publication lag (weather observed in month *t* only affects positions from month *t+1*).
3. Add volatility targeting or risk-parity sizing.
4. Walk-forward or simple train/test split.
5. Optional: switch from continuous KC=F to a proper front-month roll series.
