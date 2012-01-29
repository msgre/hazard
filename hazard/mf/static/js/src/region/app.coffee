###
TODO:

- nacist informace o krajich z JSONu ze serveru
###

###
Upravy HTML stranky.

Pretaveni statickeho zradlicka pro boty do interaktivni podoby, kterou budou
pouzivat lidi.
###
class ModifyHtml

    modify: () ->
        @modifyTable()
        @injectControl()
        @injectLegend()
        @injectMap()

    modifyTable: () ->
        $('#statistics thead').remove()

    injectControl: () ->
        makeOption = (value, key) ->
            "<option value=\"#{ key }\">#{ value }</option>"
        html = """
            <p id="control">
                Zobrazit
                    <select id="parameter">#{ _.map(PARAMETERS, makeOption).join('\n') }</select>
                    <select id="type">#{ _.map(TYPES, makeOption).join('\n') }</select>
                <a href="#">Legenda +</a>
            </p>
        """
        $('#right-col').append(html)

    injectLegend: () ->
        html = '<p id="legend" class="hide"></p>'
        $('#control').after(html)
        $('#control a').click () ->
            $('#legend').slideToggle('fast')
            false

    injectMap: () ->
        html = '<div id="map"></div>'
        $('#legend').after(html)

        script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.late_map'
        document.body.appendChild(script)

MAP = undefined

# TODO: kam s tim?
window.late_map = () ->
    map_options =
        zoom: 6
        center: new google.maps.LatLng(49.38512, 14.61765) # stred CR
        mapTypeControl: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP
        streetViewControl: false
        panControl: false
        zoomControl: true
        zoomControlOptions:
            style: google.maps.ZoomControlStyle.SMALL

    MAP = new google.maps.Map(document.getElementById("map"), map_options)
    HazardEvents.trigger('map:init')


$(document).ready () ->
    # nejdriv si upravime HTML...
    modify = new ModifyHtml
    modify.modify()

    Regions = new RegionList
    App = new AppView
        regions: Regions
