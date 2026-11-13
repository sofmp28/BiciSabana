# Sprint 1 — Programación básica

## Objetivo

Construir un prototipo en Python que pueda crear bicicletas, consultar sus datos, prestarlas si están disponibles y registrar su devolución.

## Requerimientos cubiertos por el prototipo

| Historia | Requerimiento | Criterio | Evidencia automatizada |
|---|---|---|---|
| HU-01 | RF-01 | Crear bicicletas con código, color y estado inicial | test_01, test_13, test_14, test_18, test_23, test_27 |
| HU-02 | RF-02 | Consultar información de B01 | test_02, test_19, test_22 |
| HU-03 | RF-03 | Cambiar a Prestada cuando está disponible | test_03 |
| HU-04 | RF-04 | Impedir préstamo duplicado | test_04 |
| HU-05 | RF-05 | Registrar devolución y disponibilidad | test_05, test_12, test_15, test_20, test_26 |
| HU-13 | RF-13 | Asociar y mostrar código estudiantil del préstamo activo | test_06, test_19, test_20, test_21 |
| HU-14 | RF-14 | Registrar fecha/hora automáticamente | test_07 |

**Pruebas complementarias:** formato de código, inexistentes, no duplicar posiciones, un préstamo activo por estudiante, représtamo tras devolución.

## Roles de trabajo (académicos)

- **Integrante 1:** implementar y explicar préstamos/devoluciones, RF-03 a RF-05 y RF-13.
- **Integrante 2:** verificar asociación de estudiante, hora de salida y registrar evidencias DevSecOps.
- **Integrante 3:** estructurar las clases, inicialización, registro y consulta, y coordinar la integración.

Los tres deben comprender el programa y revisarlo cruzadamente.

## Revisión pendiente

Verificación técnica realizada por Codex: 18 pruebas originales aprobadas y,
después de los cambios, 27 aprobadas con Python 3.12.14; demostración ejecutada.
Las salidas están en `RESULTADOS_PRUEBAS.txt` y `DEMOSTRACION.txt`.
Esto no acredita revisión ni aprobación del equipo. Los siguientes pasos
siguen pendientes para los integrantes:

1. Ejecutar la demostración y explicar qué cambia antes y después de `registrar_prestamo`.
2. Ejecutar pruebas, guardar salida y revisar casos negativos.
3. Revisar código en equipo y confirmar claridad de clases y métodos.
4. Adjuntar evidencias en Notion y cambiar el estado solo de las historias comprobadas.

## Limitaciones vigentes

Persistencia inexistente; los registros no permanecen entre ejecuciones. La interfaz final y la matriz de 30 puestos corresponden a etapas futuras.
