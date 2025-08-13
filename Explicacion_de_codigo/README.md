# Explicaciones de Codigo:
Bienvenido(a) dentro de aqui podra ver las explicaciones de las 
## 3. Base de datos: 
Hola, en este caso no me complique tanto con la base de datos ocupe una base de datos default o por defecto que trae la libreria de python que seria SQLite3.
### ¿Cómo se ejecuta una base de datos en SQLite3? 
1. Escribes **sqlite3** en tu terminal, tras esto pones el nombre de la tabla o base de datos que deseas crear: **codiprompt.db**
2. SQLite no es tan diferente de posgre o alguna otra plataforma, la única diferencia es que aquí optamos por ejecutar en una sola terminal la gestión y creación de tablas en esa misma terminal sin tener que optar por una aplicación diferente de la terminal.
3. **.headers on .mode column y PRAGMA_foreing keys =on** son comandos que nos permiten ver la cabecera, las columnas y las llaves foráneas.
4. Para visualizar las tablas creadas en sql solo  pones **.tables**
5. **SELECT * FROM nombre_de_la_tabla;** para ver el contenido de las tablas y las tablas creadas en el archivo .db.  
  
### ¿que hice yo? 
Como recomendacion yo recomiendo hacer un archivo **.sql** donde guardes la creacion de tus tablas o las insercciones que haces para que en futuras configuraciones o si es que el repositorio cae no tengas mas que pegar en la terminal, claro se puede hacer la inserccion de base de datos por un .py pero yo recomiendo que lo hagas manualmente por mera experiencia. Mi archivo de la creacion de tablas y insercion manual de algunas de estas se encuentra en **base_de_datos** con una unica carpeta que es el .sql, si ya subiste tus bases de datos, te recomiendo que las pruebes con las consultas en **consultas.txt**

#### Despues de creadas las tablas 
Aqui explicare las inserciones a base de datos y en main.py
1. **DB_PATH** se pone para que el sistema o aplicacion sepa donde ubicar el archivo de la base, es para que no este buscando en todas las carpetas la base de datos y sea mas directo el proceso para la base de datos 
2. **def** los def, los ocupo 


