# HUMANA · sitio web

Sitio de HUMANA, consultoría en ética y gobernanza de IA para Colombia y Latinoamérica.
Se publica en **PythonAnywhere** (cuenta `HumanaLatam`) con una app Flask mínima que sirve las páginas
y guarda los mensajes del formulario de contacto.

| Archivo | Contenido |
|---|---|
| `index.html` | Inicio: reto, Ruta HUMANA, frameworks, servicios, experiencias, equipo y contacto |
| `privacidad.html` | Política de tratamiento de datos personales (Ley 1581 de 2012), en borrador |
| `gracias.html` | Confirmación tras enviar el formulario |
| `flask_app.py` | Sirve solo las páginas y carpetas de la lista blanca y recibe `POST /contacto` |
| `exportar_contactos.py` | Muestra o exporta a CSV los mensajes recibidos |
| `css/tokens.css` | Tokens de marca v1.1. **No editar aquí**: la fuente de verdad está en el repositorio privado |
| `css/site.css` | Composición de página y correcciones documentadas sobre los tokens |
| `logo/`, `img/` | Logos oficiales y fotos |

Los mensajes se guardan en `~/humana-datos/contactos.db`, **fuera** de la carpeta del sitio y fuera de Git.

## Publicar en PythonAnywhere (primera vez)

1. **Consola:** en *Consoles* abre una consola **Bash** y clona el repositorio:
   ```bash
   git clone https://github.com/acatherinebusinessintelligence/humana-web.git ~/humana-web
   ```
2. **Web app:** en la pestaña *Web* → *Add a new web app* → *Next* → **Manual configuration** (no "Flask") → la versión de Python más reciente → *Next*.
3. **Archivo WSGI:** en la misma pestaña, abre el enlace *WSGI configuration file*, borra todo su contenido y deja solo:
   ```python
   import sys
   sys.path.insert(0, "/home/HumanaLatam/humana-web")
   from flask_app import app as application
   ```
   Guarda.
4. **Forzar HTTPS:** en *Web* → *Security*, activa **Force HTTPS**.
5. **Recargar:** pulsa el botón verde **Reload**. El sitio queda en `https://humanalatam.pythonanywhere.com/`.

Flask ya viene instalado en PythonAnywhere. Si diera error de importación: `pip install --user flask` en la consola.

## Actualizar el sitio

```bash
cd ~/humana-web && git pull
```
y luego **Reload** en la pestaña *Web*.

## Leer los mensajes del formulario

```bash
python3 ~/humana-web/exportar_contactos.py --ver
```
Para descargarlos en Excel: `python3 ~/humana-web/exportar_contactos.py` y descarga `~/humana-datos/contactos.csv`
desde la pestaña *Files*. Son datos personales: bórralo después de usarlo.

## Problemas

Si algo falla, la pestaña *Web* tiene enlaces al **error log**: la última línea suele explicar el problema.
