(function() {
  var AppView, EXTREMS, HazardEvents, LEGENDS, LegendView, MAP, MAP_ACTIVE_POLY_COLOR, MAP_ACTIVE_POLY_ZINDEX, MAP_HOVER_POLY_COLOR, MAP_POLY_ZINDEX, MAP_SEMAPHORE, ModifyHtml, PARAMETERS, PrimerView, Region, RegionList, RegionRowView, RegionTableView, SEMAPHORE, TYPES, convert_to_hex, convert_to_rgb, get_color, hex, interpolate_color, trim;
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
  };
  MAP_SEMAPHORE = [];
  MAP_POLY_ZINDEX = 10;
  MAP_ACTIVE_POLY_COLOR = '#333333';
  MAP_ACTIVE_POLY_ZINDEX = 20;
  MAP_HOVER_POLY_COLOR = '#333333';
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
  /*
  TODO:
  */
  SEMAPHORE = {};
  HazardEvents = {};
  _.extend(HazardEvents, Backbone.Events);
  HazardEvents.bind('all', function(name, arg) {
    var parts;
    parts = name.split(':');
    if (!(parts[0] in SEMAPHORE)) {
      SEMAPHORE[parts[0]] = {};
    }
    SEMAPHORE[parts[0]][parts[1]] = arg;
    if ('map' in SEMAPHORE && 'extras_loaded' in SEMAPHORE.map && 'init' in SEMAPHORE.map) {
      SEMAPHORE['map']['initialized'] = true;
      SEMAPHORE.map.extras_loaded.trigger('redraw:done');
      delete SEMAPHORE.map.init;
      delete SEMAPHORE.map.extras_loaded;
      return $('h1').removeClass('loading');
    }
  });
  /*
  Popis jednoho kraje.
  */
  Region = (function() {
    function Region() {
      Region.__super__.constructor.apply(this, arguments);
    }
    __extends(Region, Backbone.Model);
    Region.prototype.defaults = {
      hover: false
    };
    return Region;
  })();
  EXTREMS = {};
  /*
  Kolekce vsech kraju v republice.
  */
  RegionList = (function() {
    function RegionList() {
      RegionList.__super__.constructor.apply(this, arguments);
    }
    __extends(RegionList, Backbone.Collection);
    RegionList.prototype.model = Region;
    RegionList.prototype.url = '/kampan/mf/ajax/kraje/';
    RegionList.prototype.initialize = function() {
      this.type = $('#type');
      this.type.bind('change', _.bind(this.redraw, this));
      this.parameter = $('#parameter');
      return this.parameter.bind('change', _.bind(this.redraw, this));
    };
    RegionList.prototype.scrape = function() {
      var that;
      that = this;
      return $('#statistics tbody tr').each(__bind(function(idx, el) {
        var active, item, slug, statistics, statistics_map, tds, title, tr, url, _i, _len;
        tr = $(el);
        tds = tr.find('td');
        active = tr.hasClass('active');
        slug = tr.attr('id').replace('region_', '');
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
          if (num_value > EXTREMS[type][parameter].max) {
            EXTREMS[type][parameter].max = num_value;
          }
          if (num_value < EXTREMS[type][parameter].min) {
            EXTREMS[type][parameter].min = num_value;
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
        return this.add(new Region({
          title: title,
          slug: slug,
          statistics: statistics,
          statistics_map: statistics_map,
          url: url,
          active: active
        }));
      }, this));
    };
    RegionList.prototype.fetch = function() {
      var options;
      options = {
        url: this.url,
        success: __bind(function(resp, status, xhr) {
          this.each(function(region) {
            var data;
            data = {};
            _.each(resp['details'][region.get('slug')], function(value, key) {
              return data[key] = value;
            });
            return region.set(data);
          });
          return HazardEvents.trigger('map:extras_loaded', this);
        }, this)
      };
      return Backbone.sync('read', this, options);
    };
    RegionList.prototype.getValue = function(str) {
      return parseFloat($.trim(str.replace(',', '.').replace('%', '')));
    };
    RegionList.prototype.redraw = function() {
      console.log('redraw');
      this.each(function(region) {
        return region.trigger('change');
      });
      return this.trigger('redraw:done');
    };
    RegionList.prototype.active = function() {
      return this.filter(function(region) {
        return region.get('active');
      });
    };
    return RegionList;
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
      this.type = $('#type');
      this.type.bind('change', _.bind(this.render, this));
      return this.collection.bind('fragments:change', this.render, this);
    };
    PrimerView.prototype.render = function() {
      var type;
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
  Jeden radek tabulky == jeden kraj.
  */
  RegionRowView = (function() {
    function RegionRowView() {
      RegionRowView.__super__.constructor.apply(this, arguments);
    }
    __extends(RegionRowView, Backbone.View);
    RegionRowView.prototype.events = {
      "mouseover": "mouseover",
      "mouseout": "mouseout",
      "click": "click"
    };
    RegionRowView.prototype.initialize = function() {
      this.model.bind('change', this.render, this);
      return this.model.bind('map:update_polys', this.updatePolys, this);
    };
    RegionRowView.prototype.createPolys = function() {
      var i, item, poly, shape;
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
        strokeWeight: 1,
        fillColor: MAP_ACTIVE_POLY_COLOR,
        fillOpacity: 1,
        zIndex: MAP_POLY_ZINDEX,
        map: MAP
      });
      google.maps.event.addListener(poly, 'mouseover', __bind(function() {
        $('#statistics').parent().scrollTo("#region_" + (this.model.get('slug')), 200);
        return this.el.trigger('mouseover');
      }, this));
      google.maps.event.addListener(poly, 'mouseout', __bind(function() {
        return this.el.trigger('mouseout');
      }, this));
      google.maps.event.addListener(poly, 'click', __bind(function() {
        return this.el.trigger('click');
      }, this));
      this.model.set({
        poly: poly
      });
      return poly;
    };
    RegionRowView.prototype.updatePolys = function(options) {
      var poly;
      if (options == null) {
        options = {};
      }
      if ('map' in SEMAPHORE && 'initialized' in SEMAPHORE.map) {
        poly = this.model.get('poly') || this.createPolys();
        return poly.setOptions(options);
      }
    };
    RegionRowView.prototype.render = function() {
      var changed, content, context;
      changed = _.keys(this.model.changedAttributes() || {});
      if ((__indexOf.call(changed, 'shape') >= 0 && changed.length === 1) || (__indexOf.call(changed, 'poly') >= 0 && changed.length === 1)) {
        return this;
      }
      if (__indexOf.call(changed, 'hover') >= 0) {
        this.el.toggleClass('hover');
        if (this.el.hasClass('hover')) {
          this.renderPolys('hover');
        } else {
          if (this.model.get('active')) {
            this.renderPolys('active');
          } else {
            this.renderPolys('normal');
          }
        }
      }
      if (__indexOf.call(changed, 'active') >= 0 || __indexOf.call(changed, 'color') >= 0) {
        if (__indexOf.call(changed, 'active') >= 0) {
          this.el.toggleClass('active');
        }
        if (this.el.hasClass('active')) {
          this.renderPolys('active');
        } else {
          this.renderPolys('normal');
        }
      }
      if (changed.length > 1 || (__indexOf.call(changed, 'hover') < 0 && __indexOf.call(changed, 'active') < 0 && __indexOf.call(changed, 'color') < 0 && __indexOf.call(changed, 'fragments') < 0)) {
        context = this.model.toJSON();
        _.extend(context, {
          type: this.collection.type.val(),
          parameter: this.collection.parameter.val()
        });
        content = _.template($('#region-item-template').html(), context);
        this.el.html(content);
      }
      return this;
    };
    RegionRowView.prototype.renderPolys = function(state) {
      var color;
      color = this.model.get('color');
      if (state === 'hover') {
        return this.model.trigger('map:update_polys', {
          fillColor: MAP_HOVER_POLY_COLOR,
          strokeColor: MAP_HOVER_POLY_COLOR,
          zIndex: MAP_POLY_ZINDEX
        });
      } else if (state === 'active') {
        return this.model.trigger('map:update_polys', {
          fillColor: color,
          strokeColor: MAP_ACTIVE_POLY_COLOR,
          zIndex: MAP_ACTIVE_POLY_ZINDEX
        });
      } else {
        return this.model.trigger('map:update_polys', {
          fillColor: color,
          strokeColor: color,
          zIndex: MAP_POLY_ZINDEX
        });
      }
    };
    RegionRowView.prototype.mouseover = function() {
      return this.model.set({
        hover: true
      });
    };
    RegionRowView.prototype.mouseout = function() {
      return this.model.set({
        hover: false
      });
    };
    RegionRowView.prototype.click = function() {
      var $h1, fragments, options, success;
      fragments = this.model.get('fragments');
      $h1 = $('h1');
      success = __bind(function(resp, status, xhr) {
        if (!fragments) {
          this.model.set({
            fragments: resp
          });
        }
        $('#breadcrumb').html(resp.breadcrumb);
        $('h1').text(this.model.get('title'));
        $('#primer').html(resp.primer_content);
        this.model.trigger('fragments:change');
        Backbone.history.navigate("/" + (this.model.get('slug')) + "/kampan/mf/");
        return $h1.removeClass('loading');
      }, this);
      if (!fragments) {
        $h1.addClass('loading');
        options = {
          url: this.el.find('a').attr('href'),
          success: success
        };
        Backbone.sync('read', this, options);
      } else {
        success(fragments);
      }
      _.each(this.collection.active(), function(region) {
        return region.set({
          active: false
        });
      });
      this.model.set({
        active: true
      });
      return false;
    };
    return RegionRowView;
  })();
  /*
  Tabulka kraju.
  */
  RegionTableView = (function() {
    function RegionTableView() {
      RegionTableView.__super__.constructor.apply(this, arguments);
    }
    __extends(RegionTableView, Backbone.View);
    RegionTableView.prototype.initialize = function() {
      this.type = $('#type');
      this.parameter = $('#parameter');
      return this.collection.bind('redraw:done', this.render, this);
    };
    /*
    Projede tabulku s regiony a interpretuje hodnotu v druhem sloupci do podoby
    grafu (napozicuje obrazek na pozadi radku tabulky).

    Poznamka: tato metoda je povesena na udalost "redraw:done", kterou odpaluje
    kolekce RegionList na konci metody redraw.
    Puvodne jsem si myslel, ze tuhle funkcionalitu bude delat primo RegionRowView,
    ale nejde to. Nejdrive je totiz treba vykreslit vsechny radky tabulky
    (tj. RegionRowView.render) a teprve **potom** muzu kreslit grafy. Duvod je
    ten, ze dynamicky nalevany obsah sibuje s rozmery bunek a pro vykresleni
    grafu potrebuji znat jejich rozmery.
    */
    RegionTableView.prototype.render = function() {
      var max, parameter, td1_w, td2_w, type, width;
      width = this.el.width();
      td1_w = this.el.find('td:first').width();
      td2_w = width - td1_w;
      type = this.type.val();
      parameter = this.parameter.val();
      max = parameter === 'conflict_perc' ? 100 : EXTREMS[type][parameter].max;
      this.collection.each(__bind(function(region, idx) {
        var $td1, $td2, $tr, color, statistics_map, w, x1, x2;
        $tr = this.$("tr:eq(" + idx + ")");
        $td1 = $tr.find('td:first');
        $td2 = $tr.find(":not(:first):not(.hide)");
        statistics_map = region.get('statistics_map');
        w = Math.round(statistics_map[type][parameter] / max * width);
        if (w > td1_w) {
          x1 = 1000;
          x2 = w - td1_w;
        } else {
          x1 = w;
          x2 = 0;
        }
        $td1.css('background-position', "" + x1 + "px 0");
        $td2.css('background-position', "" + x2 + "px 0");
        color = get_color(type, (statistics_map[type][parameter] - EXTREMS[type][parameter].min) / EXTREMS[type][parameter].max);
        return region.set({
          color: color
        });
      }, this));
      return this;
    };
    return RegionTableView;
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
      this.parameter.bind('change', _.bind(this.render, this));
      return this.type.bind('change', _.bind(this.render, this));
    };
    LegendView.prototype.render = function() {
      var parameter, type;
      type = this.type.val();
      parameter = this.parameter.val();
      this.el.empty();
      this.el.append(LEGENDS[type][parameter]);
      return this;
    };
    return LegendView;
  })();
  /*
  Aplikace.
  */
  AppView = (function() {
    function AppView() {
      AppView.__super__.constructor.apply(this, arguments);
    }
    __extends(AppView, Backbone.View);
    AppView.prototype.el = $('#app');
    AppView.prototype.initialize = function() {
      $('h1').addClass('loading');
      this.options.regions.scrape();
      this.options.regions.fetch();
      this.options.regions.each(__bind(function(region) {
        var view;
        view = new RegionRowView({
          model: region,
          collection: this.options.regions,
          el: $("#region_" + (region.get('slug')))
        });
        return region.trigger('change');
      }, this));
      new RegionTableView({
        el: $("#statistics"),
        collection: this.options.regions
      });
      new PrimerView({
        el: $("#primer"),
        collection: this.options.regions
      });
      new LegendView({
        el: $("#legend")
      });
      Backbone.history = new Backbone.History;
      return Backbone.history.start({
        pushState: true
      });
    };
    return AppView;
  })();
  /*
  TODO:

  - nacist informace o krajich z JSONu ze serveru
  */
  /*
  Upravy HTML stranky.

  Pretaveni statickeho zradlicka pro boty do interaktivni podoby, kterou budou
  pouzivat lidi.
  */
  ModifyHtml = (function() {
    function ModifyHtml() {}
    ModifyHtml.prototype.modify = function() {
      this.modifyTable();
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
      script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map';
      return document.body.appendChild(script);
    };
    return ModifyHtml;
  })();
  MAP = void 0;
  window.late_map = function() {
    var map_options;
    map_options = {
      zoom: 6,
      center: new google.maps.LatLng(49.38512, 14.61765),
      mapTypeControl: false,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      streetViewControl: false,
      panControl: false,
      zoomControl: true,
      zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SMALL
      }
    };
    MAP = new google.maps.Map(document.getElementById("map"), map_options);
    return HazardEvents.trigger('map:init');
  };
  $(document).ready(function() {
    var App, Regions, modify;
    modify = new ModifyHtml;
    modify.modify();
    Regions = new RegionList;
    return App = new AppView({
      regions: Regions
    });
  });
}).call(this);
