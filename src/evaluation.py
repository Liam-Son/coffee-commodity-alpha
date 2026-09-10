"""
Evaluation metrics beyond raw Sharpe.

Includes a Bailey & López de Prado (2014) style Deflated Sharpe Ratio
approximation for a *known* number of trials.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import norm


def deflated_sharpe(
    sharpe: float,
    n_obs: int,
    n_trials: int,
    skew: float = 0.0,
    kurt: float = 3.0,
    sharpe_benchmark: float = 0.0,
) -> dict:
    """
    Approximate Deflated Sharpe Ratio (DSR).

    Parameters
    ----------
    sharpe : observed Sharpe (already annualised if n_obs is in years-equivalent
             daily bars, pass the *daily* Sharpe * sqrt(252) consistently with n_obs=days)
    n_obs : number of return observations used to compute Sharpe
    n_trials : independent specifications inspected (thresholds, lags, vol targets)
    skew, kurt : sample skewness and kurtosis of strategy returns
    sharpe_benchmark : null Sharpe (0 for 'no skill')

    Notes
    -----
    This is an approximation for reporting, not a substitute for a White Reality Check.
    If n_trials is understated, DSR is overstated.
    """
    if n_obs < 10 or n_trials < 1:
        return {"dsr": float("nan"), "p_value": float("nan")}

    sr = sharpe
    # Non-normal adjustment of Sharpe variance (Lo 2002 / BLP 2014 style)
    sr_var = (
        (1 - skew * sr + ((kurt - 1) / 4.0) * sr**2) / (n_obs - 1)
    )
    sr_se = math.sqrt(max(sr_var, 1e-12))

    # Expected max Sharpe under n_trials (approx.)
    emc = 0.5772156649
    z = norm.ppf(1 - 1.0 / n_trials)
    sr_max_exp = sharpe_benchmark + sr_se * ((1 - emc) * z + emc * norm.ppf(1 - 1.0 / (n_trials * math.e)))

    dsr = norm.cdf((sr - sr_max_exp) / sr_se)
    return {
        "sharpe": float(sr),
        "dsr": float(dsr),
        "expected_max_sharpe": float(sr_max_exp),
        "n_obs": int(n_obs),
        "n_trials": int(n_trials),
    }


def turnover_stats(position: pd.Series) -> dict:
    chg = position.diff().abs().fillna(0)
    return {
        "mean_abs_position": float(position.abs().mean()),
        "mean_daily_turnover": float(chg.mean()),
        "ann_turnover": float(chg.mean() * 252),
        "frac_long": float((position > 0).mean()),
        "frac_short": float((position < 0).mean()),
        "frac_flat": float((position == 0).mean()),
    }
