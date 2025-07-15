import web

urls = (
    '/', 'Index',
    '/registro', 'Registro',
    '/inicio-sesion', 'InicioSesion',
    '/static/(.*)', 'Static'
)

render = web.template.render('templates')

class Index:
    def GET(self):
        return render.index()

class Registro:
    def GET(self):
        return render.registro()

class InicioSesion:
    def GET(self):
        return render['inicio-sesion']()

class Static:
    def GET(self, file):
        return web.redirect('/static/' + file)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
