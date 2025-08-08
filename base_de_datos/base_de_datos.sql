.headers on --
.mode column --hace que se vea en columnas
PRAGMA foreign_keys = ON; --conecta tablas y relaciones

CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    plantel TEXT NOT NULL,
    matricula TEXT NOT NULL UNIQUE,
    correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    fecha_de_registro DATE DEFAULT CURRENT_DATE,
    imagen TEXT
    rol TEXT
);

CREATE TABLE lecciones (
    id_leccion INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    contenido_html TEXT NOT NULL,
    explicacion TEXT NOT NULL
);

CREATE TABLE lecciones_completadas(
    id_leccion_completada INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_leccion INTEGER NOT NULL,
    id_actividad INTEGER NOT NULL,
    tipo_de_leccion TEXT NOT NULL,
    estado TEXT NOT NULL,
    id_lenguaje TEXT NOT NULL,
    id_time INTEGER NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad),
    FOREIGN KEY (id_time) REFERENCES tiempo_de_uso(id_time),
    FOREIGN KEY (id_leccion) REFERENCES lecciones(id_leccion),
    FOREIGN KEY (id_lenguaje) REFERENCES lenguajes(id_lenguaje),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE lenguajes (
    id_lenguaje TEXT PRIMARY KEY,
    nombre_lenguaje TEXT NOT NULL,
    descripcion TEXT NOT NULL
);


-- Tabla para registrar sesiones de usuario (inicio y fin de sesión)
CREATE TABLE sesiones (
    id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fin DATETIME,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla para registrar el tiempo de uso por sesión
CREATE TABLE tiempo_de_uso (
    id_time INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_sesion INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    fecha_de_uso DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_sesion) REFERENCES sesiones(id_sesion)
);

CREATE TABLE tiempo_leccion (
    id_time_leccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_leccion_completada INTEGER NOT NULL,
    id_time INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_leccion_completada) REFERENCES lecciones_completadas(id_leccion_completada),
    FOREIGN KEY (id_time) REFERENCES tiempo_de_uso(id_time)
);

CREATE TABLE resumen_diario (
    id_resumen INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    id_time INTEGER NOT NULL,
    promedio_tiempo REAL,
    id_leccion_completada INTEGER NOT NULL,
    id_prompt INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_leccion_completada) REFERENCES lecciones_completadas(id_leccion_completada),
    FOREIGN KEY (id_prompt) REFERENCES prompt(id_prompt)
);

CREATE TABLE actividades (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_leccion INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    contenido TEXT, 
    respuesta_correcta TEXT, 
    puntaje INTEGER NOT NULL,
    FOREIGN KEY (id_leccion) REFERENCES lecciones(id_leccion)
);

CREATE TABLE prompt (
    id_prompt INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_leccion INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    prompts_correctos INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_leccion) REFERENCES lecciones(id_leccion)
);

CREATE TABLE rol (
    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    rol TEXT NOT NULL
);










































INSERT INTO lecciones (titulo, contenido_html, explicacion) VALUES
("Lección 1: Estructura de un Documento HTML",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n  <title>Mi sitio web</title>\n</head>\n<body>\n  <h1>Hola mundo</h1>\n  <p>Este es un documento HTML básico.</p>\n</body>\n</html>",
"Se explican etiquetas clave: <!DOCTYPE html> define el tipo de documento; <html lang=\"es\"> indica el idioma; <head> incluye metadatos como charset y viewport; <title> muestra el título en la pestaña; <body> contiene el contenido visible como encabezados y párrafos. Se enfatiza el orden correcto de etiquetas y la importancia de cerrarlas adecuadamente."),

("Lección 2: Texto, Encabezados y Formato Semántico",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Texto y encabezados</title>\n</head>\n<body>\n  <h1>Bienvenido a mi página</h1>\n  <h2>Subtítulo importante</h2>\n  <p>Este es un párrafo con <strong>énfasis</strong> y <em>cursiva</em>.</p>\n  <p>También podemos <mark>resaltar</mark> texto y usar <br> saltos de línea.</p>\n</body>\n</html>",
"Se detallan etiquetas para estructurar texto (<h1> a <h6>, <p>) y aplicar semántica visual (<strong>, <em>, <mark>). El uso correcto de encabezados mejora el SEO y la accesibilidad. <br> permite saltos de línea, y atributos como title y hidden brindan funcionalidad adicional."),

("Lección 3: Enlaces e Imágenes",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Enlaces e Imágenes</title>\n</head>\n<body>\n  <h1>Galería y enlaces</h1>\n  <p>Visita mi <a href=\"https://www.ejemplo.com\" target=\"_blank\" rel=\"noopener noreferrer\" title=\"Ir a Ejemplo\">sitio web</a>.</p>\n  <img src=\"banana.jpg\" alt=\"Foto de un plátano\" width=\"300\" height=\"200\" loading=\"lazy\">\n</body>\n</html>",
"Se estudian enlaces (<a>) con atributos como href, target, rel y title para accesibilidad y seguridad. También se muestra cómo insertar imágenes (<img>) con atributos src, alt, width, height y loading para mejorar rendimiento y accesibilidad."),

("Lección 4: Listas ordenadas, desordenadas y anidadas",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Listas HTML</title>\n</head>\n<body>\n  <h1>Tipos de listas</h1>\n  <h2>Lista desordenada</h2>\n  <ul><li>Manzana</li><li>Plátano</li><li>Naranja</li></ul>\n  <h2>Lista ordenada</h2>\n  <ol type=\"A\" start=\"3\"><li>Precalentar el horno</li><li>Preparar la masa</li><li>Hornear</li></ol>\n  <h2>Lista anidada</h2>\n  <ul><li>Frutas<ul><li>Manzana</li><li>Banana</li></ul></li><li>Verduras</li></ul>\n</body>\n</html>",
"Explica el uso de <ul>, <ol> y <li> para crear listas, con atributos type, start, reversed y value. Se presentan listas anidadas para jerarquías y recomendaciones de organización semántica."),

("Lección 5: Tablas en HTML",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Tablas HTML</title>\n</head>\n<body>\n  <h1>Precios de productos</h1>\n  <table border=\"1\">\n    <caption>Lista de productos</caption>\n    <thead><tr><th>Producto</th><th>Precio</th></tr></thead>\n    <tbody><tr><td>Manzana</td><td>$10</td></tr><tr><td>Banana</td><td>$8</td></tr></tbody>\n    <tfoot><tr><td>Total</td><td>$18</td></tr></tfoot>\n  </table>\n</body>\n</html>",
"Se explica la estructura de una tabla con <table>, <caption>, <thead>, <tbody>, <tfoot>, <tr>, <th> y <td>. También se analizan atributos como border, colspan, rowspan y scope, enfocados en claridad semántica y accesibilidad."),

("Lección 6: Formularios HTML",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Formulario de contacto</title>\n</head>\n<body>\n  <h1>Contáctanos</h1>\n  <form action=\"/enviar\" method=\"POST\">\n    <label for=\"nombre\">Nombre:</label>\n    <input type=\"text\" id=\"nombre\" name=\"nombre\" required maxlength=\"50\"><br><br>\n    <label for=\"email\">Correo electrónico:</label>\n    <input type=\"email\" id=\"email\" name=\"correo\" required><br><br>\n    <label for=\"mensaje\">Mensaje:</label><br>\n    <textarea id=\"mensaje\" name=\"mensaje\" rows=\"4\" cols=\"40\" placeholder=\"Escribe tu mensaje aquí...\"></textarea><br><br>\n    <button type=\"submit\">Enviar</button>\n  </form>\n</body>\n</html>",
"Se abordan los elementos clave para formularios: <form>, <label>, <input>, <textarea> y <button>. Atributos esenciales incluyen action, method, required, maxlength, placeholder, name, id y type, con énfasis en validación y experiencia de usuario."),

("Lección 7: CSS Básico dentro de HTML",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>CSS Básico</title>\n  <style>\n    body { background-color: #f0f8ff; font-family: Arial, sans-serif; color: #333; }\n    h1 { text-align: center; color: #0077cc; }\n    p { font-size: 18px; line-height: 1.6; margin: 20px; }\n  </style>\n</head>\n<body>\n  <h1>Estilos con CSS</h1>\n  <p>Este es un ejemplo de cómo aplicar estilos básicos directamente en HTML usando CSS.</p>\n</body>\n</html>",
"Explica cómo usar CSS interno con <style> dentro del <head>. Se presentan selectores, propiedades como background-color, font-family, color, text-align, font-size, line-height, margin; y buenas prácticas como usar clases e IDs."),

("Lección 8: HTML Semántico",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>HTML Semántico</title>\n  <style>\n    header, nav, main, section, article, footer {\n      border: 1px solid #ccc;\n      padding: 10px;\n      margin-bottom: 10px;\n    }\n  </style>\n</head>\n<body>\n  <header><h1>Mi Blog</h1></header>\n  <nav><ul><li><a href=\"#\">Inicio</a></li><li><a href=\"#\">Artículos</a></li><li><a href=\"#\">Contacto</a></li></ul></nav>\n  <main>\n    <section>\n      <h2>Últimas publicaciones</h2>\n      <article>\n        <h3>Artículo 1</h3>\n        <p>Este es el contenido del primer artículo.</p>\n      </article>\n      <article>\n        <h3>Artículo 2</h3>\n        <p>Este es el contenido del segundo artículo.</p>\n      </article>\n    </section>\n  </main>\n  <footer><p>© 2025 Mi Blog. Todos los derechos reservados.</p></footer>\n</body>\n</html>",
"Se explican etiquetas semánticas clave como <header>, <nav>, <main>, <section>, <article>, <footer>. Se destaca cómo mejoran la accesibilidad, el SEO y la estructura lógica del documento."
)

("Lección 9: Multimedia en HTML5 (Audio, Video e Iframe)",
"<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Multimedia HTML5</title>\n</head>\n<body>\n  <h1>Contenido multimedia en HTML</h1>\n  <h2>Audio</h2>\n  <audio controls>\n    <source src=\"musica.mp3\" type=\"audio/mpeg\">\n    Tu navegador no soporta el elemento de audio.\n  </audio>\n  <h2>Video</h2>\n  <video width=\"320\" height=\"240\" controls>\n    <source src=\"video.mp4\" type=\"video/mp4\">\n    Tu navegador no soporta el elemento de video.\n  </video>\n  <h2>Contenido incrustado (iframe)</h2>\n  <iframe src=\"https://www.youtube.com/embed/dQw4w9WgXcQ\" width=\"560\" height=\"315\" title=\"Video de YouTube\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>\n</body>\n</html>",
"Se explora el uso de elementos multimedia en HTML5: <audio>, <video> e <iframe>. Se discuten atributos como controls, src, type, width, height, y buenas prácticas para la inclusión de contenido multimedia."
);


















INSERT INTO rol (id_rol, rol) VALUES
(1, 'Alumno'),
(2, 'Administrativo');

















INSERT INTO actividades (id_leccion, titulo, descripcion, contenido, respuesta_correcta) VALUES
(1, "Tu primer documento HTML estructurado",
"Comprender y aplicar la estructura base de un documento HTML5.",
"Crear estructura.html con las etiquetas básicas de HTML incluyendo <html>, <head>, <meta>, <title>, <body>, <h1> y <p>.",
"Archivo HTML válido con título 'Hola, mundo' y párrafo con nombre, edad y afición."),

(2, "Estructura de una noticia",
"Jerarquizar información y aplicar formato semántico al contenido textual.",
"Noticia ficticia con encabezados <h1>, <h2>, <h3> y párrafos usando <strong>, <em>, <mark>.",
"Una página estructurada con texto y etiquetas semánticas correctamente aplicadas."),

(3, "Crea tu tarjeta de presentación digital",
"Introducir el uso de hipervínculos y elementos gráficos en HTML.",
"Archivo tarjeta.html con imagen <img>, párrafo de bienvenida y tres enlaces <a>.",
"Tarjeta personal con imagen, texto y enlaces que funcionan correctamente."),

(4, "Mi lista organizada",
"Diferenciar y aplicar listas ordenadas, desordenadas y anidadas.",
"Archivo listas.html con una <ul>, una <ol>, y una lista anidada bajo categorías 'Tecnología' y 'Arte'.",
"Una página que muestra claramente los tres tipos de listas aplicados correctamente."),

(5, "Catálogo de productos",
"Construir tablas con encabezados, celdas y pie de tabla.",
"Tabla con <thead>, <tbody>, <tfoot>, usando border, y al menos tres filas de productos.",
"Tabla funcional y visualmente organizada con separación de secciones."),

(6, "Formulario de suscripción",
"Recoger datos del usuario usando campos accesibles y validados.",
"Formulario <form> con campos de texto, email, contraseña, <textarea>, y botón de envío.",
"Formulario que valida los campos requeridos y no permite envío si hay errores."),

(7, "Dale estilo a tu perfil",
"Aplicar estilos visuales básicos usando CSS en bloque.",
"Archivo tarjeta.html con <style> y estilos aplicados a body, encabezados y párrafos.",
"Una página estilizada con fondo claro, colores y fuentes personalizadas."),

(8, "Construye una página informativa",
"Usar etiquetas semánticas para organizar contenido web.",
"Archivo semantica.html con <header>, <nav>, <main>, <section>, <article>, <footer>.",
"Estructura semántica clara que mejora accesibilidad y SEO."),

(9, "Centro multimedia",
"Incorporar contenido multimedia en una página web.",
"Archivo multimedia.html con <audio>, <video> y <iframe> de YouTube, acompañados de texto explicativo.",
"Página funcional con reproductores visibles y enlaces multimedia correctamente integrados.");





SELECT * FROM usuarios;