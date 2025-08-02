###############################################################
# utils.py
# Funciones utilitarias para CODIPROMPT.
# Incluye helpers para manejo de lecciones, configuración de API,
# y otras operaciones comunes usadas en el backend.
# Casi me dejan, esto esta bien dlvrga 
###############################################################
import sqlite3
import os

def obtener_info_leccion(id_leccion, user_session=None):
    usuario = None
    id_usuario = None
    if user_session:
        usuario = getattr(user_session, 'usuario', None)
        id_usuario = getattr(user_session, 'id_usuario', None)
    con = sqlite3.connect("lecciones.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT contenido FROM lecciones WHERE id_leccion=?", (id_leccion,))
    row = cur.fetchone()
    contenido = row["contenido"] if row and "contenido" in row.keys() else (row[0] if row else "")
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

def get_api_config():
    api_key = os.getenv("GROQ_API_KEY")
    modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    return api_key, modelo