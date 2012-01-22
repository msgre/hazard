(function() {
  var $, MAP, MAP_STYLE, POINTS, POINT_MAX_RADIUS, POINT_MIN_RADIUS, POLYS, POLYS_COLORS, SCHOVAVACZ_OPTS, VIEW, ajax_key, convert_to_hex, convert_to_rgb, draw_points, draw_shapes, get_color, handle_switcher, handle_table, handle_what_to_do, hex, interpolate_color, load_maps_api, map_legend, number_to_graph, select_legend_handler, select_legend_handler2, trim, update_map_legend, update_points, update_shapes;
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
  "TODO:\n- zvyraznovat aktualni kraj/okres?\n    - nebo se na to vykaslat?\n- kua nemam orafnout aspon ten okres?\n    - o tom data mam ne?";
  /*
  Skryvacka v uvodnim textu
  */
  handle_what_to_do = function() {
    var $div, $link;
    $link = $('.what-to-do');
    $div = $link.closest('p').next('div');
    $div.hide();
    return $link.click(function() {
      $div.slideToggle('fast');
      return false;
    });
  };
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
    $('table.statistics tr').hover(function() {
      var key;
      key = $.trim($(this).attr('class').replace('active', '').replace('hide', ''));
      google.maps.event.trigger(POINTS[key], 'mouseover');
      return $(this).addClass('hover');
    }, function() {
      var key;
      $(this).removeClass('hover');
      key = $.trim($(this).attr('class').replace('active', '').replace('hide', ''));
      return google.maps.event.trigger(POINTS[key], 'mouseout');
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
          $('#breadcrumb').empty().append(data.breadcrumb);
          handle_switcher(false);
          $('table.statistics tr.active').removeClass('active');
          POINTS[window.actual].setOptions({
            fillColor: '#000000',
            zIndex: 30
          });
          window.actual = $.trim($tr.attr('class').replace('hover', '').replace('hide', ''));
          POINTS[window.actual].setOptions({
            fillColor: '#ffffff',
            zIndex: 40
          });
          $tr.addClass('active');
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
      update_shapes();
      update_points();
      return $('h1').removeClass('loading');
    });
    return $('.table-switcher').change();
  };
  /*
  Konstrukce klice do AJAX dat podle hodnot ze selektitek.
  */
  ajax_key = function() {
    var key, kind, type;
    type = $('#type-switcher').val();
    type = type.substr(0, type.length - 1);
    kind = $('#table-switcher').val();
    if (kind === 'counts') {
      key = "" + type + "_" + kind;
    } else {
      kind = kind.split('_');
      key = "" + kind[0] + "_" + type + "_" + kind[1];
    }
    return key;
  };
  /*
  Prvotni vykresleni barevnych polygonu do mapy (dle aktualne zvolenych voleb
  v selektitkach a datech v tabulce).
  */
  draw_shapes = function() {
    var delta, statistics_key, type;
    statistics_key = ajax_key();
    delta = window.extrems[statistics_key].max - window.extrems[statistics_key].min;
    type = $('#type-switcher').val();
    update_map_legend(window.extrems[statistics_key]);
    _.each(window.shapes, function(shape, key) {
      var color, i, item, value;
      if (!shape) {
        return true;
      }
      value = window.districts[key]['statistics'][statistics_key];
      value = (value - window.extrems[statistics_key].min) / delta;
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
        strokeColor: key === window.actual_disctrict.toString() ? '#555555' : color,
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: key === window.actual_disctrict.toString() ? '#555555' : color,
        fillOpacity: 1,
        zIndex: 10
      });
      POLYS_COLORS[key] = color;
      POLYS[key].setMap(MAP);
      google.maps.event.addListener(POLYS[key], 'mouseover', function() {
        if (key === window.actual_disctrict.toString()) {
          return;
        }
        return POLYS[key].setOptions({
          fillColor: '#444444',
          strokeColor: '#444444',
          zIndex: 15
        });
      });
      google.maps.event.addListener(POLYS[key], 'mouseout', function() {
        if (key === window.actual_disctrict.toString()) {
          return;
        }
        return POLYS[key].setOptions({
          fillColor: POLYS_COLORS[key],
          strokeColor: POLYS_COLORS[key],
          zIndex: 10
        });
      });
      return google.maps.event.addListener(POLYS[key], 'click', function() {
        if (key === window.actual_disctrict.toString()) {
          return;
        }
        return window.location = "" + window.districts[key].url + "_/";
      });
    });
    google.maps.event.addListenerOnce(MAP, 'zoom_changed', function() {
      return MAP.setZoom(MAP.getZoom());
    });
    return MAP.fitBounds(POLYS[window.actual_disctrict].getBounds());
  };
  POINTS = {};
  POINT_MIN_RADIUS = 800;
  POINT_MAX_RADIUS = 3000;
  /*
  Vykresli obce ve forme ruzne velkych kolecek (v zavislosti na nastavenych
  hodnotach v selektitkach nad mapou).
  */
  draw_points = function() {
    var $table, color, delta, statistics_key, statistics_max, statistics_min, type;
    $table = $("table.statistics." + VIEW);
    statistics_key = ajax_key();
    statistics_min = _.min(_.values(window.statistics[statistics_key]));
    statistics_max = _.max(_.values(window.statistics[statistics_key]));
    delta = statistics_max - statistics_min;
    type = $('#type-switcher').val();
    color = get_color(type, .6);
    return _.each(window.points, function(point, slug) {
      var id, radius, value;
      if (!point.point) {
        return true;
      }
      id = window.points[slug].id;
      if (id in window.statistics[statistics_key]) {
        value = window.statistics[statistics_key][id];
        value = value ? value : statistics_min;
        value = (value - statistics_min) / delta;
        radius = value * (POINT_MAX_RADIUS - POINT_MIN_RADIUS) + POINT_MIN_RADIUS;
      } else {
        radius = POINT_MIN_RADIUS;
      }
      POINTS[slug] = new google.maps.Circle({
        center: new google.maps.LatLng(point.point[1], point.point[0]),
        fillColor: slug === window.actual ? '#ffffff' : '#000000',
        fillOpacity: 1,
        strokeOpacity: 0,
        radius: radius,
        zIndex: 30,
        map: MAP
      });
      google.maps.event.addListener(POINTS[slug], 'mouseover', function() {
        var $tr;
        $tr = $table.find("tr." + slug);
        $tr.addClass('hover');
        if (slug === window.actual) {
          return;
        }
        return POINTS[slug].setOptions({
          fillColor: '#ffffff',
          zIndex: 40
        });
      });
      google.maps.event.addListener(POINTS[slug], 'mouseout', function() {
        $table.find("tr." + slug).removeClass('hover');
        if (slug === window.actual) {
          return;
        }
        return POINTS[slug].setOptions({
          fillColor: '#000000',
          zIndex: 30
        });
      });
      return google.maps.event.addListener(POINTS[slug], 'click', function() {
        if (window.actual in POINTS) {
          POINTS[window.actual].setOptions({
            fillColor: '#000000',
            zIndex: 30
          });
        }
        window.actual = slug;
        return $table.find("tr." + slug + " a").click();
      });
    });
  };
  /*
  Aktualizace velikosti kolecek (mest) na mape (dle aktualne zvolenych voleb
  v selektitkach).
  */
  update_points = function() {
    var $table, color, delta, statistics_key, statistics_max, statistics_min, type;
    $table = $("table.statistics." + VIEW);
    statistics_key = ajax_key();
    statistics_min = _.min(_.values(window.statistics[statistics_key]));
    statistics_max = _.max(_.values(window.statistics[statistics_key]));
    delta = statistics_max - statistics_min;
    type = $('#type-switcher').val();
    color = get_color(type, .6);
    return _.each(window.points, function(point, slug) {
      var id, radius, value;
      if (!POINTS[slug]) {
        return true;
      }
      id = window.points[slug].id;
      if (id in window.statistics[statistics_key]) {
        value = window.statistics[statistics_key][id];
        value = value ? value : statistics_min;
        value = (value - statistics_min) / delta;
        radius = value * (POINT_MAX_RADIUS - POINT_MIN_RADIUS) + POINT_MIN_RADIUS;
      } else {
        radius = POINT_MIN_RADIUS;
      }
      return POINTS[slug].setOptions({
        radius: radius
      });
    });
  };
  /*
  Aktualizace barev vykreslenych polygonu na mape (dle aktualne zvolenych voleb
  v selektitkach a datech v tabulce).
  */
  update_shapes = function() {
    var delta, statistics_key, type;
    select_legend_handler2();
    statistics_key = ajax_key();
    delta = window.extrems[statistics_key].max - window.extrems[statistics_key].min;
    type = $('#type-switcher').val();
    update_map_legend(window.extrems[statistics_key]);
    return _.each(window.shapes, function(shape, key) {
      var color, value;
      if (!POLYS[key]) {
        return true;
      }
      value = window.districts[key]['statistics'][statistics_key];
      value = (value - window.extrems[statistics_key].min) / delta;
      color = get_color(type, value);
      POLYS_COLORS[key] = color;
      return POLYS[key].setOptions({
        strokeColor: key === window.actual_disctrict.toString() ? '#555555' : color,
        fillColor: key === window.actual_disctrict.toString() ? '#555555' : color
      });
    });
  };
  /*
  Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
  */
  load_maps_api = function() {
    $('h1').addClass('loading');
    return $.getJSON(window.url, function(data) {
      var id, script, _i, _len, _ref;
      window.shapes = {};
      _ref = _.keys(data['districts']);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        id = _ref[_i];
        window.shapes[id] = data['districts'][id]['shape'];
      }
      window.extrems = data['extrems'];
      window.districts = data['districts'];
      window.points = data['details'];
      window.statistics = data['statistics'];
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
    map_legend();
    draw_shapes();
    draw_points();
    $('h1').removeClass('loading');
    handle_table();
    handle_switcher();
    return select_legend_handler();
  };
  $(document).ready(function() {
    handle_what_to_do();
    return load_maps_api();
  });
}).call(this);
