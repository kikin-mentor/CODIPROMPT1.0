.headers on --
.mode column --hace que se vea en columnas
PRAGMA foreign_keys = ON; --conecta tablas y relaciones

CREATE TABLE  usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    plantel TEXT NOT NULL,
    matricula TEXT NOT NULL UNIQUE,
    correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE lecciones (
    id_leccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    tipo_de_leccion TEXT NOT NULL,
    estado TEXT NOT NULL,
    puntaje INTEGER NOT NULL,
    id_lenguaje TEXT NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_lenguaje) REFERENCES lenguajes(id_lenguaje),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE lenguajes (
    id_lenguaje TEXT PRIMARY KEY,
    nombre_lenguaje TEXT NOT NULL,
    descripcion TEXT NOT NULL,
);

CREATE TABLE tiempo_de_uso (
    id_time INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    tiempo DATE DEFAULT CURRENT_DATE,
    minutos INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE tiempo_leccion (
    id_time_leccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_time INTEGER NOT NULL,
    FOREIGN KEY (id_time) REFERENCES tiempo_de_uso(id_time),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    lecciones_completadas INTEGER NOT NULL
);

CREATE TABLE resumen_diario (
    id_resumen INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    tiempo_total INTEGER NOT NULL,
    promedio_tiempo REAL,
    id_time_leccion INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_time_leccion) REFERENCES tiempo_leccion(id_time_leccion)
);

CREATE TABLE prompt (
    id_prompt INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    tipo_leccion TEXT NOT NULL,
    id_leccion INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    FOREIGN KEY (id_leccion) REFERENCES lecciones(id_leccion),
)

SELECT * FROM usuarios;