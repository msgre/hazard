###
Upravy HTML stranky.

Pretaveni statickeho zradlicka pro boty do interaktivni podoby, kterou budou
pouzivat lidi.
###
class ModifyHtml

    modify: () ->
        @modifyTable()
        @modifyDistrictTable()
        @injectControl()
        @injectLegend()
        @injectMap()
        @modifySubobjects()
        @injectDescription()

    # pryc s hlavickou tabulky
    modifyTable: () ->
        $('#statistics thead').remove()

    injectDescription: () ->
        $('.wrapper:first').before('<p id="table-description">V tabulce je zobrazen <span></span>.</p>')

    # sup do stranky se selektitky, ktere budou prepinat pohled na data
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

    # sup do stranky s legendou k mape
    injectLegend: () ->
        html = '<p id="legend" class="hide"></p>'
        $('#control').after(html)
        $('#control a').click () ->
            $('#legend').slideToggle('fast')
            false

    # sup do stranky s mapou (a Google Maps API)
    # TODO: mame tady natvrdo mapovy klic; to asi neni uplne koser...
    injectMap: () ->
        html = '<div id="map"></div>'
        $('#legend').after(html)

        script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'http://maps.googleapis.com/maps/api/js?key=AIzaSyDw1uicJmcKKdEIvLS9XavLO0RPFvIpOT4&v=3&sensor=false&callback=window.init_map'
        document.body.appendChild(script)

    # specielni osetreni tabulky s vypisem okresu -- schovame vsechny radky
    # ktere nepatri do aktualniho kraje a prida za tabulku jejich odkryvatko
    modifyDistrictTable: () ->
        if PAGE_TYPE == 'district'
            $table = $('#statistics')

            # schovame radky z jinych kraju
            $table.find('tr').each () ->
                $tr = $(@)
                classes = _.filter($tr.attr('class').split(' '), (i) -> i.length > 0 and i.indexOf('region_') == 0)
                region = classes[0].replace('region_', '')
                if region != parseUrl().region
                    $tr.addClass('hide')

            # vlozime link za tabulku na odhaleni i zbytku okresu
            $table.parent().after("""
                <p><i>Poznámka: V tabulce jsou vypsány pouze okresy z aktuálního
                kraje. Chcete raději zobrazit <a href="#" id="show-all-districts">všechny
                okresy ČR</a>?</i></p>
            """)
            $link = $('#show-all-districts')
            $link.click () ->
                first = $table.find('tr:not(.hide):first')
                $table.find('tr').removeClass('hide')
                $table.parent().stop().scrollTo(first)
                $link.closest('p').fadeOut(200, () -> $(@).remove())
                return false

    # nahrazeni <ul><li> seznamu za kompaktnejsi selektitko
    modifySubobjects: () ->
        $objs = $('#sub-objects')
        options = []
        $objs.find('a').each () ->
            $item = $(@)
            options.push """
                <option value="#{ $item.attr('href') }">
                    #{ $item.text() }
                </option>"""
        $objs.replaceWith """
            <select id="sub-objects">
                <option value="">Vyberte si...</option>
                #{ options.join('') }
            </select>
        """

        $('#sub-objects').change () ->
            val = $(@).val()
            if val
                $('h1').addClass('loading')
                window.location = val

# inicializace mapy
# obyc fce, protoze je volana jako callback asynchronniho natazeni Google map
window.init_map = () ->
    MAP = new google.maps.Map document.getElementById("map"),
        disableDoubleClickZoom: true
        scrollwheel: false
        zoom: 6
        center: new google.maps.LatLng(49.38512, 14.61765) # stred CR
        mapTypeControl: false,
        mapTypeId: 'CB'
        streetViewControl: false
        panControl: false
        zoomControl: true
        zoomControlOptions:
            style: google.maps.ZoomControlStyle.SMALL
    MAP.mapTypes.set('CB', new google.maps.StyledMapType(MAP_STYLE, {name:'Černobílá'}))
    HazardEvents.trigger('Google:map_initialized')


# --- meso (stara mama) -------------------------------------------------------

$(document).ready () ->
    # nejdriv si upravime HTML...
    window.modifier = new ModifyHtml
    window.modifier.modify()

    # a teprve pak zasuneme pater...
    App = new AppView
        geo_objects: new GeoObjectList

    # specialitky pro ruzne typy stranek
    if PAGE_TYPE == 'district' or PAGE_TYPE == 'town'
        if PAGE_TYPE == 'town'
            # obce vykresli tvary okresu
            App.loadDistricts()
        # okresy/obce vykresli obrysy kraju
        App.loadRegions()
