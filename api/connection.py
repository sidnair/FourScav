from pymongo import Connection

mongo = Connection('flame.mongohq.com', 27058)['4sqav']
mongo.authenticate('4sqav', 'hacknyspring2011')
