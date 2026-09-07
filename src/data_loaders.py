"""
Data loaders for coffee prices and weather stress series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Literal, Sequence

try:
    import yfinance as yf
except ImportError:
    yf = None

from .weather_data import (
    fetch_multi_point,
    build_lagged_stress,
    DEFAULT_REGIONS,
)


def load_coffee_futures(
    start: str = "2015-01-01",
    end: Optional[str] = None,
    ticker: str = "KC=F",
) -> pd.Series:
    """Daily continuous Arabica coffee futures (KC) via Yahoo Finance."""
    if yf is None:
        raise ImportError("yfinance is required: pip install yfinance")
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel(1, axis=1)
    s = df["Close"].dropna()
    s.name = "price"
    s.index = pd.to_datetime(s.index)
    return s


def real_weather_stress(
    price: pd.Series,
    regions: Sequence[str] = DEFAULT_REGIONS,
    ehd_threshold: float = 31.0,
    lag_months: int = 1,
    start: Optional[str] = None,
) -> pd.Series:
    """
    Multi-point real ERA5 stress with 1-month lag, aligned to price index.
    """
    if start is None:
        start = (price.index.min() - pd.DateOffset(months=3)).strftime("%Y-%m-%d")
    end = price.index.max().strftime("%Y-%m-%d")

    daily = fetch_multi_point(regions=regions, start=start, end=end)
    monthly_stress = build_lagged_stress(
        daily,
        lag_months=lag_months,
        ehd_threshold=ehd_threshold,
    )

    stress = monthly_stress.reindex(price.index, method="ffill")
    stress = stress.bfill().fillna(0)
    stress.name = "stress"
    return stress


def synthetic_stress(price: pd.Series, seed: int = 42) -> pd.Series:
    """Fallback synthetic series (kept for comparison)."""
    rng = np.random.default_rng(seed)
    monthly = price.resample("ME").last().to_frame("price")
    monthly["ret"] = monthly["price"].pct_change()
    monthly["vol"] = monthly["ret"].rolling(6, min_periods=1).std().fillna(0)
    monthly["month"] = monthly.index.month
    seasonal = np.zeros(len(monthly))
    seasonal[monthly["month"].isin([5, 6, 7, 8])] = 0.6
    seasonal[monthly["month"].isin([9, 10, 11, 12])] = 0.4
    shock = rng.normal(0, 0.7, len(monthly))
    for i, m in enumerate(monthly["month"]):
        if m in [5, 6, 7, 8, 9, 10] and rng.random() < 0.18:
            shock[i] += rng.uniform(1.5, 3.0)
    monthly["stress"] = (0.5 * monthly["vol"] * 3 + seasonal + shock).clip(-0.5, 4.0)
    monthly["stress"] = monthly["stress"].rolling(2, min_periods=1).mean()
    stress = monthly["stress"].reindex(price.index, method="ffill").fillna(0)
    stress.name = "stress"
    return stress


def load_stress(
    price: pd.Series,
    source: Literal["real", "synthetic"] = "real",
    **kwargs,
) -> pd.Series:
    if source == "real":
        return real_weather_stress(price, **kwargs)
    return synthetic_stress(price, **kwargs)
