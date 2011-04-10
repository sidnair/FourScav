class ConfigData:
	clientID="DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00"
	clientSecret="MOBSNY4L5INCORUP1YPS4W3YYINAKSPWXLFSMZWYZUNNH4AE"

class apiURL:
	authorizeURL="https://foursquare.com/oauth2/authorize"
	oauthCallbackURL="http://localhost:8080/auth/"
	getCodeURL=("https://foursquare.com/oauth2/authenticate?client_id=%s&response_type=code&redirect_uri=%s" % (ConfigData.clientID,oauthCallbackURL) )
	getTokenURL=("https://foursquare.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=" % (ConfigData.clientID, ConfigData.clientSecret, oauthCallbackURL))

