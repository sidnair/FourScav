
//top-level name for the app
var fs = {};

//fs.userLocation = {};

//ACTUALLY LOAD THIS
fs.userLists = { };

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

fs.inlineEdit = function(node, type) {
  var originalHtml = node.html();
  var originalText = node.text();
  var options = $('<' + type + '>' + '</' + type + '>');
  options.val(node.text());
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
    node.html(originalHtml.replace(originalText, options.val()));
    node.remove(type);
    node.one('click', function() { fs.inlineEdit(node, type); });
  });
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
  var newyork = new google.maps.LatLng(40.69847032728747, -73.9514422416687);
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
      userLocation.lat = position.coords.latitude;
      userLocation.lng = position.coords.longitude;
      initialLocation = new google.maps.LatLng(userLocation.lat, userLocation.lng);
      map.setCenter(initialLocation);
    });
  }
};

fs.loadFirstList = function() {
  fs.loadListDisplay($('#listChoice option')[0].id);
};

$(document).ready(function() {
  fs.makeListDropDown(fs.userLists);
  fs.buildListCreater();
  fs.loadFirstList();
  fs.loadMaps();
});
