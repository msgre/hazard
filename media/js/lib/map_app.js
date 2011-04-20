(function() {
  window.map = void 0;
  $(document).ready(function() {
    var center, map_options;
    if (!(window.map != null)) {
      map_options = {
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        noClear: true
      };
      window.map = new google.maps.Map(document.getElementById("body"), map_options);
    }
    center = new google.maps.LatLng(49.38512, 17.41765);
    window.map.setCenter(center);
    return window.map.setZoom(11);
  });
  /*
  - pokud nadetekuje window.hells pak to znamena popis heren na mape
  - pokud nadetekuje window.buildings pak to znamena popis budov na mape
  - pokud nadetekuje window.zones pak to znamena popis okoli budov

  - kazdy podnik musi mit lat/lon, titulek, jestli je v konfliktu a id
  - kazda budova bude mit pole bodu pro polygon, id, titulek
  - kazda zona ma sve id a id budovy, ke ktere patri; a pak popis polygonu
  */
}).call(this);
