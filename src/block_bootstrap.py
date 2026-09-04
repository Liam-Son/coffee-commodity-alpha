"""
Moving Block Bootstrap for time-series OLS.

Provides residual and pairs (case) block bootstrap standard errors,
percentile confidence intervals, and simple block-length robustness.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Optional, Literal


def _moving_block_indices(T: int, block_length: int, rng: np.random.Generator) -> np.ndarray:
    """
    Draw overlapping moving-block indices that cover approximately T observations.
    """
    if block_length < 1:
        raise ValueError("block_length must be >= 1")
    if block_length > T:
        block_length = T

    n_blocks = int(np.ceil(T / block_length))
    max_start = T - block_length
    starts = rng.integers(0, max_start + 1, size=n_blocks)

    indices = []
    for s in starts:
        indices.extend(range(s, s + block_length))
    return np.array(indices[:T])


def block_bootstrap_ols(
    y: np.ndarray | pd.Series,
    X: np.ndarray | pd.DataFrame,
    block_length: int = 3,
    n_boot: int = 999,
    method: Literal["residual", "pairs"] = "residual",
    conf_level: float = 0.95,
    seed: Optional[int] = 42,
) -> dict:
    """
    Moving Block Bootstrap for OLS coefficients.

    Parameters
    ----------
    y : array-like, shape (T,)
        Dependent variable.
    X : array-like, shape (T, k)
        Regressor matrix (should already include a constant if desired).
    block_length : int
        Length of each block (typical annual choice: 2–4).
    n_boot : int
        Number of bootstrap replications.
    method : {"residual", "pairs"}
        - "residual": resample blocks of residuals, keep X fixed.
        - "pairs": resample blocks of (y, X) rows together.
    conf_level : float
        Confidence level for percentile intervals (e.g. 0.95).
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        coef          – original OLS point estimates
        boot_se       – bootstrap standard errors
        ci_low        – lower percentile CI
        ci_high       – upper percentile CI
        boot_coefs    – (n_boot, k) array of bootstrap coefficient draws
        block_length  – block length used
        method        – bootstrap method used
        n_boot        – number of replications
    """
    rng = np.random.default_rng(seed)

    y = np.asarray(y).ravel()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    T, k = X.shape
    if len(y) != T:
        raise ValueError("y and X must have the same number of rows")

    # Original OLS fit
    ols = sm.OLS(y, X).fit()
    beta_hat = ols.params.copy()
    resid = ols.resid

    boot_coefs = np.zeros((n_boot, k))

    for b in range(n_boot):
        idx = _moving_block_indices(T, block_length, rng)

        if method == "residual":
            # Keep X fixed; resample residual blocks
            u_star = resid[idx]
            y_star = X @ beta_hat + u_star
            X_star = X
        elif method == "pairs":
            y_star = y[idx]
            X_star = X[idx, :]
        else:
            raise ValueError("method must be 'residual' or 'pairs'")

        try:
            beta_star = sm.OLS(y_star, X_star).fit().params
            boot_coefs[b, :] = beta_star
        except Exception:
            # Rare singular draws; leave as NaN and drop later
            boot_coefs[b, :] = np.nan

    # Drop any failed replications
    valid = ~np.isnan(boot_coefs).any(axis=1)
    boot_coefs = boot_coefs[valid]

    alpha = 1 - conf_level
    ci_low = np.nanpercentile(boot_coefs, 100 * alpha / 2, axis=0)
    ci_high = np.nanpercentile(boot_coefs, 100 * (1 - alpha / 2), axis=0)
    boot_se = np.nanstd(boot_coefs, axis=0, ddof=1)

    return {
        "coef": beta_hat,
        "boot_se": boot_se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "boot_coefs": boot_coefs,
        "block_length": block_length,
        "method": method,
        "n_boot": int(valid.sum()),
        "conf_level": conf_level,
    }


def bootstrap_summary(
    result: dict,
    param_names: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Turn block_bootstrap_ols output into a readable table.
    """
    k = len(result["coef"])
    if param_names is None:
        param_names = [f"x{i}" for i in range(k)]
    if len(param_names) != k:
        raise ValueError("param_names length must match number of coefficients")

    df = pd.DataFrame(
        {
            "coef": result["coef"],
            "boot_se": result["boot_se"],
            "ci_low": result["ci_low"],
            "ci_high": result["ci_high"],
        },
        index=param_names,
    )
    df["significant"] = (df["ci_low"] > 0) | (df["ci_high"] < 0)
    return df


def block_length_robustness(
    y: np.ndarray | pd.Series,
    X: np.ndarray | pd.DataFrame,
    block_lengths: list[int] = [2, 3, 4],
    n_boot: int = 999,
    method: Literal["residual", "pairs"] = "residual",
    conf_level: float = 0.95,
    param_names: Optional[list[str]] = None,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Re-run Moving Block Bootstrap across several block lengths
    and return a comparison table (useful robustness check).
    """
    rows = []
    for ell in block_lengths:
        res = block_bootstrap_ols(
            y, X,
            block_length=ell,
            n_boot=n_boot,
            method=method,
            conf_level=conf_level,
            seed=seed,
        )
        summary = bootstrap_summary(res, param_names=param_names)
        summary["block_length"] = ell
        rows.append(summary.reset_index().rename(columns={"index": "param"}))

    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# Convenience wrapper that works directly with a statsmodels OLS result
# or with the design matrices used in yield_price_models.py
# ---------------------------------------------------------------------------

def bootstrap_from_model(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    block_length: int = 3,
    n_boot: int = 999,
    method: Literal["residual", "pairs"] = "residual",
    conf_level: float = 0.95,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Run block bootstrap using y and X from an already-fitted statsmodels model.
    Returns a summary DataFrame.
    """
    y = model.model.endog
    X = model.model.exog
    names = list(model.model.exog_names)

    res = block_bootstrap_ols(
        y, X,
        block_length=block_length,
        n_boot=n_boot,
        method=method,
        conf_level=conf_level,
        seed=seed,
    )
    return bootstrap_summary(res, param_names=names)
