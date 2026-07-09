# Reporte de preparación de datos - AP1

## Entradas

- Créditos originales: 10127 filas y 12 columnas.
- Tarjetas originales: 10127 filas y 11 columnas.

## Salida

- Dataset integrado preparado: 8899 filas y 23 columnas.
- Registros no conservados respecto a créditos originales: 1228.

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
