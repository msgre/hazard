###
Synchronizatko.

Co se v EVENTS_CACHE muze objevit:

* zaznamenani signalu Google:map_initialized a GeoObjectList:extras_loaded
* flag GObjectsDrawingAllowed, ktery rika, ze uz se muze kreslit do mapy
###

EVENTS_CACHE = {}

HazardEvents = {}
_.extend(HazardEvents, Backbone.Events)

HazardEvents.bind 'all', (name, arg=true) ->
    # nejdrive si uchovame informaci o probehle udalosti
    parts = name.split(':')
    if parts[0] not of EVENTS_CACHE
        EVENTS_CACHE[parts[0]] = {}
    EVENTS_CACHE[parts[0]][parts[1]] = arg

    # az se inicializuji mapy a natahnou extra JSON data, vykreslime GeoObjecty
    extras_loaded = 'GeoObjectList' of EVENTS_CACHE and 'extras_loaded' of EVENTS_CACHE.GeoObjectList
    map_init = 'Google' of EVENTS_CACHE and 'map_initialized' of EVENTS_CACHE.Google
    if map_init and extras_loaded
        log('HazardEvents:map initialized')
        EVENTS_CACHE['GObjectsDrawingAllowed'] = true
        EVENTS_CACHE.GeoObjectList.extras_loaded.trigger('GeoObjectList:redraw_done')
        delete EVENTS_CACHE.GeoObjectList.extras_loaded
        $('h1').removeClass('loading')

    # roznetka pro vykresleni obrysu regionu
    # (pouziva se v pohledech na okresy a obce)
    regions_prepared = 'RegionList' of EVENTS_CACHE and 'regions_loaded' of EVENTS_CACHE.RegionList
    if map_init and regions_prepared
        log('HazardEvents:regions_prepared')
        EVENTS_CACHE['RegionsDrawingAllowed'] = true
        EVENTS_CACHE.RegionList.regions_loaded.trigger('AppView:draw_regions')
        delete EVENTS_CACHE.RegionList.regions_loaded

    # roznetka pro vykresleni okresu
    # (pouziva se v pohledu na obce)
    regions_prepared = 'DistrictList' of EVENTS_CACHE and 'districts_loaded' of EVENTS_CACHE.DistrictList
    if map_init and regions_prepared
        log('HazardEvents:districts_prepared')
        EVENTS_CACHE['DistrictsDrawingAllowed'] = true
        EVENTS_CACHE.DistrictList.districts_loaded.trigger('AppView:draw_districts')
        delete EVENTS_CACHE.DistrictList.districts_loaded
