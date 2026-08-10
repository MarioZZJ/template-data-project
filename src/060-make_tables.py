#!/usr/bin/env python3
"""Create tracked CSV and TeX tables from validated interim summaries.

Purpose: Promote analysis summaries into stable formal tables for review and TeX use.
Inputs: data-quality, descriptive, regression, fit, performance, and diagnostics CSV files.
Outputs: paired CSV/TeX tables in outputs/tables/ plus formal influence CSV.
Run: uv run python src/060-make_tables.py
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Callable

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
OUTPUT_ROOT = resolve_root(os.environ.get("OUTPUT_ROOT"), ROOT / "outputs")
INTERIM_DIR = DATA_ROOT / "interim"
TABLE_DIR = OUTPUT_ROOT / "tables"

INPUTS = {
    "data-quality-summary": INTERIM_DIR / "data-quality-summary.csv",
    "descriptive-statistics": INTERIM_DIR / "descriptive-statistics.csv",
    "group-survival-rates": INTERIM_DIR / "group-survival-rates.csv",
    "logistic-regression-results": INTERIM_DIR / "logistic-regression-results.csv",
    "logistic-model-fit": INTERIM_DIR / "logistic-model-fit.csv",
    "model-performance": INTERIM_DIR / "model-performance.csv",
    "model-diagnostics": INTERIM_DIR / "model-diagnostics.csv",
    "influence-observations": INTERIM_DIR / "influence-observations.csv",
}


def tex_escape(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "--"
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in str(value))


def write_tex_table(
    frame: pd.DataFrame,
    path: Path,
    caption: str,
    label: str,
    headers: list[str],
    align: str | None = None,
    resize_to_width: bool = False,
) -> None:
    if frame.empty:
        raise ValueError(f"Cannot write empty formal table: {path}")
    alignment = align or ("l" + "r" * (len(frame.columns) - 1))
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{tex_escape(caption)}}}",
        rf"\label{{{label}}}",
        r"\small",
    ]
    if resize_to_width:
        lines.append(r"\resizebox{\linewidth}{!}{%")
    lines.extend([
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        " & ".join(tex_escape(header) for header in headers) + r" \\",
        r"\midrule",
    ])
    for row in frame.itertuples(index=False, name=None):
        lines.append(" & ".join(tex_escape(value) for value in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    if resize_to_width:
        lines.append("}")
    lines.append(r"\end{table}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def p_value(value: float) -> str:
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def save_csv(frame: pd.DataFrame, name: str) -> Path:
    path = TABLE_DIR / f"{name}.csv"
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")
    return path


def formalize_quality(frame: pd.DataFrame) -> None:
    save_csv(frame, "data-quality-summary")
    numeric = pd.to_numeric(frame["value"], errors="coerce")
    display = frame.loc[
        frame["metric"].isin(["row_count", "column_count", "duplicate_rows", "unique_key"])
        | ((frame["metric"] == "missing_count") & numeric.gt(0))
        | ((frame["metric"] == "invalid_value_count") & numeric.gt(0)),
        ["dataset", "metric", "variable", "value", "status"],
    ].copy()
    write_tex_table(
        display,
        TABLE_DIR / "data-quality-summary.tex",
        "Titanic source-data quality summary.",
        "tab:data-quality",
        ["Dataset", "Metric", "Variable", "Value", "Status"],
        "lllrl",
    )


def formalize_descriptive(frame: pd.DataFrame) -> None:
    save_csv(frame, "descriptive-statistics")
    display = frame.copy()
    for column in ["mean", "sd", "median", "q1", "q3", "minimum", "maximum"]:
        display[column] = display[column].map(lambda value: f"{value:.2f}")
    write_tex_table(
        display,
        TABLE_DIR / "descriptive-statistics.tex",
        "Descriptive statistics for the Titanic analysis sample.",
        "tab:descriptive",
        ["Variable", "N", "Missing", "Mean", "SD", "Median", "Q1", "Q3", "Min", "Max"],
        "lrrrrrrrrr",
        True,
    )


def formalize_group_rates(frame: pd.DataFrame) -> None:
    save_csv(frame, "group-survival-rates")
    display = frame[["dimension", "level", "n", "survived_n", "survival_rate", "ci_lower", "ci_upper"]].copy()
    display["survival_rate"] = display["survival_rate"].map(lambda value: f"{100 * value:.1f}%")
    display["ci_95"] = [
        f"{100 * lower:.1f}--{100 * upper:.1f}%"
        for lower, upper in zip(display.pop("ci_lower"), display.pop("ci_upper"), strict=True)
    ]
    write_tex_table(
        display,
        TABLE_DIR / "group-survival-rates.tex",
        "Observed survival rates by focal passenger characteristics.",
        "tab:group-rates",
        ["Dimension", "Level", "N", "Survived", "Rate", "95% CI"],
        "llrrrl",
    )


def formalize_regression(frame: pd.DataFrame) -> None:
    save_csv(frame, "logistic-regression-results")
    main = frame.loc[(frame["model"] == "Main model") & (frame["term"] != "const")].copy()
    main_display = pd.DataFrame(
        {
            "term": main["term_label"],
            "odds_ratio": main["odds_ratio"].map(lambda value: f"{value:.2f}"),
            "ci_95": [
                f"{lower:.2f}--{upper:.2f}"
                for lower, upper in zip(main["ci_lower_95"], main["ci_upper_95"], strict=True)
            ],
            "p_value": main["p_value"].map(p_value),
        }
    )
    write_tex_table(
        main_display,
        TABLE_DIR / "logistic-regression-results.tex",
        "Main Logistic regression associations with survival.",
        "tab:logit-main",
        ["Term", "Odds ratio", "95% CI", "p-value"],
        "lrrr",
    )

    main_terms = frame.loc[frame["model"] == "Main model", ["term", "term_label", "odds_ratio", "ci_lower_95", "ci_upper_95"]]
    sensitivity_terms = frame.loc[
        frame["model"] == "Complete-age sensitivity",
        ["term", "odds_ratio", "ci_lower_95", "ci_upper_95"],
    ]
    comparison = main_terms.merge(sensitivity_terms, on="term", suffixes=("_main", "_complete"))
    comparison = comparison.loc[comparison["term"] != "const"].copy()
    save_csv(comparison, "age-missing-sensitivity")
    comparison_display = pd.DataFrame(
        {
            "term": comparison["term_label"],
            "main": [
                f"{odds:.2f} ({lower:.2f}--{upper:.2f})"
                for odds, lower, upper in zip(
                    comparison["odds_ratio_main"],
                    comparison["ci_lower_95_main"],
                    comparison["ci_upper_95_main"],
                    strict=True,
                )
            ],
            "complete": [
                f"{odds:.2f} ({lower:.2f}--{upper:.2f})"
                for odds, lower, upper in zip(
                    comparison["odds_ratio_complete"],
                    comparison["ci_lower_95_complete"],
                    comparison["ci_upper_95_complete"],
                    strict=True,
                )
            ],
        }
    )
    write_tex_table(
        comparison_display,
        TABLE_DIR / "age-missing-sensitivity.tex",
        "Odds-ratio comparison for the main and complete-age models.",
        "tab:age-sensitivity",
        ["Term", "Main OR (95% CI)", "Complete-age OR (95% CI)"],
        "lrr",
    )


def formalize_fit(frame: pd.DataFrame) -> None:
    save_csv(frame, "logistic-model-fit")
    display = frame[["model", "n", "survived_n", "aic", "mcfadden_pseudo_r2", "likelihood_ratio_p_value", "converged"]].copy()
    display["aic"] = display["aic"].map(lambda value: f"{value:.1f}")
    display["mcfadden_pseudo_r2"] = display["mcfadden_pseudo_r2"].map(lambda value: f"{value:.3f}")
    display["likelihood_ratio_p_value"] = display["likelihood_ratio_p_value"].map(p_value)
    write_tex_table(
        display,
        TABLE_DIR / "logistic-model-fit.tex",
        "Logistic model fit summary.",
        "tab:logit-fit",
        ["Model", "N", "Survived", "AIC", "McFadden R2", "LR p-value", "Converged"],
        "lrrrrrl",
        True,
    )


def formalize_performance(frame: pd.DataFrame) -> None:
    save_csv(frame, "model-performance")
    display = frame[["metric", "out_of_fold_estimate", "fold_mean", "fold_sd", "folds", "random_seed"]].copy()
    for column in ["out_of_fold_estimate", "fold_mean", "fold_sd"]:
        display[column] = display[column].map(lambda value: f"{value:.3f}")
    write_tex_table(
        display,
        TABLE_DIR / "model-performance.tex",
        "Five-fold stratified cross-validation performance within train.csv.",
        "tab:model-performance",
        ["Metric", "OOF", "Fold mean", "Fold SD", "Folds", "Seed"],
        "lrrrrr",
    )


def formalize_diagnostics(frame: pd.DataFrame) -> None:
    save_csv(frame, "model-diagnostics")
    display = frame[["diagnostic", "term", "value", "reference", "flag"]].copy()
    display["value"] = display["value"].map(lambda value: f"{value:.3f}")
    write_tex_table(
        display,
        TABLE_DIR / "model-diagnostics.tex",
        "Main-model collinearity, influence, and calibration diagnostics.",
        "tab:model-diagnostics",
        ["Diagnostic", "Term", "Value", "Reference", "Flag"],
        "llrll",
        True,
    )


def main() -> int:
    missing = [str(path) for path in INPUTS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing formal-table inputs: {missing}")
    frames = {name: pd.read_csv(path) for name, path in INPUTS.items()}
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    formalizers: list[tuple[str, Callable[[pd.DataFrame], None]]] = [
        ("data-quality-summary", formalize_quality),
        ("descriptive-statistics", formalize_descriptive),
        ("group-survival-rates", formalize_group_rates),
        ("logistic-regression-results", formalize_regression),
        ("logistic-model-fit", formalize_fit),
        ("model-performance", formalize_performance),
        ("model-diagnostics", formalize_diagnostics),
    ]
    for name, formalizer in formalizers:
        formalizer(frames[name])

    save_csv(frames["influence-observations"], "influence-observations")
    expected = list(TABLE_DIR.glob("*.csv")) + list(TABLE_DIR.glob("*.tex"))
    if not expected or any(path.stat().st_size == 0 for path in expected):
        raise RuntimeError("One or more formal table files are missing or empty")
    print(f"formal tables: {TABLE_DIR}")
    print(f"files written: {len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
