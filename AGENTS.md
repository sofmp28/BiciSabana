# Instrucciones del proyecto para Codex

## Contexto

Proyecto universitario BiciSabana, tercer corte de Fundamentos de Programación. Equipo de tres personas que se identifican solamente como Integrante 1 (Product Owner), Integrante 2 (Scrum Master) e Integrante 3 (desarrollo e integración). El Sprint 0 ya fue documentado y aprobado.

## Prioridades de programación

1. **No sustituir la programación orientada a objetos por una implementación web o un framework**: explicar claramente clases, atributos, `__init__`, métodos, objetos, listas, ciclos y validaciones.
2. Usar Python estándar, nombres expresivos y mensajes al usuario en español. Sin bibliotecas adicionales salvo que el equipo lo apruebe.
3. Foco Sprint 1: RF-01 a RF-05, RF-13 y RF-14. El código actual también adelanta controles relacionados con RF-12 y la ubicación, pero eso no significa que los sprints siguientes estén finalizados.
4. La bicicleta solo puede prestarse si está «Disponible». No registrar préstamos duplicados ni permitir préstamo simultáneo a un mismo estudiante. Las entradas inválidas no deben alterar el inventario.
5. La validación de código estudiantil de **seis dígitos numéricos** es la decisión tomada para el prototipo; valida formato, no identidad. Los datos solo viven en memoria durante la ejecución.
6. Usar los documentos de `referencias/` para confirmar el alcance. El cuaderno `.ipynb` contiene ejercicios de aprendizaje y debe mantenerse como práctica identificable, no fusionarse sin explicación al prototipo.
7. No inventar resultados de pruebas ni afirmar que el equipo aprobó los cambios realizados por Codex.

## Flujo de trabajo

- Revisar el código existente antes de modificarlo. Mantener simplicidad y compatibilidad con Python 3.10+.
- Ejecutar `python -m unittest -v test_bicisabana.py` antes y después de cambios.
- Cada cambio debe mencionar qué requerimiento cubre, añadir o actualizar una prueba y explicar su razón en lenguaje accesible.
- No implementar mapas, interfaz HTML, menú interactivo final, almacenamiento permanente ni otras funciones de Sprints 2 y 3 sin pedido explícito.
- No cambiar estados de Notion hasta que haya evidencia y revisión del equipo.

## Definition of Done

El código cumple el criterio de aceptación, las pruebas pasan, la revisión manual de un compañero está documentada y la evidencia se enlaza a Notion. Los tests son necesarios, pero no reemplazan la aprobación del equipo.
