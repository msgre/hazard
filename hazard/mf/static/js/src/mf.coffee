"""
TODO:
"""

$(document).ready () ->
    handle_table()
    $('#sub-objects').schovavacz
        limit: 4
        epsilon: 1
        show_txt: ' <i>a další…</i>'
        hide_txt: ' <i>zkrátit seznam…</i>'
        items_selector: 'span'

    handle_switcher()

    init_map()
    #draw_hells()
    draw_shapes()

VIEW = 'hells'


# TODO:
perex_addon = () ->
    view = $('#table-switcher option:selected').attr('title')
    type = $('#type-switcher option:selected').attr('title')
    geo = $("#primer .#{ VIEW } span.title").text()

    values = $("table.statistics.#{ VIEW } td.#{ $('#table-switcher').val() }")
    values = _.sortBy(($.trim($(i).text()) for i in values), (num) -> if num then parseFloat(num.replace('%', '').replace(',', '.')) else 0)
    values.reverse()
    actual_value = $.trim($("table.statistics.#{ VIEW } tr.#{ window.actual } td.#{ $('#table-switcher').val() }").text())
    actual_value = actual_value
    order = _.indexOf(values, actual_value)

    if order == 0
        text = "Z pohledu <b>#{ view } #{ type}</b> je stav v #{ geo } <b>nejhorší</b> v republice."
    else
        text = "Z pohledu <b>#{ view } #{ type}</b> je stav v #{ geo } <b>#{ order + 1 }. nejhorší</b> v republice."

    $perex = $("#primer .#{ VIEW } h2")
    if $perex.next('h2').length
        $perex.next('h2').html(text)
    else
        $perex.after("<h2>#{ text }</h2>")




###
Obsluha preklikavani pohledu herny/automaty.
###
handle_switcher = () ->
    $primer = $('#primer')

    $primer.children('div').last().hide()
    $('table.machines').closest('div.outer-wrapper').hide()

    $('#type-switcher').change () ->
        VIEW = $(@).val()
        old_value = _.reject($(@).find('option'), (i) -> $(i).attr('value') == VIEW)
        old_class = $(old_value).attr('value')

        $("div.outer-wrapper.#{ VIEW }, #primer div.#{ VIEW }").show()
        $("div.outer-wrapper.#{ old_class}, #primer div.#{ old_class }").hide()

        $('#table-switcher').change()

    $('#type-switcher').change()


###
Zjednodusi tabulku na strance -- zobrazi vzdy jen jeden vybrany sloupec
a data v nem interpretuje jako barevny prouzek na pozadi radku.
###
handle_table = () ->
    # TODO: tady kravi ta bublina...
    $('table.statistics tr').hover () ->
        key = $.trim($(@).attr('class').replace('active', ''))
        google.maps.event.trigger(POLYS[key], 'mouseover')
        $(@).addClass('hover')
    , () ->
        $(@).removeClass('hover')
        key = $.trim($(@).attr('class').replace('active', ''))
        google.maps.event.trigger(POLYS[key], 'mouseout')

    # klikance fachaji nad kteroukoliv bunkou v tabulce
    $('table.statistics td').click () ->
        href = $(@).closest('tr').find('a').attr('href')
        window.location = href
        false

    # pryc s hlavickou tabulky
    $('table.statistics thead').remove()

    # obsluha selektitka
    $('#table-switcher').change () ->
        switcher_value = $(@).val()
        type_value = $('#type-switcher').val()

        $("table.statistics").each () ->
            values = []
            percents = false
            $table = $(@)
            $table.find('td').each () ->
                $td = $(@)
                if $td.attr('class') and not $td.hasClass(switcher_value)
                    $td.hide()
                else
                    if $td.attr('class')
                        value = $.trim($td.text())
                        percents = '%' in value
                        value = value.replace('%', '').replace(',', '.')
                        if value.length
                            values.push(parseFloat(value))
                        else
                            values.push(0)
                    $td.show()
            # uchovani min/max hodnoty ve sloupci
            if not $table.data(switcher_value)
                $table.data(switcher_value, {'min': _.min(values), 'max': if percents then 100.0 else _.max(values)})
            number_to_graph($table, values, percents, switcher_value)
        update_shapes()
        perex_addon()

    $('.table-switcher').change()


###
Interpretuje hodnotu jako barevny prouzek na pozadi radku tabulky.
###
number_to_graph = ($table, values, percents, cls) ->
    # maximum ve sloupecku s daty
    if percents
        max = 100.0
    else
        max = _.max(values) * 1.2

    # sirky bunek
    width = $table.width()
    td1_w = $table.find('td:first').width()
    td2_w = width - td1_w

    # kazdy radek tabulky podbarvime
    $table.find('tr').each (idx, el) ->
        $tr = $(@)
        $td1 = $tr.find('td:first')
        $td2 = $tr.find(".#{ cls }")
        w = Math.round(values[idx] / max * width)
        if w > td1_w
            x1 = 1000
            x2 = w - td1_w
        else
            x1 = w
            x2 = 0

        $td1.css('background-position', "#{ x1 }px 0")
        $td2.css('background-position', "#{ x2 }px 0")


POLYS = {}
POLYS_COLORS = {}

###
TODO:
###
draw_shapes = () ->

    $table = $("table.statistics.#{ VIEW }")
    $select = $('#table-switcher')
    col = $select.val()
    extrems = $table.data(col)
    delta = extrems.max - extrems.min

    [min_lats, max_lats, min_lons, max_lons] = [[], [], [], []]
    [actual_min_lat, actual_max_lat, actual_min_lon, actual_max_lon] = [null, null, null, null]

    _.each window.shapes, (shape, key) ->
        if not shape
            return true

        polys = []
        [min_lat, max_lat, min_lon, max_lon] = [100000000, 0, 100000000, 0]
        for item in shape
            _polys = []
            for i in item
                min_lat = if i[0] < min_lat then i[0] else min_lat
                max_lat = if i[0] > max_lat then i[0] else max_lat
                min_lon = if i[1] < min_lon then i[1] else min_lon
                max_lon = if i[1] > max_lon then i[1] else max_lon
                _polys.push(new google.maps.LatLng(i[0], i[1]))
            polys.push(_polys)
        min_lats.push(min_lat)
        max_lats.push(max_lat)
        min_lons.push(min_lon)
        max_lons.push(max_lon)
        if key == window.actual
            actual_min_lat = min_lat
            actual_max_lat = max_lat
            actual_min_lon = min_lon
            actual_max_lon = max_lon

        value = $.trim($table.find("tr.#{ key } td.#{ col }").text())
        value = value.replace('%', '').replace(',', '.')
        value = (value - extrems.min) / delta
        color = interpolate_color('#FFD700', '#EE0000', value)
        #color = interpolate_color('#E5ECF9', '#0066CC', value)
        #color = interpolate_color('#CCCCCC', '#555555', value)
        POLYS[key] = new google.maps.Polygon
            paths: polys
            strokeColor: color
            strokeOpacity: 1
            strokeWeight: 1
            fillColor: color
            fillOpacity: 1
            zIndex: 10

        POLYS_COLORS[key] = color

        if key == window.actual
            POLYS[key].setOptions
                zIndex: 20
                strokeColor: "#333333"
                strokeWeight: 3

        google.maps.event.addListener POLYS[key], 'mouseover', () ->
            POLYS[key].setOptions
                fillColor: '#333333'
                strokeColor: '#333333'
                zIndex: 15
            $tr = $table.find("tr.#{ key }")
            $tr.addClass('hover')

            titles = ($(i).text() for i in $select.find('option'))
            texts = ($.trim($(i).text()) for i in $tr.find('td'))
            hovno = _.zip(titles, _.last(texts, 3))
            hovno = ("#{ i[0] }: #{ i[1] }" for i in hovno)

            #tooltip.show("<strong>#{ _.first(texts) }</strong><br /><br /><p>#{ hovno.join('<br>') }</p>")

        google.maps.event.addListener POLYS[key], 'mouseout', () ->
            POLYS[key].setOptions
                fillColor: POLYS_COLORS[key]
                strokeColor: if key == window.actual then '#333333' else POLYS_COLORS[key]
                zIndex: if key == window.actual then 20 else 10
            $table.find("tr.#{ key }").removeClass('hover')
            #tooltip.hide()

        google.maps.event.addListener POLYS[key], 'click', () ->
            $table.find("tr.#{ key } a").click()

        POLYS[key].setMap(MAP)


    min_lat = _.min(min_lats)
    max_lat = _.max(max_lats)
    min_lon = _.min(min_lons)
    max_lon = _.max(max_lons)

    min_lat = actual_min_lat
    max_lat = actual_max_lat
    min_lon = actual_min_lon
    max_lon = actual_max_lon

    google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
        MAP.setZoom(MAP.getZoom() - 1)
    MAP.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(min_lat, min_lon), new google.maps.LatLng(max_lat, max_lon)))


###
TODO:
###
update_shapes = () ->

    $table = $("table.statistics.#{ VIEW }")
    $select = $('#table-switcher')
    col = $select.val()
    extrems = $table.data(col)
    delta = extrems.max - extrems.min

    _.each window.shapes, (shape, key) ->
        if not POLYS[key]
            return true

        value = $.trim($table.find("tr.#{ key } td.#{ col }").text())
        value = value.replace('%', '').replace(',', '.')
        value = (value - extrems.min) / delta
        color = interpolate_color('#FFD700', '#EE0000', value)

        POLYS_COLORS[key] = color

        POLYS[key].setOptions
            fillColor: color
            strokeColor: color

        if key == window.actual
            POLYS[key].setOptions
                zIndex: 20
                strokeColor: "#333333"
                strokeWeight: 3














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
  #   featureType: "landscape",
  #   stylers: [
  #     { lightness: -80 },
  #   ]
  # },{
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
  },{
    featureType: "administrative.country",
    elementType: "geometry",
    stylers: [
      { visibility: "on" },
      { lightness: 58 }
    ]
  }
]

# MAP_STYLE = [
#   {
#     featureType: "landscape",
#     stylers: [
#       { visibility: "off" }
#     ]
#   },{
#     featureType: "administrative.province",
#     stylers: [
#       { visibility: "off" }
#     ]
#   },{
#     featureType: "poi",
#     stylers: [
#       { visibility: "off" }
#     ]
#   },{
#     featureType: "administrative",
#     stylers: [
#       { lightness: 30 },
#       { saturation: -100 }
#     ]
#   },{
#     featureType: "road",
#     stylers: [
#       { saturation: -100 },
#       { lightness: 30 }
#     ]
#   },{
#     featureType: "transit",
#     stylers: [
#       { visibility: "off" }
#     ]
#   },{
#     featureType: "water",
#     stylers: [
#       { saturation: -100 },
#       { lightness: 30 }
#     ]
#   }
# ]




show_surround = (hell) ->
    conflict = window.conflicts["#{ hell.id }"]
    coords = [new google.maps.LatLng(i[1], i[0]) for i in conflict.shape[0]]
    poly = new google.maps.Polygon
        paths: coords
        strokeColor: "#EE0000"
        strokeOpacity: 0
        strokeWeight: 0
        fillColor: "#EE0000"
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
            center: new google.maps.LatLng(49.38512, 14.61765) # defaultne zamerime na CR
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



hex = (v) ->
    out = v.toString(16)
    if out.length == 1
        out = '0' + out
    out

convert_to_hex = (rgb) ->
    '#' + hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2])

trim = (s) ->
    return if s.charAt(0) == '#' then s.substring(1, 7) else s

convert_to_rgb = (hex) ->
    color = [
        parseInt(trim(hex).substring(0, 2), 16)
        parseInt(trim(hex).substring(2, 4), 16)
        parseInt(trim(hex).substring(4, 6), 16)
    ]

interpolate_color = (start_color, end_color, value) ->
    start = convert_to_rgb(start_color)
    end = convert_to_rgb(end_color)
    c = [
        Math.round((end[0] - start[0]) * value + start[0])
        Math.round((end[1] - start[1]) * value + start[1])
        Math.round((end[2] - start[2]) * value + start[2])
    ]
    convert_to_hex(c)
