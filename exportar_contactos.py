"""Exporta los mensajes del formulario a un CSV.

Uso en una consola Bash de PythonAnywhere:
    python3 ~/humana-web/exportar_contactos.py            # escribe ~/humana-datos/contactos.csv
    python3 ~/humana-web/exportar_contactos.py --ver      # muestra los últimos 10 en pantalla

El CSV contiene datos personales: descárgalo, úsalo y bórralo. No lo subas a Git.
"""

import csv
import os
import sqlite3
import sys
from pathlib import Path

DATOS = Path(os.environ.get("HUMANA_DATOS", Path.home() / "humana-datos"))
BASE = DATOS / "contactos.db"

if not BASE.exists():
    sys.exit(f"Aún no hay mensajes ({BASE} no existe).")

con = sqlite3.connect(BASE)
filas = con.execute("SELECT * FROM contactos ORDER BY id DESC").fetchall()
columnas = [c[0] for c in con.execute("SELECT * FROM contactos LIMIT 0").description]

if "--ver" in sys.argv:
    for fila in filas[:10]:
        d = dict(zip(columnas, fila))
        print(f"#{d['id']} {d['fecha_utc']} · {d['nombre']} <{d['correo']}> · {d['interes']}\n   {d['mensaje']}\n")
    print(f"Total: {len(filas)} mensajes.")
else:
    salida = DATOS / "contactos.csv"
    with open(salida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        w.writerows(filas)
    print(f"{len(filas)} mensajes exportados a {salida}")
