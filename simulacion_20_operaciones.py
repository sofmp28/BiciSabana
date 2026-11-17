"""Simulación reproducible de 20 operaciones para DevSecOps — Monitorear.

10 préstamos válidos + 6 devoluciones válidas + 4 préstamos rechazados.
No utiliza datos reales de estudiantes.
Ejecutar: python simulacion_20_operaciones.py
"""
from bicisabana import SistemaBiciSabana


def simular():
    sistema = SistemaBiciSabana()
    sistema.cargar_bicicletas_ejemplo()
    aceptadas = 0
    rechazadas = 0
    detalle = []

    def operar(etiqueta, funcion):
        nonlocal aceptadas, rechazadas
        try:
            funcion()
            aceptadas += 1
            detalle.append(f"ACEPTADA  | {etiqueta}")
        except ValueError as error:
            rechazadas += 1
            detalle.append(f"RECHAZADA | {etiqueta} | {error}")

    for n in range(1, 11):
        operar(f"Prestar B{n:02d} al código {n:06d}",
               lambda n=n: sistema.registrar_prestamo(f"B{n:02d}", f"{n:06d}"))
    for n in range(1, 7):
        operar(f"Devolver B{n:02d}",
               lambda n=n: sistema.registrar_devolucion(f"B{n:02d}"))

    operar("Intento repetido B07", lambda: sistema.registrar_prestamo("B07", "123456"))
    operar("Segundo préstamo del estudiante 000010",
           lambda: sistema.registrar_prestamo("B11", "000010"))
    operar("Bicicleta inexistente B31",
           lambda: sistema.registrar_prestamo("B31", "555555"))
    operar("Código de estudiante inválido",
           lambda: sistema.registrar_prestamo("B12", "12AB56"))

    total = aceptadas + rechazadas
    conteos = sistema.contar_estados()
    assert (total, aceptadas, rechazadas) == (20, 16, 4)
    assert len(sistema.consultar_rechazos()) == rechazadas
    assert (conteos["prestadas"], conteos["disponibles"]) == (4, 26)

    print("BICISABANA | SIMULACIÓN DEVSECOPS — MONITOREAR")
    for numero, linea in enumerate(detalle, start=1):
        print(f"{numero:02d}. {linea}")
    print(f"TOTAL={total} | ACEPTADAS={aceptadas} | RECHAZADAS={rechazadas}")
    print("Estados finales:", conteos)
    print("Conclusión 1: 16 de 20 operaciones simuladas se aceptaron (80%).")
    print("Conclusión 2: 4 intentos inválidos (20%) fueron rechazados; "
          "el inventario terminó coherente: 4 prestadas y 26 disponibles.")
    return sistema


if __name__ == "__main__":
    simular()
