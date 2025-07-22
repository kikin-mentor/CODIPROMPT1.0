import web
import sqlite3
import re

urls = (
    '/', 'Index',
    '/registro', 'Registro',
    '/inicio_sesion', 'InicioSesion',
    '/info_secion','InfoSecion',
    '/leccion_rapida','LeccionRapida',
    '/perfil_user','PerfilUser',
    '/static/(.*)', 'Static',
    '/cambiarcontraseña', 'cambiarcontraseña',
)

render = web.template.render('templates')

class Index:
    def GET(self):
        return render.index()

class Registro:
    def GET(self):
        return render.registro()

    def POST(self):
        form = web.input()
        campos = [
            form.get('nombre', '').strip(),
            form.get('apellidos', '').strip(),
            form.get('usuario', '').strip(),
            form.get('plantel', '').strip(),
            form.get('matricula', '').strip(),
            form.get('correo', '').strip(),
            form.get('password', '').strip(),
            form.get('confirmar', '').strip()
        ]
        if any(not campo for campo in campos):
            return render.registro(error="llena los campos para continuar")

        # Validar correo electrónico
        import re
        correo = form.get('correo', '').strip()
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if not re.match(correo_regex, correo):
            return render.registro(error="Ingresa un correo válido")

        # Validar que las contraseñas coincidan
        password = form.get('password', '').strip()
        confirmar = form.get('confirmar', '').strip()
        if password != confirmar:
            return render.registro(error="Las contraseñas no coinciden")

        nombre = form.get('nombre', '').strip()
        apellidos = form.get('apellidos', '').strip()
        usuario = form.get('usuario', '').strip()
        plantel = form.get('plantel', '').strip()
        matricula = form.get('matricula', '').strip()
        correo = form.get('correo', '').strip()
        password = form.get('password', '').strip()
        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            cur.execute("INSERT INTO usuarios (nombre, apellidos, usuario, plantel, matricula, correo, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (nombre, apellidos, usuario, plantel, matricula, correo, password))
            con.commit()
            con.close()
            return render.inicio_sesion() # Redirige a la página de inicio de sesión
        except sqlite3.IntegrityError as e:
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
        usuario = form.usuario.strip()
        password = form.password.strip()

        if not usuario or not password:
            return render.inicio_sesion(error="llena los campos para continuar")


        # Validar si el usuario es un correo electrónico válido
        correo_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if '@' in usuario and not re.match(correo_regex, usuario):
            return render.inicio_sesion(error="Ingresa un correo válido")

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            # Permitir login por usuario o correo
            cur.execute("SELECT password FROM usuarios WHERE usuario=? OR correo=?", (usuario, usuario))
            row = cur.fetchone()
            con.close()

            if row and row[0] == password:
                # session.usuario = usuario  # Si usas sesiones, inicialízalas correctamente
                return render.info_secion()
            else:
                return render.inicio_sesion(error="usuario o contraseña incorrecta")
        except Exception as e:
            return render.inicio_sesion(error="usuario o contraseña incorrecta")

# Registro de nuevo usuario

class InfoSecion:
    def GET(self):
        return render.info_secion()
    
class LeccionRapida:
    def GET(self):
        return render.leccion_rapida()

class PerfilUser:
    def GET(self):
        return render.perfil_user()

class Static:
    def GET(self, file):
        return web.redirect('/static/' + file)

class cambiarcontraseña:
    def GET(self):
        return render.cambiar_contraseña()

    def POST(self):
        form = web.input()
        usuario = form.usuario.strip()
        correo = form.correo.strip()
        antigua_pass = form.antigua_password.strip()
        nueva_pass = form.nueva_password.strip()
        repite_pass = form.repite_password.strip()

        if not usuario or not correo or not antigua_pass or not nueva_pass or not repite_pass:
            return render.cambiar_contraseña(error="Llena todos los campos")
        if nueva_pass != repite_pass:
            return render.cambiar_contraseña(error="Las contraseñas no coinciden")

        try:
            con = sqlite3.connect("usuarios.db")
            cur = con.cursor()
            
            cur.execute("SELECT 1 FROM usuarios WHERE usuario=?", (usuario,))
            if not cur.fetchone():
                con.close()
                return render.cambiar_contraseña(error="No se encontro usuario")
            # Validar correo
            cur.execute("SELECT 1 FROM usuarios WHERE correo=?", (correo,))
            if not cur.fetchone():
                con.close()
                return render.cambiar_contraseña(error="No se encontro correo")
            # Validar antigua contraseña
            cur.execute("SELECT password FROM usuarios WHERE usuario=? AND correo=?", (usuario, correo))
            row = cur.fetchone()
            if not row or row[0] != antigua_pass:
                con.close()
                return render.cambiar_contraseña(error="La contraseña no es valida")
            # Actualizar contraseña
            cur.execute("UPDATE usuarios SET password=? WHERE usuario=? AND correo=?", (nueva_pass, usuario, correo))
            con.commit()
            con.close()
            # Redirigir a la página de inicio de sesión después de actualizar
            return web.seeother("/inicio_sesion")
        except Exception as e:
            return render.cambiar_contraseña(error=f"Error al cambiar contraseña: {e}")

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
