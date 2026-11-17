# BiciSabana — Implementación Python de los Sprints 2 y 3

## Resultado técnico
Se amplió bicisabana.py sin borrar las cuatro clases originales para cubrir RF-01 a RF-21, incluidos los diez requerimientos adicionales del equipo. Se conservó la demostración del Sprint 1 y las 27 pruebas existentes.

**La implementación técnica y sus pruebas no sustituyen la revisión académica de los tres integrantes.**

## Archivos
- bicisabana.py: clases y menú interactivo.
- test_bicisabana.py: 27 pruebas originales intactas.
- test_sprints_2_3.py: 32 nuevas pruebas sobre consultas, errores, menú y rendimiento.
- simulacion_20_operaciones.py: simulación para DevSecOps / Monitorear.
- docs/RESULTADOS_SPRINTS_2_3.txt: resultados reales de unittest.
- docs/SIMULACION_20_OPERACIONES.txt: resultado real de simulación.
- docs/DEMOSTRACION_SPRINTS_2_3.txt: demostración de terminal.

## Ejecutar
Requiere Python 3.10 o posterior, sin dependencias externas.

    python bicisabana.py
    python -m unittest discover -v
    python simulacion_20_operaciones.py

En Windows se puede utilizar py en vez de python.

En el menú usa la opción **15** para cargar las 30 bicicletas B01–B30 y elige 0 para salir.

## Correspondencia con los requisitos
| Requisitos | Métodos y comportamiento |
| --- | --- |
| RF-01/02 | registrar_bicicleta, mostrar_informacion_bicicleta |
| RF-03/04/05 | registrar_prestamo, registrar_devolucion, bloqueo de duplicados |
| RF-06/07 | listar_disponibles, buscar_bicicleta |
| RF-08 | Estudiante.validar_formato: seis números ASCII |
| RF-09 | contar_estados: disponibles, prestadas, mantenimiento |
| RF-10 | estacion: matriz 3 × 10, mostrar_mapa |
| RF-11 | menu: bucle hasta elegir 0 |
| RF-12/13 | Un préstamo por estudiante, consulta del estudiante asignado |
| RF-14/15 | fecha_inicio, fecha_fin, calcular_duracion |
| RF-16/17 | marcar_mantenimiento, reactivar_bicicleta |
| RF-18/19 | historial, prestamos_activos |
| RF-20 | mover_bicicleta y evitar puestos duplicados |
| RF-21 | registrar_rechazo, consultar_rechazos |

## Evidencia observada
- **59 pruebas Python satisfactorias:** 27 del Sprint 1 y 32 de Sprints 2–3.
- Menú real probado con 30 bicicletas, préstamo válido, rechazo de duplicado, devolución, mapa y salida: proceso terminado sin error.
- Simulación de 20 operaciones: **16 aceptadas (80 %) y 4 rechazadas (20 %)**.
- Estado final de simulación: **30 registradas, 26 disponibles, 4 prestadas, cero en mantenimiento**.
- Consulta y mapa de 30 bicicletas ejecutados en menos de un segundo en el entorno de pruebas.

## Dos conclusiones para Laura
1. En la simulación se aceptaron 16 operaciones válidas, el 80 % del total; las devoluciones conservaron la coherencia entre disponibilidad, estados y préstamos activos.
2. Los cuatro intentos incorrectos (20 %) se rechazaron y registraron con motivo: préstamo duplicado, segundo préstamo del mismo estudiante, bicicleta inexistente y código inválido. El inventario final quedó consistente.

Los porcentajes proceden de una simulación académica, no de datos reales de la universidad.

## Pendientes antes de entrega definitiva
- Python guarda datos solo mientras esté abierto; la web usa almacenamiento local independiente. La conexión web-Python es opcional según la guía.
- El código de seis dígitos no verifica identidad en una base universitaria.
- Un compañero externo debe completar la prueba de usabilidad y revisar la accesibilidad visual (RNF-01 y RNF-06).
- Registrar revisión cruzada, versión, despliegue, comentarios de usuario y el documento separado de las ocho fases de DevSecOps.
- Comparar Python e interfaz con los mismos casos de prueba.
- El equipo debe revisar el resultado antes de marcar los sprints como «Hecho» en Notion.

## Decisiones
Diseño pedagógico: Python estándar, clases, objetos, listas y matriz 2D. Se mantienen 27 pruebas originales para detectar regresiones. Se evitan datos estudiantiles reales.
