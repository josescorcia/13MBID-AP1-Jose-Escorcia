# Resumen inicial de datos - AP1

## Dimensiones

- Créditos: 10127 filas y 12 columnas.
- Tarjetas: 10127 filas y 11 columnas.

## Variable objetivo

- Distribución absoluta de `falta_pago`: {'N': 8359, 'Y': 1768}
- Distribución porcentual de `falta_pago`: {'N': 82.54, 'Y': 17.46}

## Valores nulos destacados

Créditos:
|                     |   0 |
|:--------------------|----:|
| id_cliente          |   0 |
| edad                |   0 |
| importe_solicitado  |   0 |
| duracion_credito    |   0 |
| antiguedad_empleado | 337 |
| situacion_vivienda  |   0 |
| ingresos            |   0 |
| objetivo_credito    |   0 |
| pct_ingreso         |   0 |
| tasa_interes        | 912 |
| estado_credito      |   0 |
| falta_pago          |   0 |

Tarjetas:
|                     |   0 |
|:--------------------|----:|
| id_cliente          |   0 |
| antiguedad_cliente  |   0 |
| estado_civil        |   0 |
| estado_cliente      |   0 |
| gastos_ult_12m      |   0 |
| genero              |   0 |
| limite_credito_tc   |   0 |
| nivel_educativo     |   0 |
| nivel_tarjeta       |   0 |
| operaciones_ult_12m |   0 |
| personas_a_cargo    |   0 |

## Observaciones iniciales

- Las tablas tienen la misma cantidad de registros y comparten el identificador `id_cliente`.
- La variable objetivo presenta desbalance: la clase `N` es mayoritaria.
- En créditos existen valores nulos en `antiguedad_empleado` y `tasa_interes`, que deben tratarse antes de entrenar modelos.
- Se identifican posibles valores atípicos en `edad` y `antiguedad_empleado` que deben analizarse en la fase de calidad.
