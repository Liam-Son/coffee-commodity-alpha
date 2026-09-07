"""
Vectorized backtester for coffee strategies.

Includes:
- Simple long/flat or long/short execution with costs
- EWMA volatility targeting
- Basic performance stats
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


def ewma_vol(
    returns: pd.Series,
    span: int = 30,
    ann_factor: int = 252,
    lag: int = 1,
) -> pd.Series:
    """
    Exponentially weighted volatility forecast (annualised).

    Parameters
    ----------
    returns : daily returns
    span : EWMA span (≈ 2/(1-λ) - 1; span=30 → λ≈0.94)
    ann_factor : days per year for annualisation
    lag : bars to shift the estimate (1 = no look-ahead)

    Returns
    -------
    Annualised volatility series, lagged.
    """
    var = returns.ewm(span=span, min_periods=max(5, span // 3)).var()
    sigma = np.sqrt(var * ann_factor)
    return sigma.shift(lag)


def vol_target_weights(
    returns: pd.Series,
    target_vol: float = 0.10,
    span: int = 30,
    lag: int = 1,
    w_min: float = 0.25,
    w_max: float = 2.0,
    ann_factor: int = 252,
) -> pd.Series:
    """
    Position scaler that targets a constant annualised volatility.

        w_t = clip( target_vol / σ̂_{t-lag} , w_min, w_max )

    Parameters
    ----------
    returns : daily asset (or strategy) returns used to estimate vol
    target_vol : desired annualised volatility (e.g. 0.10 = 10%)
    span : EWMA span
    lag : prevent look-ahead
    w_min, w_max : leverage floors / caps

    Returns
    -------
    Weight series aligned to returns index.
    """
    sigma = ewma_vol(returns, span=span, ann_factor=ann_factor, lag=lag)
    w = target_vol / sigma.replace(0, np.nan)
    w = w.clip(w_min, w_max).fillna(1.0)
    w.name = "vol_weight"
    return w


def run_backtest(
    price: pd.Series,
    signal: pd.Series,
    cost_bps: float = 5.0,
    position_lag: int = 1,
    target_vol: Optional[float] = None,
    vol_span: int = 30,
    vol_w_min: float = 0.25,
    vol_w_max: float = 2.0,
) -> pd.DataFrame:
    """
    Vectorized long/flat (or long/short) backtest with optional EWMA vol targeting.

    Parameters
    ----------
    price : daily close prices (DatetimeIndex)
    signal : desired raw position in [-1, 1] or [0, 1]
    cost_bps : cost in basis points applied to absolute turnover
    position_lag : bars to lag the final position (1 = next-bar execution)
    target_vol : if set (e.g. 0.10), scale signal by EWMA vol weights
    vol_span, vol_w_min, vol_w_max : vol-targeting parameters

    Returns
    -------
    DataFrame with price, signal, vol_weight, position, ret, strat_ret, equity, ...
    """
    df = pd.DataFrame({"price": price}).sort_index()
    df["signal"] = signal.reindex(df.index).fillna(0)
    df["ret"] = df["price"].pct_change()

    if target_vol is not None:
        df["vol_weight"] = vol_target_weights(
            df["ret"],
            target_vol=target_vol,
            span=vol_span,
            lag=1,
            w_min=vol_w_min,
            w_max=vol_w_max,
        )
        scaled = df["signal"] * df["vol_weight"]
    else:
        df["vol_weight"] = 1.0
        scaled = df["signal"]

    df["position"] = scaled.shift(position_lag).fillna(0)
    df["strat_ret"] = df["position"] * df["ret"]

    # Transaction costs on position changes
    df["turnover"] = df["position"].diff().abs().fillna(0)
    df["strat_ret"] = df["strat_ret"] - df["turnover"] * (cost_bps / 10000.0)

    df["equity"] = (1 + df["strat_ret"].fillna(0)).cumprod()
    df["bh_equity"] = (1 + df["ret"].fillna(0)).cumprod()
    return df


def performance_stats(returns: pd.Series, ann_factor: int = 252) -> dict:
    """Annualised performance metrics from a return series."""
    r = returns.dropna()
    if len(r) < 5:
        return {}
    mu = r.mean() * ann_factor
    vol = r.std() * np.sqrt(ann_factor)
    sharpe = mu / vol if vol > 0 else 0.0
    equity = (1 + r).cumprod()
    max_dd = (equity / equity.cummax() - 1).min()
    hit = (r > 0).mean()
    return {
        "CAGR": float(mu),
        "Vol": float(vol),
        "Sharpe": float(sharpe),
        "MaxDD": float(max_dd),
        "HitRate": float(hit),
        "N": int(len(r)),
    }


def summarise(bt: pd.DataFrame) -> pd.DataFrame:
    """Side-by-side strategy vs buy-and-hold stats."""
    s = performance_stats(bt["strat_ret"])
    b = performance_stats(bt["ret"])
    return pd.DataFrame({"Strategy": s, "BuyHold": b}).T
