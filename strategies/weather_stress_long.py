"""
Weather-stress strategy (long/short) on Arabica coffee futures (KC).

Long when synthetic stress is elevated, light short when stress is low.
This is still a framework demo – replace the synthetic stress with real
Extreme-Heat-Day / soil-moisture indices from src/weather_indices.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.data_loaders import load_coffee_futures, synthetic_stress
from src.backtest import run_backtest, summarise


def build_signal(
    stress: pd.Series,
    long_thresh: float = 1.2,
    short_thresh: float = -0.2,
    short_size: float = -0.5,
) -> pd.Series:
    """
    Long (+1) when stress > long_thresh
    Light short (short_size) when stress < short_thresh
    Flat otherwise.
    """
    signal = pd.Series(0.0, index=stress.index)
    signal[stress > long_thresh] = 1.0
    signal[stress < short_thresh] = short_size
    return signal


def main(
    start: str = "2015-01-01",
    long_thresh: float = 1.2,
    short_thresh: float = -0.2,
    cost_bps: float = 5.0,
    save_chart: str | None = "artifacts/stress_ls_equity.png",
) -> pd.DataFrame:
    price = load_coffee_futures(start=start)
    stress = synthetic_stress(price)
    signal = build_signal(stress, long_thresh=long_thresh, short_thresh=short_thresh)

    bt = run_backtest(price, signal, cost_bps=cost_bps)
    bt["stress"] = stress

    stats = summarise(bt)
    print("\n=== Performance (annualised) ===")
    print(stats.round(3).to_string())
    print("\nNote: stress series is SYNTHETIC (seasonal + shocks) for framework demo.")
    print("Replace with real weather indices for meaningful alpha research.\n")

    if save_chart:
        Path(save_chart).parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(
            3, 1, figsize=(11, 8), sharex=True,
            gridspec_kw={"height_ratios": [3, 1.2, 0.8]},
        )

        axes[0].plot(bt.index, bt["equity"], label="Stress L/S", color="#1f77b4", lw=1.6)
        axes[0].plot(bt.index, bt["bh_equity"], label="Buy & Hold KC", color="#ff7f0e", alpha=0.75, lw=1.1)
        axes[0].set_ylabel("Growth of $1")
        axes[0].legend(loc="upper left", framealpha=0.9)
        axes[0].set_title(
            "Weather-Stress Long/Short vs Buy & Hold (KC=F)\n"
            "Demo with seasonal synthetic stress – replace with real EHD / soil-moisture indices"
        )
        axes[0].grid(True, alpha=0.3)
        axes[0].set_yscale("log")

        axes[1].plot(bt.index, bt["stress"], color="#d62728", lw=0.9)
        axes[1].axhline(long_thresh, color="green", ls="--", lw=0.9, label="Long threshold")
        axes[1].axhline(short_thresh, color="purple", ls="--", lw=0.9, label="Short threshold")
        axes[1].set_ylabel("Stress")
        axes[1].legend(loc="upper right", fontsize=8)
        axes[1].grid(True, alpha=0.3)

        axes[2].fill_between(bt.index, bt["position"], step="pre", alpha=0.5, color="#1f77b4")
        axes[2].set_ylabel("Position")
        axes[2].set_ylim(-0.7, 1.2)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_chart, dpi=130, bbox_inches="tight")
        print(f"Chart saved → {save_chart}")
        plt.close()

    return bt


if __name__ == "__main__":
    main()
