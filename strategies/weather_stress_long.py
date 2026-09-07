"""
Weather-stress strategy on Arabica coffee futures (KC)
with EWMA volatility targeting.

Features:
- Multi-point ERA5 weather (Sul de Minas / Cerrado / Mogiana)
- EHD ≥ 31 °C + Harmful Degree Days + precip anomaly
- 1-month publication lag on stress
- EWMA vol targeting (default 10% annualised)
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
    target_vol: float | None = 0.10,
    vol_span: int = 30,
    save_chart: str | None = "artifacts/stress_voltarget_equity.png",
) -> pd.DataFrame:
    print(f"Loading KC=F + {source} multi-point lagged weather stress...")
    price = load_coffee_futures(start=start)
    stress = load_stress(price, source=source)
    signal = build_signal(stress, long_thresh=long_thresh, short_thresh=short_thresh)

    bt = run_backtest(
        price,
        signal,
        cost_bps=cost_bps,
        target_vol=target_vol,
        vol_span=vol_span,
    )
    bt["stress"] = stress

    stats = summarise(bt)
    print("\n=== Performance (annualised) ===")
    print(stats.round(3).to_string())
    if target_vol is not None:
        print(f"\nEWMA vol targeting ON  → target={target_vol:.0%}  span={vol_span}")
    else:
        print("\nVol targeting OFF")
    print("Multi-point ERA5 · EHD 31°C + HDD · 1-month lag\n")

    if save_chart:
        Path(save_chart).parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(
            4, 1, figsize=(11, 9), sharex=True,
            gridspec_kw={"height_ratios": [3, 1.0, 0.8, 0.8]},
        )

        axes[0].plot(bt.index, bt["equity"], label="Stress + Vol Target", color="#1f77b4", lw=1.6)
        axes[0].plot(bt.index, bt["bh_equity"], label="Buy & Hold KC", color="#ff7f0e", alpha=0.75, lw=1.1)
        axes[0].set_ylabel("Growth of $1")
        axes[0].legend(loc="upper left", framealpha=0.9)
        title = "Weather-Stress + EWMA Vol Targeting vs Buy & Hold (KC=F)"
        if target_vol:
            title += f"\nTarget vol {target_vol:.0%} · multi-point ERA5 · 1-month lag"
        axes[0].set_title(title)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_yscale("log")

        axes[1].plot(bt.index, bt["stress"], color="#d62728", lw=0.9)
        axes[1].axhline(long_thresh, color="green", ls="--", lw=0.8)
        axes[1].axhline(short_thresh, color="purple", ls="--", lw=0.8)
        axes[1].set_ylabel("Stress")
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(bt.index, bt["vol_weight"], color="#2ca02c", lw=0.9)
        axes[2].set_ylabel("Vol weight")
        axes[2].grid(True, alpha=0.3)

        axes[3].fill_between(bt.index, bt["position"], step="pre", alpha=0.5, color="#1f77b4")
        axes[3].set_ylabel("Position")
        axes[3].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_chart, dpi=130, bbox_inches="tight")
        print(f"Chart saved → {save_chart}")
        plt.close()

    return bt


if __name__ == "__main__":
    main(source="real", target_vol=0.10)
