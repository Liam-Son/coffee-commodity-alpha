# Moving Block Bootstrap – Usage Guide

## Files

- `src/block_bootstrap.py` – core implementation
- `src/yield_price_models.py` – convenience wrappers for yield regressions

## Quick start

```python
import pandas as pd
import statsmodels.api as sm
from src.block_bootstrap import (
    block_bootstrap_ols,
    bootstrap_summary,
    block_length_robustness,
    bootstrap_from_model,
)
from src.yield_price_models import (
    estimate_yield_response,
    estimate_yield_response_bootstrap,
)

# --- Option A: from raw y, X ---
# X should already contain a constant if you want an intercept
X = sm.add_constant(df[["ehd", "sm_anom", "ehd_x_sm"]])
y = df["log_yield"]

result = block_bootstrap_ols(
    y, X,
    block_length=3,
    n_boot=999,
    method="residual",   # or "pairs"
    conf_level=0.95,
    seed=42,
)

print(bootstrap_summary(result, param_names=["const", "ehd", "sm_anom", "ehd_x_sm"]))

# --- Option B: from an already-fitted statsmodels model ---
model = estimate_yield_response(df)          # HAC SEs
boot_table = bootstrap_from_model(model, block_length=3, n_boot=999)
print(boot_table)

# --- Option C: one-liner convenience for yield model ---
boot_table = estimate_yield_response_bootstrap(df, block_length=3)
print(boot_table)

# --- Robustness across block lengths ---
robust = block_length_robustness(
    y, X,
    block_lengths=[2, 3, 4],
    n_boot=999,
    method="residual",
    param_names=["const", "ehd", "sm_anom", "ehd_x_sm"],
)
print(robust)
```

## Recommended defaults (annual yield data)

| Setting | Value | Reason |
|---------|-------|--------|
| `block_length` | 2–4 | Matches typical short-sample dependence |
| `n_boot` | 999 or 1999 | Stable percentile intervals |
| `method` | `"residual"` | Weather treated as exogenous |
| `method` | `"pairs"` | Safer when lagged prices or endogenous X |

## What the output gives you

- `coef` – original OLS point estimate
- `boot_se` – bootstrap standard error
- `ci_low` / `ci_high` – percentile confidence interval
- `significant` – True if CI does not cover zero

Compare these with the HAC t-stats from the original model. When both agree on sign and significance, inference is more credible.
