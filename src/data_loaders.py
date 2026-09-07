"""
Data loaders for coffee prices and weather stress series.

- Price: KC=F via yfinance
- Stress: synthetic (demo) or real (Open-Meteo ERA5 via weather_data.py)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Literal

try:
    import yfinance as yf
except ImportError:
    yf = None

from .weather_data import (
    fetch_brazil_coffee_weather,
    build_real_stress,
    BRAZIL_COFFEE_POINTS,
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


def synthetic_stress(price: pd.Series, seed: int = 42) -> pd.Series:
    """DEMO ONLY – seasonal synthetic stress (see previous version)."""
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


def real_weather_stress(
    price: pd.Series,
    region: str = "sul_de_minas",
    ehd_threshold: float = 33.0,
    start: Optional[str] = None,
) -> pd.Series:
    """
    Build stress from real Open-Meteo ERA5 weather for a Brazil coffee region,
    then align (forward-fill) to the daily price index.
    """
    if start is None:
        start = price.index.min().strftime("%Y-%m-%d")
    end = price.index.max().strftime("%Y-%m-%d")

    daily = fetch_brazil_coffee_weather(region=region, start=start, end=end)
    monthly_stress = build_real_stress(daily, ehd_threshold=ehd_threshold)

    # Forward-fill monthly stress onto daily price calendar
    stress = monthly_stress.reindex(price.index, method="ffill")
    # Back-fill any leading NaNs with first valid value
    stress = stress.bfill().fillna(0)
    stress.name = "stress"
    return stress


def load_stress(
    price: pd.Series,
    source: Literal["real", "synthetic"] = "real",
    region: str = "sul_de_minas",
    **kwargs,
) -> pd.Series:
    """Unified stress loader. Prefer source='real' for research."""
    if source == "real":
        return real_weather_stress(price, region=region, **kwargs)
    return synthetic_stress(price, **kwargs)
