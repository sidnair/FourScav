from snakelegs.document import Document
from snakelegs.fields import *
import connection

class User(Document):
	username = StringField()
	token = StringField()
	
