
//top-level name for the app
var fs = {};

//ACTUALLY LOAD THIS
fs.userLists = { };

/*
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

//dummy load
(function() {
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
    $('#listChoice').prepend('<option id="' + element.id + '">' + element.name  + '</option>');
  });
  $('#listChoice').change(function(e) {
      fs.loadListDisplay($('option:selected', this)[0].id);
    } 
  );
  $('#listChoice').selectmenu({style:'dropdown', maxHeight:350, width: 200});
}
*/

fs.loadListDisplay = function(listId) {
  if(fs.userLists[listId]) {
    $('#activeListTitle').html(fs.userLists[listId].name);
    $('#activeListDescription').html(fs.userLists[listId].desc);
    //console.log(fs.userLists[listId]);
  } else {
    $('#activeListTitle').html('');
    $('#activeListDescription').html('');
  }
}

fs.loadMaps = function() {
  var myLatlng = new google.maps.LatLng(-34.397, 150.644);
  var myOptions = {
    zoom: 14,
    center: myLatlng,
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
  // Try W3C Geolocation (Preferred)
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
      map.setCenter(initialLocation);
    }, function() {
      handleNoGeolocation();
    });
  } else {
    handleNoGeolocation();
  }
  
  function handleNoGeolocation() {
    var newyork = new google.maps.LatLng(40.69847032728747, -73.9514422416687);
    map.setCenter(newyork);
  }

}













$(document).ready(function() {
  $('#listChoice').selectmenu({style:'dropdown', maxHeight:350, width: 200});
  //fs.makeListDropDown(fs.userLists);
  //fs.loadMaps();
});
