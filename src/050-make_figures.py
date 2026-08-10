#!/usr/bin/env python3
"""Create the formal Titanic survival-rate and odds-ratio figures.

Purpose: Visualize grouped survival rates and adjusted Logistic associations.
Inputs: group-survival-rates.csv and logistic-regression-results.csv in data/interim/.
Outputs: two tracked PDF figures in outputs/figures/.
Run: uv run python src/050-make_figures.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parent.parent


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
OUTPUT_ROOT = resolve_root(os.environ.get("OUTPUT_ROOT"), ROOT / "outputs")
GROUP_PATH = DATA_ROOT / "interim" / "group-survival-rates.csv"
REGRESSION_PATH = DATA_ROOT / "interim" / "logistic-regression-results.csv"
FIGURE_DIR = OUTPUT_ROOT / "figures"
SURVIVAL_FIGURE = FIGURE_DIR / "survival-rates-by-characteristics.pdf"
ODDS_RATIO_FIGURE = FIGURE_DIR / "main-model-odds-ratios.pdf"
PDF_METADATA = {
    "Creator": "src/050-make_figures.py",
    "CreationDate": None,
    "ModDate": None,
}


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def make_survival_figure(grouped: pd.DataFrame) -> None:
    panels = [
        ("Sex", "Sex"),
        ("Pclass", "Passenger class"),
        ("AgeGroup", "Age group"),
        ("FamilyGroup", "Family group"),
    ]
    figure, axes = plt.subplots(2, 2, figsize=(8.2, 6.4), sharey=True)
    color = "#3366A6"

    for axis, (dimension, title) in zip(axes.flat, panels, strict=True):
        panel = grouped.loc[grouped["dimension"] == dimension].sort_values("sort_order")
        positions = np.arange(len(panel))
        rates = panel["survival_rate"].to_numpy()
        lower = rates - panel["ci_lower"].to_numpy()
        upper = panel["ci_upper"].to_numpy() - rates
        axis.errorbar(
            positions,
            rates,
            yerr=np.vstack([lower, upper]),
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
            linewidth=1.2,
        )
        axis.set_xticks(positions, panel["level"], rotation=20, ha="right")
        axis.set_ylim(0, 1)
        axis.yaxis.set_major_formatter(PercentFormatter(1.0))
        axis.set_title(title, loc="left")
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        for position, row in zip(positions, panel.itertuples(), strict=True):
            axis.text(position, 0.03, f"n={row.n}", ha="center", va="bottom", fontsize=7, color="#444444")

    axes[0, 0].set_ylabel("Observed survival rate")
    axes[1, 0].set_ylabel("Observed survival rate")
    figure.suptitle("Titanic survival rates by passenger characteristics", x=0.08, ha="left", fontsize=12)
    figure.text(
        0.08,
        0.01,
        "Points are observed proportions; bars are 95% Wilson intervals. These are descriptive associations.",
        fontsize=8,
    )
    figure.tight_layout(rect=[0, 0.04, 1, 0.95])
    figure.savefig(SURVIVAL_FIGURE, bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(figure)


def make_odds_ratio_figure(regression: pd.DataFrame) -> None:
    panel = regression.loc[
        (regression["model"] == "Main model") & (regression["term"] != "const")
    ].copy()
    panel = panel.iloc[::-1].reset_index(drop=True)
    positions = np.arange(len(panel))
    odds = panel["odds_ratio"].to_numpy()
    lower = odds - panel["ci_lower_95"].to_numpy()
    upper = panel["ci_upper_95"].to_numpy() - odds

    figure, axis = plt.subplots(figsize=(7.4, 5.1))
    axis.errorbar(
        odds,
        positions,
        xerr=np.vstack([lower, upper]),
        fmt="o",
        color="#B14E3B",
        ecolor="#B14E3B",
        capsize=3,
        linewidth=1.2,
    )
    axis.axvline(1.0, color="#555555", linestyle="--", linewidth=0.9)
    axis.set_xscale("log")
    axis.set_yticks(positions, panel["term_label"])
    axis.set_xlabel("Odds ratio (log scale, 95% confidence interval)")
    axis.set_title("Adjusted associations with Titanic survival", loc="left", fontsize=12)
    axis.grid(axis="x", color="#D9D9D9", linewidth=0.6)
    figure.text(
        0.16,
        0.01,
        "The model describes conditional associations in train.csv and does not identify causal effects.",
        fontsize=8,
    )
    figure.tight_layout(rect=[0, 0.04, 1, 1])
    figure.savefig(ODDS_RATIO_FIGURE, bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(figure)


def main() -> int:
    for path in (GROUP_PATH, REGRESSION_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Missing figure input: {path}")
    grouped = pd.read_csv(GROUP_PATH)
    regression = pd.read_csv(REGRESSION_PATH)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    configure_style()
    make_survival_figure(grouped)
    make_odds_ratio_figure(regression)
    for path in (SURVIVAL_FIGURE, ODDS_RATIO_FIGURE):
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Figure was not created: {path}")
        print(f"formal figure: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
