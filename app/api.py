from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "modelo_mora.pkl"
METADATA_PATH = ROOT / "models" / "modelo_metadata.json"

app = FastAPI(
    title="API AP2 13MBID - Predicción de mora",
    description="Servicio para utilizar el modelo de predicción de falta de pago del proyecto de créditos.",
    version="2.0.0",
)


class PredictionRequest(BaseModel):
    record: Dict[str, Any]


def load_assets():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError("No se encontró el modelo o su metadata. Ejecute primero `python src/entrenar_modelos.py`.")
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return model, metadata


@app.get("/")
def root():
    return {"message": "API AP2 13MBID activa", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "model_available": MODEL_PATH.exists(), "metadata_available": METADATA_PATH.exists()}


@app.get("/model-info")
def model_info():
    try:
        _, metadata = load_assets()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {
        "best_model": metadata.get("best_model"),
        "target": metadata.get("target"),
        "feature_columns": metadata.get("feature_columns"),
        "example_record": metadata.get("example_record"),
    }


@app.post("/predict")
def predict(payload: PredictionRequest):
    try:
        model, metadata = load_assets()
        feature_columns = metadata["feature_columns"]
        missing = [c for c in feature_columns if c not in payload.record]
        if missing:
            raise HTTPException(status_code=400, detail={"missing_columns": missing})
        X = pd.DataFrame([payload.record])[feature_columns]
        pred = int(model.predict(X)[0])
        label = metadata.get("prediction_mapping", {}).get(str(pred), str(pred))
        return {"prediction": pred, "prediction_label": label, "interpretable_result": "Mora" if pred == 1 else "No mora"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
