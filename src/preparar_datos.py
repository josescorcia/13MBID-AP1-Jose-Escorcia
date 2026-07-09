from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import ensure_dir, load_params, project_root, read_csv_semicolon


def preparar_dataset(df_creditos: pd.DataFrame, df_tarjetas: pd.DataFrame) -> pd.DataFrame:
    creditos = df_creditos.copy()
    tarjetas = df_tarjetas.copy()

    tarjetas = tarjetas.drop(columns=["nivel_tarjeta"], errors="ignore")

    creditos = creditos[creditos["edad"] < 90].copy()
    creditos = creditos.dropna().copy()

    integrado = pd.merge(creditos, tarjetas, on="id_cliente", how="inner")

    cambios_estado_civil = {
        "CASADO": "C",
        "SOLTERO": "S",
        "DESCONOCIDO": "N",
        "DIVORCIADO": "D",
    }
    cambios_estado_credito = {0: "P", 1: "C"}

    estado_civil_n = integrado["estado_civil"].map(cambios_estado_civil).rename("estado_civil_N")
    estado_credito_n = integrado["estado_credito"].map(cambios_estado_credito).rename("estado_credito_N")

    antiguedad_empleados_n = pd.cut(
        integrado["antiguedad_empleado"],
        bins=[0, 4, 10, 50],
        labels=["menor_5", "5_a_10", "mayor_10"],
        right=False,
    ).cat.add_categories("sin_categoria").fillna("sin_categoria").rename("antiguedad_empleado_N")

    edad_n = pd.cut(
        integrado["edad"],
        bins=[0, 24, 50],
        labels=["menor_25", "25_a_30"],
        right=False,
    ).rename("edad_N")

    # Atributos derivados útiles para futuras fases de modelado.
    ratio_gasto_limite = (integrado["gastos_ult_12m"] / integrado["limite_credito_tc"]).rename("ratio_gasto_limite_tc")
    falta_pago_bin = integrado["falta_pago"].map({"N": 0, "Y": 1}).rename("falta_pago_bin")

    integrado = integrado.drop(columns=["estado_civil", "estado_credito", "antiguedad_empleado", "edad"])
    integrado = pd.concat(
        [integrado, estado_civil_n, estado_credito_n, antiguedad_empleados_n, edad_n, ratio_gasto_limite, falta_pago_bin],
        axis=1,
    )

    # Validación final: no nulos y sin duplicados.
    integrado = integrado.dropna().drop_duplicates().reset_index(drop=True)
    return integrado


def write_preparation_report(original_creditos: pd.DataFrame, original_tarjetas: pd.DataFrame, prepared: pd.DataFrame, report_path: Path) -> None:
    ensure_dir(report_path.parent)
    removed_creditos = original_creditos.shape[0] - prepared.shape[0]
    content = f"""# Reporte de preparación de datos - AP1

## Entradas

- Créditos originales: {original_creditos.shape[0]} filas y {original_creditos.shape[1]} columnas.
- Tarjetas originales: {original_tarjetas.shape[0]} filas y {original_tarjetas.shape[1]} columnas.

## Salida

- Dataset integrado preparado: {prepared.shape[0]} filas y {prepared.shape[1]} columnas.
- Registros no conservados respecto a créditos originales: {removed_creditos}.

## Transformaciones aplicadas

1. Selección de atributos: eliminación de `nivel_tarjeta`.
2. Filtro de filas: conservación de registros con `edad < 90`.
3. Tratamiento de nulos: eliminación de registros con valores ausentes en la tabla de créditos.
4. Integración: unión interna por `id_cliente` entre créditos y tarjetas.
5. Recodificación de variables: `estado_civil_N`, `estado_credito_N`, `antiguedad_empleado_N`, `edad_N`.
6. Construcción de atributos: `ratio_gasto_limite_tc` y `falta_pago_bin`.
7. Validación final: eliminación de duplicados y verificación de ausencia de nulos.

## Justificación

La salida preparada genera un dataset único y reproducible para las siguientes fases del proyecto. Las transformaciones se implementan en script independiente para ser ejecutadas manualmente o desde un pipeline DVC.
"""
    report_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara e integra los datasets de créditos y tarjetas.")
    parser.add_argument("--creditos", default=None)
    parser.add_argument("--tarjetas", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--report", default="reports/preparacion_datos.md")
    args = parser.parse_args()

    params = load_params()
    root = project_root()
    df_creditos = read_csv_semicolon(root / (args.creditos or params["paths"]["creditos"]))
    df_tarjetas = read_csv_semicolon(root / (args.tarjetas or params["paths"]["tarjetas"]))
    preparado = preparar_dataset(df_creditos, df_tarjetas)

    out_path = root / (args.output or params["paths"]["processed"])
    ensure_dir(out_path.parent)
    preparado.to_csv(out_path, index=False)
    write_preparation_report(df_creditos, df_tarjetas, preparado, root / args.report)
    print(f"Dataset preparado exportado en: {out_path}")
    print(f"Filas: {preparado.shape[0]} | Columnas: {preparado.shape[1]}")


if __name__ == "__main__":
    main()
