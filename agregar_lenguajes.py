import sqlite3

def agregar_lenguajes():
    con = sqlite3.connect("lenguajes.db")
    cur = con.cursor()
    # Eliminar la tabla si existe para evitar conflictos de columnas
    cur.execute("DROP TABLE IF EXISTS lenguajes")
    cur.execute('''CREATE TABLE lenguajes (
        id_lenguaje INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        descripcion TEXT
    )''')
    lenguajes = [
        ("Python", "Lenguaje de programación multipropósito, fácil de aprender y muy usado en ciencia de datos, web y automatización."),
        ("CSS", "Lenguaje de estilos para definir la apariencia visual de páginas web."),
        ("HTML", "Lenguaje de marcado para estructurar el contenido de páginas web."),
        ("Flask", "Framework ligero para crear aplicaciones web en Python.")
    ]
    for nombre, descripcion in lenguajes:
        cur.execute("INSERT INTO lenguajes (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    con.commit()
    con.close()

if __name__ == "__main__":
    agregar_lenguajes()
