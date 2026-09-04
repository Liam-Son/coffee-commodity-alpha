"""
Weather index construction for coffee (Brazil) and tea (Kenya, Assam).

Step 1 of the quantitative pipeline.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


# ---------------------------------------------------------------------------
# Thresholds (can be calibrated later)
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "brazil_arabica": {
        "tmax_ehd": 33.0,       # °C – moderate extreme
        "tmax_severe": 35.0,    # °C – severe
        "gdd_base": 10.0,       # example base for GDD
        "hdd_threshold": 32.0,  # harmful degree day start
    },
    "kenya_tea": {
        "tmax_ehd": 30.0,
        "tmax_severe": 35.0,
    },
    "assam_tea": {
        "tmax_ehd": 32.0,
        "tmax_severe": 34.0,
        "monthly_mean_penalty": 26.6,  # from Assam literature
    },
}


def extreme_heat_days(
    daily: pd.DataFrame,
    tmax_col: str = "tmax",
    threshold: float = 33.0,
    date_col: str = "date",
) -> pd.Series:
    """
    Count of days with Tmax >= threshold, aggregated by month or season.

    Parameters
    ----------
    daily : DataFrame with at least [date_col, tmax_col]
    threshold : temperature threshold in °C

    Returns
    -------
    Series of EHD counts indexed by period (month or custom season).
    """
    df = daily.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["is_ehd"] = (df[tmax_col] >= threshold).astype(int)
    df["year_month"] = df[date_col].dt.to_period("M")
    return df.groupby("year_month")["is_ehd"].sum()


def growing_degree_days(
    daily: pd.DataFrame,
    tmean_col: str = "tmean",
    base: float = 10.0,
    date_col: str = "date",
) -> pd.Series:
    """Simple GDD: max(tmean - base, 0) summed by month."""
    df = daily.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["gdd"] = np.maximum(df[tmean_col] - base, 0.0)
    df["year_month"] = df[date_col].dt.to_period("M")
    return df.groupby("year_month")["gdd"].sum()


def harmful_degree_days(
    daily: pd.DataFrame,
    tmax_col: str = "tmax",
    threshold: float = 32.0,
    date_col: str = "date",
) -> pd.Series:
    """HDD: max(tmax - threshold, 0) summed by month."""
    df = daily.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["hdd"] = np.maximum(df[tmax_col] - threshold, 0.0)
    df["year_month"] = df[date_col].dt.to_period("M")
    return df.groupby("year_month")["hdd"].sum()


def soil_moisture_anomaly(
    monthly_sm: pd.Series,
    window: int = 5,
) -> pd.Series:
    """
    Simple z-score anomaly relative to trailing or expanding climatology.

    Parameters
    ----------
    monthly_sm : Series of monthly soil moisture (or precip) values
    window : years for climatology (if using rolling); ignored for full-sample z
    """
    # Full-sample z-score for simplicity; replace with month-of-year climatology in production
    return (monthly_sm - monthly_sm.mean()) / monthly_sm.std(ddof=0)


def composite_stress_index(
    ehd_anom: pd.Series,
    sm_anom: pd.Series,
    weights: tuple[float, float] = (0.6, 0.4),
) -> pd.Series:
    """
    Weighted combination of standardised EHD (positive = bad) and
    soil-moisture anomaly (negative = bad → we flip sign).
    """
    # Align indices
    common = ehd_anom.index.intersection(sm_anom.index)
    e = ehd_anom.loc[common]
    s = sm_anom.loc[common]
    # Higher EHD and lower SM both increase stress
    stress = weights[0] * e + weights[1] * (-s)
    return stress


# Example seasonal windows (Brazil Arabica focus)
BRAZIL_FLOWERING = [9, 10, 11, 12]   # Sep–Dec
BRAZIL_FILLING = [1, 2, 3]           # Jan–Mar


def seasonal_sum(series: pd.Series, months: list[int]) -> pd.Series:
    """Sum a monthly series over selected calendar months, by year."""
    # series index should be Period["M"] or DatetimeIndex
    if isinstance(series.index, pd.PeriodIndex):
        years = series.index.year
        mons = series.index.month
    else:
        years = series.index.year
        mons = series.index.month
    df = pd.DataFrame({"val": series.values, "year": years, "month": mons})
    mask = df["month"].isin(months)
    return df.loc[mask].groupby("year")["val"].sum()
