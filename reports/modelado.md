# Reporte de modelado - AP2

## Objetivo

Entrenar y comparar modelos de clasificación para predecir la posibilidad de mora (`falta_pago`) a partir del dataset integrado de créditos y productos de tarjeta.

## Diseño experimental

- Variable objetivo: `falta_pago` codificada como 0 = no mora y 1 = mora.
- División de datos: 80% entrenamiento y 20% prueba con estratificación.
- Balanceo: submuestreo determinístico de la clase mayoritaria únicamente sobre el conjunto de entrenamiento.
- Preprocesamiento: estandarización de variables numéricas y codificación one-hot de variables categóricas.
- Validación cruzada: 5 folds estratificados sobre el conjunto de entrenamiento balanceado.
- Registro de experimentos: MLflow cuando la librería está disponible en el entorno.

## Comparación de modelos

| modelo                 |   cv_f1_macro_mean |   cv_recall_macro_mean |   test_accuracy |   test_f1_macro |   test_recall_macro |   test_precision_macro |
|:-----------------------|-------------------:|-----------------------:|----------------:|----------------:|--------------------:|-----------------------:|
| LogisticRegression     |             0.8598 |                 0.8598 |          0.8438 |          0.7759 |              0.8399 |                 0.7479 |
| LinearSVC              |             0.8602 |                 0.8602 |          0.8421 |          0.7745 |              0.8401 |                 0.7465 |
| DecisionTreeClassifier |             0.8813 |                 0.8814 |          0.8281 |          0.7694 |              0.8643 |                 0.7428 |
| KNeighborsClassifier   |             0.8297 |                 0.8298 |          0.8096 |          0.7391 |              0.8153 |                 0.7158 |

## Modelo seleccionado

El modelo seleccionado fue **LogisticRegression**, con `test_f1_macro = 0.7759` y `test_recall_macro = 0.8399`.

El modelo se exportó en:

`models/modelo_mora.pkl`

## Justificación

La métrica principal utilizada fue F1 macro, ya que el problema presenta desbalance de clases y se requiere evaluar el rendimiento promedio en ambas clases. El recall macro se incluye como métrica complementaria para verificar la capacidad de detección de clientes con riesgo de mora.
