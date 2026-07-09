from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List

import pandas as pd

from utils import ensure_dir, load_params, project_root, read_csv_semicolon


@dataclass
class QualityCheck:
    dimension: str
    regla: str
    resultado: str
    errores: int
    total: int
    tasa_error: float
    umbral: float
    observacion: str


def make_check(dimension: str, regla: str, errors: int, total: int, threshold: float, observation: str) -> QualityCheck:
    rate = 0 if total == 0 else errors / total
    result = "OK" if rate <= threshold else "REVISAR"
    return QualityCheck(dimension, regla, result, int(errors), int(total), round(float(rate), 6), float(threshold), observation)


def validate(df_creditos: pd.DataFrame, df_tarjetas: pd.DataFrame) -> List[QualityCheck]:
    checks: list[QualityCheck] = []
    n_creditos = len(df_creditos)
    n_tarjetas = len(df_tarjetas)

    required_creditos = {
        "id_cliente", "edad", "importe_solicitado", "duracion_credito", "antiguedad_empleado",
        "situacion_vivienda", "ingresos", "objetivo_credito", "pct_ingreso", "tasa_interes",
        "estado_credito", "falta_pago",
    }
    required_tarjetas = {
        "id_cliente", "antiguedad_cliente", "estado_civil", "estado_cliente", "gastos_ult_12m",
        "genero", "limite_credito_tc", "nivel_educativo", "nivel_tarjeta", "operaciones_ult_12m",
        "personas_a_cargo",
    }

    checks.append(make_check(
        "Completitud estructural", "Columnas esperadas en créditos",
        len(required_creditos - set(df_creditos.columns)), len(required_creditos), 0,
        f"Faltantes: {sorted(required_creditos - set(df_creditos.columns))}",
    ))
    checks.append(make_check(
        "Completitud estructural", "Columnas esperadas en tarjetas",
        len(required_tarjetas - set(df_tarjetas.columns)), len(required_tarjetas), 0,
        f"Faltantes: {sorted(required_tarjetas - set(df_tarjetas.columns))}",
    ))

    checks.append(make_check(
        "Completitud", "Valores nulos en créditos",
        int(df_creditos.isna().sum().sum()), int(df_creditos.size), 0.10,
        "Se aceptan nulos controlados en antiguedad_empleado y tasa_interes para decidir tratamiento posterior.",
    ))
    checks.append(make_check(
        "Completitud", "Valores nulos en tarjetas",
        int(df_tarjetas.isna().sum().sum()), int(df_tarjetas.size), 0,
        "No se esperan nulos en los atributos de tarjetas.",
    ))

    checks.append(make_check(
        "Unicidad", "id_cliente único en créditos",
        int(df_creditos["id_cliente"].duplicated().sum()), n_creditos, 0,
        "Cada fila debe representar un cliente/crédito sin duplicidad del identificador.",
    ))
    checks.append(make_check(
        "Unicidad", "id_cliente único en tarjetas",
        int(df_tarjetas["id_cliente"].duplicated().sum()), n_tarjetas, 0,
        "Cada cliente debe aparecer una sola vez en datos de tarjetas.",
    ))

    symmetric_diff = set(df_creditos["id_cliente"]) ^ set(df_tarjetas["id_cliente"])
    checks.append(make_check(
        "Consistencia", "Integridad referencial entre créditos y tarjetas",
        len(symmetric_diff), max(n_creditos, n_tarjetas), 0,
        "Todos los clientes de créditos deben tener información de tarjetas y viceversa.",
    ))

    checks.append(make_check(
        "Validez", "Edad entre 18 y 90 años",
        int((~df_creditos["edad"].between(18, 90)).sum()), n_creditos, 0.01,
        "Los registros fuera de rango se consideran candidatos a filtrado por posible error o atípico extremo.",
    ))
    checks.append(make_check(
        "Validez", "Antigüedad de empleado entre 0 y 50 años o nula",
        int((~(df_creditos["antiguedad_empleado"].isna() | df_creditos["antiguedad_empleado"].between(0, 50))).sum()), n_creditos, 0.01,
        "La antigüedad de empleado muy elevada se considera inconsistente con el dominio del problema.",
    ))
    checks.append(make_check(
        "Validez", "pct_ingreso entre 0 y 1",
        int((~df_creditos["pct_ingreso"].between(0, 1)).sum()), n_creditos, 0,
        "La proporción del ingreso no debe estar fuera del intervalo [0,1].",
    ))
    ratio = df_creditos["importe_solicitado"] / df_creditos["ingresos"]
    checks.append(make_check(
        "Consistencia", "pct_ingreso coherente con importe_solicitado/ingresos",
        int(((df_creditos["pct_ingreso"] - ratio).abs() > 0.02).sum()), n_creditos, 0.01,
        "Se permite diferencia por redondeo de hasta 0,02.",
    ))
    checks.append(make_check(
        "Validez", "estado_credito binario {0,1}",
        int((~df_creditos["estado_credito"].isin([0, 1])).sum()), n_creditos, 0,
        "Solo se aceptan valores 0 y 1.",
    ))
    checks.append(make_check(
        "Validez", "falta_pago en {Y,N}",
        int((~df_creditos["falta_pago"].isin(["Y", "N"])).sum()), n_creditos, 0,
        "Variable objetivo con codificación esperada.",
    ))
    checks.append(make_check(
        "Validez", "Importes financieros no negativos en tarjetas",
        int(((df_tarjetas[["gastos_ult_12m", "limite_credito_tc"]] < 0).sum().sum())), n_tarjetas * 2, 0,
        "Gastos y límites no deben ser negativos.",
    ))
    checks.append(make_check(
        "Validez", "personas_a_cargo entre 0 y 10",
        int((~df_tarjetas["personas_a_cargo"].between(0, 10)).sum()), n_tarjetas, 0,
        "Rango razonable para dependientes declarados.",
    ))
    return checks


def write_reports(checks: list[QualityCheck], md_path: Path, json_path: Path) -> None:
    ensure_dir(md_path.parent)
    ensure_dir(json_path.parent)
    rows = [asdict(c) for c in checks]
    pd.DataFrame(rows).to_csv(md_path.with_suffix(".csv"), index=False)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    df = pd.DataFrame(rows)
    table = df.to_markdown(index=False)
    ok = int((df["resultado"] == "OK").sum())
    revisar = int((df["resultado"] == "REVISAR").sum())
    content = f"""# Reporte de calidad de datos - AP1

## Resumen ejecutivo

- Reglas evaluadas: {len(df)}
- Reglas en estado OK: {ok}
- Reglas en estado REVISAR: {revisar}

Las reglas marcadas como `REVISAR` no bloquean necesariamente el proyecto, pero deben documentarse y justificar la acción de preparación de datos aplicada.

## Detalle de reglas

{table}

## Decisiones sugeridas para preparación

1. Filtrar edades fuera del rango aceptado para evitar que atípicos extremos afecten el modelo.
2. Eliminar o imputar registros con valores nulos en `antiguedad_empleado` y `tasa_interes`. Para conservar trazabilidad con la libreta original de procesamiento, se utiliza eliminación de nulos en la primera versión del pipeline.
3. Mantener la integridad referencial mediante unión interna por `id_cliente`.
4. Documentar el desbalance de la variable objetivo para considerarlo en futuras fases de modelado.
"""
    md_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida la calidad de los datos y genera reportes.")
    parser.add_argument("--creditos", default=None)
    parser.add_argument("--tarjetas", default=None)
    parser.add_argument("--report", default=None)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    params = load_params()
    root = project_root()
    df_creditos = read_csv_semicolon(root / (args.creditos or params["paths"]["creditos"]))
    df_tarjetas = read_csv_semicolon(root / (args.tarjetas or params["paths"]["tarjetas"]))
    checks = validate(df_creditos, df_tarjetas)
    write_reports(
        checks,
        root / (args.report or params["paths"]["quality_report"]),
        root / (args.json or params["paths"]["quality_json"]),
    )
    print("Validación finalizada.")


if __name__ == "__main__":
    main()
