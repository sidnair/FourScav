import web

urls = (
)

app = web.application(urls, locals())

if __name__ == '__main__':
    app.run()