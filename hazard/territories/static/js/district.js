(function() {
  var MAP;
  MAP = void 0;
  $(document).ready(function() {
    var i, map_options, polys, sh;
    map_options = {
      zoom: 7,
      center: new google.maps.LatLng(49.38512, 14.61765),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    MAP = new google.maps.Map(document.getElementById("map"), map_options);
    polys = (function() {
      var _i, _len, _ref, _results;
      _ref = window.shape;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        _results.push(new google.maps.LatLng(i[0], i[1]));
      }
      return _results;
    })();
    sh = new google.maps.Polygon({
      paths: polys,
      strokeColor: "#FF0000",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#FF0000",
      fillOpacity: 0.35
    });
    return sh.setMap(MAP);
  });
}).call(this);
