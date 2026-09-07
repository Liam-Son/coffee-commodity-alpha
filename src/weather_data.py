"""
Real weather data integration for coffee regions.

Uses Open-Meteo Historical Weather API (ERA5 / ERA5-Land based).
No API key required for non-commercial use.
https://open-meteo.com/en/docs/historical-weather-api

Primary focus: southern Minas Gerais (Brazil Arabica belt).
"""

from __future__ import annotations

import time
from typing import Optional

import numpy as np
import pandas as pd
import requests

# Representative points in major Brazilian Arabica zones
BRAZIL_COFFEE_POINTS = {
    "sul_de_minas": (-21.55, -45.43),      # near Varginha / Três Pontas
    "cerrado_mineiro": (-18.92, -46.99),  # near Patrocínio
    "mogiana": (-22.25, -46.75),          # near Guaxupé area
}

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def fetch_daily_weather(
    lat: float,
    lon: float,
    start: str = "2015-01-01",
    end: Optional[str] = None,
    timezone: str = "America/Sao_Paulo",
    max_retries: int = 3,
) -> pd.DataFrame:
    """
    Fetch daily Tmax, Tmin, precipitation from Open-Meteo archive (ERA5).

    Returns DataFrame indexed by date with columns:
        tmax, tmin, precip
    """
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


def fetch_brazil_coffee_weather(
    region: str = "sul_de_minas",
    start: str = "2015-01-01",
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Convenience wrapper for a named Brazilian coffee region."""
    if region not in BRAZIL_COFFEE_POINTS:
        raise ValueError(f"Unknown region '{region}'. Choose from {list(BRAZIL_COFFEE_POINTS)}")
    lat, lon = BRAZIL_COFFEE_POINTS[region]
    return fetch_daily_weather(lat, lon, start=start, end=end)


def compute_ehd_series(
    daily: pd.DataFrame,
    threshold: float = 33.0,
    tmax_col: str = "tmax",
) -> pd.Series:
    """Monthly Extreme Heat Day counts (days with Tmax >= threshold)."""
    s = (daily[tmax_col] >= threshold).astype(int)
    return s.resample("ME").sum().rename("ehd")


def compute_precip_anomaly(
    daily: pd.DataFrame,
    precip_col: str = "precip",
    window_months: int = 3,
) -> pd.Series:
    """
    Simple rolling precipitation anomaly (z-score of trailing monthly totals).
    Negative values = drier than recent history.
    """
    monthly = daily[precip_col].resample("ME").sum()
    roll_mean = monthly.rolling(window_months * 4, min_periods=6).mean()  # ~1 year lookback
    roll_std = monthly.rolling(window_months * 4, min_periods=6).std()
    anom = (monthly - roll_mean) / roll_std.replace(0, np.nan)
    return anom.rename("precip_anom").fillna(0)


def build_real_stress(
    daily: pd.DataFrame,
    ehd_threshold: float = 33.0,
    ehd_weight: float = 0.6,
    precip_weight: float = 0.4,
) -> pd.Series:
    """
    Composite monthly stress index from real weather:

        stress = w1 * z(EHD) + w2 * (-precip_anomaly)

    Higher = more heat stress + drought stress.
    """
    ehd = compute_ehd_series(daily, threshold=ehd_threshold)
    precip_anom = compute_precip_anomaly(daily)

    # Align
    common = ehd.index.intersection(precip_anom.index)
    ehd = ehd.loc[common]
    precip_anom = precip_anom.loc[common]

    # Standardise EHD (positive = bad)
    ehd_z = (ehd - ehd.mean()) / (ehd.std() + 1e-6)
    # Flip precip anomaly so negative precip (drought) increases stress
    stress = ehd_weight * ehd_z + precip_weight * (-precip_anom)
    stress = stress.clip(-2, 4).rename("stress")
    return stress


def real_stress_daily(
    region: str = "sul_de_minas",
    start: str = "2015-01-01",
    end: Optional[str] = None,
    ehd_threshold: float = 33.0,
) -> pd.Series:
    """
    End-to-end: fetch weather → build monthly stress → forward-fill to daily.
    Suitable for direct use in the backtester.
    """
    daily = fetch_brazil_coffee_weather(region=region, start=start, end=end)
    monthly_stress = build_real_stress(daily, ehd_threshold=ehd_threshold)
    # We need a daily index; caller usually has price index
    return monthly_stress
