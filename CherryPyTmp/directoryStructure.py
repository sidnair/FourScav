import cherrypy


class User(object):
    def cool():
        return "Whoa"
    cool.exposed = True

cherrypy.quickstart(User)
