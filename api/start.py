import web

urls = (
	'/auth/', 'auth'
)

app = web.application(urls, locals())

if __name__ == '__main__':
	app.run()

class auth:
	def GET(self):
		return web.input()
