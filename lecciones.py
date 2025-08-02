###############################################################
# lecciones.py
# Vistas y lógica para las lecciones de CODIPROMPT.
# Cada clase representa una lección y su renderizado.
###############################################################
import sqlite3
from web import template, seeother
from utils import obtener_info_leccion

render = template.render('templates')

# Clase genérica para lecciones
class LeccionGenerica:
    def __init__(self, id_leccion, nombre_template):
        self.id_leccion = id_leccion
        self.nombre_template = nombre_template

    def GET(self):
        from main import user_session  # Importación perezosa para evitar ciclos
        if not getattr(user_session, 'id_usuario', None):
            return seeother('/inicio_sesion')
        contenido, tiempo_total, completada = obtener_info_leccion(self.id_leccion)
        return getattr(render, self.nombre_template)(contenido=contenido, tiempo_total=tiempo_total, completada=completada)

# Instancias para cada lección
Leccion1 = LeccionGenerica(1, 'leccion1')
Leccion2 = LeccionGenerica(2, 'leccion2')
Leccion3 = LeccionGenerica(3, 'leccion3')
Leccion4 = LeccionGenerica(4, 'leccion4')
Leccion5 = LeccionGenerica(5, 'leccion5')
Leccion6 = LeccionGenerica(6, 'leccion6')
Leccion7 = LeccionGenerica(7, 'leccion7')
Leccion8 = LeccionGenerica(8, 'leccion8')
Leccion9 = LeccionGenerica(9, 'leccion9')

# Lección personalizada (estática)
class LeccionPersonalizada:
    def GET(self):
        return render.leccion_personalizada()