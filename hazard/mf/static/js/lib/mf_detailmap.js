(function() {
  var FILL_OPTIONS, FILL_Z_INDEX, HELLS, HOVERED_PIN_Z_INDEX, ICONS, ICONS_URL, INFO_WINDOW, INFO_WINDOW_MARKER, MAP, MAP_STYLE, MAX_ZOOM_LEVEL, PIN_Z_INDEX, PLACES, POINT_AS_CIRCLE_RADIUS, POLYS, POLYS_COLORS, SCHOVAVACZ_OPTS, SINGLE_ZONE, VIEW, ZONES, click_on_hell, convert_to_hex, convert_to_rgb, draw_hells, get_color, hex, interpolate_color, load_maps_api, map_legend, mouse_on_hell, mouse_out_of_hell, number_to_graph, select_legend_handler, select_legend_handler2, trim, update_map_legend;
  SCHOVAVACZ_OPTS = {
    limit: 4,
    epsilon: 1,
    show_txt: ' <i>a další…(%count%)</i>',
    hide_txt: ' <i>zkrátit seznam…</i>',
    items_selector: 'span'
  };
  VIEW = 'hells';
  MAP = void 0;
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
    }, {
      featureType: "administrative.country",
      elementType: "geometry",
      stylers: [
        {
          visibility: "on"
        }, {
          lightness: 58
        }
      ]
    }
  ];
  POLYS = {};
  POLYS_COLORS = {};
  /*
  Interpretuje hodnotu v tabulce jako barevny prouzek na pozadi radku tabulky.
  */
  number_to_graph = function($table, values, percents, cls) {
    var max, td1_w, td2_w, width;
    if (percents) {
      max = 100.0;
    } else {
      max = _.max(values) * 1.2;
    }
    width = $table.width();
    td1_w = $table.find('td:first').width();
    td2_w = width - td1_w;
    return $table.find('tr').each(function(idx, el) {
      var $td1, $td2, $tr, w, x1, x2;
      $tr = $(this);
      $td1 = $tr.find('td:first');
      $td2 = $tr.find("." + cls);
      w = Math.round(values[idx] / max * width);
      if (w > td1_w) {
        x1 = 1000;
        x2 = w - td1_w;
      } else {
        x1 = w;
        x2 = 0;
      }
      $td1.css('background-position', "" + x1 + "px 0");
      return $td2.css('background-position', "" + x2 + "px 0");
    });
  };
  /*
  Funkce pro vypocet interpolovanych barev mezi dvema zadanymi body.
  */
  hex = function(v) {
    var out;
    out = v.toString(16);
    if (out.length === 1) {
      out = '0' + out;
    }
    return out;
  };
  convert_to_hex = function(rgb) {
    return '#' + hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2]);
  };
  trim = function(s) {
    if (s.charAt(0) === '#') {
      return s.substring(1, 7);
    } else {
      return s;
    }
  };
  convert_to_rgb = function(hex) {
    var color;
    return color = [parseInt(trim(hex).substring(0, 2), 16), parseInt(trim(hex).substring(2, 4), 16), parseInt(trim(hex).substring(4, 6), 16)];
  };
  interpolate_color = function(start_color, end_color, value) {
    var c, end, start;
    start = convert_to_rgb(start_color);
    end = convert_to_rgb(end_color);
    c = [Math.round((end[0] - start[0]) * value + start[0]), Math.round((end[1] - start[1]) * value + start[1]), Math.round((end[2] - start[2]) * value + start[2])];
    return convert_to_hex(c);
  };
  get_color = function(type, value) {
    var color;
    if (type === 'hells') {
      color = interpolate_color('#fac90d', '#7e000b', value);
    } else {
      color = interpolate_color('#fac90d', '#7e000b', value);
    }
    return color;
  };
  map_legend = function() {
    var pos;
    pos = $('#map').position();
    return $('#map-legend').css({
      left: "" + (pos.left + 10) + "px",
      top: "" + (pos.top + 60) + "px"
    });
  };
  update_map_legend = function(extrems) {
    $('#map-legend').attr('class', '').addClass($('#type-switcher').val());
    $('#map-legend .min').text(Math.round(extrems.min));
    return $('#map-legend .max').text(Math.round(extrems.max));
  };
  select_legend_handler = function() {
    var opened;
    opened = false;
    return $('#select-handler').click(function() {
      var selector;
      selector = "#select-legend ." + ($("#type-switcher").val()) + " ." + ($("#table-switcher").val());
      opened = !opened;
      $(selector).toggleClass('opened', opened).slideToggle('fast');
      return false;
    });
  };
  select_legend_handler2 = function() {
    var neco, selector;
    neco = $('#select-legend .opened');
    if (neco.length) {
      neco.removeClass('opened').hide();
      selector = "#select-legend ." + ($("#type-switcher").val()) + " ." + ($("#table-switcher").val());
      return $(selector).addClass('opened').show();
    }
  };
  "Detailni mapa s konflikty pro konkretni obec.\n\nNOTE: pro velka mesta by se sikl MarkerClusterer, ale prdim ted na to. Jako\nnepouzit ho ma i sve vyhody, aby jste vedeli.";
  HELLS = {};
  ZONES = {};
  PLACES = {};
  INFO_WINDOW = null;
  INFO_WINDOW_MARKER = null;
  SINGLE_ZONE = null;
  PIN_Z_INDEX = 10;
  HOVERED_PIN_Z_INDEX = PIN_Z_INDEX + 10;
  FILL_Z_INDEX = 14;
  MAX_ZOOM_LEVEL = 17;
  POINT_AS_CIRCLE_RADIUS = 8;
  FILL_OPTIONS = {};
  ICONS = {};
  ICONS_URL = 'http://media.mapyhazardu.cz/img/';
  /*
  Obsluha situace, kdy je kurzor mysi nad hernou.
  */
  mouse_on_hell = function(key, icon_type, force) {
    var addr, circle, i, item, k, place_address_id, poly, shape, shapes, _i, _j, _len, _len2, _ref, _results;
    if (force == null) {
      force = false;
    }
    if (INFO_WINDOW && !force) {
      return;
    }
    HELLS[key].setIcon(ICONS["" + icon_type + "_hovered"]);
    HELLS[key].setZIndex(HOVERED_PIN_Z_INDEX);
    if (key in window.hazardata.conflicts) {
      shapes = [];
      if (key in window.hazardata.hell_surrounds) {
        shapes.push(window.hazardata.hell_surrounds[key]);
      } else {
        shapes = (function() {
          var _i, _len, _ref, _results;
          _ref = window.hazardata.conflicts[key];
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            k = _ref[_i];
            _results.push(window.hazardata.place_surrounds[k]);
          }
          return _results;
        })();
      }
      if (shapes.length) {
        ZONES[key] = [];
        for (_i = 0, _len = shapes.length; _i < _len; _i++) {
          shape = shapes[_i];
          poly = new google.maps.Polygon(FILL_OPTIONS['zone']);
          poly.setPath((function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = shape.length; _i < _len; _i++) {
              item = shape[_i];
              _results.push((function() {
                var _i, _len, _results;
                _results = [];
                for (_i = 0, _len = item.length; _i < _len; _i++) {
                  i = item[_i];
                  _results.push(new google.maps.LatLng(i[1], i[0]));
                }
                return _results;
              })());
            }
            return _results;
          })());
          poly.setMap(MAP);
          ZONES[key].push(poly);
        }
      }
      PLACES[key] = {};
      _ref = window.hazardata.conflicts[key];
      _results = [];
      for (_j = 0, _len2 = _ref.length; _j < _len2; _j++) {
        place_address_id = _ref[_j];
        addr = window.hazardata.addresses[place_address_id];
        if (addr.geo_type === 'point') {
          circle = new google.maps.Circle(FILL_OPTIONS['building']);
          circle.setCenter(new google.maps.LatLng(addr.geo[1], addr.geo[0]));
          circle.setRadius(POINT_AS_CIRCLE_RADIUS);
          circle.setMap(MAP);
          PLACES[key][place_address_id] = circle;
        } else if (addr.geo_type === 'poly') {
          poly = new google.maps.Polygon(FILL_OPTIONS['zone']);
          poly.setPath((function() {
            var _i, _len, _ref, _results;
            _ref = addr.geo;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              item = _ref[_i];
              _results.push((function() {
                var _i, _len, _results;
                _results = [];
                for (_i = 0, _len = item.length; _i < _len; _i++) {
                  i = item[_i];
                  _results.push(new google.maps.LatLng(i[1], i[0]));
                }
                return _results;
              })());
            }
            return _results;
          })());
          poly.setMap(MAP);
          PLACES[key][place_address_id] = poly;
        } else {
          continue;
        }
      }
      return _results;
    }
  };
  /*
  Kurzor mysi odjel z ikony herny pryc. Je treba po nem uklidit.
  */
  mouse_out_of_hell = function(key, icon_type, force) {
    var place_id, zone, _i, _len, _ref;
    if (force == null) {
      force = false;
    }
    if (INFO_WINDOW && !force) {
      return;
    }
    HELLS[key].setIcon(ICONS["" + icon_type]);
    HELLS[key].setZIndex(PIN_Z_INDEX);
    if (key in ZONES) {
      _ref = ZONES[key];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        zone = _ref[_i];
        zone.setMap(null);
      }
      delete ZONES[key];
    }
    if (key in PLACES) {
      for (place_id in PLACES[key]) {
        PLACES[key][place_id].setMap(null);
        delete PLACES[key][place_id];
      }
      return delete PLACES[key];
    }
  };
  /*
  Kliknuti nad ikonou herny.
  */
  click_on_hell = function(key, icon_type) {
    var content, place, place_id, places, title, _i, _len, _ref, _type;
    if (INFO_WINDOW_MARKER) {
      _type = INFO_WINDOW_MARKER in window.hazardata.conflicts ? 'disallowed' : 'allowed';
      mouse_out_of_hell(INFO_WINDOW_MARKER, _type, true);
      mouse_on_hell(key, icon_type, true);
    }
    if (INFO_WINDOW) {
      INFO_WINDOW.close();
    }
    title = window.hazardata.hells[key].join('<br>');
    if (key in window.hazardata.conflicts) {
      content = '<p>V okolí tohoto místa se naléza ';
      content = "" + content + (window.hazardata.conflicts[key].length > 1 ? 'několik budov, se kterými' : 'budova, se kterou');
      content = "" + content + " je herna v konfliktu:</p><ul id=\"infowindow-list\">";
      places = [];
      _ref = window.hazardata.conflicts[key];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        place_id = _ref[_i];
        place = _.map(window.hazardata.places[place_id], function(item) {
          return "<li><abbr class=\"\#b-" + place_id + "\">" + item + "</abbr></li>";
        });
        places.push(place.join(''));
      }
      content = "" + content + (places.join('')) + "</ul>";
    } else {
      content = '<p>V okolí tohoto místa není žádná budova, se kterou by byla herna v konfliktu.</p>';
    }
    INFO_WINDOW = new google.maps.InfoWindow({
      content: "<h4>" + title + "</h4>" + content,
      maxWidth: 300
    });
    google.maps.event.addListener(INFO_WINDOW, 'closeclick', function() {
      mouse_out_of_hell(key, icon_type, true);
      INFO_WINDOW = null;
      return INFO_WINDOW_MARKER = null;
    });
    google.maps.event.addListener(INFO_WINDOW, 'domready', function() {
      return $('#infowindow-list abbr[class^="#b-"]').hover(function() {
        var i, id, item, shape;
        id = $(this).attr('class').split('-')[1];
        PLACES[key][id].setOptions(FILL_OPTIONS['building_hovered']);
        shape = window.hazardata.place_surrounds[id];
        SINGLE_ZONE = new google.maps.Polygon(FILL_OPTIONS['zone_hovered']);
        SINGLE_ZONE.setPath((function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = shape.length; _i < _len; _i++) {
            item = shape[_i];
            _results.push((function() {
              var _i, _len, _results;
              _results = [];
              for (_i = 0, _len = item.length; _i < _len; _i++) {
                i = item[_i];
                _results.push(new google.maps.LatLng(i[1], i[0]));
              }
              return _results;
            })());
          }
          return _results;
        })());
        return SINGLE_ZONE.setMap(MAP);
      }, function() {
        var id;
        id = $(this).attr('class').split('-')[1];
        PLACES[key][id].setOptions(FILL_OPTIONS['building']);
        SINGLE_ZONE.setMap(null);
        return SINGLE_ZONE = null;
      }).click(function() {
        return false;
      });
    });
    INFO_WINDOW_MARKER = key;
    return INFO_WINDOW.open(MAP, HELLS[key]);
  };
  /*
  Vykresleni heren.
  */
  draw_hells = function() {
    var bounds, lats, lons;
    lats = [];
    lons = [];
    _.each(window.hazardata.hell_addresses, function(hell_address_id) {
      var geo, icon_type, key;
      key = hell_address_id.toString();
      icon_type = key in window.hazardata.conflicts ? 'disallowed' : 'allowed';
      geo = window.hazardata.addresses[key].geo;
      lats.push(geo[1]);
      lons.push(geo[0]);
      HELLS[key] = new google.maps.Marker({
        map: MAP,
        position: new google.maps.LatLng(geo[1], geo[0]),
        title: 'herna',
        shadow: ICONS['shadow'],
        zIndex: PIN_Z_INDEX,
        icon: ICONS[icon_type]
      });
      google.maps.event.addListener(HELLS[key], 'mouseover', function() {
        return mouse_on_hell(key, icon_type);
      });
      google.maps.event.addListener(HELLS[key], 'mouseout', function() {
        return mouse_out_of_hell(key, icon_type);
      });
      return google.maps.event.addListener(HELLS[key], 'click', function(ev) {
        return click_on_hell(key, icon_type);
      });
    });
    bounds = new google.maps.LatLngBounds(new google.maps.LatLng(_.min(lats), _.min(lons)), new google.maps.LatLng(_.max(lats), _.max(lons)));
    google.maps.event.addListenerOnce(MAP, 'idle', function() {
      var zoom;
      zoom = MAP.getZoom();
      if (zoom > MAX_ZOOM_LEVEL) {
        return MAP.setZoom(MAX_ZOOM_LEVEL);
      }
    });
    return MAP.fitBounds(bounds);
  };
  /*
  Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
  */
  load_maps_api = function() {
    $('h1').addClass('loading');
    return $.getJSON("" + window.location.pathname + "?ajax", function(data) {
      var script;
      window.hazardata = data;
      script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map';
      return document.body.appendChild(script);
    });
  };
  /*
  Inicializace map, volana jako callback po asynchronnim nacteni Google Maps API.
  */
  window.late_map = function() {
    var map_options, point0, point14, size;
    FILL_OPTIONS['building'] = {
      strokeOpacity: 0,
      fillColor: '#ffffff',
      fillOpacity: 1,
      zIndex: FILL_Z_INDEX + 1
    };
    FILL_OPTIONS['building_hovered'] = {
      strokeOpacity: 0,
      fillColor: '#ffffff',
      fillOpacity: 1,
      zIndex: FILL_Z_INDEX + 3
    };
    FILL_OPTIONS['zone'] = {
      strokeWeight: 0,
      strokeOpacity: 0,
      fillColor: '#000000',
      fillOpacity: .7,
      zIndex: FILL_Z_INDEX
    };
    FILL_OPTIONS['zone_hovered'] = {
      strokeOpacity: 0,
      fillColor: '#000000',
      fillOpacity: 1,
      zIndex: FILL_Z_INDEX + 2
    };
    size = new google.maps.Size(28, 28);
    point0 = new google.maps.Point(0, 0);
    point14 = new google.maps.Point(14, 14);
    ICONS['allowed'] = new google.maps.MarkerImage("" + ICONS_URL + "yes.png", size, point0, point14);
    ICONS['allowed_dimmed'] = new google.maps.MarkerImage("" + ICONS_URL + "yes_dimmed.png", size, point0, point14);
    ICONS['allowed_hovered'] = new google.maps.MarkerImage("" + ICONS_URL + "yes_hovered.png", size, point0, point14);
    ICONS['disallowed'] = new google.maps.MarkerImage("" + ICONS_URL + "no.png", size, point0, point14);
    ICONS['disallowed_dimmed'] = new google.maps.MarkerImage("" + ICONS_URL + "no_dimmed.png", size, point0, point14);
    ICONS['disallowed_hovered'] = new google.maps.MarkerImage("" + ICONS_URL + "no_hovered.png", size, point0, point14);
    ICONS['shadow'] = new google.maps.MarkerImage("" + ICONS_URL + "shadow.png", new google.maps.Size(27, 14), new google.maps.Point(0, 0), new google.maps.Point(8, 0));
    map_options = {
      zoom: 6,
      center: new google.maps.LatLng(49.38512, 14.61765),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    MAP = new google.maps.Map(document.getElementById("map"), map_options);
    draw_hells();
    return $('h1').removeClass('loading');
  };
  $(document).ready(function() {
    return load_maps_api();
  });
}).call(this);
