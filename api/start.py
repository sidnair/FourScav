import web
from web.session import Session, DiskStore
import urllib
import json
from models import User
from models import Place
import connection
import time

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
			usernameUrl = 'https://api.foursquare.com/v2/users/self?oauth_token='+accToken
			f = urllib.urlopen(usernameUrl)
			userDataStr = f.read()
			userData = json.loads(userDataStr)['response']
			fullname = userData.get('firstName')+' '+userData.get('lastName')
			print(userDataStr)
			user = User(fullname=fullname, token=accToken, user_id=userData['id'])
			user.save()
			return "Congrats - you logged in as "+fullname

class new:
	def POST(self):
		lst_start = web.input()['start']
		#set start time
		lst_places = web.input()['places']
		lst_tags = web.input()['tags']
		#add places/tags
		lst_end = web.input()['end']
		#set end time
		lst_creator = web.input()['creator']
		#add a "creator"

		hunt = Hunt(creator = lst_creator, places = lst_places, tags = lst_tags, start_time = lst_start, end_time = lst_end)
		hunt.save()
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

		place = Place(name = accName,desc = accDesc, tags = accTags, geo_lat = accLat, geo_long = accLong)
		place.save()
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
		#database magic
		pass

if __name__ == '__main__':
	app.run()

def update(user_id):
	#database gets list of hunts from user_id
	for hunt in hunts:

	#gets all users on hunt
	#gets all location on hunt, puts them in dicty

		#hunt_last_updated = hunt.get("startTime")
		for usr in usrs:
		#tmp_id = usr.get_id()
		#tmp_oauth = usr.get_token()
			hostname = "https://api.foursquare.com/v2/users/" + tmp + "/venuehistory?" + "?afterTimestamp= " + hunt_last_updated + "&oauth_token="+tmp_oauth
			f = urllib.urlopen(hostname)
			accResponse = f.read()
			accDict = json.loads(accResponse)
		#lst = accDict['response']['venues']['items']

			for elt in lst:
				if elt["venue"]["id"] in dicty:
					#set list of places where he needs to go to show he has been there
					#check if winner
					#if winner, and winner is None, set him to winner
					pass
		#updates start time on all hunts
		#update start time w/ int(time.time())
	pass
