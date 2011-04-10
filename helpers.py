from models import Place, User
import json

def add_place(list_id, fsq_id):
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
	place = Place(name = accName,desc = accDesc, tags = accTags, geo_lat = accLat, 
					geo_long = accLong)
	place.save()
	
def expand_hunt(hunt):
	d = {}
	d['creator'] = clean_userdict(User.find_one({'_id':hunt.creator}).to_dict())
	d['creator']['user_id'] = d['creator']['user_id'].encode('ascii')
	d['places'] = []
	for pid in hunt.places:
		place = Place.find_one({'_id':pid})
		if place != -1:
			place = place.to_dict()
			d['places'].append(place)
	d['tags'] = hunt.tags
	d['users'] = []
	for uid in hunt.users:
		user = User.find_one({'_id':uid})
		if user != -1:
			user = user.to_dict()
			user = clean_userdict(user)
			user['user_id'] = user['user_id'].encode('ascii')
			d['users'].append(user)
	d['start_time'] = hunt.start_time
	d['end_time'] = hunt.end_time
	if hunt._id!=[None]:
		d['_id'] = str(hunt._id).encode('ascii')
	else:
		d['_id'] = -1
		

	d['name'] = hunt.name.encode('ascii')
	d['desc'] = hunt.desc.encode('ascii')
	print(str(d))
	return d

def clean_userdict(userdict):
	userdict['fullname'] = userdict['fullname'].encode('ascii')
	userdict['token'] = userdict['token'].encode('ascii')
	for i, hid in enumerate(userdict['active_lsts']):
		userdict['active_lsts'][i] = str(hid).encode('ascii')
	for i, hid in enumerate(userdict['dead_lsts']):
		userdict['dead_lsts'][i] = str(hid).encode('ascii')

	if not userdict.get('_id'):
		userdict['_id'] = -1
	return userdict

def remove_place(list_id, fsq_id):
	hunt = Hunt.find_one({'_id' : list_id})
	place = Place.find_one({'fsqid' : fsq_id})
	hunt.places.remove(place._id)
	hunt.save()

