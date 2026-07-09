# Reporte de calidad de datos - AP1

## Resumen ejecutivo

- Reglas evaluadas: 15
- Reglas en estado OK: 15
- Reglas en estado REVISAR: 0

Las reglas marcadas como `REVISAR` no bloquean necesariamente el proyecto, pero deben documentarse y justificar la acción de preparación de datos aplicada.

## Detalle de reglas

| dimension               | regla                                                 | resultado   |   errores |   total |   tasa_error |   umbral | observacion                                                                                            |
|:------------------------|:------------------------------------------------------|:------------|----------:|--------:|-------------:|---------:|:-------------------------------------------------------------------------------------------------------|
| Completitud estructural | Columnas esperadas en créditos                        | OK          |         0 |      12 |     0        |     0    | Faltantes: []                                                                                          |
| Completitud estructural | Columnas esperadas en tarjetas                        | OK          |         0 |      11 |     0        |     0    | Faltantes: []                                                                                          |
| Completitud             | Valores nulos en créditos                             | OK          |      1249 |  121524 |     0.010278 |     0.1  | Se aceptan nulos controlados en antiguedad_empleado y tasa_interes para decidir tratamiento posterior. |
| Completitud             | Valores nulos en tarjetas                             | OK          |         0 |  111397 |     0        |     0    | No se esperan nulos en los atributos de tarjetas.                                                      |
| Unicidad                | id_cliente único en créditos                          | OK          |         0 |   10127 |     0        |     0    | Cada fila debe representar un cliente/crédito sin duplicidad del identificador.                        |
| Unicidad                | id_cliente único en tarjetas                          | OK          |         0 |   10127 |     0        |     0    | Cada cliente debe aparecer una sola vez en datos de tarjetas.                                          |
| Consistencia            | Integridad referencial entre créditos y tarjetas      | OK          |         0 |   10127 |     0        |     0    | Todos los clientes de créditos deben tener información de tarjetas y viceversa.                        |
| Validez                 | Edad entre 18 y 90 años                               | OK          |         4 |   10127 |     0.000395 |     0.01 | Los registros fuera de rango se consideran candidatos a filtrado por posible error o atípico extremo.  |
| Validez                 | Antigüedad de empleado entre 0 y 50 años o nula       | OK          |         2 |   10127 |     0.000197 |     0.01 | La antigüedad de empleado muy elevada se considera inconsistente con el dominio del problema.          |
| Validez                 | pct_ingreso entre 0 y 1                               | OK          |         0 |   10127 |     0        |     0    | La proporción del ingreso no debe estar fuera del intervalo [0,1].                                     |
| Consistencia            | pct_ingreso coherente con importe_solicitado/ingresos | OK          |        37 |   10127 |     0.003654 |     0.01 | Se permite diferencia por redondeo de hasta 0,02.                                                      |
| Validez                 | estado_credito binario {0,1}                          | OK          |         0 |   10127 |     0        |     0    | Solo se aceptan valores 0 y 1.                                                                         |
| Validez                 | falta_pago en {Y,N}                                   | OK          |         0 |   10127 |     0        |     0    | Variable objetivo con codificación esperada.                                                           |
| Validez                 | Importes financieros no negativos en tarjetas         | OK          |         0 |   20254 |     0        |     0    | Gastos y límites no deben ser negativos.                                                               |
| Validez                 | personas_a_cargo entre 0 y 10                         | OK          |         0 |   10127 |     0        |     0    | Rango razonable para dependientes declarados.                                                          |

## Decisiones sugeridas para preparación

1. Filtrar edades fuera del rango aceptado para evitar que atípicos extremos afecten el modelo.
2. Eliminar o imputar registros con valores nulos en `antiguedad_empleado` y `tasa_interes`. Para conservar trazabilidad con la libreta original de procesamiento, se utiliza eliminación de nulos en la primera versión del pipeline.
3. Mantener la integridad referencial mediante unión interna por `id_cliente`.
4. Documentar el desbalance de la variable objetivo para considerarlo en futuras fases de modelado.
