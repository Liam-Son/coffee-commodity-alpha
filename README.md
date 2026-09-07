# Coffee Commodity Alpha

Finding alpha in coffee prices as a commodity market – research, data analysis, signals, and trading strategies.

## Focus Areas

- Weather & climate impacts on yields (primary supply driver)
- Production forecasts vs market expectations
- Seasonality, stocks, and demand dynamics
- Quantitative signals and backtesting
- Comparative climate risk in related beverage crops (tea)
- Weather index derivatives & parametric insurance

## Research Notes

- [Weather Impact on Coffee Yields](research/weather-impact-on-coffee-yields.md)
- [Climate Change Impact on Tea](research/climate-change-impact-on-tea.md)
- [Quantitative Weather–Yield: Coffee vs Tea](research/quantitative-weather-yield-coffee-vs-tea.md)
- [Weather Index Derivatives & Parametric Insurance](research/weather-index-derivatives-and-parametric-insurance.md)

## Quantitative Pipeline

- **Index construction**: [src/weather_indices.py](src/weather_indices.py)
- **Models**: [src/yield_price_models.py](src/yield_price_models.py)
- **Inference**: [src/block_bootstrap.py](src/block_bootstrap.py)
- **Real weather data**: [src/weather_data.py](src/weather_data.py) ← Open-Meteo ERA5
- **Backtester**: [src/backtest.py](src/backtest.py)

## First Strategy (now with real weather)

```bash
pip install yfinance pandas numpy matplotlib requests
python strategies/weather_stress_long.py
```

- Default: **real** Open-Meteo ERA5 weather for Sul de Minas
- Builds EHD (Tmax ≥ 33 °C) + precipitation anomaly → composite stress
- Long when stress high, light short when stress low
- Outputs performance table + equity chart

See [notebooks/04_real_weather_integration.md](notebooks/04_real_weather_integration.md) for details.

## Structure

```
├── research/          # Literature notes
├── notebooks/         # Pipeline & strategy docs
├── src/               # Indices, models, weather data, backtest, loaders
├── strategies/        # Signal definitions
├── data/              # (to be populated)
└── artifacts/         # Generated charts (local)
```

## Key Insight

Coffee yields (especially Arabica) are highly sensitive to weather extremes. Quantifying nonlinear heat and moisture effects — and testing their incremental value for price forecasting — is central to generating alpha.

Real weather data is now integrated so stress signals are driven by actual ERA5 temperature and precipitation rather than synthetic placeholders.
