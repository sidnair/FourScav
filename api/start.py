import web
from web.session import Session, DiskStore
import urllib
import json
from models import User

web.config.debug = False

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

session = web.session.Session(app, DiskStore('../sessions'))

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
			f = urllib.urlopen('https://api.foursquare.com/v2/users/self')
			print(f.read())
			return "Congrats - you logged in"

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
	def POST(self,list_id,fsq_id):
		oauth = None
		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth #oauth token

		f = urllib.urlopen(hostname)
		accResponse = f.read()
		accDict = json.loads(accResponse)
		accName = accDict.get("name")
		accLat = accDict.get("location").get("lat")
		accLong = accDict.get("location").get("long")
		accDesc = accDict.get("description")
		accTags = accDict.get("tags")

		#database magic
		pass

class remove_place:
	def POST(self,list_id,fsq_id):
		#database magic
		pass

class add_tag:
	def POST(self,list_id,fsq_id):
		#database magic
		pass

class remove_tag:
	def POST(self,list_id,fsq_id):
		#database magic
		pass

class join:
	def POST(self,list_id):
		#database magic
		pass

class get_list:
	def POST(self,list_id,fsq_id):
		pass

if __name__ == '__main__':
	app.run()

