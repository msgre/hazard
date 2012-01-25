"""
Detailni mapa s konflikty pro konkretni obec.

NOTE: pro velka mesta by se sikl MarkerClusterer, ale prdim ted na to. Jako
nepouzit ho ma i sve vyhody, aby jste vedeli.
"""

# hlavni seznamy
HELLS = {} # slovnik se vsemi hernami
ZONES = {} # slovnik s okolim budov
PLACES = {} # slovnik s budovami

# stavove promenne
INFO_WINDOW = null # otevrene InfoWindow; InfoWindow
INFO_WINDOW_MARKER = null # znacka, nad kterou se otevrelo InfoWindow; Marker
SINGLE_ZONE = null # okoli konkretni budovy (hover nad mistem v otevrenem InfoWindow); Polygon

# ostatni numericke konstanty
PIN_Z_INDEX = 10 # z-index ikony s hernou
HOVERED_PIN_Z_INDEX = PIN_Z_INDEX + 10 # z-index hover ikony
FILL_Z_INDEX = 14 # zakladni z-index polygonu (a ostatnich objektu) kreslenych do mapy
MAX_ZOOM_LEVEL = 17 # pokud se provede fokus na mapu po vlozeni vsech znacek do ni, nepriblizuj se vic nez na tuto hodnotu
POINT_AS_CIRCLE_RADIUS = 8 # pokud je misto reprezentovano bodem, vykreslime jej jako kruh o tomto polomeru (v metrech)

# nastaveni
FILL_OPTIONS = {} # definice stylu pro objekty kreslene do mapy
ICONS = {} # definice ikon pouzitych v mape
ICONS_URL = 'http://media.mapyhazardu.cz/img/' # bazove URL, kde se nachazi sprity s ikonama


###
Obsluha situace, kdy je kurzor mysi nad hernou.
###
mouse_on_hell = (key, icon_type, force=false) ->

    # kdyz je otevrene info okno, na hover si nehrajem
    if INFO_WINDOW and not force
        return

    # dynamicka zmena ikony herny
    HELLS[key].setIcon(ICONS["#{ icon_type }_hovered"])
    HELLS[key].setZIndex(HOVERED_PIN_Z_INDEX)

    # pokud je herna v konfliktu s nejakymi misty, vykreslime je
    if key of window.hazardata.conflicts
        # vykresleni okoli
        shapes = []
        if key of window.hazardata.hell_surrounds
            # mame pro adresu herny nejake vetsi, mergenute okoli?
            shapes.push(window.hazardata.hell_surrounds[key])
        else
            shapes = (window.hazardata.place_surrounds[k] for k in window.hazardata.conflicts[key])

        if shapes.length
            ZONES[key] = []
            for shape in shapes
                poly = new google.maps.Polygon(FILL_OPTIONS['zone'])
                poly.setPath(((new google.maps.LatLng(i[1], i[0]) for i in item) for item in shape))
                poly.setMap(MAP)
                ZONES[key].push(poly)

        # vykresleni mist
        PLACES[key] = {}
        for place_address_id in window.hazardata.conflicts[key]
            addr = window.hazardata.addresses[place_address_id]

            if addr.geo_type == 'point'
                circle = new google.maps.Circle(FILL_OPTIONS['building'])
                circle.setCenter(new google.maps.LatLng(addr.geo[1], addr.geo[0]))
                circle.setRadius(POINT_AS_CIRCLE_RADIUS)
                circle.setMap(MAP)
                PLACES[key][place_address_id] = circle

            else if addr.geo_type == 'poly'
                # TODO: odzkouset
                poly = new google.maps.Polygon(FILL_OPTIONS['zone'])
                poly.setPath(((new google.maps.LatLng(i[1], i[0]) for i in item) for item in addr.geo))
                poly.setMap(MAP)
                PLACES[key][place_address_id] = poly

            else
                # TODO: v budoucnu se asi jeste objevi cara?
                continue


###
Kurzor mysi odjel z ikony herny pryc. Je treba po nem uklidit.
###
mouse_out_of_hell = (key, icon_type, force=false) ->
    if INFO_WINDOW and not force
        return

    # dynamicka zmena ikony herny
    HELLS[key].setIcon(ICONS["#{ icon_type }"])
    HELLS[key].setZIndex(PIN_Z_INDEX)

    # smazani okoli
    if key of ZONES
        for zone in ZONES[key]
            zone.setMap(null)
        delete ZONES[key]

    # smazani mist
    if key of PLACES
        for place_id of PLACES[key]
            PLACES[key][place_id].setMap(null)
            delete PLACES[key][place_id]
        delete PLACES[key]


###
Kliknuti nad ikonou herny.
###
click_on_hell = (key, icon_type) ->
    # je prave ted otevrene nejake jine infowindow?
    if INFO_WINDOW_MARKER
        # yes! musime:
        # - odhoverovat starou hernu
        # - nahoverovat novou
        _type = if INFO_WINDOW_MARKER of window.hazardata.conflicts then 'disallowed' else 'allowed'
        mouse_out_of_hell(INFO_WINDOW_MARKER, _type, true)
        mouse_on_hell(key, icon_type, true)

    # je prave ted otevrene nejake jine infowindow?
    if INFO_WINDOW
        # yes! tak ho zavrem
        INFO_WINDOW.close()

    # konstrukce obsahu okynka
    title = window.hazardata.hells[key].join('<br>')
    if key of window.hazardata.conflicts
        # konflikt
        content = '<p>V okolí tohoto místa se naléza '
        content = "#{ content }#{ if window.hazardata.conflicts[key].length > 1 then 'několik budov, se kterými' else 'budova, se kterou' }"
        content = "#{ content } je herna v konfliktu:</p><ul id=\"infowindow-list\">"
        places = []
        for place_id in window.hazardata.conflicts[key]
            place = _.map window.hazardata.places[place_id], (item) ->
                "<li><abbr class=\"\#b-#{ place_id }\">#{ item }</abbr></li>"
            places.push(place.join(''))
        content = "#{ content }#{ places.join('') }</ul>"
    else
        # nema problema
        content = '<p>V okolí tohoto místa není žádná budova, se kterou by byla herna v konfliktu.</p>'

    # konstrukce samotneho okynka
    INFO_WINDOW = new google.maps.InfoWindow(
        content: "<h4>#{ title }</h4>#{ content }"
        maxWidth: 300
    )

    # uklid po zavreni infowindow
    google.maps.event.addListener INFO_WINDOW, 'closeclick', () ->
        mouse_out_of_hell(key, icon_type, true)
        INFO_WINDOW = null
        INFO_WINDOW_MARKER = null

    # zaveseni obsluhy na odkazy uvnitr infowindow
    # viz: http://stackoverflow.com/questions/6378007/adding-event-to-element-inside-google-maps-api-infowindow
    google.maps.event.addListener INFO_WINDOW, 'domready', () ->
        $('#infowindow-list abbr[class^="#b-"]').hover(() ->
            id = $(@).attr('class').split('-')[1]

            # zvyrazneni budovy
            PLACES[key][id].setOptions(FILL_OPTIONS['building_hovered'])

            # vykresleni okoli budovy
            shape = window.hazardata.place_surrounds[id]
            SINGLE_ZONE = new google.maps.Polygon(FILL_OPTIONS['zone_hovered'])
            SINGLE_ZONE.setPath(((new google.maps.LatLng(i[1], i[0]) for i in item) for item in shape))
            SINGLE_ZONE.setMap(MAP)
        , () ->
            id = $(@).attr('class').split('-')[1]

            # pryc se zvyraznenim budovy
            PLACES[key][id].setOptions(FILL_OPTIONS['building'])

            # pryc se zvyraznenym okolim
            SINGLE_ZONE.setMap(null)
            SINGLE_ZONE = null
        ).click () ->
            # kliknuti nad polozkou v infowindow nic nezrobi
            false

    INFO_WINDOW_MARKER = key
    INFO_WINDOW.open(MAP, HELLS[key])


###
Vykresleni heren.
###
draw_hells = () ->

    lats = []
    lons = []

    # vykreslime okresy
    _.each window.hazardata.hell_addresses, (hell_address_id) ->

        key = hell_address_id.toString()
        icon_type = if key of window.hazardata.conflicts then 'disallowed' else 'allowed'
        geo = window.hazardata.addresses[key].geo
        lats.push(geo[1])
        lons.push(geo[0])

        # ikona s hernou
        HELLS[key] = new google.maps.Marker
            map: MAP
            position: new google.maps.LatLng(geo[1], geo[0])
            title: 'herna' # TODO: window.hells[key], je to ale pole!
            shadow: ICONS['shadow']
            zIndex: PIN_Z_INDEX
            icon: ICONS[icon_type]

        # udalosti nad ikonou
        google.maps.event.addListener HELLS[key], 'mouseover', () ->
            mouse_on_hell(key, icon_type)

        google.maps.event.addListener HELLS[key], 'mouseout', () ->
            mouse_out_of_hell(key, icon_type)

        google.maps.event.addListener HELLS[key], 'click', (ev) ->
            click_on_hell(key, icon_type)

    # fokus na mapu s obci
    bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(_.min(lats), _.min(lons))
        new google.maps.LatLng(_.max(lats), _.max(lons))
    )
    google.maps.event.addListenerOnce MAP, 'idle', () ->
        zoom = MAP.getZoom()
        if zoom > MAX_ZOOM_LEVEL
            MAP.setZoom(MAX_ZOOM_LEVEL)
    MAP.fitBounds(bounds)


###
Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
###
load_maps_api = () ->
    $('h1').addClass('loading')
    $.getJSON window.location.pathname, (data) ->
        window.hazardata = data
        script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map'
        document.body.appendChild(script)


###
Inicializace map, volana jako callback po asynchronnim nacteni Google Maps API.
###
window.late_map = () ->

    # nastylovani polygonu
    FILL_OPTIONS['building'] =
        strokeOpacity: 0
        fillColor: '#ffffff'
        fillOpacity: 1
        zIndex: FILL_Z_INDEX + 1
    FILL_OPTIONS['building_hovered'] =
        strokeOpacity: 0
        fillColor: '#ffffff'
        fillOpacity: 1
        zIndex: FILL_Z_INDEX + 3
    FILL_OPTIONS['zone'] =
        strokeWeight: 0
        strokeOpacity: 0
        fillColor: '#000000'
        fillOpacity: .7
        zIndex: FILL_Z_INDEX
    FILL_OPTIONS['zone_hovered'] =
        strokeOpacity: 0
        fillColor: '#000000'
        fillOpacity: 1
        zIndex: FILL_Z_INDEX + 2

    # definice custom spendlosu
    size = new google.maps.Size(28, 28)
    point0 = new google.maps.Point(0, 0)
    point14 = new google.maps.Point(14, 14)
    ICONS['allowed'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }yes.png", size, point0, point14
    )
    ICONS['allowed_dimmed'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }yes_dimmed.png", size, point0, point14
    )
    ICONS['allowed_hovered'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }yes_hovered.png", size, point0, point14
    )
    ICONS['disallowed'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }no.png", size, point0, point14
    )
    ICONS['disallowed_dimmed'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }no_dimmed.png", size, point0, point14
    )
    ICONS['disallowed_hovered'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }no_hovered.png", size, point0, point14
    )
    ICONS['shadow'] = new google.maps.MarkerImage(
        "#{ ICONS_URL }shadow.png"
        new google.maps.Size(27, 14)
        new google.maps.Point(0,0)
        new google.maps.Point(8, 0)
    )

    # inicializace mapy
    map_options =
        zoom: 6
        center: new google.maps.LatLng(49.38512, 14.61765) # stred CR
        mapTypeId: google.maps.MapTypeId.ROADMAP

    MAP = new google.maps.Map(document.getElementById("map"), map_options)

    # vykresleni heren
    draw_hells()
    $('h1').removeClass('loading')


# -----------------------------------------------------------------------------

$(document).ready () ->
    load_maps_api()
