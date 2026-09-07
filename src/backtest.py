"""
Minimal vectorized backtester for coffee strategies.

Designed for daily price series + daily or lower-frequency signals.
Includes simple transaction costs and basic performance stats.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


def run_backtest(
    price: pd.Series,
    signal: pd.Series,
    cost_bps: float = 5.0,
    position_lag: int = 1,
) -> pd.DataFrame:
    """
    Vectorized long/flat (or long/short) backtest.

    Parameters
    ----------
    price : daily close prices (DatetimeIndex)
    signal : desired position in [-1, 1] or [0, 1], aligned to price index
    cost_bps : round-trip cost in basis points applied to turnover
    position_lag : bars to lag the signal (1 = next-bar execution)

    Returns
    -------
    DataFrame with columns: price, signal, position, ret, strat_ret, equity, bh_equity, turnover
    """
    df = pd.DataFrame({"price": price}).sort_index()
    df["signal"] = signal.reindex(df.index).fillna(0)
    df["position"] = df["signal"].shift(position_lag).fillna(0)
    df["ret"] = df["price"].pct_change()
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
