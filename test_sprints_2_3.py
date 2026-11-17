"""Pruebas de funcionalidades de BiciSabana, Sprints 2 y 3."""
import unittest
from contextlib import redirect_stdout
from io import StringIO
from time import perf_counter

from bicisabana import SistemaBiciSabana


class PruebasSprints2y3(unittest.TestCase):
    def setUp(self):
        self.s = SistemaBiciSabana()
        for numero in range(1, 6):
            self.s.registrar_bicicleta(f"B{numero:02d}", "Azul",
                                      1, numero)

    def test_01_listar_disponibles_rf06(self):
        self.s.registrar_prestamo("B01", "123456")
        self.s.registrar_prestamo("B02", "654321")
        self.assertEqual([b.codigo for b in self.s.listar_disponibles()],
                         ["B03", "B04", "B05"])

    def test_02_buscar_codigo_existente_inexistente_rf07(self):
        self.assertEqual(self.s.buscar_bicicleta("B05").codigo, "B05")
        self.assertIsNone(self.s.buscar_bicicleta("B99"))

    def test_03_totales_rf09(self):
        self.s.registrar_prestamo("B01", "123456")
        self.assertEqual(self.s.contar_estados(),
                         {"total": 5, "disponibles": 4,
                          "prestadas": 1, "mantenimiento": 0})

    def test_04_mapa_3_por_10_rf10(self):
        self.assertEqual(len(self.s.estacion), 3)
        self.assertTrue(all(len(fila) == 10 for fila in self.s.estacion))
        texto = self.s.mostrar_mapa()
        self.assertIn("B01:D", texto)
        self.assertIn("Fila 3:", texto)

    def test_05_mapa_actualiza_estados_rf10(self):
        self.s.registrar_prestamo("B01", "123456")
        self.assertIn("B01:P", self.s.mostrar_mapa())
        self.s.registrar_devolucion("B01")
        self.assertIn("B01:D", self.s.mostrar_mapa())

    def test_06_validacion_id_rf08(self):
        with self.assertRaises(ValueError):
            self.s.registrar_prestamo("B01", "12A456")
        self.assertEqual(self.s.buscar_bicicleta("B01").estado, "Disponible")

    def test_07_un_prestamo_por_estudiante_rf12(self):
        self.s.registrar_prestamo("B01", "123456")
        with self.assertRaises(ValueError):
            self.s.registrar_prestamo("B02", "123456")
        self.assertEqual(len(self.s.prestamos_activos()), 1)

    def test_08_consultar_estudiante_rf13(self):
        self.s.registrar_prestamo("B01", "123456")
        self.assertIn("123456", self.s.mostrar_informacion_bicicleta("B01"))

    def test_09_inicio_automatico_rf14(self):
        prestamo = self.s.registrar_prestamo("B01", "123456")
        self.assertIsNotNone(prestamo.fecha_inicio)

    def test_10_fin_duracion_rf15(self):
        self.s.registrar_prestamo("B01", "123456")
        prestamo = self.s.registrar_devolucion("B01")
        self.assertIsNotNone(prestamo.fecha_fin)
        self.assertGreaterEqual(prestamo.calcular_duracion().total_seconds(), 0)

    def test_11_mantenimiento_bloquea_prestamo_rf16(self):
        self.s.marcar_mantenimiento("B03")
        self.assertEqual(self.s.buscar_bicicleta("B03").estado,
                         "En mantenimiento")
        with self.assertRaises(ValueError):
            self.s.registrar_prestamo("B03", "123456")
        self.assertIn("B03:M", self.s.mostrar_mapa())

    def test_12_no_mantenimiento_si_prestada_rf16(self):
        self.s.registrar_prestamo("B03", "123456")
        with self.assertRaises(ValueError):
            self.s.marcar_mantenimiento("B03")
        self.assertEqual(self.s.buscar_bicicleta("B03").estado, "Prestada")

    def test_13_reactivar_rf17(self):
        self.s.marcar_mantenimiento("B03")
        self.s.reactivar_bicicleta("B03")
        self.assertEqual(self.s.buscar_bicicleta("B03").estado, "Disponible")
        self.assertTrue(self.s.registrar_prestamo("B03", "123456").activo)

    def test_14_reactivar_solo_mantenimiento_rf17(self):
        with self.assertRaises(ValueError):
            self.s.reactivar_bicicleta("B03")

    def test_15_historial_dos_ciclos_rf18(self):
        self.s.registrar_prestamo("B01", "123456")
        self.s.registrar_devolucion("B01")
        self.s.registrar_prestamo("B01", "654321")
        self.s.registrar_devolucion("B01")
        movimientos = self.s.historial("B01")
        self.assertEqual(len(movimientos), 2)
        self.assertTrue(all(not p.activo for p in movimientos))

    def test_16_prestamos_activos_rf19(self):
        self.s.registrar_prestamo("B01", "123456")
        self.s.registrar_prestamo("B02", "654321")
        self.assertEqual(len(self.s.prestamos_activos()), 2)
        self.s.registrar_devolucion("B01")
        self.assertEqual([p.bicicleta.codigo for p in self.s.prestamos_activos()],
                         ["B02"])

    def test_17_mover_puesto_libre_rf20(self):
        self.s.mover_bicicleta("B03", 2, 5)
        self.assertIsNone(self.s.estacion[0][2])
        self.assertEqual(self.s.estacion[1][4].codigo, "B03")
        self.assertIn("B03:D", self.s.mostrar_mapa())

    def test_18_prohibir_mover_a_ocupado_rf20(self):
        with self.assertRaises(ValueError):
            self.s.mover_bicicleta("B03", 1, 1)
        self.assertEqual((self.s.buscar_bicicleta("B03").fila,
                          self.s.buscar_bicicleta("B03").puesto), (1, 3))

    def test_19_no_mover_prestada_rf20(self):
        self.s.registrar_prestamo("B03", "123456")
        with self.assertRaises(ValueError):
            self.s.mover_bicicleta("B03", 2, 1)
        self.assertEqual((self.s.buscar_bicicleta("B03").fila,
                          self.s.buscar_bicicleta("B03").puesto), (1, 3))

    def test_20_rechazos_con_motivo_rf21(self):
        self.s.registrar_prestamo("B01", "123456")
        for codigo, estudiante in [("B01", "654321"), ("B99", "123456")]:
            with self.assertRaises(ValueError):
                self.s.registrar_prestamo(codigo, estudiante)
        self.assertEqual(len(self.s.consultar_rechazos()), 2)
        self.assertTrue(all(reg["motivo"] for reg in self.s.consultar_rechazos()))
        self.assertEqual(len(self.s.prestamos), 1)

    def test_21_maximo_30_bicicletas(self):
        s = SistemaBiciSabana()
        s.cargar_bicicletas_ejemplo()
        self.assertEqual(len(s.bicicletas), 30)
        with self.assertRaises(ValueError):
            s.registrar_bicicleta("B31", "Azul", 3, 10)
        self.assertEqual(len(s.bicicletas), 30)

    def test_22_no_cargar_ejemplos_duplicados(self):
        with self.assertRaises(ValueError):
            self.s.cargar_bicicletas_ejemplo()

    def test_23_contar_tres_estados(self):
        self.s.registrar_prestamo("B01", "123456")
        self.s.marcar_mantenimiento("B02")
        conteos = self.s.contar_estados()
        self.assertEqual(conteos, {"total": 5, "disponibles": 3,
                                   "prestadas": 1, "mantenimiento": 1})
        self.assertEqual(sum(conteos[k] for k in
                             ("disponibles", "prestadas", "mantenimiento")), 5)

    def test_24_menu_repite_y_sale_rf11(self):
        entradas = iter(["6", "7", "0"])
        salidas = []
        self.s.menu(entrada=lambda prompt: next(entradas),
                    salida=salidas.append)
        self.assertGreaterEqual(len(salidas), 4)
        self.assertIn("Gracias", salidas[-1])

    def test_25_menu_sigue_despues_de_cinco_errores_rnf03(self):
        entradas = iter(["texto", "x", "-4", "99", "", "6", "0"])
        salidas = []
        self.s.menu(entrada=lambda prompt: next(entradas),
                    salida=salidas.append)
        self.assertGreaterEqual(sum("Opción no válida" in str(s)
                                   for s in salidas), 5)
        self.assertIn("Gracias", salidas[-1])

    def test_26_menu_con_datos_mal_formados_no_se_cae(self):
        entradas = iter(["1", "B06", "Azul", "abc", "6", "0"])
        salidas = []
        self.s.menu(entrada=lambda prompt: next(entradas),
                    salida=salidas.append)
        self.assertTrue(any("No se pudo" in str(s) for s in salidas))
        self.assertIsNone(self.s.buscar_bicicleta("B06"))
        self.assertIn("Gracias", salidas[-1])

    def test_27_mantenimiento_no_muta_si_invalido(self):
        with self.assertRaises(ValueError):
            self.s.marcar_mantenimiento("B99")
        self.assertEqual(self.s.contar_estados()["mantenimiento"], 0)

    def test_28_ubicacion_no_muta_si_invalida(self):
        antes = self.s.mostrar_mapa()
        for fila, puesto in [(0, 1), (4, 1), (2, 0),
                             (2, 11), (True, 2), ("2", 2)]:
            with self.subTest(fila=fila, puesto=puesto):
                with self.assertRaises(ValueError):
                    self.s.mover_bicicleta("B03", fila, puesto)
                self.assertEqual(self.s.mostrar_mapa(), antes)

    def test_29_retirar_libera_posicion_no_el_historial(self):
        self.s.registrar_prestamo("B01", "123456")
        self.s.registrar_devolucion("B01")
        self.s.retirar_bicicleta("B01")
        self.assertIsNone(self.s.estacion[0][0])
        self.assertEqual(len(self.s.historial("B01")), 1)
        self.s.registrar_bicicleta("B99", "Negra", 1, 1)

    def test_30_retirar_prestada_rechazado(self):
        self.s.registrar_prestamo("B01", "123456")
        with self.assertRaises(ValueError):
            self.s.retirar_bicicleta("B01")
        self.assertEqual(self.s.buscar_bicicleta("B01").estado, "Prestada")

    def test_31_respuesta_30_bicicletas_menor_segundo_rnf04(self):
        s = SistemaBiciSabana()
        s.cargar_bicicletas_ejemplo()
        inicio = perf_counter()
        s.mostrar_mapa()
        s.contar_estados()
        s.listar_disponibles()
        s.buscar_bicicleta("B30")
        s.prestamos_activos()
        transcurrido = perf_counter() - inicio
        self.assertLess(transcurrido, 1.0)

    def test_32_simular_20_operaciones_y_contar(self):
        """10 préstamos y 10 devoluciones, sin datos de personas reales."""
        for numero in range(1, 11):
            codigo_bici = f"B{numero:02d}"
            if numero > 5:
                self.s.registrar_bicicleta(codigo_bici, "Roja", 2, numero-5)
            codigo_estudiante = f"{numero:06d}"
            self.s.registrar_prestamo(codigo_bici, codigo_estudiante)
            self.s.registrar_devolucion(codigo_bici)
        self.assertEqual(len(self.s.historial()), 10)
        self.assertEqual(len(self.s.prestamos_activos()), 0)
        self.assertEqual(len(self.s.consultar_rechazos()), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
