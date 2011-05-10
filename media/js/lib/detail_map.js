(function() {
  /*
  Obecny kod, ktery je vyuzivan jak v detailech obci, tak i na ostatnich strankach.
  */  var BUBBLE_POLYGONS, BUILDINGS, FILL_OPTIONS, FILL_Z_INDEX, HOVERED_PIN_Z_INDEX, ICONS, IW, MAP_STYLE, MARKERS, MC_STYLE, MEDIA_URL, OPENED, PIN_Z_INDEX, ZONES, clear_buildings, clear_zones, click_handler, dimm_hell, draw_buildings, draw_hells, draw_zones, init_fancybox, init_map, mouseout_hell, mouseover_hell, open_upload_fancybox, setup, setup_detail, shine_hell, submit, upload_fancybox_opened;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  window.map = void 0;
  MAP_STYLE = void 0;
  MEDIA_URL = 'http://media.parkujujakcyp.cz/hazard/';
  /*
  Nakonfigurovani stylu mapy.
  */
  setup = function() {
    return MAP_STYLE = [
      {
        featureType: "landscape",
        elementType: "all",
        stylers: [
          {
            saturation: -60
          }
        ]
      }, {
        featureType: "road",
        elementType: "all",
        stylers: [
          {
            saturation: -100
          }
        ]
      }, {
        featureType: "water",
        elementType: "all",
        stylers: [
          {
            saturation: -60
          }
        ]
      }, {
        featureType: "transit",
        elementType: "all",
        stylers: [
          {
            saturation: -100
          }
        ]
      }, {
        featureType: "poi",
        elementType: "all",
        stylers: [
          {
            saturation: -100
          }
        ]
      }
    ];
  };
  /*
  Serepeticky kvuli fancyboxu -- kdyz jsem ho volal na submit udalost, nestihl
  si nacist obrazky z CSSka a progress bar uvnitr taky chybel. Proto to delam
  tak ze submit nejprve nahodi fancybox, a teprve po sekunde dojde ke skutecnemu
  odeslani formulare.
  */
  upload_fancybox_opened = false;
  open_upload_fancybox = function() {
    upload_fancybox_opened = true;
    return $.fancybox({
      title: 'Uno momento',
      content: '<p><b>Vaše mapy se právě nahrávají na server a chvíli to potrvá</b></p><p><img src="' + MEDIA_URL + 'img/ajax-loader.gif"></p><p><em>Pro hrubou orientaci: Brno s cca 300 hernami trvá téměř 3 minuty.</em></p>',
      modal: true
    });
  };
  submit = function() {
    return $('form').submit();
  };
  /*
  Inicializace fancyboxu (vrstvy pro zobrazovani vetsich obrazku a modalnich
  oken).
  */
  init_fancybox = function() {
    var img;
    $("a.fb").fancybox();
    if ($('#upload_maps').length) {
      img = $('<img>').attr('src', MEDIA_URL + 'img/ajax-loader.gif');
      return $('form').submit(function() {
        var t;
        if (!upload_fancybox_opened) {
          open_upload_fancybox();
          t = setTimeout(submit, 1000);
          return false;
        } else {
          return true;
        }
      });
    }
  };
  /*
  Inicializace mapy.
  */
  init_map = function() {
    var center, map_options, styledMapType;
    $('body').height($(window).height() + 'px');
    if (!(window.map != null)) {
      map_options = {
        backgroundColor: '#ffffff',
        mapTypeControlOptions: {
          mapTypeIds: ['CB', google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.ROADMAP]
        },
        mapTypeId: 'CB',
        noClear: true,
        mapTypeControl: true,
        panControl: false,
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP
        }
      };
      window.map = new google.maps.Map(document.getElementById("body"), map_options);
      styledMapType = new google.maps.StyledMapType(MAP_STYLE, {
        name: 'Černobílá'
      });
      window.map.mapTypes.set('CB', styledMapType);
    }
    center = new google.maps.LatLng(49.38512, 14.61765);
    window.map.setCenter(center);
    return window.map.setZoom(7);
  };
  /*
  TODO:
  */
  PIN_Z_INDEX = 10;
  HOVERED_PIN_Z_INDEX = 20;
  FILL_Z_INDEX = 14;
  FILL_OPTIONS = {};
  ICONS = {};
  MARKERS = {};
  BUILDINGS = [];
  ZONES = [];
  BUBBLE_POLYGONS = [];
  OPENED = void 0;
  IW = void 0;
  MC_STYLE = {};
  /*
  Nakonfigurovani stylu a ikon.
  */
  setup_detail = function() {
    FILL_OPTIONS['building'] = {
      strokeWeight: 0,
      strokeColor: '#000000',
      strokeOpacity: .01,
      fillColor: '#ffffff',
      fillOpacity: 1,
      zIndex: FILL_Z_INDEX
    };
    FILL_OPTIONS['zone'] = {
      strokeWeight: 0,
      strokeColor: '#000000',
      strokeOpacity: .01,
      fillColor: '#000000',
      fillOpacity: .7,
      zIndex: FILL_Z_INDEX - 1
    };
    FILL_OPTIONS['building_hovered'] = {
      strokeWeight: 0,
      strokeColor: '#000000',
      strokeOpacity: .01,
      fillColor: '#000000',
      fillOpacity: .9,
      zIndex: FILL_Z_INDEX + 2
    };
    FILL_OPTIONS['zone_hovered'] = {
      strokeWeight: 0,
      strokeColor: '#e53404',
      strokeOpacity: .01,
      fillColor: '#e53404',
      fillOpacity: .9,
      zIndex: FILL_Z_INDEX + 1
    };
    ICONS['allowed'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/yes.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['allowed_dimmed'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/yes_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['allowed_hovered'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/yes_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['disallowed'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/no.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['disallowed_dimmed'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/no_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['disallowed_hovered'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/no_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14));
    ICONS['shadow'] = new google.maps.MarkerImage('http://media.parkujujakcyp.cz/hazard/img/shadow.png', new google.maps.Size(27, 14), new google.maps.Point(0, 0), new google.maps.Point(8, 0));
    MC_STYLE = {
      url: 'http://media.parkujujakcyp.cz/hazard/img/group.png',
      height: 40,
      width: 40,
      opt_anchor: [20, 20],
      opt_textColor: '#ffffff',
      opt_textSize: 11
    };
    $('#detailed_info').wrapInner('<a href="#" id="detailed_info_link"></a>').next().hide();
    $('#detailed_info_link').click(function() {
      $(this).closest('p').next().toggle();
      return false;
    });
    return false;
  };
  /*
  Vykresleni budov, ktere sousedi s hernou (znackou) `that`.
  */
  draw_buildings = function(that) {
    var building, i, path, poly, _i, _len, _ref, _results;
    _ref = that._data.buildings;
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      building = _ref[_i];
      path = (function() {
        var _i, _len, _ref, _results;
        _ref = window.buildings[building].polygon;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push(new google.maps.LatLng(i[1], i[0]));
        }
        return _results;
      })();
      poly = new google.maps.Polygon(FILL_OPTIONS['building']);
      poly.setPath(path);
      poly.setMap(window.map);
      _results.push(BUILDINGS.push(poly));
    }
    return _results;
  };
  /*
  Smazani budov, ktere sousedi s hernou (znackou) `that`.
  */
  clear_buildings = function() {
    var building, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = BUILDINGS.length; _i < _len; _i++) {
      building = BUILDINGS[_i];
      _results.push(building.setMap(null));
    }
    return _results;
  };
  /*
  Vykresleni okoli budov (zon), ktere sousedi s hernou (znackou) `that`.
  */
  draw_zones = function(that) {
    var i, path, poly;
    if (that._data.uzone.length) {
      path = (function() {
        var _i, _len, _ref, _results;
        _ref = that._data.uzone;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push(new google.maps.LatLng(i[1], i[0]));
        }
        return _results;
      })();
      poly = new google.maps.Polygon(FILL_OPTIONS['zone']);
      poly.setPath(path);
      poly.setMap(window.map);
      return ZONES.push(poly);
    }
  };
  /*
  Smazani okoli budov (zon), ktere sousedi s hernou (znackou) `that`.
  */
  clear_zones = function() {
    var zone, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = ZONES.length; _i < _len; _i++) {
      zone = ZONES[_i];
      _results.push(zone.setMap(null));
    }
    return _results;
  };
  /*
  Ztlumeni vsech heren (znacek) na mape, s vyjimkou herny (znacky) `orig`.
  */
  dimm_hell = function(orig) {
    var id, marker, _results;
    _results = [];
    for (id in MARKERS) {
      marker = MARKERS[id];
      if (orig === marker) {
        continue;
      }
      _results.push(marker.setIcon(ICONS[marker._data['dimm_image']]));
    }
    return _results;
  };
  /*
  Zruseni ztlumeni vsech heren (znacek) na mape, s vyjimkou herny (znacky) `orig`.
  */
  shine_hell = function(orig) {
    var id, marker, _results;
    _results = [];
    for (id in MARKERS) {
      marker = MARKERS[id];
      if (orig === marker) {
        continue;
      }
      _results.push(marker.setIcon(ICONS[marker._data['image']]));
    }
    return _results;
  };
  /*
  Mys najela nad hernu -- zobrazime okolni budovy a zony v konfliktu a vsecky
  ostatni herny pozhasiname.
  */
  mouseover_hell = function() {
    this.setIcon(ICONS[this._data['image'] + '_hovered']);
    this.setZIndex(HOVERED_PIN_Z_INDEX);
    if (OPENED) {
      return;
    }
    if (!this._data.conflict) {
      return;
    }
    draw_zones(this);
    return draw_buildings(this);
  };
  /*
  Mys z herny odjela -- zrusime polygony zon/budov a zase rozneme ostatni herny.
  */
  mouseout_hell = function() {
    var icon_name;
    icon_name = this._data['image'];
    this.setZIndex(PIN_Z_INDEX);
    if (OPENED || !this._data.conflict) {
      if (this !== OPENED) {
        if (OPENED) {
          icon_name = this._data['dimm_image'];
        }
        this.setZIndex(PIN_Z_INDEX);
      } else {
        icon_name = this._data['image'] + '_hovered';
        this.setZIndex(HOVERED_PIN_Z_INDEX);
      }
    }
    this.setIcon(ICONS[icon_name]);
    if (OPENED) {
      return;
    }
    clear_buildings();
    return clear_zones();
  };
  /*
  Mys nad titulkem verejne budovy v bubline -- zvyraznime danou budovu i jeji okoli.
  */
  window.mouseover_bubble_building = function(el) {
    var building, i, path1, path2, poly1, poly2;
    building = $(el).attr('id').replace('b-', '');
    path2 = (function() {
      var _i, _len, _ref, _results;
      _ref = window.zones[window.buildings[building].zone].polygon;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        _results.push(new google.maps.LatLng(i[1], i[0]));
      }
      return _results;
    })();
    poly2 = new google.maps.Polygon(FILL_OPTIONS['zone_hovered']);
    poly2.setPath(path2);
    poly2.setMap(window.map);
    BUBBLE_POLYGONS.push(poly2);
    path1 = (function() {
      var _i, _len, _ref, _results;
      _ref = window.buildings[building].polygon;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        _results.push(new google.maps.LatLng(i[1], i[0]));
      }
      return _results;
    })();
    poly1 = new google.maps.Polygon(FILL_OPTIONS['building_hovered']);
    poly1.setPath(path1);
    poly1.setMap(window.map);
    return BUBBLE_POLYGONS.push(poly1);
  };
  /*
  Mys odjela z titulku verejne budovy v bubline -- pryc se zvyraznujicima polygonama.
  */
  window.mouseout_bubble_building = function(el) {
    var bp, _i, _len;
    for (_i = 0, _len = BUBBLE_POLYGONS.length; _i < _len; _i++) {
      bp = BUBBLE_POLYGONS[_i];
      bp.setMap(null);
    }
    return BUBBLE_POLYGONS = [];
  };
  /*
  Kliknuti nad hernou -- zobrazime bublinu s popisem.
  */
  click_handler = function(ev) {
    var building, content, _i, _len, _ref;
    if (OPENED) {
      OPENED = null;
      google.maps.event.trigger(this, 'mouseout', [ev, this]);
      google.maps.event.trigger(this, 'mouseover', [ev, this]);
    }
    OPENED = this;
    if (IW) {
      IW.close();
    }
    dimm_hell(this);
    content = '<h4>' + this._data.title + '</h4>';
    if (this._data.description && !/^#style\d+$/.test(this._data.description)) {
      content += this._data.description;
    }
    if (this._data.conflict) {
      content += '<p>Provoz herny <strong>je v rozporu se zákonem</strong>, protože v jejím okolí se nalézají tyto budovy:</p>';
      content += '<ul>';
      _ref = this._data.buildings;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        building = _ref[_i];
        content += '<li><a id="b-' + building + '" onmouseover="javascript:window.mouseover_bubble_building(this)" onmouseout="javascript:window.mouseout_bubble_building(this)">' + window.buildings[building].title + '</a></li>';
      }
      content += '</ul>';
      content += '<p><em>Tip: konkrétní veřejná budova se v mapě zvýrazní, pokud najedete myší nad její název uvedený v seznamu výše</em></p>';
    } else {
      content += '<p>V okolí herny se nenalézá žádná veřejná budova, její provoz není v rozporu se zákonem.</p>';
    }
    IW = new google.maps.InfoWindow({
      content: content,
      maxWidth: 300
    });
    IW.open(window.map, this);
    return google.maps.event.addListener(IW, 'closeclick', __bind(function(ev2) {
      OPENED = null;
      google.maps.event.trigger(this, 'mouseout', [ev2, this]);
      return shine_hell(this);
    }, this));
  };
  /*
  Vykresleni vsech heren.
  */
  draw_hells = function() {
    var bounds, data, i, id, marker_cluster, ne, sw, _ref;
    sw = [1000, 1000];
    ne = [0, 0];
    _ref = window.hells;
    for (id in _ref) {
      data = _ref[id];
      if (data.conflict) {
        data['image'] = 'disallowed';
      } else {
        data['image'] = 'allowed';
      }
      if (data.pos[1] < sw[0]) {
        sw[0] = data.pos[1];
      }
      if (data.pos[1] > ne[0]) {
        ne[0] = data.pos[1];
      }
      if (data.pos[0] < sw[1]) {
        sw[1] = data.pos[0];
      }
      if (data.pos[0] > ne[1]) {
        ne[1] = data.pos[0];
      }
      MARKERS[id] = new google.maps.Marker({
        position: new google.maps.LatLng(data.pos[1], data.pos[0]),
        title: data.title,
        icon: ICONS[data['image']],
        shadow: ICONS['shadow'],
        zIndex: PIN_Z_INDEX
      });
      data['dimm_image'] = data['image'] + '_dimmed';
      MARKERS[id]._data = data;
      google.maps.event.addListener(MARKERS[id], 'mouseover', mouseover_hell);
      google.maps.event.addListener(MARKERS[id], 'mouseout', mouseout_hell);
      google.maps.event.addListener(MARKERS[id], 'click', click_handler);
    }
    marker_cluster = new MarkerClusterer(window.map, (function() {
      var _results;
      _results = [];
      for (i in MARKERS) {
        _results.push(MARKERS[i]);
      }
      return _results;
    })(), {
      maxZoom: 14,
      gridSize: 50,
      styles: [MC_STYLE, MC_STYLE, MC_STYLE]
    });
    if (window.hells) {
      bounds = new google.maps.LatLngBounds(new google.maps.LatLng(sw[0], sw[1]), new google.maps.LatLng(ne[0], ne[1]));
      google.maps.event.addListenerOnce(window.map, 'idle', function() {
        return window.map.panBy(-160, 0);
      });
      return window.map.fitBounds(bounds);
    }
  };
  $(document).ready(function() {
    setup();
    setup_detail();
    init_map();
    init_fancybox();
    return draw_hells();
  });
}).call(this);
