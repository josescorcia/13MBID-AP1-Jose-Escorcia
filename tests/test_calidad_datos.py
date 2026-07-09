from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def read_raw(name: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "raw" / name, sep=";")


def test_creditos_columnas_obligatorias():
    df = read_raw("datos_creditos.csv")
    expected = {
        "id_cliente", "edad", "importe_solicitado", "duracion_credito", "antiguedad_empleado",
        "situacion_vivienda", "ingresos", "objetivo_credito", "pct_ingreso", "tasa_interes",
        "estado_credito", "falta_pago",
    }
    assert expected.issubset(set(df.columns))


def test_tarjetas_columnas_obligatorias():
    df = read_raw("datos_tarjetas.csv")
    expected = {
        "id_cliente", "antiguedad_cliente", "estado_civil", "estado_cliente", "gastos_ult_12m",
        "genero", "limite_credito_tc", "nivel_educativo", "nivel_tarjeta", "operaciones_ult_12m",
        "personas_a_cargo",
    }
    assert expected.issubset(set(df.columns))


def test_ids_unicos_e_integridad_referencial():
    creditos = read_raw("datos_creditos.csv")
    tarjetas = read_raw("datos_tarjetas.csv")
    assert creditos["id_cliente"].is_unique
    assert tarjetas["id_cliente"].is_unique
    assert set(creditos["id_cliente"]) == set(tarjetas["id_cliente"])


def test_valores_validos_variable_objetivo_y_estado_credito():
    creditos = read_raw("datos_creditos.csv")
    assert set(creditos["falta_pago"].dropna().unique()).issubset({"Y", "N"})
    assert set(creditos["estado_credito"].dropna().unique()).issubset({0, 1})


def test_rangos_numericos_basicos():
    creditos = read_raw("datos_creditos.csv")
    tarjetas = read_raw("datos_tarjetas.csv")
    assert (creditos["importe_solicitado"] > 0).all()
    assert (creditos["ingresos"] > 0).all()
    assert creditos["pct_ingreso"].between(0, 1).all()
    assert (tarjetas[["gastos_ult_12m", "limite_credito_tc", "operaciones_ult_12m", "personas_a_cargo"]] >= 0).all().all()


def test_dataset_procesado_sin_nulos_si_existe():
    processed = ROOT / "data" / "processed" / "datos_integrados.csv"
    if processed.exists():
        df = pd.read_csv(processed)
        assert df.isna().sum().sum() == 0
        assert df.duplicated().sum() == 0
        assert "falta_pago_bin" in df.columns
