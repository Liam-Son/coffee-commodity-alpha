# Limitations (referee-facing)

A PhD-grade project states its weaknesses before a referee does.

## Critical (affects interpretation of headline numbers)

1. **No official yield panel in-repo.** RQ2 is specified but not estimated on CONAB/IBGE data. The overlay therefore skips the yield channel and jumps from weather → prices.
2. **Continuous KC=F is not a research futures series.** Roll convention, expiry cycle, and basis to cash are not modelled.
3. **Equal-weighted five points ≠ production-weighted Brazil.** Cerrado and Sul de Minas do not contribute equally to exportable Arabica.
4. **Thresholds and weights were informed by a failed 33 °C specification.** This is a mild specification search. Multiple-testing correction is not applied to the headline Sharpe.
5. **No inference on Sharpe differences.** 0.45 vs 0.38 is a point comparison, not a test.
6. **Sparse signal.** ~72% flat. Hit rate 14% reflects many zero days, not directional accuracy conditional on being in the market.
7. **Single sample, one crisis.** 2021 Brazilian frost/drought dominates recent KC history. Leave-one-crisis-out is specified in the robustness protocol but is not the headline table.
8. **Reanalysis ≠ station microclimate.** Basis risk for insurance applications is expected to be large.

## Important (does not invalidate the pipeline)

9. Open-Meteo free-tier terms are non-commercial; commercial replication needs a licence check.
10. No transaction-cost model beyond a flat 5 bp; futures slippage in stressed coffee sessions can be larger.
11. No position-size constraint in notional bags or margin.
12. Tea comparison remains a literature note, not an estimated parallel panel.

## What we do *not* claim

- That the strategy is profitable after realistic costs and capacity.
- That weather *causes* KC returns in a structural sense.
- That 10% vol targeting is optimal.
- That the code is production-ready.
