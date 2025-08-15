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

2. **def** los def, los ocupo mayormanete para obtener datos o crear tablas si es que no existen ya que en los primeros avances del proyecto algunas bases no se creaban ni por mis .sql o inserciones. Incluso las ocupe en algunos casos para guardar respuestas, ya que pasabsa en algunos casos como en el tiempo que no me lo guardaba, para evitar eso, preferi meter un respaldo con los def  

3. **.strip** ayuda a eliminar campos que yo le pido en este caso lo ocupe para quitar espacios para mejor envio en baase de datos pero si quitamos las comillas sencillas ('nombre', '').strip() y en vez de dejarlas vacias le ponemos una letra, va eliminar dicha letra ('nombre', '**a**').strip() Aqui va eliminar todas las a de nombre  

4. **sqlite3.IntegrityError** ayuda a que la integridad de la base de datos se conserve es decir que campos que deben de ser unicos o irrepetibles no se repitan para non dañar la logica de la base  

5. Como recordatorio **NO USES #* cuando comentas en .sql es con --  

6. Ocupe **init_** en algunos def ya que me permitiainiciar algunas tablas por si no existian, ya que repetidamente no me dejaba iniciar de manera correcta  

7. **cur.execute** ayuda a ejecutar los comandos de base de datos (sql) atraves de un cursor y **conn.commit()** ayuda a guardar los cambios realizados adecuadamente  

8. **CURRENT_TIMESTAMP** ayuda a guardar datos actuales como la hora o fecha ACTUALES  

9. **.get** se usa para obtener valores en un diccionario, si se le puso form por la palabra *formulario* ya que quiero que obtenga valores del formulario, y los lea, ayuda igual a evitar errores como campos vacios o errores en correo electronico  

10. **getattr** lee algun campo de forma segura dentro de los parentesis se pon el campo y  

11. **julianday** en sqlite3 sirve para convertir la fecha/hora en numero decimal y los dias transcurridos desde el año juliano  

12. **COALESCE** colobora la finalizacion de sesiones, si no "cerramos sesion" en el perfil el valor en la tabla sesiones aparecera como NULL (nulo o sin valor) y si "cerramos sesion" nos mandar la fecha y hora actual de ese cierre y la mandara a la tabla sesiones en el .db  

13. **(julianday(...) - julianday(inicio))** hace que la fecha de fin se reste con la fecha de inicio y el resultado nos lo dara en dias pero para evitar eso agregamos **(*1440)** ya que este surge por la multiplicacion de las 24 horas por los 60 minutos que tiene cada hora y con esto logramos que ahora el resultado salga en **minutos** y no en dias.  

14. **ROUND** ayuda a redondear numeros (de 5.55 minutos a 5.6 minutos)  

15. **CAST(... AS INTEGER)** convierte el numero a entero (para no tomar segundos) esto lo hacemos por si round termina redondeando los regundos y no a enteros hace que ese 5.6 se convierta en 6  

16. Para esta logueado buscamos en la carpeta session que guarda los datos del usuario, si no hay ningun dato de usuarrio el logueado no existe :3  

17. 

