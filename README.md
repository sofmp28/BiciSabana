# BiciSabana — Código de inicio para Codex (Sprint 1)

Proyecto universitario de **Fundamentos de Programación** para gestionar préstamos de bicicletas mediante programación orientada a objetos en Python. Este paquete reúne el prototipo elaborado durante el Sprint 1 y las referencias del proyecto.

## Cómo ejecutarlo

Requiere Python 3.10 o superior y **ninguna dependencia externa**.

Desde la carpeta de este proyecto:

```bash
python bicisabana.py
```

Verás una demostración con tres bicicletas. Se crea un préstamo, se intenta duplicarlo (debe rechazarse) y se devuelve la bicicleta.

Para ejecutar las pruebas:

```bash
python -m unittest -v test_bicisabana.py
```

## Archivos principales

- `bicisabana.py`: cuatro clases (`Bicicleta`, `Estudiante`, `Prestamo` y `SistemaBiciSabana`) y demostración.
- `test_bicisabana.py`: 27 pruebas automáticas de comportamiento y validaciones.
- `AGENTS.md`: instrucciones para que Codex continúe respetando la guía académica y la planificación.
- `docs/SPRINT_1.md`: alcance, prioridades, criterios de aceptación y reparto de responsabilidades.
- `docs/RESULTADOS_PRUEBAS.txt`: ejecución de las pruebas en este paquete.
- `docs/DEMOSTRACION.txt`: salida real de la demostración.
- `docs/REVISION_SPRINT_1.md`: explicación de clases, cambios, pruebas y cierre pendiente.
- `referencias/`: el enunciado del proyecto, el Sprint 0 aprobado y el cuaderno de Google Colab, proporcionados previamente.

## Alcance actual

### Ejecutar en PowerShell en este computador

El comando `python` de este computador apunta al acceso directo de Microsoft Store.
Para repetir la ejecución comprobada, usa el Python incluido con Codex:

```powershell
cd "C:\Users\Javier Marulanda\Documents\ChatGPT\SOFIA\BiciSabana_Codex_Sprint1"
$pythonBici = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonBici --version
& $pythonBici -X utf8 bicisabana.py
& $pythonBici -X utf8 -m unittest -v test_bicisabana.py
```

Se verificó con Python 3.12.14. La ruta incluida depende de la instalación de
Codex; en otro computador con Python 3.10+ instalado, usa los comandos `python`
del inicio. No necesitas instalar paquetes con `pip`.

La demostración muestra B01, B02 y B03 disponibles; presta B01 a 123456,
consulta su estado y estudiante, rechaza otro préstamo y registra la devolución.
No solicita datos por teclado. Cada ejecución comienza con listas vacías.
La fecha y hora proceden del reloj local del computador.

Para consultar desde código, usa
`sistema.mostrar_informacion_bicicleta("B01")`: devuelve un texto que incluye
el estudiante solo mientras exista un préstamo activo. `print()` lo muestra
en la terminal.

**Ya implementado como prototipo:** registro único de bicicletas con color/posición, consulta básica, préstamo y devolución, rechazo de doble préstamo, asociación con estudiante, fecha/hora de salida y algunas validaciones adicionales. Datos almacenados solo en memoria.

**Todavía no implementado:** menú interactivo completo, consulta de disponibles/totales, mapa gráfico o de 3×10, seguimiento completo de 30 bicicletas, historial consultable, mantenimiento, interfaz web y persistencia. Estas tareas se planearon para los sprints posteriores.

## Iniciar en Codex

**Codex en la aplicación de escritorio:** descomprime el ZIP, abre la carpeta del proyecto desde Codex y solicita revisar `AGENTS.md`, el código y las pruebas, antes de hacer cambios.

**Codex Cloud:** sube la carpeta a un repositorio de GitHub y selecciónalo en tu entorno de Codex Cloud. En esta conversación no se ha creado ni conectado ningún repositorio del proyecto.

### Primera instrucción sugerida para Codex

> Estamos desarrollando BiciSabana para tercer corte de Fundamentos de Programación. Revisa AGENTS.md, las referencias del proyecto, bicisabana.py y test_bicisabana.py. Ejecuta las pruebas y explícame cómo funcionan las cuatro clases (constructor, atributos, métodos, composición, condicionales y ciclos). Mantén el alcance del Sprint 1 y propón mejoras pequeñas, sin implementar automáticamente los sprints 2 y 3. Toda modificación debe ir acompañada de una prueba y una explicación para estudiantes de segundo semestre.

## Seguimiento Scrum

Tablero: https://app.notion.com/p/4093620bdfce81fdbe14e0401d790718

Sprint 1: https://app.notion.com/p/4093620bdfce81be9a66e41107cc3fe8

No marques una tarea como «Hecho» hasta que el equipo revise y acepte el código y sus evidencias.
