###
Uvodni text.
###
class PrimerView extends Backbone.View
    initialize: () ->
        # do stranky se natahly nove HTML fragmenty
        @collection.bind('TableRowView:page_fragments_changed', @render, @)
        # po kazdem prekresleni tabulky (vetsinou vlivem zmeny control
        # selektitek) obhospodarime i uvodni text
        @collection.bind('GeoObjectList:redraw_done', @render, @)
        # pomocne promenne
        @type = $('#type')

    render: () ->
        log('PrimerView.render')
        type = @type.val()
        @$el.find('.snippet').each () ->
            snippet = $(@)
            if snippet.hasClass(type)
                snippet.removeClass('hide')
            else
                snippet.addClass('hide')
        return @


###
Popis toho co se zobrazuje v tabulce.
###
class DescriptionView extends Backbone.View
    initialize: () ->
        @collection.bind('GeoObjectList:redraw_done', @render, @)
        # pomocne promenne
        @types = $('#type option')
        @parameters = $('#parameter option')

    render: () ->
        log('DescriptionView.render')
        type = @types.filter(':selected').text()
        parameter = @parameters.filter(':selected').text()
        @$el.text("#{ parameter } #{ type }")
        return @


###
Jeden radek tabulky == jeden kraj/okres/obec.

Kazdemu radku odpovida nejaky graficky objekt v mape, se kterym pak spolecne
reaguje na udalosti od uzivatele (hover, click).
###
class TableRowView extends Backbone.View
    # udalosti nad <tr>
    events:
        "mouseover": "mouseover"
        "mouseout" : "mouseout"
        "click"    : "click"
        "dblclick" : "dblclick"

    initialize: () ->
        @model.bind('change:hover',      @renderHover,              @)
        @model.bind('change:active',     @renderActiveAndCalcValue, @)
        @model.bind('change:calc_value', @renderActiveAndCalcValue, @)
        @model.bind('change',            @render,                   @)
        @model.bind('TableRowView:page_fragments_prepared', @renderFragments, @)

    # zvyrazneni radku v tabulce a objektu v mape
    renderHover: () ->
        log('TableRowView.renderHover')

        @$el.toggleClass('hover')
        if @$el.hasClass('hover')
            @updateGObject('hover')
        else
            if @model.get('active')
                @updateGObject('active')
            else
                @updateGObject('normal')

    # zvyrazneni aktivniho radku a objektu v mape, aktualizace barvy/velikosti objektu
    renderActiveAndCalcValue: () ->
        log('TableRowView.renderActiveAndCalcValue')

        changed = _.keys(@model.changedAttributes() or {})
        if 'active' in changed
            @$el.toggleClass('active')
        if @$el.hasClass('active')
            if @$el.hasClass('hover')
                @updateGObject('hover')
            else
                @updateGObject('active')
        else
            @updateGObject('normal')

    # novy obsah do fragmentu stranky
    renderFragments: () ->
        fragments = @model.get('json_fragments')
        $('#breadcrumb').html(fragments.breadcrumb)
        $('#primer').html(fragments.primer_content)
        $('h1').text(@model.get('title'))
        $('#sub-objects').replaceWith(fragments.sub_objects)
        $('#submenu').replaceWith(fragments.submenu)
        window.modifier.modifySubobjects()

        @model.trigger('TableRowView:page_fragments_changed')

    # vykresleni radky tabulky
    render: () ->
        log('TableRowView.render')

        # pokud se meni pouze "neskodne" parametry, zkratneme to
        # (o toto se staraji specialni renderXXX metody)
        ignore = ['hover', 'active', 'shape', 'gobj', 'calc_value', 'json_fragments']
        changed = _.keys(@model.changedAttributes() or [])
        if changed.length and _.all(changed, (i) -> i in ignore)
            log('TableRowView.render:shortcut')
            return @

        # sablona potrebuje mit informaci o aktualne nastavenych hodnotach
        # v control selektitkach (podle nich pozna, ktery sloupec ma svitit)
        context = @model.toJSON()
        _.extend(context,
            type: @collection.type.val()
            parameter: @collection.parameter.val()
        )
        content = _.template($('#gobj-item-template').html(), context)
        @$el.html(content)

        return @

    # vykresleni grafickeho objektu do mapy
    drawGObject: () ->
        log('TableRowView.drawGObject')

        type = @model.get('type')
        if type == 'town'
            # mesta reprezentujeme jako kolecka ruzne velikosti
            point = @model.get('point')
            gobj = new google.maps.Circle
                center: new google.maps.LatLng(point[1], point[0])
                fillColor: MAP_CIRCLE_COLOR
                fillOpacity: 1
                strokeOpacity: 1
                strokeWeight: 1
                strokeColor: '#000000'
                radius: POINT_MIN_RADIUS
                zIndex: MAP_CIRCLE_ZINDEX
                map: MAP
        else
            # okresy/kraje jako ruznobarevne polygony
            shape = @model.get('shape')
            gobj = new google.maps.Polygon
                paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
                strokeColor: MAP_ACTIVE_POLY_COLOR
                strokeOpacity: 1
                strokeWeight: 2
                fillColor: MAP_ACTIVE_POLY_COLOR
                fillOpacity: 1
                zIndex: MAP_POLY_ZINDEX
                map: MAP

        # zaveseni udalosti na objekt v mape
        google.maps.event.addListener gobj, 'mouseover', () =>
            $('#statistics').parent().stop().scrollTo(
                "##{ PAGE_TYPE }_#{ @model.get('slug') }",
                200,
                {stop: true}
            )
            @$el.trigger('mouseover')
        google.maps.event.addListener gobj, 'mouseout', () =>
            @$el.trigger('mouseout')

        # NOTE: trosku pakarna, ale jinak to asi nejde
        # Kdyz dblclicknu v mape, Google odpali jak udalost click, tak dblclick
        # Proto je treba v pripade single clicku zachovat klid a chvilku
        # poseckat. Pokud se jedna o dbclick, tak je obsluha single clicku
        # zariznuta.

        update_timeout = null
        google.maps.event.addListener gobj, 'click', () =>
            update_timeout = setTimeout(() =>
                if PAGE_TYPE == 'district' and @$el.hasClass('hide')
                    $('#show-all-districts').click()
                @$el.trigger('click')
            , 300)
        if PAGE_TYPE != 'town'
            google.maps.event.addListener gobj, 'dblclick', () =>
                clearTimeout(update_timeout)
                @$el.trigger('dblclick')

        @model.set({gobj: gobj})
        gobj

    # upravi podobu grafickych objektu v mape v zavislosti na jejich stavu
    # (hover, active, normal)
    updateGObject: (state) ->
        calc_value = @model.get('calc_value')
        log("TableRowView.updateGObject:state=#{ state }, calc_value=#{ calc_value }")

        if 'GObjectsDrawingAllowed' not of EVENTS_CACHE
            log("TableRowView.updateGObject:map drawing is disallowed now")
            return

        gobj = @model.get('gobj') or @drawGObject()
        if not gobj
            log("TableRowView.updateGObject:no geo object to update")
            return

        type = @model.get('type')
        if type == 'town'
            # obcim budeme menit radius
            if state == 'hover'
                options =
                    radius: calc_value
                    fillColor: MAP_HOVER_CIRCLE_COLOR
                    strokeColor: MAP_HOVER_CIRCLE_COLOR
                    zIndex: MAP_HOVER_CIRCLE_ZINDEX
            else if state == 'active'
                options =
                    radius: calc_value
                    fillColor: MAP_ACTIVE_CIRCLE_COLOR
                    strokeColor: MAP_ACTIVE_CIRCLE_BORDER_COLOR
                    zIndex: MAP_ACTIVE_CIRCLE_ZINDEX
            else
                options =
                    radius: calc_value
                    fillColor: MAP_CIRCLE_COLOR
                    strokeColor: MAP_CIRCLE_COLOR
                    #strokeColor: '#000000'
                    zIndex: MAP_CIRCLE_ZINDEX
        else
            if state == 'hover'
                options =
                    fillColor: MAP_HOVER_POLY_COLOR
                    strokeColor: MAP_HOVER_POLY_COLOR
                    zIndex: MAP_HOVER_POLY_ZINDEX
            else if state == 'active'
                options =
                    fillColor: calc_value
                    strokeColor: MAP_ACTIVE_POLY_COLOR
                    zIndex: MAP_ACTIVE_POLY_ZINDEX
            else
                options =
                    fillColor: calc_value
                    strokeColor: calc_value
                    zIndex: MAP_POLY_ZINDEX

        gobj.setOptions(options)
        log('TableRowView.updateGObject:done')

    # --- udalosti od mysi ----------------------------------------------------

    mouseover: () ->
        @model.set({hover: true})

    mouseout: () ->
        @model.set({hover: false})

    click: () ->
        json_fragments = @model.get('json_fragments')
        $h1 = $('h1')

        # obsluha pro JSON odpoved ze serveru
        prepare_fragments = (resp, status, xhr) =>
            # aktualizujeme data v modelu a dame vedet, ze fragmenty jsou ready
            if not json_fragments
                @model.set({json_fragments: resp})
            @model.trigger('TableRowView:page_fragments_prepared')

            # aktualizujeme URL prohlizece
            Backbone.history.navigate(@$el.find('a').attr('href'), {replace: true})
            $h1.removeClass('loading')

        # mame uz menene fragmenty nactene?
        if not json_fragments
            # ne-e; vyzobneme data ze serveru
            $h1.addClass('loading')
            options =
                url: "#{ @$el.find('a').attr('href') }?ajax" # NOTE: mrdka, musim pridat neco k URL, jinak prohlizec odpovedi kesuje a pak nabizi po stisku tlacitka Back JSON data
                success: prepare_fragments
            Backbone.sync('read', @, options)
        else
            # jo-o
            prepare_fragments(json_fragments)

        # nastaveni aktivniho radku
        _.each @collection.active(), (gobj) -> gobj.set({active: false})
        @model.set({active: true})
        false

    # dvojklik nas posle na uzemne nizsi celek (napr. kraj -> okres)
    dblclick: () ->
        if PAGE_TYPE != 'town'
            $('h1').addClass('loading')
            url = @$el.find('a').attr('href')
            url = "#{ url.replace('/kampan/mf/', '') }/_/"
            window.location = url
        false


###
Tabulka kraju/okresu/mest.
###
class TableView extends Backbone.View

    initialize: () ->
        # reference na ovladaci selektitka ve strance
        @type      = $('#type')
        @parameter = $('#parameter')
        # jakmile se aktualizuji vsechny radky v tabulce, hupnem na to
        @collection.bind('GeoObjectList:redraw_done', @render, @)
        # pomocnici
        @statistics = $('#statistics')

    ###
    Projede tabulku s regiony a interpretuje hodnotu v druhem sloupci do podoby
    grafu (napozicuje obrazek na pozadi radku tabulky).

    Poznamka: tato metoda je povesena na udalost "GeoObjectList:redraw_done",
    kterou odpaluje kolekce GeoObjectList na konci metody redraw.
    Puvodne jsem si myslel, ze tuhle funkcionalitu bude delat primo TableRowView,
    ale nejde to. Nejdrive je totiz treba vykreslit vsechny radky tabulky
    (tj. TableRowView.render) a teprve **potom** muzu kreslit grafy. Duvod je
    ten, ze dynamicky nalevany obsah sibuje s rozmery bunek a pro vykresleni
    grafu potrebuji znat jejich rozmery.
    ###
    render: () ->
        log('TableView.render')
        width = @$el.width()
        td1_w = @$el.find('tr:not(.hide) td:first').width()
        td2_w = width - td1_w

        type = @type.val()
        parameter = @parameter.val()
        max = if parameter == 'conflict_perc' then 100 else EXTREMS[type][parameter].max
        min = 0

        log @collection.length
        @collection.each (gobj, idx) =>
            $tr = @$("tr:eq(#{ idx })")
            $td1 = $tr.find('td:first')
            $td2 = $tr.find(":not(:first):not(.hide)")

            # vypocet pozice grafu
            statistics_map = gobj.get('statistics_map')
            if statistics_map[type][parameter] != undefined
                w = Math.round((statistics_map[type][parameter] - min) / max * width)
                if w > td1_w
                    x1 = 1000
                    x2 = w - td1_w
                else
                    x1 = w
                    x2 = 0
            else
                w = 0
                x1 = 0
                x2 = 0

            # uprava tabulky podle vypoctenych hodnot
            $td1.css('background-position', "#{ x1 }px 0")
            $td2.css('background-position', "#{ x2 }px 0")

            if PAGE_TYPE == 'town'
                calc_value = w / width * POINT_MAX_RADIUS
                if calc_value < POINT_MIN_RADIUS
                    calc_value = POINT_MIN_RADIUS
            else
                # nastaveni barev polygonu kraje
                if statistics_map[type][parameter] != undefined
                    calc_value = get_color(type, (statistics_map[type][parameter] - EXTREMS[type][parameter].min) / EXTREMS[type][parameter].max)
                else
                    calc_value = get_color(type, 0)
            gobj.set({calc_value: calc_value})

        @statistics.parent().stop().scrollTo(@$el.find('tr.active'), {stop: true})

        @


###
Napoveda k mape.
###
class LegendView extends Backbone.View
    initialize: () ->
        # zaveseni na dokonceni prekreslovani tabulky
        @collection.bind('GeoObjectList:redraw_done', @render, @)
        # pomocne reference na ovladaci selektitka ve strance
        @type      = $('#type')
        @parameter = $('#parameter')

    render: () ->
        log('LegendView.render')
        type = @type.val()
        parameter = @parameter.val()
        @$el.empty()
        content = "#{ LEGENDS[PAGE_TYPE][type][parameter] }<br>#{ CONTROL_LEGEND }"
        @$el.append(content)
        return @


###
Obrysy kraju v mape.

Pouziva se v pohledu na okres/obec, pro lepsi orientaci v mape. Nema zadnou
dalsi funkcnost.
###
class RegionView extends Backbone.View
    strokeColorValue: 0.24

    initialize: () ->
        @collection.bind('AppView:draw_regions', @render, @)
        @options.geo_objects.bind('GeoObjectList:redraw_done', @update, @)
        # pomocne promenne
        @type = $('#type')

    render: () ->
        log('RegionView.render')
        shapes = @model.get('shape')
        active = @model.get('active')
        paths = ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shapes)
        for path in paths
            poly = new google.maps.Polyline
                path: path
                strokeColor: if active then '#f4f3f0' else get_color(@type.val(), @strokeColorValue)
                strokeOpacity: 1
                strokeWeight: 2
                zIndex: if active then MAP_BORDERS_ZINDEX + 1 else MAP_BORDERS_ZINDEX
                map: MAP
                clickable: false
            @model.set({poly: poly})

        # fokus na kraj
        if active and PAGE_TYPE == 'district'
            setPolygonBoundsFn()
            polygon = new google.maps.Polygon
                path: paths
            google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
                zoom = MAP.getZoom()
                if zoom > 8
                    zoom = 8
                MAP.setZoom(zoom)
            MAP.fitBounds(polygon.getBounds())
        @

    update: () ->
        log('RegionView.update')
        if 'RegionsDrawingAllowed' of EVENTS_CACHE
            poly = @model.get('poly')
            active = @model.get('active')
            poly.setOptions
                strokeColor: if active then '#777777' else get_color(@type.val(), @strokeColorValue)
            log('RegionView.update:polygon updated')


###
Okresy v mape.

Pouziva se v pohledu na obce. Mapa se fokusne na dany okres (vykresleny neutralni
tmavou barvou) a mesta v nem. Okolni okresy se pak vykreslni s pomoci tohoto
view jako ruznobarevne polygony.
###
class DistrictView extends Backbone.View
    strokeColorValue: 0.24

    initialize: () ->
        @collection.bind('AppView:draw_districts', @render, @)
        @options.geo_objects.bind('GeoObjectList:redraw_done', @update, @)
        @type = $('#type')
        @parameter = $('#parameter')

    render: () ->
        log('DistrictView.render')
        shape = @model.get('shape')
        active = @model.get('active')
        color = @getColor()
        gobj = new google.maps.Polygon
            paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
            strokeColor: color
            strokeOpacity: 1
            strokeWeight: 2
            fillColor: color
            fillOpacity: 1
            zIndex: if active then MAP_ACTIVE_POLY_ZINDEX else MAP_POLY_ZINDEX
            map: MAP
            clickable: not active
        @model.set
            gobj: gobj
            color:color

        # zaveseni udalosti na objekt v mape
        if not active
            google.maps.event.addListener gobj, 'mouseover', () =>
                @updateGObject('hover')

            google.maps.event.addListener gobj, 'mouseout', () =>
                @updateGObject('normal')

            google.maps.event.addListener gobj, 'click', () =>
                $('h1').addClass('loading')
                window.location = "#{ @model.get('url') }_/"

        # fokus na okres
        if active
            setPolygonBoundsFn()
            google.maps.event.addListenerOnce MAP, 'zoom_changed', () ->
                zoom = MAP.getZoom()
                if zoom > 9
                    zoom = 9
                MAP.setZoom(zoom)
            MAP.fitBounds(gobj.getBounds())
        @

    update: () ->
        log('DistrictView.update')
        if 'DistrictsDrawingAllowed' of EVENTS_CACHE
            gobj = @model.get('gobj')
            color = @getColor()
            gobj.setOptions
                strokeColor: color
                fillColor: color
            @model.set({color: color})
            log('DistrictView.update:polygon updated')

    getColor: () ->
        active = @model.get('active')
        statistics_map = @model.get('statistics_map')

        # TODO: v pripade procent se to pocita jinak?
        type = @type.val()
        parameter = @parameter.val()
        min = @collection.extrems[type][parameter].min
        max = @collection.extrems[type][parameter].max
        v = if type of statistics_map and parameter of statistics_map[type] then statistics_map[type][parameter] else min
        v2 = (v - min) / max
        color = if active then MAP_ACTIVE_POLY_COLOR else get_color(type, not isNaN(v2) and v2 or 0)

    updateGObject: (state) ->
        color = @model.get('color')
        gobj = @model.get('gobj')
        if state == 'hover'
            options =
                fillColor: MAP_HOVER_POLY_COLOR
                strokeColor: MAP_HOVER_POLY_COLOR
                zIndex: MAP_HOVER_POLY_ZINDEX
        else if state == 'active'
            options =
                fillColor: color
                strokeColor: MAP_ACTIVE_POLY_COLOR
                zIndex: MAP_ACTIVE_POLY_ZINDEX
        else
            options =
                fillColor: color
                strokeColor: color
                zIndex: MAP_POLY_ZINDEX
        gobj.setOptions(options)


###
Aplikace. Hlavni view. Matka matek.
###
class AppView extends Backbone.View
    el: $('#app')

    initialize: () ->
        $('h1').addClass('loading')

        # nacteme data
        log('AppView.initialize:fetch')
        @options.geo_objects.fetch()

        # propojime prvky z kolekce s view (jednotlivymi radky tabulky)
        log('AppView.initialize:TableRowView')
        @options.geo_objects.each (gobj) =>
            new TableRowView
                model: gobj
                collection: @options.geo_objects
                el: $("##{ PAGE_TYPE }_#{ gobj.get('slug') }")
            gobj.trigger('change')

        # view nad celou tabulkou
        log('AppView.initialize:TableView')
        new TableView
            el: $("#statistics")
            collection: @options.geo_objects

        # view pro uvodni text
        log('AppView.initialize:PrimerView')
        new PrimerView
            el: $("#primer")
            collection: @options.geo_objects

        # view pro legendu k mape
        log('AppView.initialize:LegendView')
        new LegendView
            el: $("#legend")
            collection: @options.geo_objects

        # view pro popis tabulky
        log('AppView.initialize:DescriptionView')
        new DescriptionView
            el: $("#table-description span")
            collection: @options.geo_objects

        # tak ja si myslim, ze troska historie taky jeste nikoho nezabila...
        Backbone.history = new Backbone.History
        Backbone.history.start({pushState: true})

    # --- pomocne obrysy kraju ------------------------------------------------

    loadRegions: () ->
        log('AppView.loadRegions')
        @options.region_list = new RegionList
        @options.region_list.bind('add', @createRegionView, @)
        @options.region_list.fetch()

    createRegionView: (region) ->
        log('AppView.createRegionView')
        view = new RegionView
            model: region
            collection: @options.region_list
            geo_objects: @options.geo_objects

    # --- pomocne tvary (a barevnost) okresu ----------------------------------

    loadDistricts: () ->
        log('AppView.loadDistricts')
        @options.district_list = new DistrictList
        @options.district_list.bind('add', @createDistrictView, @)
        @options.district_list.fetch()

    createDistrictView: (district) ->
        log('AppView.createDistrictView')
        view = new DistrictView
            model: district
            collection: @options.district_list
            geo_objects: @options.geo_objects
