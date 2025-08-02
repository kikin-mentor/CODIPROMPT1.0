
# CODIPROMPT

Plataforma interactiva para aprender programación mediante lecciones y actividades prácticas.

## Estructura de carpetas

- **base_de_datos/**: Contiene el archivo SQL para inicializar las bases de datos.
- **imgs/**: Imágenes generales del sistema (logos, ilustraciones).
- **static/**: Archivos estáticos accesibles desde la web (iconos, logos, imágenes de plataformas).
- **templates/**: Plantillas HTML para renderizar las vistas del sistema.
- **sessions/**: Archivos de sesión de usuarios (gestión interna).
- **lecciones.db, usuarios.db, tiempo.db, lenguajes.db**: Bases de datos SQLite para almacenar información de usuarios, lecciones, tiempos y lenguajes.

## Archivos principales

- **main.py**: Archivo principal del backend. Define rutas, vistas y lógica central. Aquí se importan los módulos de lecciones, actividades y utilidades.
- **lecciones.py**: Define las clases y lógica de cada lección.
- **actividades.py**: Define las clases y lógica de cada actividad.
- **utils.py**: Funciones auxiliares reutilizables (por ejemplo, obtener información de lección).
- **test.py**: Pruebas y utilidades para testear el sistema.

## ¿Cómo funciona?

1. El usuario accede a la plataforma y puede registrarse o iniciar sesión.
2. Tras iniciar sesión, accede a la pantalla de bienvenida y puede navegar por las lecciones y actividades.
3. Cada lección está vinculada a una actividad práctica.
4. El progreso y tiempo de uso se almacenan en las bases de datos.
5. El sistema es modular: para agregar nuevas lecciones o actividades, solo crea una nueva clase y agrega la ruta en main.py.

## ¿Cómo ejecutar?

1. Instala las dependencias necesarias (ver requieriment.txt).
2. Ejecuta `main.py` para iniciar el servidor web.
3. Accede desde tu navegador a la URL indicada por el servidor.
4. liz ya quedo loca estas vacaciones, casi la dejan y ya ha chillado en el codigo como 200 veces.
