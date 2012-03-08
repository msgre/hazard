# min/max hodnoty sledovanych parametru
EXTREMS = {}

# URL adresy, na kterych je mozne ziskat dodatecne informace k datum vyzobnutym ze stranky
GEO_OBJECTS_URLS =
    region: '/kampane/mf/ajax/kraje/'
    district: '/kampane/mf/ajax/okresy/'
    town: '/kampane/mf/ajax/obce/'


###
Kolekce geografickych objektu, ktere se vyzobly z HTML stranky.
###
class GeoObjectList extends Backbone.Collection
    model: GeoObject
    url: GEO_OBJECTS_URLS[PAGE_TYPE]

    initialize: () ->
        # zavesime se na ovladaci selektitk (zmena v nich vyvola prekresleni dat)
        @type = $('#type')
        @type.bind('change', _.bind(@redraw, @))
        @parameter = $('#parameter')
        @parameter.bind('change', _.bind(@redraw, @))

    ###
    Natahne data do kolekce.

    Primarnim zdrojem je tabulka v HTML strance. To co v ni chybi se nasledne
    dososne ze serveru.
    ###
    fetch: () ->
        log('GeoObjectList.fetch:start')
        @scrapePage()
        @fetchExtras()
        log('GeoObjectList.fetch:done')

    ###
    Natahne extra data ze serveru a prilepi je ke stavajicim polozkam v kolekci.
    ###
    fetchExtras: () ->
        log('GeoObjectList.fetchExtras:ready to launch request')
        url = if PAGE_TYPE == 'town' then "#{ @url }#{ parseUrl().district }/" else @url

        # odpaleni ajax dotazu
        options =
            url: url
            success: (resp, status, xhr) =>
                # pridame k datum vyzobnutym ze stranky dalsi exras ze serveru
                log('GeoObjectList.fetchExtras:extras data loaded')
                @each (gobj) ->
                    data = {}
                    _.each resp.details[gobj.get('slug')], (value, key) ->
                        data[key] = value
                    gobj.set(data)
                log("GeoObjectList.fetchExtras:collection data succesfully updated (#{ @length })")
                HazardEvents.trigger('GeoObjectList:extras_loaded', @)
            error: (model, resp, options) ->
                log('GeoObjectList.fetchExtras:extras data loading error')
        Backbone.sync('read', @, options)

    ###
    Vyzobne z HTML tabulky data a udela z nich kolekci geografickych objektu.
    ###
    scrapePage: () ->
        log('GeoObjectList.scrapePage:ready to scrape data from HTML to collection')
        that = @

        # projedem tabulku radek po radku
        $('#statistics tbody tr').each (idx, el) =>
            tr = $(el)
            tds = tr.find('td')

            # vyzobnem z radku zakladni informace
            active = tr.hasClass('active')
            slug = tr.attr('id').replace("#{ PAGE_TYPE }_", '')
            title = $.trim($(tds[0]).text())
            url = $(tds[0]).find('a').attr('href')

            # vyzobnem staticticke udaje
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
                if num_value != undefined
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

            # numericke udaje ukladame ve 2 formach
            # * pod klicem `statistics` je seznam objektu, ktere odpovidaji
            #   poradi hodnot v tabulce ve strance. S pomoci teto struktury se
            #   generuje vysledna podoba radku v tabulce.
            # * pod klicem `statistics_map` je ulozen dvojity slovnik
            #   s numerickymi udaji, ktere se pouzivaji pri kresleni objektu
            #   v mape (podle nich se vypocitava barva)
            statistics_map = {}
            for item in statistics
                if item.type not of statistics_map
                    statistics_map[item.type] = {}
                statistics_map[item.type][item.parameter] = item.num_value

            # ulozime data do kolekce
            @add new GeoObject
                title: title
                slug: slug
                statistics: statistics
                statistics_map: statistics_map
                url: url
                active: active
                type: PAGE_TYPE

        log('GeoObjectList.scrapePage:found #{ @length } records on page; scraping is done')

    # vrati numerickou reprezentaci zadaneho retezce, nebo undefined
    getValue: (str) ->
        text = $.trim(str.replace(',', '.').replace('%', ''))
        if text.length then parseFloat(text) else undefined

    # vyvola kompletni prekresleni vsech dat z kolekce
    redraw: () ->
        log('GeoObjectList.redraw:start')
        @each (gobj) ->
            gobj.trigger('change')
        log('GeoObjectList.redraw:done')
        @trigger('GeoObjectList:redraw_done')

    # vrati pouze aktivni polozky z kolekce (napr. aktualne vybrany kraj)
    active: () ->
        @filter (gobj) -> gobj.get('active')


###
Kolekce regionu. Pouziva se k vykresleni obrysu kraju na strankach okresu
a obci. Takova tresnicka, nic zasadniho...
###
class RegionList extends Backbone.Collection
    model: GeoObject
    url: GEO_OBJECTS_URLS.region

    fetch: () ->
        log('RegionList.fetch:start')
        current_region = parseUrl().region

        # odpaleni ajax dotazu
        options =
            url: @url
            success: (resp, status, xhr) =>
                log('RegionList.fetch:data loaded')
                _.each resp.details, (obj, slug) =>
                    _.extend obj,
                        slug: slug
                        active: slug == current_region
                    @add(obj)
                log("RegionList.fetchExtras:collection data succesfully updated (#{ @length })")
                HazardEvents.trigger('RegionList:regions_loaded', @)
            error: (model, resp, options) ->
                log('RegionList.fetch:data loading error')
        Backbone.sync('read', @, options)
        log('RegionList.fetch:done')


###
Kolekce okresu. Pouziva se k vykresleni tvaru (a barev) okresu na strankach
s obcemi.
###
class DistrictList extends Backbone.Collection
    model: GeoObject
    url: "#{ GEO_OBJECTS_URLS.district }?detailni"
    # NOTE: prilepenim parametru ?detailni ziskame podrobnejsi vypis o okresech,
    # vcetne numerickych dat potrebnych k vykresleni barev

    fetch: () ->
        log('DistrictList.fetch:start')
        @extrems = {}
        current_district_slug = parseUrl().district

        # odpaleni ajax dotazu
        options =
            url: @url
            success: (resp, status, xhr) =>
                log('DistrictList.fetch:data loaded')
                _.each resp.details, (obj, slug) =>
                    stat_flag = resp.statistics and slug of resp.statistics
                    _.extend obj,
                        slug: slug
                        statistics_map: if stat_flag then resp.statistics[slug] else {}
                        active: slug == current_district_slug
                    @add(obj)
                    # uchovani hodnot pro vypocet extremu
                    for t in ['hells', 'machines']
                        if t not of @extrems
                            @extrems[t] = {}
                        for p in ['conflict_perc', 'conflict_counts', 'counts']
                            if p not of @extrems[t]
                                @extrems[t][p] = []
                            if stat_flag and t of resp.statistics[slug] and p of resp.statistics[slug][t]
                                @extrems[t][p].push(resp.statistics[slug][t][p])

                # nalezeni min/max
                for t in ['hells', 'machines']
                    for p in ['conflict_perc', 'conflict_counts', 'counts']
                        @extrems[t][p] =
                            min: _.min(@extrems[t][p])
                            max: _.max(@extrems[t][p])

                log("DistrictList.fetchExtras:collection data succesfully updated (#{ @length })")
                HazardEvents.trigger('DistrictList:districts_loaded', @)

            error: (model, resp, options) ->
                log('DistrictList.fetch:data loading error')

        Backbone.sync('read', @, options)
        log('DistrictList.fetch:done')
