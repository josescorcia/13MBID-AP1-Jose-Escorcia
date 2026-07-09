# Actividad Práctica II - 13MBID

Proyecto desarrollado para el módulo **Metodologías de Gestión y Diseño de Proyectos Big Data**.

Esta segunda entrega continúa el trabajo de la Actividad Práctica I e incorpora la fase de **modelado, evaluación y despliegue** del proyecto de ciencia de datos para predicción de mora en créditos.

## Objetivo

Automatizar la generación y evaluación del modelo de predicción mediante prácticas de MLOps:

- Comparación de modelos de clasificación.
- Registro de experimentación con MLflow.
- Exportación del modelo entrenado.
- Evaluación automatizada mediante PyTest.
- Integración de modelado y evaluación al pipeline DVC.
- Implementación de API con FastAPI.
- Implementación de aplicación web con Streamlit.

## Estructura del repositorio

```text
app/                  API FastAPI y aplicación Streamlit
 data/                Datos crudos y dataset procesado
 deployment/          Guía y archivos de despliegue
 docs/                Memorias de trabajo AP1/AP2
 models/              Modelo entrenado y metadata
 notebooks/           Libreta original de experimentación AP2
 reports/             Reportes, métricas y figuras generadas
 src/                 Scripts reproducibles del pipeline
 tests/               Pruebas automatizadas PyTest
 dvc.yaml             Pipeline DVC actualizado
 params.yaml          Parámetros del proyecto
 requirements.txt     Dependencias pip
 environment.yml      Entorno conda
```

## Instalación

### Opción A: entorno virtual con pip

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Opción B: Conda

```bash
conda env create -f environment.yml
conda activate 13mbid-ap2
```

## Ejecución manual por etapas

```bash
python src/generar_visualizaciones.py
python src/validar_calidad.py
python src/preparar_datos.py
python src/entrenar_modelos.py
python src/evaluar_modelo.py
python -m pytest -q
```

## Ejecución con DVC

```bash
python -m dvc repro --no-commit
```

> En Windows, si el proyecto se encuentra dentro de una carpeta sincronizada con Google Drive, se recomienda usar `--no-commit` para evitar errores de caché de DVC.

## MLflow

El script de modelado registra los experimentos en la carpeta local `mlruns/` cuando MLflow está instalado.

Para abrir la interfaz local:

```bash
mlflow ui --backend-store-uri mlruns
```

Luego ingresar a:

```text
http://127.0.0.1:5000
```

## API FastAPI

Ejecutar localmente:

```bash
uvicorn app.api:app --reload
```

Documentación interactiva:

```text
http://127.0.0.1:8000/docs
```

## Aplicación Streamlit

```bash
streamlit run app/streamlit_app.py
```

## Resultados principales

Modelo seleccionado en la ejecución base: **LogisticRegression**.

Métricas principales en test:

- Accuracy: 0.8438
- F1 macro: 0.7759
- Recall macro: 0.8399
- Precision macro: 0.7479

Los reportes generados se encuentran en:

```text
reports/modelado.md
reports/evaluacion_modelo.md
reports/modelos_comparacion.csv
reports/metricas_modelo.json
reports/figures/06_matriz_confusion_modelo.png
reports/figures/07_comparacion_modelos_f1.png
```
