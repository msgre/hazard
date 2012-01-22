###
Kod pro uvodni stranky MF kampane.
###

###
Naseptavac na uvodni strance kampane MF VLT.
###

renderMenu = (ul, items) ->
    self = @
    current_category = ''
    $.each items, (index, item) ->
        if item.category != current_category
            ul.append("<li class='ui-autocomplete-category'>#{ item.category }</li>")
            current_category = item.category
        self._renderItem(ul, item)


###
Vykresleni barevnych polygonu kraju do mapy.
###
draw_shapes = () ->

    statistics_key = 'conflict_hell_counts'
    min = _.min(_.values(window.statistics[statistics_key]))
    max = _.max(_.values(window.statistics[statistics_key]))
    delta = max - min
    type = 'hells'

    # vykreslime kraje
    _.each window.shapes, (shape, key) ->
        if not shape
            return true

        # vypocet barvy
        value = window.regions[key]['statistics'][statistics_key]
        value = (value - min) / delta
        color = get_color(type, value)

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

        google.maps.event.addListener POLYS[key], 'mouseover', () ->
            POLYS[key].setOptions
                fillColor: '#444444'
                strokeColor: '#444444'
                zIndex: 15

        google.maps.event.addListener POLYS[key], 'mouseout', () ->
            POLYS[key].setOptions
                fillColor: POLYS_COLORS[key]
                strokeColor: POLYS_COLORS[key]
                zIndex: 10

        google.maps.event.addListener POLYS[key], 'click', () ->
            window.location = "/#{ key }/kampan/mf/"


###
Ajaxove nacteni geografickych dat o polygonech a asynchronni load Google Maps API.
###
load_maps_api = () ->
    $('h1').addClass('loading')
    $.getJSON '/kampan/mf/ajax/kraje/', (data) ->
        # NOTE: rychla prasarna
        # copy/paste kodu pro regiony a obce a jeho ohnuti pro potreby uvodni
        # stranky (kde nemame selektitka, ani zadne souvisejici data v HTML
        # strukture). Jedine co chceme je vykresleni mapy podle jednoho kriteria
        # a po kliknuti soupnuti na patricne URL kraje a MF kampane
        window.shapes = {}
        window.regions = {}
        for key in _.keys(data['details'])
            window.shapes[key] = data['details'][key]['shape']
            window.regions[key] = data['details'][key]
            id = data['details'][key].id.toString()
            window.regions[key].statistics = {}
            for k of data['statistics']
                window.regions[key].statistics[k] = data['statistics'][k][id]
            window.statistics = data['statistics']

        script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map'
        document.body.appendChild(script)


###
Inicializace map, volana jako callback po asynchronnim nacteni Google Maps API.
###
window.late_map = () ->

    # inicializace mapy
    map_options =
        zoom: 6
        center: new google.maps.LatLng(49.78512, 15.41765)
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

    draw_shapes()
    $('h1').removeClass('loading')


# -----------------------------------------------------------------------------

$(document).ready () ->
    load_maps_api()

    $.widget('custom.catcomplete', $.ui.autocomplete, {
        _renderMenu: renderMenu
    })

    $('#search').catcomplete
        delay: 0
        source: '/autocomplete/'
        select: (event, ui) ->
            window.location = "#{ ui.item.url }kampan/mf/"
