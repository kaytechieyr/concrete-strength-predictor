"""Streamlit interface for concrete compressive-strength prediction."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"

INPUT_LABELS = {
    "Cement": "Semen (kg/m³)",
    "Blast Furnace Slag": "Blast furnace slag (kg/m³)",
    "Fly Ash": "Fly ash (kg/m³)",
    "Water": "Air (kg/m³)",
    "Superplasticizer": "Superplasticizer (kg/m³)",
    "Coarse Aggregate": "Agregat kasar (kg/m³)",
    "Fine Aggregate": "Agregat halus (kg/m³)",
    "Age": "Umur beton (hari)",
}


@st.cache_resource
def load_artifacts() -> tuple[object, dict[str, object]]:
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError("Model belum tersedia. Jalankan: python train.py")
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return model, metadata


def main() -> None:
    st.set_page_config(
        page_title="Prediksi Kuat Tekan Beton",
        page_icon="🏗️",
        layout="wide",
    )
    st.title("Sistem Prediksi Kuat Tekan Beton")
    st.write(
        "Masukkan komposisi campuran per meter kubik dan umur beton untuk "
        "memperoleh estimasi kuat tekan dalam MPa."
    )

    try:
        model, metadata = load_artifacts()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    ranges = metadata["feature_ranges"]
    values: dict[str, float] = {}

    with st.form("prediction_form"):
        left, right = st.columns(2)
        for index, feature in enumerate(metadata["features"]):
            feature_range = ranges[feature]
            target_column = left if index < 4 else right
            with target_column:
                if feature == "Age":
                    values[feature] = st.number_input(
                        INPUT_LABELS[feature],
                        min_value=int(feature_range["min"]),
                        max_value=int(feature_range["max"]),
                        value=int(feature_range["median"]),
                        step=1,
                    )
                else:
                    values[feature] = st.number_input(
                        INPUT_LABELS[feature],
                        min_value=float(feature_range["min"]),
                        max_value=float(feature_range["max"]),
                        value=float(feature_range["median"]),
                        step=0.1,
                        format="%.1f",
                    )
        submitted = st.form_submit_button("Prediksi kuat tekan", type="primary")

    if submitted:
        input_data = pd.DataFrame([values], columns=metadata["features"])
        prediction = float(model.predict(input_data)[0])
        st.success(f"Estimasi kuat tekan beton: {prediction:.2f} MPa")
        st.caption(
            "Hasil merupakan estimasi berdasarkan pola data historis UCI, bukan "
            "pengganti pengujian kuat tekan beton di laboratorium."
        )

    metrics = metadata["test_metrics_selected_model"]
    st.divider()
    st.subheader("Informasi model")
    st.write(f"Model terpilih: **{metadata['selected_model']}**")
    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("MAE test", f"{metrics['MAE (MPa)']:.2f} MPa")
    metric_2.metric("RMSE test", f"{metrics['RMSE (MPa)']:.2f} MPa")
    metric_3.metric("R² test", f"{metrics['R2']:.3f}")

    with st.expander("Lihat pengaruh relatif fitur"):
        importance = pd.DataFrame(metadata["feature_importance"])
        importance = importance.set_index("Feature")
        st.bar_chart(importance["Importance"])


if __name__ == "__main__":
    main()
