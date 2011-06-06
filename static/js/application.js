//top-level name for the app
var fs = {};

//ACTUALLY LOAD THIS
fs.userLists = { };

//SANITIZE DATA
fs.loadLists = function(serverLists) {
  for(var i = 0, len = serverLists.length; i < len; i++) {
    var currentServerList = serverLists[i];
    var formattedList = {};
    formattedList.id = currentServerList._id;
    formattedList.desc = currentServerList.desc;
    formattedList.name = currentServerList.name;
    formattedList.places = currentServerList.places;
    fs.userLists[formattedList.id] = formattedList;
  }
}

/* Used to store information related to the maps display. This includes user
 * location and map marker information
 */
fs.maps = {};
fs.maps.userLocation = {};
fs.maps.storedMarkers = [];
fs.maps.NEW_YORK_LAT = 40.69847032728747;
fs.maps.NEW_YORK_LNG = -73.9514422416687;
fs.maps.clearMarkers = function() {
  for(var m in fs.maps.storedMarkers) {
    fs.maps.storedMarkers[m].setVisible(false);
  }
  fs.maps.storedMarkers = [];
}

fs.maps.addMarker = function(map, lat, lng, name, desc) {
  var loc = new google.maps.LatLng(lat, lng);
  var marker = new google.maps.Marker({
      position: loc, 
      map: map, 
      title: name
  });
  var infoWindow = new google.maps.InfoWindow({ 
    content: name + ' - ' + desc
  }); 
  google.maps.event.addListener(marker, 'click', function() { 
    infoWindow.open(map, marker); 
  }); 
  fs.maps.storedMarkers.push(marker);
};

fs.makeListDropDown = function(list) {
  $.each(list, function(key, element) {
      $('#listChoice').append('<option id="' + element.id + '">' + element.name  + '</option>');
  });
  $('#listChoice').append('<option id="new">Make New Hunt!</option>');
  $('#listChoice').change(function(e) {
    fs.loadListDisplay($('option:selected', this)[0].id);
  });
  $('#listChoice').selectmenu({style:'dropdown', maxHeight:350, width: 200});
}

fs.loadListDisplay = function(listId) {
  //it is an existing list
  if(fs.userLists[listId]) {
    $('#newListMaker').hide();
    $('#activeListTitle').html(fs.userLists[listId].name);
    $('#activeListDescription').html(fs.userLists[listId].desc);
    $('#activeListInfo').show();
    $('#searchAndStandings').hide();
    $('#activeListTable').html('');
    /*
    $('#search').hide();
    $('#standings').show();
    */
  } else {
    //it is a new list
    $('#activeListInfo').hide();
    $('#newListMaker').show();
    $('#searchAndStandings').show();
    /*
    $('#standings').hide();
    $('#search').show();
    */
  }
}

fs.buildListCreater = function(title, display) {
  var title = $('#newListTitle');
  title.html('<h1>My New List</h1>')
  //fs.inlineEdit(title, $('#newListMaker'), 'input');
      .one('click', function() { fs.inlineEdit(title, 'input'); });
  fs.inlineHover(title);
  var desc = $('#newListDescription');
  desc.html('<p>Enter a description here.</p>')
  //fs.inlineEdit(desc, $('#newListMaker'), 'input');
      .one('click', function() { fs.inlineEdit(desc, 'textarea'); })
  fs.inlineHover(desc);
  $('button').button();
}

fs.inlineEdit = function(node, type, holderText) {
  var originalHtml = node.html();
  var originalText = node.text();
  holderText = holderText || originalText;
  var options = $('<' + type + '>' + '</' + type + '>');
  options.val(originalText);
  node.html('');
  node.append(options);
  //TODO - add cancel button
  //TODO - add done button
  if(type === 'input') {
    options.keydown(function(e) {
      if(e.keyCode === 13) {
        options.blur();
      }
    });
  }
  options.blur(function() {
    if(options.val() === '') {
      options.val(holderText);
    }
    node.html(originalHtml.replace(originalText, options.val()));
    node.remove(type);
    node.one('click', function() { fs.inlineEdit(node, type, holderText); });
  });
  options.focus(function() {
      if(originalText === holderText) {
        options.val('');
      }
  });
  options.focus();
}

fs.inlineHover = function(node) {
  var oldColor = node.attr('background') || 'white';
  node.mouseover(function() {
      $(this).animate({background: 'yellow'}, 'fast');
  });
  node.mouseleave(function() {
      $(this).animate({background: oldColor }, 'fast');
  });
}

fs.loadMaps = function() {
  var newyork = new google.maps.LatLng(fs.maps.NEW_YORK_LAT, fs.maps.NEW_YORK_LNG);
  var myOptions = {
    zoom: 14,
    center: newyork,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoomControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER
    },
    mapTypeControl: false,
    panControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER
    },
    streetViewControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER
    }
  }

  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  //use html5 geolocation if possible - otherwise, it stays at default of new york
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      fs.map.userLocation.lat = position.coords.latitude;
      fs.map.userLocation.lng = position.coords.longitude;
      initialLocation = new google.maps.LatLng(fs.userLocation.lat, fs.userLocation.lng);
      map.setCenter(initialLocation);
    });
  } else {
    fs.map.userLocation.lat = fs.NEW_YORK_LAT;
    fs.maps.userLocation.lng = fs.NEW_YORK_LNG;
  }
  fs.map = map;
};

fs.loadFirstList = function() {
  fs.loadListDisplay($('#listChoice option')[0].id);
};

fs.searchVenue = function(query) {
  //don't proceed if query is undefined, empty, etc
  if(!query) {
    return;
  }
  $.post('/venues/search', {
      query:query,
      lat:fs.maps.userLocation.lat,
      'long':fs.maps.userLocation.lng
  }, function(data, textStatus, jqXHR) {
    var agg_results = [];
    var k = 0;
    var result = $.parseJSON(data);
    if(result.response && result.response.groups && result.response.groups[0]) {
      var keys = [0, 1];
      for(var i in keys) {
        var items = result.response.groups[i] && result.response.groups[i].items;
        if(items) {
          for(var j = 0, l = items.length; j < l; j++) {
            if(k < 6) {
              agg_results[k] = items[j];
              k++;
            }
          }
        }
      }
      fs.renderResults(agg_results);
    }
  });
}

fs.renderListPlaces = function(places, list) {
  $('#activeListTable').html('');
  fs.renderResults(places, $('#activeListTable'), true);
 // for(var i = 0, l = places.length; i < l; i++) {
   // fs.addMarker(places[i], places[i].lat, places[i].lng, places[i].name, places[i].desc);
    //fs.addMarker(places[i], places[i].location.lat, places[i].location.lng, list);
//  }
};

fs.renderResults = function(result_list, resultListDiv, shouldNotAdd) {
  if(!resultListDiv) {
    //cache results div
    resultListDiv = $('#searchResults');
    //clear prexisting results
    resultListDiv.html('<table></table>');
  }
  for(var i = 0, l = result_list.length; i < l; i++) {
    var result = result_list[i];
    var resultDiv = $('<tr class="searchResult"></tr>');
    var addButton = $('<td><span id="' + result.id + 'Button" class="searchButton"></span></td>');
    resultDiv.append(addButton);
    resultDiv.append($('<td id="' + result.id + '" class="searchResultText">' + result.name + '</td>'));
    for(var j = 0, l2 = result.categories.length; j < l2; j++) {
      var cat = result.categories[j];
      var icon = cat.icon;
      var name = cat.name;
      resultDiv.append('<td><img src="' + icon + '" alt="' + name + '" class="catIcon" /></td>');
    }
      resultListDiv.append(resultDiv);
    if(!shouldNotAdd) {
      $('#' + result.id + 'Button').button({
  icons: {primary:'ui-icon-plusthick'},
        text: false
      });
      (function() {
        var clickF = (function(resultDiv) {
            return function() {
              fs.addResult(resultDiv, result.id + 'Button');
            };
        })(resultDiv);
        addButton.click(function() {
            clickF();
        });
      })();
    }
  }
}

fs.addResult = function(resultNode, oldId) {
  var clonedNode = resultNode.clone();
  $('#newListTable').append(clonedNode);
  $($('td', clonedNode)[0]).remove();
  (function() {
    var removeButton = $('<td><span id="' + oldId + 'Remove" class="searchButton"></span></td>');
    clonedNode.prepend(removeButton);
    removeButton.button({
        icons: {primary:'ui-icon-minusthick'},
        text: false
    });
    removeButton.click(function() {
        clonedNode.remove();
    });
  })();
}

fs.addSearchEvents = function() {
  var runSearch = function() { fs.searchVenue($('#searchBar').val()); };
  $('#searchBar').keydown(function(e) {
    if(e.keyCode === 13) {
      runSearch();
    }
  });
  $('#searchButton').click(function(e) {
    runSearch();
  });
}

fs.addSubmitEvent = function() {
  $('#submitListButton').click(function() {
      var enteredPlaces = [];
      $('#newListTable tr').each(function(index, element) {
        fullId = $('td', element)[1].id
        enteredPlaces.push(fullId);
      });
      var obj = {
          name:$('#newListTitle').text(),
          desc:$('#newListDescription').text(),
          tags:[],
          places:enteredPlaces
      };
      $.post('/list/new', obj, function(data, textStatus, jqXHR) {
          console.log(data);
         //on success, add stuff to list 
      });
      /*
      $('#newListTable tr').each(function(index, element) {
        console.log($('td span', element));
        $('td span', element).each(function(i, e) {
          var fullId = e.id;
          if(fullId && fullId.indexOf('ButtonRemove') > 0) {
            enteredPlaces.push(fullId.replace('ButtonRemove', ''));
          }
        });
      });
      */
  });
}

$(document).ready(function() {
  fs.makeListDropDown(fs.userLists);
  fs.buildListCreater();
  fs.loadFirstList();
  fs.loadMaps();
  fs.addSearchEvents();
  fs.addSubmitEvent();
});
