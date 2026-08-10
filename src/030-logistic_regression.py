#!/usr/bin/env python3
"""Estimate the main and age-missing-sensitivity Logistic models.

Purpose: Quantify conditional associations with survival using interpretable odds ratios.
Inputs: data/processed/titanic-analysis.csv.
Outputs: regression, fit, specification, and main-design CSV files in data/interim/.
Run: uv run python src/030-logistic_regression.py
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parent.parent


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
ANALYSIS_PATH = DATA_ROOT / "processed" / "titanic-analysis.csv"
INTERIM_DIR = DATA_ROOT / "interim"
RESULTS_PATH = INTERIM_DIR / "logistic-regression-results.csv"
FIT_PATH = INTERIM_DIR / "logistic-model-fit.csv"
SPECIFICATION_PATH = INTERIM_DIR / "model-specification.csv"
DESIGN_PATH = INTERIM_DIR / "main-model-design.csv"

TERM_LABELS = {
    "const": "Intercept",
    "Female": "Female (vs male)",
    "Pclass_1": "First class (vs third)",
    "Pclass_2": "Second class (vs third)",
    "Age_per_10y": "Age (per 10 years)",
    "FamilySize": "Family size (per passenger)",
    "LogFare": "Log fare (log1p units)",
    "Embarked_C": "Embarked C (vs S)",
    "Embarked_Q": "Embarked Q (vs S)",
    "AgeMissing": "Age missing indicator",
}


def make_design(
    frame: pd.DataFrame,
    age_fill: float,
    fare_fill: float,
    embarked_fill: str,
    include_age_missing: bool,
) -> pd.DataFrame:
    age = frame["Age"].fillna(age_fill)
    fare = frame["Fare"].fillna(fare_fill)
    embarked = frame["Embarked"].fillna(embarked_fill)
    design = pd.DataFrame(index=frame.index)
    design["Female"] = frame["Sex"].eq("female").astype(float)
    design["Pclass_1"] = frame["Pclass"].eq(1).astype(float)
    design["Pclass_2"] = frame["Pclass"].eq(2).astype(float)
    design["Age_per_10y"] = age.astype(float) / 10.0
    design["FamilySize"] = frame["FamilySize"].astype(float)
    design["LogFare"] = np.log1p(fare.astype(float))
    design["Embarked_C"] = embarked.eq("C").astype(float)
    design["Embarked_Q"] = embarked.eq("Q").astype(float)
    if include_age_missing:
        design["AgeMissing"] = frame["Age"].isna().astype(float)
    return sm.add_constant(design, has_constant="add")


def fit_model(y: pd.Series, design: pd.DataFrame) -> sm.discrete.discrete_model.BinaryResultsWrapper:
    result = sm.Logit(y.astype(float), design.astype(float), check_rank=True).fit(
        method="lbfgs",
        maxiter=1000,
        disp=False,
    )
    if not bool(result.mle_retvals.get("converged", False)):
        raise RuntimeError("Logistic regression did not converge")
    return result


def coefficient_rows(
    result: sm.discrete.discrete_model.BinaryResultsWrapper,
    model_name: str,
) -> list[dict[str, object]]:
    intervals = result.conf_int(alpha=0.05)
    rows: list[dict[str, object]] = []
    for term in result.params.index:
        estimate = float(result.params[term])
        lower = float(intervals.loc[term, 0])
        upper = float(intervals.loc[term, 1])
        rows.append(
            {
                "model": model_name,
                "term": term,
                "term_label": TERM_LABELS[term],
                "estimate_log_odds": estimate,
                "std_error": float(result.bse[term]),
                "z_value": float(result.tvalues[term]),
                "p_value": float(result.pvalues[term]),
                "odds_ratio": float(np.exp(estimate)),
                "ci_lower_95": float(np.exp(lower)),
                "ci_upper_95": float(np.exp(upper)),
            }
        )
    return rows


def fit_row(
    result: sm.discrete.discrete_model.BinaryResultsWrapper,
    model_name: str,
    y: pd.Series,
) -> dict[str, object]:
    return {
        "model": model_name,
        "n": int(result.nobs),
        "survived_n": int(y.sum()),
        "df_model": int(result.df_model),
        "log_likelihood": float(result.llf),
        "aic": float(result.aic),
        "bic": float(result.bic),
        "mcfadden_pseudo_r2": float(result.prsquared),
        "likelihood_ratio_p_value": float(result.llr_pvalue),
        "converged": bool(result.mle_retvals.get("converged", False)),
    }


def main() -> int:
    if not ANALYSIS_PATH.is_file():
        raise FileNotFoundError(f"Missing analysis data: {ANALYSIS_PATH}")
    frame = pd.read_csv(ANALYSIS_PATH)
    required = {"PassengerId", "Survived", "Pclass", "Sex", "Age", "FamilySize", "Fare", "Embarked"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Analysis data is missing required columns: {missing}")

    age_median = float(frame["Age"].median())
    fare_median = float(frame["Fare"].median())
    embarked_mode = str(frame["Embarked"].mode(dropna=True).iloc[0])

    main_design = make_design(frame, age_median, fare_median, embarked_mode, True)
    main_result = fit_model(frame["Survived"], main_design)

    complete = frame.loc[frame["Age"].notna()].copy()
    complete_design = make_design(complete, age_median, fare_median, embarked_mode, False)
    complete_result = fit_model(complete["Survived"], complete_design)

    coefficient_data = coefficient_rows(main_result, "Main model")
    coefficient_data.extend(coefficient_rows(complete_result, "Complete-age sensitivity"))
    fit_data = [
        fit_row(main_result, "Main model", frame["Survived"]),
        fit_row(complete_result, "Complete-age sensitivity", complete["Survived"]),
    ]
    specification_data = [
        {"item": "age_imputation", "value": "Median plus missing indicator"},
        {"item": "age_median", "value": f"{age_median:.8g}"},
        {"item": "fare_imputation", "value": "Median"},
        {"item": "fare_median", "value": f"{fare_median:.8g}"},
        {"item": "embarked_imputation", "value": "Mode"},
        {"item": "embarked_mode", "value": embarked_mode},
        {"item": "reference_sex", "value": "male"},
        {"item": "reference_pclass", "value": "3"},
        {"item": "reference_embarked", "value": "S"},
        {"item": "family_structure", "value": "FamilySize continuous; TravelAlone descriptive only"},
    ]

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(coefficient_data).to_csv(
        RESULTS_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    pd.DataFrame(fit_data).to_csv(FIT_PATH, index=False, lineterminator="\n", float_format="%.10g")
    pd.DataFrame(specification_data).to_csv(SPECIFICATION_PATH, index=False, lineterminator="\n")

    saved_design = pd.concat(
        [
            frame[["PassengerId", "Survived"]].reset_index(drop=True),
            main_design.reset_index(drop=True),
        ],
        axis=1,
    )
    saved_design.to_csv(DESIGN_PATH, index=False, lineterminator="\n", float_format="%.10g")

    print(f"main model n={int(main_result.nobs)}, complete-age n={int(complete_result.nobs)}")
    print(f"regression results: {RESULTS_PATH}")
    print(f"model fit: {FIT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
