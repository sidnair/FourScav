from snakelegs.document import Document
from snakelegs.fields import *
import connection

class User(Document):
	username = StringField()
	token = StringField()
	active_lsts = ListField()
	dead_lsts = ListField()
	
class Place(Document):
	name = StringField()
	desc = StringField()
	tags = ListField()
	geo_lat = DoubleField()
	geo_long = DoubleField()

class Hunt(Document):
	creator = StringField()
	places = ListField()
	tags = ListField()
	users = ListField()
	winner = StringField()
	start_time = IntField()
	end_time = IntField()
