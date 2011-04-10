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
	
def expand_place(place):
	d 

def remove_place(list_id, fsq_id:
	hunt = Hunt.find_one({'_id' : list_id})
	place = Place.find_one({'fsqid' : fsq_id})
	hunt.places.remove(place._id)
	hunt.save()

