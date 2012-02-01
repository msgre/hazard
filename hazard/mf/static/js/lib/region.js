(function() {
  var AppView, CONTROL_LEGEND, DEBUG, EVENTS_CACHE, EXTREMS, GEO_OBJECTS_URLS, GeoObject, GeoObjectList, HazardEvents, LEGENDS, LegendView, MAP, MAP_ACTIVE_POLY_COLOR, MAP_ACTIVE_POLY_ZINDEX, MAP_HOVER_POLY_COLOR, MAP_POLY_ZINDEX, MAP_STYLE, ModifyHtml, PAGE_TYPE, PARAMETERS, PrimerView, TYPES, TableRowView, TableView, convert_to_hex, convert_to_rgb, get_color, hex, interpolate_color, log, parseUrl, path, trim;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  DEBUG = true;
  PARAMETERS = {
    counts: 'celkový počet',
    conflict_counts: 'počet nezákonně povolených',
    conflict_perc: 'poměr nezákonně/zákonně povolených'
  };
  TYPES = {
    hells: 'heren',
    machines: 'automatů'
  };
  LEGENDS = {
    region: {
      hells: {
        counts: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím větší počet heren se v kraji vyskytuje.",
        conflict_counts: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím se v nich vyskytuje větší počet <a href=\"#\">nezákonně\npovolených heren",
        conflict_perc: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím je v kraji více <a href=\"#\">nezákonně povolených heren</a>,\nnež těch, jejichž umístění neodporuje žádnému zákonu."
      },
      machines: {
        counts: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím větší počet automatů se v kraji vyskytuje.",
        conflict_counts: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím se v nich vyskytuje větší počet <a href=\"#\">nezákonně\npovolených automatů</a>.",
        conflict_perc: "V mapě jsou vykresleny kraje České republiky. Čím tmavší\nbarva je použita, tím je v kraji více <a href=\"#\">nezákonně povolených automatů</a>,\nnež těch, jejichž umístění neodporuje žádnému zákonu."
      }
    },
    district: {
      hells: {
        counts: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím větší počet heren se v okrese vyskytuje.",
        conflict_counts: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím se v nich vyskytuje větší počet <a href=\"#\">nezákonně\npovolených heren</a>.",
        conflict_perc: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím je v okrese více <a href=\"#\">nezákonně povolených heren</a>,\nnež těch, jejichž umístění neodporuje žádnému zákonu."
      },
      machines: {
        counts: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím větší počet automatů se v okrese vyskytuje.",
        conflict_counts: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím se v nich vyskytuje větší počet <a href=\"#\">nezákonně\npovolených automatů</a>.",
        conflict_perc: "V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší\nbarva je použita, tím je v okrese více <a href=\"#\">nezákonně povolených automatů</a>,\nnež těch, jejichž umístění neodporuje žádnému zákonu."
      }
    },
    town: {
      hells: {
        counts: "V mapě jsou vykresleny obce vybraného okresu České\nrepubliky.  Čím větší počet heren se v obci vyskytuje, tím\nvětší kolečko je vykresleno.",
        conflict_counts: "V mapě jsou vykresleny obce vybraného okresu České republiky.\nČím více je v obci <a href=\"#\">nezákonně povolených heren</a>, tím větší kolečko\nje vykresleno.",
        conflict_perc: "V mapě jsou vykresleny obce vybraného okresu České republiky.\nČím více je v obci nezákonně povolených heren, vůči těm, jejichž\numístění neodporuje žádnému zákonu, tím je kolečko větší."
      },
      machines: {
        counts: "V mapě jsou vykresleny obce vybraného okresu České\nrepubliky.  Čím větší počet automatů se v obci vyskytuje, tím\nvětší kolečko je vykresleno.",
        conflict_counts: "V mapě jsou vykresleny obce vybraného okresu České republiky.\nČím více je v obci <a href=\"#\">nezákonně povolených automatů</a>, tím větší kolečko\nje vykresleno.",
        conflict_perc: "V mapě jsou vykresleny obce vybraného okresu České republiky.\nČím více je v obci nezákonně povolených automatů, vůči těm, jejichž\numístění neodporuje žádnému zákonu, tím je kolečko větší."
      }
    }
  };
  CONTROL_LEGEND = "Ovládání mapy: najeďte myší nad region či obec která vás zajímá a kliknutím\naktualizujete informace na stránce. Pokud v případě krajů a okresů nad oblastí\nprovedete dvojklik, aplikace vám zobrazí územně nižší celky (např. pokud si\nprohlížíte nějaký kraj, dvojklikem se dostanete na zobrazení okresů).";
  MAP_POLY_ZINDEX = 10;
  MAP_ACTIVE_POLY_COLOR = '#333333';
  MAP_ACTIVE_POLY_ZINDEX = 20;
  MAP_HOVER_POLY_COLOR = '#333333';
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
  ({
    setPolygonBoundsFn: function() {
      if (!google.maps.Polygon.prototype.getBounds) {
        return google.maps.Polygon.prototype.getBounds = function(latLng) {
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
    }
  });
  MAP = void 0;
  path = _.filter(window.location.pathname.split('/'), function(i) {
    return i.length > 0;
  });
  if (path.length === 3) {
    PAGE_TYPE = 'region';
  } else if (path.length === 4) {
    PAGE_TYPE = 'district';
  } else if (path.length === 5) {
    PAGE_TYPE = 'town';
  }
  parseUrl = function() {
    var out;
    out = {
      district: void 0,
      town: void 0
    };
    path = _.filter(window.location.pathname.split('/'), function(i) {
      return i.length > 0;
    });
    if (PAGE_TYPE === 'region') {
      out.region = path[0];
    } else if (PAGE_TYPE === 'district') {
      out.region = path[0];
      out.district = path[1];
    } else if (PAGE_TYPE === 'town') {
      out.region = path[0];
      out.district = path[1];
      out.town = path[2];
    }
    return out;
  };
  log = function(message) {
    if (DEBUG) {
      return console.log(message);
    }
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
  window.hovno = get_color;
  /*
  Synchronizatko.

  Co se v EVENTS_CACHE muze objevit:

  * zaznamenani signalu Google:map_initialized a GeoObjectList:extras_loaded
  * flag MapDrawingAllowed, ktery rika, ze uz se muze kreslit do mapy
  */
  EVENTS_CACHE = {};
  HazardEvents = {};
  _.extend(HazardEvents, Backbone.Events);
  HazardEvents.bind('all', function(name, arg) {
    var extras_loaded, map_init, parts;
    if (arg == null) {
      arg = true;
    }
    parts = name.split(':');
    if (!(parts[0] in EVENTS_CACHE)) {
      EVENTS_CACHE[parts[0]] = {};
    }
    EVENTS_CACHE[parts[0]][parts[1]] = arg;
    extras_loaded = 'GeoObjectList' in EVENTS_CACHE && 'extras_loaded' in EVENTS_CACHE.GeoObjectList;
    map_init = 'Google' in EVENTS_CACHE && 'map_initialized' in EVENTS_CACHE.Google;
    if (map_init && extras_loaded) {
      log('HazardEvents:map initialized');
      EVENTS_CACHE['MapDrawingAllowed'] = true;
      EVENTS_CACHE.GeoObjectList.extras_loaded.trigger('GeoObjectList:redraw_done');
      delete EVENTS_CACHE.Google.map_initialized;
      delete EVENTS_CACHE.GeoObjectList.extras_loaded;
      return $('h1').removeClass('loading');
    }
  });
  /*
  Popis geografickeho objektu v mape.
  */
  GeoObject = (function() {
    function GeoObject() {
      GeoObject.__super__.constructor.apply(this, arguments);
    }
    __extends(GeoObject, Backbone.Model);
    GeoObject.prototype.defaults = {
      hover: false
    };
    return GeoObject;
  })();
  /*
  * json_fragments
    Obsahuje fragmenty stranky. Pri kliknuti na jiny radek v tabulce se vyvola
    dotaz na server, stahnou JSON data a podle nich se zaktualizuje stranka.
    To co prijde ze serveru se ulozi do tohoto atributu, at se priste JSON
    dotaz nemusi znovu podavat.
  */
  EXTREMS = {};
  GEO_OBJECTS_URLS = {
    region: '/kampan/mf/ajax/kraje/',
    district: '/kampan/mf/ajax/okresy/',
    town: '/kampan/mf/ajax/obce/'
  };
  /*
  Kolekce geografickych objektu, ktere se vyzobly z HTML stranky.
  */
  GeoObjectList = (function() {
    function GeoObjectList() {
      GeoObjectList.__super__.constructor.apply(this, arguments);
    }
    __extends(GeoObjectList, Backbone.Collection);
    GeoObjectList.prototype.model = GeoObject;
    GeoObjectList.prototype.url = GEO_OBJECTS_URLS[PAGE_TYPE];
    GeoObjectList.prototype.initialize = function() {
      this.type = $('#type');
      this.type.bind('change', _.bind(this.redraw, this));
      this.parameter = $('#parameter');
      return this.parameter.bind('change', _.bind(this.redraw, this));
    };
    /*
    Natahne data do kolekce.

    Primarnim zdrojem je tabulka v HTML strance. To co v ni chybi se nasledne
    dososne ze serveru.
    */
    GeoObjectList.prototype.fetch = function() {
      log('GeoObjectList.fetch:start');
      this.scrapePage();
      this.fetchExtras();
      return log('GeoObjectList.fetch:done');
    };
    /*
    Natahne extra data ze serveru a prilepi je ke stavajicim polozkam v kolekci.
    */
    GeoObjectList.prototype.fetchExtras = function() {
      var options, url;
      log('GeoObjectList.fetchExtras:ready to launch request');
      url = PAGE_TYPE === 'town' ? "" + this.url + (parseUrl().town) + "/" : this.url;
      options = {
        url: url,
        success: __bind(function(resp, status, xhr) {
          log('GeoObjectList.fetchExtras:extras data loaded');
          this.each(function(gobj) {
            var data;
            data = {};
            _.each(resp.details[gobj.get('slug')], function(value, key) {
              return data[key] = value;
            });
            return gobj.set(data);
          });
          log("GeoObjectList.fetchExtras:collection data succesfully updated (" + this.length + ")");
          return HazardEvents.trigger('GeoObjectList:extras_loaded', this);
        }, this),
        error: function(model, resp, options) {
          return log('GeoObjectList.fetchExtras:extras data loading error');
        }
      };
      return Backbone.sync('read', this, options);
    };
    /*
    Vyzobne z HTML tabulky data a udela z nich kolekci geografickych objektu.
    */
    GeoObjectList.prototype.scrapePage = function() {
      var that;
      log('GeoObjectList.scrapePage:ready to scrape data from HTML to collection');
      that = this;
      $('#statistics tbody tr').each(__bind(function(idx, el) {
        var active, item, slug, statistics, statistics_map, tds, title, tr, url, _i, _len;
        tr = $(el);
        tds = tr.find('td');
        active = tr.hasClass('active');
        slug = tr.attr('id').replace("" + PAGE_TYPE + "_", '');
        title = $.trim($(tds[0]).text());
        url = $(tds[0]).find('a').attr('href');
        statistics = _.map(_.last(tds, 6), function(i) {
          var $i, cls, num_value, parameter, type;
          $i = $(i);
          cls = _.filter($i.attr('class').split(' '), function(y) {
            return $.trim(y).length > 0;
          });
          type = _.intersection(cls, _.keys(TYPES))[0];
          parameter = _.intersection(cls, _.keys(PARAMETERS))[0];
          if (!(type in EXTREMS)) {
            EXTREMS[type] = {};
          }
          if (!(parameter in EXTREMS[type])) {
            EXTREMS[type][parameter] = {
              min: 1000000000000,
              max: 0
            };
          }
          num_value = that.getValue($i.text());
          if (num_value !== void 0) {
            if (num_value > EXTREMS[type][parameter].max) {
              EXTREMS[type][parameter].max = num_value;
            }
            if (num_value < EXTREMS[type][parameter].min) {
              EXTREMS[type][parameter].min = num_value;
            }
          }
          return {
            type: type,
            parameter: parameter,
            value: $.trim($i.text()),
            num_value: num_value
          };
        });
        statistics_map = {};
        for (_i = 0, _len = statistics.length; _i < _len; _i++) {
          item = statistics[_i];
          if (!(item.type in statistics_map)) {
            statistics_map[item.type] = {};
          }
          statistics_map[item.type][item.parameter] = item.num_value;
        }
        return this.add(new GeoObject({
          title: title,
          slug: slug,
          statistics: statistics,
          statistics_map: statistics_map,
          url: url,
          active: active,
          type: PAGE_TYPE
        }));
      }, this));
      return log('GeoObjectList.scrapePage:found #{ @length } records on page; scraping is done');
    };
    GeoObjectList.prototype.getValue = function(str) {
      var text;
      text = $.trim(str.replace(',', '.').replace('%', ''));
      if (text.length) {
        return parseFloat(text);
      } else {
        return;
      }
    };
    GeoObjectList.prototype.redraw = function() {
      log('GeoObjectList.redraw:start');
      this.each(function(gobj) {
        return gobj.trigger('change');
      });
      log('GeoObjectList.redraw:done');
      return this.trigger('GeoObjectList:redraw_done');
    };
    GeoObjectList.prototype.active = function() {
      return this.filter(function(gobj) {
        return gobj.get('active');
      });
    };
    return GeoObjectList;
  })();
  /*
  Uvodni text.
  */
  PrimerView = (function() {
    function PrimerView() {
      PrimerView.__super__.constructor.apply(this, arguments);
    }
    __extends(PrimerView, Backbone.View);
    PrimerView.prototype.initialize = function() {
      this.collection.bind('TableRowView:page_fragments_changed', this.render, this);
      this.collection.bind('GeoObjectList:redraw_done', this.render, this);
      return this.type = $('#type');
    };
    PrimerView.prototype.render = function() {
      var type;
      log('PrimerView.render');
      type = this.type.val();
      this.el.find('.snippet').each(function() {
        var snippet;
        snippet = $(this);
        if (snippet.hasClass(type)) {
          return snippet.removeClass('hide');
        } else {
          return snippet.addClass('hide');
        }
      });
      return this;
    };
    return PrimerView;
  })();
  /*
  Jeden radek tabulky == jeden kraj/okres/obec.

  Kazdemu radku odpovida nejaky graficky objekt v mape, se kterym pak spolecne
  reaguje na udalosti od uzivatele (hover, click).
  */
  TableRowView = (function() {
    function TableRowView() {
      TableRowView.__super__.constructor.apply(this, arguments);
    }
    __extends(TableRowView, Backbone.View);
    TableRowView.prototype.events = {
      "mouseover": "mouseover",
      "mouseout": "mouseout",
      "click": "click",
      "dblclick": "dblclick"
    };
    TableRowView.prototype.initialize = function() {
      this.model.bind('change:hover', this.renderHover, this);
      this.model.bind('change:active', this.renderActiveAndColor, this);
      this.model.bind('change:color', this.renderActiveAndColor, this);
      this.model.bind('change', this.render, this);
      return this.model.bind('TableRowView:page_fragments_prepared', this.renderFragments, this);
    };
    TableRowView.prototype.renderHover = function() {
      log('TableRowView.renderHover');
      this.el.toggleClass('hover');
      if (this.el.hasClass('hover')) {
        return this.updateGObject('hover');
      } else {
        if (this.model.get('active')) {
          return this.updateGObject('active');
        } else {
          return this.updateGObject('normal');
        }
      }
    };
    TableRowView.prototype.renderActiveAndColor = function() {
      var changed;
      log('TableRowView.renderActiveAndColor');
      changed = _.keys(this.model.changedAttributes() || {});
      if (__indexOf.call(changed, 'active') >= 0) {
        this.el.toggleClass('active');
      }
      if (this.el.hasClass('active')) {
        if (this.el.hasClass('hover')) {
          return this.updateGObject('hover');
        } else {
          return this.updateGObject('active');
        }
      } else {
        return this.updateGObject('normal');
      }
    };
    TableRowView.prototype.renderFragments = function() {
      var fragments;
      fragments = this.model.get('json_fragments');
      $('#breadcrumb').html(fragments.breadcrumb);
      $('#primer').html(fragments.primer_content);
      $('h1').text(this.model.get('title'));
      return this.model.trigger('TableRowView:page_fragments_changed');
    };
    TableRowView.prototype.render = function() {
      var changed, content, context, ignore;
      log('TableRowView.render');
      ignore = ['hover', 'active', 'shape', 'poly', 'color', 'json_fragments'];
      changed = _.keys(this.model.changedAttributes() || []);
      if (changed.length && _.all(changed, function(i) {
        return __indexOf.call(ignore, i) >= 0;
      })) {
        log('TableRowView.render:shortcut');
        return this;
      }
      context = this.model.toJSON();
      _.extend(context, {
        type: this.collection.type.val(),
        parameter: this.collection.parameter.val()
      });
      content = _.template($('#gobj-item-template').html(), context);
      this.el.html(content);
      return this;
    };
    TableRowView.prototype.drawGObject = function() {
      var i, item, poly, shape, update_timeout;
      log('TableRowView.drawGObject');
      shape = this.model.get('shape');
      poly = new google.maps.Polygon({
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
        strokeColor: MAP_ACTIVE_POLY_COLOR,
        strokeOpacity: 1,
        strokeWeight: 2,
        fillColor: MAP_ACTIVE_POLY_COLOR,
        fillOpacity: 1,
        zIndex: MAP_POLY_ZINDEX,
        map: MAP
      });
      google.maps.event.addListener(poly, 'mouseover', __bind(function() {
        $('#statistics').parent().stop().scrollTo("#" + PAGE_TYPE + "_" + (this.model.get('slug')), 200, {
          stop: true
        });
        return this.el.trigger('mouseover');
      }, this));
      google.maps.event.addListener(poly, 'mouseout', __bind(function() {
        return this.el.trigger('mouseout');
      }, this));
      update_timeout = null;
      google.maps.event.addListener(poly, 'click', __bind(function() {
        return update_timeout = setTimeout(__bind(function() {
          return this.el.trigger('click');
        }, this), 300);
      }, this));
      google.maps.event.addListener(poly, 'dblclick', __bind(function() {
        clearTimeout(update_timeout);
        return this.el.trigger('dblclick');
      }, this));
      this.model.set({
        poly: poly
      });
      return poly;
    };
    TableRowView.prototype.updateGObject = function(state) {
      var color, options, poly;
      color = this.model.get('color');
      log("TableRowView.updateGObject:state=" + state + ", color=" + color);
      if (!('MapDrawingAllowed' in EVENTS_CACHE)) {
        log("TableRowView.updateGObject:map drawing is disallowed now");
        return;
      }
      poly = this.model.get('poly') || this.drawGObject();
      if (!poly) {
        log("TableRowView.updateGObject:no geo object to update");
        return;
      }
      if (state === 'hover') {
        options = {
          fillColor: MAP_HOVER_POLY_COLOR,
          strokeColor: MAP_HOVER_POLY_COLOR,
          zIndex: MAP_POLY_ZINDEX
        };
      } else if (state === 'active') {
        options = {
          fillColor: color,
          strokeColor: MAP_ACTIVE_POLY_COLOR,
          zIndex: MAP_ACTIVE_POLY_ZINDEX
        };
      } else {
        options = {
          fillColor: color,
          strokeColor: color,
          zIndex: MAP_POLY_ZINDEX
        };
      }
      poly.setOptions(options);
      return log('TableRowView.updateGObject:done');
    };
    TableRowView.prototype.mouseover = function() {
      return this.model.set({
        hover: true
      });
    };
    TableRowView.prototype.mouseout = function() {
      return this.model.set({
        hover: false
      });
    };
    TableRowView.prototype.click = function() {
      var $h1, json_fragments, options, prepare_fragments;
      json_fragments = this.model.get('json_fragments');
      $h1 = $('h1');
      prepare_fragments = __bind(function(resp, status, xhr) {
        if (!json_fragments) {
          this.model.set({
            json_fragments: resp
          });
        }
        this.model.trigger('TableRowView:page_fragments_prepared');
        Backbone.history.navigate(this.el.find('a').attr('href'));
        return $h1.removeClass('loading');
      }, this);
      if (!json_fragments) {
        $h1.addClass('loading');
        options = {
          url: this.el.find('a').attr('href'),
          success: prepare_fragments
        };
        Backbone.sync('read', this, options);
      } else {
        prepare_fragments(json_fragments);
      }
      _.each(this.collection.active(), function(gobj) {
        return gobj.set({
          active: false
        });
      });
      this.model.set({
        active: true
      });
      return false;
    };
    TableRowView.prototype.dblclick = function() {
      var url;
      $('h1').addClass('loading');
      url = this.el.find('a').attr('href');
      url = "" + (url.replace('/kampan/mf/', '')) + "/_/";
      window.location = url;
      return false;
    };
    return TableRowView;
  })();
  /*
  Tabulka kraju/okresu/mest.
  */
  TableView = (function() {
    function TableView() {
      TableView.__super__.constructor.apply(this, arguments);
    }
    __extends(TableView, Backbone.View);
    TableView.prototype.initialize = function() {
      this.type = $('#type');
      this.parameter = $('#parameter');
      return this.collection.bind('GeoObjectList:redraw_done', this.render, this);
    };
    /*
    Projede tabulku s regiony a interpretuje hodnotu v druhem sloupci do podoby
    grafu (napozicuje obrazek na pozadi radku tabulky).

    Poznamka: tato metoda je povesena na udalost "GeoObjectList:redraw_done",
    kterou odpaluje kolekce GeoObjectList na konci metody redraw.
    Puvodne jsem si myslel, ze tuhle funkcionalitu bude delat primo TableRowView,
    ale nejde to. Nejdrive je totiz treba vykreslit vsechny radky tabulky
    (tj. TableRowView.render) a teprve **potom** muzu kreslit grafy. Duvod je
    ten, ze dynamicky nalevany obsah sibuje s rozmery bunek a pro vykresleni
    grafu potrebuji znat jejich rozmery.
    */
    TableView.prototype.render = function() {
      var max, min, parameter, td1_w, td2_w, type, width;
      log('TableView.render');
      width = this.el.width();
      td1_w = this.el.find('tr:not(.hide) td:first').width();
      td2_w = width - td1_w;
      type = this.type.val();
      parameter = this.parameter.val();
      max = parameter === 'conflict_perc' ? 100 : EXTREMS[type][parameter].max;
      min = 0;
      log(this.collection.length);
      this.collection.each(__bind(function(gobj, idx) {
        var $td1, $td2, $tr, color, statistics_map, w, x1, x2;
        $tr = this.$("tr:eq(" + idx + ")");
        $td1 = $tr.find('td:first');
        $td2 = $tr.find(":not(:first):not(.hide)");
        statistics_map = gobj.get('statistics_map');
        if (statistics_map[type][parameter] !== void 0) {
          w = Math.round((statistics_map[type][parameter] - min) / max * width);
          if (w > td1_w) {
            x1 = 1000;
            x2 = w - td1_w;
          } else {
            x1 = w;
            x2 = 0;
          }
        } else {
          x1 = 0;
          x2 = 0;
        }
        $td1.css('background-position', "" + x1 + "px 0");
        $td2.css('background-position', "" + x2 + "px 0");
        if (statistics_map[type][parameter] !== void 0) {
          color = get_color(type, (statistics_map[type][parameter] - EXTREMS[type][parameter].min) / EXTREMS[type][parameter].max);
        } else {
          color = get_color(type, 0);
        }
        return gobj.set({
          color: color
        });
      }, this));
      return this;
    };
    return TableView;
  })();
  /*
  Napoveda k mape.
  */
  LegendView = (function() {
    function LegendView() {
      LegendView.__super__.constructor.apply(this, arguments);
    }
    __extends(LegendView, Backbone.View);
    LegendView.prototype.initialize = function() {
      this.type = $('#type');
      this.parameter = $('#parameter');
      return this.collection.bind('GeoObjectList:redraw_done', this.render, this);
    };
    LegendView.prototype.render = function() {
      var content, parameter, type;
      log('LegendView.render');
      type = this.type.val();
      parameter = this.parameter.val();
      this.el.empty();
      content = "" + LEGENDS[PAGE_TYPE][type][parameter] + "<br>" + CONTROL_LEGEND;
      this.el.append(content);
      return this;
    };
    return LegendView;
  })();
  /*
  Aplikace. Hlavni view. Matka matek.
  */
  AppView = (function() {
    function AppView() {
      AppView.__super__.constructor.apply(this, arguments);
    }
    __extends(AppView, Backbone.View);
    AppView.prototype.el = $('#app');
    AppView.prototype.initialize = function() {
      $('h1').addClass('loading');
      log('AppView.initialize:fetch');
      this.options.geo_objects.fetch();
      log('AppView.initialize:TableRowView');
      this.options.geo_objects.each(__bind(function(gobj) {
        new TableRowView({
          model: gobj,
          collection: this.options.geo_objects,
          el: $("#" + PAGE_TYPE + "_" + (gobj.get('slug')))
        });
        return gobj.trigger('change');
      }, this));
      log('AppView.initialize:TableView');
      new TableView({
        el: $("#statistics"),
        collection: this.options.geo_objects
      });
      log('AppView.initialize:PrimerView');
      new PrimerView({
        el: $("#primer"),
        collection: this.options.geo_objects
      });
      log('AppView.initialize:LegendView');
      new LegendView({
        el: $("#legend"),
        collection: this.options.geo_objects
      });
      Backbone.history = new Backbone.History;
      return Backbone.history.start({
        pushState: true
      });
    };
    return AppView;
  })();
  /*
  Upravy HTML stranky.

  Pretaveni statickeho zradlicka pro boty do interaktivni podoby, kterou budou
  pouzivat lidi.
  */
  ModifyHtml = (function() {
    function ModifyHtml() {}
    ModifyHtml.prototype.modify = function() {
      this.modifyTable();
      this.modifyDistrictTable();
      this.injectControl();
      this.injectLegend();
      return this.injectMap();
    };
    ModifyHtml.prototype.modifyTable = function() {
      return $('#statistics thead').remove();
    };
    ModifyHtml.prototype.injectControl = function() {
      var html, makeOption;
      makeOption = function(value, key) {
        return "<option value=\"" + key + "\">" + value + "</option>";
      };
      html = "<p id=\"control\">\n    Zobrazit\n        <select id=\"parameter\">" + (_.map(PARAMETERS, makeOption).join('\n')) + "</select>\n        <select id=\"type\">" + (_.map(TYPES, makeOption).join('\n')) + "</select>\n    <a href=\"#\">Legenda +</a>\n</p>";
      return $('#right-col').append(html);
    };
    ModifyHtml.prototype.injectLegend = function() {
      var html;
      html = '<p id="legend" class="hide"></p>';
      $('#control').after(html);
      return $('#control a').click(function() {
        $('#legend').slideToggle('fast');
        return false;
      });
    };
    ModifyHtml.prototype.injectMap = function() {
      var html, script;
      html = '<div id="map"></div>';
      $('#legend').after(html);
      script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.init_map';
      return document.body.appendChild(script);
    };
    ModifyHtml.prototype.modifyDistrictTable = function() {
      var $link, $table;
      if (PAGE_TYPE === 'district') {
        $table = $('#statistics');
        $table.find('tr').each(function() {
          var $tr, classes, region;
          $tr = $(this);
          classes = _.filter($tr.attr('class').split(' '), function(i) {
            return i.length > 0 && i.indexOf('region_') === 0;
          });
          region = classes[0].replace('region_', '');
          if (region !== parseUrl().region) {
            return $tr.addClass('hide');
          }
        });
        $table.parent().after("<p><i>Poznámka: V tabulce jsou vypsány pouze okresy z aktuálního\nkraje. Chcete raději zobrazit <a href=\"#\" id=\"show-all-districts\">všechny\nokresy ČR</a>?</i></p>");
        $link = $('#show-all-districts');
        return $link.click(function() {
          var first;
          first = $table.find('tr:not(.hide):first');
          $table.find('tr').removeClass('hide');
          $table.parent().stop().scrollTo(first);
          $link.closest('p').fadeOut(200, function() {
            return $(this).remove();
          });
          return false;
        });
      }
    };
    return ModifyHtml;
  })();
  window.init_map = function() {
    MAP = new google.maps.Map(document.getElementById("map"), {
      disableDoubleClickZoom: true,
      scrollwheel: false,
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
    });
    MAP.mapTypes.set('CB', new google.maps.StyledMapType(MAP_STYLE, {
      name: 'Černobílá'
    }));
    return HazardEvents.trigger('Google:map_initialized');
  };
  $(document).ready(function() {
    var App, modify;
    modify = new ModifyHtml;
    modify.modify();
    return App = new AppView({
      geo_objects: new GeoObjectList
    });
  });
}).call(this);
