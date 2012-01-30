# min/max hodnoty sledovanych parametru
EXTREMS = {}

# URL adresy, na kterych je mozne ziskat dodatecne informace k datum vyzobnutym ze stranky
COLLECTION_URLS =
    region: '/kampan/mf/ajax/kraje/'
    district: '/kampan/mf/ajax/okresy/'

###
Kolekce vsech kraju v republice.
###
class RegionList extends Backbone.Collection
    model: Region
    url: COLLECTION_URLS[window.PAGE_TYPE]

    initialize: () ->
        @type = $('#type')
        @type.bind('change', _.bind(@redraw, @))
        @parameter = $('#parameter')
        @parameter.bind('change', _.bind(@redraw, @))

    # vyzobne z HTML tabulky data a udela z nich kolekci regionu
    # mimo to vytahne do globalniho slovniku EXTREMS min/max hodnoty
    scrape: () ->
        that = @
        $('#statistics tbody tr').each (idx, el) =>
            tr = $(el)
            tds = tr.find('td')

            active = tr.hasClass('active')
            slug = tr.attr('id').replace("#{ window.PAGE_TYPE }_", '')
            title = $.trim($(tds[0]).text())
            url = $(tds[0]).find('a').attr('href')
            statistics = _.map(_.last(tds, 6), (i) ->
                $i = $(i)
                cls = _.filter($i.attr('class').split(' '), (y) -> $.trim(y).length > 0)
                type = _.intersection(cls, _.keys(TYPES))[0]
                parameter = _.intersection(cls, _.keys(PARAMETERS))[0]

                if type not of EXTREMS
                    EXTREMS[type] = {}
                if parameter not of EXTREMS[type]
                    EXTREMS[type][parameter] = {min: 1000000000000, max: 0}

                num_value = that.getValue($i.text())
                if num_value > EXTREMS[type][parameter].max
                    EXTREMS[type][parameter].max = num_value
                if num_value < EXTREMS[type][parameter].min
                    EXTREMS[type][parameter].min = num_value

                return {
                    type: type
                    parameter: parameter
                    value: $.trim($i.text())
                    num_value: num_value
                }
            )

            statistics_map = {}
            for item in statistics
                if item.type not of statistics_map
                    statistics_map[item.type] = {}
                statistics_map[item.type][item.parameter] = item.num_value

            @add new Region
                title: title
                slug: slug
                statistics: statistics
                statistics_map: statistics_map
                url: url
                active: active

    # natahne tvary kraju ze serveru, a prida je k prvkum kolekce
    fetch: () ->
        # TODO: nejake osetreni erroru?
        options =
            url: @url
            success: (resp, status, xhr) =>
                # pridame k datum vyzobnutym ze stranky dalsi exras ze serveru
                @each (region) ->
                    data = {}
                    _.each resp['details'][region.get('slug')], (value, key) ->
                        data[key] = value
                    region.set(data)
                HazardEvents.trigger('map:extras_loaded', @)
        Backbone.sync('read', @, options)

    getValue: (str) ->
        parseFloat($.trim(str.replace(',', '.').replace('%', '')))

    redraw: () ->
        @each (region) ->
            region.trigger('change')
        @trigger('redraw:done')

    active: () ->
        @filter (region) -> region.get('active')
