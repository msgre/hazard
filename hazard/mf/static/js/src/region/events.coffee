###
Synchronizatko.
###

SEMAPHORE = {}

HazardEvents = {}
_.extend(HazardEvents, Backbone.Events)

HazardEvents.bind 'all', (name, arg) ->
    # uchovani informace o probehle udalosti
    parts = name.split(':')
    if parts[0] not of SEMAPHORE
        SEMAPHORE[parts[0]] = {}
    SEMAPHORE[parts[0]][parts[1]] = arg

    # nejdrive je treba natahnout do stranky Google API a JSON data ze serveru
    # teprem pak muzeme neco s mapama delat
    if 'map' of SEMAPHORE and 'extras_loaded' of SEMAPHORE.map and 'init' of SEMAPHORE.map
        SEMAPHORE['map']['initialized'] = true
        SEMAPHORE.map.extras_loaded.trigger('redraw:done')
        delete SEMAPHORE.map.init
        delete SEMAPHORE.map.extras_loaded
        $('h1').removeClass('loading')
