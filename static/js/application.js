//top-level name for the app
var fs = {};
fs.userLists = {};
fs.ui = {};
fs.util = {};

fs.util.metersToMiles = function(meters) {
  var miles = meters * 0.000621371192;
  miles *= 10;
  miles = Math.round(miles) / 10;
  return miles;
};

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

fs.ui.makeSmallButton = function(text, cb) {
  return $('<button class="smallButton">' + text + '</button>')
    .button()
    .click(cb);
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
  var $target = $(event.target);
  if ($target.is('button') || $target.hasClass('ui-button-text')) {
    restoreInlineListener();
    return;
  }
  var originalHtml = node.html(),
      originalText = node.text(),
      editableNode = $('<' + type + '>' + '</' + type + '>');
  editableNode.val(originalText);
  node.html('');
  node.append(editableNode, '<br />', fs.ui.makeSmallButton('Cancel', undoEdits),
      fs.ui.makeSmallButton('Done', saveEdits));
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

fs.searchVenue = function(query, cb) {
  //don't proceed if query is undefined, empty, etc
  if (!query) {
    fs.ui.displayError('You must enter a query.');
    return;
  }
  $.get('/venues/search/', {
      query:query,
      lat:fs.maps.userLocation.lat,
      lng:fs.maps.userLocation.lng
  }, function(data, textStatus, jqXHR) {
    console.log(data);
    var result = $.parseJSON(data);
    fs.renderResults(result.response && result.response.venues);
    cb();
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

fs.renderResults = function(resultList, resultListDiv, shouldNotAdd) {
  resultListDiv = resultListDiv || $('#searchResultsDiv');
  var resultListTable = $('table', resultListDiv);
  if(!resultList || resultList.length === 0) {
    resultListTable.html('<tr><td>No results found.</td></tr>');
  } else {
    resultListTable.append($('<tr class="searchResult tableHeading">' +
        '<td></td>' +
        '<td>Name</td>' +
        '<td>Distance</td>' +
        '</tr>'));
    var i,
        resultListLen = resultList.length,
        j,
        resultCatLen;
    for (i = 0; i < resultListLen; i++) {
      var result = resultList[i],
          resultDiv = $('<tr class="searchResult"></tr>'),
          addButton = $('<td><span id="' + result.id + 'Button" class="searchButton"></span></td>'),
          distance;
      resultDiv.append(addButton);
      resultDiv.append($('<td id="' + result.id + '" class="searchResultText">' + result.name + '</td>'));
      distance = fs.util.metersToMiles(result.location.distance);
      resultDiv.append($('<td id="' + result.id + 'Distance' +
            '" class="searchResultText">' + distance + '</td>'));
      for (j = 0, resultCatLen = result.categories.length; j < resultCatLen;
          j++) {
        var cat = result.categories[j],
            icon = cat.icon,
            name = cat.name;
        resultDiv.append('<td><img src="' + icon + '" alt="' + name + '" class="catIcon" /></td>');
      }
      resultListTable.append(resultDiv);
      if (!shouldNotAdd) {
        $('#' + result.id + 'Button').button({
          icons: {primary:'ui-icon-plusthick'},
          text: false
        });
        // self-invoking anonymous function here so that it accesses the current
        // result rather than always accessing the last once (since closures are
        // by reference)
        (function(resultDiv, resultId) {
          addButton.click(function() {
            fs.addResult(resultDiv, resultId + 'Button')
          });
        })(resultDiv, result.id);
      }
    }
  }
  if (!resultListDiv.is(':visible')) {
    resultListDiv.slideDown('slow');
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
    var runSearch = function(query) {
      lastSearchVal = query || $('#searchBar').val();
      fs.searchVenue(lastSearchVal, function() {
        $('#toggleResultsButton').button('enable');
      });
    };
    var lastSearchVal;
    $('#searchButton').one('click', function(e) {
      var query = $('#searchBar').val();
      if (query !== lastSearchVal) {
        runSearch(query);
      } else if (!$('#toggleResultsButton').text() == 'Show') {
        $('#toggleResultsButton').click();
      }
    });
    $('#searchBar').keydown(function(e) {
      if (e.keyCode === 13) {
        runSearch();
      }
    });
  }

  function configureToggleResultsButton() {
    $('#toggleResultsButton').button('disable');
    $('#toggleResultsButton').click(function() {
      $('#searchResultsDiv').slideToggle('slow', function() {
          $('#toggleResultsButton').text() == 'Show' ?
            $('#toggleResultsButton span').text('Hide') :
            $('#toggleResultsButton span').text('Show');
      });
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
  configureToggleResultsButton();
});
