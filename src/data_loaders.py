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
) -> pd.Series:
    """
    DEMO ONLY – improved synthetic monthly stress index with seasonal structure.

    - Higher base risk in Brazil frost window (May–Aug) and flowering period (Sep–Dec)
    - Realised volatility component
    - Occasional strong positive shocks (proxy for extreme heat / drought)

    Replace this function with real output from weather_indices.py
    (EHD, soil-moisture anomaly, composite stress) as soon as data is available.
    """
    rng = np.random.default_rng(seed)
    monthly = price.resample("ME").last().to_frame("price")
    monthly["ret"] = monthly["price"].pct_change()
    monthly["vol"] = monthly["ret"].rolling(6, min_periods=1).std().fillna(0)
    monthly["month"] = monthly.index.month

    # Seasonal risk profile (coffee-relevant windows)
    seasonal = np.zeros(len(monthly))
    seasonal[monthly["month"].isin([5, 6, 7, 8])] = 0.6   # frost risk window
    seasonal[monthly["month"].isin([9, 10, 11, 12])] = 0.4  # flowering / early set

    shock = rng.normal(0, 0.7, len(monthly))
    for i, m in enumerate(monthly["month"]):
        if m in [5, 6, 7, 8, 9, 10] and rng.random() < 0.18:
            shock[i] += rng.uniform(1.5, 3.0)

    monthly["stress"] = (0.5 * monthly["vol"] * 3 + seasonal + shock).clip(-0.5, 4.0)
    monthly["stress"] = monthly["stress"].rolling(2, min_periods=1).mean()

    stress = monthly["stress"].reindex(price.index, method="ffill").fillna(0)
    stress.name = "stress"
    return stress
