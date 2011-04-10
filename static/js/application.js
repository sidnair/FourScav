//top-level name for the app
var fs = {};
fs.userLocation = {};

//ACTUALLY LOAD THIS
fs.userLists = { };

fs.NEW_YORK_LAT = 40.69847032728747;
fs.NEW_YORK_LNG = -73.9514422416687;

//dummy load
(function() {
  //DUMMMY DATA GENERATION
  list0 = {
        name: 'foo',
        id: '023q4q',
        desc: 'lorem ipsum'
  };

  list1 = {
        name: 'bar',
        id: '234134sdf',
        desc: 'lorem ipsum 2'
  };

  list2 = {
        name: 'baz',
        id: '23dasfsa',
        desc: 'lorem ipsum 3'
  };

  dummy = [list0, list1, list2];

  for(var i in dummy) {
    var list = dummy[i];
    fs.userLists[list.id] = list;
  }

})();


//SANITIZE DATA
fs.loadLists = function() {
}

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
  if(fs.userLists[listId]) {
    $('#newListMaker').hide();
    $('#activeListTitle').html(fs.userLists[listId].name);
    $('#activeListDescription').html(fs.userLists[listId].desc);
    $('#activeListInfo').show();
  } else {
    $('#activeListInfo').hide();
    $('#newListMaker').show();
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
  var oldColor = node.attr('backgroundColor') || 'white';
  node.mouseover(function() {
      $(this).animate({backgroundColor: 'yellow'}, 'fast');
  });
  node.mouseleave(function() {
      $(this).animate({backgroundColor: oldColor }, 'fast');
  });
}

fs.loadMaps = function() {
  var newyork = new google.maps.LatLng(fs.NEW_YORK_LAT, fs.NEW_YORK_LNG);
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
      fs.userLocation.lat = position.coords.latitude;
      fs.userLocation.lng = position.coords.longitude;
      initialLocation = new google.maps.LatLng(fs.userLocation.lat, fs.userLocation.lng);
      map.setCenter(initialLocation);
    });
  } else {
    fs.userLocation.lat = fs.NEW_YORK_LAT;
    fs.userLocation.lng = fs.NEW_YORK_LNG;
  }
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
      lat:fs.userLocation.lat,
      'long':fs.userLocation.lng
  }, function(data, textStatus, jqXHR) {
  console.log($.parseJSON(data));
    var agg_results = [];
    var k = 0;
    var result = $.parseJSON(data);
    if(result.response && result.response.groups && result.response.groups[0]) {
      var keys = [0, 1];
      for(var i in keys) {
        var items = result.response.groups[i].items;
        for(var j = 0, l = items.length; j < l; j++) {
          if(k < 11) {
            agg_results[k] = items[j];
            k++;
          }
        }
      }
      fs.renderResults(agg_results);
    }
  });
}

fs.renderResults = function(result_list) {
  //cache results div
  resultListDiv = $('#searchResults');
  //clear prexisting results
  resultListDiv.html('<table></table>');
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
    $('#' + result.id + 'Button').button({
icons: {primary:'ui-icon-plusthick'},
      text: false
    });
    (function() {
      var clickF = (function(resultDiv) {
          return function() {
            fs.addResult(resultDiv);
          };
      })(resultDiv);
      addButton.click(function() {
          clickF();
      });
    })();
  }
}

fs.addResult = function(resultNode) {
  var clonedNode = resultNode.clone();
  $('#newListTable').append(clonedNode);
  var oldAdd = $($('td', clonedNode)[0])
  var oldId = oldAdd.id;
  console.log(oldId);
  oldAdd.remove();
  var removeButton = $('<td><span id="' + oldId + '" class="searchButton"></span></td>');
  resultNode.prepend(removeButton);
  $('#' + result.id + 'Button').button({
      icons: {primary:'ui-icon', secondary:'ui-icon-plusthick'},
      text: false
  });
  removeButton.click(function() {
      $(this).remove();
  });
  //change icon to remove
  //clone the result node (row) and paste it
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

$(document).ready(function() {
  fs.makeListDropDown(fs.userLists);
  fs.buildListCreater();
  fs.loadFirstList();
  fs.loadMaps();
  fs.addSearchEvents();
});
