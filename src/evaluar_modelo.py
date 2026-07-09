from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils import ensure_dir, project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un reporte de evaluación del modelo entrenado.")
    parser.add_argument("--metrics", default="reports/metricas_modelo.json")
    parser.add_argument("--output", default="reports/evaluacion_modelo.md")
    args = parser.parse_args()

    root = project_root()
    metrics_path = root / args.metrics
    if not metrics_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de métricas: {metrics_path}")

    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    m = payload["metrics"]
    cm = payload["confusion_matrix"]
    dataset = payload["dataset"]

    status = "APROBADO" if m["test_f1_macro"] >= 0.55 and m["test_recall_macro"] >= 0.55 else "REVISAR"

    content = f"""# Reporte de evaluación del modelo - AP2

## Resultado general

Estado del control de regresión: **{status}**.

## Dataset utilizado

- Filas: {dataset['rows']}
- Columnas originales: {dataset['columns']}
- Variables predictoras: {dataset['features']}
- Tasa de clase positiva: {dataset['positive_rate']:.4f}
- Muestras de entrenamiento originales: {dataset['train_samples']}
- Muestras de entrenamiento balanceadas: {dataset['train_samples_balanced']}
- Muestras de prueba: {dataset['test_samples']}

## Modelo seleccionado

- Modelo: **{payload['best_model']}**
- Accuracy en test: {m['test_accuracy']:.4f}
- F1 macro en test: {m['test_f1_macro']:.4f}
- Recall macro en test: {m['test_recall_macro']:.4f}
- Precision macro en test: {m['test_precision_macro']:.4f}

## Matriz de confusión

| | Predicción 0 | Predicción 1 |
|---|---:|---:|
| Real 0 | {cm[0][0]} | {cm[0][1]} |
| Real 1 | {cm[1][0]} | {cm[1][1]} |

## Interpretación

El control de regresión verifica que el modelo generado mantenga un desempeño mínimo en términos de F1 macro y recall macro. Estas métricas son pertinentes porque el problema de mora presenta desbalance de clases y se requiere que el modelo no se limite a favorecer la clase mayoritaria.
"""
    out_path = root / args.output
    ensure_dir(out_path.parent)
    out_path.write_text(content, encoding="utf-8")
    print(f"Reporte de evaluación exportado en: {out_path}")


if __name__ == "__main__":
    main()
