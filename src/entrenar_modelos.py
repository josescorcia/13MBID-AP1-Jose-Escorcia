from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from utils import ensure_dir, load_params, project_root

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:  # MLflow is required by the activity, but the script remains executable if it is absent.
    import mlflow
    from mlflow.models import infer_signature
except Exception:  # pragma: no cover - defensive fallback for local environments without mlflow
    mlflow = None
    infer_signature = None


RANDOM_STATE = 42
TARGET = "falta_pago"
SECONDARY_TARGET = "falta_pago_bin"
ID_COL = "id_cliente"


def get_one_hot_encoder() -> OneHotEncoder:
    """Return a OneHotEncoder compatible with recent and older scikit-learn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # sklearn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    if TARGET not in df.columns:
        raise ValueError(f"No se encontró la variable objetivo esperada: {TARGET}")
    y = df[TARGET].map({"N": 0, "Y": 1}) if df[TARGET].dtype == "object" else df[TARGET]
    drop_cols = [TARGET, SECONDARY_TARGET, ID_COL]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return X, y.astype(int)


def build_preprocessor(X: pd.DataFrame) -> tuple[ColumnTransformer, list[str], list[str]]:
    num_cols = X.select_dtypes(include=["int64", "int32", "float64", "float32"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_transformer = Pipeline([("scaler", StandardScaler())])
    categorical_transformer = Pipeline([("encoder", get_one_hot_encoder())])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop",
    )
    return preprocessor, num_cols, cat_cols


def undersample_training_set(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """Simple deterministic undersampling of the majority class on training data only."""
    train = X.copy()
    train["__target__"] = y.values
    counts = train["__target__"].value_counts()
    min_count = int(counts.min())
    parts = []
    for label in sorted(counts.index):
        part = train[train["__target__"] == label].sample(n=min_count, random_state=RANDOM_STATE)
        parts.append(part)
    balanced = pd.concat(parts, axis=0).sample(frac=1.0, random_state=RANDOM_STATE).reset_index(drop=True)
    y_bal = balanced.pop("__target__").astype(int)
    return balanced, y_bal


def model_candidates() -> Dict[str, Any]:
    return {
        "LogisticRegression": LogisticRegression(max_iter=2000, solver="liblinear", random_state=RANDOM_STATE),
        "LinearSVC": LinearSVC(max_iter=5000, random_state=RANDOM_STATE),
        "KNeighborsClassifier": KNeighborsClassifier(n_neighbors=7),
        "DecisionTreeClassifier": DecisionTreeClassifier(random_state=RANDOM_STATE, max_depth=6, min_samples_leaf=20),
    }


def evaluate_model(name: str, pipeline: Pipeline, X_train_bal: pd.DataFrame, y_train_bal: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    scoring = {
        "accuracy": "accuracy",
        "f1_macro": "f1_macro",
        "recall_macro": "recall_macro",
        "precision_macro": "precision_macro",
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_results = cross_validate(pipeline, X_train_bal, y_train_bal, cv=cv, scoring=scoring, n_jobs=None)

    pipeline.fit(X_train_bal, y_train_bal)
    y_pred = pipeline.predict(X_test)

    metrics = {
        "modelo": name,
        "cv_accuracy_mean": float(np.mean(cv_results["test_accuracy"])),
        "cv_accuracy_std": float(np.std(cv_results["test_accuracy"])),
        "cv_f1_macro_mean": float(np.mean(cv_results["test_f1_macro"])),
        "cv_f1_macro_std": float(np.std(cv_results["test_f1_macro"])),
        "cv_recall_macro_mean": float(np.mean(cv_results["test_recall_macro"])),
        "cv_recall_macro_std": float(np.std(cv_results["test_recall_macro"])),
        "cv_precision_macro_mean": float(np.mean(cv_results["test_precision_macro"])),
        "cv_precision_macro_std": float(np.std(cv_results["test_precision_macro"])),
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
    }
    return metrics


def save_confusion_matrix(y_test: pd.Series, y_pred: np.ndarray, path: Path) -> None:
    ensure_dir(path.parent)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(cm)
    ax.set_title("Matriz de confusión - Modelo final")
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    ax.set_xticks([0, 1], labels=["No mora", "Mora"])
    ax.set_yticks([0, 1], labels=["No mora", "Mora"])
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_model_comparison_plot(results: list[dict[str, Any]], path: Path) -> None:
    ensure_dir(path.parent)
    df = pd.DataFrame(results).sort_values("test_f1_macro", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(df["modelo"], df["test_f1_macro"])
    ax.set_title("Comparación de modelos por F1 macro en test")
    ax.set_xlabel("F1 macro")
    ax.set_xlim(0, 1)
    for i, val in enumerate(df["test_f1_macro"]):
        ax.text(val + 0.01, i, f"{val:.3f}", va="center")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def write_markdown_report(results: list[dict[str, Any]], best_metrics: dict[str, Any], report_path: Path, model_path: Path) -> None:
    ensure_dir(report_path.parent)
    df = pd.DataFrame(results).sort_values("test_f1_macro", ascending=False)
    table = df[[
        "modelo",
        "cv_f1_macro_mean",
        "cv_recall_macro_mean",
        "test_accuracy",
        "test_f1_macro",
        "test_recall_macro",
        "test_precision_macro",
    ]].to_markdown(index=False, floatfmt=".4f")
    content = f"""# Reporte de modelado - AP2

## Objetivo

Entrenar y comparar modelos de clasificación para predecir la posibilidad de mora (`falta_pago`) a partir del dataset integrado de créditos y productos de tarjeta.

## Diseño experimental

- Variable objetivo: `{TARGET}` codificada como 0 = no mora y 1 = mora.
- División de datos: 80% entrenamiento y 20% prueba con estratificación.
- Balanceo: submuestreo determinístico de la clase mayoritaria únicamente sobre el conjunto de entrenamiento.
- Preprocesamiento: estandarización de variables numéricas y codificación one-hot de variables categóricas.
- Validación cruzada: 5 folds estratificados sobre el conjunto de entrenamiento balanceado.
- Registro de experimentos: MLflow cuando la librería está disponible en el entorno.

## Comparación de modelos

{table}

## Modelo seleccionado

El modelo seleccionado fue **{best_metrics['modelo']}**, con `test_f1_macro = {best_metrics['test_f1_macro']:.4f}` y `test_recall_macro = {best_metrics['test_recall_macro']:.4f}`.

El modelo se exportó en:

`{model_path.as_posix()}`

## Justificación

La métrica principal utilizada fue F1 macro, ya que el problema presenta desbalance de clases y se requiere evaluar el rendimiento promedio en ambas clases. El recall macro se incluye como métrica complementaria para verificar la capacidad de detección de clientes con riesgo de mora.
"""
    report_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena y compara modelos para AP2 con registro opcional en MLflow.")
    parser.add_argument("--data", default=None)
    parser.add_argument("--model-output", default="models/modelo_mora.pkl")
    parser.add_argument("--metrics-output", default="reports/metricas_modelo.json")
    parser.add_argument("--comparison-output", default="reports/modelos_comparacion.csv")
    parser.add_argument("--metadata-output", default="models/modelo_metadata.json")
    parser.add_argument("--report", default="reports/modelado.md")
    args = parser.parse_args()

    root = project_root()
    params = load_params()
    data_path = root / (args.data or params["paths"]["processed"])
    df = pd.read_csv(data_path)
    X, y = prepare_features(df)
    preprocessor, num_cols, cat_cols = build_preprocessor(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    X_train_bal, y_train_bal = undersample_training_set(X_train, y_train)

    if mlflow is not None:
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("AP2_Modelado_Mora_Creditos")

    results: list[dict[str, Any]] = []
    fitted_pipelines: dict[str, Pipeline] = {}

    for name, model in model_candidates().items():
        pipeline = Pipeline([("prep", preprocessor), ("model", model)])
        metrics = evaluate_model(name, pipeline, X_train_bal, y_train_bal, X_test, y_test)
        results.append(metrics)
        fitted_pipelines[name] = pipeline

        if mlflow is not None:
            with mlflow.start_run(run_name=name):
                mlflow.log_param("modelo", name)
                mlflow.log_param("target", TARGET)
                mlflow.log_param("train_samples_original", int(len(X_train)))
                mlflow.log_param("train_samples_balanced", int(len(X_train_bal)))
                mlflow.log_param("test_samples", int(len(X_test)))
                mlflow.log_param("balancing_method", "undersampling")
                for k, v in metrics.items():
                    if k != "modelo":
                        mlflow.log_metric(k, float(v))

    best_metrics = max(results, key=lambda d: d["test_f1_macro"])
    best_name = best_metrics["modelo"]
    best_pipeline = fitted_pipelines[best_name]
    best_pipeline.fit(X_train_bal, y_train_bal)
    y_pred = best_pipeline.predict(X_test)

    model_path = root / args.model_output
    ensure_dir(model_path.parent)
    joblib.dump(best_pipeline, model_path)

    metrics_path = root / args.metrics_output
    ensure_dir(metrics_path.parent)
    metrics_payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "target": TARGET,
        "best_model": best_name,
        "metrics": best_metrics,
        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "features": int(X.shape[1]),
            "positive_rate": float(y.mean()),
            "train_samples": int(len(X_train)),
            "train_samples_balanced": int(len(X_train_bal)),
            "test_samples": int(len(X_test)),
        },
        "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    comparison_path = root / args.comparison_output
    ensure_dir(comparison_path.parent)
    pd.DataFrame(results).sort_values("test_f1_macro", ascending=False).to_csv(comparison_path, index=False)

    metadata = {
        "model_path": args.model_output,
        "target": TARGET,
        "best_model": best_name,
        "feature_columns": X.columns.tolist(),
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "class_mapping": {"N": 0, "Y": 1},
        "prediction_mapping": {"0": "N", "1": "Y"},
        "example_record": X.iloc[0].to_dict(),
    }
    metadata_path = root / args.metadata_output
    ensure_dir(metadata_path.parent)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    save_confusion_matrix(y_test, y_pred, root / "reports/model_figures/06_matriz_confusion_modelo.png")
    save_model_comparison_plot(results, root / "reports/model_figures/07_comparacion_modelos_f1.png")
    write_markdown_report(results, best_metrics, root / args.report, model_path.relative_to(root))

    if mlflow is not None:
        with mlflow.start_run(run_name=f"modelo_final_{best_name}"):
            mlflow.log_param("modelo_final", best_name)
            for k, v in best_metrics.items():
                if k != "modelo":
                    mlflow.log_metric(k, float(v))
            mlflow.log_artifact(str(metrics_path))
            mlflow.log_artifact(str(comparison_path))
            mlflow.log_artifact(str(root / "reports/model_figures/06_matriz_confusion_modelo.png"))
            if infer_signature is not None:
                try:
                    signature = infer_signature(X_test, best_pipeline.predict(X_test))
                    mlflow.sklearn.log_model(best_pipeline, "modelo_final", signature=signature)
                except Exception:
                    mlflow.sklearn.log_model(best_pipeline, "modelo_final")
            else:
                mlflow.sklearn.log_model(best_pipeline, "modelo_final")

    print(f"Modelo seleccionado: {best_name}")
    print(f"Métricas exportadas en: {metrics_path}")
    print(f"Modelo exportado en: {model_path}")


if __name__ == "__main__":
    main()
