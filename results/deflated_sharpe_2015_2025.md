# Deflated Sharpe Ratio — registered overlay

Computed 2026-09-10. Daily Sharpe = annualised Sharpe / sqrt(252).  
Bailey and López de Prado (2014) approximation. n_obs = 2,767 daily bars.

| Strategy | Ann. Sharpe | Daily Sharpe | n_trials | Expected max ann. Sharpe | DSR |
|----------|-------------|--------------|----------|---------------------------|-----|
| Overlay, no vol target | 0.45 | 0.028 | 8 | 0.44 | **0.51** |
| Overlay, no vol target | 0.45 | 0.028 | 20 | 0.57 | **0.34** |
| Overlay, vol target 10% | 0.40 | 0.025 | 8 | 0.44 | **0.45** |
| Buy-and-hold (null trials = 1) | 0.38 | 0.024 | 1 | 0.00 | 0.90 |

**Interpretation.** Under a conservative but still modest trial count of eight (the 33 °C specification plus the 31 °C specification plus a handful of threshold/vol cells), the overlay Sharpe of 0.45 is almost exactly what one would expect from the *maximum* of eight noise strategies. DSR ≈ 0.51 is not a rejection of skill; it is a refusal of discovery. This is the academically honest number that belongs next to Table 6.1.

If the researcher inspected twenty cells, DSR falls to 0.34.
