"""
Kod pro stranky s krajem a okresy.

Z tabulky vlozene do stranky dokaze vyzobnout potrebne informace (napr.
absolutni pocet heren v kraji), spoji se serverem a vytahne z nej polygony
geokrafickych objektu (obrysy kraju/okresu), zavesi na elementy ve strance
obsluzne funkce a upravi vzhled stranky.

TODO: predelat draw_shapes aby vyuzival getBounds
"""

###
Obsluha preklikavani pohledu herny/automaty.
###
handle_switcher = (set=true) ->
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
a data v nem interpretuje jako barevny prouzek na pozadi radku. Povesi na
tabulku hover obsluhu (zvyrazeneni radku i polygonu v mape).
###
handle_table = () ->
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
        $tr = $(@).closest('tr')
        href = $tr.find('a').attr('href')
        $('h1').addClass('loading')

        $.ajax
            url: href
            cache: true
            dataType: 'json'
            success: (data) ->
                $('h1').replaceWith(data.main_header)
                $('#primer').replaceWith(data.primer_content)
                $('.sub-objects').schovavacz(SCHOVAVACZ_OPTS)
                handle_switcher(false)
                $('table.statistics tr.active').removeClass('active')
                POLYS[window.actual].setOptions
                    zIndex: 10
                    strokeWeight: 0
                window.actual = $.trim($tr.attr('class').replace('hover', ''))
                POLYS[window.actual].setOptions
                    zIndex: 20
                    strokeWeight: 3
                    strokeColor: "#333333"
                $tr.addClass('active')
                google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
                    MAP.setZoom(MAP.getZoom() - 1)
                MAP.fitBounds(POLYS[window.actual].getBounds())
                $('h1').removeClass('loading')
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

    $('.table-switcher').change()


###
Prvotni vykresleni barevnych polygonu do mapy (dle aktualne zvolenych voleb
v selektitkach a datech v tabulce).
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

        google.maps.event.addListener POLYS[key], 'mouseout', () ->
            POLYS[key].setOptions
                fillColor: POLYS_COLORS[key]
                strokeColor: if key == window.actual then '#333333' else POLYS_COLORS[key]
                zIndex: if key == window.actual then 20 else 10
            $table.find("tr.#{ key }").removeClass('hover')

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
Aktualizace barev vykreslenych polygonu na mape (dle aktualne zvolenych voleb
v selektitkach a datech v tabulce).
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


###
Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
###
load_maps_api = () ->
    $('h1').addClass('loading')
    $.getJSON window.url, (data) ->
        window.shapes = {}
        for key in _.keys(data['details'])
            window.shapes[key] = data['details'][key]['shape']

        script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map'
        document.body.appendChild(script)


###
Inicializace map, volana jako callback po asynchronnim nacteni Google Maps API.
###
window.late_map = () ->

    # vypocet bounding boxy polygonu (Google to neumi), viz
    # http://code.google.com/p/google-maps-extensions/source/browse/google.maps.Polygon.getBounds.js
    if not google.maps.Polygon.prototype.getBounds
        google.maps.Polygon.prototype.getBounds = (latLng) ->

            bounds = new google.maps.LatLngBounds()
            paths = this.getPaths()
            for path in paths.getArray()
                for item in path.getArray()
                    bounds.extend(item)
            bounds

    # inicializace mapy
    map_options =
        zoom: 6
        center: new google.maps.LatLng(49.38512, 14.61765) # stred CR
        mapTypeControl: false,
        mapTypeId: 'CB'
        streetViewControl: false
    MAP = new google.maps.Map(document.getElementById("map"), map_options)
    styledMapType = new google.maps.StyledMapType(MAP_STYLE, {name:'Černobílá'})
    MAP.mapTypes.set('CB', styledMapType)

    # vykresleni polygonu (kraje/okresy)
    draw_shapes()
    $('h1').removeClass('loading')


# -----------------------------------------------------------------------------

$(document).ready () ->
    handle_table()
    load_maps_api()
    $('.sub-objects').schovavacz(SCHOVAVACZ_OPTS)
    handle_switcher()
