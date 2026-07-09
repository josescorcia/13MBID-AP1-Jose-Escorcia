# Actividad Práctica I - 13MBID

Este paquete organiza una propuesta de entrega para la Actividad Práctica I del módulo **Metodologías de Gestión y Diseño de Proyectos Big Data**.

## Estructura

```text
.
├── data/
│   ├── raw/                 # Datos originales
│   └── processed/           # Dataset integrado preparado
├── docs/                    # Memoria de trabajo editable y versión PDF
├── reports/
│   ├── figures/             # Gráficos exportados por el pipeline
│   ├── calidad_datos.md     # Reporte de validación de calidad
│   └── preparacion_datos.md # Reporte de preparación
├── src/                     # Scripts independientes de las libretas
├── tests/                   # Tests automatizados con PyTest
├── dvc.yaml                 # Pipeline DVC
├── params.yaml              # Parámetros del proyecto
├── environment.yml          # Entorno Conda propuesto
└── requirements.txt         # Dependencias mínimas con pip
```

## Configuración del entorno

Opción con Conda:

```bash
conda env create -f environment.yml
conda activate 13mbid-ap1
```

Opción con pip/venv:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
#source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Ejecución manual

```bash
python src/generar_visualizaciones.py
python src/validar_calidad.py
python src/preparar_datos.py
pytest -q
```

## Ejecución con DVC

```bash
dvc init
dvc repro
```

Después de ejecutar, revisar:

- `reports/resumen_datos.md`
- `reports/calidad_datos.md`
- `reports/preparacion_datos.md`
- `data/processed/datos_integrados.csv`
- `reports/figures/*.png`
