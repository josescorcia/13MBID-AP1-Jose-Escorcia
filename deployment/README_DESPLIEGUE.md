# Despliegue AP2

## API FastAPI en local

```bash
uvicorn app.api:app --reload
```

La documentación interactiva queda en:

```text
http://127.0.0.1:8000/docs
```

## Aplicación Streamlit en local

```bash
streamlit run app/streamlit_app.py
```

## Render

El archivo `deployment/render_api.yaml` resume una configuración posible para publicar la API en Render.

## Streamlit Cloud

La aplicación puede publicarse seleccionando el repositorio de GitHub y el archivo principal:

```text
app/streamlit_app.py
```
