import web
from web.session import Session, DiskStore
import urllib
import json
from models import User

urls = (
	'/auth/', 'auth',
	'/list/new', 'new',
	'/list/([^/]+)/add_place/(.+)', 'add_place',
	'/list/([^/]+)/remove_place/(.+)', 'remove_place',
	'/list/([^/]+)/add_tag/(.+)', 'add_tag',
	'/list/([^/]+)/remove_tag/(.+)', 'remove_tag',
	'/list/([^/]+)/join', 'join',
	'/list/([^/]+)', 'get_list'
)

app = web.application(urls, locals())

session = web.session.Session(app, Diskstore('../sessions'))

if __name__ == '__main__':
	app.run()

class auth:
	def GET(self):
		params = urllib.urlencode({'client_id' : 'DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00', 'client_secret' : 'MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE', 'grant_type' : 'authorization_code', 'redirect_uri' : 'http://localhost:8080/auth/', 'code' : web.input().code })

		hostname = "https://foursquare.com/oauth2/access_token?" + params
		f = urllib.urlopen(hostname)
		accResponse = f.read()
		accDict = json.loads(accResponse)
		accToken = accDict.get("access_token")
		if accToken == None:
			return "ID 10 T error"
		else:
			session.token = accToken
			return "Congrats - you logged in"

class login:
	def GET(self):
		return "<a href=""></a>"

class new:
	def POST(self):
		web.input()['start']
		#set start time
		web.input()['places']
		web.input()['tags']
		#add places/tags
		web.input()['end time']
		#set end time
		web.input()['creator']
		#add a "creator"
		#return new list id
		pass

class add_place:
	def POST(self):
		pass

class remove_place:
	def POST(self):
		pass

class add_tag:
	def POST(self):
		pass

class remove_tag:
	def POST(self):
		pass

class join:
	def POST(self):
		pass

class get_list:
	def POST(self):
		pass
