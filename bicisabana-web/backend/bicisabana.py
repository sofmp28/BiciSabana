"""BiciSabana: sistema educativo de préstamos de bicicletas.

Proyecto universitario de programación orientada a objetos.
Incluye RF-01 a RF-21. Los datos se mantienen en memoria durante la ejecución.
Ejecutar: python bicisabana.py
Probar:   python -m unittest discover -v
"""

from datetime import datetime


class Bicicleta:
    """Representa una bicicleta, su estado y la posición en la estación."""

    def __init__(self, codigo, color, fila, puesto):
        self.codigo = codigo
        self.color = color
        self.fila = fila
        self.puesto = puesto
        self.estado = "Disponible"

    def mostrar_informacion(self):
        return (f"{self.codigo} | Color: {self.color} | "
                f"Estado: {self.estado} | Puesto: ({self.fila}, {self.puesto})")

    def prestar(self):
        if self.estado != "Disponible":
            raise ValueError("La bicicleta no está disponible para prestar.")
        self.estado = "Prestada"

    def devolver(self):
        if self.estado != "Prestada":
            raise ValueError("No se puede devolver: la bicicleta no está prestada.")
        self.estado = "Disponible"

    def marcar_mantenimiento(self):
        if self.estado != "Disponible":
            raise ValueError("Solo se puede enviar a mantenimiento una bicicleta disponible.")
        self.estado = "En mantenimiento"

    def reactivar(self):
        if self.estado != "En mantenimiento":
            raise ValueError("La bicicleta no se encuentra en mantenimiento.")
        self.estado = "Disponible"


class Estudiante:
    """El código identifica un préstamo, pero NO autentica al estudiante."""

    def __init__(self, codigo):
        if not self.validar_formato(codigo):
            raise ValueError("El código estudiantil debe contener exactamente 6 números.")
        self.codigo = codigo

    def validar_formato(self, codigo):
        return (isinstance(codigo, str)
                and len(codigo) == 6
                and codigo.isascii()
                and codigo.isdigit())


class Prestamo:
    """Relaciona un estudiante, una bicicleta y sus horas de salida y retorno."""

    def __init__(self, bicicleta, estudiante):
        self.bicicleta = bicicleta
        self.estudiante = estudiante
        self.fecha_inicio = datetime.now()
        self.fecha_fin = None
        self.activo = True

    def cerrar(self):
        if not self.activo:
            raise ValueError("Este préstamo ya estaba cerrado.")
        self.fecha_fin = datetime.now()
        self.activo = False

    def calcular_duracion(self):
        if self.fecha_fin is None:
            return None
        return self.fecha_fin - self.fecha_inicio

    def mostrar_resumen(self):
        inicio = self.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S")
        if self.activo:
            return (f"{self.bicicleta.codigo} | Estudiante: {self.estudiante.codigo} "
                    f"| Salida: {inicio} | Activo")
        fin = self.fecha_fin.strftime("%Y-%m-%d %H:%M:%S")
        return (f"{self.bicicleta.codigo} | Estudiante: {self.estudiante.codigo} "
                f"| Salida: {inicio} | Regreso: {fin} "
                f"| Duración: {self.calcular_duracion()}")


class SistemaBiciSabana:
    """Coordina inventario, préstamos, estación, consultas y seguridad básica."""

    def __init__(self):
        self.bicicletas = []
        self.prestamos = []
        self.intentos_rechazados = []
        self.estacion = [[None for _ in range(10)] for _ in range(3)]

    @staticmethod
    def validar_ubicacion(fila, puesto):
        if (not isinstance(fila, int) or isinstance(fila, bool)
                or not 1 <= fila <= 3):
            raise ValueError("La fila debe ser un número entre 1 y 3.")
        if (not isinstance(puesto, int) or isinstance(puesto, bool)
                or not 1 <= puesto <= 10):
            raise ValueError("El puesto debe ser un número entre 1 y 10.")

    def registrar_bicicleta(self, codigo, color, fila, puesto):
        # Se valida completamente antes de alterar el inventario.
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código de la bicicleta no puede estar vacío.")
        if not isinstance(color, str) or not color.strip():
            raise ValueError("El color no puede estar vacío.")
        if self.buscar_bicicleta(codigo) is not None:
            raise ValueError("Ya existe una bicicleta con ese código.")
        self.validar_ubicacion(fila, puesto)
        if len(self.bicicletas) >= 30:
            raise ValueError("La estación solo admite 30 bicicletas.")
        if self.estacion[fila - 1][puesto - 1] is not None:
            raise ValueError("Ese puesto ya está ocupado por otra bicicleta.")
        bicicleta = Bicicleta(codigo, color, fila, puesto)
        self.bicicletas.append(bicicleta)
        self.estacion[fila - 1][puesto - 1] = bicicleta
        return bicicleta

    def buscar_bicicleta(self, codigo):
        for bicicleta in self.bicicletas:
            if bicicleta.codigo == codigo:
                return bicicleta
        return None

    def mostrar_informacion_bicicleta(self, codigo):
        bicicleta = self.buscar_bicicleta(codigo)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        informacion = bicicleta.mostrar_informacion()
        for prestamo in self.prestamos:
            if prestamo.activo and prestamo.bicicleta is bicicleta:
                return informacion + f" | Estudiante: {prestamo.estudiante.codigo}"
        return informacion

    def registrar_rechazo(self, codigo_bicicleta, codigo_estudiante, motivo):
        """Registra la razón del intento fallido sin crear un préstamo."""
        self.intentos_rechazados.append({
            "fecha": datetime.now(),
            "bicicleta": codigo_bicicleta,
            "estudiante": codigo_estudiante,
            "motivo": motivo,
        })

    def registrar_prestamo(self, codigo_bicicleta, codigo_estudiante):
        try:
            estudiante = Estudiante(codigo_estudiante)
            bicicleta = self.buscar_bicicleta(codigo_bicicleta)
            if bicicleta is None:
                raise ValueError("No existe una bicicleta con ese código.")
            if bicicleta.estado != "Disponible":
                raise ValueError("La bicicleta ya está prestada o no está disponible.")
            for prestamo in self.prestamos:
                if prestamo.activo and prestamo.estudiante.codigo == estudiante.codigo:
                    raise ValueError("Este estudiante ya tiene una bicicleta prestada.")
        except ValueError as error:
            self.registrar_rechazo(codigo_bicicleta, codigo_estudiante, str(error))
            raise

        nuevo_prestamo = Prestamo(bicicleta, estudiante)
        bicicleta.prestar()
        self.prestamos.append(nuevo_prestamo)
        return nuevo_prestamo

    def registrar_devolucion(self, codigo_bicicleta):
        bicicleta = self.buscar_bicicleta(codigo_bicicleta)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        if bicicleta.estado != "Prestada":
            raise ValueError("No se puede devolver una bicicleta que no esté prestada.")
        for prestamo in self.prestamos:
            if prestamo.activo and prestamo.bicicleta is bicicleta:
                prestamo.cerrar()
                bicicleta.devolver()
                return prestamo
        raise ValueError("No se encontró un préstamo activo asociado a la bicicleta.")

    def listar_disponibles(self):
        return [b for b in self.bicicletas if b.estado == "Disponible"]

    def contar_estados(self):
        return {
            "total": len(self.bicicletas),
            "disponibles": len(self.listar_disponibles()),
            "prestadas": sum(b.estado == "Prestada" for b in self.bicicletas),
            "mantenimiento": sum(b.estado == "En mantenimiento"
                                 for b in self.bicicletas),
        }

    def mostrar_mapa(self):
        """Devuelve la representación de las 3 filas por 10 puestos (RF-10)."""
        letras = {"Disponible": "D", "Prestada": "P", "En mantenimiento": "M"}
        filas = ["ESTACIÓN BICISABANA (D=Disponible, P=Prestada, M=Mantenimiento)"]
        for i, fila in enumerate(self.estacion, start=1):
            puestos = []
            for bicicleta in fila:
                if bicicleta is None:
                    puestos.append("[  --  ]")
                else:
                    puestos.append(f"[{bicicleta.codigo[:4]:>4}:{letras[bicicleta.estado]}]")
            filas.append(f"Fila {i}: " + " ".join(puestos))
        return "\n".join(filas)

    def prestamos_activos(self):
        return [p for p in self.prestamos if p.activo]

    def historial(self, codigo_bicicleta=None):
        if codigo_bicicleta is not None and self.buscar_bicicleta(codigo_bicicleta) is None:
            # Se conservan registros incluso si después se retiró la bicicleta.
            if not any(p.bicicleta.codigo == codigo_bicicleta for p in self.prestamos):
                raise ValueError("No existe una bicicleta con ese código.")
        return [p for p in self.prestamos
                if codigo_bicicleta is None or p.bicicleta.codigo == codigo_bicicleta]

    def marcar_mantenimiento(self, codigo):
        bicicleta = self._exigir_bicicleta(codigo)
        bicicleta.marcar_mantenimiento()
        return bicicleta

    def reactivar_bicicleta(self, codigo):
        bicicleta = self._exigir_bicicleta(codigo)
        bicicleta.reactivar()
        return bicicleta

    def mover_bicicleta(self, codigo, fila, puesto):
        bicicleta = self._exigir_bicicleta(codigo)
        self.validar_ubicacion(fila, puesto)
        if bicicleta.estado == "Prestada":
            raise ValueError("No se puede mover una bicicleta prestada.")
        ocupante = self.estacion[fila - 1][puesto - 1]
        if ocupante is not None and ocupante is not bicicleta:
            raise ValueError("Ese puesto ya está ocupado por otra bicicleta.")
        self.estacion[bicicleta.fila - 1][bicicleta.puesto - 1] = None
        bicicleta.fila, bicicleta.puesto = fila, puesto
        self.estacion[fila - 1][puesto - 1] = bicicleta
        return bicicleta

    def retirar_bicicleta(self, codigo):
        """Función complementaria para liberar puestos sin borrar el historial."""
        bicicleta = self._exigir_bicicleta(codigo)
        if bicicleta.estado == "Prestada":
            raise ValueError("No se puede retirar una bicicleta con préstamo activo.")
        self.estacion[bicicleta.fila - 1][bicicleta.puesto - 1] = None
        self.bicicletas.remove(bicicleta)
        return bicicleta

    def _exigir_bicicleta(self, codigo):
        bicicleta = self.buscar_bicicleta(codigo)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        return bicicleta

    def consultar_rechazos(self):
        return list(self.intentos_rechazados)

    def cargar_bicicletas_ejemplo(self):
        """Carga las 30 bicicletas B01 a B30 para demostrar el sistema."""
        if self.bicicletas:
            raise ValueError("La estación debe estar vacía para cargar la demostración.")
        colores = ["Azul", "Rojo", "Verde", "Amarillo", "Negro", "Blanco"]
        for numero in range(1, 31):
            fila = (numero - 1) // 10 + 1
            puesto = (numero - 1) % 10 + 1
            self.registrar_bicicleta(
                f"B{numero:02d}", colores[(numero - 1) % len(colores)],
                fila, puesto)

    def menu(self, entrada=input, salida=print):
        """Menú que sigue atendiendo operaciones hasta que el monitor sale."""
        opciones = """
=== BICISABANA ===
1. Registrar bicicleta      2. Consultar bicicleta
3. Prestar bicicleta        4. Devolver bicicleta
5. Listar disponibles       6. Contar bicicletas
7. Mostrar mapa 3 x 10      8. Préstamos activos
9. Historial de bicicleta  10. Marcar mantenimiento
11. Reactivar bicicleta    12. Mover bicicleta
13. Intentos rechazados    14. Retirar bicicleta
15. Cargar 30 de ejemplo    0. Salir
"""
        while True:
            salida(opciones)
            try:
                opcion = entrada("Elige una opción: ").strip()
                if opcion == "0":
                    salida("Gracias por utilizar BiciSabana.")
                    break
                if opcion == "1":
                    codigo = entrada("Código: ").strip()
                    color = entrada("Color: ").strip()
                    fila = int(entrada("Fila (1-3): ").strip())
                    puesto = int(entrada("Puesto (1-10): ").strip())
                    b = self.registrar_bicicleta(codigo, color, fila, puesto)
                    salida("Registrada: " + b.mostrar_informacion())
                elif opcion == "2":
                    salida(self.mostrar_informacion_bicicleta(entrada("Código: ").strip()))
                elif opcion == "3":
                    codigo = entrada("Bicicleta: ").strip()
                    estudiante = entrada("Código estudiantil (6 dígitos): ").strip()
                    p = self.registrar_prestamo(codigo, estudiante)
                    salida("Préstamo correcto: " + p.mostrar_resumen())
                elif opcion == "4":
                    p = self.registrar_devolucion(entrada("Bicicleta: ").strip())
                    salida("Devolución correcta: " + p.mostrar_resumen())
                elif opcion == "5":
                    disponibles = self.listar_disponibles()
                    salida(f"Disponibles: {len(disponibles)}")
                    for b in disponibles:
                        salida(b.mostrar_informacion())
                elif opcion == "6":
                    salida(str(self.contar_estados()))
                elif opcion == "7":
                    salida(self.mostrar_mapa())
                elif opcion == "8":
                    activos = self.prestamos_activos()
                    salida(f"Préstamos activos: {len(activos)}")
                    for p in activos:
                        salida(p.mostrar_resumen())
                elif opcion == "9":
                    codigo = entrada("Código bicicleta (vacío = todos): ").strip()
                    movimientos = self.historial(codigo or None)
                    salida(f"Movimientos: {len(movimientos)}")
                    for p in movimientos:
                        salida(p.mostrar_resumen())
                elif opcion == "10":
                    b = self.marcar_mantenimiento(entrada("Bicicleta: ").strip())
                    salida("En mantenimiento: " + b.codigo)
                elif opcion == "11":
                    b = self.reactivar_bicicleta(entrada("Bicicleta: ").strip())
                    salida("Disponible: " + b.codigo)
                elif opcion == "12":
                    codigo = entrada("Bicicleta: ").strip()
                    fila = int(entrada("Nueva fila: ").strip())
                    puesto = int(entrada("Nuevo puesto: ").strip())
                    salida("Movida: " + self.mover_bicicleta(
                        codigo, fila, puesto).mostrar_informacion())
                elif opcion == "13":
                    rechazos = self.consultar_rechazos()
                    salida(f"Préstamos rechazados: {len(rechazos)}")
                    for r in rechazos:
                        salida(f"{r['fecha']:%Y-%m-%d %H:%M} | "
                               f"{r['bicicleta']} | {r['motivo']}")
                elif opcion == "14":
                    b = self.retirar_bicicleta(entrada("Bicicleta: ").strip())
                    salida("Retirada: " + b.codigo)
                elif opcion == "15":
                    self.cargar_bicicletas_ejemplo()
                    salida("Se cargaron las 30 bicicletas de demostración.")
                else:
                    salida("Opción no válida. Selecciona una opción del menú.")
            except (ValueError, TypeError) as error:
                salida("No se pudo completar la operación: " + str(error))
            except (EOFError, KeyboardInterrupt):
                salida("\nPrograma finalizado.")
                break


def demostracion():
    """Conserva el ejemplo anterior del Sprint 1 para las pruebas originales."""
    sistema = SistemaBiciSabana()
    sistema.registrar_bicicleta("B01", "Roja", 1, 1)
    sistema.registrar_bicicleta("B02", "Azul", 1, 2)
    sistema.registrar_bicicleta("B03", "Verde", 1, 3)

    print("=== BICISABANA | DEMOSTRACIÓN SPRINT 1 ===")
    for bicicleta in sistema.bicicletas:
        print("REGISTRO:", bicicleta.mostrar_informacion())
    print("ANTES:", sistema.mostrar_informacion_bicicleta("B01"))
    prestamo = sistema.registrar_prestamo("B01", "123456")
    print("PRÉSTAMO:", prestamo.bicicleta.codigo,
          "al estudiante", prestamo.estudiante.codigo)
    print("HORA DE SALIDA:", prestamo.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"))
    print("DURANTE:", sistema.mostrar_informacion_bicicleta("B01"))
    try:
        sistema.registrar_prestamo("B01", "654321")
    except ValueError as error:
        print("INTENTO DUPLICADO RECHAZADO:", error)
    devolucion = sistema.registrar_devolucion("B01")
    print("DEVOLUCIÓN:", devolucion.bicicleta.codigo,
          "| Estado:", devolucion.bicicleta.estado)
    print("DESPUÉS:", sistema.mostrar_informacion_bicicleta("B01"))


if __name__ == "__main__":
    SistemaBiciSabana().menu()
