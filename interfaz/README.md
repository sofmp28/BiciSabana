# Interfaz web de BiciSabana

## Abrir la interfaz

Abre [interfaz/index.html](../interfaz/index.html) en Chrome, Edge u otro navegador moderno. No requiere servidor ni instalar paquetes.

La interfaz incluye un panel de control, estación de 3 filas × 10 puestos, 30 bicicletas de ejemplo (B01–B30), inventario, registro de préstamos y devoluciones, búsqueda, conteos, mantenimiento y reactivación, movimiento entre puestos, historial y registro de rechazos. El código del estudiante requiere seis dígitos numéricos, conforme a la decisión del equipo en Sprint 0.

### Importante: alcance técnico
Esta implementación HTML/CSS/JavaScript es **independiente** del programa de Python `bicisabana.py`. La sincronización entre ambos **no está implementada**. Los datos web se guardan en el navegador (almacenamiento local); no es una base de datos universitaria ni un sistema de autenticación. Evita usar información real.

### Pruebas manuales sugeridas
1. Prestar B01 al código 123456: préstamo aceptado; B01 pasa a Prestada.
2. Prestar B01 otra vez: debe rechazarse.
3. Prestar B02 al mismo 123456 sin devolver B01: debe rechazarse.
4. Devolver B01: vuelve a Disponible y se registra la fecha.
5. Marcar B03 En mantenimiento: no permite prestarla; al reactivarla sí.
6. Buscar B01, consultar su historial y comprobar conteos.
7. Cambiar una bicicleta a puesto ocupado: se rechaza el movimiento.
8. Validar entradas vacías, letras y códigos estudiantiles con longitud errónea.
9. Recargar el navegador: se conservan los datos del navegador.
10. Verificar en móvil que el diseño no se desborde horizontalmente.

Estas son instrucciones para repetir la revisión; la revisión final del equipo debe documentarse antes de marcar tareas como Hecho.

### Correspondencia con Python
| Acción web | Clase/método conceptual en Python |
|---|---|
| Registrar bicicleta | `SistemaBiciSabana.registrar_bicicleta()` |
| Buscar/consultar | `SistemaBiciSabana.buscar_bicicleta()`, `Bicicleta.mostrar_informacion()` |
| Prestar | `SistemaBiciSabana.registrar_prestamo()`, `Bicicleta.prestar()` |
| Devolver | `SistemaBiciSabana.registrar_devolucion()`, `Bicicleta.devolver()` |
| Mapa 3 × 10 | `SistemaBiciSabana.mostrar_mapa()` (planificado en Sprint 3) |
| Conteos | `SistemaBiciSabana.contar_estados()` (planificado en Sprint 2) |
| Mantenimiento/reactivación | `Bicicleta.marcar_mantenimiento()`, `Bicicleta.reactivar()` (planificados) |
| Historial | `SistemaBiciSabana.historial()` (planificado) |
| Préstamos activos | `SistemaBiciSabana.prestamos_activos()` (planificado) |
| Cambiar puesto | `SistemaBiciSabana.mover_bicicleta()` (planificado) |

La tabla muestra equivalencias o métodos planificados; **no** afirma que todos estén implementados aún en Python.

### Uso de IA
Herramienta: ChatGPT (OpenAI). Fecha: 16 de noviembre de 2026.
Solicitud original: «Necesito completar completamente la interfaz» en el proyecto BiciSabana.
Alcance pedido: interfaz web funcional, reglas equivalentes a Python, mapa 3 × 10, las funcionalidades de los requerimientos originales y adicionales, y documentación.
La implementación se preparó con ayuda de IA y requiere revisión académica de los tres integrantes.

### Publicación
Los cambios se subieron en una rama para revisión, no en `main`. Integra la rama solamente después de revisar el comportamiento y el código.
