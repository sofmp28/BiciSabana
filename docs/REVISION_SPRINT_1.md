# Revisión técnica y guía de estudio del Sprint 1

El prototipo conserva sus cuatro clases y utiliza solamente la biblioteca
estándar. Los siete RF del Sprint 1 tienen implementación y evidencia automática.
El cierre oficial sigue pendiente de revisión y aceptación del equipo.

## Archivos revisados y cambios

Se revisaron AGENTS.md, README.md, bicisabana.py, test_bicisabana.py,
.gitignore y los tres archivos originales de docs/. Se consultaron los textos
de Guia_Proyecto_Tercer_Corte.docx y Sprint_0_Aprobado.docx y el cuaderno
BiciSabana_Guia_POO.ipynb para contrastar alcance y práctica académica.
Las referencias se conservaron sin modificaciones; no se ejecutaron ni
completaron los ejercicios del cuaderno ni se revisó el diseño visual de Word.
Los ejemplos de prompts y las tareas de etapas futuras en esos documentos
son referencias: no amplían el encargo actual.

Cambios realizados:

- bicisabana.py: nueva consulta mostrar_informacion_bicicleta para RF-02 y
  RF-13. El Sprint 0 pide ver el estudiante al consultar una bicicleta prestada;
  antes solo se guardaba la asociación y se mostraba al crear el préstamo.
  La consulta omite préstamos cerrados. Se agregaron comentarios explicativos.
- La demostración muestra las tres bicicletas (RF-01) y el estado durante el
  préstamo (RF-03), además del rechazo y devolución ya existentes.
- test_bicisabana.py: nueve pruebas nuevas y una comprobación más precisa de
  fecha/hora; se retiró una importación que no se usaba.
- README.md: instrucciones comprobadas para esta terminal y explicación de
  la nueva consulta. docs/SPRINT_1.md: trazabilidad de pruebas actualizada,
  manteniendo pendiente la revisión del equipo.
- RESULTADOS_PRUEBAS.txt y DEMOSTRACION.txt: reemplazados por salidas reales
  de esta revisión. Este informe es nuevo.

## Las cuatro clases

Una clase describe qué datos y acciones tendrá un objeto. El constructor
__init__ se ejecuta al crear cada objeto y self representa ese objeto concreto.
Por ejemplo, Bicicleta("B01", "Roja", 1, 1) crea una bicicleta con datos propios.

| Clase | Constructor y atributos | Métodos y responsabilidad |
|---|---|---|
| Bicicleta | __init__(codigo, color, fila, puesto); guarda esos cuatro atributos y estado="Disponible" | mostrar_informacion devuelve texto; prestar cambia a Prestada si está disponible; devolver exige Prestada y cambia a Disponible. |
| Estudiante | __init__(codigo); valida el formato y guarda codigo como texto | validar_formato exige seis dígitos ASCII; permite ceros iniciales. Comprueba formato, no identidad. |
| Prestamo | __init__(bicicleta, estudiante); guarda referencias a ambos objetos, fecha_inicio=datetime.now(), fecha_fin=None y activo=True | cerrar registra fin y desactiva; impide cerrar de nuevo. calcular_duracion devuelve None mientras no haya devolución, y después una diferencia de fechas. Ese cálculo ya existía como adelanto de RF-15. |
| SistemaBiciSabana | __init__(); crea listas vacías bicicletas y prestamos | registrar_bicicleta valida unicidad, campos y ubicación; buscar_bicicleta recorre la lista y devuelve objeto o None; mostrar_informacion_bicicleta consulta datos y estudiante actual; registrar_prestamo valida y conecta objetos; registrar_devolucion cierra el préstamo y libera la bicicleta. |

El sistema usa composición: contiene listas de objetos. Cada préstamo guarda
la misma bicicleta del inventario, no una copia. Por eso prestar esa bicicleta
también cambia el estado visible desde el préstamo. Los ciclos for buscan
objetos y los if deciden si una operación es válida. append agrega un objeto
a una lista; return entrega un resultado al código que llamó al método.

Flujo: registrar bicicleta → validar estudiante y disponibilidad → crear
Prestamo → cambiar estado → guardar préstamo → consultar → devolver.
Las validaciones se hacen antes de modificar las listas. ValueError informa
una operación inválida; la demostración usa try/except para mostrar el rechazo
sin interrumpir su ejecución. Al utilizar los métodos desde otro programa,
el código que los llama debe gestionar esos errores.

Para conservar la coherencia, las operaciones completas se realizan mediante
SistemaBiciSabana. Llamar directamente a bicicleta.prestar() solo cambia el
estado: no crea un préstamo ni asocia estudiante. Tampoco se deben modificar
manualmente estado o activo durante el uso normal.

## Requerimientos comprobados

| RF | Comportamiento implementado |
|---|---|
| RF-01 | Registro único con código, color y estado Disponible; demostración de tres bicicletas. |
| RF-02 | Información de código, color, estado, fila y puesto. |
| RF-03 | Préstamo únicamente si la bicicleta está Disponible. |
| RF-04 | Segundo préstamo rechazado sin agregar otro registro. |
| RF-05 | Devolución cierra el préstamo y deja la bicicleta Disponible. |
| RF-13 | Préstamo asociado al estudiante y consulta que muestra al titular actual. |
| RF-14 | Fecha y hora de inicio automáticas con datetime.now(). |

La fecha/hora es local, sin zona horaria incorporada, según el reloj del equipo.
Los códigos de la demostración son simulados. Los datos desaparecen al terminar.

## Pruebas y evidencia

Las 18 pruebas originales pasaron antes de modificar el programa. La versión
revisada pasó 27 pruebas con Python 3.12.14, sin errores ni fallos. Se ejecutó
también bicisabana.py con salida normal. Las pruebas 23 y 24 usan subTest para
probar varias entradas inválidas dentro de un mismo método de prueba.

- RF-02/RF-13: pruebas 19 a 22 verifican datos completos, omisión del estudiante
  anterior después de devolver, titular correcto al volver a prestar e inexistentes.
- RF-01: prueba 23 comprueba que campos vacíos, tipos incorrectos y posiciones
  inválidas no agregan bicicletas.
- RF-03/RF-13: pruebas 24 y 25 comprueban rechazo de códigos inválidos sin
  alterar estado o préstamos y preservación de ceros iniciales.
- RF-05: prueba 26 verifica que una segunda devolución no modifica el cierre.
- RF-01 a RF-05 y RF-13: prueba 27 comprueba la demostración completa.
- RF-14: prueba 07 verifica que fecha_inicio sea datetime y esté entre los
  instantes inmediatamente anterior y posterior al registro.

Los comandos para repetir estas comprobaciones están en README.md. El comando
python de Windows no funcionó en este computador: se usó el intérprete incluido
con Codex, sin instalar paquetes ni cambiar la configuración del sistema.

## Pendiente para el cierre oficial

- [ ] Cada integrante ejecuta la demostración y las pruebas y explica el ciclo.
- [ ] Un compañero revisa código y casos negativos; registrar quién revisó,
  cuándo, observaciones y correcciones o aceptación.
- [ ] El Product Owner y el equipo aceptan los siete criterios del Sprint 1.
- [ ] Adjuntar las evidencias y la revisión en Notion; actualizar solo las
  historias aceptadas por el equipo.
- [ ] Acordar y registrar la versión de entrega y los cambios correspondientes.

No se modificó Notion ni se otorgó aprobación en nombre del equipo. Las pruebas
automáticas ayudan a comprobar comportamientos; no reemplazan la revisión humana.

No se implementaron funcionalidades nuevas de Sprints 2 y 3. El prototipo ya
traía búsqueda interna, validación del código, bloqueo por estudiante, posiciones
y cálculo de duración; se conservaron sin declarar cerrados sus RF futuros.
Menú, listados, totales, mapa, mantenimiento, historial consultable y demás
funciones futuras siguen fuera de esta entrega.
