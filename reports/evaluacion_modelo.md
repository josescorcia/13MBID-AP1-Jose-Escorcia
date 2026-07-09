# Reporte de evaluación del modelo - AP2

## Resultado general

Estado del control de regresión: **APROBADO**.

## Dataset utilizado

- Filas: 8899
- Columnas originales: 23
- Variables predictoras: 20
- Tasa de clase positiva: 0.1759
- Muestras de entrenamiento originales: 7119
- Muestras de entrenamiento balanceadas: 2504
- Muestras de prueba: 1780

## Modelo seleccionado

- Modelo: **LogisticRegression**
- Accuracy en test: 0.8438
- F1 macro en test: 0.7759
- Recall macro en test: 0.8399
- Precision macro en test: 0.7479

## Matriz de confusión

| | Predicción 0 | Predicción 1 |
|---|---:|---:|
| Real 0 | 1241 | 226 |
| Real 1 | 52 | 261 |

## Interpretación

El control de regresión verifica que el modelo generado mantenga un desempeño mínimo en términos de F1 macro y recall macro. Estas métricas son pertinentes porque el problema de mora presenta desbalance de clases y se requiere que el modelo no se limite a favorecer la clase mayoritaria.
