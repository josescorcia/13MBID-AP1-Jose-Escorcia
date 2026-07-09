from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "models" / "modelo_metadata.json"

st.set_page_config(page_title="AP2 13MBID - Predicción de mora", layout="wide")
st.title("AP2 13MBID - Herramienta de predicción de mora")
st.write("Aplicación web de consulta para usuarios finales. Permite enviar un registro a la API del modelo entrenado.")

api_url = st.sidebar.text_input("URL de la API", value="http://localhost:8000")

if not METADATA_PATH.exists():
    st.error("No se encontró models/modelo_metadata.json. Ejecute primero el entrenamiento del modelo.")
    st.stop()

metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
example = metadata["example_record"]
feature_columns = metadata["feature_columns"]

st.subheader("Datos del cliente/crédito")
record: dict[str, Any] = {}
cols = st.columns(2)
for idx, col_name in enumerate(feature_columns):
    value = example.get(col_name)
    with cols[idx % 2]:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            record[col_name] = st.number_input(col_name, value=float(value))
        else:
            record[col_name] = st.text_input(col_name, value=str(value))

if st.button("Generar predicción"):
    try:
        response = requests.post(f"{api_url.rstrip('/')}/predict", json={"record": record}, timeout=15)
        if response.ok:
            result = response.json()
            st.success(f"Resultado: {result['interpretable_result']}")
            st.json(result)
        else:
            st.error(f"Error de API: {response.status_code}")
            st.write(response.text)
    except Exception as exc:
        st.error(f"No fue posible conectar con la API: {exc}")

st.subheader("Ejemplo de registro")
st.dataframe(pd.DataFrame([example]))
