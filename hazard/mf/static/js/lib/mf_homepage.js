(function() {
  var MAP, MAP_STYLE, POLYS, POLYS_COLORS, SCHOVAVACZ_OPTS, VIEW, convert_to_hex, convert_to_rgb, draw_shapes, get_color, hex, interpolate_color, load_maps_api, map_legend, number_to_graph, renderMenu, select_legend_handler, select_legend_handler2, trim, update_map_legend;
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
  /*
  Kod pro uvodni stranky MF kampane.
  */
  /*
  Naseptavac na uvodni strance kampane MF VLT.
  */
  renderMenu = function(ul, items) {
    var current_category, self;
    self = this;
    current_category = '';
    return $.each(items, function(index, item) {
      if (item.category !== current_category) {
        ul.append("<li class='ui-autocomplete-category'>" + item.category + "</li>");
        current_category = item.category;
      }
      return self._renderItem(ul, item);
    });
  };
  /*
  Vykresleni barevnych polygonu kraju do mapy.
  */
  draw_shapes = function() {
    var delta, max, min, statistics_key, type;
    statistics_key = 'conflict_hell_counts';
    min = _.min(_.values(window.statistics));
    max = _.max(_.values(window.statistics));
    delta = max - min;
    type = 'hells';
    return _.each(window.shapes, function(shape, key) {
      var color, i, item, value;
      if (!shape) {
        return true;
      }
      value = window.statistics[key];
      value = (value - min) / delta;
      color = get_color(type, value);
      POLYS[key] = new google.maps.Polygon({
        paths: (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = shape.length; _i < _len; _i++) {
            item = shape[_i];
            _results.push((function() {
              var _i, _len, _results;
              _results = [];
              for (_i = 0, _len = item.length; _i < _len; _i++) {
                i = item[_i];
                _results.push(new google.maps.LatLng(i[0], i[1]));
              }
              return _results;
            })());
          }
          return _results;
        })(),
        strokeColor: color,
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: color,
        fillOpacity: 1,
        zIndex: 10
      });
      POLYS_COLORS[key] = color;
      POLYS[key].setMap(MAP);
      google.maps.event.addListener(POLYS[key], 'mouseover', function() {
        return POLYS[key].setOptions({
          fillColor: '#444444',
          strokeColor: '#444444',
          zIndex: 15
        });
      });
      google.maps.event.addListener(POLYS[key], 'mouseout', function() {
        return POLYS[key].setOptions({
          fillColor: POLYS_COLORS[key],
          strokeColor: POLYS_COLORS[key],
          zIndex: 10
        });
      });
      return google.maps.event.addListener(POLYS[key], 'click', function() {
        return window.location = "/" + key + "/kampan/mf/";
      });
    });
  };
  /*
  Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
  */
  load_maps_api = function() {
    $('h1').addClass('loading');
    return $.getJSON('/kampan/mf/ajax/kraje/?detailni', function(data) {
      var key, script, _i, _len, _ref;
      window.shapes = {};
      window.regions = {};
      window.statistics = {};
      _ref = _.keys(data['details']);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        window.shapes[key] = data['details'][key]['shape'];
        window.regions[key] = data['details'][key];
        window.regions[key].statistics = data['statistics'][key];
        window.statistics[key] = data['statistics'][key]['hells']['conflict_counts'];
      }
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
    var map_options, styledMapType;
    map_options = {
      zoom: 6,
      center: new google.maps.LatLng(49.78512, 15.41765),
      mapTypeControl: false,
      mapTypeId: 'CB',
      streetViewControl: false,
      panControl: false,
      zoomControl: true,
      zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SMALL
      }
    };
    MAP = new google.maps.Map(document.getElementById("map"), map_options);
    styledMapType = new google.maps.StyledMapType(MAP_STYLE, {
      name: 'Černobílá'
    });
    MAP.mapTypes.set('CB', styledMapType);
    draw_shapes();
    return $('h1').removeClass('loading');
  };
  $(document).ready(function() {
    load_maps_api();
    $.widget('custom.catcomplete', $.ui.autocomplete, {
      _renderMenu: renderMenu
    });
    return $('#search').catcomplete({
      delay: 0,
      source: '/autocomplete/',
      select: function(event, ui) {
        return window.location = "" + ui.item.url + "kampan/mf/";
      }
    });
  });
}).call(this);
