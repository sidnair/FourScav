import cherrypy
import urllib2
import urllib
import json
import pymongo
from pymongo import Connection

userID = 'admin'
pwd =  'mangolassi'
host = 'flame.mongohq.com'
port = 27071
dbName = 'fourscav'

#connection = Connection(host, port)
connection = Connection()
#db = connection[dbName]
db = connection['fourscav']

class Auth(object):
    def index(self,code=""):
#        db.authenticate(userID, pwd)
        authDict = {}
        authDict["client_id"] = "DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00"
        authDict["client_secret"] = "MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE"
        authDict["grant_type"] = "authorization_code"
        authDict["redirect_uri"] = "http://localhost:8080/auth/"
        authDict["code"] = code
        urlencoding = urllib.urlencode(authDict)
        req = urllib2.urlopen("https://foursquare.com/oauth2/access_token",urlencoding)
        dicty = json.load(req)
        token = dicty["access_token"]
        
        
        get_user_dict = {"oauth_token":token}
        urlencoding = urllib.urlencode(get_user_dict)
        
        req = urllib2.urlopen("https://api.foursquare.com/v2/users/self?"+urlencoding)

        dicty = json.load(req)

        userid = dicty["response"]["user"]["id"]

        user_collection = db.Users
        
        usr = user_collection.find_one({"userid":userid})
        if usr:
            if usr["token"] == token:
                pass
            else:
                #updates with a new token
                user_collection.update({"userid":userid},{"$set":{"token":token}})

        else:
            user_collection.insert({"json":dicty,"token":token,"userid":userid,"hunts":[],"old_hunts":[],"active_hunts":[]})

        #set cookie
        cookie = cherrypy.response.cookie

        cookie['token'] = token
        cookie['token']['max-age'] = 3600

        #do we want to save first name? last name? username?
        
        return dicty["response"]["user"]["firstName"]


    index.exposed = True


class User(object):
    def hunts(self):
        cookie = cherrypy.request.cookie
        token = cookie['token'].value
        user_collection = db.Users
        hunts_collection = db.Hunts

        user_hunts = user_collection.find_one({"token":token})["hunts"]


        hunts = {"user_hunts":user_hunts}

        huntjson = []

        for hunt in user_hunts:
            cur_hunt = hunts_collection.find_one({"huntid":hunt[0]})
            huntjson.append(cur_hunt["json"])
        hunts['json'] = huntjson

        return json.dumps(hunts)


    def name(self):
        cookie = cherrypy.request.cookie
        token = cookie['token'].value
        user_collection = db.Users
        usr = user_collection.find_one({"token":token})

        return json.dumps(usr["json"])

    hunts.exposed = True
    name.exposed = True

class Hunts(object):
    def new(self, **jsonText):
        return json.loads(jsonText);
        for val,key in [(name,0), (desc,1), (places,2)]:
            if not val:
                return json.dumps({'status':'fail', \
                                   'data':'Please enter all required params', \
                                   'param':key \
                                   })
        cookie = cherrypy.request.cookie
        token = cookie['token'].value
        user_collection = db.Users
        usr = user_collection.find_one({"token":token})

        venues = [(place,[]) for place in places]
        new_hunt = {"users":[usr["userid"]],"venues":venues,"title":name,"rankings":[],"owner":usr["userid"]}

        hunts_collection = db.Hunts
        try:
            hunts_collection.insert(new_hunt,safe=True)
            return json.dumps({'status':'ok',"data":new_hunt})
        except pymongo.errors.OperationFailure:
            return json.dumps({'status':'fail', \
                                   'data':'Failed to insert' \
                                   })
    new.exposed = True

    def bullshit(self):
        tmp = '''
<html> <head><title></title></head>
<body>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js"></script>
        <script>
          var obj = {
              name: "Title",
              desc: "Description",
              tags:[],
              places:['id1', 'id2']
          };
          str_obj = JSON.stringify(obj);
          simple_obj = { name: "name", desc: "desc" };
$.ajax({
  type: 'POST',
  url: '/hunts/new',
  data: str_obj,
  success: function(data) { console.log('here'); console.log(data); },
  contentType:"application/json; charset=utf-8",
  dataType:"json"
});
/*
          $.post('/hunts/new', obj, function(data, textStatus, jqXHR) {
              console.log(data);
             //on success, add stuff to list 
          });
*/
        </script>
</body>
</html>
        '''


        return tmp
    bullshit.exposed = True

    def default(self,id = "", action = "get", foursq = ""):
        if id == "":
            return "Empty id"
        if action == "get":
            return "getting name"
        elif action == "join":
            return "joining hunt"
        elif action == "remove_tag":
            if foursq == "":
                return "need to give me a foursquare id"
            return "removing tag"
        elif action == "add_tag":
            if foursq == "":
                return "need to give me a foursquare id"
            return "adding tag"
        elif action == "remove_place":
            if foursq == "":
                return "need to give me a foursquare id"
            return "removing placing"
        elif action == "add_place":
            if foursq == "":
                return "need to give me a foursquare id"
            return "adding place"
        else:
            return "bad action!"
            
        return "tmp"
    default.exposed = True

class Venues(object):
    def search(self):
        return "searching"
    search.exposed = True

class Index(object):
    user = User()
    venues = Venues()
    auth = Auth()
    hunts = Hunts()

    def index(self):
        return "hello world"
    index.exposed = True

cherrypy.quickstart(Index())

