"""
Yield response functions and price-model tests.

Steps 2 and 3 of the quantitative pipeline.
Also exposes optional Moving Block Bootstrap inference.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Optional

from .block_bootstrap import bootstrap_from_model, block_length_robustness


def estimate_yield_response(
    df: pd.DataFrame,
    yield_col: str = "log_yield",
    ehd_col: str = "ehd",
    sm_col: str = "sm_anom",
    controls: Optional[list[str]] = None,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Simple OLS yield response:

        yield = α + β1·EHD + β2·SM + β3·EHD×SM + controls + ε

    Returns a statsmodels results object fitted with HAC (Newey–West) SEs.
    """
    data = df.dropna(subset=[yield_col, ehd_col, sm_col]).copy()
    data["ehd_x_sm"] = data[ehd_col] * data[sm_col]

    x_cols = [ehd_col, sm_col, "ehd_x_sm"]
    if controls:
        x_cols += controls

    X = sm.add_constant(data[x_cols])
    y = data[yield_col]
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    return model


def estimate_yield_response_bootstrap(
    df: pd.DataFrame,
    yield_col: str = "log_yield",
    ehd_col: str = "ehd",
    sm_col: str = "sm_anom",
    controls: Optional[list[str]] = None,
    block_length: int = 3,
    n_boot: int = 999,
    method: str = "residual",
) -> pd.DataFrame:
    """
    Fit the yield response model and return Moving Block Bootstrap summary
    (point estimate, bootstrap SE, percentile CI).
    """
    model = estimate_yield_response(
        df, yield_col=yield_col, ehd_col=ehd_col, sm_col=sm_col, controls=controls
    )
    return bootstrap_from_model(
        model,
        block_length=block_length,
        n_boot=n_boot,
        method=method,  # type: ignore
    )


def price_baseline(
    df: pd.DataFrame,
    price_col: str = "dlog_price",
    lags: int = 3,
    supply_col: Optional[str] = None,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Baseline:
        Δlog(P_t) = α + Σ φ_i Δlog(P_{t-i}) + θ·SupplyProxy + ε
    """
    data = df.copy()
    for i in range(1, lags + 1):
        data[f"lag{i}"] = data[price_col].shift(i)

    x_cols = [f"lag{i}" for i in range(1, lags + 1)]
    if supply_col and supply_col in data.columns:
        x_cols.append(supply_col)

    data = data.dropna(subset=[price_col] + x_cols)
    X = sm.add_constant(data[x_cols])
    y = data[price_col]
    return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})


def price_augmented(
    df: pd.DataFrame,
    price_col: str = "dlog_price",
    lags: int = 3,
    supply_col: Optional[str] = None,
    weather_cols: Optional[list[str]] = None,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Augmented with weather anomalies:
        Δlog(P_t) = baseline + λ·WeatherAnomalies + ε
    """
    data = df.copy()
    for i in range(1, lags + 1):
        data[f"lag{i}"] = data[price_col].shift(i)

    x_cols = [f"lag{i}" for i in range(1, lags + 1)]
    if supply_col and supply_col in data.columns:
        x_cols.append(supply_col)
    if weather_cols:
        x_cols += weather_cols

    data = data.dropna(subset=[price_col] + x_cols)
    X = sm.add_constant(data[x_cols])
    y = data[price_col]
    return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})


def compare_models(
    baseline: sm.regression.linear_model.RegressionResultsWrapper,
    augmented: sm.regression.linear_model.RegressionResultsWrapper,
) -> dict:
    """Simple comparison metrics."""
    return {
        "baseline_aic": baseline.aic,
        "augmented_aic": augmented.aic,
        "baseline_bic": baseline.bic,
        "augmented_bic": augmented.bic,
        "baseline_rsquared_adj": baseline.rsquared_adj,
        "augmented_rsquared_adj": augmented.rsquared_adj,
        "delta_aic": augmented.aic - baseline.aic,  # negative → augmented preferred
    }
