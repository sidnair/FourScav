$('#loginButtonLink').click(function() {
    var base_url = window.location.href.replace('static/index.html', '')
        .replace('static/', '').replace('static','').replace('index.html', '');
    var foursquare_url = 'https://foursquare.com/oauth2/authenticate?client_id=DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00&response_type=code&redirect_uri=http://localhost:8080/auth/';
    /*
    var foursquare_url = 'https://foursquare.com/oauth2/authenticate?' +
        'client_id=DQCCND5KOFCIYVQXB3QX4GHJAR4AH4OHTQAM21JD0OFY4J00' +
        '&response_type=code&redirect_uri=' + base_url + 'auth/';
    */

    window.location.href = foursquare_url;
});
$('#loginButtonLink').addClass('clickable');
