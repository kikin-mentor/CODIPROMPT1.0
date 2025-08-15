import web #ayuda a la carga de web.py
import sqlite3 #ayuda a la conexionn con base de datos 
import re #ayuda a validar un texto regular para python
import os #ayuda a interactuar con el sistema operativo
import requests #facilita el CRUD en solicitudes HTTP
import json #contenedor para almacenar datos 
from dotenv import load_dotenv #carga variables del .env
import html
import datetime #obtiene la fecha y hora actual 
import plotly.graph_objs as go #es la que ayuda a crear las graficas y figuras para esta
import plotly.io as pio #ayuda a que se vean en el html las graficas 
import smtplib 
import ssl
import random
from email.mime.text import MIMEText
import bcrypt # encripta las contraseñas en hash  

# Cargar variables de entorno
load_dotenv()

# ----- SMTP / Email -----
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

# Modelos para la IA
api_key = os.getenv("GROQ_API_KEY") #lee el .env
#igual ayuda a autenticar los solicitudes a groq

modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192") #llama las varibles del modelo
#si no existe esa variable usa llama por defecto

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
    '/estadisticas', 'Estadisticas',
    '/admin','Admin',
    '/usuario/(\\d+)', 'UsuarioDetalle',
    '/enviar_codigo', 'EnviarCodigo',       # <<< NUEVO: endpoint para mandar código por correo
)

render = web.template.render('templates') #renderiza las plantillas y las manda a templates 
#este modulo nos deja hacer los render de cada pagina

# Base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "codiprompt.db")  #hace una ruta absoluta a
#la base de datos para el script __file__ esto nos ayuda a siempre ejecutar el
#archivo correcto

web.config.debug = False 

app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore("sessions")) #configura el sistema de sesiones 
# Diskstore (sesiones) guarda las sesiones en la carpeta sessions para mayor control


#para hashear: 
def hash_password(password: str) -> str:
    """Devuelve un hash bcrypt (con salt incluido)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _is_bcrypt_hash(value: str | None) -> bool:
    """Detecta si lo guardado ya es un hash bcrypt ($2a/$2b/$2y)."""
    return isinstance(value, str) and value.startswith(("$2a$", "$2b$", "$2y$"))

def verify_password(plain: str, stored: str | None) -> bool:
    """
    Verifica la contraseña.
    - Si 'stored' es bcrypt: checkpw.
    - Si 'stored' es texto plano (legacy): compara directo (compatibilidad).
    """
    if not stored:
        return False
    if _is_bcrypt_hash(stored):
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            return False
    # Compatibilidad con cuentas antiguas (texto plano)
    return plain == stored


# Ayuda a la base de datos
def get_db(): #los def son funciones reutilizables que se utilizan para en este caso abrir conexión a la base de datos
    con = sqlite3.connect(DB_PATH) #conecta con la base de datos 
    con.row_factory = sqlite3.Row #permite acceder a columnas por nombre
    return con #retorna la conexion 

def obtener_id_tiempo(id_usuario): # Obtiene el último tiempo_de_uso registrado del usuario
    con = get_db() #coneccion con base
    cur = con.cursor() #crea el cursor para hacer consultas de base de datos 
    cur.execute(""" 
        SELECT id_time FROM tiempo_de_uso
        WHERE id_usuario=?
        ORDER BY id_time DESC
        LIMIT 1
    """, (id_usuario,)) #pasa el id_usuario como algo seguro
    row = cur.fetchone() #da la primera fila del resultado
    con.close() #cierra la conexion con base 
    return row[0] if row else 0 #si se consigue el resultado nos va a mandar 1 si no lo hay nos mandara 0

def _init_result_table():  #esta crea la tabla respuesta_actividades si es que no existe 
    con = get_db()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS respuestas_actividades (
        id_respuesta       INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario         INTEGER NOT NULL,
        id_leccion         INTEGER NOT NULL,
        id_actividad       INTEGER NOT NULL,
        respuesta_usuario  TEXT NOT NULL,
        puntaje            INTEGER NOT NULL,
        feedback           TEXT,
        created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_usuarios) REFERENCES usuarios(id_usuario),
        UNIQUE(id_usuario, id_leccion, id_actividad) ON CONFLICT REPLACE
    );
    """)
    con.commit()
    con.close()

def guardar_resultado_actividad(id_usuario, id_leccion, id_actividad, respuesta_html, puntaje, feedback):
    #ayuda a guardar las respuesta de actividades ya que las inserta en cur.execute

    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO respuestas_actividades
            (id_usuario, id_leccion, id_actividad, respuesta_usuario, puntaje, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_usuario, id_leccion, id_actividad, respuesta_html, puntaje, feedback))
        con.commit()
        con.close()
    except Exception as e:
        print("❌ Error guardando resultado de actividad:", e)

def asegurar_tiempo_en_vivo(id_usuario: int, id_sesion: int) -> int | None: 
    # Devuelve el tiempo_de_uso según la sesión iniciada,
    # ayudando a crear y actualizar el tiempo en vivo
    try:
        con = get_db()
        cur = con.cursor()

        # Verificamos que exista la sesión y calculamos minutos hasta ahora
        cur.execute("SELECT inicio FROM sesiones WHERE id_sesion=?", (id_sesion,))
        row = cur.fetchone()
        if not row:
            con.close()
            return None

        # Minutos transcurridos desde 'inicio' hasta ahora (CURRENT_TIMESTAMP)
        cur.execute("""
            SELECT CAST(ROUND( (julianday(CURRENT_TIMESTAMP) - julianday(inicio)) * 1440 ) AS INTEGER)
            FROM sesiones
            WHERE id_sesion=?
        """, (id_sesion,))
        minutos = cur.fetchone()[0] or 0
        minutos = max(0, int(minutos))

        # Busca la existencia de el tiempo_de_uso para la sesion iniciada
        cur.execute("SELECT id_time FROM tiempo_de_uso WHERE id_sesion=?", (id_sesion,))
        trow = cur.fetchone()

        if trow:
            id_time = trow["id_time"] if isinstance(trow, sqlite3.Row) else trow[0]
            cur.execute("UPDATE tiempo_de_uso SET minutos=? WHERE id_time=?", (minutos, id_time))
        else:
            cur.execute("""
                INSERT INTO tiempo_de_uso (id_usuario, id_sesion, minutos)
                VALUES (?, ?, ?)
            """, (id_usuario, id_sesion, minutos))
            id_time = cur.lastrowid

        con.commit()
        con.close()
        return id_time
    except Exception as e:
        print("❌ Error en asegurar_tiempo_en_vivo:", e)
        return None


# crear tabla de resultados
_init_result_table()

# =========================
# Verificación por correo (nuevo)
# =========================
def _init_verificacion_table():
    con = get_db()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verificacion_email (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario  TEXT,
        correo   TEXT NOT NULL,
        codigo   TEXT NOT NULL,
        expira   DATETIME NOT NULL,
        usado    INTEGER NOT NULL DEFAULT 0
    );
    """)
    con.commit()
    con.close()
_init_verificacion_table() #esto lo hizo juluis ya no se pa que ocupo esto 

class Index:
    def GET(self):
        return render.index()

class Registro:
    def GET(self):
        return render.registro()

    def POST(self):
        form = web.input() #obtiene los datos enviados del html
        campos = [ #aqui buscamos los campos que buscamos mandar a la base
            form.get('nombre', '').strip(), #accede a un valor con el nombre de "nombre"
            form.get('apellidos', '').strip(),
            form.get('usuario', '').strip(),
            form.get('plantel', '').strip(),
            form.get('matricula', '').strip(),
            form.get('correo', '').strip(),
            form.get('password', '').strip(),
            form.get('confirmar', '').strip()
        ]
        if any(not campo for campo in campos): #verifica que los campos no esten vacios 
            return render.registro(error="llena los campos para continuar")

        correo = form.get('correo', '').strip() #elimina los espacios en correo
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$' #validacion de correos
        if not re.match(correo_regex, correo): #errores
            return render.registro(error="Ingresa un correo válido")

        password = form.get('password', '').strip() #elimna espacios en la contraseña
        confirmar = form.get('confirmar', '').strip() #igual en su confirmacion
        if password != confirmar:
            return render.registro(error="Las contraseñas no coinciden")

        nombre = form.get('nombre', '').strip() #quitamos espacios
        apellidos = form.get('apellidos', '').strip()
        usuario = form.get('usuario', '').strip()
        plantel = form.get('plantel', '').strip()
        matricula = form.get('matricula', '').strip()

        try:
            con = get_db() #conexion 
            cur = con.cursor() #cursor
            cur.execute("""
                INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, apellidos, usuario, plantel, matricula, correo, password)) #inserta al usuario en el .db
            con.commit()
            con.close()
            # CAMBIO: antes era return render.inicio_sesion()
            # Ahora redirigimos para que la URL apunte a /inicio_sesion
            return web.seeother('/inicio_sesion')
        except sqlite3.IntegrityError as e: #aqui mostramos errores con claves que deben de ser unicas
        #para que la base no caiga se mandan los errores para no repetir ciertos campos unicos
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
        usuario = (form.usuario or "").strip()   # puede ser usuario o correo
        password = (form.password or "").strip()

        if not usuario or not password:
            return render.inicio_sesion(error="Llena los campos para continuar")

        # si parece correo, validar formato
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if '@' in usuario and not re.match(correo_regex, usuario):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT id_usuario, usuario, correo, password
                FROM usuarios
                WHERE usuario=? OR correo=?
            """, (usuario, usuario))
            row = cur.fetchone()

            if row and verify_password(password, row["password"]):
                session.logged_in = True
                session.usuario_id = row["id_usuario"]
                session.username = row["usuario"]
                try:
                    cur.execute("INSERT INTO sesiones (id_usuario) VALUES (?)", (row["id_usuario"],))
                    con.commit()
                    session.id_sesion = cur.lastrowid
                except Exception as e:
                    print("⚠ Error registrando sesión:", e)
                    session.id_sesion = None
                con.close()
                return web.seeother('/info_secion')
            else:
                con.close()
                return render.inicio_sesion(error="Correo o contraseña incorrecta")
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

            # marca el fin de las tablas sesiones
            cur.execute("UPDATE sesiones SET fin = CURRENT_TIMESTAMP WHERE id_sesion = ?", (id_sesion,))

            # Calcular minutos en SQL
            cur.execute("""
                SELECT CAST(ROUND((julianday(COALESCE(fin, CURRENT_TIMESTAMP)) - julianday(inicio)) * 1440) AS INTEGER)
                FROM sesiones
                WHERE id_sesion = ?
            """, (id_sesion,))
            row = cur.fetchone()
            minutos = max(0, int(row[0])) if row and row[0] is not None else 0

            # Insertar en la tabla tiempo_de_uso
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

class Admin:
    def GET(self):
        # verifica si la sesion existe con logged_in
        if not getattr(session, "logged_in", False):
            return web.seeother('/iniciar_secion_admin') #si el admin no esta logueado, lo manda de nuevo al inicio de sesion

        try:
            con = get_db() # Crea un cursor para ejecutar consultas SQL
            cur = con.cursor()
            cur.execute("""
                SELECT id_usuario, nombre, apellidos, usuario, correo, plantel, fecha_de_registro
                FROM usuarios
                WHERE id_rol IN (1, '1') -- filtra usuarios con rol 1 (admin)
                ORDER BY fecha_de_registro DESC
            """)
            rows = cur.fetchall()
            con.close()
        except Exception as e:
            return render.admin(respuesta={"error": f"Error cargando usuarios: {e}", "usuarios": []})

        usuarios = [dict(r) for r in (rows or [])]  # Convierte cada fila en un diccionario para facilitar el movimiento de datos
        # y evitar si los datos cambian de posicion haya algun error
        # no es necesario poner r es una manera de definir mis filas, si tu quieres puedes ponerle "filas" o "chetos"

        return render.admin(respuesta={"error": None, "usuarios": usuarios}) # manda la plantilla admin usando un diccionario llamado
        # respuesta que contiene el error el cual se manda, y usuarios que es la lista de usuarios de la base de datos

class Info:
    def GET (self):
        return render.info()

class IniciarSecionAdmin:
    def GET(self):
        return render.iniciar_secion_admin(error=None)

    def POST(self):
        form = web.input(usuario='', password='')
        usuario = (form.usuario or '').strip()
        password = (form.password or '').strip()

        if not usuario or not password:
            return render.iniciar_secion_admin(error="Ingresa usuario y contraseña.")

        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("""
                SELECT id_usuario, usuario, password, id_rol
                FROM usuarios
                WHERE usuario=? OR correo=?
            """, (usuario, usuario))
            row = cur.fetchone()
            con.close()

            if not row or not verify_password(password, row["password"]):
                return render.iniciar_secion_admin(error="Usuario o contraseña incorrectos.")

            if str(row["id_rol"]) != "2":
                return render.iniciar_secion_admin(error="Acceso solo para administradores.")

            session.logged_in  = True
            session.usuario_id = row["id_usuario"]
            session.username   = row["usuario"]
            session.rol        = str(row["id_rol"])

            try:
                con = get_db(); cur = con.cursor()
                cur.execute("INSERT INTO sesiones (id_usuario) VALUES (?)", (row["id_usuario"],))
                con.commit()
                session.id_sesion = cur.lastrowid
                con.close()
            except Exception as e:
                print("⚠ Error registrando sesión:", e)
                session.id_sesion = None

            raise web.seeother('/admin')

        except Exception as e:
            return render.iniciar_secion_admin(error=f"Error interno: {e}")

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

        # Cambio de nombre
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

        # Borrado de cuenta
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

# ====== Lecciones ======
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
        codigo = (form.codigo or "").strip()   # código enviado por el usuario (contraseña actual)
        nueva_pass = (form.nueva_password or "").strip()
        repite_pass = (form.repite_password or "").strip()

        if not usuario or not correo or not codigo or not nueva_pass or not repite_pass:
            return render.cambiar_contraseña(error="Llena todos los campos")
        if nueva_pass != repite_pass:
            return render.cambiar_contraseña(error="Las contraseñas no coinciden")

        try:
            con = get_db()
            cur = con.cursor()
            # ... tras verificar existencia de usuario y correo
            cur.execute("SELECT password FROM usuarios WHERE usuario=? AND correo=?", (usuario, correo))
            row = cur.fetchone()
            if not row or not verify_password(codigo, row[0]):
                con.close()
                return render.cambiar_contraseña(error="La contraseña actual no es válida")

            # Hashea la nueva
            nuevo_hash = hash_password(nueva_pass)
            cur.execute("UPDATE usuarios SET password=? WHERE usuario=? AND correo=?", (nuevo_hash, usuario, correo))
            con.commit()
            con.close()
            # redirecciona al inicio de sesión
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

        prompt = ("Evalúa el siguiente código HTML proporcionado por un estudiante. "
                  "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
                  "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo)
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

            m = re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback)
            puntaje = int(m.group(1)) if m else 0

            if getattr(session, "usuario_id", None):
                try:
                    guardar_resultado_actividad(session.usuario_id, 1, 1, codigo, puntaje, feedback)
                except Exception as e:
                    print("⚠️ No se pudo guardar respuesta de actividad1:", e)

            if puntaje >= 7 and getattr(session, "usuario_id", None):
                try:
                    con = get_db(); cur = con.cursor()
                    id_time_actual = asegurar_tiempo_en_vivo(session.usuario_id, session.id_sesion) if getattr(session, "id_sesion", None) else None
                    cur.execute("""
                        INSERT INTO lecciones_completadas
                        (id_usuario, id_leccion, id_actividad, tipo_de_leccion, estado, id_lenguaje, id_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (session.usuario_id, 1, 1, "HTML", "completada", 1, id_time_actual))
                    con.commit(); con.close()
                except Exception as e:
                    print("⚠️ Error insertando lección completada:", e)

            return render.actividad1(resultado=feedback, codigo_enviado=codigo)

        except Exception as e:
            return render.actividad1(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad2:
    def GET(self): return render.actividad2(resultado=None, codigo_enviado="")
    def POST(self):
        form = web.input(codigo_html=""); codigo = (form.codigo_html or "").strip()
        if not codigo:
            return render.actividad2(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1 = os.getenv("GROQ_API_KEY"); modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        criterio = ("Escribe una noticia falsa (puede ser humorística, educativa o creativa). "
                    "Usa <h1> para el título, <h2> para subtítulo, <h3> para secciones; "
                    "usa <p> con <strong>, <em>, <mark>.")
        if not api_key1:
            return render.actividad2(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt = ("Evalúa el siguiente código HTML proporcionado por un estudiante. "
                  "Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n" + codigo)
        payload = {"model": modelo, "messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                              json=payload, timeout=60)
            r.raise_for_status(); data = r.json()
            feedback = data["choices"][0]["message"]["content"]
            m = re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje = int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,2,2,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad2:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,2,2,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad2(resultado=feedback,codigo_enviado=codigo)
        except Exception as e:
            return render.actividad2(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad3:
    def GET(self): return render.actividad3(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad3(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Inserta una imagen (<img> con alt, width, height), un párrafo de bienvenida y tres enlaces <a> "
                  "(externo, red social con target=\"_blank\", y ancla interna con id + href=\"#...\").")
        if not api_key1: return render.actividad3(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. "
                "Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,3,3,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad3:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,3,3,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad3(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad3(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad4:
    def GET(self): return render.actividad4(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad4(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Crea una <ul> con 4 elementos, una <ol> con pasos de un platillo, y una lista anidada con categorías 'Tecnología' y 'Arte'.")
        if not api_key1: return render.actividad4(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,4,4,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad4:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,4,4,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad4(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad4(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad5:
    def GET(self): return render.actividad5(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad5(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Tabla con <thead>, <tbody>, <tfoot>, con border y al menos 3 filas de productos; usa colspan/rowspan si aplica.")
        if not api_key1: return render.actividad5(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,5,5,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad5:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,5,5,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad5(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad5(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad6:
    def GET(self): return render.actividad6(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad6(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Formulario con: input texto (required, maxlength=40), email (type=email), password (min 6), textarea con placeholder y botón; usa label for/id.")
        if not api_key1: return render.actividad6(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,6,6,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad6:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,6,6,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad6(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad6(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad7:
    def GET(self): return render.actividad7(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad7(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Agrega <style> en el <head>; body color de fondo claro; h1/h2 azules y centrados; p con fuente diferente y tamaño mayor; usa márgenes y padding.")
        if not api_key1: return render.actividad7(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,7,7,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad7:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,7,7,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad7(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad7(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad8:
    def GET(self): return render.actividad8(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad8(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Página con <header>, <nav> (lista), <main> con <section id='Noticias'> y dos <article> (cada uno con título y párrafo); <footer> con nombre y año.")
        if not api_key1: return render.actividad8(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,8,8,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad8:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,8,8,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad8(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad8(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

class actividad9:
    def GET(self): return render.actividad9(resultado=None, codigo_enviado="")
    def POST(self):
        form=web.input(codigo_html=""); codigo=(form.codigo_html or "").strip()
        if not codigo: return render.actividad9(resultado="Por favor escribe tu código antes de enviarlo.", codigo_enviado="")
        api_key1=os.getenv("GROQ_API_KEY"); modelo=os.getenv("GROQ_MODEL","llama3-8b-8192")
        criterio=("Incluye <audio> (musica.mp3), <video> con dimensiones y un <iframe> de YouTube; escribe un <p> antes de cada uno.")
        if not api_key1: return render.actividad9(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).", codigo_enviado=codigo)
        prompt=("Evalúa el siguiente código HTML proporcionado por un estudiante. Califica de 1 a 10 y proporciona retroalimentación clara...\n\nCódigo:\n"+codigo)
        payload={"model":modelo,"messages":[
            {"role":"system","content":"Eres un evaluador experto en programación web. Evalúa exclusivamente el siguiente criterio: "+criterio+" No tomes en cuenta ningún otro aspecto del código. Sé claro, conciso y objetivo en tu retroalimentación."},
            {"role":"user","content":prompt}], "temperature":0.4}
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Content-Type":"application/json","Authorization": f"Bearer {api_key1}"},
                            json=payload, timeout=60)
            r.raise_for_status(); data=r.json()
            feedback=data["choices"][0]["message"]["content"]
            m=re.search(r'(?<!\d)(10|[0-9])(?:\s*/\s*10)?', feedback); puntaje=int(m.group(1)) if m else 0
            if getattr(session,"usuario_id",None):
                try: guardar_resultado_actividad(session.usuario_id,9,9,codigo,puntaje,feedback)
                except Exception as e: print("⚠️ No se pudo guardar respuesta de actividad9:", e)
            if puntaje>=7 and getattr(session,"usuario_id",None):
                try:
                    con=get_db(); cur=con.cursor()
                    id_time_actual=asegurar_tiempo_en_vivo(session.usuario_id,session.id_sesion) if getattr(session,"id_sesion",None) else None
                    cur.execute("""INSERT INTO lecciones_completadas
                        (id_usuario,id_leccion,id_actividad,tipo_de_leccion,estado,id_lenguaje,id_time)
                        VALUES (?,?,?,?,?,?,?)""",(session.usuario_id,9,9,"HTML","completada",1,id_time_actual))
                    con.commit(); con.close()
                except Exception as e: print("⚠️ Error insertando lección completada:", e)
            return render.actividad9(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.actividad9(resultado=f"Error al evaluar: {str(e)}", codigo_enviado=codigo)

# ====== Prompt Trainer (con persistencia) ======
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

def render_safe_markdownish(md_text: str) -> str:
    import re as _re, html as _html
    blocks = []
    def _block_repl(m):
        lang = (m.group(1) or "").strip()
        code = m.group(2)
        blocks.append(f'<pre><code class="lang-{_html.escape(lang)}">{_html.escape(code)}</code></pre>')
        return f"@@BLOCK{len(blocks)-1}@@"
    text = _re.sub(r"```(\w+)?\s*\n(.*?)\n```", _block_repl, md_text, flags=_re.DOTALL)
    html_match = _re.search(r"<!DOCTYPE html>.*</html>", md_text, flags=_re.DOTALL | _re.IGNORECASE)
    if html_match:
        code = html_match.group(0)
        blocks.append(f'<pre><code class="lang-html">{_html.escape(code)}</code></pre>')
        text = text.replace(code, f"@@BLOCK{len(blocks)-1}@@")
    text = _html.escape(text)
    for i, block_html in enumerate(blocks):
        text = text.replace(f"@@BLOCK{i}@@", block_html)
    return text

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

def _ensure_state(sess):
    if not hasattr(sess, "trainer") or not isinstance(sess.trainer, dict):
        sess.trainer = {}
    sess.trainer.setdefault("activo", False)
    sess.trainer.setdefault("paso", 0)
    sess.trainer.setdefault("historial", [])
    if not hasattr(sess, "trainer_ps_id"):
        sess.trainer_ps_id = None
    return sess.trainer

def _historial_to_text(historial):
    if not historial:
        return "Sin respuestas previas."
    return "\n".join(f"{i+1}. P: {qa['q']}\n   R: {qa['a']}" for i, qa in enumerate(historial))

def _init_prompt_tables():
    con = get_db(); cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prompt_sesiones (
        id_ps              INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario         INTEGER NOT NULL REFERENCES usuarios(id_usuario),
        prompts_correctos  INTEGER NOT NULL DEFAULT 0,
        prompt_final       TEXT,
        fecha_completado   DATETIME
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prompt_detalle (
        id_det            INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ps             INTEGER NOT NULL REFERENCES prompt_sesiones(id_ps),
        num_pregunta      INTEGER NOT NULL,
        prompt_ia         TEXT NOT NULL,
        respuesta_usuario TEXT,
        created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(id_ps, num_pregunta) ON CONFLICT REPLACE
    );
    """)
    con.commit(); con.close()
_init_prompt_tables()

def _crear_prompt_sesion(id_usuario: int) -> int:
    con = get_db(); cur = con.cursor()
    cur.execute("INSERT INTO prompt_sesiones (id_usuario, prompts_correctos) VALUES (?, 0)", (id_usuario,))
    con.commit(); ps_id = cur.lastrowid; con.close()
    return ps_id

def _registrar_prompt_ia(id_ps: int, num_pregunta: int, prompt_ia: str):
    con = get_db(); cur = con.cursor()
    cur.execute("""
        INSERT INTO prompt_detalle (id_ps, num_pregunta, prompt_ia)
        VALUES (?, ?, ?)
    """, (id_ps, num_pregunta, prompt_ia))
    con.commit(); con.close()

def _registrar_respuesta_usuario(id_ps: int, num_pregunta: int, respuesta_usuario: str):
    con = get_db(); cur = con.cursor()
    cur.execute("""
        UPDATE prompt_detalle
           SET respuesta_usuario = ?
         WHERE id_ps = ? AND num_pregunta = ?
    """, (respuesta_usuario, id_ps, num_pregunta))
    cur.execute("""
        UPDATE prompt_sesiones
           SET prompts_correctos = prompts_correctos + 1
         WHERE id_ps = ?
    """, (id_ps,))
    con.commit(); con.close()

def _finalizar_prompt_sesion(id_ps: int, prompt_final: str):
    con = get_db(); cur = con.cursor()
    cur.execute("""
        UPDATE prompt_sesiones
           SET prompt_final = ?, fecha_completado = CURRENT_TIMESTAMP
         WHERE id_ps = ?
    """, (prompt_final, id_ps))
    con.commit(); con.close()

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
            session.trainer_ps_id = None
            return json.dumps({"respuesta": "🗑️ Chat reiniciado.", "limpiar": True})

        if msg.lower() == "/help":
            return safe_json(
"""📘 Bienvenido al Prompt Trainer
Este asistente educativo te ayudará a diseñar un prompt maestro para generar una interfaz web con HTML, CSS y Flask.

Comandos disponibles:
`/quiz` — Iniciar cuestionario  
`/clear` — Reiniciar  
`/final` — Mostrar el prompt maestro (cuando termines)"""
            )

        if msg.lower() == "/quiz":
            state["activo"] = True
            state["paso"] = 0
            state["historial"] = []

            id_ps = None
            if getattr(session, "usuario_id", None):
                try:
                    id_ps = _crear_prompt_sesion(session.usuario_id)
                except Exception as e:
                    print("⚠️ Error creando prompt_sesion:", e)
            session.trainer_ps_id = id_ps

            q = TRAINER_QUESTIONS[0]
            system = (
                "Eres un asistente educativo experto en desarrollo web (Python y HTML). "
                "Para cada pregunta, primero da una definición. "
                "Incluye SIEMPRE un mini-ejemplo en triple backticks (```html ... ```). "
                "Después formula la pregunta al usuario."
            )
            user = f"Pregunta: {q}"
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)

            if session.trainer_ps_id and getattr(session, "usuario_id", None):
                try:
                    _registrar_prompt_ia(session.trainer_ps_id, 1, respuesta_raw)
                except Exception as e:
                    print("⚠️ Error guardando prompt IA (1):", e)

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

            if session.trainer_ps_id and getattr(session, "usuario_id", None):
                try:
                    _finalizar_prompt_sesion(session.trainer_ps_id, respuesta_raw)
                except Exception as e:
                    print("⚠️ Error finalizando prompt_sesion (/final):", e)

            return safe_json(respuesta_raw)

        if not state["activo"]:
            return safe_json("⚠️ Usa `/quiz` para comenzar el cuestionario.")

        paso = state["paso"]

        if msg.startswith("?") or msg.endswith("?"):
            system = "Eres un experto en desarrollo web. Responde de forma clara y didáctica."
            respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, msg)
            return safe_json(f"{respuesta_raw}\n\nAhora retomemos: {TRAINER_QUESTIONS[paso]}")

        if paso < len(TRAINER_QUESTIONS):
            num_preg = paso + 1
            state["historial"].append({"q": TRAINER_QUESTIONS[paso], "a": msg})

            if session.trainer_ps_id and getattr(session, "usuario_id", None):
                try:
                    _registrar_respuesta_usuario(session.trainer_ps_id, num_preg, msg)
                except Exception as e:
                    print("⚠️ Error guardando respuesta usuario:", e)

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

            if session.trainer_ps_id and getattr(session, "usuario_id", None):
                try:
                    _finalizar_prompt_sesion(session.trainer_ps_id, respuesta_raw)
                except Exception as e:
                    print("⚠️ Error finalizando prompt_sesion:", e)

            return safe_json(respuesta_raw)

        q = TRAINER_QUESTIONS[paso]
        system = (
            "Eres un asistente educativo experto en desarrollo web. "
            "Primero da una definición y un ejemplo en ```html ... ```. "
            "Después formula la pregunta al usuario."
        )
        user = f"Pregunta: {q}"
        respuesta_raw = _groq(os.getenv("GROQ_MODEL", "llama3-8b-8192"), system, user)

        if session.trainer_ps_id and getattr(session, "usuario_id", None):
            try:
                _registrar_prompt_ia(session.trainer_ps_id, paso + 1, respuesta_raw)
            except Exception as e:
                print("⚠️ Error guardando prompt IA (siguiente):", e)

        return safe_json(respuesta_raw)

# ====== Util para fechas en estadísticas ======
def _to_ymd(value):
    """Convierte a 'YYYY-MM-DD' desde múltiples formatos (ISO, 'YYYY-MM-DD HH:MM:SS', epoch)."""
    if value is None:
        return None
    try:
        # Epoch int/float o str numérica
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            ts = int(value)
            return datetime.datetime.utcfromtimestamp(ts).date().isoformat()
    except Exception:
        pass
    if isinstance(value, str):
        v = value.strip().replace('T', ' ')
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(v, fmt).date().isoformat()
            except Exception:
                continue
    return None

class Estadisticas:
    def _build_stats(self, id_usuario: int):
        con = get_db()
        cur = con.cursor()

        cur.execute("""
            SELECT s.inicio, s.fin, tu.minutos
            FROM tiempo_de_uso tu
            JOIN sesiones s ON s.id_sesion = tu.id_sesion
            WHERE tu.id_usuario = ?
        """, (id_usuario,))
        rows = cur.fetchall()

        agreg = {}
        for r in rows or []:
            fin = r['fin'] if isinstance(r['fin'], str) else (r['fin'].decode() if r['fin'] else None)
            inicio = r['inicio'] if isinstance(r['inicio'], str) else (r['inicio'].decode() if r['inicio'] else None)
            fecha = _to_ymd(fin) or _to_ymd(inicio)
            if not fecha:
                continue
            minutos = int(r['minutos'] or 0)
            agreg[fecha] = agreg.get(fecha, 0) + minutos

        dias_semana = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
        fechas_orden = sorted(agreg.keys())
        x_labels, y_vals = [], []
        for f in fechas_orden:
            try:
                wd = datetime.datetime.strptime(f, '%Y-%m-%d').weekday()
                x_labels.append(dias_semana[wd])
            except Exception:
                x_labels.append(f)
            y_vals.append(agreg[f])

        cur.execute("SELECT COUNT(*) AS c FROM lecciones_completadas WHERE id_usuario = ?", (id_usuario,))
        row = cur.fetchone()
        lecciones = int(row['c']) if row and row['c'] is not None else 0

        cur.execute("""
            SELECT COUNT(*) AS c
            FROM prompt_sesiones
            WHERE id_usuario = ? AND fecha_completado IS NOT NULL
        """, (id_usuario,))
        row = cur.fetchone()
        prompts = int(row['c']) if row and row['c'] is not None else 0

        con.close()

        return {
            'ok': True,
            'bar': {
                'x': x_labels,
                'y': y_vals,
                'title': 'Tiempo de uso',
                'x_title': 'Día',
                'y_title': 'Minutos'
            },
            'pie': {
                'labels': ['Lecciones', 'Prompts'],
                'values': [lecciones, prompts],
                'title': 'Lecciones vs Prompts'
            },
            'totales': {
                'minutos_totales': sum(y_vals) if y_vals else 0,
                'lecciones': lecciones,
                'prompts': prompts
            }
        }

    def GET(self):
        if not getattr(session, "usuario_id", None):
            return web.seeother('/inicio_sesion')

        data = self._build_stats(session.usuario_id)

        kpi_min = data['totales']['minutos_totales']
        kpi_lec = data['totales']['lecciones']
        TOTAL_LECCIONES = 9
        kpi_pro = int((kpi_lec / TOTAL_LECCIONES) * 100) if TOTAL_LECCIONES else 0

        bar_data = {
            'x': data['bar']['x'],
            'y': data['bar']['y'],
            'title': data['bar']['title'],
            'x_title': data['bar']['x_title'],
            'y_title': data['bar']['y_title']
        }
        pie_data = {
            'labels': data['pie']['labels'],
            'values': data['pie']['values'],
            'title': data['pie']['title']
        }

        return render.estadistica(
            kpi_min=kpi_min,
            kpi_lec=kpi_lec,
            kpi_pro=kpi_pro,
            bar_data_json=json.dumps(bar_data, ensure_ascii=False),
            pie_data_json=json.dumps(pie_data, ensure_ascii=False)
        )

    def POST(self):
        return self.GET()

class UsuarioDetalle:
    def GET(self, uid):
        if not getattr(session, "logged_in", False):
            return web.seeother('/iniciar_secion_admin')

        try:
            id_usuario = int(uid)
        except Exception:
            return web.notfound("ID de usuario inválido")

        try:
            con = get_db()
            cur = con.cursor()
            cur.execute("SELECT id_usuario FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            ok = cur.fetchone()
            con.close()
            if not ok:
                return render.admin(respuesta={"error": "El usuario no existe.", "usuarios": []})
        except Exception as e:
            return render.admin(respuesta={"error": f"Error validando usuario: {e}", "usuarios": []})

        data = Estadisticas()._build_stats(id_usuario)

        kpi_min = data['totales']['minutos_totales']
        kpi_lec = data['totales']['lecciones']
        TOTAL_LECCIONES = 9
        kpi_pro = int((kpi_lec / TOTAL_LECCIONES) * 100) if TOTAL_LECCIONES else 0

        bar_data = {
            'x': data['bar']['x'],
            'y': data['bar']['y'],
            'title': data['bar']['title'],
            'x_title': data['bar']['x_title'],
            'y_title': data['bar']['y_title']
        }
        pie_data = {
            'labels': data['pie']['labels'],
            'values': data['pie']['values'],
            'title': data['pie']['title']
        }

        return render.estadistica(
            kpi_min=kpi_min,
            kpi_lec=kpi_lec,
            kpi_pro=kpi_pro,
            bar_data_json=json.dumps(bar_data, ensure_ascii=False),
            pie_data_json=json.dumps(pie_data, ensure_ascii=False)
        )

# ─────────────────────── Lanzador ────────────────────────
if __name__ == "__main__":
    app.run()
