###
Vykresleni zlutych kolecek s procenty protizakonnych heren na mapu CR.
Toto pozadi je defaultni pro vetsinu stranek s vyjimkou detailu konkretni
obce.
###

draw_entries = () ->

    #window.entries = {1: {'lat': 49.21388, 'lon': 16.57467, 'perc': 10, 'url': '/d/valasske-mezirici/'}}

    for id, data of window.perc_entries
        _data =
            'a': data.lat
            'o': data.lon
            'c': data.perc
            'u': data.url
        group = new Group(_data, window.map)
        group.show()


$(document).ready () ->
    setup()
    init_map()
    draw_entries()
