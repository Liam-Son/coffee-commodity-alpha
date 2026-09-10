"""
Pre-specified robustness helpers.

These do not download data. Callers pass an already-built daily stress series
and a price series so grids can be run offline after one weather pull.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from .backtest import run_backtest, performance_stats


def threshold_grid(
    price: pd.Series,
    stress: pd.Series,
    long_grid: Iterable[float] = (0.6, 0.8, 1.0, 1.2),
    short_grid: Iterable[float] = (-0.8, -0.6, -0.4),
    target_vol: float | None = None,
    cost_bps: float = 5.0,
    short_size: float = -0.4,
) -> pd.DataFrame:
    """Run a small pre-specified threshold grid and return a results table."""
    rows = []
    for lo in long_grid:
        for sh in short_grid:
            if lo <= 0 or sh >= 0:
                continue
            sig = pd.Series(0.0, index=price.index)
            s = stress.reindex(price.index).ffill().fillna(0)
            sig[s > lo] = 1.0
            sig[s < sh] = short_size
            bt = run_backtest(price, sig, cost_bps=cost_bps, target_vol=target_vol)
            stats = performance_stats(bt["strat_ret"])
            stats.update({"long_thresh": lo, "short_thresh": sh, "target_vol": target_vol})
            rows.append(stats)
    return pd.DataFrame(rows)


def subsample_split(
    price: pd.Series,
    signal: pd.Series,
    splits: dict[str, tuple[str, str]] | None = None,
    target_vol: float | None = 0.10,
    cost_bps: float = 5.0,
) -> pd.DataFrame:
    """Evaluate the *same* signal on pre-specified date windows."""
    if splits is None:
        splits = {
            "full": ("2015-01-01", "2025-12-31"),
            "pre_2020": ("2015-01-01", "2019-12-31"),
            "post_2020": ("2020-01-01", "2025-12-31"),
            "ex_2021": ("2015-01-01", "2025-12-31"),
        }
    rows = []
    for name, (a, b) in splits.items():
        p = price.loc[a:b]
        if name == "ex_2021":
            p = p[(p.index.year != 2021)]
        sig = signal.reindex(p.index).fillna(0)
        bt = run_backtest(p, sig, cost_bps=cost_bps, target_vol=target_vol)
        stats = performance_stats(bt["strat_ret"])
        stats["window"] = name
        stats["n_days"] = int(len(p))
        rows.append(stats)
    return pd.DataFrame(rows)
