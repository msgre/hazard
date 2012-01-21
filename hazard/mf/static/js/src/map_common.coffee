# nastaveni schovavace (pluginu starajiciho se o zkraceni seznamu okresu/obci
# pod uvodnim textem)
SCHOVAVACZ_OPTS =
    limit: 4
    epsilon: 1
    show_txt: ' <i>a další…(%count%)</i>'
    hide_txt: ' <i>zkrátit seznam…</i>'
    items_selector: 'span'


# globalni promenna, ktera udrzuje informaci o tom, jestli si na strance
# prohlizime udaje o hernach nebo automatech (voli se selektitkem nad mapou)
VIEW = 'hells'

# mapa
MAP = undefined

# nastylovani mapy
MAP_STYLE = [
  {featureType:"water", stylers:[{visibility:"off"}]},
  {featureType:"transit", stylers:[{ visibility:"off"}]},
  {featureType:"landscape.natural", stylers:[{visibility:"off"}]},
  {featureType:"road", stylers:[{visibility:"off"}]},
  {featureType:"landscape.man_made", stylers:[{visibility:"off"}]},
  {featureType:"poi", stylers:[{visibility:"off"}]},
  {featureType:"administrative.province", stylers:[{visibility:"off"}]},
  {featureType:"administrative.locality", stylers:[{visibility:"off"}]},
  {featureType:"administrative", elementType:"labels", stylers:[{visibility:"off"}]},
  {featureType:"administrative.country", elementType:"geometry", stylers:[{visibility:"on"}, {lightness:58}]}
]

# globalni objekt se vsemi polygony vykreslenymi do mapy
POLYS = {}

# aktualni barvy vykreslenych polygonu
POLYS_COLORS = {}


###
Interpretuje hodnotu v tabulce jako barevny prouzek na pozadi radku tabulky.
###
number_to_graph = ($table, values, percents, cls) ->
    # maximum ve sloupecku s daty
    if percents
        max = 100.0
    else
        max = _.max(values) * 1.2

    # sirky bunek
    width = $table.width()
    td1_w = $table.find('td:first').width()
    td2_w = width - td1_w

    # kazdy radek tabulky podbarvime
    $table.find('tr').each (idx, el) ->
        $tr = $(@)
        $td1 = $tr.find('td:first')
        $td2 = $tr.find(".#{ cls }")
        w = Math.round(values[idx] / max * width)
        if w > td1_w
            x1 = 1000
            x2 = w - td1_w
        else
            x1 = w
            x2 = 0

        $td1.css('background-position', "#{ x1 }px 0")
        $td2.css('background-position', "#{ x2 }px 0")


###
Funkce pro vypocet interpolovanych barev mezi dvema zadanymi body.
###

hex = (v) ->
    out = v.toString(16)
    if out.length == 1
        out = '0' + out
    out

convert_to_hex = (rgb) ->
    '#' + hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2])

trim = (s) ->
    return if s.charAt(0) == '#' then s.substring(1, 7) else s

convert_to_rgb = (hex) ->
    color = [
        parseInt(trim(hex).substring(0, 2), 16)
        parseInt(trim(hex).substring(2, 4), 16)
        parseInt(trim(hex).substring(4, 6), 16)
    ]

interpolate_color = (start_color, end_color, value) ->
    start = convert_to_rgb(start_color)
    end = convert_to_rgb(end_color)
    c = [
        Math.round((end[0] - start[0]) * value + start[0])
        Math.round((end[1] - start[1]) * value + start[1])
        Math.round((end[2] - start[2]) * value + start[2])
    ]
    convert_to_hex(c)

get_color = (type, value) ->
    if type == 'hells'
        color = interpolate_color('#FFD700', '#EE0000', value)
    else
        color = interpolate_color('#00FFFF', '#0028FF', value)
    return color

map_legend = () ->
    pos = $('#map').position()
    $('#map-legend').css({
        left: "#{ pos.left + 10 }px";
        top: "#{ pos.top + 60 }px";
    })

update_map_legend = (extrems) ->
    $('#map-legend').attr('class', '').addClass($('#type-switcher').val())
    $('#map-legend .min').text(Math.round(extrems.min))
    $('#map-legend .max').text(Math.round(extrems.max))

select_legend_handler = () ->
    opened = false
    $('#select-handler').click () ->
        selector = "#select-legend .#{ $("#type-switcher").val() } .#{ $("#table-switcher").val() }"
        opened = not opened
        $(selector).toggleClass('opened', opened).slideToggle('fast')
        false

select_legend_handler2 = () ->
    neco = $('#select-legend .opened')
    if neco.length
        neco.removeClass('opened').hide()
        selector = "#select-legend .#{ $("#type-switcher").val() } .#{ $("#table-switcher").val() }"
        $(selector).addClass('opened').show()
