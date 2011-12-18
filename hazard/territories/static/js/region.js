(function() {
  var MAP;
  MAP = void 0;
  $(document).ready(function() {
    var map_options;
    map_options = {
      zoom: 7,
      center: new google.maps.LatLng(49.38512, 14.61765),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    MAP = new google.maps.Map(document.getElementById("map"), map_options);
    return _.each(window.shapes, function(shape) {
      var i, polys, sh;
      if (!shape) {
        return true;
      }
      polys = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = shape.length; _i < _len; _i++) {
          i = shape[_i];
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
  });
}).call(this);
