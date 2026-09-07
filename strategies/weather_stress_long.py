"""
Weather-stress strategy on Arabica coffee futures (KC).

Supports real Open-Meteo ERA5 weather (default) or synthetic stress.
Long when stress elevated, light short when stress low.
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
    long_thresh: float = 1.0,
    short_thresh: float = -0.5,
    short_size: float = -0.5,
) -> pd.Series:
    signal = pd.Series(0.0, index=stress.index)
    signal[stress > long_thresh] = 1.0
    signal[stress < short_thresh] = short_size
    return signal


def main(
    start: str = "2015-01-01",
    source: str = "real",          # "real" or "synthetic"
    region: str = "sul_de_minas",
    long_thresh: float = 1.0,
    short_thresh: float = -0.5,
    cost_bps: float = 5.0,
    save_chart: str | None = "artifacts/stress_real_equity.png",
) -> pd.DataFrame:
    print(f"Loading KC=F and {source} weather stress ({region})...")
    price = load_coffee_futures(start=start)
    stress = load_stress(price, source=source, region=region)
    signal = build_signal(stress, long_thresh=long_thresh, short_thresh=short_thresh)

    bt = run_backtest(price, signal, cost_bps=cost_bps)
    bt["stress"] = stress

    stats = summarise(bt)
    print("\n=== Performance (annualised) ===")
    print(stats.round(3).to_string())
    if source == "real":
        print("\nUsing REAL Open-Meteo ERA5 weather (Sul de Minas).")
        print("Still a simple threshold strategy – not optimised alpha.\n")
    else:
        print("\nUsing SYNTHETIC stress (demo only).\n")

    if save_chart:
        Path(save_chart).parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(
            3, 1, figsize=(11, 8), sharex=True,
            gridspec_kw={"height_ratios": [3, 1.2, 0.8]},
        )

        axes[0].plot(bt.index, bt["equity"], label="Weather Stress L/S", color="#1f77b4", lw=1.6)
        axes[0].plot(bt.index, bt["bh_equity"], label="Buy & Hold KC", color="#ff7f0e", alpha=0.75, lw=1.1)
        axes[0].set_ylabel("Growth of $1")
        axes[0].legend(loc="upper left", framealpha=0.9)
        title_src = "REAL ERA5" if source == "real" else "SYNTHETIC"
        axes[0].set_title(
            f"Weather-Stress Long/Short vs Buy & Hold (KC=F)\n"
            f"Source: {title_src} • Region: {region}"
        )
        axes[0].grid(True, alpha=0.3)
        axes[0].set_yscale("log")

        axes[1].plot(bt.index, bt["stress"], color="#d62728", lw=0.9)
        axes[1].axhline(long_thresh, color="green", ls="--", lw=0.9, label="Long thresh")
        axes[1].axhline(short_thresh, color="purple", ls="--", lw=0.9, label="Short thresh")
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
    main(source="real")
