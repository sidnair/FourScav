
class auth:
	def GET(self):
		params = urllib.urlencode({'client_id' : 'DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00', 'client_secret' : 'MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE', 'grant_type' : 'authorization_code', 'redirect_uri' : 'http://localhost:8080/auth/', 'code' : web.input().code })

		hostname = "https://foursquare.com/oauth2/access_token?" + params
		f = urllib.urlopen(hostname)
		accResponse = f.read()
		accDict = json.loads(accResponse)
		accToken = accDict["access_token"]
		return accToken 
