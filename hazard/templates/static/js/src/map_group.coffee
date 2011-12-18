###
Custom ikonka, ktera ve sve stredu zobrazuje procenta.

Pozor! Vzhled ikony je treba definovat na urovni CSS, napr.:

    .group {
        position:absolute;
        background:url(http://media.mapyhazardu.cz/img/percent.png);
        width:40px;
        height:40px;
        font-size:11px;
        font-weight:bold;
        text-align:center;
    }
    .group p {
        padding-top:12px;
    }

Nad ikonou se vykresluje pruhledny DIV, ktery zachytava klikani mysi. Musi
byt stejne velky, jako ikona. Napr.:

    .slide {
        position:absolute;
        width:40px;
        height:40px;
    }
    .slide:hover {
        cursor:pointer;
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
    @icon_ = null      # HTML reprezentace ikony
    @slide_ = null     # pruhledny DIV nad ikonou, ktery zachytava klikani
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

    # ikona
    icon = document.createElement('DIV')
    icon.className = "group"
    icon.style.display = "none"
    icon.title = @data_['t']
    count = document.createElement('P')
    count.innerHTML = @data_['c']
    icon.appendChild(count)

    # pruhledna klikaci vrstva nad ikonou
    slide = document.createElement('DIV')
    slide.className = "slide"
    slide.style.display = "none"
    $(slide).tipsy(
        title: () => @data_['t']
    )

    # kliknuti na ikonu nas dovede na detailni stranku
    google.maps.event.addDomListener slide, 'click', (ev) =>
        window.location = @url

    @icon_ = icon
    @slide_ = slide

    # sup do mapy
    panes = @getPanes()
    panes.overlayImage.appendChild(icon)
    panes.overlayMouseTarget.appendChild(slide)


###
Vykresli grupu v mape, presne na zadanych souradnicich. Pokud je interni atribut
@visible_ == false, grupa se nevykresli.
###

Group.prototype.draw = () ->
    if @icon_ and @visible_
        # ukazeme element
        @icon_.style.display = "block"
        @slide_.style.display = "block"

        # nastavime spravnou pozici
        overlayProjection = @getProjection()
        pixel_pos = overlayProjection.fromLatLngToDivPixel(@pos_)

        left = pixel_pos.x - @center_[0] + 'px'
        top = pixel_pos.y - @center_[1] + 'px'
        @icon_.style.left = left
        @icon_.style.top = top
        @slide_.style.left = left
        @slide_.style.top = top

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
    if @icon_
        @icon_.style.display = "none"
        @slide_.style.display = "none"
        @visible_ = false
    return


###
Metoda volana po Group.set_map(null). Postara se o odstraneni HTML elementu z
mapy a resetu vnitrnich hodnot.
###

Group.prototype.onRemove = () ->
    # odstraneni HTML elementu
    @icon_.parentNode.removeChild(@icon_)
    @icon_ = null
    @slide_.parentNode.removeChild(@slide_)
    @slide_ = null

    # reset atributu
    @data_ = null
    @visible_ = false
    @pos_ = null


###
Vrati souradnice stredu grupy.
###

Group.prototype.getPosition = () ->
    @pos_
