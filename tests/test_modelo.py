from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_metricas_modelo_existen_y_superan_umbral():
    metrics_path = ROOT / "reports" / "metricas_modelo.json"
    assert metrics_path.exists(), "Debe existir el archivo reports/metricas_modelo.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics = payload["metrics"]
    assert metrics["test_f1_macro"] >= 0.55
    assert metrics["test_recall_macro"] >= 0.55


def test_modelo_exportado_puede_generar_predicciones():
    model_path = ROOT / "models" / "modelo_mora.pkl"
    metadata_path = ROOT / "models" / "modelo_metadata.json"
    assert model_path.exists(), "Debe existir el modelo exportado"
    assert metadata_path.exists(), "Debe existir la metadata del modelo"
    model = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    example = pd.DataFrame([metadata["example_record"]])
    prediction = model.predict(example)
    assert len(prediction) == 1
    assert int(prediction[0]) in [0, 1]
