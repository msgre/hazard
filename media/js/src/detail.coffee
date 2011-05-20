###
TODO:
###

# konstanty
# z-index normalni a hover znacky
PIN_Z_INDEX = 10
HOVERED_PIN_Z_INDEX = 20
# z-index polygonu (budovy, zony okoli)
FILL_Z_INDEX = 14

# globalni promenne
FILL_OPTIONS = {}       # definice stylu pro polygony
ICONS = {}              # definice custom ikonek pouzitych v mape
MARKERS = {}            # hash mapa vsech znacek na mape (id: data)
BUILDINGS = []          # seznam vsech aktualne vykreslenych budov na mape
ZONES = []              # seznam vsech vykreslenych oblasti okolo budov na mape
BUBBLE_POLYGONS = []    # seznam polygonu budov a zon, ktere se vykreslily po hoveru nad verejnou budovou v bubline
OPENED = undefined      # rozkliknuta znacka
IW = undefined          # rozkliknuta bublina
MC_STYLE = {}           # styly pro marker clusterer


###
Nakonfigurovani stylu a ikon.
###

setup_detail = () ->
    # nastylovani polygonu
    FILL_OPTIONS['building'] =
        strokeWeight: 0
        strokeColor: '#000000'
        strokeOpacity: .01
        fillColor: '#ffffff'
        fillOpacity: 1
        zIndex: FILL_Z_INDEX
    FILL_OPTIONS['zone'] =
        strokeWeight: 0
        strokeColor: '#000000'
        strokeOpacity: .01
        fillColor: '#000000'
        fillOpacity: .7
        zIndex: FILL_Z_INDEX - 1
    FILL_OPTIONS['building_hovered'] =
        strokeWeight: 0
        strokeColor: '#000000'
        strokeOpacity: .01
        fillColor: '#000000'
        fillOpacity: .9
        zIndex: FILL_Z_INDEX + 2
    FILL_OPTIONS['zone_hovered'] =
        strokeWeight: 0
        strokeColor: '#e53404'
        strokeOpacity: .01
        fillColor: '#e53404'
        fillOpacity: .9
        zIndex: FILL_Z_INDEX + 1

    # definice custom spendlosu
    ICONS['allowed'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/yes.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['allowed_dimmed'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/yes_dimmed.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['allowed_hovered'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/yes_hovered.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['disallowed'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/no.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['disallowed_dimmed'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/no_dimmed.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['disallowed_hovered'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/no_hovered.png'
        new google.maps.Size(28, 28)
        new google.maps.Point(0,0)
        new google.maps.Point(14, 14)
    )
    ICONS['shadow'] = new google.maps.MarkerImage(
        'http://media.parkujujakcyp.cz/hazard/img/shadow.png'
        new google.maps.Size(27, 14)
        new google.maps.Point(0,0)
        new google.maps.Point(8, 0)
    )

    # nastylovani marker clusterer
    MC_STYLE =
        url: 'http://media.parkujujakcyp.cz/hazard/img/group.png'
        height: 40
        width: 40
        opt_anchor: [20, 20]
        opt_textColor: '#ffffff'
        opt_textSize: 11

    # Inicializace prvku na strance s detailem konkretni obce.
    $('#detailed_info, #join_us').hide()
    $('#detailed_info_anchor').click () ->
        $('#join_us').hide()
        $('#detailed_info').show()
        false
    $('#join_us_anchor').click () ->
        $('#join_us').show()
        $('#detailed_info').hide()
        false


###
Vykresleni budov, ktere sousedi s hernou (znackou) `that`.
###

draw_buildings = (that) ->
    for building in that._data.buildings
        path = (new google.maps.LatLng(i[1], i[0]) for i in window.buildings[building].polygon)
        poly = new google.maps.Polygon(FILL_OPTIONS['building'])
        poly.setPath(path)
        poly.setMap(window.map)
        BUILDINGS.push(poly)

###
Smazani budov, ktere sousedi s hernou (znackou) `that`.
###

clear_buildings = () ->
    for building in BUILDINGS
        building.setMap(null)

###
Vykresleni okoli budov (zon), ktere sousedi s hernou (znackou) `that`.
###

draw_zones = (that) ->
    if that._data.uzone.length
        path = (new google.maps.LatLng(i[1], i[0]) for i in that._data.uzone)
        poly = new google.maps.Polygon(FILL_OPTIONS['zone'])
        poly.setPath(path)
        poly.setMap(window.map)
        ZONES.push(poly)

###
Smazani okoli budov (zon), ktere sousedi s hernou (znackou) `that`.
###

clear_zones = () ->
    for zone in ZONES
        zone.setMap(null)

###
Ztlumeni vsech heren (znacek) na mape, s vyjimkou herny (znacky) `orig`.
###

dimm_hell = (orig) ->
    for id, marker of MARKERS
        continue if orig == marker
        marker.setIcon(ICONS[marker._data['dimm_image']])

###
Zruseni ztlumeni vsech heren (znacek) na mape, s vyjimkou herny (znacky) `orig`.
###

shine_hell = (orig) ->
    for id, marker of MARKERS
        continue if orig == marker
        marker.setIcon(ICONS[marker._data['image']])

###
Mys najela nad hernu -- zobrazime okolni budovy a zony v konfliktu a vsecky
ostatni herny pozhasiname.
###

mouseover_hell = () ->
    @.setIcon(ICONS[@._data['image'] + '_hovered'])
    @.setZIndex(HOVERED_PIN_Z_INDEX)
    if OPENED
        return
    if not @._data.conflict
        return
    draw_zones(@)
    draw_buildings(@)

###
Mys z herny odjela -- zrusime polygony zon/budov a zase rozneme ostatni herny.
###

mouseout_hell = () ->
    icon_name = @._data['image']
    @.setZIndex(PIN_Z_INDEX)
    if OPENED or not @._data.conflict
        if @ != OPENED
            if OPENED
                icon_name = @._data['dimm_image']
            @.setZIndex(PIN_Z_INDEX)
        else
            icon_name = @._data['image'] + '_hovered'
            @.setZIndex(HOVERED_PIN_Z_INDEX)
    @.setIcon(ICONS[icon_name])
    if OPENED
        return
    clear_buildings()
    clear_zones()

###
Mys nad titulkem verejne budovy v bubline -- zvyraznime danou budovu i jeji okoli.
###

window.mouseover_bubble_building = (el) ->
    building = $(el).attr('id').replace('b-', '')

    # zona kolem budovy
    path2 = (new google.maps.LatLng(i[1], i[0]) for i in window.zones[window.buildings[building].zone].polygon)
    poly2 = new google.maps.Polygon(FILL_OPTIONS['zone_hovered'])
    poly2.setPath(path2)
    poly2.setMap(window.map)
    BUBBLE_POLYGONS.push(poly2)

    # budova
    path1 = (new google.maps.LatLng(i[1], i[0]) for i in window.buildings[building].polygon)
    poly1 = new google.maps.Polygon(FILL_OPTIONS['building_hovered'])
    poly1.setPath(path1)
    poly1.setMap(window.map)
    BUBBLE_POLYGONS.push(poly1)

###
Mys odjela z titulku verejne budovy v bubline -- pryc se zvyraznujicima polygonama.
###

window.mouseout_bubble_building = (el) ->
    for bp in BUBBLE_POLYGONS
        bp.setMap(null)
    BUBBLE_POLYGONS = []


###
Kliknuti nad hernou -- zobrazime bublinu s popisem.
###

click_handler = (ev) ->
    # poroziname a pozhasiname co je treba
    if OPENED
        OPENED = null
        google.maps.event.trigger(@, 'mouseout', [ev, @])
        google.maps.event.trigger(@, 'mouseover', [ev, @])
    OPENED = @

    # stara bublina
    IW.close() if IW
    dimm_hell(@)

    # zobrazime bublinu
    content = '<h4>' + @._data.title + '</h4>'
    if @._data.description and not /^#style\d+$/.test(@._data.description)
        content += @._data.description
    if @_data.conflict
        content += '<p>Provoz herny <strong>je v rozporu se zákonem</strong>, protože v jejím okolí se nalézají tyto budovy:</p>'
        content += '<ul>'
        for building in @_data.buildings
            content += '<li><a id="b-' + building + '" onmouseover="javascript:window.mouseover_bubble_building(this)" onmouseout="javascript:window.mouseout_bubble_building(this)">' + window.buildings[building].title + '</a></li>'
        content += '</ul>'
        content += '<p><em>Tip: konkrétní veřejná budova se v mapě zvýrazní, pokud najedete myší nad její název uvedený v seznamu výše</em></p>'
    else
        content += '<p>V okolí herny se nenalézá žádná veřejná budova, její provoz není v rozporu se zákonem.</p>'
    IW = new google.maps.InfoWindow(
        content: content
        maxWidth: 300
    )
    IW.open(window.map, @)
    google.maps.event.addListener IW, 'closeclick', (ev2) =>
        OPENED = null
        google.maps.event.trigger(@, 'mouseout', [ev2, @])
        shine_hell(@)

###
Vykresleni vsech heren.
###

draw_hells = () ->
    sw = [1000, 1000]
    ne = [0, 0]

    for id, data of window.hells

        # custom ikonka
        if data.conflict
            data['image'] = 'disallowed'
        else
            data['image'] = 'allowed'

        # bounding box
        sw[0] = data.pos[1] if data.pos[1] < sw[0]
        ne[0] = data.pos[1] if data.pos[1] > ne[0]
        sw[1] = data.pos[0] if data.pos[0] < sw[1]
        ne[1] = data.pos[0] if data.pos[0] > ne[1]

        # vlozeni znacky do mapy
        MARKERS[id] = new google.maps.Marker({
            position: new google.maps.LatLng(data.pos[1], data.pos[0])
            #map: window.map
            title: data.title
            icon: ICONS[data['image']]
            shadow: ICONS['shadow']
            zIndex: PIN_Z_INDEX
        })
        data['dimm_image'] = data['image'] + '_dimmed'
        MARKERS[id]._data = data

        # hover nad znackou
        google.maps.event.addListener(MARKERS[id], 'mouseover', mouseover_hell)
        google.maps.event.addListener(MARKERS[id], 'mouseout', mouseout_hell)

        # click nad znackou
        google.maps.event.addListener(MARKERS[id], 'click', click_handler)

    # vlozime znacky do shlukovace
    marker_cluster = new MarkerClusterer(window.map, (MARKERS[i] for i of MARKERS), {
        maxZoom: 14
        gridSize: 50
        styles: [MC_STYLE, MC_STYLE, MC_STYLE]
    })

    # focus na spendlosy
    if window.hells
        bounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(sw[0], sw[1]),
            new google.maps.LatLng(ne[0], ne[1])
        )
        google.maps.event.addListenerOnce window.map, 'idle', () ->
            window.map.panBy(-160, 0)
        window.map.fitBounds(bounds)



# maso - maso - maso - maso - maso - maso - maso - maso - maso - maso - maso

$(document).ready () ->

    # inicializace
    setup()
    setup_detail()
    init_map()
    init_fancybox()

    draw_hells()
