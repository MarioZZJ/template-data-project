#!/usr/bin/env python3
"""Prepare the Titanic analysis dataset and record source-data quality checks.

Purpose: Validate the official train/test files and construct analysis variables.
Inputs: data/raw/titanic/train.csv and data/raw/titanic/test.csv.
Outputs: data/processed/titanic-analysis.csv and data/interim/data-quality-summary.csv.
Run: uv run python src/010-prepare_analysis_data.py
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent


def resolve_root(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else ROOT / path


DATA_ROOT = resolve_root(os.environ.get("DATA_ROOT"), ROOT / "data")
RAW_DIR = DATA_ROOT / "raw" / "titanic"
INTERIM_DIR = DATA_ROOT / "interim"
PROCESSED_DIR = DATA_ROOT / "processed"
TRAIN_PATH = RAW_DIR / "train.csv"
TEST_PATH = RAW_DIR / "test.csv"
ANALYSIS_PATH = PROCESSED_DIR / "titanic-analysis.csv"
QUALITY_PATH = INTERIM_DIR / "data-quality-summary.csv"

TRAIN_COLUMNS = {
    "PassengerId",
    "Survived",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
}
TEST_COLUMNS = TRAIN_COLUMNS - {"Survived"}


def require_columns(frame: pd.DataFrame, expected: set[str], dataset: str) -> None:
    missing = sorted(expected - set(frame.columns))
    if missing:
        raise ValueError(f"{dataset} is missing required columns: {missing}")


def add_check(
    rows: list[dict[str, object]],
    dataset: str,
    metric: str,
    variable: str,
    value: object,
    status: str,
    detail: str,
) -> None:
    rows.append(
        {
            "dataset": dataset,
            "metric": metric,
            "variable": variable,
            "value": value,
            "status": status,
            "detail": detail,
        }
    )


def invalid_count(mask: pd.Series) -> int:
    return int(mask.fillna(False).sum())


def audit_frame(
    frame: pd.DataFrame,
    dataset: str,
    include_outcome: bool,
    rows: list[dict[str, object]],
) -> None:
    add_check(rows, dataset, "row_count", "all", len(frame), "INFO", "Source rows")
    add_check(rows, dataset, "column_count", "all", len(frame.columns), "INFO", "Source columns")

    duplicate_rows = int(frame.duplicated().sum())
    add_check(
        rows,
        dataset,
        "duplicate_rows",
        "all",
        duplicate_rows,
        "PASS" if duplicate_rows == 0 else "FAIL",
        "Exact duplicate source rows",
    )

    key_valid = frame["PassengerId"].notna().all() and frame["PassengerId"].is_unique
    add_check(
        rows,
        dataset,
        "unique_key",
        "PassengerId",
        int(frame["PassengerId"].nunique(dropna=True)),
        "PASS" if key_valid else "FAIL",
        "PassengerId must be nonmissing and unique",
    )

    for column in frame.columns:
        add_check(
            rows,
            dataset,
            "dtype",
            column,
            str(frame[column].dtype),
            "INFO",
            "Pandas source dtype",
        )
        missing = int(frame[column].isna().sum())
        add_check(
            rows,
            dataset,
            "missing_count",
            column,
            missing,
            "INFO",
            f"{missing / len(frame):.6f} of rows" if len(frame) else "Empty dataset",
        )

    range_checks: list[tuple[str, pd.Series, str]] = [
        ("Pclass", ~frame["Pclass"].isin([1, 2, 3]), "Allowed values are 1, 2, 3"),
        ("Sex", ~frame["Sex"].isin(["female", "male"]), "Allowed values are female, male"),
        ("Age", frame["Age"].notna() & ~frame["Age"].between(0, 100), "Nonmissing age must be 0--100"),
        ("SibSp", frame["SibSp"].isna() | (frame["SibSp"] < 0) | (frame["SibSp"] % 1 != 0), "Must be a nonnegative integer"),
        ("Parch", frame["Parch"].isna() | (frame["Parch"] < 0) | (frame["Parch"] % 1 != 0), "Must be a nonnegative integer"),
        ("Fare", frame["Fare"].notna() & (frame["Fare"] < 0), "Nonmissing fare must be nonnegative"),
        ("Embarked", frame["Embarked"].notna() & ~frame["Embarked"].isin(["C", "Q", "S"]), "Allowed nonmissing values are C, Q, S"),
    ]
    if include_outcome:
        range_checks.insert(
            0,
            ("Survived", ~frame["Survived"].isin([0, 1]), "Allowed values are 0, 1"),
        )

    for variable, mask, detail in range_checks:
        count = invalid_count(mask)
        add_check(
            rows,
            dataset,
            "invalid_value_count",
            variable,
            count,
            "PASS" if count == 0 else "FAIL",
            detail,
        )


def main() -> int:
    for path in (TRAIN_PATH, TEST_PATH):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Missing non-empty official Titanic file: {path}")

    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)
    require_columns(train, TRAIN_COLUMNS, "train.csv")
    require_columns(test, TEST_COLUMNS, "test.csv")

    quality_rows: list[dict[str, object]] = []
    audit_frame(train, "train.csv", True, quality_rows)
    audit_frame(test, "test.csv", False, quality_rows)

    compatible = set(test.columns) == set(train.columns) - {"Survived"}
    add_check(
        quality_rows,
        "train/test",
        "schema_compatibility",
        "columns",
        int(compatible),
        "PASS" if compatible else "FAIL",
        "test.csv columns must equal train.csv columns except Survived",
    )
    disjoint_ids = set(train["PassengerId"]).isdisjoint(set(test["PassengerId"]))
    add_check(
        quality_rows,
        "train/test",
        "disjoint_keys",
        "PassengerId",
        int(disjoint_ids),
        "PASS" if disjoint_ids else "FAIL",
        "Train and test PassengerId values must not overlap",
    )

    quality = pd.DataFrame(quality_rows)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    quality.to_csv(QUALITY_PATH, index=False, lineterminator="\n")

    failures = quality.loc[quality["status"] == "FAIL"]
    if not failures.empty:
        failed = failures[["dataset", "metric", "variable", "value"]].to_dict("records")
        raise ValueError(f"Source-data quality checks failed: {failed}")

    analysis = train.copy()
    analysis["Sex"] = analysis["Sex"].str.lower()
    analysis["FamilySize"] = analysis["SibSp"] + analysis["Parch"] + 1
    analysis["TravelAlone"] = analysis["FamilySize"].eq(1).astype("int64")
    analysis["FamilyGroup"] = pd.cut(
        analysis["FamilySize"],
        bins=[0, 1, 4, np.inf],
        labels=["Alone", "Small (2-4)", "Large (5+)"],
    ).astype("string")
    analysis["AgeMissing"] = analysis["Age"].isna().astype("int64")
    analysis["AgeGroup"] = np.select(
        [analysis["Age"].lt(18), analysis["Age"].between(18, 59), analysis["Age"].ge(60)],
        ["Child (<18)", "Adult (18-59)", "Older (60+)"],
        default="Missing",
    )

    columns = [
        "PassengerId",
        "Survived",
        "Pclass",
        "Sex",
        "Age",
        "AgeMissing",
        "AgeGroup",
        "SibSp",
        "Parch",
        "FamilySize",
        "TravelAlone",
        "FamilyGroup",
        "Fare",
        "Embarked",
    ]
    analysis = analysis[columns]
    if analysis["FamilySize"].lt(1).any():
        raise ValueError("Constructed FamilySize contains values below one")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    analysis.to_csv(ANALYSIS_PATH, index=False, lineterminator="\n", float_format="%.8g")

    print(f"train.csv: rows={len(train)}, columns={len(train.columns)}")
    print(f"test.csv: rows={len(test)}, columns={len(test.columns)}")
    print(f"analysis data: {ANALYSIS_PATH}")
    print(f"quality checks: {QUALITY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
