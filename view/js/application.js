//top-level name for the app
var fs = {};

//ACTUALLY LOAD THIS
fs.userLists = { };

/* DUMMMY DATA GENERATION */
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
    $('#listChoice').append('<option id="' + element.id + '">' + element.name  + '</option>');
  });
  $('#listChoice').change(function(e) {
    fs.loadListDisplay($('option:selected', this)[0].id);
  } 
  );
}

fs.loadListDisplay = function(listId) {
  $('#activeListTitle').html(fs.userLists[listId].name);
  $('#activeListDescription').html(fs.userLists[listId].desc);
  //console.log(fs.userLists[listId]);
}

var myOptions = {
  zoom: 8,
  center: new google.maps.LatLng(-34.397, 150.644),
  mapTypeId: google.maps.MapTypeId.ROADMAP
};

var map = new google.maps.Map($('#map_canvas'), myOptions);

fs.makeListDropDown(fs.userLists);

