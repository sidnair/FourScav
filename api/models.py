from snakelegs.document import Document
from snakelegs.fields import *
import connection

class User(Document):
	fullname = StringField()
	token = StringField()
	user_id = IntField()
	
class Place(Document):
	pass
