(function() {
  var $, HELL_MARKERS, HOVERED_HELL, ICONS, MAP, MAP_STYLE, MARKER_LUT, OPENED_INFOWINDOW, POLYS, POLYS_COLORS, VIEW, clear_surround, convert_to_hex, convert_to_rgb, draw_hells, draw_shapes, handle_switcher, handle_table, hex, init_map, interpolate_color, number_to_graph, perex_addon, show_surround, trim, update_shapes;
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
      var $el, items, link;
      $el = $(el);
      $el.addClass(opts.hidden_container_class);
      items = $el.find(opts.items_selector);
      items.addClass(opts.item_class);
      if ((items.length - opts.epsilon) > opts.limit) {
        items.filter(":gt(" + (opts.limit - 1) + ")").addClass(opts.item_overlimit_class).hide();
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
  "TODO:";
  $(document).ready(function() {
    handle_table();
    $('#sub-objects').schovavacz({
      limit: 4,
      epsilon: 1,
      show_txt: ' <i>a další…</i>',
      hide_txt: ' <i>zkrátit seznam…</i>',
      items_selector: 'span'
    });
    handle_switcher();
    init_map();
    return draw_shapes();
  });
  VIEW = 'hells';
  perex_addon = function() {
    var $perex, actual_value, geo, i, order, text, type, values, view;
    view = $('#table-switcher option:selected').attr('title');
    type = $('#type-switcher option:selected').attr('title');
    geo = $("#primer ." + VIEW + " span.title").text();
    values = $("table.statistics." + VIEW + " td." + ($('#table-switcher').val()));
    values = _.sortBy((function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = values.length; _i < _len; _i++) {
        i = values[_i];
        _results.push($.trim($(i).text()));
      }
      return _results;
    })(), function(num) {
      if (num) {
        return parseFloat(num.replace('%', '').replace(',', '.'));
      } else {
        return 0;
      }
    });
    values.reverse();
    actual_value = $.trim($("table.statistics." + VIEW + " tr." + window.actual + " td." + ($('#table-switcher').val())).text());
    actual_value = actual_value;
    order = _.indexOf(values, actual_value);
    if (order === 0) {
      text = "Z pohledu <b>" + view + " " + type + "</b> je stav v " + geo + " <b>nejhorší</b> v republice.";
    } else {
      text = "Z pohledu <b>" + view + " " + type + "</b> je stav v " + geo + " <b>" + (order + 1) + ". nejhorší</b> v republice.";
    }
    $perex = $("#primer ." + VIEW + " h2");
    if ($perex.next('h2').length) {
      return $perex.next('h2').html(text);
    } else {
      return $perex.after("<h2>" + text + "</h2>");
    }
  };
  /*
  Obsluha preklikavani pohledu herny/automaty.
  */
  handle_switcher = function() {
    var $primer;
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
  a data v nem interpretuje jako barevny prouzek na pozadi radku.
  */
  handle_table = function() {
    $('table.statistics tr').hover(function() {
      var key;
      key = $.trim($(this).attr('class').replace('active', ''));
      google.maps.event.trigger(POLYS[key], 'mouseover');
      return $(this).addClass('hover');
    }, function() {
      var key;
      $(this).removeClass('hover');
      key = $.trim($(this).attr('class').replace('active', ''));
      return google.maps.event.trigger(POLYS[key], 'mouseout');
    });
    $('table.statistics td').click(function() {
      var href;
      href = $(this).closest('tr').find('a').attr('href');
      window.location = href;
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
      update_shapes();
      return perex_addon();
    });
    return $('.table-switcher').change();
  };
  /*
  Interpretuje hodnotu jako barevny prouzek na pozadi radku tabulky.
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
  POLYS = {};
  POLYS_COLORS = {};
  /*
  TODO:
  */
  draw_shapes = function() {
    var $select, $table, actual_max_lat, actual_max_lon, actual_min_lat, actual_min_lon, col, delta, extrems, max_lat, max_lats, max_lon, max_lons, min_lat, min_lats, min_lon, min_lons, _ref, _ref2;
    $table = $("table.statistics." + VIEW);
    $select = $('#table-switcher');
    col = $select.val();
    extrems = $table.data(col);
    delta = extrems.max - extrems.min;
    _ref = [[], [], [], []], min_lats = _ref[0], max_lats = _ref[1], min_lons = _ref[2], max_lons = _ref[3];
    _ref2 = [null, null, null, null], actual_min_lat = _ref2[0], actual_max_lat = _ref2[1], actual_min_lon = _ref2[2], actual_max_lon = _ref2[3];
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
      color = interpolate_color('#FFD700', '#EE0000', value);
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
          strokeColor: "#333333",
          strokeWeight: 3
        });
      }
      google.maps.event.addListener(POLYS[key], 'mouseover', function() {
        var $tr, hovno, i, texts, titles;
        POLYS[key].setOptions({
          fillColor: '#333333',
          strokeColor: '#333333',
          zIndex: 15
        });
        $tr = $table.find("tr." + key);
        $tr.addClass('hover');
        titles = (function() {
          var _i, _len, _ref, _results;
          _ref = $select.find('option');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            i = _ref[_i];
            _results.push($(i).text());
          }
          return _results;
        })();
        texts = (function() {
          var _i, _len, _ref, _results;
          _ref = $tr.find('td');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            i = _ref[_i];
            _results.push($.trim($(i).text()));
          }
          return _results;
        })();
        hovno = _.zip(titles, _.last(texts, 3));
        return hovno = (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = hovno.length; _i < _len; _i++) {
            i = hovno[_i];
            _results.push("" + i[0] + ": " + i[1]);
          }
          return _results;
        })();
      });
      google.maps.event.addListener(POLYS[key], 'mouseout', function() {
        POLYS[key].setOptions({
          fillColor: POLYS_COLORS[key],
          strokeColor: key === window.actual ? '#333333' : POLYS_COLORS[key],
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
  TODO:
  */
  update_shapes = function() {
    var $select, $table, col, delta, extrems;
    $table = $("table.statistics." + VIEW);
    $select = $('#table-switcher');
    col = $select.val();
    extrems = $table.data(col);
    delta = extrems.max - extrems.min;
    return _.each(window.shapes, function(shape, key) {
      var color, value;
      if (!POLYS[key]) {
        return true;
      }
      value = $.trim($table.find("tr." + key + " td." + col).text());
      value = value.replace('%', '').replace(',', '.');
      value = (value - extrems.min) / delta;
      color = interpolate_color('#FFD700', '#EE0000', value);
      POLYS_COLORS[key] = color;
      POLYS[key].setOptions({
        fillColor: color,
        strokeColor: color
      });
      if (key === window.actual) {
        return POLYS[key].setOptions({
          zIndex: 20,
          strokeColor: "#333333",
          strokeWeight: 3
        });
      }
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
      strokeColor: "#EE0000",
      strokeOpacity: 0,
      strokeWeight: 0,
      fillColor: "#EE0000",
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
        center: new google.maps.LatLng(49.38512, 14.61765),
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
}).call(this);
