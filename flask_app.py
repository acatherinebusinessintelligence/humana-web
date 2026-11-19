"""HUMANA · aplicación web para PythonAnywhere.

Sirve el sitio estático y recibe el formulario de contacto, que se guarda en
una base SQLite FUERA de la carpeta del sitio (por defecto ~/humana-datos/).

Solo se publican las páginas y carpetas de la lista blanca: el código, la base
de datos y los archivos internos del repositorio nunca se sirven.
"""

import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from flask import Flask, abort, redirect, request, send_from_directory

RAIZ = Path(__file__).resolve().parent
DATOS = Path(os.environ.get("HUMANA_DATOS", Path.home() / "humana-datos"))
BASE = DATOS / "contactos.db"

PAGINAS = {"index.html", "privacidad.html", "gracias.html"}
CARPETAS = {"css", "logo", "img"}
INTERESES = {
    "Cursos cortos certificados",
    "Talleres para mi equipo",
    "Consultoría",
    "HUMANA Radar",
    "Alianzas e impacto social",
}
CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LIMITE_POR_HORA = 5  # envíos por IP

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024  # el formulario no necesita más


def conexion():
    DATOS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(BASE)
    con.execute(
        """CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_utc TEXT NOT NULL,
            nombre TEXT NOT NULL,
            organizacion TEXT,
            correo TEXT NOT NULL,
            interes TEXT,
            mensaje TEXT,
            autorizacion INTEGER NOT NULL,
            ip TEXT
        )"""
    )
    return con


_envios = {}  # ip -> marcas de tiempo (memoria del proceso; suficiente para spam básico)


def demasiados_envios(ip):
    ahora = time.time()
    recientes = [t for t in _envios.get(ip, []) if ahora - t < 3600]
    _envios[ip] = recientes
    if len(recientes) >= LIMITE_POR_HORA:
        return True
    recientes.append(ahora)
    return False


def pagina_aviso(titulo, texto, codigo=400):
    html = f"""<!DOCTYPE html><html lang="es-CO"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(titulo)} · HUMANA</title>
<link rel="icon" href="/logo/humana-icono.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,400&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/tokens.css"><link rel="stylesheet" href="/css/site.css"></head>
<body><main class="h-seccion"><div class="h-contenedor h-legal">
<a href="/"><img src="/logo/humana-logo-claro.svg" alt="HUMANA" width="140" height="30"></a>
<h1 style="margin-top:48px">{escape(titulo)}</h1><p>{escape(texto)}</p>
<p><a class="h-btn" href="/#contacto">Volver al formulario</a></p></div></main></body></html>"""
    return html, codigo


@app.get("/")
def inicio():
    return send_from_directory(RAIZ, "index.html")


@app.get("/<pagina>")
def pagina(pagina):
    if pagina not in PAGINAS:
        abort(404)
    return send_from_directory(RAIZ, pagina)


@app.get("/<carpeta>/<path:archivo>")
def estatico(carpeta, archivo):
    if carpeta not in CARPETAS:
        abort(404)
    return send_from_directory(RAIZ / carpeta, archivo)


@app.post("/contacto")
def contacto():
    f = request.form
    # Campo trampa: invisible para personas, los robots lo llenan.
    if f.get("sitio_web"):
        return redirect("/gracias.html", code=303)

    nombre = f.get("nombre", "").strip()[:120]
    organizacion = f.get("organizacion", "").strip()[:160]
    correo = f.get("correo", "").strip()[:200]
    interes = f.get("interes", "").strip()
    mensaje = f.get("mensaje", "").strip()[:4000]
    autorizacion = f.get("autorizacion") == "si"

    if not nombre or not CORREO_RE.match(correo):
        return pagina_aviso("Revisa tus datos", "Necesitamos tu nombre y un correo válido para responderte.")
    if not autorizacion:
        return pagina_aviso(
            "Falta tu autorización",
            "Para responderte necesitamos que autorices el tratamiento de tus datos (Ley 1581 de 2012).",
        )
    if interes not in INTERESES:
        interes = ""

    ip = request.headers.get("X-Real-IP", request.remote_addr or "")
    if demasiados_envios(ip):
        return pagina_aviso("Vamos más despacio", "Recibimos varios mensajes seguidos. Intenta de nuevo en una hora.", 429)

    with conexion() as con:
        con.execute(
            "INSERT INTO contactos (fecha_utc, nombre, organizacion, correo, interes, mensaje, autorizacion, ip)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), nombre, organizacion, correo, interes, mensaje, 1, ip),
        )
    return redirect("/gracias.html", code=303)


@app.after_request
def cabeceras(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
