import web
from web.session import Session, DiskStore
import urllib
import json
nfrom models import User
from models import Place
import time
from snakelegs import connect
from secrets.secrets import ConfigData, apiURL

web.config.debug = False

connect('4sqav', 'flame.mongohq.com', 27058, '4sqav', 'hacknyspring2011')

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
	return User.find_one({'token', session.token})

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
		lst_creator = web.input()['creator']
		hunt = Hunt(creator = lst_creator, places = lst_places, tags = lst_tags, 
					start_time = lst_start, end_time = lst_end)
		hunt.save()
		return json.dumps(hunt.to_dict())

class search:
	def POST(self):
		hostname = "https://api.foursquare.com/v2/venues/search?limit=10&query=" + web.input().query
		return urllib.urlopen(hostname)
		

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


#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/photos/" #oauth token

#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/links/" #oauth token

#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/tips/" #oauth token

		place = Place(name = accName,desc = accDesc, tags = accTags, geo_lat = accLat, geo_long = accLong)
		place.save()


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
		user = User.find_one({'_id':list_id})
		return json.dumps(user.to_dict())
		
def 

class get_username:
	def GET(self):
		user = get_current_user()
		return user.fullname

if __name__ == '__main__':
	app.run()

def update(user_id):
	#database gets list of hunts from user_id
	cur_usr = User.find_one({"user_id":user_id})
	usr_dict = cur_usr.to_dict()
	hunts = usr_dict['active_lsts']

	for hunt in hunts:
		hunt_dict = hunt.to_dict()
		usrs = hunt_dict['users']
	#gets all users on hunt
	#gets all location on hunt, puts them in dicty

		#hunt_last_updated = hunt.get("startTime")
		for usr in usrs:
			cur_usr_dict = usr.to_dict()
			tmp_id = cur_usr_dict['user_id']
			tmp_oauth = cur_usr_dict['token']
			hostname = "https://api.foursquare.com/v2/users/" + tmp + "/venuehistory?" + "?afterTimestamp= " + hunt_last_updated + "&oauth_token="+tmp_oauth
			f = urllib.urlopen(hostname)
			accResponse = f.read()
			accDict = json.loads(accResponse)
			lst = accDict['response']['venues']['items']

			for elt in lst:
				if elt["venue"]["id"] in dicty:
					#set list of places where he needs to go to show he has been there

					hunt_lsts = []
					#check if winner
					for :
						hunt_lsts.append()
					#if winner, and winner is None, set him to winner
					pass
		#updates start time on all hunts
		#update start time w/ int(time.time())
