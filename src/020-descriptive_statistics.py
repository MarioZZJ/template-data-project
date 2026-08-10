#!/usr/bin/env python3
"""Produce descriptive statistics and grouped Titanic survival rates.

Purpose: Describe the analysis sample and survival rates for the focal characteristics.
Inputs: data/processed/titanic-analysis.csv.
Outputs: data/interim/descriptive-statistics.csv and data/interim/group-survival-rates.csv.
Run: uv run python src/020-descriptive_statistics.py
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
ANALYSIS_PATH = DATA_ROOT / "processed" / "titanic-analysis.csv"
INTERIM_DIR = DATA_ROOT / "interim"
DESCRIPTIVE_PATH = INTERIM_DIR / "descriptive-statistics.csv"
GROUP_PATH = INTERIM_DIR / "group-survival-rates.csv"


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    proportion = successes / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def descriptive_rows(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for variable in ["Survived", "Age", "Fare", "FamilySize"]:
        values = frame[variable].dropna()
        rows.append(
            {
                "variable": variable,
                "n": int(values.size),
                "missing": int(frame[variable].isna().sum()),
                "mean": float(values.mean()),
                "sd": float(values.std(ddof=1)),
                "median": float(values.median()),
                "q1": float(values.quantile(0.25)),
                "q3": float(values.quantile(0.75)),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
        )
    return rows


def grouped_rows(frame: pd.DataFrame) -> list[dict[str, object]]:
    specifications: list[tuple[str, list[object], dict[object, str]]] = [
        ("Sex", ["female", "male"], {"female": "Female", "male": "Male"}),
        ("Pclass", [1, 2, 3], {1: "First class", 2: "Second class", 3: "Third class"}),
        (
            "AgeGroup",
            ["Child (<18)", "Adult (18-59)", "Older (60+)", "Missing"],
            {},
        ),
        (
            "FamilyGroup",
            ["Alone", "Small (2-4)", "Large (5+)"],
            {},
        ),
        (
            "TravelAlone",
            [0, 1],
            {0: "With family", 1: "Travelling alone"},
        ),
    ]

    rows: list[dict[str, object]] = []
    for dimension, levels, labels in specifications:
        for sort_order, level in enumerate(levels):
            subset = frame.loc[frame[dimension] == level]
            total = int(len(subset))
            survived = int(subset["Survived"].sum())
            lower, upper = wilson_interval(survived, total)
            rows.append(
                {
                    "dimension": dimension,
                    "level": labels.get(level, str(level)),
                    "sort_order": sort_order,
                    "n": total,
                    "survived_n": survived,
                    "survival_rate": survived / total if total else math.nan,
                    "ci_lower": lower,
                    "ci_upper": upper,
                }
            )
    return rows


def main() -> int:
    if not ANALYSIS_PATH.is_file():
        raise FileNotFoundError(f"Missing analysis data: {ANALYSIS_PATH}")

    frame = pd.read_csv(ANALYSIS_PATH)
    required = {
        "PassengerId",
        "Survived",
        "Pclass",
        "Sex",
        "Age",
        "AgeGroup",
        "FamilySize",
        "FamilyGroup",
        "TravelAlone",
        "Fare",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Analysis data is missing required columns: {missing}")
    if not frame["Survived"].isin([0, 1]).all():
        raise ValueError("Survived must contain only 0 and 1")

    descriptive = pd.DataFrame(descriptive_rows(frame))
    grouped = pd.DataFrame(grouped_rows(frame))
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    descriptive.to_csv(DESCRIPTIVE_PATH, index=False, lineterminator="\n", float_format="%.8g")
    grouped.to_csv(GROUP_PATH, index=False, lineterminator="\n", float_format="%.8g")

    print(f"descriptive statistics: {DESCRIPTIVE_PATH}")
    print(f"group survival rates: {GROUP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
