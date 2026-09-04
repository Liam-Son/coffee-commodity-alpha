# Quantitative Pipeline: Weather Indices → Yield Response → Price Models

**Steps 1–3 implemented as a reproducible research pipeline**

This document + accompanying Python modules define:

1. **Extreme-heat-day + soil-moisture indices** for Brazil (coffee), Kenya & Assam (tea)
2. **Simple yield response functions** using public yield + ERA5-style weather
3. **Tests of whether weather anomalies improve short-term price models**

---

## 1. Index Definitions

### Extreme Heat Days (EHD)

Count of days where daily maximum temperature exceeds a crop-specific threshold during critical periods.

| Region / Crop | Threshold | Critical window (approx.) |
|---------------|-----------|---------------------------|
| Brazil Arabica | Tmax ≥ 33 °C (strict) or ≥ 35 °C (severe) | Sep–Dec (flowering / early fruit set) + Jan–Mar (bean filling) |
| Kenya Tea | Tmax ≥ 27–30 °C (regional) or ≥ 35 °C | Main flush periods (varies; often prioritise dry-season heat) |
| Assam Tea | Tmax ≥ 32–34 °C or monthly mean > 26.6 °C | Growing season, especially pre-monsoon and monsoon |

**Construction**
- Daily Tmax from ERA5 / ERA5-Land (or equivalent reanalysis).
- Aggregate to monthly or seasonal sums of EHD.
- Also compute growing-degree-days (GDD) and harmful-degree-days (HDD) for Brazil coffee (blooming stage focus).

### Soil Moisture / Drought Proxy

- ERA5 volumetric soil water (layer 1 or root-zone equivalent) or derived drought indices.
- Alternatives: consecutive dry days, SPEI, or precipitation anomaly during key windows.
- For Kenya: emphasise soil moisture in the months preceding main flushes.
- For Assam: pre-monsoon and monsoon rainfall anomalies + VPD.

### Composite Stress Index (optional)

Simple interaction or principal-component style index:
`Stress = f(EHD_anomaly, SoilMoisture_anomaly, VPD_anomaly)`
Standardise each component (z-score) before combining.

---

## 2. Data Sources (Public / Free)

**Weather**
- ERA5 / ERA5-Land via Copernicus CDS (cds.climate.copernicus.eu) or Google Earth Engine / Microsoft Planetary Computer
- Variables: `2m_temperature`, `maximum_2m_temperature_since_previous_post_processing`, `total_precipitation`, `volumetric_soil_water_layer_1` (or equivalent)
- Bounding boxes (approximate):
  - Brazil coffee (Minas Gerais focus): ~14°S–23°S, 40°W–50°W
  - Kenya tea highlands: ~0.5°S–1.5°S, 35°E–38°E
  - Assam: ~24°N–28°N, 89°E–96°E

**Yields / Production**
- Brazil coffee: CONAB historical series + IBGE SIDRA (municipality/state level preferred)
- Kenya tea: Tea Board of Kenya / KNBS / FAOSTAT
- Assam / India tea: Tea Board of India, Assam DES statistical handbooks, FAOSTAT

**Prices**
- ICE Arabica (KC) continuous or front-month futures (daily/monthly)
- Sources: FRED (PCOFFOTMUSDM or similar), Macrotrends, exchange data, Yahoo Finance continuous contracts
- Tea: limited liquid futures; use auction averages (Guwahati, Mombasa) or export unit values as proxies where needed

---

## 3. Yield Response Functions (Step 2)

**Basic specification (log or level)**

```
log(Yield_t) = α + β1 · EHD_t + β2 · SM_t + β3 · EHD_t × SM_t
               + γ · Controls_t + ε_t
```

Controls can include:
- Lagged yield (biennial bearing for coffee)
- Linear / quadratic time trend
- Seasonal dummies if using sub-annual data

**Expected signs (from literature)**
- β1 (EHD) < 0
- β2 (soil moisture) > 0 (or drought index < 0)
- Interaction: heat damage amplified under low soil moisture

Estimate separately for:
- Brazil Arabica (or Minas Gerais subset)
- Kenya tea
- Assam tea

Use Newey-West or HAC standard errors if serial correlation is present.

---

## 4. Price Model Tests (Step 3)

**Baseline price model**
```
Δ log(P_t) = α + Σ φ_i · Δ log(P_{t-i}) + θ · Δ log(Stocks or SupplyProxy)_t + ε_t
```

**Augmented model**
```
Δ log(P_t) = α + Σ φ_i · Δ log(P_{t-i}) + θ · SupplyProxy_t
             + λ1 · EHD_anomaly_t + λ2 · SM_anomaly_t + ε_t
```

**Evaluation**
- Compare in-sample adjusted R² / AIC / BIC
- Out-of-sample RMSE or directional accuracy (hit rate)
- Diebold-Mariano or encompassing tests if formal comparison desired
- Check whether weather variables remain significant after controlling for reported production revisions / USDA or CONAB estimates

Focus windows: 1–6 months ahead (matching typical weather-to-harvest lags).

---

## 5. Implementation Notes

See `src/weather_indices.py` and `src/yield_price_models.py` for starter code.

Recommended workflow:
1. Download / cache ERA5 monthly or daily aggregates for the three regions.
2. Construct EHD and soil-moisture series aligned to crop calendars.
3. Merge with annual (or higher-frequency) yield series.
4. Estimate yield response regressions.
5. Merge weather anomalies with coffee futures (and tea price proxies).
6. Run baseline vs weather-augmented price models and compare performance.

---

## 6. Next Concrete Actions

- [ ] Authenticate with Copernicus CDS and pull ERA5 for the three bounding boxes
- [ ] Build clean yield panels (Brazil state/municipality, Kenya national + key counties, Assam)
- [ ] Implement index construction functions
- [ ] Fit and diagnose yield models
- [ ] Build monthly price + weather dataset and test predictive content

*Pipeline designed September 2026*
