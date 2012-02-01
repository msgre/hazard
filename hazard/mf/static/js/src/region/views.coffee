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
        @el.find('.snippet').each () ->
            snippet = $(@)
            if snippet.hasClass(type)
                snippet.removeClass('hide')
            else
                snippet.addClass('hide')
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
        @model.bind('change:hover',          @renderHover,          @)
        @model.bind('change:active',         @renderActiveAndColor, @)
        @model.bind('change:color',          @renderActiveAndColor, @)
        @model.bind('change',                @render,               @)
        @model.bind('TableRowView:page_fragments_prepared', @renderFragments, @)

    # zvyrazneni radku v tabulce a objektu v mape
    renderHover: () ->
        log('TableRowView.renderHover')

        @el.toggleClass('hover')
        if @el.hasClass('hover')
            @updateGObject('hover')
        else
            if @model.get('active')
                @updateGObject('active')
            else
                @updateGObject('normal')

    # zvyrazneni aktivniho radku a objektu v mape, aktualizace barvy objektu
    renderActiveAndColor: () ->
        log('TableRowView.renderActiveAndColor')

        changed = _.keys(@model.changedAttributes() or {})
        if 'active' in changed
            @el.toggleClass('active')
        if @el.hasClass('active')
            if @el.hasClass('hover')
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
        @model.trigger('TableRowView:page_fragments_changed')

    # vykresleni radky tabulky
    render: () ->
        log('TableRowView.render')

        # pokud se meni pouze "neskodne" parametry, zkratneme to
        # (o toto se staraji specialni renderXXX metody)
        ignore = ['hover', 'active', 'shape', 'poly', 'color', 'json_fragments']
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
        @el.html(content)

        return @

    # vykresleni grafickeho objektu do mapy
    drawGObject: () ->
        log('TableRowView.drawGObject')

        shape = @model.get('shape')
        poly = new google.maps.Polygon
            paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
            strokeColor: MAP_ACTIVE_POLY_COLOR
            strokeOpacity: 1
            strokeWeight: 2
            fillColor: MAP_ACTIVE_POLY_COLOR
            fillOpacity: 1
            zIndex: MAP_POLY_ZINDEX
            map: MAP

        # zaveseni udalosti na objekt v mape
        google.maps.event.addListener poly, 'mouseover', () =>
            $('#statistics').parent().stop().scrollTo(
                "##{ PAGE_TYPE }_#{ @model.get('slug') }",
                200,
                {stop: true}
            )
            @el.trigger('mouseover')
        google.maps.event.addListener poly, 'mouseout', () =>
            @el.trigger('mouseout')

        # NOTE: trosku pakarna, ale jinak to asi nejde
        # Kdyz dblclicknu v mape, Google odpali jak udalost click, tak dblclick
        # Proto je treba v pripade single clicku zachovat klid a chvilku
        # poseckat. Pokud se jedna o dbclick, tak je obsluha single clicku
        # zariznuta.

        update_timeout = null
        google.maps.event.addListener poly, 'click', () =>
            update_timeout = setTimeout(() =>
                @el.trigger('click')
            , 300)
        google.maps.event.addListener poly, 'dblclick', () =>
            clearTimeout(update_timeout)
            @el.trigger('dblclick')

        @model.set({poly: poly})
        poly

    # upravi podobu grafickych objektu v mape v zavislosti na jejich stavu
    # (hover, active, normal)
    updateGObject: (state) ->
        color = @model.get('color')
        log("TableRowView.updateGObject:state=#{ state }, color=#{ color }")

        if 'MapDrawingAllowed' not of EVENTS_CACHE
            log("TableRowView.updateGObject:map drawing is disallowed now")
            return

        poly = @model.get('poly') or @drawGObject()
        if not poly
            log("TableRowView.updateGObject:no geo object to update")
            return

        if state == 'hover'
            options =
                fillColor: MAP_HOVER_POLY_COLOR
                strokeColor: MAP_HOVER_POLY_COLOR
                zIndex: MAP_POLY_ZINDEX
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

        poly.setOptions(options)
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
            Backbone.history.navigate(@el.find('a').attr('href'))
            $h1.removeClass('loading')

        # mame uz menene fragmenty nactene?
        if not json_fragments
            # ne-e; vyzobneme data ze serveru
            $h1.addClass('loading')
            options =
                url: @el.find('a').attr('href')
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
        $('h1').addClass('loading')
        url = @el.find('a').attr('href')
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
        width = @el.width()
        td1_w = @el.find('tr:not(.hide) td:first').width()
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
                x1 = 0
                x2 = 0

            # uprava tabulky podle vypoctenych hodnot
            $td1.css('background-position', "#{ x1 }px 0")
            $td2.css('background-position', "#{ x2 }px 0")

            # nastaveni barev polygonu kraje
            if statistics_map[type][parameter] != undefined
                color = get_color(type, (statistics_map[type][parameter] - EXTREMS[type][parameter].min) / EXTREMS[type][parameter].max)
            else
                color = get_color(type, 0)
            gobj.set({color: color})

        return @


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
        @el.empty()
        content = "#{ LEGENDS[PAGE_TYPE][type][parameter] }<br>#{ CONTROL_LEGEND }"
        @el.append(content)
        return @


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

        # tak ja si myslim, ze troska historie taky jeste nikoho nezabila...
        Backbone.history = new Backbone.History
        Backbone.history.start({pushState: true})
