# Research Design

**Status:** working paper design note  
**Last updated:** 2026-09-10

## 1. Motivation

Arabica coffee yields are nonlinearly sensitive to heat and moisture during flowering and bean filling. Brazil accounts for a dominant share of globally traded Arabica. ICE KC futures are the liquid claim on that supply. If weather stress is (i) measurable with public reanalysis, (ii) lagged relative to harvest and price discovery, and (iii) only partially embedded in contemporaneous prices, then a *lagged* weather-stress index can have incremental content for returns, volatility, and risk premia.

This is an *economics / agricultural finance* question, not a machine-learning leaderboard problem.

## 2. Research questions and hypotheses

### RQ1 — Measurement
**H1.** A multi-point average of ERA5 Tmax and precipitation over the Brazilian Arabica belt produces Extreme Heat Day (EHD) and precipitation-anomaly series with economically plausible seasonal concentration in May–August (frost / winter stress windows) and September–March (flowering / filling).

### RQ2 — Yield channel
**H2a.** In a log-yield regression, $\beta_{\text{EHD}} < 0$, $\beta_{\text{SM}} > 0$.  
**H2b.** The interaction $\text{EHD} \times \text{SM}$ is negative (heat damage larger under drought).

*Status:* specification implemented (`estimate_yield_response`); **not yet estimated on official CONAB/IBGE panels** in this repository.

### RQ3 — Price channel
**H3.** Adding lagged weather anomalies to a baseline $\Delta \log P_t$ model (own lags + supply proxy) improves AIC/BIC and/or out-of-sample RMSE.

*Status:* specification implemented (`price_baseline`, `price_augmented`, `compare_models`); **not yet estimated on a merged official panel**.

### RQ4 — Risk transfer
**H4.** Basis risk between the constructed index and farm-level (or municipal) yield is material; hedging effectiveness is strictly less than one.

*Status:* literature and product mapping complete; pricing / basis-risk estimation is future work.

### RQ5 — Overlay
**H5.** A lagged threshold rule on the stress index, with next-bar execution and costs, produces **higher Sharpe and/or lower max drawdown** than unlevered KC buy-and-hold over 2015–2025, even if raw CAGR is lower.

*Status:* tested. Point estimates support H5 on Sharpe (0.45 vs 0.38 without vol targeting) and MaxDD; **reject** any claim of CAGR dominance. No bootstrap *p*-value on the Sharpe difference is reported in the headline table — that is a registered gap.

## 3. Identification strategy

### 3.1 What is identified

We identify **predictive association** of *lagged Brazilian weather stress* with subsequent KC returns under a timing restriction:

- Weather for calendar month $t$ is only allowed to affect positions from month $t+1$ onward (`lag_months=1`).
- Positions are applied at $t+1$ relative to the signal bar (`position_lag=1`).
- EWMA volatility is estimated on past returns and shifted one day.

This is **not** an IV / natural-experiment design for $\partial P / \partial W$.

### 3.2 Why weather is still useful as a predetermined variable

ERA5 Tmax and precipitation at Brazilian grid points are not chosen by coffee traders. Conditional on the lag, they are predetermined with respect to next-month KC returns. That justifies treating $W_{t-1}$ as a valid predictor in a forecasting regression. It does **not** purge omitted global factors (USD, Vietnam robusta weather, inventories, CFTC positioning).

### 3.3 Threats to identification

| Threat | Direction | Mitigation in this repo | Residual risk |
|--------|-----------|-------------------------|---------------|
| Look-ahead in continuous futures | Overstate predictability | Next-bar execution; lagged vol | Continuous KC=F is not a roll-adjusted research series |
| Look-ahead in weather | Overstate | 1-month shift of monthly stress | Reanalysis revisions exist |
| Data mining of thresholds | False discovery | Pre-specify 31 °C / 30 °C / weights in code + results note | Thresholds were informed by earlier failed 33 °C tests |
| Spatial aggregation | Attenuation | 5-point average | Not a production-weighted map |
| Multiple testing | Inflated Sharpe | Documented; not corrected | Need White Reality Check / Deflated Sharpe |
| Regime dependence (2015–25 includes 2021 frost) | Unstable | Robustness protocol | Single sample |

## 4. Estimands

1. Yield-response coefficients $(\beta_{\text{EHD}}, \beta_{\text{SM}}, \beta_{\text{int}})$ with HAC and moving-block bootstrap CIs.
2. Incremental fit of weather in price models ($\Delta$AIC, $\Delta$adj. $R^2$).
3. Strategy moments: CAGR, volatility, Sharpe, max DD, hit rate, turnover, average absolute position.
4. (Future) Deflated Sharpe and bootstrap CI on Sharpe$^{\text{strat}} -$ Sharpe$^{\text{BH}}$.

## 5. Pre-analysis plan (registered in-repo)

Before claiming stronger results, the following must be run and reported together:

1. Headline 2015–2025 test (done).
2. Threshold grid: EHD $\in \{30,31,32,33\}$, lag $\in \{0,1,2\}$ months (lag 0 is *invalid* for trading claims).
3. Vol-target grid: $\{None, 10\%, 15\%, 20\%\}$.
4. Subsamples: 2015–19 / 2020–25.
5. Drop 2021 (frost year) as a leave-one-crisis-out check.
6. Report Deflated Sharpe (Bailey & López de Prado).

Helpers live in `src/robustness.py` and `src/evaluation.py`.

## 6. What would make this a thesis chapter

Minimum additional empirics:

- Official Brazilian yield / production panel (CONAB or IBGE SIDRA), state or mesoregion.
- Production-weighted weather, not equal-weighted points.
- Proper KC roll series (front-month with documented roll rule).
- Formal inference on Sharpe differences.
- Comparison with USDA/CONAB *revision* surprises as an alternative information set.
