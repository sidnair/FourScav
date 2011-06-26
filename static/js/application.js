//top-level name for the app
var fs = {};
fs.userLists = {};
fs.ui = {};

fs.ui.displayError = function(msg) {
  alert(msg);
};

//TODO: SANITIZE DATA
fs.loadLists = function(serverLists) {
  function formatList() {
    return {
      id: currentServerList._id,
      desc: currentServerList.desc,
      name: currentServerList.name,
      places: currentServerList.places
    };
  }
  $.each(serverLists, function(ind, el) {
      var formatted = formatList(el);
      fs.userLists(formatted.id) = formatted;
  });
};

/* 
 * Used to store information related to the maps display. This includes user
 * location and map marker information
 */
fs.maps = {
  userLocation: {},
  storedMarkers: [],
  NEW_YORK_LAT: 40.69847032728747,
  NEW_YORK_LNG: -73.9514422416687,
  /*
   * Remove the markers from the map. The markers will no longer be stored.
   */
  clearMarkers: function() {
    $.each(fs.maps.storedMarkers, function(index, element) {
        element.setVisible(false);
    });
    fs.maps.storedMarkers = [];
  },

  //TODO: see old implementation, make sure the changes are okay
  /*
   * Add a marker to the map. Pass a hash with the arguments:
   *  lat: latitutude
   *  lng: longitude
   *  name: name..
   *  desc: description
   */
  addMarker: function(args) {
    var lat = args.lat,
        lng = args.lng,
        name = args.name,
        desc = args.desc,
        map = fs.maps.map,
        loc = new google.maps.LatLng(lat, lng),
        marker = new google.maps.Marker({
            position: loc, 
            map: map, 
            title: name
        }),
        infoWindow = new google.maps.InfoWindow({ 
          content: name + ' - ' + desc
        }); 
    google.maps.event.addListener(marker, 'click', function() { 
      infoWindow.open(map, marker);
    }); 
    fs.maps.storedMarkers.push(marker);
  }
};

fs.loadListDisplay = function(listId) {
  //an existing list
  if (fs.userLists[listId]) {
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
    //new list
    $('#activeListInfo').hide();
    $('#newListMaker').show();
    $('#searchAndStandings').show();
    /*
    $('#standings').hide();
    $('#search').show();
    */
  }
};

fs.ui.makeButton = function(text, cb) {
  var button = $('<button>' + text + '</button>');
  if (cb) {
    button.click(cb);
  }
  return button;
};

/*
 * Allows for inline editing.
 *
 * node: should be jQuery wrapped DOM element
 * type: html type of the element you want to display. This should be input or
 * textarea.
 * holderText (optional): text to display when someone clicks on the text to
 * edit.
 *
 */
fs.ui.inlineEdit = function(event, node, type, holderText) {
  function saveEdits() {
    // if it becomes blank, they can't edit it any more, so do this to prevent
    // the text from becoming empty
    if (editableNode.val() === '') {
      editableNode.val(holderText || originalText);
    }
    node.html(originalHtml.replace(originalText, editableNode.val()));
    restoreInlineListener();
  }

  function undoEdits() {
    node.html(originalHtml);
    restoreInlineListener();
  }

  function restoreInlineListener() {
    node.one('click', function(e) { fs.ui.inlineEdit(e, node, type, holderText); });
  }

  if ($(event.target).is('button')) {
    restoreInlineListener();
    return;
  }
  var originalHtml = node.html(),
      originalText = node.text(),
      editableNode = $('<' + type + '>' + '</' + type + '>');
  editableNode.val(originalText);
  node.html('');
  node.append(editableNode, '<br />', fs.ui.makeButton('Cancel', undoEdits),
      fs.ui.makeButton('Done', saveEdits));
  //only add listener for enter to input -- don't add to textarea since they
  //should be able to make multiline edits
  if (type === 'input') {
    editableNode.keydown(function(e) {
      //enter
      if (e.keyCode === 13) {
        saveEdits();
      }
    });
  }
  editableNode.one('focus', function() {
    if (holderText && originalText === holderText) {
      editableNode.val('');
    }
  });
  editableNode.focus();
};

/*
fs.ui.inlineHover = function(node) {
  node.addClass('editable');
  var oldColor = node.attr('background') || 'white';
  node.mouseover(function() {
      $(this).
      css({background: '#F7FE2E'});
  });
  node.mouseleave(function() {
      $(this).css({background: oldColor });
  });
};
*/

/*
fs.util = {};
fs.util.mapToGet = function(obj) {
  var str_arr = ['?'];
  for (var i in obj) {
    if (str_arr.length === 1) {
      str_arr.push([i, '=', obj[i]].join(''));
    } else {
      str_arr.push(['&', i, '=', obj[i]].join(''));
    }
  }
  return str_arr.join('');
};
*/

fs.searchVenue = function(query) {
  //don't proceed if query is undefined, empty, etc
  if (!query) {
    fs.ui.displayError('You must enter places');
    return;
  }
  $.get('/venues/search/', {
      query:query,
      lat:fs.maps.userLocation.lat,
      lng:fs.maps.userLocation.lng
  }, function(data, textStatus, jqXHR) {
    console.log(data);
    var agg_results = [];
    var k = 0;
    var result = $.parseJSON(data);
    if (result.response && result.response.groups && result.response.groups[0]) {
      var keys = [0, 1];
      for (var i in keys) {
        var items = result.response.groups[i] && result.response.groups[i].items;
        if (items) {
          for (var j = 0, l = items.length; j < l; j++) {
            if (k < 6) {
              agg_results[k] = items[j];
              k++;
            }
          }
        }
      }
      fs.renderResults(agg_results);
    }
  });
};

fs.renderListPlaces = function(places, list) {
  $('#activeListTable').html('');
  fs.renderResults(places, $('#activeListTable'), true);
 // for (var i = 0, l = places.length; i < l; i++) {
   // fs.addMarker(places[i], places[i].lat, elaces[i].lng, places[i].name, places[i].desc);
    //fs.addMarker(places[i], places[i].location.lat, places[i].location.lng, list);
//  }
};

fs.renderResults = function(result_list, resultListDiv, shouldNotAdd) {
  if (!resultListDiv) {
    //cache results div
    resultListDiv = $('#searchResults');
    //clear prexisting results
    resultListDiv.html('<table></table>');
  }
  for (var i = 0, l = result_list.length; i < l; i++) {
    var result = result_list[i];
    var resultDiv = $('<tr class="searchResult"></tr>');
    var addButton = $('<td><span id="' + result.id + 'Button" class="searchButton"></span></td>');
    resultDiv.append(addButton);
    resultDiv.append($('<td id="' + result.id + '" class="searchResultText">' + result.name + '</td>'));
    for (var j = 0, l2 = result.categories.length; j < l2; j++) {
      var cat = result.categories[j];
      var icon = cat.icon;
      var name = cat.name;
      resultDiv.append('<td><img src="' + icon + '" alt="' + name + '" class="catIcon" /></td>');
    }
      resultListDiv.append(resultDiv);
    if (!shouldNotAdd) {
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
};

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
};


$(document).ready(function() {
  function addSearchEvents() {
    var runSearch = function() { fs.searchVenue($('#searchBar').val()); };
    $('#searchBar').keydown(function(e) {
      if (e.keyCode === 13) {
        runSearch();
      }
    });
    $('#searchButton').click(function(e) {
      runSearch();
    });
  }

  function addSubmitEvent() {
    $('#submitListButton').click(function() {
        var enteredPlaces = [];
        $('#newListTable tr').each(function(index, element) {
          fullId = $('td', element)[1].id
          enteredPlaces.push(fullId);
        });
        if (enteredPlaces.length === 0) {
          fs.ui.displayError('You must enter places');
          return;
        }
        var obj = {
            name: $('#newListTitle').text(),
            desc: $('#newListDescription').text(),
            tags: [],
            places: enteredPlaces
        };
        $.post('/hunts/new', obj, function(data, textStatus, jqXHR) {
            console.log(data);
           //on success, add stuff to list 
        });
        /*
        $('#newListTable tr').each(function(index, element) {
          console.log($('td span', element));
          $('td span', element).each(function(i, e) {
            var fullId = e.id;
            if (fullId && fullId.indexOf('ButtonRemove') > 0) {
              enteredPlaces.push(fullId.replace('ButtonRemove', ''));
            }
          });
        });
        */
    });
  }

  /* Makes a select menu out of the list provided. The list elements should have 
   * id and name properties. This represents the list of hunts in which the user
   * is participating. The option to create a new hunt is automatically added.
   */
  function makeListDropDown(list) {
    //TODO: fetch list from server
    //$.ajax
    //TODO: this will be the callback
    (function() {
      //store data in fs.userLists
      buildDropDownFromList(fs.userLists);
    })();

    function buildDropDownFromList() {
      $.each(list, function(key, element) {
          $('#listChoice').append('<option id="' + element.id + '">' + element.name
              + '</option>');
      });
      $('#listChoice').append('<option id="new">Make New Hunt!</option>');
      $('#listChoice').change(function(e) {
        fs.loadListDisplay($('option:selected', this)[0].id);
      });
      $('#listChoice').selectmenu({style:'dropdown', maxHeight:350, width: 200});
    };
  }

  function buildListMaker(title, display) {
    var title = $('#newListTitle');
    title.html('<h1>My New List</h1>')
        .one('click', function(e) { fs.ui.inlineEdit(e, title, 'input'); });
    var desc = $('#newListDescription');
    desc.html('<p>Enter a description here.</p>')
        .one('click', function(e) { fs.ui.inlineEdit(e, desc, 'textarea'); })
    $('button').button();
  }

  function loadMaps() {
    var newyork = new google.maps.LatLng(fs.maps.NEW_YORK_LAT,
          fs.maps.NEW_YORK_LNG),
        myOptions = {
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
    };

    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    //use html5 geolocation if possible - otherwise, it stays at default of new york
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        fs.maps.userLocation.lat = position.coords.latitude;
        fs.maps.userLocation.lng = position.coords.longitude;
        initialLocation = new google.maps.LatLng(fs.maps.userLocation.lat, fs.maps.userLocation.lng);
        map.setCenter(initialLocation);
      });
    } else {
      fs.map.userLocation.lat = fs.NEW_YORK_LAT;
      fs.maps.userLocation.lng = fs.NEW_YORK_LNG;
    }
    fs.maps.map = map;
  };

  makeListDropDown(fs.userLists);
  buildListMaker();
  //load the first list
  fs.loadListDisplay($('#listChoice option')[0].id);
  loadMaps();
  addSearchEvents();
  addSubmitEvent();
});
