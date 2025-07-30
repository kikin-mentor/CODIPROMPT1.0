import web
import sqlite3
import re
import os
import requests
import json
from dotenv import load_dotenv  
import html
import time
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import plotly.graph_objs as go
import plotly.io as pio
import os


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
    '/perfil_estadisticas', 'PerfilEstadisticas',
)
def get_db():
    # Retorna conexión con row_factory para dict
    con = sqlite3.connect("tiempo.db")
    con.row_factory = sqlite3.Row
    return con

class PerfilEstadisticas:
    """
    Ruta para mostrar las estadísticas del usuario (tiempo de uso, gráficas, etc).
    """
    def GET(self):
        id_usuario = None
        if hasattr(user_session, 'id_usuario') and user_session.id_usuario:
            id_usuario = user_session.id_usuario
        dias = []
        minutos = []
        lecciones_realizadas = 0
        prompts_correctos = 0
        if id_usuario:
            conn = get_db()
            cur = conn.cursor()
            # Calcular minutos de sesión actual y actualizar tiempo_de_uso
            try:
                inicio = getattr(user_session, 'inicio', None)
                if inicio:
                    minutos_sesion = int((time.time() - inicio) // 60)
                    fecha = time.strftime('%Y-%m-%d')
                    cur.execute('UPDATE tiempo_de_uso SET minutos = minutos + ? WHERE id_usuario=? AND fecha=?', (minutos_sesion, id_usuario, fecha))
                    conn.commit()
                    user_session.inicio = int(time.time())
            except Exception:
                pass
            # Tiempo de uso por día
            cur.execute('SELECT fecha, SUM(minutos) as total_minutos FROM tiempo_de_uso WHERE id_usuario=? GROUP BY fecha', (id_usuario,))
            tiempo_data = cur.fetchall()
            import datetime
            dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            fechas = [row['fecha'] for row in tiempo_data]
            dias = [dias_semana[datetime.datetime.strptime(f, '%Y-%m-%d').weekday()] for f in fechas]
            minutos = [row['total_minutos'] for row in tiempo_data]
            # Lecciones realizadas
            cur.execute('SELECT COUNT(*) FROM lecciones_completadas WHERE id_usuario=?', (id_usuario,))
            lecciones_realizadas = cur.fetchone()[0] or 0
            # Prompts correctos (tabla prompt, campo correcto)
            cur.execute('SELECT COUNT(*) FROM prompt WHERE id_usuario=? AND correcto=1', (id_usuario,))
            prompts_correctos = cur.fetchone()[0] or 0
            conn.close()
        # Gráfica de barras
        bar = go.Figure([go.Bar(x=dias, y=minutos, name='Minutos de uso')])
        bar.update_layout(title='Tiempo de uso por día', xaxis_title='Día de la semana', yaxis_title='Minutos')
        # Gráfica de pastel
        pie = go.Figure(data=[go.Pie(labels=['Lecciones', 'Prompts correctos'], values=[lecciones_realizadas, prompts_correctos])])
        pie.update_layout(title='Lecciones vs Prompts correctos')
        # Gráfica de dispersión
        scatter = go.Figure()
        scatter.add_trace(go.Scatter(x=[lecciones_realizadas], y=[minutos[-1] if minutos else 0], mode='markers', name='Lecciones'))
        scatter.add_trace(go.Scatter(x=[prompts_correctos], y=[minutos[-1] if minutos else 0], mode='markers', name='Prompts'))
        scatter.update_layout(title='Comparativa: Tiempo vs Lecciones/Prompts', xaxis_title='Lecciones/Prompts', yaxis_title='Minutos')
        # Renderizar la plantilla
        bar_html = pio.to_html(bar, full_html=False)
        pie_html = pio.to_html(pie, full_html=False)
        scatter_html = pio.to_html(scatter, full_html=False)
        return render.perfil_estadisticas(bar_html, pie_html, scatter_html)
render = web.template.render('templates')
api_key = os.getenv("GROQ_API_KEY")
modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # usa este modelo por defecto si no se encuentra la variable
load_dotenv()  # Cargar variables de entorno desde .env


class Index:
    def GET(self):
        return render.index()

class Registro:
    def GET(self):
        return render.registro()

    def POST(self):
        import re
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
            return render.registro(error="Llena los campos para continuar")

        # Validar correo electrónico
        correo = form.get('correo', '').strip()
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if not re.match(correo_regex, correo):
            return render.registro(error="Ingresa un correo válido")

        # Validar que las contraseñas coincidan
        password = form.get('password', '').strip()
        confirmar = form.get('confirmar', '').strip()
        if password != confirmar:
            return render.registro(error="Las contraseñas no coinciden")

        nombre = form.get('nombre', '').strip()
        apellidos = form.get('apellidos', '').strip()
        usuario = form.get('usuario', '').strip()
        plantel = form.get('plantel', '').strip()
        matricula = form.get('matricula', '').strip()

        # Debug: verificar la ruta real a la base de datos
        print("[DEBUG] Ruta actual:", os.getcwd())
        print("[DEBUG] Ruta DB absoluta:", os.path.abspath("usuarios.db"))

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            print("[DEBUG] Conexión a DB abierta")

            cur.execute("""
                INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (nombre, apellidos, usuario, plantel, matricula, correo, password)
            )
            con.commit()
            print("[DEBUG] Registro insertado correctamente")
            con.close()
            print("[DEBUG] Conexión cerrada")

            print("[DEBUG] Redirigiendo a /inicio_sesion")
            return web.seeother("/inicio_sesion")

        except sqlite3.IntegrityError as e:
            print(f"[DEBUG] Error de integridad en registro: {e}")
            if 'usuario' in str(e):
                return render.registro(error="El nombre de usuario ya existe")
            if 'correo' in str(e):
                return render.registro(error="El correo ya está registrado")
            if 'matricula' in str(e):
                return render.registro(error="La matrícula ya está registrada")
            return render.registro(error=f"Error de integridad: {e}")

        except Exception as e:
            print(f"[DEBUG] Error general en registro: {e}")
            return render.registro(error=f"Error al registrar: {e}")

class InicioSesion:
    def GET(self):
        return render.inicio_sesion(error=None)

    def POST(self):
        form = web.input()
        correo = form.get('correo', '').strip()
        password = form.get('password', '').strip()

        if not correo or not password:
            return render.inicio_sesion(error="Llena los campos para continuar")

        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if not re.match(correo_regex, correo):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("SELECT password FROM usuarios WHERE correo=?", (correo,))
            row = cur.fetchone()
            con.close()

            if row and row[0] == password:
                return render.info_secion()
            else:
                return render.inicio_sesion(error="Correo o contraseña incorrecta")
        except Exception as e:
            return render.inicio_sesion(error="Correo o contraseña incorrecta")

class InfoSecion:
    def GET(self):
        return render.info_secion()

class LeccionRapida:
    def GET(self):
        return render.leccion_rapida()

class PerfilUser:
    def GET(self):
        correo = None
        try:
            correo = user_session.usuario
        except Exception:
            pass
        nombre = None
        estado = None
        mensaje = None
        if correo:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("SELECT nombre, estado FROM usuarios WHERE correo=?", (correo,))
            row = cur.fetchone()
            con.close()
            if row:
                nombre = row[0]
                estado = row[1] if len(row) > 1 else ""
        return render.perfil_user(nombre=nombre, estado=estado, mensaje=mensaje)

    def POST(self):
        correo = None
        try:
            correo = user_session.usuario
        except Exception:
            pass
        form = web.input()
        nuevo_nombre = form.get('nuevo_nombre', '').strip()
        nuevo_estado = form.get('nuevo_estado', '').strip()
        borrar_usuario = form.get('borrar_usuario', '').strip()
        password = form.get('password', '').strip()
        mensaje = None
        # Si se solicita borrar la cuenta
        if borrar_usuario and password and correo:
            try:
                con = sqlite3.connect("usuarios.db")
                cur = con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=? AND password=?", (correo, password))
                row = cur.fetchone()
                if not row:
                    con.close()
                    return render.perfil_user(error="Correo o contraseña incorrectos")
                id_usuario = row[0]
                cur.execute("DELETE FROM tiempo_de_uso WHERE id_usuario=?", (id_usuario,))
                cur.execute("DELETE FROM sesiones WHERE id_usuario=?", (id_usuario,))
                cur.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
                con.commit()
                con.close()
                return render.index(mensaje="Cuenta eliminada correctamente")
            except Exception as e:
                return render.perfil_user(error=f"Error al borrar la cuenta: {e}")
        # Si se solicita actualizar nombre o estado
        if correo and (nuevo_nombre or nuevo_estado):
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            if nuevo_nombre:
                cur.execute("UPDATE usuarios SET nombre=? WHERE correo=?", (nuevo_nombre, correo))
            if nuevo_estado:
                cur.execute("UPDATE usuarios SET estado=? WHERE correo=?", (nuevo_estado, correo))
            con.commit()
            cur.execute("SELECT nombre, estado FROM usuarios WHERE correo=?", (correo,))
            row = cur.fetchone()
            con.close()
            mensaje = "Datos actualizados correctamente."
            nombre = row[0] if row else None
            estado = row[1] if row and len(row) > 1 else ""
            return render.perfil_user(nombre=nombre, estado=estado, mensaje=mensaje)
        # Si no hay cambios, solo muestra la info
        nombre = None
        estado = None
        if correo:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("SELECT nombre, estado FROM usuarios WHERE correo=?", (correo,))
            row = cur.fetchone()
            con.close()
            if row:
                nombre = row[0]
                estado = row[1] if len(row) > 1 else ""
        return render.perfil_user(nombre=nombre, estado=estado, mensaje=mensaje)

def obtener_info_leccion(id_leccion):
    usuario = None
    id_usuario = None
    try:
        usuario = user_session.usuario
        id_usuario = user_session.id_usuario
    except Exception:
        pass
    con = sqlite3.connect("lecciones.db")
    cur = con.cursor()
    cur.execute("SELECT contenido FROM lecciones WHERE id_leccion=?", (id_leccion,))
    row = cur.fetchone()
    contenido = row[0] if row else ""
    con.close()
    tiempo_total = 0
    completada = False
    if id_usuario:
        con2 = sqlite3.connect("tiempo.db")
        cur2 = con2.cursor()
        cur2.execute("SELECT SUM(tiempo) FROM tiempo_leccion WHERE id_usuario=? AND id_leccion=?", (id_usuario, id_leccion))
        row = cur2.fetchone()
        tiempo_total = row[0] if row and row[0] else 0
        cur2.execute("SELECT 1 FROM lecciones_completadas WHERE id_usuario=? AND id_leccion=?", (id_usuario, id_leccion))
        completada = bool(cur2.fetchone())
        con2.close()
    return contenido, tiempo_total, completada

class Leccion1:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(1)
        return render.leccion1(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion2:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(2)
        return render.leccion2(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion3:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(3)
        return render.leccion3(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion4:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(4)
        return render.leccion4(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion5:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(5)
        return render.leccion5(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion6:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(6)
        return render.leccion6(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion7:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(7)
        return render.leccion7(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion8:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(8)
        return render.leccion8(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class Leccion9:
    def GET(self):
        contenido, tiempo_total, completada = obtener_info_leccion(9)
        return render.leccion9(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

class LeccionPersonalizada:
    def GET(self):
        # Página estática, sin lógica dinámica ni consulta a la base de datos
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 1, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)
        
class actividad2:
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
    "Escribe una noticia falsa (puede ser humorística, educativa o creativa). "
    "Usa <h1> para el título de la noticia, <h2> para subtítulo o resumen, "
    "<h3> para dividir secciones como 'Introducción', 'Desarrollo' y 'Conclusión'. "
    "Utiliza <p> en cada sección y dentro de los párrafos incluye <strong> para advertencias, "
    "<em> para opiniones o sentimientos, y <mark> para resaltar fechas o cifras."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 2, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad3:
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
            "Inserta una imagen (foto personal o avatar) usando <img> con los atributos alt, width y height. "
            "Agrega un párrafo de bienvenida. Crea tres enlaces con <a>: "
            "uno a un sitio externo, uno a una red social en una nueva pestaña (target=\"_blank\"), "
            "y uno que lleve a otra sección de la misma página usando un id y href=\"#...\"."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 3, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad4:
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
    "Crea una lista desordenada (<ul>) con 4 cosas que usarías para acampar. "
    "Agrega una lista ordenada (<ol>) con pasos para preparar tu platillo favorito. "
    "Incluye una lista anidada con dos categorías principales: 'Tecnología' y 'Arte', "
    "y debajo de cada una agrega subelementos."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 4, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad5:
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
    "Diseña una tabla con los encabezados: Producto, Precio, Cantidad. "
    "Agrega 3 filas con diferentes productos. Usa <tfoot> para incluir una fila final con el total. "
    "Utiliza border=\"1\" y aplica colspan o rowspan si deseas fusionar celdas."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 5, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad6:
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
    "Incluye un formulario <form> con: "
    "campo de texto para nombre completo (obligatorio, maxlength=\"40\"), "
    "campo de correo electrónico (type=\"email\"), "
    "campo de contraseña (type=\"password\", mínimo 6 caracteres), "
    "comentarios con <textarea> y placeholder, y botón de envío. "
    "Usa <label> para cada campo y enlázalo con su id."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 6, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad7:
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
    "Dentro del <head>, agrega un bloque <style>. "
    "Estiliza el fondo del body con un color claro, los títulos (h1, h2) con color azul y alineación centrada, "
    "los párrafos con una fuente diferente y un tamaño de fuente mayor. "
    "Aplica márgenes y padding para dar espacio entre los elementos."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 7, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad8:
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
    "Escribe una página con: un <header> con el título del sitio, "
    "una <nav> con una lista de navegación, un <main> con una <section> llamada 'Noticias' y dos <article>. "
    "Cada <article> debe tener un título y un párrafo. "
    "Agrega un <footer> con tu nombre y el año actual."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 8, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad9:
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
    "Inserta un reproductor de audio usando <audio> con el archivo musica.mp3. "
    "Agrega un reproductor de video <video> con dimensiones personalizadas. "
    "Incluye un iframe con un video de YouTube (usa el código de inserción). "
    "Escribe un texto explicativo con <p> antes de cada elemento multimedia."
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
            # Guardar resultado y código en la base de datos actividades.db
            try:
                usuario = None
                id_usuario = None
                try:
                    usuario = user_session.usuario
                    id_usuario = user_session.id_usuario
                except Exception:
                    pass
                con = sqlite3.connect("lecciones.db")
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
                cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, 9, codigo, feedback))
                con.commit()
                con.close()
            except Exception:
                pass
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)


class ApiChat:
    def POST(self):
        data = web.input()
        mensaje_usuario = data.get("mensaje", "").strip()

        if not mensaje_usuario:
            return json.dumps({"respuesta": "Por favor, escribe un mensaje o usa /start para comenzar."})

        # ───────────────────────────── /help ─────────────────────────────
        if mensaje_usuario.lower() == "/help":
            guia = """
📘 Bienvenido al Prompt Trainer de interfaces web

Este asistente te ayuda a redactar prompts efectivos para generar interfaces completas (HTML + CSS + JS).

🧠 ¿Cómo funciona?
1. Escribe /start para ver un ejemplo.
2. Escribe un prompt claro describiendo la interfaz.
3. Recibirás una evaluación (1–10) y el código generado.

✅ Ejemplo de prompt efectivo:
"Una página con encabezado oscuro que diga 'Mi Tienda', un botón azul al centro
que al hacer clic muestre una alerta JS."
"""
            # Aquí SÍ escapamos porque incluye < > que no queremos interpretar
            return json.dumps({"respuesta": html.escape(guia)})

        # ───────────────────────────── /start ────────────────────────────
        if mensaje_usuario.lower() == "/start":
            ejemplo_html = """
<!DOCTYPE html>
<html lang='es'>
<head>
  <meta charset='UTF-8'>
  <style>
    body{background:#f0f0f0;font-family:sans-serif;margin:0;padding:20px;text-align:center}
    header{background:#333;color:#fff;padding:10px;font-size:20px}
    main{margin-top:20px}
    button{padding:10px 20px;background:#007bff;color:#fff;border:none;border-radius:5px}
  </style>
</head>
<body>
  <header>Mi Sitio Web</header>
  <main>
    <p>Bienvenido a mi página</p>
    <button>Haz clic aquí</button>
  </main>
</body>
</html>
"""
            instrucciones = (
                "🎯 <strong>Reto Prompt Trainer</strong><br>"
                "Redacta un prompt que permita generar una interfaz como esta. "
                "Luego recibirás una calificación (1–10) y el código correspondiente.<br><br>"
            )

            iframe = (
                f'<iframe sandbox="allow-scripts allow-same-origin" '
                f'style="width:100%;max-width:800px;height:400px;'
                f'border:1px solid #ccc;border-radius:10px;" '
                f'srcdoc="{(ejemplo_html)}"></iframe>'
            )

            # NO escapamos todo el bloque porque queremos que el iframe se renderice
            return json.dumps({"respuesta": instrucciones + iframe})

        # ─────────────── Evaluación del prompt + generación de código ───────────────
        try:
            api_key = os.getenv("GROQ_API_KEY")
            modelo  = os.getenv("GROQ_MODEL", "llama3-8b-8192")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            prompt_sistema = (
                "Eres un experto en prompt engineering aplicado al desarrollo web. "
                "Primero evalúa el prompt del usuario con base en claridad, precisión y estructura. "
                "Otorga una calificación del 1 al 10 y explica brevemente por qué.\n\n"
                "Después genera un documento HTML5 completo que cumpla la solicitud.\n\n"
                "✅ Formato EXACTO:\n"
                "1. 📝 Evaluación del prompt:\n"
                "Puntaje: X/10\n"
                "Comentario: ...\n\n"
                "2. 🧾 Código generado:\n"
                "(bloque completo desde <!DOCTYPE html> hasta </html>)"
                "3. recomendaciones:\n"
            )

            payload = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user",   "content": mensaje_usuario}
                ],
                "max_tokens": 4096,
                "temperature": 0.4,
                "top_p": 1.0
            }

            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            respuesta = data["choices"][0]["message"]["content"].strip()

            if data["choices"][0].get("finish_reason") == "length":
                respuesta += (
                    "\n\n⚠️ La respuesta fue truncada. Intenta dividir tu prompt "
                    "o aumentar max_tokens."
                )

            # Escapamos porque puede contener <html> y luego el frontend lo pintará en iframe
            return json.dumps({"respuesta": html.escape(respuesta)})

        except Exception as e:
            return json.dumps({"respuesta": f"Error al procesar la solicitud: {e}"})


# ─────────────────────── Lanzador de la aplicación ────────────────────────
if __name__ == "__main__":
    app = web.application(urls, globals())
    store = web.session.DiskStore('sessions')
    user_session = web.session.Session(app, store, initializer={'usuario': None, 'id_usuario': None, 'inicio': None})
    # Usar el middleware Session para que web.ctx.session esté disponible en cada petición
    app.add_processor(user_session._processor)
    app.run()