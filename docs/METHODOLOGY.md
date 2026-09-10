# Methodology

## 1. Weather data

**Source.** Open-Meteo Historical Weather API wrapping ERA5 / ERA5-Land reanalysis.  
**Variables.** Daily `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`.  
**Licence.** CC BY 4.0; attribution required.  
**Spatial units.** Five representative points:

| Key | Lat, Lon | Belt |
|-----|----------|------|
| sul_de_minas | -21.55, -45.43 | Southern Minas Gerais |
| sul_minas_2 | -21.15, -44.95 | Southern Minas Gerais |
| cerrado_mineiro | -18.92, -46.99 | Cerrado |
| cerrado_2 | -19.45, -46.55 | Cerrado |
| mogiana | -22.25, -46.75 | Mogiana |

Daily fields are **equal-weighted averages** across points. This is a transparency choice, not an optimal spatial estimator.

## 2. Index construction

### Extreme Heat Days (month $m$)

$$
\mathrm{EHD}_m = \sum_{d \in m} \mathbf{1}\{T^{\max}_d \ge 31^{\circ}\mathrm{C}\}
$$

The 31 °C threshold is a *research default* after a 33 °C cutoff produced too few events (30 days in 11 years at a single point). It is not a plant-physiology constant.

### Harmful Degree Days

$$
\mathrm{HDD}_m = \sum_{d \in m} \max(T^{\max}_d - 30, 0)
$$

### Precipitation anomaly

Monthly precipitation $P_m$ is standardised against a trailing 12-month mean and standard deviation (minimum 6 months):

$$
A_m = \frac{P_m - \bar{P}_{m,12}}{s_{m,12}}
$$

### Composite stress (pre-lag)

$$
S_m = 0.35\, z(\mathrm{EHD}_m) + 0.25\, z(\mathrm{HDD}_m) + 0.40\, (-A_m)
$$

then clipped to $[-2.5, 4]$ and **shifted by one month**.

Weights are a priori, not estimated on KC returns. Estimating them on the same sample used for the backtest would be in-sample overfitting.

## 3. Price data

Daily continuous KC=F close from Yahoo Finance, auto-adjusted.  
**Known defect:** this is not a research-grade roll-adjusted front-month series. Results that depend on roll returns should be treated as provisional.

## 4. Yield and price econometrics

Implemented in `src/yield_price_models.py`.

**Yield (intended specification)**

$$
\log Y_t = \alpha + \beta_1 \mathrm{EHD}_t + \beta_2 \mathrm{SM}_t + \beta_3 (\mathrm{EHD}_t \times \mathrm{SM}_t) + \gamma' C_t + \varepsilon_t
$$

Inference: Newey–West HAC (`maxlags=2`) and moving-block bootstrap (Künsch 1989 style overlapping blocks).

**Price models**

- Baseline: $\Delta \log P_t$ on own lags (default 3) ± supply proxy.
- Augmented: baseline + weather columns.
- Comparison: AIC, BIC, adjusted $R^2$.

These functions are *library code*. They do not run in the headline engine test because an official yield panel is not in `data/`.

## 5. Overlay protocol

1. Align lagged monthly $S_m$ onto the daily KC calendar by forward-fill.
2. Signal: $+1$ if $S > 0.8$; $-0.4$ if $S < -0.6$; else $0$.
3. Optional EWMA vol weight:

$$
\hat{\sigma}_t = \sqrt{252 \cdot \mathrm{Var}^{\mathrm{EWMA}}_{\lambda}(r_{1:t-1})}, \qquad
w_t = \mathrm{clip}\!\left(\frac{\sigma^\star}{\hat{\sigma}_t}, 0.25, 2\right)
$$

with span 30 ($\lambda \approx 0.94$) and $\sigma^\star = 10\%$ in the registered test.

4. Position $_t = (\mathrm{signal}_t \cdot w_t)$ applied at $t+1$.
5. Costs: 5 basis points times absolute position change.

## 6. Performance statistics

Annualisation factor 252.  
Sharpe uses *arithmetic* mean / std of daily returns × $\sqrt{252}$ — the conventional industry definition, not the log-utility version.  
Max drawdown is computed on the compounded equity path.

Deflated Sharpe is implemented in `src/evaluation.py` for robustness tables; it is **not** the headline number.
