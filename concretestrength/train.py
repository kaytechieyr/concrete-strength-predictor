"""Train, compare, evaluate, and save concrete-strength regression models."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "concrete_compressive_strength.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"
RESULTS_DIR = PROJECT_ROOT / "results"

FEATURE_COLUMNS = [
    "Cement",
    "Blast Furnace Slag",
    "Fly Ash",
    "Water",
    "Superplasticizer",
    "Coarse Aggregate",
    "Fine Aggregate",
    "Age",
]
TARGET_COLUMN = "Concrete compressive strength"
RANDOM_STATE = 42


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and validate the official UCI concrete dataset."""
    data = pd.read_csv(data_path)
    expected = [*FEATURE_COLUMNS, TARGET_COLUMN]
    missing_columns = sorted(set(expected) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    data = data[expected].copy()
    if data.isna().any().any():
        raise ValueError("Dataset contains missing values.")
    if data.duplicated().any():
        data = data.drop_duplicates(ignore_index=True)
    if (data[FEATURE_COLUMNS] < 0).any().any():
        raise ValueError("Concrete inputs cannot be negative.")
    if (data[TARGET_COLUMN] <= 0).any():
        raise ValueError("Compressive strength must be positive.")
    return data


def split_data(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create reproducible 70/15/15 train, validation, and test splits."""
    train_validation, test = train_test_split(
        data,
        test_size=0.15,
        random_state=RANDOM_STATE,
    )
    validation_fraction = 0.15 / 0.85
    train, validation = train_test_split(
        train_validation,
        test_size=validation_fraction,
        random_state=RANDOM_STATE,
    )
    return (
        train.reset_index(drop=True),
        validation.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def build_candidates() -> dict[str, object]:
    """Return the two regression methods compared in the study."""
    return {
        "Multiple Linear Regression": LinearRegression(),
        "Random Forest Regression": RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def regression_metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    """Calculate the three primary regression metrics."""
    return {
        "MAE (MPa)": float(mean_absolute_error(actual, predicted)),
        "RMSE (MPa)": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(actual, predicted)),
    }


def save_joblib(model: object, model_path: Path) -> None:
    """Save the selected model atomically."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=model_path.parent, suffix=".joblib", delete=False) as file:
        temporary_path = Path(file.name)
    try:
        joblib.dump(model, temporary_path, compress=3)
        temporary_path.replace(model_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def save_metadata(metadata: dict[str, object], metadata_path: Path) -> None:
    """Save model details used by the Streamlit application."""
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_comparison_plot(comparison: pd.DataFrame) -> None:
    """Save validation metric comparison for the report."""
    validation = comparison.loc[comparison["Split"] == "Validation"].copy()
    validation = validation.set_index("Model")

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    validation[["MAE (MPa)", "RMSE (MPa)"]].plot(
        kind="bar",
        ax=axes[0],
        color=["#2563eb", "#f59e0b"],
        rot=0,
    )
    axes[0].set_title("Error pada Validation")
    axes[0].set_ylabel("MPa")
    axes[0].grid(axis="y", alpha=0.25)

    validation[["R2"]].plot(
        kind="bar",
        ax=axes[1],
        color=["#16a34a"],
        rot=0,
        legend=False,
    )
    axes[1].set_title("R² pada Validation")
    axes[1].set_ylim(0, 1)
    axes[1].grid(axis="y", alpha=0.25)

    figure.tight_layout()
    figure.savefig(RESULTS_DIR / "model_comparison.png", dpi=180)
    plt.close(figure)


def save_prediction_plot(actual: pd.Series, predicted: np.ndarray) -> None:
    """Save actual-versus-predicted plot for the selected model."""
    lower = float(min(actual.min(), predicted.min()))
    upper = float(max(actual.max(), predicted.max()))

    figure, axis = plt.subplots(figsize=(6, 5.5))
    axis.scatter(actual, predicted, alpha=0.55, s=28, color="#2563eb")
    axis.plot([lower, upper], [lower, upper], "--", color="#dc2626")
    axis.set_title("Nilai Aktual vs Prediksi pada Test")
    axis.set_xlabel("Aktual (MPa)")
    axis.set_ylabel("Prediksi (MPa)")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(RESULTS_DIR / "actual_vs_predicted.png", dpi=180)
    plt.close(figure)


def main() -> None:
    data = load_data()
    train, validation, test = split_data(data)
    candidates = build_candidates()

    rows: list[dict[str, object]] = []
    validation_scores: dict[str, dict[str, float]] = {}

    for name, model in candidates.items():
        model.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])
        predicted = model.predict(validation[FEATURE_COLUMNS])
        scores = regression_metrics(validation[TARGET_COLUMN], predicted)
        validation_scores[name] = scores
        rows.append({"Model": name, "Split": "Validation", **scores})

    selected_name = min(
        validation_scores,
        key=lambda name: validation_scores[name]["RMSE (MPa)"],
    )

    train_validation = pd.concat([train, validation], ignore_index=True)
    fitted_models: dict[str, object] = {}
    test_predictions: dict[str, np.ndarray] = {}
    for name, candidate in candidates.items():
        fitted = clone(candidate)
        fitted.fit(train_validation[FEATURE_COLUMNS], train_validation[TARGET_COLUMN])
        predicted = fitted.predict(test[FEATURE_COLUMNS])
        fitted_models[name] = fitted
        test_predictions[name] = predicted
        rows.append({
            "Model": name,
            "Split": "Test",
            **regression_metrics(test[TARGET_COLUMN], predicted),
        })

    selected_model = fitted_models[selected_name]
    selected_prediction = test_predictions[selected_name]
    selected_test_metrics = regression_metrics(test[TARGET_COLUMN], selected_prediction)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    comparison = pd.DataFrame(rows)
    comparison.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    pd.DataFrame({
        "Actual (MPa)": test[TARGET_COLUMN],
        "Predicted (MPa)": selected_prediction,
        "Absolute Error (MPa)": np.abs(test[TARGET_COLUMN] - selected_prediction),
    }).to_csv(RESULTS_DIR / "actual_vs_predicted.csv", index=False)

    if hasattr(selected_model, "feature_importances_"):
        importance_values = selected_model.feature_importances_
    else:
        importance_values = np.abs(selected_model.coef_)
    feature_importance = pd.DataFrame({
        "Feature": FEATURE_COLUMNS,
        "Importance": importance_values,
    }).sort_values("Importance", ascending=False)
    feature_importance.to_csv(RESULTS_DIR / "feature_importance.csv", index=False)

    save_comparison_plot(comparison)
    save_prediction_plot(test[TARGET_COLUMN], selected_prediction)

    feature_ranges = {
        column: {
            "min": float(data[column].min()),
            "max": float(data[column].max()),
            "median": float(data[column].median()),
        }
        for column in FEATURE_COLUMNS
    }
    metadata: dict[str, object] = {
        "project_title": (
            "Sistem Prediksi Kuat Tekan Beton Berdasarkan Komposisi Campuran "
            "dan Umur Menggunakan Multiple Linear Regression dan Random Forest Regression"
        ),
        "dataset": {
            "name": "Concrete Compressive Strength",
            "source": "UCI Machine Learning Repository",
            "doi": "10.24432/C5PK67",
            "records_after_cleaning": len(data),
            "missing_values": 0,
        },
        "selected_model": selected_name,
        "selection_metric": "RMSE validation terendah",
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "split": {
            "train": len(train),
            "validation": len(validation),
            "test": len(test),
            "random_state": RANDOM_STATE,
        },
        "validation_metrics": validation_scores,
        "test_metrics_selected_model": selected_test_metrics,
        "feature_ranges": feature_ranges,
        "feature_importance": feature_importance.to_dict(orient="records"),
    }

    save_joblib(selected_model, MODEL_PATH)
    save_metadata(metadata, METADATA_PATH)

    print(f"Dataset: {len(data)} records, {len(FEATURE_COLUMNS)} features.")
    print(f"Split: train={len(train)}, validation={len(validation)}, test={len(test)}.")
    print("\nValidation results:")
    for name, scores in validation_scores.items():
        print(
            f"- {name}: MAE={scores['MAE (MPa)']:.3f} MPa, "
            f"RMSE={scores['RMSE (MPa)']:.3f} MPa, R2={scores['R2']:.3f}"
        )
    print(f"\nSelected model: {selected_name}")
    print(
        f"Test: MAE={selected_test_metrics['MAE (MPa)']:.3f} MPa, "
        f"RMSE={selected_test_metrics['RMSE (MPa)']:.3f} MPa, "
        f"R2={selected_test_metrics['R2']:.3f}"
    )
    print(f"Saved model to {MODEL_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
