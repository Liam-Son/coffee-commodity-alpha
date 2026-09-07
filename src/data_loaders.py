"""
Data loaders for coffee prices and (placeholder) weather stress series.

Real weather indices from src/weather_indices.py should replace the
synthetic stress once ERA5 / yield panels are available.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional

try:
    import yfinance as yf
except ImportError:
    yf = None


def load_coffee_futures(
    start: str = "2015-01-01",
    end: Optional[str] = None,
    ticker: str = "KC=F",
) -> pd.Series:
    """
    Daily continuous Arabica coffee futures (KC) via Yahoo Finance.
    Returns a Close price Series with DatetimeIndex.
    """
    if yf is None:
        raise ImportError("yfinance is required: pip install yfinance")
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel(1, axis=1)
    s = df["Close"].dropna()
    s.name = "price"
    s.index = pd.to_datetime(s.index)
    return s


def synthetic_stress(
    price: pd.Series,
    seed: int = 42,
    threshold_scale: float = 1.0,
) -> pd.Series:
    """
    DEMO ONLY – synthetic monthly stress index.

    Combines realised volatility with occasional random positive shocks
    that stand in for heat / drought events.  Replace this function with
    real output from weather_indices.py (EHD, soil-moisture anomaly,
    composite stress) as soon as the data pipeline is populated.
    """
    rng = np.random.default_rng(seed)
    monthly = price.resample("ME").last().to_frame("price")
    monthly["ret"] = monthly["price"].pct_change()
    monthly["vol"] = monthly["ret"].rolling(6, min_periods=1).std().fillna(0)

    shock = rng.normal(0, 1, len(monthly))
    # Sparse strong positive shocks (proxy for extreme weather)
    shock[::17] += 2.5 * threshold_scale
    shock[::23] += 1.8 * threshold_scale

    monthly["stress"] = (monthly["vol"] * 2 + shock).clip(-1, 4)
    monthly["stress"] = monthly["stress"].rolling(2, min_periods=1).mean()

    # Forward-fill to daily
    stress = monthly["stress"].reindex(price.index, method="ffill").fillna(0)
    stress.name = "stress"
    return stress
