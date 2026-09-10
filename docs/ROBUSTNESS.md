# Robustness protocol

Pre-specified *before* treating any alternative Sharpe as a result.

## Grid A — thresholds (signal construction)

- Long threshold $\in \{0.6, 0.8, 1.0, 1.2\}$
- Short threshold $\in \{-0.8, -0.6, -0.4\}$
- Short size fixed at $-0.4$

Implementation: `src.robustness.threshold_grid`.

## Grid B — weather definition

- EHD cutoff $\in \{30, 31, 32, 33\}$ °C
- Lag $\in \{1, 2\}$ months  
  Lag 0 is allowed only as a *look-ahead diagnostic*, never as a trading claim.

## Grid C — risk overlay

- `target_vol` $\in \{\mathrm{None}, 0.10, 0.15, 0.20\}$
- EWMA span $\in \{20, 30, 60\}$

## Grid D — samples

| Window | Purpose |
|--------|--------|
| 2015–2019 | pre-pandemic / pre-2021 frost |
| 2020–2025 | recent regime |
| Full sample excluding 2021 | leave-one-crisis-out |

Implementation: `src.robustness.subsample_split`.

## Multiple testing

Count every cell you actually looked at as a trial. Pass that count into `deflated_sharpe(..., n_trials=N)`. If you inspected the 33 °C single-point spec before the 31 °C multi-point spec, that is at least **two** families already.

A conservative working number for this repository as of 2026-09-10 is $N_{\text{trials}} \ge 8$.

## Reporting rule

A specification is "robust" only if:

1. Sign of Sharpe$^{\text{strat}} -$ Sharpe$^{\text{BH}}$ is stable in at least 2 of 3 date windows, **and**
2. MaxDD$^{\text{strat}}$ remains below MaxDD$^{\text{BH}}$ in the full sample, **and**
3. DSR is reported next to the headline Sharpe.

The registered headline table does **not** yet satisfy (3). That is an open item, not a hidden one.
