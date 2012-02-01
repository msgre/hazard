###
Synchronizatko.

Co se v EVENTS_CACHE muze objevit:

* zaznamenani signalu Google:map_initialized a GeoObjectList:extras_loaded
* flag MapDrawingAllowed, ktery rika, ze uz se muze kreslit do mapy
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
        EVENTS_CACHE['MapDrawingAllowed'] = true
        EVENTS_CACHE.GeoObjectList.extras_loaded.trigger('GeoObjectList:redraw_done')
        delete EVENTS_CACHE.Google.map_initialized
        delete EVENTS_CACHE.GeoObjectList.extras_loaded
        $('h1').removeClass('loading')
