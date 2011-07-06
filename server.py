import cherrypy
from Cheetah.Template import Template
import urllib2
import urllib
import os
import sys
import json
import pymongo
from pymongo import Connection

base = os.path.abspath(os.path.dirname(sys.argv[0]))
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
#    @cherrypy.expose
#    @cherrypy.tools.json_in()
#    @cherrypy.tools.json_out()

    def index(self,code=""):
        cookie = cherrypy.request.cookie
        if "token" in cookie:
            raise cherrypy.InternalRedirect('../main.html')
        
#        db.authenticate(userID, pwd)
        authDict = {}
        authDict["client_id"] = "DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00"
        authDict["client_secret"] = "MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE"
        authDict["grant_type"] = "authorization_code"
        authDict["redirect_uri"] = "http://localhost:8080/auth/"
        authDict["code"] = code
        authDict["v"] = "20110525"
        urlencoding = urllib.urlencode(authDict)
        req = urllib2.urlopen("https://foursquare.com/oauth2/access_token",urlencoding)
        dicty = json.load(req)
        token = dicty["access_token"]
        
        
        get_user_dict = {"oauth_token":token, "v":"20110525"}
        urlencoding = urllib.urlencode(get_user_dict)
        
        req = urllib2.urlopen("https://api.foursquare.com/v2/users/self?"+urlencoding)

        dicty = json.load(req)

        userid = dicty["response"]["user"]["id"]
        first_name = dicty["response"]["user"]["firstName"].lower()
        last_name = dicty["response"]["user"]["lastName"].lower()
        email =  dicty["response"]["user"]["contact"]["email"]
        user_collection = db.Users
        
        usr = user_collection.find_one({"userid":userid})
        if usr:
            if usr["token"] == token:
                pass
            else:
                #updates with a new token
                user_collection.update({"userid":userid},{"$set":{"token":token}},safe=True)

        else:
            names = []
            if (first_name):
                stri = ""
                for elt in first_name:
                    stri += elt
                    names.append(stri)
                names.append(first_name)
            if (last_name):
                stri = ""
                for elt in last_name:
                    stri += elt
                    names.append(stri)
            user_collection.insert({"json":dicty,"token":token,"userid":userid,"hunts":[],"old_hunts":[],"active_hunts":[],"invited":[],"first":first_name,"last":last_name,"names":names,"email":email},safe=True)

        #set cookie
        cookie = cherrypy.response.cookie

        cookie['token'] = token
        cookie['token']['path'] = '/'
        cookie['token']['max-age'] = 3600

        #do we want to save first name? last name? username?
        fp = open('./static/main.html')
        return fp.read()


    index.exposed = True

class Invite(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def default(self):
        data = cherrypy.request.json
        if "userid" in data and data["userid"]:
            if "huntid" in data and data["huntiDs"]:
                email_addresses = []
                if "email" in data and data["email"]:
                    email_addresses.extend(data["email"])
                user_collection = db.Users
                user_collection.update({"userid":{"$in":data["userIds"]}},{"$addToSet":{"invited":{"$each":data["huntIds"]}}},safe=True)
                cursor = user_collection.find({"userid":{"$in":data["userIds"]}})
                email_addresses.extend([elt["email"] for elt in cursor])
                return email(email_addresses,data["huntIds"])
            else:
                return  {'status':'fail', \
                             'message':'No hunt name' \
                             }
        elif "email" in data and data["email"]:
            if "huntid" in data and data["huntid"]:
                return email(data["email"],data["huntid"])
            else:
                return email(data["email"])
        else:
            return   {'status':'fail', \
                          'message':'No users or email addresses' \
                          }
        return {'status':'ok'}

def email(email_addresses="",huntid=""):
    if email_addresses:
        if huntid:
            message = "Someone has invited you to a game!" + huntid
            return message
        else:
            message = "Would you like to join fourscav?  It's awesome!"
            return message
    else:
        return   {'status':'fail', \
                          'message':'No email addresses' \
                          }


class User(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()

    def lookup(self,name=""):
        if (name):
            user_collection = db.Users
            cursor = user_collection.find({"names":{"$all":name.lower().split(" ")}})
            lst = []
            for elt in cursor:
                elt.pop('_id')
                lst.append(elt)
            return {'status':'ok','data':lst}
        else:
            return  {'status':'fail', \
                                   'message':'Empty user name' \
                                   }

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

        return ({"status":"ok","data":huntjson})


    def name(self):
        cookie = cherrypy.request.cookie
        token = cookie['token'].value
        user_collection = db.Users
        usr = user_collection.find_one({"token":token})

        return ({"status":"ok","data":usr["json"]})

    hunts.exposed = True
    name.exposed = True

class Hunts(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()


    def lookup(self,name=""):
        if (name):
            hunt_collection = db.Hunts
            cursor = hunt_collection.find({"names":{"$all":name.lower().split(" ")}})
            lst = []
            for elt in cursor:
                elt.pop('_id')
                lst.append(elt)
            return {"status":"ok","data":lst}
        else:
            return  {'status':'fail', \
                                   'message':'Empty hunt name' \
                                   }
    def new(self):
        #this does the json parsing manually
        #cl = cherrypy.request.headers['Content-Length']
        #rawbody = cherrypy.request.body.read(int(cl))
        #obj = json.loads(rawbody)
        #return json.dumps(obj)
        data = cherrypy.request.json

        for val in ["name","places","desc"]:
            if val in data and data[val]:
                pass
            else:
                return {'status':'fail', \
                                       'message':'Please enter all required params', \
                                       'param':val \
                                       }
        tags = []
        name = data['name']
        places = data['places']
        desc = data['desc']
        if "tags" in data:
            tags = data["tags"]
                
        cookie = cherrypy.request.cookie
        token = cookie['token'].value
        user_collection = db.Users
        usr = user_collection.find_one({"token":token})
        venues = [(place,[]) for place in places]
        names = []
        prefixable = name.lower().split(" ")
        for word in prefixable:
            stri = ""
            for letter in word:
                stri += letter
                names.append(stri)
        new_hunt = {"users":[usr["userid"]],"venues":venues,"title":name,"rankings":[],"owner":usr["userid"],"names":names}
        hunts_collection = db.Hunts
        try:
            hunts_collection.insert(new_hunt,safe=True)
            del new_hunt['_id']
            return {'status':'ok',"data":new_hunt}
        except pymongo.errors.OperationFailure:
            return {'status':'fail', \
                                   'message':'Failed to insert' \
                                   }


    new.exposed = True

    def bullshit(self):
        tmp = '''
<html> <head><title>Sup</title></head>
<body>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js"></script>
        <script>
            var obj = JSON.stringify({
                name: "Title",
                desc: "Description",
                tags:[],
                places:['id1', 'id2']
            });
            $.ajax({
                type: 'POST',
                url: '/hunts/new',
                data: obj,
                success: function(data) { console.log(data); },
                contentType:"application/json; charset=utf-8",
                dataType:"json"
            });
        </script>
</body>
</html>
        '''


        return tmp
#    bullshit.exposed = True

    def default(self,id = "", action = "get", foursq = ""):
        if id == "":
            return "Empty id"
        if action == "get":
            #reach into mongo and get the hunt
            hunt_collection = db.Hunts #fetches a collection from mongo
            cur_hunt = hunt_collection.find_one({"_id":id}) #get the specified hunt
            return {"status":"ok","data":str(cur_hunt)}
        elif action == "join":
            #add member to hunt
            #this entails modifying hunt and member
            cookie = cherrypy.request.cookie
            token = cookie['token'].value

            user_collection = db.Users #fetches a collection from mongo
            user_collection.update({"token":token},{"$push":{"hunts":id},"$pull":{"invited":id}},safe=True)
            user = user_collection.find_one({"token":token})

            hunt_collection = db.Hunts #fetches a collection from mongo
            hunt_collection.update({"_id":id},{"$push":{"users":user["userid"]}},safe=True)
            '''
            elif action == "remove_tag":
            #reach into mongo and remove tag
            if foursq == "":
            return "need to give me a foursquare id"
            
            return "removing tag"
            
            elif action == "add_tag":
            #reach into mongo and add tag
            if foursq == "":
            return "need to give me a foursquare id"
            return "adding tag"
            '''



            return {"status":"ok","data":"joining hunt"}

        #do we even want this functionality?

        elif action == "remove_place":
            #reach into mongo and remove place
            if foursq == "":
                return {"status":"fail","message":"need to give me a foursquare id"}

            cookie = cherrypy.request.cookie
            token = cookie['token'].value

            user_collection = db.Users #fetches a collection from mongo
            user_collection.update({"hunts.hunt_id":id},{"$pull":{"hunts.venues":foursq}},safe=True)

            hunt_collection = db.Hunts #fetches a collection from mongo
            hunt_collection.update({"_id":id},{"$pull":{"venues":foursq}},safe=True)
            
            return {"status":"ok","message":"removing placing"}
        elif action == "add_place":
            #reach into mongo and add place
            if foursq == "":
                return {"status":"fail","message":"need to give me a foursquare id"}

            hunt_collection = db.Hunts #fetches a collection from mongo
            #inserts a new place in a hunt
            hunt_collection.update({"_id":id},{"$push":{"venues":foursq}},safe=True)

            return {"status":"ok","data":"adding place"}
        else:
            return {"status":"fail","message":"bad action!"}
            
        return "tmp"
    default.exposed = True

class Venues(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()

    def search(self,query="",lat="40.7",lng="-74"):
        "https://api.foursquare.com/v2/venues/search?ll=40.7,-74&client_id=CLIENT_ID&client_secret=CLIENT_SECRET"

        authDict = {}
        authDict["client_id"] = "DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00"
        authDict["client_secret"] = "MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE"
        authDict["ll"] = lat+","+lng

        authDict["query"] = query
        authDict["v"] = "20110625"
        
        urlencoding = urllib.urlencode(authDict)
        codestr = "https://api.foursquare.com/v2/venues/search?" + urlencoding

        req = urllib2.urlopen(codestr)
        return {"status":"ok","data": json.load(req)}

    search.exposed = True

class Logout(object):
    @cherrypy.expose
    def default(self):
        ask_cookie = cherrypy.request.cookie
        if "token" in ask_cookie:
            tell_cookie = cherrypy.response.cookie
            tell_cookie['token'] = ask_cookie['token']
            tell_cookie['token']['expires'] = 0
            
        index_t = open('static/index.tmpl', 'r')
        self.index_template = index_t.read()
        return str(Template(self.index_template))


class Index(object):
    invite = Invite()
    user = User()
    venues = Venues()
    auth = Auth()
    hunts = Hunts()
    logout = Logout()
    def default(self):
        index_t = open('static/index.tmpl', 'r')
        self.index_template = index_t.read()
        cookie = cherrypy.request.cookie
        if "token" in cookie:
            fp = open('./static/main.html')
            return fp.read()
#        else:
#            return "no cookie"
        return str(Template(self.index_template))
    default.exposed = True

#Server configuration
site_conf = \
    {'server.socket_host': '127.0.0.1',
     'server.socket_port': 8080,
     'error_page.404': os.path.join(base, "static/error.html")
    }


cherrypy.config.update(site_conf)

#App configuration
board_conf = \
    {
    '/':
        {
            'tools.staticdir.root':base,
            'tools.staticfile.root':base,
            },
    '/static':
        {'tools.staticdir.on':True,
         'tools.staticdir.dir':'static',
         'tools.staticdir.content_types': {'png': 'image/png',
                                           'css': 'text/css',
                                           'js':'application/javascript',}
         },
    '/css':
        {'tools.staticdir.on':True,
         'tools.staticdir.dir':'static/css',
         'tools.staticdir.content_types': {'png': 'image/png',
                                           'css': 'text/css',
                                           'js':'application/javascript',}
         },
    '/images':
        {'tools.staticdir.on':True,
         'tools.staticdir.dir':'static/images',
         'tools.staticdir.content_types': {'png': 'image/png',
                                           'css': 'text/css',
                                           'js':'application/javascript',}
         },
    '/js':
        {'tools.staticdir.on':True,
         'tools.staticdir.dir':'static/js',
         'tools.staticdir.content_types': {'png': 'image/png',
                                           'css': 'text/css',
                                           'js':'application/javascript',}
         },
    '/index.html':
        {
            'tools.staticfile.on':True,
            'tools.staticfile.filename':'static/index.html'
            },
    '/profiles':
        {
            'tools.staticfile.on':True,
            'tools.staticfile.filename':'static/profiles/index.html'
            }
    }

'''
    #The key 'database' is for book keeping and as of now doesnt effect anything
    'database': 
        {'type': 'mongodb',
         'host': 'localhost',
         'port': 0000,
        },
'''

cherrypy.quickstart(Index(),'/',config=board_conf)

