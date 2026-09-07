"""
Minimal first strategy: Long coffee when weather-stress proxy is elevated.

This is intentionally simple so the backtest framework can be validated.
Replace the synthetic stress with real Extreme-Heat-Day / soil-moisture
indices from src/weather_indices.py for production research.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

from src.data_loaders import load_coffee_futures, synthetic_stress
from src.backtest import run_backtest, summarise


def build_signal(stress: pd.Series, threshold: float = 1.0) -> pd.Series:
    """Long (1) when stress > threshold, otherwise flat (0)."""
    return (stress > threshold).astype(float)


def main(
    start: str = "2015-01-01",
    threshold: float = 1.0,
    cost_bps: float = 5.0,
    save_chart: str | None = "artifacts/first_strategy_equity.png",
) -> pd.DataFrame:
    price = load_coffee_futures(start=start)
    stress = synthetic_stress(price)
    signal = build_signal(stress, threshold=threshold)

    bt = run_backtest(price, signal, cost_bps=cost_bps)
    bt["stress"] = stress

    stats = summarise(bt)
    print("\n=== Performance (annualised) ===")
    print(stats.round(3).to_string())
    print("\nNote: stress series is SYNTHETIC for framework demo.")
    print("Replace with real weather indices for meaningful results.\n")

    if save_chart:
        Path(save_chart).parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(
            3, 1, figsize=(10, 8), sharex=True,
            gridspec_kw={"height_ratios": [3, 1, 1]},
        )
        axes[0].plot(bt.index, bt["equity"], label="Weather-Stress Long", color="C0", lw=1.5)
        axes[0].plot(bt.index, bt["bh_equity"], label="Buy & Hold KC", color="C1", alpha=0.7, lw=1)
        axes[0].set_ylabel("Growth of $1")
        axes[0].legend(loc="upper left")
        axes[0].set_title(
            "Minimal Weather-Stress Strategy vs Buy & Hold (KC=F)\n"
            "(Demo with synthetic stress – replace with real EHD / soil-moisture indices)"
        )
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(bt.index, bt["stress"], color="C3", lw=0.8)
        axes[1].axhline(threshold, color="k", ls="--", lw=0.8)
        axes[1].set_ylabel("Stress")
        axes[1].grid(True, alpha=0.3)

        axes[2].fill_between(bt.index, bt["position"], step="pre", alpha=0.4, color="C0")
        axes[2].set_ylabel("Position")
        axes[2].set_ylim(-0.05, 1.05)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_chart, dpi=120, bbox_inches="tight")
        print(f"Chart saved → {save_chart}")
        plt.close()

    return bt


if __name__ == "__main__":
    main()
