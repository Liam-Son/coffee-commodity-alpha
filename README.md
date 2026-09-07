# Coffee Commodity Alpha

Finding alpha in coffee prices as a commodity market – research, data analysis, signals, and trading strategies.

## Focus Areas

- Weather & climate impacts on yields (primary supply driver)
- Production forecasts vs market expectations
- Seasonality, stocks, and demand dynamics
- Quantitative signals and backtesting
- Comparative climate risk in related beverage crops (tea)
- Weather index derivatives & parametric insurance

## Latest Engine Test (2015–2025)

| Metric | Vol-Target 10% | No Vol Target | Buy & Hold |
|--------|----------------|---------------|------------|
| CAGR | +1.8% | +5.8% | +12.7% |
| Vol | 4.6% | 13.0% | 33.6% |
| Sharpe | 0.40 | **0.45** | 0.38 |
| MaxDD | **−14.8%** | −29.9% | −51.9% |
| Final $1→ | 1.21× | 1.72× | 2.17× |

Full write-up: [results/engine_test_2015_2025.md](results/engine_test_2015_2025.md)

```bash
pip install yfinance pandas numpy matplotlib requests
python strategies/weather_stress_long.py
```

## Research Notes

- [Weather Impact on Coffee Yields](research/weather-impact-on-coffee-yields.md)
- [Climate Change Impact on Tea](research/climate-change-impact-on-tea.md)
- [Quantitative Weather–Yield: Coffee vs Tea](research/quantitative-weather-yield-coffee-vs-tea.md)
- [Weather Index Derivatives & Parametric Insurance](research/weather-index-derivatives-and-parametric-insurance.md)

## Pipeline

- **Real weather**: [src/weather_data.py](src/weather_data.py) — Open-Meteo ERA5, 5-point Brazil average
- **Indices / models / bootstrap**: `src/weather_indices.py`, `yield_price_models.py`, `block_bootstrap.py`
- **Backtester + EWMA vol targeting**: [src/backtest.py](src/backtest.py)
- **Strategy**: [strategies/weather_stress_long.py](strategies/weather_stress_long.py)

## Structure

```
├── research/          # Literature notes
├── notebooks/         # Pipeline docs
├── src/               # Data, indices, models, backtest
├── strategies/        # Runnable signals
├── results/           # Engine test outputs
└── artifacts/         # Local charts
```

## Key Insight

Coffee yields (especially Arabica) are highly sensitive to weather extremes. A lagged, multi-point weather-stress signal with EWMA volatility targeting produces better risk-adjusted characteristics than buy-and-hold, at the cost of lower absolute return under a conservative 10% vol target.
