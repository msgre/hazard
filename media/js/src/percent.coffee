###
Vykresleni zlutych kolecek s procenty protizakonnych heren na mapu CR.
Toto pozadi je defaultni pro vetsinu stranek s vyjimkou detailu konkretni
obce.
###

draw_entries = () ->
    for id, data of window.perc_entries
        _data =
            'a': data.lat
            'o': data.lon
            'c': data.perc
            't': data.title
            'u': data.url
        group = new Group(_data, window.map)
        group.show()

$(document).ready () ->
    setup()
    init_map()
    init_fancybox()
    draw_entries()
