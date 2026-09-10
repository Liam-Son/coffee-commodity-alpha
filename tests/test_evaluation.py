from src.evaluation import deflated_sharpe, turnover_stats
import pandas as pd


def test_dsr_between_zero_and_one():
    out = deflated_sharpe(sharpe=0.45, n_obs=2500, n_trials=8)
    assert 0.0 <= out["dsr"] <= 1.0


def test_turnover_fractions_sum_to_one():
    pos = pd.Series([1, 1, 0, 0, -0.4, -0.4])
    t = turnover_stats(pos)
    s = t["frac_long"] + t["frac_short"] + t["frac_flat"]
    assert abs(s - 1.0) < 1e-12
