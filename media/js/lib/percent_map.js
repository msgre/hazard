(function() {
  /*
  TODO:
  */  var Group, MAP_STYLE, draw_entries, init_map, setup;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  window.map = void 0;
  MAP_STYLE = void 0;
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
  TODO:
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
  Custom ikonka, ktera ve sve stredu zobrazuje procenta.

  Pozor! Vzhled ikomny je treba definovat na urovni CSS, napr.:

      .group {
          position:absolute;
          background:url(http://media.parkujujakcyp.cz/hazard/img/percent.png);
          width:40px;
          height:40px;
          font-size:11px;
          font-weight:bold;
          text-align:center;
      }
      .group:hover {
          cursor:pointer;
      }
      .group p {
          padding-top:12px;
      }
  */
  /*
  Konstruktor. Priklad pouziti:

      marker = new Group(data, window.map)

  `data` maji nasledujici strukturu:

      {
              'a': 49.124333,   # latitude
              'o': 16.46354,    # longitude
              'c': 10,          # cislo dovnitr ikony, 10%
              'u': '/d/vsetin/' # URL na stranku s detailem
      }
  */
  Group = function(data, map) {
    this.center_ = [20, 20];
    this.data_ = data;
    this.div_ = null;
    this.visible_ = false;
    this.pos_ = new google.maps.LatLng(data['a'], data['o']);
    this.url = data['u'];
    this.setMap(map);
    return this;
  };
  Group.prototype = new google.maps.OverlayView();
  /*
  Vytvori HTML kod grupoznacky a vlozi ji fyzicky do mapy (zatim ale bez presne
  pozice). Grupa zustava skryta (ma nastaveno CSS display=none), pro jeji
  zobrazeni je nutne volat metodu show).
  */
  Group.prototype.onAdd = function() {
    var count, div, panes;
    div = document.createElement('DIV');
    div.className = "group";
    div.style.display = "none";
    div.title = this.data_['t'];
    count = document.createElement('P');
    count.innerHTML = this.data_['c'];
    div.appendChild(count);
    google.maps.event.addDomListener(div, 'click', __bind(function(ev) {
      console.log('klikanec');
      return window.location = this.url;
    }, this));
    this.div_ = div;
    panes = this.getPanes();
    return panes.overlayMouseTarget.appendChild(div);
  };
  /*
  Vykresli grupu v mape, presne na zadanych souradnicich. Pokud je interni atribut
  @visible_ == false, grupa se nevykresli.
  */
  Group.prototype.draw = function() {
    var overlayProjection, pixel_pos;
    if (this.div_ && this.visible_) {
      this.div_.style.display = "block";
      overlayProjection = this.getProjection();
      pixel_pos = overlayProjection.fromLatLngToDivPixel(this.pos_);
      this.div_.style.left = pixel_pos.x - this.center_[0] + 'px';
      this.div_.style.top = pixel_pos.y - this.center_[1] + 'px';
    }
  };
  /*
  Zobrazi grupu v mape.
  */
  Group.prototype.show = function() {
    this.visible_ = true;
    this.draw();
  };
  /*
  Skryje grupu v mape (fyzicky tam zustava, ale z oci mizi).
  */
  Group.prototype.hide = function() {
    if (this.div_) {
      this.div_.style.display = "none";
      this.visible_ = false;
    }
  };
  /*
  Metoda volana po Group.set_map(null). Postara se o odstraneni HTML elementu z
  mapy a resetu vnitrnich hodnot.
  */
  Group.prototype.onRemove = function() {
    this.div_.parentNode.removeChild(this.div_);
    this.div_ = null;
    this.data_ = null;
    this.visible_ = false;
    return this.pos_ = null;
  };
  /*
  Vrati souradnice stredu grupy.
  */
  Group.prototype.getPosition = function() {
    return this.pos_;
  };
  /*
  Vykresleni zlutych kolecek s procenty protizakonnych heren na mapu CR.
  Toto pozadi je defaultni pro vetsinu stranek s vyjimkou detailu konkretni
  obce.
  */
  draw_entries = function() {
    var data, group, id, _data, _ref, _results;
    _ref = window.perc_entries;
    _results = [];
    for (id in _ref) {
      data = _ref[id];
      _data = {
        'a': data.lat,
        'o': data.lon,
        'c': data.perc,
        't': data.title,
        'u': data.url
      };
      group = new Group(_data, window.map);
      _results.push(group.show());
    }
    return _results;
  };
  $(document).ready(function() {
    setup();
    init_map();
    return draw_entries();
  });
}).call(this);
