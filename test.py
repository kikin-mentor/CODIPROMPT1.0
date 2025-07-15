import web

urls = (
    '/', 'Index',
    '/static/(.*)', 'Static'
)

render = web.template.render('templates')

class Index:
    def GET(self):
        return render.index()

class Static:
    def GET(self, file):
        return web.redirect('/' + file)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

