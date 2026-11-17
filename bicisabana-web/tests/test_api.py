"""Pruebas locales de la integración Python: BD simulada, sin credenciales reales.
Ejecutar desde raíz: python -m unittest discover -s tests -v
"""
import importlib.util
import os
import sys
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path

# El cliente Supabase real se usa en Vercel; las pruebas usan un doble controlado.
stub = types.ModuleType("supabase")
stub.create_client = lambda *_: None
sys.modules.setdefault("supabase", stub)
app_path = Path(__file__).resolve().parent.parent / "api" / "index.py"
spec = importlib.util.spec_from_file_location("bicisabana_api", app_path)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class Respuesta:
    def __init__(self, data):
        self.data = data


class Consulta:
    def __init__(self, db, nombre):
        self.db = db
        self.nombre = nombre
        self.accion = "select"
        self.valores = None
        self.filtros = []
        self.orden = None

    def select(self, *_):
        return self

    def order(self, nombre, desc=False):
        self.orden = (nombre, desc)
        return self

    def eq(self, nombre, valor):
        self.filtros.append((nombre, valor, True))
        return self

    def neq(self, nombre, valor):
        self.filtros.append((nombre, valor, False))
        return self

    def insert(self, valores):
        self.accion, self.valores = "insert", valores
        return self

    def update(self, valores):
        self.accion, self.valores = "update", valores
        return self

    def delete(self):
        self.accion = "delete"
        return self

    def execute(self):
        tabla = self.db.tablas[self.nombre]
        filtradas = [r for r in tabla if all(
            (r.get(c) == v) if igual else (r.get(c) != v)
            for c, v, igual in self.filtros)]
        if self.accion == "select":
            if self.orden:
                columna, desc = self.orden
                filtradas.sort(key=lambda r: r.get(columna) or "", reverse=desc)
            return Respuesta([r.copy() for r in filtradas])
        if self.accion == "insert":
            filas = self.valores if isinstance(self.valores, list) else [self.valores]
            new = []
            for fila in filas:
                row = dict(fila)
                if self.nombre != "bicicletas":
                    row["id"] = len(tabla) + 1
                tabla.append(row)
                new.append(row.copy())
            return Respuesta(new)
        if self.accion == "update":
            for fila in filtradas:
                fila.update(self.valores)
            return Respuesta([r.copy() for r in filtradas])
        if self.accion == "delete":
            for fila in filtradas:
                tabla.remove(fila)
            return Respuesta([r.copy() for r in filtradas])
        raise AssertionError(self.accion)


class RPC:
    def __init__(self, db, nombre, datos):
        self.db, self.nombre, self.datos = db, nombre, datos

    def execute(self):
        codigo = self.datos["p_bicicleta"]
        bici = next(b for b in self.db.tablas["bicicletas"] if b["codigo"] == codigo)
        if self.nombre == "prestar_bicicleta_atomico":
            assert bici["estado"] == "Disponible"
            bici["estado"] = "Prestada"
            row = dict(id=len(self.db.tablas["prestamos"]) + 1,
                       bicicleta=codigo, estudiante=self.datos["p_estudiante"],
                       fecha_inicio=self.datos["p_inicio"], fecha_fin=None,
                       activo=True, duracion_minutos=None)
            self.db.tablas["prestamos"].append(row)
            return Respuesta(row.copy())
        if self.nombre == "devolver_bicicleta_atomico":
            p = next(p for p in self.db.tablas["prestamos"]
                     if p["activo"] and p["bicicleta"] == codigo)
            assert bici["estado"] == "Prestada"
            bici["estado"] = "Disponible"
            p.update(activo=False, fecha_fin=self.datos["p_fin"],
                     duracion_minutos=self.datos["p_duracion"])
            return Respuesta(p.copy())
        raise AssertionError(self.nombre)


class DB:
    def __init__(self):
        self.tablas = {
            "bicicletas": [dict(codigo="B01", color="Verde", fila=1,
                                puesto=1, estado="Disponible")],
            "prestamos": [],
            "intentos_rechazados": [],
        }

    def table(self, nombre):
        return Consulta(self, nombre)

    def rpc(self, nombre, datos):
        return RPC(self, nombre, datos)


class PruebasRutasVercel(unittest.TestCase):
    def test_originales(self):
        h = app.handler.__new__(app.handler)
        for path in ("/api/estado", "/api/prestamos", "/api/devoluciones"):
            h.path = path
            self.assertEqual(h._ruta(), path)

    def test_reescritas(self):
        h = app.handler.__new__(app.handler)
        for name in ("estado", "prestamos", "devoluciones", "bicicletas",
                     "mantenimiento", "reactivar", "mover", "retirar", "cargar-ejemplo"):
            h.path = "/api/index.py?operacion=" + name
            self.assertEqual(h._ruta(), "/api/" + name)

    def test_invalidas(self):
        h = app.handler.__new__(app.handler)
        for path in ("/api/index.py?operacion=%2E%2E%2Fsecretos", "/api/index.py"):
            h.path = path
            self.assertEqual(h._ruta(), "/api/index.py")


class PruebasIntegracion(unittest.TestCase):
    def setUp(self):
        self.db = DB()
        app._db = self.db

    def test_01_registrar_prestamo_python_y_bd(self):
        p = app.op_prestar(app.cargar_sistema(),
                           {"bicicleta": "b01", "estudiante": "123456"})
        self.assertTrue(p["activo"])
        self.assertEqual(self.db.tablas["bicicletas"][0]["estado"], "Prestada")
        self.assertEqual(len(app.estado()["prestamos"]), 1)

    def test_02_devolver_python_y_bd(self):
        app.op_prestar(app.cargar_sistema(),
                       {"bicicleta": "B01", "estudiante": "123456"})
        p = app.op_devolver(app.cargar_sistema(), {"bicicleta": "B01"})
        self.assertFalse(p["activo"])
        self.assertEqual(self.db.tablas["bicicletas"][0]["estado"], "Disponible")
        self.assertEqual(len(app.estado()["prestamos"]), 1)

    def test_03_no_prestar_bicicleta_duplicada(self):
        app.op_prestar(app.cargar_sistema(),
                       {"bicicleta": "B01", "estudiante": "123456"})
        with self.assertRaises(ValueError):
            app.op_prestar(app.cargar_sistema(),
                           {"bicicleta": "B01", "estudiante": "654321"})
        self.assertEqual(len(self.db.tablas["prestamos"]), 1)
        self.assertEqual(len(self.db.tablas["intentos_rechazados"]), 1)

    def test_04_formulario_cadena_fila_puesto(self):
        b = app.op_registrar(app.cargar_sistema(),
                            {"codigo": "b02", "color": "Azul", "fila": "3", "puesto": "10"})
        self.assertEqual((b["fila"], b["puesto"]), (3, 10))
        self.assertEqual(b["codigo"], "B02")

    def test_05_mantenimiento_y_reactivacion(self):
        b = app.op_mantenimiento(app.cargar_sistema(), {"bicicleta": "B01"})
        self.assertEqual(b["estado"], "En mantenimiento")
        b = app.op_reactivar(app.cargar_sistema(), {"bicicleta": "B01"})
        self.assertEqual(b["estado"], "Disponible")

    def test_06_reubicar_y_retirar(self):
        b = app.op_mover(app.cargar_sistema(), {"bicicleta": "B01", "fila": "2", "puesto": "4"})
        self.assertEqual((b["fila"], b["puesto"]), (2, 4))
        b = app.op_retirar(app.cargar_sistema(), {"bicicleta": "B01"})
        self.assertEqual(b["codigo"], "B01")
        self.assertEqual(self.db.tablas["bicicletas"], [])

    def test_07_validar_codigo_estudiante(self):
        with self.assertRaises(ValueError):
            app.op_prestar(app.cargar_sistema(),
                           {"bicicleta": "B01", "estudiante": "12AB56"})
        self.assertEqual(len(self.db.tablas["prestamos"]), 0)
        self.assertEqual(len(self.db.tablas["intentos_rechazados"]), 1)

    def test_08_http_sin_clave_devuelve_401(self):
        import threading
        from http.server import HTTPServer
        from urllib.request import urlopen
        from urllib.error import HTTPError
        from unittest.mock import patch
        servidor = HTTPServer(("127.0.0.1", 0), app.handler)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "clave-educativa-123"}):
                with self.assertRaises(HTTPError) as c:
                    urlopen(f"http://127.0.0.1:{servidor.server_port}/api/estado")
                self.assertEqual(c.exception.code, 401)
        finally:
            servidor.shutdown()
            servidor.server_close()

    def test_09_http_con_clave_consulta_y_prepara_prestamo(self):
        import json
        import threading
        from http.server import HTTPServer
        from urllib.request import Request, urlopen
        from unittest.mock import patch
        servidor = HTTPServer(("127.0.0.1", 0), app.handler)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "clave-educativa-123"}):
                url = f"http://127.0.0.1:{servidor.server_port}"
                post = Request(url + "/api/prestamos",
                               data=json.dumps({"bicicleta":"B01", "estudiante":"123456"}).encode(),
                               headers={"X-BiciSabana-Access":"clave-educativa-123",
                                        "Content-Type":"application/json"}, method="POST")
                with urlopen(post) as respuesta:
                    self.assertEqual(respuesta.status, 200)
                    cuerpo = json.load(respuesta)
                    self.assertTrue(cuerpo["ok"])
                get = Request(url + "/api/estado",
                              headers={"X-BiciSabana-Access":"clave-educativa-123"})
                with urlopen(get) as respuesta:
                    estados = json.load(respuesta)["resultado"]
                    self.assertEqual(estados["bicicletas"][0]["estado"], "Prestada")
        finally:
            servidor.shutdown()
            servidor.server_close()


if __name__ == "__main__":
    unittest.main()
