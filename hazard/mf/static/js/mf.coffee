"""
TODO:
"""

$(document).ready () ->
    init_map()
    #draw_hells()
    draw_shapes()
    handle_perex()

draw_shapes = () ->
    _.each window.shapes, (shape, key) ->
        if not shape
            return true
        polys = (new google.maps.LatLng(i[0], i[1]) for i in shape)
        if key == window.region
            sh = new google.maps.Polygon
                paths: polys
                strokeColor: "#FFFF00"
                strokeOpacity: 1
                strokeWeight: 3
                fillColor: "#000000"
                fillOpacity: 1
        else
            sh = new google.maps.Polygon
                paths: polys
                strokeColor: "#dddddd"
                strokeOpacity: 1
                strokeWeight: 0
                fillColor: "#666666"
                fillOpacity: 1

        sh.setMap(MAP)


MAP = undefined
ICONS =
    'allowed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'allowed_dimmed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'allowed_hovered': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/yes_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'disallowed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'disallowed_dimmed': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no_dimmed.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'disallowed_hovered': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/no_hovered.png', new google.maps.Size(28, 28), new google.maps.Point(0, 0), new google.maps.Point(14, 14))
    'shadow': new google.maps.MarkerImage('http://media.mapyhazardu.cz/img/shadow.png', new google.maps.Size(27, 14), new google.maps.Point(0, 0), new google.maps.Point(8, 0))

MARKER_LUT = {} # kes spendliku na mape
HELL_MARKERS = {}
HOVERED_HELL = null
OPENED_INFOWINDOW = false


MAP_STYLE = [
  {
    featureType: "water",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "transit",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "landscape.natural",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "road",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "landscape.man_made",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "poi",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "administrative.province",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "administrative.locality",
    stylers: [
      { visibility: "off" }
    ]
  },{
    featureType: "administrative",
    elementType: "labels",
    stylers: [
      { visibility: "off" }
    ]
  }
]



show_surround = (hell) ->
    conflict = window.conflicts["#{ hell.id }"]
    coords = [new google.maps.LatLng(i[1], i[0]) for i in conflict.shape[0]]
    poly = new google.maps.Polygon
        paths: coords
        strokeColor: "#FF0000"
        strokeOpacity: 0
        strokeWeight: 0
        fillColor: "#FF0000"
        fillOpacity: 0.35
    poly.setMap(MAP)
    HOVERED_HELL = {'hell': hell, 'poly': poly}


clear_surround = () ->
    if HOVERED_HELL
        HOVERED_HELL['poly'].setMap(null)
        HOVERED_HELL = null


# TODO:
draw_hells = () ->
    sw = [1000, 1000]
    ne = [0, 0]

    _.each window.hells, (hell) ->
        address = window.addresses["#{ hell.address }"] # adresa herny
        pos_key = "#{ address.point[1] }-#{ address.point[0] }" # pozice herny v mape

        # tak co, uz jsme na pozici address.point neco zapichli?
        if pos_key of MARKER_LUT
            # yes! tak si jen poznamename co tam jeste patri a novy spendlik nekreslime
            MARKER_LUT[pos_key]['hells'].push(hell.id)
            HELL_MARKERS[hell.id] = pos_key
            return true
        else
            MARKER_LUT[pos_key] = {'hells': [], 'gobjects': [], 'marker': undefined}

        # zapamatujeme si co kde lezi
        MARKER_LUT[pos_key]['hells'].push(hell.id)
        HELL_MARKERS[hell.id] = pos_key

        # zapichneme spendlik
        marker_pos = new google.maps.LatLng(address.point[1], address.point[0])
        MARKER_LUT[pos_key]['marker'] = new google.maps.Marker
            position: marker_pos
            map: MAP
            icon: if "#{ hell.id }" of window.conflicts then ICONS.disallowed else ICONS.allowed
            shadow: ICONS.shadow

        # bounding box
        sw[0] = address.point[1] if address.point[1] < sw[0]
        ne[0] = address.point[1] if address.point[1] > ne[0]
        sw[1] = address.point[0] if address.point[0] < sw[1]
        ne[1] = address.point[0] if address.point[0] > ne[1]

        # bublina s podrobnymi informacemi
        infowindow = new google.maps.InfoWindow()
        google.maps.event.addListener MARKER_LUT[pos_key]['marker'], 'click', () ->

            if OPENED_INFOWINDOW
                clear_surround()
                OPENED_INFOWINDOW.close()
            OPENED_INFOWINDOW = infowindow

            # odkryti okoli
            show_surround(hell)

            # nadpis s nazvem heren
            if MARKER_LUT[pos_key]['hells'].length
                hell_titles = ("<a href=\"herny/#{ i }/\">#{ window.hells[i].title }</a>" for i in MARKER_LUT[pos_key]['hells']).join('<br/>')
            else
                hell_titles = null

            # uvodni text bubliny
            text = "<h4>#{ hell_titles }</h4>"
            if "#{ hell.id }" of window.conflicts
                text = "#{ text }<p>Provoz herny(-en) je na tomto místě v <b>rozporu se zákonem o loteriích</b>.</p>"
            else
                text = "#{ text }<p>Provoz herny(-en) na tomto místě není v rozporu se zákonem o loteriích.</p>"

            # seznam konfliktnich oblasti
            if "#{ hell.id }" of window.conflicts
                text = "#{ text }<p>Konfliktní budovy/oblasti:</p>"
                building_names = (window.gobjects["#{ i }"].title for i in window.conflicts["#{ hell.id }"]['buildings']).join('</li><li>')
                text = "#{ text }<ul><li>#{ building_names }</li></ul>"

            # otevreni bubliny
            infowindow.setContent(text)
            infowindow.open(MAP, MARKER_LUT[pos_key]['marker'])

        google.maps.event.addListener infowindow, 'closeclick', () ->
            OPENED_INFOWINDOW = false
            clear_surround()

        # mouseover/out nad ikonou konfliktni herny
        if "#{ hell.id }" of window.conflicts

            # mouseover
            google.maps.event.addListener MARKER_LUT[pos_key]['marker'], 'mouseover', () ->
                if not OPENED_INFOWINDOW
                    show_surround(hell)

            # mouseout
            google.maps.event.addListener MARKER_LUT[pos_key]['marker'], 'mouseout', () ->
                if not OPENED_INFOWINDOW
                    clear_surround()

    # focus na spendlosy
    if window.hells
        bounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(sw[0], sw[1]),
            new google.maps.LatLng(ne[0], ne[1])
        )
        MAP.fitBounds(bounds)



# TODO:
init_map = () ->
    if $('#map').hasClass('detail-map')
        map_options =
            zoom: 14
            center: new google.maps.LatLng(49.340, 17.993) # defaultne zamerime na CR
            mapTypeControl: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP
            streetViewControl: false
        MAP = new google.maps.Map(document.getElementById("map"), map_options)
    else
        map_options =
            zoom: 6
            center: new google.maps.LatLng(49.38512, 14.61765) # defaultne zamerime na CR
            mapTypeControl: false,
            mapTypeId: 'CB'
            streetViewControl: false
        MAP = new google.maps.Map(document.getElementById("map"), map_options)
        styledMapType = new google.maps.StyledMapType(MAP_STYLE, {name:'Černobílá'})
        MAP.mapTypes.set('CB', styledMapType)


handle_perex = () ->
    $('#percentual-perex').hide()

    $('#perex a').click () ->
        parent = $(@).closest('div.block')
        console.log parent
        parent.hide()
        parent.siblings().show()
        false

    $table = $('#table-data')
    $table.hide()
    $table.before('<p><a href="#">Tabulková data</a></p>')
    $table.prev('p').find('a').click () ->
        $table.toggle()
        false
