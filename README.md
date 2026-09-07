# Coffee Commodity Alpha

Finding alpha in coffee prices as a commodity market – research, data analysis, signals, and trading strategies.

## Focus Areas

- Weather & climate impacts on yields (primary supply driver)
- Production forecasts vs market expectations
- Seasonality, stocks, and demand dynamics
- Quantitative signals and backtesting
- Comparative climate risk in related beverage crops (tea)
- Weather index derivatives & parametric insurance (risk transfer, basis risk, product design)

## Research Notes

- [Weather Impact on Coffee Yields](research/weather-impact-on-coffee-yields.md)
- [Climate Change Impact on Tea](research/climate-change-impact-on-tea.md)
- [Quantitative Weather–Yield: Coffee vs Tea](research/quantitative-weather-yield-coffee-vs-tea.md)
- [Weather Index Derivatives & Parametric Insurance](research/weather-index-derivatives-and-parametric-insurance.md)

## Quantitative Pipeline (Steps 1–3)

- **Pipeline overview**: [notebooks/01_weather_yield_price_pipeline.md](notebooks/01_weather_yield_price_pipeline.md)
- **Index construction**: [src/weather_indices.py](src/weather_indices.py) – Extreme Heat Days, GDD/HDD, soil-moisture anomalies, composite stress
- **Models**: [src/yield_price_models.py](src/yield_price_models.py) – Yield response functions + baseline vs weather-augmented price models
- **Inference**: [src/block_bootstrap.py](src/block_bootstrap.py) – Moving Block Bootstrap (residual & pairs) with percentile CIs and block-length robustness
- **Bootstrap usage**: [notebooks/02_block_bootstrap_usage.md](notebooks/02_block_bootstrap_usage.md)

### What the pipeline does
1. Builds extreme-heat-day and soil-moisture indices for Brazil (coffee), Kenya & Assam (tea)
2. Estimates simple yield response functions (EHD + soil moisture + interaction)
3. Tests whether weather anomalies improve short-term coffee price models (AIC/BIC, adj. R², out-of-sample)
4. Provides both HAC (Newey–West) and Moving Block Bootstrap inference for short samples

## First Strategy & Backtest Framework

- **Strategy**: [strategies/weather_stress_long.py](strategies/weather_stress_long.py) – long KC when stress proxy is elevated
- **Backtester**: [src/backtest.py](src/backtest.py)
- **Data loaders**: [src/data_loaders.py](src/data_loaders.py) (KC=F + synthetic stress placeholder)
- **Walk-through**: [notebooks/03_first_strategy_backtest.md](notebooks/03_first_strategy_backtest.md)

```bash
pip install yfinance pandas numpy matplotlib
python strategies/weather_stress_long.py
```
Produces a performance table and an equity-curve chart.  
**Important**: the current stress series is synthetic (demo only). Replace it with real weather indices for meaningful results.

## Structure

```
├── research/          # Literature notes and findings
├── notebooks/         # Pipeline documentation & analysis
├── src/               # Reusable code (indices, models, bootstrap, backtest, loaders)
├── strategies/        # Signal definitions and backtests
├── data/              # (to be populated) Raw & processed datasets
└── artifacts/         # Generated charts / outputs (local)
```

## Key Insight

Coffee yields (especially Arabica) are highly sensitive to weather extremes. Quantifying nonlinear heat and moisture effects — and testing their incremental value for price forecasting — is central to generating alpha. Tea provides a useful comparative climate-risk benchmark.

Weather-index derivatives and parametric insurance form the practical risk-transfer layer: the same indices that drive yield and price models can underpin insurance products and synthetic hedges, subject to careful management of basis risk.
