from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import ensure_dir, load_params, project_root, read_csv_semicolon


def save_target_distribution(df_creditos: pd.DataFrame, out_dir: Path) -> None:
    counts = df_creditos["falta_pago"].value_counts().sort_index()
    ax = counts.plot(kind="bar")
    ax.set_title("Distribución de la variable objetivo falta_pago")
    ax.set_xlabel("falta_pago")
    ax.set_ylabel("Cantidad de registros")
    plt.tight_layout()
    plt.savefig(out_dir / "01_distribucion_falta_pago.png", dpi=150)
    plt.close()


def save_missing_values(df_creditos: pd.DataFrame, df_tarjetas: pd.DataFrame, out_dir: Path) -> None:
    missing = pd.concat(
        [
            df_creditos.isna().mean().mul(100).rename("creditos"),
            df_tarjetas.isna().mean().mul(100).rename("tarjetas"),
        ],
        axis=1,
    ).fillna(0)
    ax = missing.plot(kind="bar", figsize=(12, 5))
    ax.set_title("Porcentaje de valores nulos por atributo")
    ax.set_xlabel("Atributo")
    ax.set_ylabel("Valores nulos (%)")
    plt.xticks(rotation=70, ha="right")
    plt.tight_layout()
    plt.savefig(out_dir / "02_valores_nulos.png", dpi=150)
    plt.close()


def save_credit_amount_by_default(df_creditos: pd.DataFrame, out_dir: Path) -> None:
    groups = [
        df_creditos.loc[df_creditos["falta_pago"] == value, "importe_solicitado"]
        for value in sorted(df_creditos["falta_pago"].dropna().unique())
    ]
    labels = sorted(df_creditos["falta_pago"].dropna().unique())
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(groups, tick_labels=labels, showfliers=False)
    ax.set_title("Importe solicitado según falta_pago")
    ax.set_xlabel("falta_pago")
    ax.set_ylabel("Importe solicitado")
    plt.tight_layout()
    plt.savefig(out_dir / "03_importe_solicitado_por_mora.png", dpi=150)
    plt.close()


def save_numeric_correlation(df: pd.DataFrame, title: str, out_path: Path) -> None:
    corr = df.select_dtypes(include="number").corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, aspect="auto")
    ax.set_title(title)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.columns)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def write_summary(df_creditos: pd.DataFrame, df_tarjetas: pd.DataFrame, output_path: Path) -> None:
    target_counts = df_creditos["falta_pago"].value_counts().to_dict()
    target_pct = df_creditos["falta_pago"].value_counts(normalize=True).mul(100).round(2).to_dict()
    content = f"""# Resumen inicial de datos - AP1

## Dimensiones

- Créditos: {df_creditos.shape[0]} filas y {df_creditos.shape[1]} columnas.
- Tarjetas: {df_tarjetas.shape[0]} filas y {df_tarjetas.shape[1]} columnas.

## Variable objetivo

- Distribución absoluta de `falta_pago`: {target_counts}
- Distribución porcentual de `falta_pago`: {target_pct}

## Valores nulos destacados

Créditos:
{df_creditos.isna().sum().to_markdown()}

Tarjetas:
{df_tarjetas.isna().sum().to_markdown()}

## Observaciones iniciales

- Las tablas tienen la misma cantidad de registros y comparten el identificador `id_cliente`.
- La variable objetivo presenta desbalance: la clase `N` es mayoritaria.
- En créditos existen valores nulos en `antiguedad_empleado` y `tasa_interes`, que deben tratarse antes de entrenar modelos.
- Se identifican posibles valores atípicos en `edad` y `antiguedad_empleado` que deben analizarse en la fase de calidad.
"""
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera visualizaciones y resumen inicial de los datos.")
    parser.add_argument("--creditos", default=None)
    parser.add_argument("--tarjetas", default=None)
    parser.add_argument("--figures-dir", default=None)
    parser.add_argument("--summary", default=None)
    args = parser.parse_args()

    params = load_params()
    root = project_root()
    creditos_path = root / (args.creditos or params["paths"]["creditos"])
    tarjetas_path = root / (args.tarjetas or params["paths"]["tarjetas"])
    figures_dir = ensure_dir(root / (args.figures_dir or params["paths"]["figures_dir"]))
    summary_path = root / (args.summary or params["paths"]["summary_report"])
    ensure_dir(summary_path.parent)

    df_creditos = read_csv_semicolon(creditos_path)
    df_tarjetas = read_csv_semicolon(tarjetas_path)

    save_target_distribution(df_creditos, figures_dir)
    save_missing_values(df_creditos, df_tarjetas, figures_dir)
    save_credit_amount_by_default(df_creditos, figures_dir)
    save_numeric_correlation(df_creditos, "Matriz de correlación - créditos", figures_dir / "04_correlacion_creditos.png")
    save_numeric_correlation(df_tarjetas, "Matriz de correlación - tarjetas", figures_dir / "05_correlacion_tarjetas.png")
    write_summary(df_creditos, df_tarjetas, summary_path)

    print(f"Visualizaciones exportadas en: {figures_dir}")
    print(f"Resumen exportado en: {summary_path}")


if __name__ == "__main__":
    main()
