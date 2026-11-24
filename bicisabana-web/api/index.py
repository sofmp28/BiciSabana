"""BiciSabana: API Python para Vercel + Supabase.

La lógica de validación permanece en backend/bicisabana.py. Los cambios
relacionados entre préstamos y bicicletas se confirman atómicamente mediante
funciones de PostgreSQL definidas en supabase/schema.sql.

La estación se conecta sin introducir una clave en la interfaz. Los préstamos
y devoluciones utilizan una sesión anónima firmada, con comprobación de origen.
La gestión administrativa sigue protegida por una clave en el servidor.
La service role de Supabase se usa SOLO en el servidor; nunca en el navegador.
"""

import hmac
import hashlib
import secrets
import time
from http.cookies import SimpleCookie, CookieError
import json
import logging
import re
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from bicisabana import Bicicleta, Estudiante, Prestamo, SistemaBiciSabana  # noqa: E402

from supabase import create_client  # noqa: E402

logger = logging.getLogger(__name__)
_db = None


def _db_client():
    global _db
    if _db is None:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("Faltan variables del servidor SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY")
        _db = create_client(url, key)
    return _db


def _iso(fecha):
    if fecha is None:
        return None
    if fecha.tzinfo is None:
        fecha = fecha.astimezone()
    return fecha.astimezone(timezone.utc).isoformat()


def _single(data):
    if isinstance(data, list):
        if not data:
            raise ValueError("El inventario cambió. Actualiza la pantalla e inténtalo nuevamente.")
        return data[0]
    if data is None:
        raise ValueError("No se pudo completar la operación. Actualiza la pantalla.")
    return data


def cargar_sistema():
    """Reconstruye el estado orientado a objetos antes de cada operación."""
    db = _db_client()
    s = SistemaBiciSabana()
    for fila in db.table("bicicletas").select("*").execute().data:
        b = Bicicleta(fila["codigo"], fila["color"], fila["fila"], fila["puesto"])
        b.estado = fila["estado"]
        s.bicicletas.append(b)
        s.estacion[b.fila - 1][b.puesto - 1] = b
    for fila in (db.table("prestamos").select("*")
                 .eq("activo", True).execute().data):
        b = s.buscar_bicicleta(fila["bicicleta"])
        if b is None:
            logger.error("Préstamo activo sin bicicleta: %s", fila["id"])
            continue
        p = Prestamo(b, Estudiante(fila["estudiante"]))
        # Prestamo.cerrar() usa datetime.now() sin zona horaria.
        # Convertir el timestamp UTC de Supabase a hora local sin tzinfo
        # evita restar datetimes de tipos incompatibles.
        p.fecha_inicio = (datetime.fromisoformat(fila["fecha_inicio"])
                          .astimezone().replace(tzinfo=None))
        p.id = fila["id"]
        s.prestamos.append(p)
    return s


def estado():
    """Fotografía actual de la base de datos en el servidor."""
    db = _db_client()
    return {
        "bicicletas": db.table("bicicletas").select("*").order("codigo").execute().data,
        "prestamos": (db.table("prestamos").select("*")
                      .order("fecha_inicio", desc=True).execute().data),
        "rechazos": (db.table("intentos_rechazados").select("*")
                     .order("fecha", desc=True).execute().data),
    }


def estado_publico():
    """Inventario y movimientos; nunca revelar códigos completos de estudiantes."""
    datos = estado()
    for prestamo in datos["prestamos"]:
        codigo = str(prestamo.get("estudiante") or "").strip()
        prestamo["estudiante"] = "••••" + codigo[-2:] if codigo else "—"
    for rechazo in datos["rechazos"]:
        codigo = str(rechazo.get("estudiante") or "").strip()
        rechazo["estudiante"] = "••••" + codigo[-2:] if codigo else "—"
    return datos


def crear_sesion():
    """Token aleatorio temporal firmado solo con secreto del servidor."""
    secreto = os.getenv("BICISABANA_ACCESS_KEY", "")
    if not secreto:
        raise RuntimeError("La clave interna de sesión no está configurada.")
    cuerpo = str(int(time.time())) + "." + secrets.token_urlsafe(20)
    firma = hmac.new(secreto.encode(), cuerpo.encode(), hashlib.sha256).hexdigest()
    return cuerpo + "." + firma


def validar_sesion(token):
    secreto = os.getenv("BICISABANA_ACCESS_KEY", "")
    if not secreto or not token or len(token) > 250:
        return False
    partes = token.split(".")
    if len(partes) != 3 or not partes[0].isdigit():
        return False
    instante = int(partes[0])
    if not 0 <= time.time() - instante <= 7200:
        return False
    cuerpo = partes[0] + "." + partes[1]
    firma = hmac.new(secreto.encode(), cuerpo.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(partes[2], firma)


def _registrar_rechazo(info):
    _db_client().table("intentos_rechazados").insert(info).execute()


def _codigo(d, campo="bicicleta"):
    value = d.get(campo, "")
    return value.strip().upper() if isinstance(value, str) else value


def _entero(value):
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        return int(value.strip())
    return value


def op_prestar(s, d):
    codigo, estudiante = _codigo(d), d.get("estudiante", "")
    if isinstance(estudiante, str):
        estudiante = estudiante.strip()
    try:
        p = s.registrar_prestamo(codigo, estudiante)
    except ValueError:
        rechazo = s.intentos_rechazados[-1]
        _registrar_rechazo({
            "fecha": _iso(rechazo["fecha"]), "bicicleta": rechazo["bicicleta"],
            "estudiante": str(rechazo["estudiante"])[:32],
            "motivo": rechazo["motivo"]})
        raise
    # La función SQL confirma el cambio de estado y el nuevo préstamo
    # en una misma transacción: no deja bicicletas bloqueadas si falla.
    try:
        respuesta = _db_client().rpc("prestar_bicicleta_atomico", {
            "p_bicicleta": p.bicicleta.codigo,
            "p_estudiante": p.estudiante.codigo,
            "p_inicio": _iso(p.fecha_inicio),
        }).execute()
    except Exception:
        _registrar_rechazo({
            "fecha": _iso(datetime.now(timezone.utc)),
            "bicicleta": str(codigo)[:32], "estudiante": str(estudiante)[:32],
            "motivo": "Préstamo no disponible por actualización concurrente.",
        })
        raise ValueError("La bicicleta o el estudiante ya tienen un préstamo activo. Actualiza la pantalla.") from None
    return _single(respuesta.data)


def op_devolver(s, d):
    p = s.registrar_devolucion(_codigo(d))
    try:
        return _single(_db_client().rpc("devolver_bicicleta_atomico", {
            "p_bicicleta": p.bicicleta.codigo,
            "p_fin": _iso(p.fecha_fin),
            "p_duracion": max(0, round(p.calcular_duracion().total_seconds() / 60)),
        }).execute().data)
    except Exception:
        raise ValueError("El préstamo ya cambió. Actualiza la pantalla e inténtalo de nuevo.") from None


def op_registrar(s, d):
    b = s.registrar_bicicleta(_codigo(d, "codigo"), d.get("color", ""),
                              _entero(d.get("fila")), _entero(d.get("puesto")))
    try:
        result = _db_client().table("bicicletas").insert({
            "codigo": b.codigo, "color": b.color,
            "fila": b.fila, "puesto": b.puesto, "estado": b.estado,
        }).select("*").execute().data
        return _single(result)
    except Exception:
        raise ValueError("El código, el puesto o la capacidad ya no están disponibles.") from None


def _cambiar_estado(s, codigo, operacion, estado_anterior):
    b = operacion(codigo)
    result = (_db_client().table("bicicletas").update({"estado": b.estado})
              .eq("codigo", b.codigo).eq("estado", estado_anterior)
              .select("*").execute().data)
    return _single(result)


def op_mantenimiento(s, d):
    return _cambiar_estado(s, _codigo(d),
                           s.marcar_mantenimiento, "Disponible")


def op_reactivar(s, d):
    return _cambiar_estado(s, _codigo(d),
                           s.reactivar_bicicleta, "En mantenimiento")


def op_mover(s, d):
    b = s.mover_bicicleta(_codigo(d), _entero(d.get("fila")), _entero(d.get("puesto")))
    try:
        result = (_db_client().table("bicicletas")
                  .update({"fila": b.fila, "puesto": b.puesto})
                  .eq("codigo", b.codigo).neq("estado", "Prestada")
                  .select("*").execute().data)
        return _single(result)
    except Exception:
        raise ValueError("Ese puesto ya está ocupado o la bicicleta cambió de estado.") from None


def op_retirar(s, d):
    b = s.retirar_bicicleta(_codigo(d))
    result = (_db_client().table("bicicletas").delete()
              .eq("codigo", b.codigo).neq("estado", "Prestada")
              .select("*").execute().data)
    _single(result)
    return {"codigo": b.codigo}


def op_cargar_ejemplo(s, _d):
    s.cargar_bicicletas_ejemplo()
    valores = [{"codigo": b.codigo, "color": b.color, "fila": b.fila,
                "puesto": b.puesto, "estado": b.estado} for b in s.bicicletas]
    # El INSERT múltiple se realiza en una sola instrucción SQL.
    try:
        _db_client().table("bicicletas").insert(valores).execute()
    except Exception:
        raise ValueError("La estación cambió o ya tiene bicicletas. Actualiza la pantalla.") from None
    return {"cantidad": 30}


RUTAS = {
    "/api/prestamos": op_prestar,
    "/api/devoluciones": op_devolver,
    "/api/bicicletas": op_registrar,
    "/api/mantenimiento": op_mantenimiento,
    "/api/reactivar": op_reactivar,
    "/api/mover": op_mover,
    "/api/retirar": op_retirar,
    "/api/cargar-ejemplo": op_cargar_ejemplo,
}


class handler(BaseHTTPRequestHandler):  # Vercel reconoce este nombre exacto.
    def _enviar(self, status, cuerpo, sesion=None):
        data = json.dumps(cuerpo, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if sesion:
            # La cookie es inaccesible a JavaScript, de uso exclusivo de /api.
            seguro = "; Secure" if self.headers.get("Host", "").split(":")[0] != "127.0.0.1" else ""
            self.send_header("Set-Cookie", "bicisabana_sesion=" + sesion +
                             "; HttpOnly; SameSite=Strict; Path=/api; Max-Age=7200" + seguro)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _ruta(self):
        parsed = urlsplit(self.path)
        ruta = parsed.path
        if ruta == "/api/estado" or ruta in RUTAS:
            return ruta
        if ruta.rstrip("/") in ("/api", "/api/index", "/api/index.py"):
            operaciones = parse_qs(parsed.query).get("operacion", [])
            if len(operaciones) == 1 and re.fullmatch(r"[a-z][a-z0-9-]*", operaciones[0]):
                return "/api/" + operaciones[0]
        return ruta

    def _autorizar_admin(self):
        clave = os.getenv("BICISABANA_ACCESS_KEY", "")
        recibida = self.headers.get("X-BiciSabana-Access", "")
        if not clave or not recibida or not hmac.compare_digest(clave, recibida):
            self._enviar(403, {"ok": False, "error":
                "Operación administrativa protegida. Solicita autorización al responsable de la estación."})
            return False
        return True

    def _autorizar_publico(self):
        # CSRF: peticiones de lectura son públicas, escrituras solo desde el sitio.
        origen = self.headers.get("Origin", "")
        host = self.headers.get("Host", "")
        partes = urlsplit(origen)
        local = host.startswith("127.0.0.1:") or host.startswith("localhost:")
        if partes.netloc != host or partes.scheme != ("http" if local else "https"):
            self._enviar(403, {"ok": False, "error": "Solicitud desde un origen no autorizado."})
            return False
        try:
            cookie = SimpleCookie()
            cookie.load(self.headers.get("Cookie", ""))
            token = cookie["bicisabana_sesion"].value if "bicisabana_sesion" in cookie else ""
        except (CookieError, ValueError):
            token = ""
        if not validar_sesion(token):
            self._enviar(403, {"ok": False, "error":
                "La sesión venció. Recarga BiciSabana para seguir operando."})
            return False
        return True

    def do_GET(self):
        ruta = self._ruta()
        if ruta != "/api/estado":
            return self._enviar(404, {"ok": False, "error": "Ruta no encontrada."})
        try:
            sesion = crear_sesion()
            self._enviar(200, {"ok": True, "resultado": estado_publico()}, sesion=sesion)
        except Exception:
            logger.exception("Error consultando inventario")
            self._enviar(503, {"ok": False, "error": "No se pudo consultar la base de datos."})

    def do_POST(self):
        ruta = self._ruta()
        funcion = RUTAS.get(ruta)
        if funcion is None:
            return self._enviar(404, {"ok": False, "error": "Ruta no encontrada."})
        es_publico = ruta in ("/api/prestamos", "/api/devoluciones")
        if es_publico:
            if not self._autorizar_publico():
                return
        elif not self._autorizar_admin():
            return
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            if largo <= 0 or largo > 4096:
                return self._enviar(413, {"ok": False, "error": "Solicitud vacía o demasiado grande."})
            data = json.loads(self.rfile.read(largo))
            if not isinstance(data, dict):
                raise ValueError("Envía los datos de la operación como un objeto JSON.")
            resultado = funcion(cargar_sistema(), data)
            self._enviar(200, {"ok": True, "resultado": resultado})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._enviar(400, {"ok": False, "error": str(error)})
        except Exception:
            logger.exception("Error de servidor en %s", ruta)
            self._enviar(503, {"ok": False, "error": "No se pudo completar la operación. Intenta más tarde."})
