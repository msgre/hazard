"""
TODO:
- zvyraznovat aktualni kraj/okres?
    - nebo se na to vykaslat?
- kua nemam orafnout aspon ten okres?
    - o tom data mam ne?
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
        key = $.trim($(@).attr('class').replace('active', '').replace('hide', ''))
        google.maps.event.trigger(POINTS[key], 'mouseover')
        $(@).addClass('hover')
    , () ->
        $(@).removeClass('hover')
        key = $.trim($(@).attr('class').replace('active', '').replace('hide', ''))
        google.maps.event.trigger(POINTS[key], 'mouseout')

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
                $('#breadcrumb').empty().append(data.breadcrumb)
                handle_switcher(false)
                $('table.statistics tr.active').removeClass('active')
                POINTS[window.actual].setOptions
                    fillColor: '#000000'
                    zIndex: 30
                window.actual = $.trim($tr.attr('class').replace('hover', '').replace('hide', ''))
                POINTS[window.actual].setOptions
                    fillColor: '#ffffff'
                    zIndex: 40
                $tr.addClass('active')
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
        update_points()
        $('h1').removeClass('loading')

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
    type = $('#type-switcher').val()
    update_map_legend(window.extrems[statistics_key])

    # vykreslime okresy
    _.each window.shapes, (shape, key) ->
        if not shape
            return true

        # vypocet barvy
        value = window.districts[key]['statistics'][statistics_key]
        value = (value - window.extrems[statistics_key].min) / delta
        color = get_color(type, value)

        # vykresleni polygonu do mapy
        POLYS[key] = new google.maps.Polygon
            paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
            strokeColor: if key == window.actual_disctrict.toString() then '#555555' else color
            strokeOpacity: 1
            strokeWeight: 1
            fillColor: if key == window.actual_disctrict.toString() then '#555555' else color
            fillOpacity: 1
            zIndex: 10
        POLYS_COLORS[key] = color
        POLYS[key].setMap(MAP)

        google.maps.event.addListener POLYS[key], 'mouseover', () ->
            if key == window.actual_disctrict.toString()
                return
            POLYS[key].setOptions
                fillColor: '#444444'
                strokeColor: '#444444'
                zIndex: 15

        google.maps.event.addListener POLYS[key], 'mouseout', () ->
            if key == window.actual_disctrict.toString()
                return
            POLYS[key].setOptions
                fillColor: POLYS_COLORS[key]
                strokeColor: POLYS_COLORS[key]
                zIndex: 10

        google.maps.event.addListener POLYS[key], 'click', () ->
            if key == window.actual_disctrict.toString()
                return
            window.location = "#{ window.districts[key].url }_/"

    google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
        MAP.setZoom(MAP.getZoom())
    MAP.fitBounds(POLYS[window.actual_disctrict].getBounds())


POINTS = {}

# min/max rozmer kolecka, ktere reprezentuje obci
# (hodnota je v metrech)
POINT_MIN_RADIUS = 800
POINT_MAX_RADIUS = 3000

###
Vykresli obce ve forme ruzne velkych kolecek (v zavislosti na nastavenych
hodnotach v selektitkach nad mapou).
###
draw_points = () ->

    # pripravime se
    $table = $("table.statistics.#{ VIEW }")
    statistics_key = ajax_key()
    statistics_min = _.min(_.values(window.statistics[statistics_key]))
    statistics_max = _.max(_.values(window.statistics[statistics_key]))
    delta = statistics_max - statistics_min
    type = $('#type-switcher').val()
    color = get_color(type, .6)

    # vykreslime obce
    _.each window.points, (point, slug) ->
        if not point.point
            return true

        # vypocet velikosti kolca
        id = window.points[slug].id
        if id of window.statistics[statistics_key]
            value = window.statistics[statistics_key][id]
            value = if value then value else statistics_min
            value = (value - statistics_min) / delta
            radius = value * (POINT_MAX_RADIUS - POINT_MIN_RADIUS) + POINT_MIN_RADIUS
        else
            radius = POINT_MIN_RADIUS

        # vykresleni obce
        POINTS[slug] = new google.maps.Circle(
            center: new google.maps.LatLng(point.point[1], point.point[0])
            fillColor: if slug == window.actual then '#ffffff' else '#000000'
            fillOpacity: 1
            strokeOpacity: 0
            radius: radius
            zIndex: 30
            map: MAP
        )

        # hovery
        google.maps.event.addListener POINTS[slug], 'mouseover', () ->
            $tr = $table.find("tr.#{ slug }")
            $tr.addClass('hover')
            if slug == window.actual
                return
            POINTS[slug].setOptions(
                fillColor: '#ffffff'
                zIndex: 40
            )

        google.maps.event.addListener POINTS[slug], 'mouseout', () ->
            $table.find("tr.#{ slug }").removeClass('hover')
            if slug == window.actual
                return
            POINTS[slug].setOptions
                fillColor: '#000000'
                zIndex: 30

        # klikanec
        google.maps.event.addListener POINTS[slug], 'click', () ->
            if window.actual of POINTS
                POINTS[window.actual].setOptions
                    fillColor: '#000000'
                    zIndex: 30
            window.actual = slug
            $table.find("tr.#{ slug } a").click()


###
Aktualizace velikosti kolecek (mest) na mape (dle aktualne zvolenych voleb
v selektitkach).
###
update_points = () ->

    # rozsah zobrazovanych hodnot
    $table = $("table.statistics.#{ VIEW }")
    statistics_key = ajax_key()
    statistics_min = _.min(_.values(window.statistics[statistics_key]))
    statistics_max = _.max(_.values(window.statistics[statistics_key]))
    delta = statistics_max - statistics_min
    type = $('#type-switcher').val()
    color = get_color(type, .6)

    # aktualizujeme body
    _.each window.points, (point, slug) ->
        if not POINTS[slug]
            return true

        # vypocet velikosti kolca
        id = window.points[slug].id
        if id of window.statistics[statistics_key]
            value = window.statistics[statistics_key][id]
            value = if value then value else statistics_min
            value = (value - statistics_min) / delta
            radius = value * (POINT_MAX_RADIUS - POINT_MIN_RADIUS) + POINT_MIN_RADIUS
        else
            radius = POINT_MIN_RADIUS

        # aktualizace
        POINTS[slug].setOptions
            radius: radius


###
Aktualizace barev vykreslenych polygonu na mape (dle aktualne zvolenych voleb
v selektitkach a datech v tabulce).
###
update_shapes = () ->

    select_legend_handler2()
    statistics_key = ajax_key()
    delta = window.extrems[statistics_key].max - window.extrems[statistics_key].min
    type = $('#type-switcher').val()
    update_map_legend(window.extrems[statistics_key])

    _.each window.shapes, (shape, key) ->
        if not POLYS[key]
            return true

        value = window.districts[key]['statistics'][statistics_key]
        value = (value - window.extrems[statistics_key].min) / delta
        color = get_color(type, value)

        POLYS_COLORS[key] = color
        POLYS[key].setOptions
            strokeColor: if key == window.actual_disctrict.toString() then '#555555' else color
            fillColor: if key == window.actual_disctrict.toString() then '#555555' else color



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
        window.points = data['details']
        window.statistics = data['statistics']

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
        panControl: false
        zoomControl: true
        zoomControlOptions:
            style: google.maps.ZoomControlStyle.SMALL

    MAP = new google.maps.Map(document.getElementById("map"), map_options)
    styledMapType = new google.maps.StyledMapType(MAP_STYLE, {name:'Černobílá'})
    MAP.mapTypes.set('CB', styledMapType)
    map_legend()

    # vykresleni polygonu (kraje/okresy)
    draw_shapes()
    # vykresleni bodu (obci)
    draw_points()
    $('h1').removeClass('loading')

    handle_table()
    handle_switcher()
    select_legend_handler()

# -----------------------------------------------------------------------------

$(document).ready () ->
    load_maps_api()
