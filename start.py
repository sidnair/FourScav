import web
from web.session import Session, DiskStore
import urllib
import json
from models import User
from models import Place
import time
from snakelegs import connect
from secrets.secrets import ConfigData, apiURL
from helpers import *

web.config.debug = False

connect('4sqav')

urls = (
	'/auth/', 'auth',
	'/list/new', 'new',
	'/list/([0-9a-f]+)/add_place/(.+)', 'add_place',
	'/list/([0-9a-f]+)/remove_place/(.+)', 'remove_place',
	'/list/([0-9a-f]+)/add_tag/(.+)', 'add_tag',
	'/list/([0-9a-f]+)/remove_tag/(.+)', 'remove_tag',
	'/list/([0-9a-f]+)/join', 'join',
	'/list/([0-9a-f]+)', 'get_list',
	'/user/name', 'get_username',
)

app = web.application(urls, locals())

session = web.session.Session(app, DiskStore('../sessions'))

def get_current_user():
	return User.find_one({'token': session.token})

class auth:
	def GET(self):
		params = urllib.urlencode({'client_id' : ConfigData.clientID, 'client_secret' : ConfigData.clientSecret, 'grant_type' : 'authorization_code', 'redirect_uri' : apiURL.oauthCallbackURL , 'code' : web.input().code })
		
		hostname = "https://foursquare.com/oauth2/access_token?" + params
		f = urllib.urlopen(hostname)
		print(hostname)
		accResponse = f.read()
		accDict = json.loads(accResponse)
		print(accResponse)
		accToken = accDict.get("access_token")
		if accToken == None:
			return """<!--ID10T,--> There was a problem authenticating, please go back to the 
					front page and try again"""
		else:
			session.token = accToken
			usernameUrl = 'https://api.foursquare.com/v2/users/self?oauth_token='+accToken
			f = urllib.urlopen(usernameUrl)
			userDataStr = f.read()
			userData = json.loads(userDataStr)['response']['user']
			fullname = userData.get('firstName', '')+' '+userData.get('lastName','')
			print(userDataStr)
			user = User.find_one({'token':accToken})
			if user==None:
				user = User(fullname=fullname, token=accToken, user_id=userData['id'])
				user.save()
			return 'You are logged in as '+fullname
			#raise web.seeother('/')

class new:
	def POST(self):
		#set start time
		lst_start = int(web.input().get('start', time.time()))
		lst_places = web.input()['places']
		#add places/tags
		lst_tags = web.input()['tags']
		#set end time
		lst_end = int(web.input().get('end', -1))
		#add a "creator"
		lst_creator = get_current_user()._id
		hunt = Hunt(creator = lst_creator, places = lst_places, tags = lst_tags, 
					start_time = lst_start, end_time = lst_end)
		hunt.save()
		return expand_place(hunt.to_dict())

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
		user = get_current_user()
		hunt = Hunt.find_one({'_id':list_id})
		hunt.users.append(user._id)
		hunt.save()
		return "ok"

class leave:
	def POST(self, list_id):
		user = get_current_user()
		hunt = Hunt.find_one({'_id':list_id})
		hunt.users.remove(user._id)
		if len(hunt.users) == 0:
			hunt.delete()
		else: hunt.save()
		return "ok"

class get_list:
	def GET(self,list_id):
		hunt = Hunt.find_one({'_id':list_id})
		return expand_hunt(hunt)

class get_username:
	def GET(self):
		user = get_current_user()
		return user.fullname

if __name__ == '__main__':
	app.run()

def update(user_id):
	#database gets list of hunts from user_id
	for hunt in hunts:
		pass
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
