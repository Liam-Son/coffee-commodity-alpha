"""
Improved weather-stress strategy on Arabica coffee futures (KC).

Changes vs original:
- Multi-point average (5 locations across Sul de Minas / Cerrado / Mogiana)
- EHD threshold lowered to 31 °C + Harmful Degree Days
- 1-month publication lag on stress (no look-ahead)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.data_loaders import load_coffee_futures, load_stress
from src.backtest import run_backtest, summarise


def build_signal(
    stress: pd.Series,
    long_thresh: float = 0.8,
    short_thresh: float = -0.6,
    short_size: float = -0.4,
) -> pd.Series:
    signal = pd.Series(0.0, index=stress.index)
    signal[stress > long_thresh] = 1.0
    signal[stress < short_thresh] = short_size
    return signal


def main(
    start: str = "2015-01-01",
    source: str = "real",
    long_thresh: float = 0.8,
    short_thresh: float = -0.6,
    cost_bps: float = 5.0,
    save_chart: str | None = "artifacts/stress_improved_equity.png",
) -> pd.DataFrame:
    print(f"Loading KC=F + {source} multi-point lagged weather stress...")
    price = load_coffee_futures(start=start)
    stress = load_stress(price, source=source)
    signal = build_signal(stress, long_thresh=long_thresh, short_thresh=short_thresh)

    bt = run_backtest(price, signal, cost_bps=cost_bps)
    bt["stress"] = stress

    stats = summarise(bt)
    print("\n=== Performance (annualised) ===")
    print(stats.round(3).to_string())
    print("\nImprovements active: multi-point avg · EHD 31°C + HDD · 1-month lag")
    print("Still a simple threshold rule – not fully optimised.\n")

    if save_chart:
        Path(save_chart).parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(
            3, 1, figsize=(11, 8), sharex=True,
            gridspec_kw={"height_ratios": [3, 1.2, 0.8]},
        )
        axes[0].plot(bt.index, bt["equity"], label="Improved Stress L/S", color="#1f77b4", lw=1.6)
        axes[0].plot(bt.index, bt["bh_equity"], label="Buy & Hold KC", color="#ff7f0e", alpha=0.75, lw=1.1)
        axes[0].set_ylabel("Growth of $1")
        axes[0].legend(loc="upper left", framealpha=0.9)
        axes[0].set_title(
            "Improved Weather-Stress Strategy vs Buy & Hold (KC=F)\n"
            "Multi-point ERA5 · EHD≥31°C + HDD · 1-month lag"
        )
        axes[0].grid(True, alpha=0.3)
        axes[0].set_yscale("log")

        axes[1].plot(bt.index, bt["stress"], color="#d62728", lw=0.9)
        axes[1].axhline(long_thresh, color="green", ls="--", lw=0.9, label="Long")
        axes[1].axhline(short_thresh, color="purple", ls="--", lw=0.9, label="Short")
        axes[1].set_ylabel("Stress (lagged)")
        axes[1].legend(loc="upper right", fontsize=8)
        axes[1].grid(True, alpha=0.3)

        axes[2].fill_between(bt.index, bt["position"], step="pre", alpha=0.5, color="#1f77b4")
        axes[2].set_ylabel("Position")
        axes[2].set_ylim(-0.6, 1.2)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_chart, dpi=130, bbox_inches="tight")
        print(f"Chart saved → {save_chart}")
        plt.close()

    return bt


if __name__ == "__main__":
    main(source="real")
