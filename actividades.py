###############################################################
# actividades.py
# Vistas y lógica para las actividades de CODIPROMPT.
# Cada clase representa una actividad y su evaluación.
# Me dijjo copilot que siempre va al inicio la cabecera de licencia
# y los imports necesarios.
###############################################################
import os
import sqlite3
import requests
from web import template, seeother

from utils import get_api_config

render = template.render('templates')

# Criterios por número de actividad
CRITERIOS = {
    1: "Crea un archivo nuevo con la estructura básica de un documento HTML5. Incluye en el <body> un título que diga “Hola, mundo” y un párrafo donde te presentes (nombre, edad, afición). El documento comienza con <!DOCTYPE html>. Se utiliza <html lang=\"es\">. Dentro de <head> aparecen las meta etiquetas correctas y el título. Dentro del <body> hay un encabezado <h1> y un <p> con presentación.",
    2: "Escribe una noticia falsa (puede ser humorística, educativa o creativa). Usa <h1> para el título de la noticia, <h2> para subtítulo o resumen, <h3> para dividir secciones como 'Introducción', 'Desarrollo' y 'Conclusión'. Utiliza <p> en cada sección y dentro de los párrafos incluye <strong> para advertencias, <em> para opiniones o sentimientos, y <mark> para resaltar fechas o cifras.",
    3: "Inserta una imagen (foto personal o avatar) usando <img> con los atributos alt, width y height. Agrega un párrafo de bienvenida. Crea tres enlaces con <a>: uno a un sitio externo, uno a una red social en una nueva pestaña (target=\"_blank\"), y uno que lleve a otra sección de la misma página usando un id y href=\"#...\".",
    4: "Crea una lista desordenada (<ul>) con 4 cosas que usarías para acampar. Agrega una lista ordenada (<ol>) con pasos para preparar tu platillo favorito. Incluye una lista anidada con dos categorías principales: 'Tecnología' y 'Arte', y debajo de cada una agrega subelementos.",
    5: "Diseña una tabla con los encabezados: Producto, Precio, Cantidad. Agrega 3 filas con diferentes productos. Usa <tfoot> para incluir una fila final con el total. Utiliza border=\"1\" y aplica colspan o rowspan si deseas fusionar celdas.",
    6: "Incluye un formulario <form> con: campo de texto para nombre completo (obligatorio, maxlength=\"40\"), campo de correo electrónico (type=\"email\"), campo de contraseña (type=\"password\", mínimo 6 caracteres), comentarios con <textarea> y placeholder, y botón de envío. Usa <label> para cada campo y enlázalo con su id.",
    7: "Dentro del <head>, agrega un bloque <style>. Estiliza el fondo del body con un color claro, los títulos (h1, h2) con color azul y alineación centrada, los párrafos con una fuente diferente y un tamaño de fuente mayor. Aplica márgenes y padding para dar espacio entre los elementos.",
    8: "Escribe una página con: un <header> con el título del sitio, una <nav> con una lista de navegación, un <main> con una <section> llamada 'Noticias' y dos <article>. Cada <article> debe tener un título y un párrafo. Agrega un <footer> con tu nombre y el año actual.",
    9: "Inserta un reproductor de audio usando <audio> con el archivo musica.mp3. Agrega un reproductor de video <video> con dimensiones personalizadas. Incluye un iframe con un video de YouTube (usa el código de inserción). Escribe un texto explicativo con <p> antes de cada elemento multimedia."
}

def procesar_actividad(num_actividad, codigo, user_session=None):
    api_key, modelo = get_api_config()
    criterio = CRITERIOS.get(num_actividad, "")
    if not api_key:
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
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
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
            if user_session:
                usuario = getattr(user_session, 'usuario', None)
                id_usuario = getattr(user_session, 'id_usuario', None)
            con = sqlite3.connect("lecciones.db")
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS actividades (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, actividad INTEGER, codigo TEXT, resultado TEXT, fecha TEXT)")
            cur.execute("INSERT INTO actividades (id_usuario, actividad, codigo, resultado, fecha) VALUES (?, ?, ?, ?, date('now'))", (id_usuario, num_actividad, codigo, feedback))
            con.commit()
            con.close()
        except Exception:
            pass
        return render.actividad1(resultado=feedback, codigo_enviado=codigo)
    except Exception as e:
        return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

# Clase genérica para actividades
class ActividadGenerica:
    def __init__(self, num_actividad):
        self.num_actividad = num_actividad
    def GET(self):
        if not getattr(user_session, 'id_usuario', None):
            return seeother('/inicio_sesion')
        return render.actividad1(resultado=None, codigo_enviado="")
    def POST(self):
        form = __import__('web').input(codigo_html="")
        codigo = form.codigo_html.strip()
        if not codigo:
            return render.actividad1(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        return procesar_actividad(self.num_actividad, codigo, user_session)

# Instancias para cada actividad
actividad1 = ActividadGenerica(1)
actividad2 = ActividadGenerica(2)
actividad3 = ActividadGenerica(3)
actividad4 = ActividadGenerica(4)
actividad5 = ActividadGenerica(5)
actividad6 = ActividadGenerica(6)
actividad7 = ActividadGenerica(7)
actividad8 = ActividadGenerica(8)
actividad9 = ActividadGenerica(9)