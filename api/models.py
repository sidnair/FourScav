from snakelegs.document import Document
from snakelegs.fields import *

class User(Document):
	fullname = StringField()
	token = StringField()
	user_id = IntField()
	active_lsts = ListField()
	dead_lsts = ListField()

class Place(Document):
	name = StringField()
	desc = StringField()
	tags = ListField()
	geo_lat = DecimalField()
	geo_long = DecimalField()
	fsq_id = IntField()

class Hunt(Document):
	creator = StringField()
	places = ListField()
	tags = ListField()
	users = ListField()
	winner = StringField()
	start_time = IntField()
	end_time = IntField()
