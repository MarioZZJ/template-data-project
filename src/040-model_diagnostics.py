#!/usr/bin/env python3
"""Evaluate model stability, influence, calibration, and cross-validated performance.

Purpose: Check simple model diagnostics without treating prediction as a competition result.
Inputs: analysis data and the main-model design CSV in data/interim/.
Outputs: performance, diagnostics, and influential-observation CSV files in data/interim/.
Run: uv run python src/040-model_diagnostics.py
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor


ROOT = Path(__file__).resolve().parent.parent
RANDOM_SEED = 20260810
N_SPLITS = 5


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
ANALYSIS_PATH = DATA_ROOT / "processed" / "titanic-analysis.csv"
INTERIM_DIR = DATA_ROOT / "interim"
DESIGN_PATH = INTERIM_DIR / "main-model-design.csv"
PERFORMANCE_PATH = INTERIM_DIR / "model-performance.csv"
DIAGNOSTICS_PATH = INTERIM_DIR / "model-diagnostics.csv"
INFLUENCE_PATH = INTERIM_DIR / "influence-observations.csv"


def prediction_frame(frame: pd.DataFrame) -> pd.DataFrame:
    features = frame[["Age", "FamilySize", "Fare", "AgeMissing", "Sex", "Pclass", "Embarked"]].copy()
    features["LogFare"] = np.log1p(features.pop("Fare"))
    features["Pclass"] = features["Pclass"].astype("string")
    return features


def make_pipeline() -> Pipeline:
    numeric = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(drop="first", handle_unknown="ignore")),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", numeric, ["Age", "FamilySize", "LogFare", "AgeMissing"]),
            ("categorical", categorical, ["Sex", "Pclass", "Embarked"]),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            (
                "model",
                LogisticRegression(
                    solver="lbfgs",
                    max_iter=2000,
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )


def cross_validated_predictions(
    features: pd.DataFrame,
    outcome: pd.Series,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    splitter = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_SEED)
    probabilities = np.full(len(outcome), np.nan, dtype=float)
    fold_rows: list[dict[str, float]] = []
    base_pipeline = make_pipeline()

    for fold, (train_index, test_index) in enumerate(splitter.split(features, outcome), start=1):
        model = clone(base_pipeline)
        model.fit(features.iloc[train_index], outcome.iloc[train_index])
        fold_probabilities = model.predict_proba(features.iloc[test_index])[:, 1]
        probabilities[test_index] = fold_probabilities
        fold_outcome = outcome.iloc[test_index]
        fold_rows.append(
            {
                "fold": float(fold),
                "roc_auc": float(roc_auc_score(fold_outcome, fold_probabilities)),
                "brier_score": float(brier_score_loss(fold_outcome, fold_probabilities)),
                "log_loss": float(log_loss(fold_outcome, fold_probabilities, labels=[0, 1])),
            }
        )

    if np.isnan(probabilities).any():
        raise RuntimeError("Cross-validation did not produce one prediction per observation")
    return probabilities, fold_rows


def metric_row(
    metric: str,
    oof_value: float,
    fold_values: list[float],
    preferred_direction: str,
) -> dict[str, object]:
    return {
        "metric": metric,
        "out_of_fold_estimate": oof_value,
        "fold_mean": float(np.mean(fold_values)),
        "fold_sd": float(np.std(fold_values, ddof=1)),
        "folds": N_SPLITS,
        "random_seed": RANDOM_SEED,
        "preferred_direction": preferred_direction,
    }


def main() -> int:
    for path in (ANALYSIS_PATH, DESIGN_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Missing model input: {path}")

    frame = pd.read_csv(ANALYSIS_PATH)
    design_frame = pd.read_csv(DESIGN_PATH)
    outcome = frame["Survived"].astype(int)
    features = prediction_frame(frame)
    oof_probabilities, folds = cross_validated_predictions(features, outcome)

    performance_rows = [
        metric_row(
            "ROC AUC",
            float(roc_auc_score(outcome, oof_probabilities)),
            [row["roc_auc"] for row in folds],
            "higher",
        ),
        metric_row(
            "Brier score",
            float(brier_score_loss(outcome, oof_probabilities)),
            [row["brier_score"] for row in folds],
            "lower",
        ),
        metric_row(
            "Log loss",
            float(log_loss(outcome, oof_probabilities, labels=[0, 1])),
            [row["log_loss"] for row in folds],
            "lower",
        ),
    ]

    clipped = np.clip(oof_probabilities, 1e-6, 1 - 1e-6)
    calibration_logit = np.log(clipped / (1 - clipped))
    calibration_design = sm.add_constant(calibration_logit, has_constant="add")
    calibration = sm.Logit(outcome, calibration_design).fit(disp=False, method="lbfgs", maxiter=1000)

    predictor_columns = [
        column
        for column in design_frame.columns
        if column not in {"PassengerId", "Survived", "const"}
    ]
    vif_matrix = design_frame[["const", *predictor_columns]].astype(float)
    diagnostic_rows: list[dict[str, object]] = []
    for index, term in enumerate(predictor_columns, start=1):
        vif = float(variance_inflation_factor(vif_matrix.to_numpy(), index))
        diagnostic_rows.append(
            {
                "diagnostic": "Variance inflation factor",
                "term": term,
                "value": vif,
                "reference": "Review values >= 5",
                "flag": "REVIEW" if vif >= 5 else "OK",
                "detail": "Auxiliary VIF regression includes an intercept",
            }
        )

    glm_design = design_frame.drop(columns=["PassengerId", "Survived"]).astype(float)
    glm_result = sm.GLM(
        design_frame["Survived"].astype(float),
        glm_design,
        family=sm.families.Binomial(),
    ).fit()
    influence = glm_result.get_influence(observed=True)
    cooks_distance = np.asarray(influence.cooks_distance[0], dtype=float)
    influence_threshold = 4.0 / len(design_frame)
    influential_count = int((cooks_distance > influence_threshold).sum())
    diagnostic_rows.extend(
        [
            {
                "diagnostic": "Maximum Cook's distance",
                "term": "all observations",
                "value": float(cooks_distance.max()),
                "reference": f"4/n = {influence_threshold:.8g}",
                "flag": "REVIEW" if influential_count else "OK",
                "detail": f"{influential_count} observations exceed 4/n",
            },
            {
                "diagnostic": "OOF calibration intercept",
                "term": "cross-validated probabilities",
                "value": float(calibration.params.iloc[0]),
                "reference": "Ideal 0",
                "flag": "INFO",
                "detail": "Estimated from out-of-fold probabilities",
            },
            {
                "diagnostic": "OOF calibration slope",
                "term": "cross-validated probabilities",
                "value": float(calibration.params.iloc[1]),
                "reference": "Ideal 1",
                "flag": "INFO",
                "detail": "Estimated from out-of-fold probabilities",
            },
            {
                "diagnostic": "Observed survival rate",
                "term": "all observations",
                "value": float(outcome.mean()),
                "reference": "Compare with mean OOF probability",
                "flag": "INFO",
                "detail": f"Mean OOF probability = {oof_probabilities.mean():.8g}",
            },
        ]
    )

    influence_frame = pd.DataFrame(
        {
            "PassengerId": design_frame["PassengerId"].astype(int),
            "cooks_distance": cooks_distance,
            "threshold_4_over_n": influence_threshold,
            "exceeds_threshold": cooks_distance > influence_threshold,
        }
    ).sort_values("cooks_distance", ascending=False)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(performance_rows).to_csv(
        PERFORMANCE_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    pd.DataFrame(diagnostic_rows).to_csv(
        DIAGNOSTICS_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    influence_frame.head(20).to_csv(
        INFLUENCE_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )

    print(f"cross-validation: folds={N_SPLITS}, random_seed={RANDOM_SEED}")
    print(f"performance summary: {PERFORMANCE_PATH}")
    print(f"model diagnostics: {DIAGNOSTICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
