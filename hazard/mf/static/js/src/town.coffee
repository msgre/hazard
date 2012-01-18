"""
TODO:
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
        console.log 'stary znamy'
        update_shapes()

    $('.table-switcher').change()


###
Konstrukce klice do AJAX dat podle hodnot ze selektitek.
###
ajax_key = () ->
    type = $('#type-switcher').val()
    type = type.substr(0, type.length - 1)
    kind = $('#table-switcher').val()
    if kind == 'counts'
        # klice: hell_counts/machine_counts
        key = "#{ type }_#{ kind }"
    else
        # klice: conflict_hell_counts/conflict_machine_counts
        #        conflict_hell_perc/conflict_machine_perc
        kind = kind.split('_')
        key = "#{ kind[0] }_#{ type }_#{ kind[1] }"
    key


###
Prvotni vykresleni barevnych polygonu do mapy (dle aktualne zvolenych voleb
v selektitkach a datech v tabulce).
###
draw_shapes = () ->

    # rozsah zobrazovanych hodnot
    statistics_key = ajax_key()
    delta = window.extrems[statistics_key].max - window.extrems[statistics_key].min

    # vykreslime okresy
    _.each window.shapes, (shape, key) ->
        if not shape
            return true

        # vypocet barvy
        value = window.districts[key]['statistics'][statistics_key]
        value = (value - window.extrems[statistics_key].min) / delta
        color = interpolate_color('#FFD700', '#EE0000', value)

        # vykresleni polygonu do mapy
        POLYS[key] = new google.maps.Polygon
            paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
            strokeColor: color
            strokeOpacity: 1
            strokeWeight: 1
            fillColor: color
            fillOpacity: 1
            zIndex: 10
        POLYS_COLORS[key] = color
        POLYS[key].setMap(MAP)

    google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
        MAP.setZoom(MAP.getZoom() - 1)
    MAP.fitBounds(POLYS[window.actual_disctrict].getBounds())


###
Aktualizace barev vykreslenych polygonu na mape (dle aktualne zvolenych voleb
v selektitkach a datech v tabulce).
###
update_shapes = () ->

    # rozsah zobrazovanych hodnot
    statistics_key = ajax_key()
    delta = window.extrems[statistics_key].max - window.extrems[statistics_key].min

    # aktualizujeme obrysy
    _.each window.shapes, (shape, key) ->
        if not POLYS[key]
            return true

        # vypocet barvy
        value = window.districts[key]['statistics'][statistics_key]
        value = (value - window.extrems[statistics_key].min) / delta
        color = interpolate_color('#FFD700', '#EE0000', value)

        # aktualizace
        POLYS_COLORS[key] = color
        POLYS[key].setOptions
            fillColor: color
            strokeColor: color


###
Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
###
load_maps_api = () ->
    $('h1').addClass('loading')
    $.getJSON window.url, (data) ->
        window.shapes = {}
        for id in _.keys(data['districts'])
            window.shapes[id] = data['districts'][id]['shape']
        window.extrems = data['extrems']
        window.districts = data['districts']

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
    load_maps_api()
    $('.sub-objects').schovavacz(SCHOVAVACZ_OPTS)
    handle_table()
    handle_switcher()
