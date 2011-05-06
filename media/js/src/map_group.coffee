###
Custom ikonka, ktera ve sve stredu zobrazuje procenta.

Pozor! Vzhled ikomny je treba definovat na urovni CSS, napr.:

    .group {
        position:absolute;
        background:url(http://media.parkujujakcyp.cz/hazard/img/percent.png);
        width:40px;
        height:40px;
        font-size:11px;
        font-weight:bold;
        text-align:center;
    }
    .group:hover {
        cursor:pointer;
    }
    .group p {
        padding-top:12px;
    }
###


###
Konstruktor. Priklad pouziti:

    marker = new Group(data, window.map)

`data` maji nasledujici strukturu:

    {
            'a': 49.124333,   # latitude
            'o': 16.46354,    # longitude
            'c': 10,          # cislo dovnitr ikony, 10%
            'u': '/d/vsetin/' # URL na stranku s detailem
    }
###

Group = (data, map) ->

    # inicializace
    @center_ = [20, 20]
    @data_ = data
    @div_ = null       # HTML reprezentace ikony
    @visible_ = false  # flag viditelnosti
    @pos_ = new google.maps.LatLng(data['a'], data['o'])
    @url = data['u']

    @setMap(map)
    return @


Group.prototype = new google.maps.OverlayView()


###
Vytvori HTML kod grupoznacky a vlozi ji fyzicky do mapy (zatim ale bez presne
pozice). Grupa zustava skryta (ma nastaveno CSS display=none), pro jeji
zobrazeni je nutne volat metodu show).
###

Group.prototype.onAdd = () ->

    # obal
    div = document.createElement('DIV')
    div.className = "group"
    div.style.display = "none"
    div.title = @data_['t']

    # box s obsahem (cislem s procenty)
    count = document.createElement('P')
    count.innerHTML = @data_['c']
    div.appendChild(count)

    # kliknuti na ikonu nas dovede na detailni stranku
    google.maps.event.addDomListener div, 'click', (ev) =>
        console.log 'klikanec'
        window.location = @url

    # prcnem grupu do mapy
    @div_ = div

    # overlayImage -> This pane contains the marker foreground images. (Pane 3).
    panes = @getPanes()
    panes.overlayMouseTarget.appendChild(div)


###
Vykresli grupu v mape, presne na zadanych souradnicich. Pokud je interni atribut
@visible_ == false, grupa se nevykresli.
###

Group.prototype.draw = () ->
    if @div_ and @visible_
        # ukazeme element
        @div_.style.display = "block"

        # nastavime spravnou pozici
        overlayProjection = @getProjection()
        pixel_pos = overlayProjection.fromLatLngToDivPixel(@pos_)

        @div_.style.left = pixel_pos.x - @center_[0] + 'px'
        @div_.style.top = pixel_pos.y - @center_[1] + 'px'

    return


###
Zobrazi grupu v mape.
###

Group.prototype.show = () ->
    @visible_ = true
    @draw()
    return


###
Skryje grupu v mape (fyzicky tam zustava, ale z oci mizi).
###

Group.prototype.hide = () ->
    if @div_
        @div_.style.display = "none"
        @visible_ = false
    return


###
Metoda volana po Group.set_map(null). Postara se o odstraneni HTML elementu z
mapy a resetu vnitrnich hodnot.
###

Group.prototype.onRemove = () ->
    # odstraneni HTML elementu
    @div_.parentNode.removeChild(@div_)
    @div_ = null

    # reset atributu
    @data_ = null
    @visible_ = false
    @pos_ = null


###
Vrati souradnice stredu grupy.
###

Group.prototype.getPosition = () ->
    @pos_
