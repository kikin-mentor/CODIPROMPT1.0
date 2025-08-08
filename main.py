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
    '/datos','Datos',
    '/logout', 'Logout',
)
render = web.template.render('templates')
api_key = os.getenv("GROQ_API_KEY")
modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # usa este modelo por defecto si no se encuentra la variable
load_dotenv()  # Cargar variables de entorno desde .env
# Esto va al inicio del archivo principal
web.config.debug = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("sessions"))

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
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (nombre, apellidos, usuario, plantel, matricula, correo, password))
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
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (nombre, apellidos, usuario, plantel, matricula, correo, password))
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
        usuario = form.usuario.strip()
        password = form.password.strip()

        if not usuario or not password:
            return render.inicio_sesion(error="Llena los campos para continuar")

        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if '@' in usuario and not re.match(correo_regex, usuario):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            # 📌 Validar usuario en usuarios.db
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("SELECT id_usuario, usuario, password FROM usuarios WHERE usuario=? OR correo=?", (usuario, usuario))
            row = cur.fetchone()
            con.close()

            if row and row[2] == password:
                session.logged_in = True
                session.usuario_id = row[0]
                session.username = row[1]

                # 📌 Insertar registro en tiempo.db (tabla sesiones)
                try:
                    con_tiempo = sqlite3.connect("tiempo.db")
                    cur_tiempo = con_tiempo.cursor()
                    cur_tiempo.execute("INSERT INTO sesiones (id_usuario) VALUES (?)", (row[0],))
                    con_tiempo.commit()

                    # Guardar id_sesion en la sesión de Python para usarlo después
                    session.id_sesion = cur_tiempo.lastrowid
                    con_tiempo.close()
                except Exception as e:
                    print("⚠️ Error registrando sesión en tiempo.db:", e)
                # 📌 Registrar inicio en la base tiempo.db
                    try:
                        con_t = get_db_tiempo()
                        cur_t = con_t.cursor()
                        cur_t.execute("INSERT INTO sesiones (id_usuario) VALUES (?)", (session.usuario_id,))
                        con_t.commit()
                        session.id_sesion = cur_t.lastrowid
                        con_t.close()
                        print(">>> SESIÓN REGISTRADA EN tiempo.db, ID:", session.id_sesion)
                    except Exception as e:
                        print("⚠️ Error registrando sesión en tiempo.db:", e)
                        session.id_sesion = None

                return web.seeother('/info_secion')
            else:
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
            con_t = get_db_tiempo()
            cur_t = con_t.cursor()

            # 1) Marcar fin
            cur_t.execute("UPDATE sesiones SET fin = CURRENT_TIMESTAMP WHERE id_sesion = ?", (id_sesion,))

            # 2) Calcular minutos entre inicio y fin (en SQL, con julianday)
            cur_t.execute("""
                SELECT CAST(ROUND((julianday(COALESCE(fin, CURRENT_TIMESTAMP)) - julianday(inicio)) * 1440) AS INTEGER)
                FROM sesiones
                WHERE id_sesion = ?
            """, (id_sesion,))
            row = cur_t.fetchone()
            minutos = max(0, int(row[0])) if row and row[0] is not None else 0

            # 3) Insertar en tiempo_de_uso
            cur_t.execute("""
                INSERT INTO tiempo_de_uso (id_usuario, id_sesion, minutos)
                VALUES (?, ?, ?)
            """, (id_usuario, id_sesion, minutos))

            con_t.commit()
            con_t.close()
        except Exception as e:
            print("❌ Error guardando tiempo de uso:", e)

        # Cerrar sesión de la app
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
def get_db():
        con = sqlite3.connect("usuarios.db")
        con.row_factory = sqlite3.Row
        return con
def get_db_tiempo():
        con = sqlite3.connect("tiempo.db")
        con.row_factory = sqlite3.Row
        return con

class PerfilUser: 
    def GET(self):
        print("DEBUG >> session.usuario_id:", session.get('usuario_id'))
        if hasattr(session, 'usuario_id') and session.usuario_id:
            usuario_id = session.usuario_id
            con = get_db()
            cur = con.cursor()
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
            cur.execute("SELECT id_usuario FROM usuarios WHERE usuario=? AND password=?", (usuario, password))
            row = cur.fetchone()
            if not row:
                con.close()
                return render.perfil_user(usuario=form.get('nombre'), error="Usuario o contraseña incorrectos")

            id_usuario = row['id_usuario']
            cur.execute("DELETE FROM tiempo_de_uso WHERE id_usuario=?", (id_usuario,))
            cur.execute("DELETE FROM sesiones WHERE id_usuario=?", (id_usuario,))
            cur.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
            con.commit()
            con.close()
            session.kill()
            return render.index(mensaje="Cuenta eliminada correctamente")

        except Exception as e:
            return render.perfil_user(usuario=form.get('nombre'), error=f"Error al borrar la cuenta: {e}")

class Datos:
    def GET (self):
        return render.datos()

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
        usuario = form.usuario.strip()
        correo = form.correo.strip()
        antigua_pass = form.antigua_password.strip()
        nueva_pass = form.nueva_password.strip()
        repite_pass = form.repite_password.strip()

        if not usuario or not correo or not antigua_pass or not nueva_pass or not repite_pass:
            return render.cambiar_contraseña(error="Llena todos los campos")
        if nueva_pass != repite_pass:
            return render.cambiar_contraseña(error="Las contraseñas no coinciden")

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
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

class actividad1:
    def GET(self):
        return render.actividad1(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad1(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
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
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)
        
class actividad2:
    def GET(self):
        return render.actividad2(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad2(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Escribe una noticia falsa (puede ser humorística, educativa o creativa). "
    "Usa <h1> para el título de la noticia, <h2> para subtítulo o resumen, "
    "<h3> para dividir secciones como 'Introducción', 'Desarrollo' y 'Conclusión'. "
    "Utiliza <p> en cada sección y dentro de los párrafos incluye <strong> para advertencias, "
    "<em> para opiniones o sentimientos, y <mark> para resaltar fechas o cifras."
)
        if not api_key1:
            return render.actividad2(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad2(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad2(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad3:
    def GET(self):
        return render.actividad3(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad3(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
        criterio = (
            "Inserta una imagen (foto personal o avatar) usando <img> con los atributos alt, width y height. "
            "Agrega un párrafo de bienvenida. Crea tres enlaces con <a>: "
            "uno a un sitio externo, uno a una red social en una nueva pestaña (target=\"_blank\"), "
            "y uno que lleve a otra sección de la misma página usando un id y href=\"#...\"."
        )
        if not api_key1:
            return render.actividad3(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad3(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad3(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad4:
    def GET(self):
        return render.actividad4(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad4(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Crea una lista desordenada (<ul>) con 4 cosas que usarías para acampar. "
    "Agrega una lista ordenada (<ol>) con pasos para preparar tu platillo favorito. "
    "Incluye una lista anidada con dos categorías principales: 'Tecnología' y 'Arte', "
    "y debajo de cada una agrega subelementos."
)

        if not api_key1:
            return render.actividad4(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad4(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad4(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad5:
    def GET(self):
        return render.actividad5(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad5(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Diseña una tabla con los encabezados: Producto, Precio, Cantidad. "
    "Agrega 3 filas con diferentes productos. Usa <tfoot> para incluir una fila final con el total. "
    "Utiliza border=\"1\" y aplica colspan o rowspan si deseas fusionar celdas."
)     
        if not api_key1:
            return render.actividad5(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad5(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad5(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad6:
    def GET(self):
        return render.actividad6(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad6(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Incluye un formulario <form> con: "
    "campo de texto para nombre completo (obligatorio, maxlength=\"40\"), "
    "campo de correo electrónico (type=\"email\"), "
    "campo de contraseña (type=\"password\", mínimo 6 caracteres), "
    "comentarios con <textarea> y placeholder, y botón de envío. "
    "Usa <label> para cada campo y enlázalo con su id."
)
        if not api_key1:
            return render.actividad6(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad6(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad6(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad7:
    def GET(self):
        return render.actividad7(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad7(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Dentro del <head>, agrega un bloque <style>. "
    "Estiliza el fondo del body con un color claro, los títulos (h1, h2) con color azul y alineación centrada, "
    "los párrafos con una fuente diferente y un tamaño de fuente mayor. "
    "Aplica márgenes y padding para dar espacio entre los elementos."
)

        if not api_key1:
            return render.actividad7(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad7(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad7(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad8:
    def GET(self):
        return render.actividad8(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad8(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Escribe una página con: un <header> con el título del sitio, "
    "una <nav> con una lista de navegación, un <main> con una <section> llamada 'Noticias' y dos <article>. "
    "Cada <article> debe tener un título y un párrafo. "
    "Agrega un <footer> con tu nombre y el año actual."
)
        if not api_key1:
            return render.actividad8(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad8(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad8(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad9:
    def GET(self):
        return render.actividad9(resultado=None, codigo_enviado="")

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.actividad9(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")

        # Cargar API Key y modelo desde .env
        api_key1 = "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"
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = (
    "Inserta un reproductor de audio usando <audio> con el archivo musica.mp3. "
    "Agrega un reproductor de video <video> con dimensiones personalizadas. "
    "Incluye un iframe con un video de YouTube (usa el código de inserción). "
    "Escribe un texto explicativo con <p> antes de cada elemento multimedia."
)
        if not api_key1:
            return render.actividad9(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: " + criterio +" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key1}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.actividad9(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad9(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)
start_activate = False

# ───────────── Estado global mínimo ─────────────
start_activate = False  # bandera simple de arranque
TRAINER_QUESTIONS = [
    # HTML – Estructura, Semántica y Contenido
    "¿Tu documento comienza con &lt;<!DOCTYPE html>&gt; y contiene &lt;<html>&gt;, <head> y <body> correctamente estructurados?",
    "¿Declaraste el idioma del sitio con <html lang=\"es\">?",
    "¿Utilizarás etiquetas semánticas como <header>, <footer>, <section>, <article> para mejorar accesibilidad y SEO?",
    "¿El <head> incluye <title>, <meta charset=\"UTF-8\">, y <meta name=\"viewport\"> para diseño responsive?",
    "¿Necesitas favicon, keywords o descripción (<meta name=\"description\">)?",
    "¿Usarás encabezados <h1> a <h6> y contenido textual con <p>, <strong>, <em>?",
    "¿Insertarás imágenes con <img src=\"...\" alt=\"...\"> o contenido multimedia como audio/video con etiquetas HTML5?",
    "¿Tendrás navegación con <nav> y enlaces <a href=\"...\"> internos/externos (target=\"_blank\")?",
    "¿Mostrarás listas <ul>/<ol> o tablas <table> para estructurar datos?",
    # CSS – Diseño y Responsividad
    "¿Vas a enlazar un archivo CSS externo (<link rel=\"stylesheet\">) o escribir estilos inline?",
    "¿Usarás layout con Flexbox, Grid o columnas flotantes?",
    "¿Tu sitio será responsive? ¿Incluirás media queries para adaptarlo a distintos dispositivos?",
    "¿Implementarás modo oscuro o selector de temas con clases o lógica JS?",
    # Python + Flask – Backend y Templates
    "¿Usarás Flask para definir rutas como /inicio, /usuarios, /productos?",
    "¿Los templates HTML tendrán variables Jinja2 como {{ nombre }} para mostrar datos del backend?",
    "¿Qué datos manejará el servidor? (usuarios, productos, respuestas, formularios…)",
    "¿Se requiere una base de datos como SQLite?",
    "¿Tu aplicación tendrá autenticación de usuarios, manejo de sesiones o control de acceso por roles?",
    # Accesibilidad
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

class ApiChat:
    def POST(self):
        data = web.input()
        msg = (data.get("mensaje") or "").strip()

        global session
        state = _ensure_state(session)
        
        # ───── Comando CLEAR ─────
        if msg.lower() == "/clear":
            state["activo"] = False
            state["paso"] = 0
            state["historial"] = []
            return json.dumps({
                "respuesta": "🗑️ Chat reiniciado.",
                "limpiar": True
            })


        # ───── Comando help ─────
        if msg.lower() == "/help":
            return json.dumps({"respuesta": """
<h3>📘 Bienvenido al Prompt Trainer</h3>
<p>Este asistente educativo te ayudará a diseñar un prompt maestro para generar una interfaz web con HTML, CSS y Flask.</p>
<p>Comandos disponibles:</p>
<ul>
<li><code>/quiz</code> — Iniciar cuestionario de 19 preguntas</li>
<li><code>/clear</code> — Borrar todo el chat y reiniciar</li>
<li><code>/final</code> — Mostrar el prompt maestro (solo si ya terminaste)</li>
</ul>
"""})

        # ───── Comando QUIZ ─────
        if msg.lower() == "/quiz":
            state["activo"] = True
            state["paso"] = 0
            state["historial"] = []
            q = TRAINER_QUESTIONS[0]
            system = (
                "Eres un asistente educativo experto en desarrollo web. "
                "Para cada pregunta del cuestionario, primero da una definición extensa (~120 palabras) "
                "explicando el concepto: qué es, para qué sirve, por qué es importante, y un mini-ejemplo de código si aplica. "
                "Si das un ejemplo de código, encierra cada línea entre &lt; y &gt; para evitar que se renderice como HTML en el navegador. "
                "Después formula la pregunta al usuario."
            )
            user = f"Pregunta: {q}"
            return json.dumps({"respuesta": _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)})

        # ───── Comando FINAL ─────
        if msg.lower() == "/final":
            if state["paso"] < len(TRAINER_QUESTIONS):
                faltan = len(TRAINER_QUESTIONS) - state["paso"]
                return json.dumps({"respuesta": f"⚠️ Aún faltan {faltan} preguntas por responder antes de generar el prompt final."})
            hist = _historial_to_text(state["historial"])
            system = (
                "Construye un 'prompt maestro' único y completo a partir del historial Q&A. "
                "Debe ser específico, incluir todos los detalles mencionados, y estar listo para usarse en otra IA para generar la interfaz web."
            )
            return json.dumps({"respuesta": _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, f"Historial:\n{hist}")})

        # ───── Si no está en modo quiz ─────
        if not state["activo"]:
            return json.dumps({"respuesta": "⚠️ Usa <code>/quiz</code> para comenzar el cuestionario."})

        # ───── Respuesta dentro del quiz ─────
        paso = state["paso"]

        # Guardar respuesta del usuario si es a la pregunta actual
        if not msg.startswith("?") and not msg.endswith("?") and paso < len(TRAINER_QUESTIONS):
            state["historial"].append({"q": TRAINER_QUESTIONS[paso], "a": msg})
            paso += 1
            state["paso"] = paso

        # Si ya terminó → generar prompt final
        if paso >= len(TRAINER_QUESTIONS):
            hist = _historial_to_text(state["historial"])
            system = (
                "Construye un 'prompt maestro' único y completo a partir del historial Q&A. "
                "Debe ser específico, incluir todos los detalles mencionados, y estar listo para usarse en otra IA para generar la interfaz web."
            )
            state["activo"] = False
            return json.dumps({"respuesta": _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, f"Historial:\n{hist}")})

        # Si es una pregunta libre → responder y repetir pregunta actual
        if msg.startswith("?") or msg.endswith("?"):
            system = "Eres un experto en desarrollo web. Responde de forma clara, concisa y didáctica."
            respuesta = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, msg)
            return json.dumps({"respuesta": f"{respuesta}<br><br>Ahora retomemos: {TRAINER_QUESTIONS[paso]}"})

        # Enviar siguiente pregunta
        q = TRAINER_QUESTIONS[paso]
        system = (
            "Eres un asistente educativo experto en desarrollo web. "
            "Para cada pregunta, primero da una definición extensa (~120 palabras) "
            "explicando el concepto: qué es, para qué sirve, por qué es importante, y un mini-ejemplo de código si aplica. "
            "Después formula la pregunta al usuario."
        )
        user = f"Pregunta: {q}"
        return json.dumps({"respuesta": _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)})

# ─────────────────────── Lanzador de la aplicación ────────────────────────
if __name__ == "__main__":
    app.run()