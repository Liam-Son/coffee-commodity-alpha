import numpy as np
import pandas as pd

from src.backtest import run_backtest, ewma_vol, vol_target_weights, performance_stats


def _toy_price(n=400, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, 0.015, n)
    idx = pd.bdate_range("2020-01-01", periods=n)
    px = 100 * np.exp(np.cumsum(r))
    return pd.Series(px, index=idx, name="price")


def test_flat_signal_matches_cash():
    px = _toy_price()
    sig = pd.Series(0.0, index=px.index)
    bt = run_backtest(px, sig, cost_bps=0.0)
    assert abs(bt["strat_ret"].fillna(0).sum()) < 1e-12
    assert np.isclose(bt["equity"].iloc[-1], 1.0)


def test_full_long_no_cost_matches_buyhold():
    px = _toy_price()
    sig = pd.Series(1.0, index=px.index)
    bt = run_backtest(px, sig, cost_bps=0.0, position_lag=0)
    # lag 0 + unit position => strategy returns = asset returns after first bar alignment
    err = (bt["strat_ret"] - bt["ret"]).dropna().abs().max()
    assert err < 1e-12


def test_costs_reduce_equity_when_churning():
    px = _toy_price()
    sig = pd.Series(np.resize([1.0, 0.0], len(px)), index=px.index)
    cheap = run_backtest(px, sig, cost_bps=0.0)
    dear = run_backtest(px, sig, cost_bps=50.0)
    assert dear["equity"].iloc[-1] < cheap["equity"].iloc[-1]


def test_ewma_vol_is_lagged_and_positive():
    px = _toy_price()
    r = px.pct_change()
    sig = ewma_vol(r, span=20, lag=1)
    assert sig.dropna().min() > 0
    # first non-null cannot be on day 0
    assert sig.isna().sum() >= 1


def test_vol_weights_clipped():
    px = _toy_price()
    w = vol_target_weights(px.pct_change(), target_vol=0.10, w_min=0.25, w_max=2.0)
    assert w.min() >= 0.25 - 1e-12
    assert w.max() <= 2.0 + 1e-12


def test_performance_stats_keys():
    px = _toy_price()
    bt = run_backtest(px, pd.Series(1.0, index=px.index), cost_bps=0.0)
    s = performance_stats(bt["strat_ret"])
    for k in ("CAGR", "Vol", "Sharpe", "MaxDD", "HitRate", "N"):
        assert k in s
