import web
import sqlite3
import re
import os
import requests
import json
from dotenv import load_dotenv  

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
)
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
            return render.inicio_sesion(error="llena los campos para continuar")

        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if '@' in usuario and not re.match(correo_regex, usuario):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("SELECT password FROM usuarios WHERE usuario=? OR correo=?", (usuario, usuario))
            row = cur.fetchone()
            con.close()

            if row and row[0] == password:
                return render.info_secion()
            else:
                return render.inicio_sesion(error="usuario o contraseña incorrecta")
        except Exception as e:
            return render.inicio_sesion(error="usuario o contraseña incorrecta")

class InfoSecion:
    def GET(self):
        return render.info_secion()

class LeccionRapida:
    def GET(self):
        return render.leccion_rapida()

class PerfilUser:
    def GET(self):
        return render.perfil_user()

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
            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)



import os
import json
import requests
import web
import html  # Para escapar caracteres HTML

class ApiChat:
    def POST(self):
        data = web.input()
        mensaje_usuario = data.get("mensaje", "").strip()

        # --- Comando especial /help ---
        if mensaje_usuario.lower() == "/help":
            guia = """
🔧 Instrucciones para que tu solicitud funcione correctamente:

Escribe tu idea de proyecto web respondiendo brevemente con las siguientes áreas:

1. HTML: ¿Qué elementos deseas incluir? (ej. estructura semántica, uso de etiquetas como header, footer, main, etc.)
2. CSS: ¿Qué tipo de estilo quieres? (ej. modo oscuro, centrado, grid, responsive...)
3. JS: ¿Qué interacciones tendrá? (ej. validación, audio al hacer clic, sliders, conexión API...)
4. Backend (opcional): ¿Vas a usar Flask o Django? ¿Qué rutas necesitas? ¿Requiere login, base de datos...?)

🧠 Ejemplo de entrada correcta:

HTML: Página con formulario de contacto que tenga campos para nombre, correo y mensaje. Debe estar dentro de una sección con main.
CSS: Diseño responsivo con columnas y modo oscuro.
JS: Validación de campos vacíos antes de enviar el formulario.
Backend: Flask con ruta /contacto, almacenamiento en base de datos SQLite.
"""
            return json.dumps({"respuesta": html.escape(guia)})

        # --- Validación de mensaje vacío ---
        if not mensaje_usuario:
            return json.dumps({"respuesta": "Por favor, escribe un mensaje o escribe /help para obtener instrucciones."})

        try:
            api_key = os.getenv("GROQ_API_KEY")
            modelo  = os.getenv("GROQ_MODEL", "llama3-8b-8192")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json"
            }

            # Prompt del sistema reforzado
            prompt_sistema = (
                "Eres un generador de PROMPTS técnicos para proyectos web. Tu tarea es analizar las respuestas del usuario y producir un PROMPT perfectamente estructurado.\n\n"
                "🔴 MUY IMPORTANTE: NO debes generar código (ni HTML, ni CSS, ni JavaScript). No uses etiquetas como <div>, <audio>, etc.\n"
                "🔴 No uses encabezados como 'Título', 'Configuración Final', 'Código' ni cierres con frases como '¡Listo!'.\n"
                "🔴 RESPONDE SIEMPRE con las siguientes SEIS SECCIONES, estrictamente en este orden:\n\n"
                "1. Descripción general del proyecto web.\n"
                "2. Tecnologías seleccionadas (HTML, CSS, JS, Framework backend).\n"
                "3. Estructura semántica y etiquetas clave.\n"
                "4. Estilo visual (CSS, diseño responsivo, modo oscuro...).\n"
                "5. Interactividad esperada (validación, modales, API).\n"
                "6. Backend: framework elegido, estructura de rutas, manejo de datos, base de datos, seguridad.\n\n"
                "✅ Cada sección debe comenzar con su número y título.\n"
                "✅ Si alguna sección no aplica, escríbela igualmente y di 'No se requiere para este proyecto'.\n"
                "✅ No inventes más secciones. No salgas del formato.\n\n"
                "Ejemplo de entrada:\n"
                "HTML: Página con formulario de contacto que tenga campos para nombre, correo y mensaje. Debe estar dentro de una sección con main.\n"
                "CSS: Diseño responsivo con columnas y modo oscuro.\n"
                "JS: Validación de campos vacíos antes de enviar el formulario.\n"
                "Backend: Flask con ruta /contacto, almacenamiento en base de datos SQLite.\n\n"
                "Comienza cuando recibas la entrada del usuario."
            )

            payload = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": mensaje_usuario}
                ],
                "max_tokens": 4096,
                "temperature": 0.3,
                "top_p": 1.0,
                "stop": None
            }

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            r.raise_for_status()
            data = r.json()
            respuesta = data["choices"][0]["message"]["content"].strip()

            # Verificar si fue truncada
            finish_reason = data["choices"][0].get("finish_reason", "")
            if finish_reason == "length":
                respuesta += "\n\n⚠️ La respuesta fue truncada. Intenta dividir tu entrada o aumentar max_tokens."

            # Escape para evitar ejecución como HTML en navegador
            return json.dumps({"respuesta": html.escape(respuesta)})

        except Exception as e:
            return json.dumps({"respuesta": f"Error al procesar la solicitud: {e}"})



if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
