# Real Weather Data Integration

## Overview

Weather data is now pulled live from the **Open-Meteo Historical Weather API** (ERA5 / ERA5-Land reanalysis). No API key required for non-commercial use.

### Source
- Endpoint: `https://archive-api.open-meteo.com/v1/archive`
- Variables: daily `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`
- Coverage: 1940–present, global

### Regions configured
| Key | Location | Approx. area |
|-----|----------|--------------|
| `sul_de_minas` | -21.55, -45.43 | Southern Minas Gerais (core Arabica) |
| `cerrado_mineiro` | -18.92, -46.99 | Cerrado Mineiro |
| `mogiana` | -22.25, -46.75 | Mogiana belt |

## New modules

- `src/weather_data.py` – fetch daily weather, compute EHD, precip anomaly, composite stress
- `src/data_loaders.py` – unified `load_stress(price, source="real"|"synthetic")`

## Stress construction (real)

```
monthly EHD = count of days with Tmax ≥ 33 °C
precip anomaly = z-score of monthly precipitation vs recent history
stress = 0.6 · z(EHD) + 0.4 · (−precip_anomaly)
```

Higher stress = more extreme heat + drier conditions.

## Run the strategy with real weather

```bash
pip install yfinance pandas numpy matplotlib requests
python strategies/weather_stress_long.py
```

By default it now uses `source="real"` and `region="sul_de_minas"`.

To force synthetic (for comparison):

```python
from strategies.weather_stress_long import main
main(source="synthetic")
```

## Important notes

1. **Point vs area** – current implementation uses a single representative lat/lon. For production, average several points or use a gridded extract.
2. **Publication lag** – monthly stress is forward-filled; for true no-lookahead research you should lag by one month.
3. **Thresholds** – 33 °C EHD and the 0.6/0.4 weights are starting points from the research notes; calibrate against yield data later.
4. **Rate limits** – Open-Meteo is free for non-commercial use; be polite with request volume.

## Next steps

- Multi-point or bounding-box aggregation for Sul de Minas
- Add soil-moisture if available from ERA5-Land via Open-Meteo
- Proper month-lag for live trading signals
- Link stress directly to the original `weather_indices.py` functions
