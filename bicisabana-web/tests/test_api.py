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

    def _http_server(self):
        import threading
        from http.server import HTTPServer
        servidor = HTTPServer(("127.0.0.1", 0), app.handler)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        return servidor

    def test_08_estado_sin_clave_es_real_y_enmascara_estudiante(self):
        import json
        from urllib.request import urlopen
        from unittest.mock import patch
        servidor = self._http_server()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "secreto-servidor-de-prueba-123456"}):
                app.op_prestar(app.cargar_sistema(),
                               {"bicicleta": "B01", "estudiante": "123456"})
                with urlopen(f"http://127.0.0.1:{servidor.server_port}/api/estado") as r:
                    data = json.load(r)
                    cookie = r.headers.get("Set-Cookie", "")
                    self.assertEqual(r.status, 200)
                    self.assertTrue(data["ok"])
                    self.assertTrue(cookie.startswith("bicisabana_sesion="))
                    self.assertEqual(data["resultado"]["prestamos"][0]["estudiante"], "••••56")
        finally:
            servidor.shutdown(); servidor.server_close()

    def test_09_prestar_y_devolver_sin_escribir_clave(self):
        import json
        from urllib.request import Request, urlopen
        from unittest.mock import patch
        servidor = self._http_server()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "secreto-servidor-de-prueba-123456"}):
                base = f"http://127.0.0.1:{servidor.server_port}"
                with urlopen(base + "/api/estado") as r:
                    cookie = r.headers["Set-Cookie"].split(";", 1)[0]
                def post(path, payload):
                    return Request(base + path, data=json.dumps(payload).encode(),
                                   method="POST", headers={"Content-Type": "application/json",
                                   "Origin":base, "Cookie":cookie})
                with urlopen(post("/api/prestamos", {"bicicleta":"B01", "estudiante":"123456"})) as r:
                    self.assertEqual(r.status,200)
                    self.assertTrue(json.load(r)["resultado"]["activo"])
                with urlopen(post("/api/devoluciones", {"bicicleta":"B01"})) as r:
                    self.assertFalse(json.load(r)["resultado"]["activo"])
                self.assertEqual(self.db.tablas["bicicletas"][0]["estado"], "Disponible")
                self.assertEqual(len(self.db.tablas["prestamos"]), 1)
        finally:
            servidor.shutdown(); servidor.server_close()

    def test_10_no_se_permiten_escrituras_sin_sesion(self):
        import json
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from unittest.mock import patch
        servidor = self._http_server()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "secreto-servidor-de-prueba-123456"}):
                base = f"http://127.0.0.1:{servidor.server_port}"
                body=json.dumps({"bicicleta":"B01","estudiante":"123456"}).encode()
                for headers in [{"Origin":base},{"Origin":"https://sitio-ajeno.example"}]:
                    request=Request(base+"/api/prestamos", data=body,method="POST",headers=headers)
                    with self.assertRaises(HTTPError) as exc:
                        urlopen(request)
                    self.assertEqual(exc.exception.code,403)
                self.assertEqual(len(self.db.tablas["prestamos"]),0)
        finally:
            servidor.shutdown(); servidor.server_close()

    def test_11_administracion_sigue_protegida(self):
        import json
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from unittest.mock import patch
        servidor = self._http_server()
        try:
            with patch.dict(os.environ, {"BICISABANA_ACCESS_KEY": "secreto-servidor-de-prueba-123456"}):
                base = f"http://127.0.0.1:{servidor.server_port}"
                body=json.dumps({"bicicleta":"B01"}).encode()
                request=Request(base+"/api/mantenimiento",data=body,method="POST")
                with self.assertRaises(HTTPError) as exc: urlopen(request)
                self.assertEqual(exc.exception.code,403)
                request=Request(base+"/api/mantenimiento",data=body,method="POST",
                                headers={"X-BiciSabana-Access":"secreto-servidor-de-prueba-123456"})
                with urlopen(request) as r:
                    self.assertEqual(json.load(r)["resultado"]["estado"],"En mantenimiento")
        finally:
            servidor.shutdown(); servidor.server_close()


class PruebasRutasVercel(unittest.TestCase):
    def test_reescritura_y_rutas_originales(self):
        h = app.handler.__new__(app.handler)
        for op in ("estado", "prestamos", "devoluciones", "mantenimiento"):
            h.path = f"/api/index.py?operacion={op}"
            self.assertEqual(h._ruta(), f"/api/{op}")
            h.path = f"/api/{op}"
            self.assertEqual(h._ruta(), f"/api/{op}")
    def test_reescritura_invalida(self):
        h = app.handler.__new__(app.handler)
        h.path = "/api/index.py?operacion=%2E%2E%2Fsecretos"
        self.assertEqual(h._ruta(), "/api/index.py")


if __name__ == "__main__":
    unittest.main()
