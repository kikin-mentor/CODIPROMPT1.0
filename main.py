import web
import sqlite3
import re
import os
import requests
import json
from dotenv import load_dotenv
import html
#import time
#from flask import Flask, render_template, request, redirect, session, url_for, jsonify
#import plotly.graph_objs as go
#import plotly.io as pio

# Cargar variables de entorno
load_dotenv()

urls = (
    '/', 'Index',
    '/registro', 'Registro',
    '/inicio_sesion', 'InicioSesion',
    '/info_secion','InfoSecion',
    '/leccion_rapida','LeccionRapida',
    '/perfil_user','PerfilUser',
    '/leccion1', 'Leccion1',
    '/leccion2', 'Leccion2',
    '/leccion3', 'Leccion3',
    '/leccion4', 'Leccion4',
    '/leccion5', 'Leccion5',
    '/leccion6', 'Leccion6',
    '/leccion7', 'Leccion7',
    '/leccion8', 'Leccion8',
    '/leccion9', 'Leccion9',
    '/leccion_personalizada', 'LeccionPersonalizada',
    '/static/(.*)', 'Static',
    '/cambiar_contraseña', 'cambiarcontraseña',
    '/actividad1', 'actividad1',
    '/actividad2', 'actividad2',
    '/actividad3', 'actividad3',
    '/actividad4', 'actividad4',
    '/actividad5', 'actividad5',
    '/actividad6', 'actividad6',
    '/actividad7', 'actividad7',
    '/actividad8', 'actividad8',
    '/actividad9', 'actividad9',
    '/api_chat', 'ApiChat',
    '/iniciar_secion_admin','IniciarSecionAdmin',
    '/info','Info',
    '/logout', 'Logout',
)

render = web.template.render('templates')
api_key = os.getenv("GROQ_API_KEY")
modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")

web.config.debug = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("sessions"))

# =============== BD ÚNICA ===============
DB_PATH = "codiprompt.db"

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def obtener_id_tiempo(id_usuario):
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        SELECT id_time FROM tiempo_de_uso
        WHERE id_usuario=?
        ORDER BY id_time DESC
        LIMIT 1
    """, (id_usuario,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else 0

# =============== VISTAS ===============
class Index:
    def GET(self):
        return render.index()

class Registro:
    def GET(self):
        return render.registro()

    def POST(self):
        form = web.input()
        campos = [
            form.get('nombre', '').strip(),
            form.get('apellidos', '').strip(),
            form.get('usuario', '').strip(),
            form.get('plantel', '').strip(),
            form.get('matricula', '').strip(),
            form.get('correo', '').strip(),
            form.get('password', '').strip(),
            form.get('confirmar', '').strip()
        ]
        if any(not campo for campo in campos):
            return render.registro(error="llena los campos para continuar")

        correo = form.get('correo', '').strip()
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if not re.match(correo_regex, correo):
            return render.registro(error="Ingresa un correo válido")

        password = form.get('password', '').strip()
        confirmar = form.get('confirmar', '').strip()
        if password != confirmar:
            return render.registro(error="Las contraseñas no coinciden")

        nombre = form.get('nombre', '').strip()
        apellidos = form.get('apellidos', '').strip()
        usuario = form.get('usuario', '').strip()
        plantel = form.get('plantel', '').strip()
        matricula = form.get('matricula', '').strip()

        try:
            con = get_db()
            cur = con.cursor()
            # Tabla: usuarios
            cur.execute("""
                INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, apellidos, usuario, plantel, matricula, correo, password))
            con.commit()
            con.close()
            return render.inicio_sesion()
        except sqlite3.IntegrityError as e:
            if 'usuario' in str(e):
                return render.registro(error="El nombre de usuario ya existe")
            if 'correo' in str(e):
                return render.registro(error="El correo ya está registrado")
            if 'matricula' in str(e):
                return render.registro(error="La matrícula ya está registrada")
            return render.registro(error=f"Error al registrar: {e}")
        except Exception as e:
            return render.registro(error=f"Error al registrar: {e}")

class InicioSesion:
    def GET(self):
        return render.inicio_sesion()

    def POST(self):
        form = web.input()
        usuario = (form.usuario or "").strip()
        password = (form.password or "").strip()

        if not usuario or not password:
            return render.inicio_sesion(error="Llena los campos para continuar")

        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if '@' in usuario and not re.match(correo_regex, usuario):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            con = get_db()
            cur = con.cursor()
            # Tabla: usuarios
            cur.execute("""
                SELECT id_usuario, usuario, password
                FROM usuarios
                WHERE usuario=? OR correo=?
            """, (usuario, usuario))
            row = cur.fetchone()

            if row and row["password"] == password:
                session.logged_in = True
                session.usuario_id = row["id_usuario"]
                session.username = row["usuario"]

                # Tabla: sesiones (registro de inicio)
                try:
                    cur.execute("INSERT INTO sesiones (id_usuario) VALUES (?)", (row["id_usuario"],))
                    con.commit()
                    session.id_sesion = cur.lastrowid
                except Exception as e:
                    print("⚠️ Error registrando sesión:", e)
                    session.id_sesion = None

                con.close()
                return web.seeother('/info_secion')
            else:
                con.close()
                return render.inicio_sesion(error="Usuario o contraseña incorrecta")

        except Exception as e:
            return render.inicio_sesion(error=f"Error al procesar los datos: {e}")

class Logout:
    def POST(self):
        # Debe estar logueado y tener id_sesion
        if not getattr(session, "logged_in", False) or not getattr(session, "id_sesion", None):
            session.kill()
            return web.seeother('/inicio_sesion')

        id_sesion = session.id_sesion
        id_usuario = session.usuario_id

        try:
            con = get_db()
            cur = con.cursor()

            # Tabla: sesiones -> marcar fin
            cur.execute("UPDATE sesiones SET fin = CURRENT_TIMESTAMP WHERE id_sesion = ?", (id_sesion,))

            # Calcular minutos en SQL
            cur.execute("""
                SELECT CAST(ROUND((julianday(COALESCE(fin, CURRENT_TIMESTAMP)) - julianday(inicio)) * 1440) AS INTEGER)
                FROM sesiones
                WHERE id_sesion = ?
            """, (id_sesion,))
            row = cur.fetchone()
            minutos = max(0, int(row[0])) if row and row[0] is not None else 0

            # Tabla: tiempo_de_uso -> insertar
            cur.execute("""
                INSERT INTO tiempo_de_uso (id_usuario, id_sesion, minutos)
                VALUES (?, ?, ?)
            """, (id_usuario, id_sesion, minutos))

            con.commit()
            con.close()
        except Exception as e:
            print("❌ Error guardando tiempo de uso:", e)

        session.kill()
        return web.seeother('/inicio_sesion')

class InfoSecion:
    def GET(self):
        return render.info_secion()

class Info:
    def GET (self):
        return render.info()

class IniciarSecionAdmin:
    def GET(self):
        return render.iniciar_secion_admin()

class LeccionRapida:
    def GET(self):
        return render.leccion_rapida()

class PerfilUser:
    def GET(self):
        print("DEBUG >> session.usuario_id:", getattr(session, 'usuario_id', None))
        if hasattr(session, 'usuario_id') and session.usuario_id:
            usuario_id = session.usuario_id
            con = get_db()
            cur = con.cursor()
            # Tabla: usuarios
            cur.execute("SELECT usuario FROM usuarios WHERE id_usuario=?", (usuario_id,))
            row = cur.fetchone()
            con.close()
            nombre_usuario = row['usuario'] if row else "usuario"
            return render.perfil_user(usuario=nombre_usuario)
        else:
            return web.seeother('/inicio_sesion')

    def POST(self):
        if not hasattr(session, 'usuario_id') or not session.usuario_id:
            return web.seeother('/inicio_sesion')

        form = web.input()
        usuario_id = session.usuario_id

        # ───── Cambio de nombre ─────
        if 'nombre' in form:
            nuevo_nombre = form.get('nombre', '').strip()
            if nuevo_nombre:
                try:
                    con = get_db()
                    cur = con.cursor()
                    # Tabla: usuarios
                    cur.execute("UPDATE usuarios SET usuario=? WHERE id_usuario=?", (nuevo_nombre, usuario_id))
                    con.commit()
                    con.close()
                    return web.seeother('/perfil_user')
                except Exception as e:
                    return render.perfil_user(usuario=nuevo_nombre, error=f"Error al actualizar nombre: {e}")
            else:
                return render.perfil_user(usuario=form.get('nombre'), error="El nombre no puede estar vacío")

        # ───── Borrado de cuenta ─────
        usuario = form.get('usuario', '').strip()
        password = form.get('password', '').strip()

        if not usuario or not password:
            return render.perfil_user(usuario=form.get('nombre'), error="Debes ingresar usuario y contraseña para borrar la cuenta")

        try:
            con = get_db()
            cur = con.cursor()
            # Tabla: usuarios
            cur.execute("SELECT id_usuario FROM usuarios WHERE usuario=? AND password=?", (usuario, password))
            row = cur.fetchone()
            if not row:
                con.close()
                return render.perfil_user(usuario=form.get('nombre'), error="Usuario o contraseña incorrectos")

            id_usuario = row['id_usuario']
            # Borrar respetando FKs: tiempo_de_uso -> sesiones -> usuarios
            # Tablas: tiempo_de_uso, sesiones, usuarios
            cur.execute("DELETE FROM tiempo_de_uso WHERE id_usuario=?", (id_usuario,))
            cur.execute("DELETE FROM sesiones WHERE id_usuario=?", (id_usuario,))
            cur.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
            con.commit()
            con.close()
            session.kill()
            return render.index(mensaje="Cuenta eliminada correctamente")

        except Exception as e:
            return render.perfil_user(usuario=form.get('nombre'), error=f"Error al borrar la cuenta: {e}")

# ====== Lecciones (como estaban) ======
class Leccion1:
    def GET(self):
        return render.leccion1()

class Leccion2:
    def GET(self):
        return render.leccion2()

class Leccion3:
    def GET(self):
        return render.leccion3()

class Leccion4:
    def GET(self):
        return render.leccion4()

class Leccion5:
    def GET(self):
        return render.leccion5()

class Leccion6:
    def GET(self):
        return render.leccion6()

class Leccion7:
    def GET(self):
        return render.leccion7()

class Leccion8:
    def GET(self):
        return render.leccion8()

class Leccion9:
    def GET(self):
        return render.leccion9()

class LeccionPersonalizada:
    def GET(self):
        return render.leccion_personalizada()

class Static:
    def GET(self, file):
        return web.redirect('/static/' + file)

class cambiarcontraseña:
    def GET(self):
        return render.cambiar_contraseña()

    def POST(self):
        form = web.input()
        usuario = (form.usuario or "").strip()
        correo = (form.correo or "").strip()
        antigua_pass = (form.antigua_password or "").strip()
        nueva_pass = (form.nueva_password or "").strip()
        repite_pass = (form.repite_password or "").strip()

        if not usuario or not correo or not antigua_pass or not nueva_pass or not repite_pass:
            return render.cambiar_contraseña(error="Llena todos los campos")
        if nueva_pass != repite_pass:
            return render.cambiar_contraseña(error="Las contraseñas no coinciden")

        try:
            con = get_db()
            cur = con.cursor()
            # Tabla: usuarios
            cur.execute("SELECT 1 FROM usuarios WHERE usuario=?", (usuario,))
            if not cur.fetchone():
                con.close()
                return render.cambiar_contraseña(error="No se encontro usuario")
            cur.execute("SELECT 1 FROM usuarios WHERE correo=?", (correo,))
            if not cur.fetchone():
                con.close()
                return render.cambiar_contraseña(error="No se encontro correo")
            cur.execute("SELECT password FROM usuarios WHERE usuario=? AND correo=?", (usuario, correo))
            row = cur.fetchone()
            if not row or row[0] != antigua_pass:
                con.close()
                return render.cambiar_contraseña(error="La contraseña no es valida")
            cur.execute("UPDATE usuarios SET password=? WHERE usuario=? AND correo=?", (nueva_pass, usuario, correo))
            con.commit()
            con.close()
            return web.seeother("/inicio_sesion")
        except Exception as e:
            return render.cambiar_contraseña(error=f"Error al cambiar contraseña: {e}")

# ====== Actividades ======
class actividad1:
    def GET(self):
        return render.actividad1(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()

        if not codigo:
            return render.actividad1(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Crea un archivo nuevo con la estructura básica de un documento HTML5. "
            "Incluye en el <body> un título que diga “Hola, mundo” y un párrafo donde te presentes (nombre, edad, afición). "
            "El documento comienza con <!DOCTYPE html>. Se utiliza <html lang=\"es\">. "
            "Dentro de <head> aparecen las meta etiquetas correctas y el título. "
            "Dentro del <body> hay un encabezado <h1> y un <p> con presentación."
        )
        if not api_key1:
            return render.actividad1(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key1}"},
                json=payload,
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            feedback = data["choices"][0]["message"]["content"]

            # Extraer puntaje (0-10)
            m = re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback)
            puntaje = int(m.group(1)) if m else 0

            # Si aprueba, registrar en tabla lecciones_completadas (en la MISMA BD)
            if puntaje >= 7 and getattr(session, "usuario_id", None):
                try:
                    con = get_db()
                    cur = con.cursor()
                    # Tabla: lecciones_completadas
                    cur.execute("""
                        INSERT INTO lecciones_completadas
                        (id_usuario, id_leccion, id_actividad, tipo_de_leccion, estado, id_lenguaje, id_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        session.usuario_id,
                        1,     # lección 1
                        1,     # actividad 1
                        "HTML",
                        "completada",
                        1,     # id_lenguaje (ajusta si usas otro catálogo)
                        obtener_id_tiempo(session.usuario_id)  # FK a tiempo_de_uso si existe un id_time reciente
                    ))
                    con.commit()
                    con.close()
                except Exception as e:
                    print("⚠️ Error insertando lección completada:", e)

            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

# Las demás actividades no escriben en BD (solo evalúan y renderizan), así que no toco tablas:
class actividad2:
    def GET(self):
        return render.actividad2(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad2(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Escribe una noticia falsa (puede ser humorística, educativa o creativa). "
            "Usa <h1> para el título, <h2> para subtítulo, <h3> para secciones; "
            "usa <p> con <strong>, <em>, <mark>."
        )
        if not api_key1:
            return render.actividad2(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type": "application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad2(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad2(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad3:
    def GET(self):
        return render.actividad3(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad3(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Inserta una imagen (<img> con alt, width, height), un párrafo de bienvenida y tres enlaces <a> "
            "(externo, red social con target=\"_blank\", y ancla interna con id + href=\"#...\")."
        )
        if not api_key1:
            return render.actividad3(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad3(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad3(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad4:
    def GET(self):
        return render.actividad4(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad4(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Crea una <ul> con 4 elementos, una <ol> con pasos de un platillo, y una lista anidada con categorías 'Tecnología' y 'Arte'."
        )
        if not api_key1:
            return render.actividad4(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad4(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad4(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad5:
    def GET(self):
        return render.actividad5(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad5(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Tabla con <thead>, <tbody>, <tfoot>, con border y al menos 3 filas de productos; usa colspan/rowspan si aplica."
        )
        if not api_key1:
            return render.actividad5(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad5(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad5(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad6:
    def GET(self):
        return render.actividad6(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad6(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Formulario con: input texto (required, maxlength=40), email (type=email), password (min 6), textarea con placeholder y botón; usa label for/id."
        )
        if not api_key1:
            return render.actividad6(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad6(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad6(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad7:
    def GET(self):
        return render.actividad7(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad7(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Agrega <style> en el <head>; body color de fondo claro; h1/h2 azules y centrados; p con fuente diferente y tamaño mayor; usa márgenes y padding."
        )
        if not api_key1:
            return render.actividad7(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad7(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad7(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad8:
    def GET(self):
        return render.actividad8(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad8(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Página con <header>, <nav> (lista), <main> con <section id='Noticias'> y dos <article> (cada uno con título y párrafo); <footer> con nombre y año."
        )
        if not api_key1:
            return render.actividad8(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad8(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad8(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad9:
    def GET(self):
        return render.actividad9(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html="")
        codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad9(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
            "Incluye <audio> (musica.mp3), <video> con dimensiones y un <iframe> de YouTube; escribe un <p> explicativo antes de cada uno."
        )
        if not api_key1:
            return render.actividad9(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio + " No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": "Evalúa el siguiente código:\n" + codigo}
            ],
            "temperature": 0.4
        }
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad9(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad9(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

# ====== Prompt Trainer (sin cambios de tablas, usa API externa) ======
start_activate = False
TRAINER_QUESTIONS = [
    "¿Tu documento comienza con &lt;<!DOCTYPE html>&gt; y contiene &lt;<html>&gt;, <head> y <body> correctamente estructurados?",
    "¿Declaraste el idioma del sitio con <html lang=\"es\">?",
    "¿Utilizarás etiquetas semánticas como <header>, <footer>, <section>, <article> para mejorar accesibilidad y SEO?",
    "¿El <head> incluye <title>, <meta charset=\"UTF-8\">, y <meta name=\"viewport\"> para diseño responsive?",
    "¿Necesitas favicon, keywords o descripción (<meta name=\"description\">)?",
    "¿Usarás encabezados <h1> a <h6> y contenido textual con <p>, <strong>, <em>?",
    "¿Insertarás imágenes con <img src=\"...\" alt=\"...\"> o contenido multimedia como audio/video con etiquetas HTML5?",
    "¿Tendrás navegación con <nav> y enlaces <a href=\"...\"> internos/externos (target=\"_blank\")?",
    "¿Mostrarás listas <ul>/<ol> o tablas <table> para estructurar datos?",
    "¿Vas a enlazar un archivo CSS externo (<link rel=\"stylesheet\">) o escribir estilos inline?",
    "¿Usarás layout con Flexbox, Grid o columnas flotantes?",
    "¿Tu sitio será responsive? ¿Incluirás media queries para adaptarlo a distintos dispositivos?",
    "¿Implementarás modo oscuro o selector de temas con clases o lógica JS?",
    "¿Usarás Flask para definir rutas como /inicio, /usuarios, /productos?",
    "¿Los templates HTML tendrán variables Jinja2 como {{ nombre }} para mostrar datos del backend?",
    "¿Qué datos manejará el servidor? (usuarios, productos, respuestas, formularios…)",
    "¿Se requiere una base de datos como SQLite?",
    "¿Tu aplicación tendrá autenticación de usuarios, manejo de sesiones o control de acceso por roles?",
    "¿La interfaz será accesible para navegación por teclado y lectores de pantalla (ARIA, roles)?"
]

def _ensure_state(sess):
    if not hasattr(sess, "trainer") or not isinstance(sess.trainer, dict):
        sess.trainer = {}
    sess.trainer.setdefault("activo", False)
    sess.trainer.setdefault("paso", 0)
    sess.trainer.setdefault("historial", [])
    return sess.trainer

def _historial_to_text(historial):
    if not historial:
        return "Sin respuestas previas."
    return "\n".join(f"{i+1}. P: {qa['q']}\n   R: {qa['a']}" for i, qa in enumerate(historial))

def _groq(modelo, system, user):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GROQ_API_KEY en variables de entorno.")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": modelo,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": 4000,
        "temperature": 0.3,
        "top_p": 1.0
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def render_safe_markdownish(md_text: str) -> str:
    blocks = []
    def _block_repl(m):
        lang = (m.group(1) or "").strip()
        code = m.group(2)
        blocks.append(f'<pre><code class="lang-{html.escape(lang)}">{html.escape(code)}</code></pre>')
        return f"@@BLOCK{len(blocks)-1}@@"
    text = re.sub(r"```(\w+)?\s*\n(.*?)\n```", _block_repl, md_text, flags=re.DOTALL)
    html_match = re.search(r"<!DOCTYPE html>.*</html>", md_text, flags=re.DOTALL | re.IGNORECASE)
    if html_match:
        code = html_match.group(0)
        blocks.append(f'<pre><code class="lang-html">{html.escape(code)}</code></pre>')
        text = text.replace(code, f"@@BLOCK{len(blocks)-1}@@")
    text = html.escape(text)
    for i, block_html in enumerate(blocks):
        text = text.replace(f"@@BLOCK{i}@@", block_html)
    return text

class ApiChat:
    def POST(self):
        data = web.input()
        msg = (data.get("mensaje") or "").strip()

        global session
        state = _ensure_state(session)

        def safe_json(respuesta_raw: str):
            return json.dumps({"respuesta": render_safe_markdownish(respuesta_raw)})

        if msg.lower() == "/clear":
            state["activo"] = False
            state["paso"] = 0
            state["historial"] = []
            return json.dumps({"respuesta": "🗑️ Chat reiniciado.", "limpiar": True})

        if msg.lower() == "/help":
            return safe_json(
"""📘 Bienvenido al Prompt Trainer
Este asistente educativo te ayudará a diseñar un prompt maestro para generar una interfaz web con HTML, CSS y Flask.

Comandos disponibles:
`/quiz` — Iniciar cuestionario de 19 preguntas  
`/clear` — Borrar todo el chat y reiniciar  
`/final` — Mostrar el prompt maestro (solo si ya terminaste)"""
            )

        if msg.lower() == "/quiz":
            state["activo"] = True
            state["paso"] = 0
            state["historial"] = []
            q = TRAINER_QUESTIONS[0]
            system = (
                "Eres un asistente educativo experto en desarrollo web (Python y HTML). "
                "Para cada pregunta del cuestionario, primero da una definición extensa (~120 palabras). "
                "Incluye SIEMPRE un mini-ejemplo dentro de un bloque de código usando triple backticks "
                "con el lenguaje correcto, por ejemplo:\n"
                "```html\n<!DOCTYPE html>\n<html>\n<head>...</head>\n<body>...</body>\n</html>\n```\n"
                "No uses solo texto ni &lt; y &gt;, usa siempre este formato. "
                "Después formula la pregunta al usuario."
            )
            user = f"Pregunta: {q}"
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)
            return safe_json(respuesta_raw)

        if msg.lower() == "/final":
            if state["paso"] < len(TRAINER_QUESTIONS):
                faltan = len(TRAINER_QUESTIONS) - state["paso"]
                return safe_json(f"⚠️ Aún faltan {faltan} preguntas por responder antes de generar el prompt final.")
            hist = _historial_to_text(state["historial"])
            system = (
                "Construye un 'prompt maestro' único y completo a partir del historial Q&A. "
                "Debe ser específico, incluir todos los detalles mencionados, y estar listo para usarse en otra IA."
            )
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, f"Historial:\n{hist}")
            return safe_json(respuesta_raw)

        if not state["activo"]:
            return safe_json("⚠️ Usa `/quiz` para comenzar el cuestionario.")

        paso = state["paso"]

        if not msg.startswith("?") and not msg.endswith("?") and paso < len(TRAINER_QUESTIONS):
            state["historial"].append({"q": TRAINER_QUESTIONS[paso], "a": msg})
            paso += 1
            state["paso"] = paso

        if paso >= len(TRAINER_QUESTIONS):
            hist = _historial_to_text(state["historial"])
            system = (
                "Construye un 'prompt maestro' único y completo a partir del historial Q&A. "
                "Debe ser específico e incluir todos los detalles mencionados."
            )
            state["activo"] = False
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, f"Historial:\n{hist}")
            return safe_json(respuesta_raw)

        if msg.startswith("?") or msg.endswith("?"):
            system = "Eres un experto en desarrollo web. Responde de forma clara, concisa y didáctica."
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, msg)
            return safe_json(f"{respuesta_raw}\n\nAhora retomemos: {TRAINER_QUESTIONS[paso]}")

        q = TRAINER_QUESTIONS[paso]
        system = (
            "Eres un asistente educativo experto en desarrollo web. "
            "Primero da una definición extensa (~120 palabras). "
            "Incluye SIEMPRE un mini-ejemplo dentro de triple backticks (```html ... ```) "
            "para que pueda mostrarse formateado. "
            "Después formula la pregunta al usuario."
        )
        user = f"Pregunta: {q}"
        respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)
        return safe_json(respuesta_raw)

# ─────────────────────── Lanzador ────────────────────────
if __name__ == "__main__":
    app.run()
