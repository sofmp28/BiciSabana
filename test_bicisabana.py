"""Pruebas automáticas del Sprint 1 (biblioteca estándar unittest).
Ejecutar: python -m unittest -v test_bicisabana.py
"""
import unittest
from datetime import datetime
from contextlib import redirect_stdout
from io import StringIO
from bicisabana import Estudiante, SistemaBiciSabana, demostracion


class PruebasSprint1(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaBiciSabana()
        self.sistema.registrar_bicicleta("B01", "Roja", 1, 1)
        self.sistema.registrar_bicicleta("B02", "Azul", 1, 2)

    def test_01_registro_estado_inicial(self):
        self.assertEqual(self.sistema.buscar_bicicleta("B01").estado, "Disponible")

    def test_02_mostrar_informacion(self):
        info = self.sistema.buscar_bicicleta("B01").mostrar_informacion()
        self.assertIn("Roja", info)
        self.assertIn("Disponible", info)

    def test_03_registrar_prestamo(self):
        prestamo = self.sistema.registrar_prestamo("B01", "123456")
        self.assertTrue(prestamo.activo)
        self.assertEqual(self.sistema.buscar_bicicleta("B01").estado, "Prestada")

    def test_04_bloquear_segundo_prestamo_misma_bicicleta(self):
        self.sistema.registrar_prestamo("B01", "123456")
        with self.assertRaises(ValueError):
            self.sistema.registrar_prestamo("B01", "654321")
        self.assertEqual(len(self.sistema.prestamos), 1)

    def test_05_devolucion_correcta(self):
        self.sistema.registrar_prestamo("B01", "123456")
        prestamo = self.sistema.registrar_devolucion("B01")
        self.assertFalse(prestamo.activo)
        self.assertEqual(prestamo.bicicleta.estado, "Disponible")
        self.assertIsNotNone(prestamo.fecha_fin)

    def test_06_estudiante_asociado(self):
        prestamo = self.sistema.registrar_prestamo("B01", "123456")
        self.assertEqual(prestamo.estudiante.codigo, "123456")

    def test_07_hora_inicio(self):
        antes = datetime.now()
        prestamo = self.sistema.registrar_prestamo("B01", "123456")
        despues = datetime.now()
        self.assertIsInstance(prestamo.fecha_inicio, datetime)
        self.assertLessEqual(antes, prestamo.fecha_inicio)
        self.assertLessEqual(prestamo.fecha_inicio, despues)

    def test_08_codigo_estudiantil_no_numerico(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_prestamo("B01", "12AB56")
        self.assertEqual(self.sistema.buscar_bicicleta("B01").estado, "Disponible")

    def test_09_codigo_estudiantil_longitud_invalida(self):
        with self.assertRaises(ValueError):
            Estudiante("1234")

    def test_10_prestamo_bicicleta_inexistente(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_prestamo("B99", "123456")

    def test_11_no_dos_bicicletas_mismo_estudiante(self):
        self.sistema.registrar_prestamo("B01", "123456")
        with self.assertRaises(ValueError):
            self.sistema.registrar_prestamo("B02", "123456")
        self.assertEqual(self.sistema.buscar_bicicleta("B02").estado, "Disponible")

    def test_12_no_devolver_bicicleta_disponible(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_devolucion("B01")

    def test_13_no_duplicar_codigo_de_bicicleta(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_bicicleta("B01", "Negra", 2, 1)
        self.assertEqual(len(self.sistema.bicicletas), 2)

    def test_14_no_ocupar_dos_veces_un_puesto(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_bicicleta("B03", "Verde", 1, 1)

    def test_15_represtar_tras_devolucion(self):
        self.sistema.registrar_prestamo("B01", "123456")
        self.sistema.registrar_devolucion("B01")
        segundo = self.sistema.registrar_prestamo("B01", "654321")
        self.assertTrue(segundo.activo)
        self.assertEqual(len(self.sistema.prestamos), 2)

    def test_16_estudiante_tras_devolucion_puede_pedir_otra(self):
        self.sistema.registrar_prestamo("B01", "123456")
        self.sistema.registrar_devolucion("B01")
        nuevo = self.sistema.registrar_prestamo("B02", "123456")
        self.assertTrue(nuevo.activo)

    def test_17_bicicleta_inexistente_al_devolver(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_devolucion("B99")

    def test_18_registro_bicicleta_fila_fuera_rango(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_bicicleta("B03", "Verde", 4, 1)

    def test_19_consulta_completa_con_estudiante_actual(self):
        self.sistema.registrar_prestamo("B01", "123456")
        info = self.sistema.mostrar_informacion_bicicleta("B01")
        for dato in ("B01", "Roja", "Prestada", "(1, 1)", "123456"):
            self.assertIn(dato, info)

    def test_20_consulta_tras_devolucion_sin_estudiante_anterior(self):
        self.sistema.registrar_prestamo("B01", "123456")
        self.sistema.registrar_devolucion("B01")
        info = self.sistema.mostrar_informacion_bicicleta("B01")
        self.assertIn("Disponible", info)
        self.assertNotIn("Estudiante:", info)
        self.assertNotIn("123456", info)

    def test_21_consulta_represtamo_muestra_solo_estudiante_actual(self):
        self.sistema.registrar_prestamo("B01", "123456")
        self.sistema.registrar_devolucion("B01")
        self.sistema.registrar_prestamo("B01", "654321")
        info = self.sistema.mostrar_informacion_bicicleta("B01")
        self.assertIn("654321", info)
        self.assertNotIn("123456", info)

    def test_22_consulta_inexistente_no_altera_inventario(self):
        with self.assertRaises(ValueError):
            self.sistema.mostrar_informacion_bicicleta("B99")
        self.assertEqual(len(self.sistema.bicicletas), 2)
        self.assertEqual(self.sistema.prestamos, [])

    def test_23_registros_invalidos_no_agregan_bicicletas(self):
        # RF-01: cada entrada errónea debe dejar intacto el inventario.
        casos = [
            ("", "Verde", 2, 1), ("   ", "Verde", 2, 1),
            (None, "Verde", 2, 1), ("B03", "", 2, 1),
            ("B03", "   ", 2, 1), ("B03", None, 2, 1),
            ("B03", "Verde", 0, 1), ("B03", "Verde", True, 1),
            ("B03", "Verde", "2", 1), ("B03", "Verde", 2, 0),
            ("B03", "Verde", 2, 11), ("B03", "Verde", 2, False),
            ("B03", "Verde", 2, 1.5),
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                with self.assertRaises(ValueError):
                    self.sistema.registrar_bicicleta(*datos)
                self.assertEqual(len(self.sistema.bicicletas), 2)
                self.assertIsNone(self.sistema.buscar_bicicleta("B03"))

    def test_24_codigos_invalidos_no_crean_prestamos(self):
        for codigo in ("", "12345", "1234567", "12AB56", " 12345",
                       "１２３４５６", "¹²³⁴⁵⁶", 123456, None):
            with self.subTest(codigo=codigo):
                with self.assertRaises(ValueError):
                    self.sistema.registrar_prestamo("B01", codigo)
                self.assertEqual(self.sistema.prestamos, [])
                self.assertEqual(self.sistema.buscar_bicicleta("B01").estado,
                                 "Disponible")

    def test_25_codigo_estudiantil_con_ceros_iniciales(self):
        prestamo = self.sistema.registrar_prestamo("B01", "001234")
        self.assertEqual(prestamo.estudiante.codigo, "001234")

    def test_26_doble_devolucion_conserva_prestamo_cerrado(self):
        prestamo = self.sistema.registrar_prestamo("B01", "123456")
        self.sistema.registrar_devolucion("B01")
        fecha_fin = prestamo.fecha_fin
        with self.assertRaises(ValueError):
            self.sistema.registrar_devolucion("B01")
        self.assertEqual(prestamo.fecha_fin, fecha_fin)
        self.assertFalse(prestamo.activo)
        self.assertEqual(prestamo.bicicleta.estado, "Disponible")

    def test_27_demostracion_muestra_registros_y_ciclo_completo(self):
        salida = StringIO()
        with redirect_stdout(salida):
            demostracion()
        texto = salida.getvalue()
        for codigo in ("B01", "B02", "B03"):
            self.assertIn("REGISTRO: " + codigo, texto)
        self.assertIn("DURANTE: B01 | Color: Roja | Estado: Prestada", texto)
        self.assertIn("Estudiante: 123456", texto)
        self.assertIn("INTENTO DUPLICADO RECHAZADO:", texto)
        self.assertIn("DESPUÉS: B01 | Color: Roja | Estado: Disponible", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
