"""
Real weather data integration for coffee regions.

Uses Open-Meteo Historical Weather API (ERA5 based).
No API key required for non-commercial use.

Improvements:
- Multi-point average across Sul de Minas / Cerrado / Mogiana
- Lower EHD threshold (31 °C) + Harmful Degree Days
- Proper 1-month publication lag on stress
"""

from __future__ import annotations

import time
from typing import Optional, Sequence

import numpy as np
import pandas as pd
import requests

# Representative points in major Brazilian Arabica zones
BRAZIL_COFFEE_POINTS = {
    "sul_de_minas": (-21.55, -45.43),      # Varginha / Três Pontas
    "cerrado_mineiro": (-18.92, -46.99),  # Patrocínio
    "mogiana": (-22.25, -46.75),          # Guaxupé area
    "sul_minas_2": (-21.15, -44.95),      # extra Sul de Minas point
    "cerrado_2": (-19.45, -46.55),        # extra Cerrado point
}

DEFAULT_REGIONS = ["sul_de_minas", "cerrado_mineiro", "mogiana", "sul_minas_2", "cerrado_2"]

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def fetch_daily_weather(
    lat: float,
    lon: float,
    start: str = "2015-01-01",
    end: Optional[str] = None,
    timezone: str = "America/Sao_Paulo",
    max_retries: int = 3,
) -> pd.DataFrame:
    """Fetch daily Tmax, Tmin, precipitation from Open-Meteo (ERA5)."""
    if end is None:
        end = pd.Timestamp.today().strftime("%Y-%m-%d")

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone,
    }

    last_err = None
    for attempt in range(max_retries):
        try:
            r = requests.get(OPEN_METEO_ARCHIVE, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            if "daily" not in data:
                raise ValueError(f"Unexpected response: {list(data.keys())}")
            daily = data["daily"]
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(daily["time"]),
                    "tmax": daily["temperature_2m_max"],
                    "tmin": daily["temperature_2m_min"],
                    "precip": daily["precipitation_sum"],
                }
            )
            df = df.set_index("date").sort_index()
            df["tmean"] = (df["tmax"] + df["tmin"]) / 2.0
            return df
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch weather after {max_retries} retries: {last_err}")


def fetch_multi_point(
    regions: Sequence[str] = DEFAULT_REGIONS,
    start: str = "2015-01-01",
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch daily weather for several points and average them.
    Returns a single DataFrame with mean tmax / tmin / precip.
    """
    frames = []
    for name in regions:
        if name not in BRAZIL_COFFEE_POINTS:
            raise ValueError(f"Unknown region '{name}'")
        lat, lon = BRAZIL_COFFEE_POINTS[name]
        df = fetch_daily_weather(lat, lon, start=start, end=end)
        df = df.add_suffix(f"_{name}")
        frames.append(df)
        time.sleep(0.4)  # be polite to the free API

    combined = pd.concat(frames, axis=1)
    out = pd.DataFrame(index=combined.index)
    out["tmax"] = combined[[c for c in combined.columns if c.startswith("tmax_")]].mean(axis=1)
    out["tmin"] = combined[[c for c in combined.columns if c.startswith("tmin_")]].mean(axis=1)
    out["precip"] = combined[[c for c in combined.columns if c.startswith("precip_")]].mean(axis=1)
    out["tmean"] = (out["tmax"] + out["tmin"]) / 2.0
    return out


def compute_ehd_series(
    daily: pd.DataFrame,
    threshold: float = 31.0,
    tmax_col: str = "tmax",
) -> pd.Series:
    """Monthly Extreme Heat Day counts (days with Tmax >= threshold)."""
    s = (daily[tmax_col] >= threshold).astype(int)
    return s.resample("ME").sum().rename("ehd")


def compute_hdd_series(
    daily: pd.DataFrame,
    threshold: float = 30.0,
    tmax_col: str = "tmax",
) -> pd.Series:
    """Monthly Harmful Degree Days: sum of max(Tmax - threshold, 0)."""
    hdd = np.maximum(daily[tmax_col] - threshold, 0.0)
    return hdd.resample("ME").sum().rename("hdd")


def compute_precip_anomaly(
    daily: pd.DataFrame,
    precip_col: str = "precip",
    lookback_months: int = 12,
) -> pd.Series:
    """Z-score of monthly precipitation vs trailing history."""
    monthly = daily[precip_col].resample("ME").sum()
    roll_mean = monthly.rolling(lookback_months, min_periods=6).mean()
    roll_std = monthly.rolling(lookback_months, min_periods=6).std()
    anom = (monthly - roll_mean) / roll_std.replace(0, np.nan)
    return anom.rename("precip_anom").fillna(0)


def build_real_stress(
    daily: pd.DataFrame,
    ehd_threshold: float = 31.0,
    hdd_threshold: float = 30.0,
    ehd_weight: float = 0.35,
    hdd_weight: float = 0.25,
    precip_weight: float = 0.40,
) -> pd.Series:
    """
    Composite monthly stress:

        stress = w_ehd * z(EHD) + w_hdd * z(HDD) + w_precip * (-precip_anom)
    """
    ehd = compute_ehd_series(daily, threshold=ehd_threshold)
    hdd = compute_hdd_series(daily, threshold=hdd_threshold)
    precip_anom = compute_precip_anomaly(daily)

    common = ehd.index.intersection(hdd.index).intersection(precip_anom.index)
    ehd = ehd.loc[common]
    hdd = hdd.loc[common]
    precip_anom = precip_anom.loc[common]

    def z(s: pd.Series) -> pd.Series:
        return (s - s.mean()) / (s.std() + 1e-6)

    stress = (
        ehd_weight * z(ehd)
        + hdd_weight * z(hdd)
        + precip_weight * (-precip_anom)
    )
    return stress.clip(-2.5, 4.0).rename("stress")


def build_lagged_stress(
    daily: pd.DataFrame,
    lag_months: int = 1,
    **stress_kwargs,
) -> pd.Series:
    """
    Build stress and shift it forward by `lag_months` so that
    weather observed in month t only affects positions from month t+lag onward.
    """
    stress = build_real_stress(daily, **stress_kwargs)
    # Shift the index forward by lag_months (publication / decision lag)
    stress = stress.shift(lag_months)
    return stress.dropna()
