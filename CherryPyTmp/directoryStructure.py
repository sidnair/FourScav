import cherrypy
import urllib2
import urllib
import json
import pymongo

class Auth(object):
    def index(self,code=""):
        authDict = {}
        authDict["client_id"] = "DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00"
        authDict["client_secret"] = "MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE"
        authDict["grant_type"] = "authorization_code"
        authDict["redirect_uri"] = "http://localhost:8080/auth/"
        authDict["code"] = code
        urlencoding = urllib.urlencode(authDict)
        req = urllib2.urlopen("https://foursquare.com/oauth2/access_token",urlencoding)
        dicty = json.load(req)
        return dicty["access_token"]

    index.exposed = True


class User(object):
    def hunts(self):
        return "tmp"
    def name(self):
        return "name"
    hunts.exposed = True

class Hunts(object):
    def new(self):
        return "new hunt"
    new.exposed = True

    def default(self,id = "", action = "get", foursq = ""):
        if id == "":
            return "Empty id"
        if action == "get":
            return "getting name"
        elif action == "join":
            return "joining hunt"
        elif action == "remove_tag":
            if foursq == "":
                return "need to give me a foursquare id"
            return "removing tag"
        elif action == "add_tag":
            if foursq == "":
                return "need to give me a foursquare id"
            return "adding tag"
        elif action == "remove_place":
            if foursq == "":
                return "need to give me a foursquare id"
            return "removing placing"
        elif action == "add_place":
            if foursq == "":
                return "need to give me a foursquare id"
            return "adding place"
        else:
            return "bad action!"
            
        return "tmp"
    default.exposed = True

class Venues(object):
    def search(self):
        return "searching"
    search.exposed = True

class Index(object):
    user = User()
    venues = Venues()
    auth = Auth()
    hunts = Hunts()

    def index(self):
        return "hello world"
    index.exposed = True

cherrypy.quickstart(Index())

