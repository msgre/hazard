(function() {
  /*
  Obecny kod, ktery je vyuzivan jak v detailech obci, tak i na ostatnich strankach.
  */  var Group, MAP_STYLE, MEDIA_URL, draw_entries, hide_messages, init_fancybox, init_map, open_upload_fancybox, setup, submit, upload_fancybox_opened;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  window.map = void 0;
  MAP_STYLE = void 0;
  MEDIA_URL = 'http://media.mapyhazardu.cz/';
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
      content: '<p><b>Vaše mapy se právě nahrávají na server a chvíli to potrvá. Vydržte!</b></p><p><img src="' + MEDIA_URL + 'img/ajax-loader.gif"></p>',
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
    if ($('#upload_maps').length || $('#join_us').length) {
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
    var center, map_options, open, speed, styledMapType;
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
    window.map.setZoom(7);
    open = true;
    speed = 120;
    return $('#hide a').click(function() {
      var height, opacity;
      $('#inner_box').slideToggle(speed);
      if (open) {
        height = '120px';
        opacity = .8;
      } else {
        height = '80%';
        opacity = 1;
      }
      $('#info_box').animate({
        height: height,
        opacity: opacity
      }, speed);
      open = !open;
      return false;
    });
  };
  /*
  Kliknuti na jakykoliv odkaz v info_boxu skryje provozni hlasku.
  */
  hide_messages = function() {
    return $('#info_box a').click(function() {
      var $messages;
      $messages = $('#messages');
      if ($messages.length) {
        return $messages.fadeOut(100, function() {
          return $messages.remove();
        });
      }
    });
  };
  /*
  Custom ikonka, ktera ve sve stredu zobrazuje procenta.

  Pozor! Vzhled ikony je treba definovat na urovni CSS, napr.:

      .group {
          position:absolute;
          background:url(http://media.mapyhazardu.cz/img/percent.png);
          width:40px;
          height:40px;
          font-size:11px;
          font-weight:bold;
          text-align:center;
      }
      .group p {
          padding-top:12px;
      }

  Nad ikonou se vykresluje pruhledny DIV, ktery zachytava klikani mysi. Musi
  byt stejne velky, jako ikona. Napr.:

      .slide {
          position:absolute;
          width:40px;
          height:40px;
      }
      .slide:hover {
          cursor:pointer;
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
    this.icon_ = null;
    this.slide_ = null;
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
    var count, icon, panes, slide;
    icon = document.createElement('DIV');
    icon.className = "group";
    icon.style.display = "none";
    icon.title = this.data_['t'];
    count = document.createElement('P');
    count.innerHTML = this.data_['c'];
    icon.appendChild(count);
    slide = document.createElement('DIV');
    slide.className = "slide";
    slide.style.display = "none";
    $(slide).tipsy({
      title: __bind(function() {
        return this.data_['t'];
      }, this)
    });
    google.maps.event.addDomListener(slide, 'click', __bind(function(ev) {
      return window.location = this.url;
    }, this));
    this.icon_ = icon;
    this.slide_ = slide;
    panes = this.getPanes();
    panes.overlayImage.appendChild(icon);
    return panes.overlayMouseTarget.appendChild(slide);
  };
  /*
  Vykresli grupu v mape, presne na zadanych souradnicich. Pokud je interni atribut
  @visible_ == false, grupa se nevykresli.
  */
  Group.prototype.draw = function() {
    var left, overlayProjection, pixel_pos, top;
    if (this.icon_ && this.visible_) {
      this.icon_.style.display = "block";
      this.slide_.style.display = "block";
      overlayProjection = this.getProjection();
      pixel_pos = overlayProjection.fromLatLngToDivPixel(this.pos_);
      left = pixel_pos.x - this.center_[0] + 'px';
      top = pixel_pos.y - this.center_[1] + 'px';
      this.icon_.style.left = left;
      this.icon_.style.top = top;
      this.slide_.style.left = left;
      this.slide_.style.top = top;
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
    if (this.icon_) {
      this.icon_.style.display = "none";
      this.slide_.style.display = "none";
      this.visible_ = false;
    }
  };
  /*
  Metoda volana po Group.set_map(null). Postara se o odstraneni HTML elementu z
  mapy a resetu vnitrnich hodnot.
  */
  Group.prototype.onRemove = function() {
    this.icon_.parentNode.removeChild(this.icon_);
    this.icon_ = null;
    this.slide_.parentNode.removeChild(this.slide_);
    this.slide_ = null;
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
    init_fancybox();
    hide_messages();
    return draw_entries();
  });
}).call(this);
