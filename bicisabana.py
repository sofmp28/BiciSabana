"""BiciSabana — Sprint 1.

Prototipo educativo de programación orientada a objetos.
Los datos se conservan solo mientras el programa está abierto.
Ejecutar: python bicisabana.py
"""

from datetime import datetime


class Bicicleta:
    """Representa una bicicleta de la estación."""

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


class Estudiante:
    """Identifica al estudiante por un código de prueba de seis dígitos."""

    def __init__(self, codigo):
        if not self.validar_formato(codigo):
            raise ValueError("El código estudiantil debe contener exactamente 6 números.")
        self.codigo = codigo

    def validar_formato(self, codigo):
        # No es una prueba de identidad: solo valida longitud y caracteres.
        return isinstance(codigo, str) and len(codigo) == 6 and codigo.isascii() and codigo.isdigit()


class Prestamo:
    """Conecta una bicicleta con el estudiante que la recibió."""

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


class SistemaBiciSabana:
    """Coordina los registros, préstamos y devoluciones."""

    def __init__(self):
        self.bicicletas = []
        self.prestamos = []

    def registrar_bicicleta(self, codigo, color, fila, puesto):
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código de la bicicleta no puede estar vacío.")
        if not isinstance(color, str) or not color.strip():
            raise ValueError("El color no puede estar vacío.")
        if self.buscar_bicicleta(codigo) is not None:
            raise ValueError("Ya existe una bicicleta con ese código.")
        if not isinstance(fila, int) or isinstance(fila, bool) or not 1 <= fila <= 3:
            raise ValueError("La fila debe ser un número entre 1 y 3.")
        if not isinstance(puesto, int) or isinstance(puesto, bool) or not 1 <= puesto <= 10:
            raise ValueError("El puesto debe ser un número entre 1 y 10.")
        for bicicleta in self.bicicletas:
            if bicicleta.fila == fila and bicicleta.puesto == puesto:
                raise ValueError("Ese puesto ya está ocupado por otra bicicleta.")
        bicicleta = Bicicleta(codigo, color, fila, puesto)
        self.bicicletas.append(bicicleta)
        return bicicleta

    def buscar_bicicleta(self, codigo):
        for bicicleta in self.bicicletas:
            if bicicleta.codigo == codigo:
                return bicicleta
        return None

    def mostrar_informacion_bicicleta(self, codigo):
        """Consulta los datos y el estudiante del préstamo activo (RF-02 y RF-13)."""
        bicicleta = self.buscar_bicicleta(codigo)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        informacion = bicicleta.mostrar_informacion()
        # Los préstamos cerrados no indican quién tiene la bicicleta ahora.
        for prestamo in self.prestamos:
            if prestamo.activo and prestamo.bicicleta is bicicleta:
                return informacion + f" | Estudiante: {prestamo.estudiante.codigo}"
        return informacion

    def registrar_prestamo(self, codigo_bicicleta, codigo_estudiante):
        # Primero se valida TODO; solo al final se modifica el inventario.
        estudiante = Estudiante(codigo_estudiante)
        bicicleta = self.buscar_bicicleta(codigo_bicicleta)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        if bicicleta.estado != "Disponible":
            raise ValueError("La bicicleta ya está prestada o no está disponible.")
        for prestamo in self.prestamos:
            if prestamo.activo and prestamo.estudiante.codigo == estudiante.codigo:
                raise ValueError("Este estudiante ya tiene una bicicleta prestada.")
        prestamo = Prestamo(bicicleta, estudiante)
        bicicleta.prestar()
        self.prestamos.append(prestamo)
        return prestamo

    def registrar_devolucion(self, codigo_bicicleta):
        bicicleta = self.buscar_bicicleta(codigo_bicicleta)
        if bicicleta is None:
            raise ValueError("No existe una bicicleta con ese código.")
        if bicicleta.estado != "Prestada":
            raise ValueError("No se puede devolver una bicicleta que no esté prestada.")
        for prestamo in self.prestamos:
            if prestamo.activo and prestamo.bicicleta.codigo == codigo_bicicleta:
                prestamo.cerrar()
                bicicleta.devolver()
                return prestamo
        raise ValueError("No se encontró un préstamo activo asociado a la bicicleta.")


def demostracion():
    """Ejemplo fijo del Sprint 1. El menú interactivo se hará en el Sprint 3."""
    sistema = SistemaBiciSabana()
    sistema.registrar_bicicleta("B01", "Roja", 1, 1)
    sistema.registrar_bicicleta("B02", "Azul", 1, 2)
    sistema.registrar_bicicleta("B03", "Verde", 1, 3)

    print("=== BICISABANA | DEMOSTRACIÓN SPRINT 1 ===")
    # RF-01: comprobar en pantalla las tres bicicletas recién registradas.
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
    demostracion()
