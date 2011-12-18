(function() {
  "TODO:";  var HELL_MARKERS, HOVERED_HELL, ICONS, MAP, MAP_STYLE, MARKER_LUT, OPENED_INFOWINDOW, clear_surround, draw_hells, draw_shapes, handle_perex, init_map, show_surround;
  $(document).ready(function() {
    init_map();
    draw_shapes();
    return handle_perex();
  });
  draw_shapes = function() {
    return _.each(window.shapes, function(shape, key) {
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
      if (key === window.region) {
        sh = new google.maps.Polygon({
          paths: polys,
          strokeColor: "#FFFF00",
          strokeOpacity: 1,
          strokeWeight: 3,
          fillColor: "#000000",
          fillOpacity: 1
        });
      } else {
        sh = new google.maps.Polygon({
          paths: polys,
          strokeColor: "#dddddd",
          strokeOpacity: 1,
          strokeWeight: 0,
          fillColor: "#666666",
          fillOpacity: 1
        });
      }
      return sh.setMap(MAP);
    });
  };
  MAP = void 0;
  ICONS = {
    'allowed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'allowed_dimmed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'allowed_hovered': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'disallowed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'disallowed_dimmed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'disallowed_hovered': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14)),
    'shadow': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/shadow.png', new google.maps.Size(27, 14), new google.maps.Point(0, 0), new google.maps.Point(8, 0))
  };
  MARKER_LUT = {};
  HELL_MARKERS = {};
  HOVERED_HELL = null;
  OPENED_INFOWINDOW = false;
  MAP_STYLE = [
    {
      featureType: "water",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "transit",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "landscape.natural",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "road",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "landscape.man_made",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "poi",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "administrative.province",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "administrative.locality",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }, {
      featureType: "administrative",
      elementType: "labels",
      stylers: [
        {
          visibility: "off"
        }
      ]
    }
  ];
  show_surround = function(hell) {
    var conflict, coords, i, poly;
    conflict = window.conflicts["" + hell.id];
    coords = [
      (function() {
        var _i, _len, _ref, _results;
        _ref = conflict.shape[0];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push(new google.maps.LatLng(i[1], i[0]));
        }
        return _results;
      })()
    ];
    poly = new google.maps.Polygon({
      paths: coords,
      strokeColor: "#FF0000",
      strokeOpacity: 0,
      strokeWeight: 0,
      fillColor: "#FF0000",
      fillOpacity: 0.35
    });
    poly.setMap(MAP);
    return HOVERED_HELL = {
      'hell': hell,
      'poly': poly
    };
  };
  clear_surround = function() {
    if (HOVERED_HELL) {
      HOVERED_HELL['poly'].setMap(null);
      return HOVERED_HELL = null;
    }
  };
  draw_hells = function() {
    var bounds, ne, sw;
    sw = [1000, 1000];
    ne = [0, 0];
    _.each(window.hells, function(hell) {
      var address, infowindow, marker_pos, pos_key;
      address = window.addresses["" + hell.address];
      pos_key = "" + address.point[1] + "-" + address.point[0];
      if (pos_key in MARKER_LUT) {
        MARKER_LUT[pos_key]['hells'].push(hell.id);
        HELL_MARKERS[hell.id] = pos_key;
        return true;
      } else {
        MARKER_LUT[pos_key] = {
          'hells': [],
          'gobjects': [],
          'marker': void 0
        };
      }
      MARKER_LUT[pos_key]['hells'].push(hell.id);
      HELL_MARKERS[hell.id] = pos_key;
      marker_pos = new google.maps.LatLng(address.point[1], address.point[0]);
      MARKER_LUT[pos_key]['marker'] = new google.maps.Marker({
        position: marker_pos,
        map: MAP,
        icon: ("" + hell.id) in window.conflicts ? ICONS.disallowed : ICONS.allowed,
        shadow: ICONS.shadow
      });
      if (address.point[1] < sw[0]) {
        sw[0] = address.point[1];
      }
      if (address.point[1] > ne[0]) {
        ne[0] = address.point[1];
      }
      if (address.point[0] < sw[1]) {
        sw[1] = address.point[0];
      }
      if (address.point[0] > ne[1]) {
        ne[1] = address.point[0];
      }
      infowindow = new google.maps.InfoWindow();
      google.maps.event.addListener(MARKER_LUT[pos_key]['marker'], 'click', function() {
        var building_names, hell_titles, i, text;
        if (OPENED_INFOWINDOW) {
          clear_surround();
          OPENED_INFOWINDOW.close();
        }
        OPENED_INFOWINDOW = infowindow;
        show_surround(hell);
        if (MARKER_LUT[pos_key]['hells'].length) {
          hell_titles = ((function() {
            var _i, _len, _ref, _results;
            _ref = MARKER_LUT[pos_key]['hells'];
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              i = _ref[_i];
              _results.push("<a href=\"herny/" + i + "/\">" + window.hells[i].title + "</a>");
            }
            return _results;
          })()).join('<br/>');
        } else {
          hell_titles = null;
        }
        text = "<h4>" + hell_titles + "</h4>";
        if (("" + hell.id) in window.conflicts) {
          text = "" + text + "<p>Provoz herny(-en) je na tomto místě v <b>rozporu se zákonem o loteriích</b>.</p>";
        } else {
          text = "" + text + "<p>Provoz herny(-en) na tomto místě není v rozporu se zákonem o loteriích.</p>";
        }
        if (("" + hell.id) in window.conflicts) {
          text = "" + text + "<p>Konfliktní budovy/oblasti:</p>";
          building_names = ((function() {
            var _i, _len, _ref, _results;
            _ref = window.conflicts["" + hell.id]['buildings'];
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              i = _ref[_i];
              _results.push(window.gobjects["" + i].title);
            }
            return _results;
          })()).join('</li><li>');
          text = "" + text + "<ul><li>" + building_names + "</li></ul>";
        }
        infowindow.setContent(text);
        return infowindow.open(MAP, MARKER_LUT[pos_key]['marker']);
      });
      google.maps.event.addListener(infowindow, 'closeclick', function() {
        OPENED_INFOWINDOW = false;
        return clear_surround();
      });
      if (("" + hell.id) in window.conflicts) {
        google.maps.event.addListener(MARKER_LUT[pos_key]['marker'], 'mouseover', function() {
          if (!OPENED_INFOWINDOW) {
            return show_surround(hell);
          }
        });
        return google.maps.event.addListener(MARKER_LUT[pos_key]['marker'], 'mouseout', function() {
          if (!OPENED_INFOWINDOW) {
            return clear_surround();
          }
        });
      }
    });
    if (window.hells) {
      bounds = new google.maps.LatLngBounds(new google.maps.LatLng(sw[0], sw[1]), new google.maps.LatLng(ne[0], ne[1]));
      return MAP.fitBounds(bounds);
    }
  };
  init_map = function() {
    var map_options, styledMapType;
    if ($('#map').hasClass('detail-map')) {
      map_options = {
        zoom: 14,
        center: new google.maps.LatLng(49.340, 17.993),
        mapTypeControl: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false
      };
      return MAP = new google.maps.Map(document.getElementById("map"), map_options);
    } else {
      map_options = {
        zoom: 6,
        center: new google.maps.LatLng(49.38512, 14.61765),
        mapTypeControl: false,
        mapTypeId: 'CB',
        streetViewControl: false
      };
      MAP = new google.maps.Map(document.getElementById("map"), map_options);
      styledMapType = new google.maps.StyledMapType(MAP_STYLE, {
        name: 'Černobílá'
      });
      return MAP.mapTypes.set('CB', styledMapType);
    }
  };
  handle_perex = function() {
    var $table;
    $('#percentual-perex').hide();
    $('#perex a').click(function() {
      var parent;
      parent = $(this).closest('div.block');
      console.log(parent);
      parent.hide();
      parent.siblings().show();
      return false;
    });
    $table = $('#table-data');
    $table.hide();
    $table.before('<p><a href="#">Tabulková data</a></p>');
    return $table.prev('p').find('a').click(function() {
      $table.toggle();
      return false;
    });
  };
}).call(this);
