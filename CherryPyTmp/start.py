import web
from web.session import Session, DiskStore
import urllib
import json
from models import *
import time
from snakelegs import connect
from secrets.secrets import ConfigData, apiURL
from helpers import *
from pymongo.objectid import ObjectId

web.config.debug = False

connect('4sqav')

urls = (
	'/static/main.html','main',
	'/auth/', 'auth',
	'/list/new', 'new',
	'/list/([0-9a-f]+)/add_place/(.+)', 'add_place',
	'/list/([0-9a-f]+)/remove_place/(.+)', 'remove_place',
	'/list/([0-9a-f]+)/add_tag/(.+)', 'add_tag',
	'/list/([0-9a-f]+)/remove_tag/(.+)', 'remove_tag',
	'/list/([0-9a-f]+)/join', 'join',
	'/list/([0-9a-f]+)', 'get_list',
	'/user/name', 'get_username',
	'/user/lists', 'user_lists',
	'/venues/search', 'venue_search',
)

app = web.application(urls, locals())

session = web.session.Session(app, DiskStore('./sessions/'))

class main:
	def GET(self):
#		if not hasattr(session, "id"):
		raise web.seeother("/static/index.html")

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
			print(session.token)
			usernameUrl = 'https://api.foursquare.com/v2/users/self?oauth_token='+accToken
			f = urllib.urlopen(usernameUrl)
			userDataStr = f.read()
			userData = json.loads(userDataStr)['response']['user']
			fullname = userData.get('firstName', '')+' '+userData.get('lastName','')
			print(userDataStr)
			user = User.find_one({'token':str(accToken)})
			if user==None:	
				user = User(fullname=fullname, token=accToken, user_id=userData['id'])
				user.save()
			raise web.seeother('/static/main.html')

class new:
	def POST(self):
		store = web.input(**{'places[]':[], 'tags[]':[]})
		#set start time
		print(store)
		print web.data()
		#name, desc, tags (defaults to an empty array), places
		lst_start = -1
		if hasattr(store, "start"):
			lst_start = store.start
		else:
			lst_start = time.time()

#		lst_start = time.time()
		lst_desc = store.desc
		lst_name = store.name

		lst_places = -1
		if hasattr(web.input(), "places"):
			lst_places = web.input().places
		if hasattr(store, "places[]"):
			lst_places = store['places[]']
		else:
			lst_places = []
		print lst_places
		#add places/tags

		lst_tags = -1
		if hasattr(store, "tags[]"):
			lst_tags = store['tags[]']
		else:
			lst_tags = []

		#set end time
		lst_end = -1
		if hasattr(web.input(), "end"):
			lst_end = web.input().end
		else:
			lst_end = -1

		#add a "creator"
		lst_creator = get_current_user()
		
		print(lst_creator._id)
		hunt = Hunt(name=lst_name, desc=lst_desc, creator = lst_creator._id, places = lst_places, tags = lst_tags, start_time = lst_start, end_time = lst_end, users = [lst_creator._id])
#		hunt.users.append(lst_creator._id)
		hunt.save()
		
		lst_creator.active_lsts.append(str(hunt._id))
		lst_creator.save()

		print(hunt)
		return json.dumps(expand_hunt(hunt))

class venue_search:
	def POST(self):
		hostname = "https://api.foursquare.com/v2/venues/search?limit=10&query=" + web.input().query+ "&ll=" + web.input().lat + "," + web.input().long +  "&oauth_token=" + session.token
		return urllib.urlopen(hostname)
		

class add_place:
	def POST(self,list_id,fsq_id):
		oauth = None
		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth #oauth token

		f = urllib.urlopen(hostname)
		accResponse = f.read()

		print accResponse

		accDict = json.loads(accResponse)

		user = get_current_user()  #of type user

		accName = accDict.get("name")
		accLat = accDict.get("location").get("lat")
		accLong = accDict.get("location").get("long")
		accDesc = accDict.get("description")
		accTags = accDict.get("tags")


#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/photos/" #oauth token

#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/links/" #oauth token

#		hostname = "https://api.foursquare.com/v2/venues/" + fsq_id + "?" + oauth + "/tips/" #oauth token
		
		hunt=Hunt.find({'_id' : list_id})
		

		place = Place(name = accName,desc = accDesc, tags = accTags, geo_lat = accLat, geo_long = accLong)
		hunt.places.append(place)
		hunt.save()
		place.save()
		return json.dump({"success":True})


class remove_place:
	def POST(self,list_id,fsq_id):
		hunt = Hunt.find_one({'_id' : list_id})
		place = Place.find_one({'fsq_id' : fsq_id})
		hunt.places.remove(place._id)
		hunt.save()
		return json.dump({"success":True})
		
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

		user.active_lsts.append(hunt._id)
		user.save()
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
		hunt = Hunt.find_one({'_id':ObjectId(list_id)})
		if hunt:
			return json.dumps(expand_hunt(hunt))
		return json.dumps({'ok': False})

class user_lists:
	def GET(self, inactive=False):
		user = get_current_user()
		hunts = []
		for hid in user.active_lsts:
			hunt = Hunt.find_one({'_id': hid})
			if hunt:
				hunts.append(str(hunt._id))
		if inactive:
			for hid in user.dead_lsts:
				hunt = Hunt.find_one({'_id': hid})
				if hunt:
					hunts.append(str(hunt._id))
		return json.dumps(hunts)

class get_username:
	def GET(self):
		user = get_current_user()
		return user.fullname

def update(user_id):
	#database gets list of hunts from user_id
	cur_usr = User.find_one({"user_id":user_id})
	usr_dict = cur_usr.to_dict()
	hunts = usr_dict['active_lsts']

	for hunt in hunts:
		hunt_dict = Hunt.find({"_id" : hunt[0]}).to_dict()
		usrs = hunt_dict['users']
	#gets all users on hunt
	#gets all location on hunt, puts them in dicty

		#hunt_last_updated = hunt.get("startTime")
		for usr in usrs:
			cur_usr_dict = User.find({"user_id":usr}).to_dict()
			tmp_id = cur_usr_dict['user_id']
			tmp_oauth = cur_usr_dict['token']
			hostname = "https://api.foursquare.com/v2/users/" + tmp + "/venuehistory?" + "?afterTimestamp= " + hunt_last_updated + "&oauth_token="+tmp_oauth
			f = urllib.urlopen(hostname)
			accResponse = f.read()
			accDict = json.loads(accResponse)
			venues = accDict['response']['venues']['items']

			for elt in venues:
				if elt["venue"]["id"] in dicty:
					#set list of places where he needs to go to show he has been there

					cur_active = cur_usr_dict['active_lsts']
					for x in range(len(cur_active)):
						
						if hunt_dict['_id']==cur_active[x][0]:
							winner = True
							for y in range(len(cur_active[x][1])):
								
								if elt["venue"]["id"] == cur_active[x][1][y][0]:
									cur_active[x][1][y] == cur_active[x][1][y][0],True
								if not cur_active[x][1][y][1]:
									winner = False

							if winner and not hunt.winner:
								hunt.winner = cur_usr_dict['user_id']

							usr.active_lsts = cur_active
							usr.save()

		hunt.start_time = int(time.time())
		hunt.save()
		#updates start time on all hunts
		#update start time w/ int(time.time())
		
if __name__ == '__main__':
	app.run()

