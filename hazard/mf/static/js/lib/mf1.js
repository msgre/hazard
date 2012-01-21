(function() {
  var $, MAP, MAP_STYLE, POLYS, POLYS_COLORS, SCHOVAVACZ_OPTS, VIEW, convert_to_hex, convert_to_rgb, draw_shapes, get_color, handle_switcher, handle_table, hex, interpolate_color, load_maps_api, number_to_graph, trim, update_shapes;
  var __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  $ = jQuery;
  $.fn.extend({
    schovavacz: function(options) {
      var opts, self;
      self = $.fn.schovavacz;
      opts = $.extend({}, self.default_options, options);
      return $(this).each(function(i, el) {
        return self.init(el, opts);
      });
    }
  });
  $.extend($.fn.schovavacz, {
    default_options: {
      show_txt: 'Next',
      hide_txt: 'Hide',
      link_class: 'krl_command_link',
      hidden_container_class: 'krl_hidden',
      shown_container_class: 'krl_shown',
      item_class: 'krl_item',
      item_overlimit_class: 'krl_item_overlimit',
      link_class: 'krl_command_link',
      items_selector: 'a',
      epsilon: 0,
      limit: 2
    },
    init: function(el, opts) {
      var $el, items, link, rest;
      $el = $(el);
      $el.addClass(opts.hidden_container_class);
      items = $el.find(opts.items_selector);
      items.addClass(opts.item_class);
      if ((items.length - opts.epsilon) > opts.limit) {
        rest = items.filter(":gt(" + (opts.limit - 1) + ")");
        rest.addClass(opts.item_overlimit_class).hide();
        opts.show_txt = opts.show_txt.replace('%count%', rest.length);
        link = $("<a>", {
          html: opts.show_txt,
          href: "#",
          "class": opts.link_class
        });
        this.makeLinkClickable(link, $el, opts);
        return $el.append(link);
      }
    },
    makeLinkClickable: function(link, container, opts) {
      return link.click(function() {
        var $link, isHidden;
        $link = $(this);
        isHidden = container.hasClass(opts.hidden_container_class);
        $link.html(isHidden ? opts.hide_txt : opts.show_txt);
        if (isHidden) {
          container.removeClass(opts.hidden_container_class).addClass(opts.shown_container_class).find("." + opts.item_class).show();
        } else {
          container.addClass(opts.hidden_container_class).removeClass(opts.shown_container_class).find("." + opts.item_overlimit_class).hide();
        }
        return false;
      });
    }
  });
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
      color = interpolate_color('#FFD700', '#EE0000', value);
    } else {
      color = interpolate_color('#00FFFF', '#0028FF', value);
    }
    return color;
  };
  "Kod pro stranky s krajem a okresy.\n\nZ tabulky vlozene do stranky dokaze vyzobnout potrebne informace (napr.\nabsolutni pocet heren v kraji), spoji se serverem a vytahne z nej polygony\ngeokrafickych objektu (obrysy kraju/okresu), zavesi na elementy ve strance\nobsluzne funkce a upravi vzhled stranky.\n\nTODO: predelat draw_shapes aby vyuzival getBounds";
  /*
  Obsluha preklikavani pohledu herny/automaty.
  */
  handle_switcher = function(set) {
    var $primer;
    if (set == null) {
      set = true;
    }
    $primer = $('#primer');
    $primer.children('div').last().hide();
    $('table.machines').closest('div.outer-wrapper').hide();
    $('#type-switcher').change(function() {
      var old_class, old_value;
      VIEW = $(this).val();
      old_value = _.reject($(this).find('option'), function(i) {
        return $(i).attr('value') === VIEW;
      });
      old_class = $(old_value).attr('value');
      $("div.outer-wrapper." + VIEW + ", #primer div." + VIEW).show();
      $("div.outer-wrapper." + old_class + ", #primer div." + old_class).hide();
      return $('#table-switcher').change();
    });
    return $('#type-switcher').change();
  };
  /*
  Zjednodusi tabulku na strance -- zobrazi vzdy jen jeden vybrany sloupec
  a data v nem interpretuje jako barevny prouzek na pozadi radku. Povesi na
  tabulku hover obsluhu (zvyrazeneni radku i polygonu v mape).
  */
  handle_table = function() {
    $('#other-districts').click(function() {
      $('table.statistics tr.hide').removeClass('hide');
      $('#other-districts-label').remove();
      $(this).closest('p').remove();
      $('#type-switcher').change();
      return false;
    });
    $('table.statistics tr').hover(function() {
      var key;
      key = $.trim($(this).attr('class').replace('active', '').replace('hide', ''));
      google.maps.event.trigger(POLYS[key], 'mouseover');
      return $(this).addClass('hover');
    }, function() {
      var key;
      $(this).removeClass('hover');
      key = $.trim($(this).attr('class').replace('active', '').replace('hide', ''));
      return google.maps.event.trigger(POLYS[key], 'mouseout');
    });
    $('table.statistics td').click(function() {
      var $tr, href;
      $tr = $(this).closest('tr');
      href = $tr.find('a').attr('href');
      $('h1').addClass('loading');
      $.ajax({
        url: href,
        cache: true,
        dataType: 'json',
        success: function(data) {
          $('h1').replaceWith(data.main_header);
          $('#primer').replaceWith(data.primer_content);
          $('.sub-objects').schovavacz(SCHOVAVACZ_OPTS);
          handle_switcher(false);
          $('table.statistics tr.active').removeClass('active');
          POLYS[window.actual].setOptions({
            zIndex: 10,
            strokeWeight: 0
          });
          window.actual = $.trim($tr.attr('class').replace('hover', '').replace('hide', ''));
          POLYS[window.actual].setOptions({
            zIndex: 20,
            strokeWeight: 3,
            strokeColor: "#444444"
          });
          $tr.addClass('active');
          google.maps.event.addListenerOnce(MAP, 'zoom_changed', function() {
            return MAP.setZoom(MAP.getZoom() - 1);
          });
          MAP.fitBounds(POLYS[window.actual].getBounds());
          return $('h1').removeClass('loading');
        }
      });
      return false;
    });
    $('table.statistics thead').remove();
    $('#table-switcher').change(function() {
      var switcher_value, type_value;
      switcher_value = $(this).val();
      type_value = $('#type-switcher').val();
      $("table.statistics").each(function() {
        var $table, percents, values;
        values = [];
        percents = false;
        $table = $(this);
        $table.find('td').each(function() {
          var $td, value;
          $td = $(this);
          if ($td.attr('class') && !$td.hasClass(switcher_value)) {
            return $td.hide();
          } else {
            if ($td.attr('class')) {
              value = $.trim($td.text());
              percents = __indexOf.call(value, '%') >= 0;
              value = value.replace('%', '').replace(',', '.');
              if (value.length) {
                values.push(parseFloat(value));
              } else {
                values.push(0);
              }
            }
            return $td.show();
          }
        });
        if (!$table.data(switcher_value)) {
          $table.data(switcher_value, {
            'min': _.min(values),
            'max': percents ? 100.0 : _.max(values)
          });
        }
        return number_to_graph($table, values, percents, switcher_value);
      });
      return update_shapes();
    });
    return $('.table-switcher').change();
  };
  /*
  Prvotni vykresleni barevnych polygonu do mapy (dle aktualne zvolenych voleb
  v selektitkach a datech v tabulce).
  */
  draw_shapes = function() {
    var $select, $table, actual_max_lat, actual_max_lon, actual_min_lat, actual_min_lon, col, delta, extrems, max_lat, max_lats, max_lon, max_lons, min_lat, min_lats, min_lon, min_lons, type, _ref, _ref2;
    $table = $("table.statistics." + VIEW);
    $select = $('#table-switcher');
    col = $select.val();
    extrems = $table.data(col);
    delta = extrems.max - extrems.min;
    _ref = [[], [], [], []], min_lats = _ref[0], max_lats = _ref[1], min_lons = _ref[2], max_lons = _ref[3];
    _ref2 = [null, null, null, null], actual_min_lat = _ref2[0], actual_max_lat = _ref2[1], actual_min_lon = _ref2[2], actual_max_lon = _ref2[3];
    type = $('#type-switcher').val();
    _.each(window.shapes, function(shape, key) {
      var color, i, item, max_lat, max_lon, min_lat, min_lon, polys, value, _i, _j, _len, _len2, _polys, _ref;
      if (!shape) {
        return true;
      }
      polys = [];
      _ref = [100000000, 0, 100000000, 0], min_lat = _ref[0], max_lat = _ref[1], min_lon = _ref[2], max_lon = _ref[3];
      for (_i = 0, _len = shape.length; _i < _len; _i++) {
        item = shape[_i];
        _polys = [];
        for (_j = 0, _len2 = item.length; _j < _len2; _j++) {
          i = item[_j];
          min_lat = i[0] < min_lat ? i[0] : min_lat;
          max_lat = i[0] > max_lat ? i[0] : max_lat;
          min_lon = i[1] < min_lon ? i[1] : min_lon;
          max_lon = i[1] > max_lon ? i[1] : max_lon;
          _polys.push(new google.maps.LatLng(i[0], i[1]));
        }
        polys.push(_polys);
      }
      min_lats.push(min_lat);
      max_lats.push(max_lat);
      min_lons.push(min_lon);
      max_lons.push(max_lon);
      if (key === window.actual) {
        actual_min_lat = min_lat;
        actual_max_lat = max_lat;
        actual_min_lon = min_lon;
        actual_max_lon = max_lon;
      }
      value = $.trim($table.find("tr." + key + " td." + col).text());
      value = value.replace('%', '').replace(',', '.');
      value = (value - extrems.min) / delta;
      color = get_color(type, value);
      POLYS[key] = new google.maps.Polygon({
        paths: polys,
        strokeColor: color,
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: color,
        fillOpacity: 1,
        zIndex: 10
      });
      POLYS_COLORS[key] = color;
      if (key === window.actual) {
        POLYS[key].setOptions({
          zIndex: 20,
          strokeColor: "#444444",
          strokeWeight: 3
        });
      }
      google.maps.event.addListener(POLYS[key], 'mouseover', function() {
        var $tr;
        POLYS[key].setOptions({
          fillColor: '#444444',
          strokeColor: '#444444',
          zIndex: 15
        });
        $tr = $table.find("tr." + key);
        return $tr.addClass('hover');
      });
      google.maps.event.addListener(POLYS[key], 'mouseout', function() {
        POLYS[key].setOptions({
          fillColor: POLYS_COLORS[key],
          strokeColor: key === window.actual ? '#444444' : POLYS_COLORS[key],
          zIndex: key === window.actual ? 20 : 10
        });
        return $table.find("tr." + key).removeClass('hover');
      });
      google.maps.event.addListener(POLYS[key], 'click', function() {
        return $table.find("tr." + key + " a").click();
      });
      return POLYS[key].setMap(MAP);
    });
    min_lat = _.min(min_lats);
    max_lat = _.max(max_lats);
    min_lon = _.min(min_lons);
    max_lon = _.max(max_lons);
    min_lat = actual_min_lat;
    max_lat = actual_max_lat;
    min_lon = actual_min_lon;
    max_lon = actual_max_lon;
    google.maps.event.addListenerOnce(MAP, 'zoom_changed', function() {
      return MAP.setZoom(MAP.getZoom() - 1);
    });
    return MAP.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(min_lat, min_lon), new google.maps.LatLng(max_lat, max_lon)));
  };
  /*
  Aktualizace barev vykreslenych polygonu na mape (dle aktualne zvolenych voleb
  v selektitkach a datech v tabulce).
  */
  update_shapes = function() {
    var $select, $table, col, delta, extrems, type;
    $table = $("table.statistics." + VIEW);
    $select = $('#table-switcher');
    col = $select.val();
    extrems = $table.data(col);
    delta = extrems.max - extrems.min;
    type = $('#type-switcher').val();
    return _.each(window.shapes, function(shape, key) {
      var color, value;
      if (!POLYS[key]) {
        return true;
      }
      value = $.trim($table.find("tr." + key + " td." + col).text());
      value = value.replace('%', '').replace(',', '.');
      value = (value - extrems.min) / delta;
      color = get_color(type, value);
      POLYS_COLORS[key] = color;
      POLYS[key].setOptions({
        fillColor: color,
        strokeColor: color
      });
      if (key === window.actual) {
        return POLYS[key].setOptions({
          zIndex: 20,
          strokeColor: "#444444",
          strokeWeight: 3
        });
      }
    });
  };
  /*
  Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
  */
  load_maps_api = function() {
    $('h1').addClass('loading');
    return $.getJSON(window.url, function(data) {
      var key, script, _i, _len, _ref;
      window.shapes = {};
      _ref = _.keys(data['details']);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        window.shapes[key] = data['details'][key]['shape'];
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
    if (!google.maps.Polygon.prototype.getBounds) {
      google.maps.Polygon.prototype.getBounds = function(latLng) {
        var bounds, item, path, paths, _i, _j, _len, _len2, _ref, _ref2;
        bounds = new google.maps.LatLngBounds();
        paths = this.getPaths();
        _ref = paths.getArray();
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          path = _ref[_i];
          _ref2 = path.getArray();
          for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
            item = _ref2[_j];
            bounds.extend(item);
          }
        }
        return bounds;
      };
    }
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
    MAP.mapTypes.set('CB', styledMapType);
    draw_shapes();
    return $('h1').removeClass('loading');
  };
  $(document).ready(function() {
    handle_table();
    load_maps_api();
    $('.sub-objects').schovavacz(SCHOVAVACZ_OPTS);
    return handle_switcher();
  });
}).call(this);
