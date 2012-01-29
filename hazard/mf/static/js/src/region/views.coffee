# TODO: musim projet update_polys, a nejak to zjednodusit


###
Uvodni text.
###
class PrimerView extends Backbone.View
    initialize: () ->
        @type = $('#type')
        # systemove udalosti
        @type.bind('change', _.bind(@render, @))
        @collection.bind('fragments:change', @render, @)

    render: () ->
        type = @type.val()
        @el.find('.snippet').each () ->
            snippet = $(@)
            if snippet.hasClass(type)
                snippet.removeClass('hide')
            else
                snippet.addClass('hide')
        return @


###
Jeden radek tabulky == jeden kraj.
###
class RegionRowView extends Backbone.View
    # udalosti nad <tr>
    events:
        "mouseover": "mouseover"
        "mouseout" : "mouseout"
        "click"    : "click"

    initialize: () ->
        # systemove udalosti
        @model.bind('change',           @render,      @)
        @model.bind('map:update_polys', @updatePolys, @)

    # Vykresli polygony s krajema do mapy.
    createPolys: () ->
        shape = @model.get('shape')

        # vykresleni polygonu
        # TODO: jak to udelam s barvama? vypocitam je ted hned, nebo ve scrape, nebo uplne jinde?
        poly = new google.maps.Polygon
            paths: ((new google.maps.LatLng(i[0], i[1]) for i in item) for item in shape)
            strokeColor: MAP_ACTIVE_POLY_COLOR
            strokeOpacity: 1
            strokeWeight: 1
            fillColor: MAP_ACTIVE_POLY_COLOR
            fillOpacity: 1
            zIndex: MAP_POLY_ZINDEX
            map: MAP

        # zaveseni udalosti nad polygonem
        google.maps.event.addListener poly, 'mouseover', () =>
            $('#statistics').parent().scrollTo("#region_#{ @model.get('slug') }", 200)
            @el.trigger('mouseover')
        google.maps.event.addListener poly, 'mouseout', () =>
            @el.trigger('mouseout')
        google.maps.event.addListener poly, 'click', () =>
            @el.trigger('click')
        # TODO: dblclick

        @model.set({poly: poly})
        poly

    # Aktualizuje polygony v mape podle dodanych parametru.
    updatePolys: (options={}) ->
        if 'map' of SEMAPHORE and 'initialized' of SEMAPHORE.map
            poly = @model.get('poly') or @createPolys()
            poly.setOptions(options)

    # TODO: tady nam to ale neprijemne bobtna....
    render: () ->
        changed = _.keys(@model.changedAttributes() or {})

        if ('shape' in changed and changed.length == 1) or ('poly' in changed and changed.length == 1)
            return @

        if 'hover' in changed
            @el.toggleClass('hover')
            if @el.hasClass('hover')
                @renderPolys('hover')
            else
                if @model.get('active')
                    @renderPolys('active')
                else
                    @renderPolys('normal')

        if 'active' in changed or 'color' in changed
            if 'active' in changed
                @el.toggleClass('active')
            if @el.hasClass('active')
                @renderPolys('active')
            else
                @renderPolys('normal')

        if changed.length > 1 or ('hover' not in changed and 'active' not in changed and 'color' not in changed and 'fragments' not in changed)
            context = @model.toJSON()
            _.extend(context,
                type: @collection.type.val()
                parameter: @collection.parameter.val()
            )
            content = _.template($('#region-item-template').html(), context)
            @el.html(content)

        return @

    # TODO:
    renderPolys: (state) ->
        color = @model.get('color')

        if state == 'hover'
            @model.trigger 'map:update_polys',
                fillColor: MAP_HOVER_POLY_COLOR
                strokeColor: MAP_HOVER_POLY_COLOR
                zIndex: MAP_POLY_ZINDEX
        else if state == 'active'
            @model.trigger 'map:update_polys',
                fillColor: color
                strokeColor: MAP_ACTIVE_POLY_COLOR
                zIndex: MAP_ACTIVE_POLY_ZINDEX
        else
            @model.trigger 'map:update_polys',
                fillColor: color
                strokeColor: color
                zIndex: MAP_POLY_ZINDEX

    # udalosti nad <tr>
    mouseover: () ->
        @model.set({hover: true})

    mouseout: () ->
        @model.set({hover: false})

    click: () ->
        fragments = @model.get('fragments')
        $h1 = $('h1')

        success = (resp, status, xhr) =>
            if not fragments
                @model.set({fragments: resp})

            $('#breadcrumb').html(resp.breadcrumb)
            $('h1').text(@model.get('title'))
            $('#primer').html(resp.primer_content)

            @model.trigger('fragments:change')

            Backbone.history.navigate("/#{ @model.get('slug') }/kampan/mf/")
            $h1.removeClass('loading')

        if not fragments
            $h1.addClass('loading')
            options =
                url: @el.find('a').attr('href')
                success: success
            Backbone.sync('read', @, options)
        else
            success(fragments)

        _.each(@collection.active(), (region) ->
            region.set({active: false})
        )
        @model.set({active: true})
        false

###
Tabulka kraju.
###
class RegionTableView extends Backbone.View

    initialize: () ->
        # reference na ovladaci selektitka ve strance
        @type      = $('#type')
        @parameter = $('#parameter')
        # systemove udalosti
        @collection.bind('redraw:done', @render, @)

    ###
    Projede tabulku s regiony a interpretuje hodnotu v druhem sloupci do podoby
    grafu (napozicuje obrazek na pozadi radku tabulky).

    Poznamka: tato metoda je povesena na udalost "redraw:done", kterou odpaluje
    kolekce RegionList na konci metody redraw.
    Puvodne jsem si myslel, ze tuhle funkcionalitu bude delat primo RegionRowView,
    ale nejde to. Nejdrive je totiz treba vykreslit vsechny radky tabulky
    (tj. RegionRowView.render) a teprve **potom** muzu kreslit grafy. Duvod je
    ten, ze dynamicky nalevany obsah sibuje s rozmery bunek a pro vykresleni
    grafu potrebuji znat jejich rozmery.
    ###
    render: () ->
        width = @el.width()
        td1_w = @el.find('td:first').width()
        td2_w = width - td1_w

        type = @type.val()
        parameter = @parameter.val()
        max = if parameter == 'conflict_perc' then 100 else EXTREMS[type][parameter].max

        @collection.each (region, idx) =>
            $tr = @$("tr:eq(#{ idx })")
            $td1 = $tr.find('td:first')
            $td2 = $tr.find(":not(:first):not(.hide)")

            # vypocet pozice grafu
            statistics_map = region.get('statistics_map')
            w = Math.round(statistics_map[type][parameter] / max * width)
            if w > td1_w
                x1 = 1000
                x2 = w - td1_w
            else
                x1 = w
                x2 = 0

            # uprava tabulky podle vypoctenych hodnot
            $td1.css('background-position', "#{ x1 }px 0")
            $td2.css('background-position', "#{ x2 }px 0")

            # nastaveni barev polygonu kraje
            color = get_color(type, (statistics_map[type][parameter] - EXTREMS[type][parameter].min) / EXTREMS[type][parameter].max)
            region.set({color: color})

        return @


###
Napoveda k mape.
###
class LegendView extends Backbone.View
    initialize: () ->
        # reference na ovladaci selektitka ve strance
        @type      = $('#type')
        @parameter = $('#parameter')
        # systemove udalosti
        @parameter.bind('change', _.bind(@render, @))
        @type.bind('change', _.bind(@render, @))

    render: () ->
        type = @type.val()
        parameter = @parameter.val()
        @el.empty()
        @el.append(LEGENDS[type][parameter])
        return @


###
Aplikace.
###
class AppView extends Backbone.View
    el: $('#app')

    initialize: () ->
        $('h1').addClass('loading')

        # vyzobneme informace z tabulky do kolekce modelu Region
        @options.regions.scrape()

        # nacteme tvary
        # TODO:
        @options.regions.fetch()

        # propojime prvky z kolekce s view (jednotlivymi radky tabulky)
        @options.regions.each (region) =>
            view = new RegionRowView
                model: region
                collection: @options.regions
                el: $("#region_#{ region.get('slug') }")
            region.trigger('change')

        # view nad celou tabulkou
        new RegionTableView
            el: $("#statistics")
            collection: @options.regions

        # view pro uvodni text
        new PrimerView
            el: $("#primer")
            collection: @options.regions

        # view pro legendu k mape
        new LegendView
            el: $("#legend")

        Backbone.history = new Backbone.History
        #Backbone.history.start(pushState: true, silent: true)
        Backbone.history.start({pushState: true})
