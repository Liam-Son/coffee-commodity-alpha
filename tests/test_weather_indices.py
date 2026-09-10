import numpy as np
import pandas as pd

from src.weather_indices import extreme_heat_days, harmful_degree_days, growing_degree_days
from src.weather_data import compute_ehd_series, compute_hdd_series, build_real_stress


def _daily(n=60):
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    tmax = pd.Series(np.linspace(25, 36, n), index=idx)
    return pd.DataFrame({"date": idx, "tmax": tmax.values, "tmean": tmax.values - 4, "precip": 2.0}, index=idx)


def test_ehd_counts_days_above_threshold():
    d = _daily()
    raw = pd.DataFrame({"date": d.index, "tmax": d["tmax"].values})
    ehd_jan = extreme_heat_days(raw, threshold=33.0)
    assert ehd_jan.sum() >= 1


def test_hdd_zero_when_below_threshold():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    raw = pd.DataFrame({"date": idx, "tmax": 20.0})
    h = harmful_degree_days(raw, threshold=32.0)
    assert (h == 0).all()


def test_gdd_nonnegative():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    raw = pd.DataFrame({"date": idx, "tmean": 8.0})
    g = growing_degree_days(raw, base=10.0)
    assert (g == 0).all()


def test_monthly_ehd_hdd_and_stress_finite():
    d = _daily(400)
    d.index.name = "date"
    ehd = compute_ehd_series(d, threshold=31.0)
    hdd = compute_hdd_series(d, threshold=30.0)
    assert ehd.min() >= 0
    assert hdd.min() >= 0
    stress = build_real_stress(d, ehd_threshold=31.0)
    assert np.isfinite(stress.dropna()).all()
