###
Obecny kod, ktery je vyuzivan jak v detailech obci, tak i na ostatnich strankach.
###

window.map = undefined  # googli mapa
MAP_STYLE = undefined   # definice stylu pro nasi custom mapu
MEDIA_URL = 'http://media.parkujujakcyp.cz/hazard/'


###
Nakonfigurovani stylu mapy.
###

setup = () ->
    # nastylovani mapy
    MAP_STYLE = [
        {featureType:"landscape", elementType:"all", stylers:[{saturation:-60}]}
        {featureType:"road", elementType:"all", stylers:[{saturation:-100}]}
        {featureType:"water", elementType:"all", stylers:[{saturation:-60}]}
        {featureType:"transit", elementType:"all", stylers:[{saturation:-100}]}
        {featureType:"poi", elementType:"all", stylers:[{saturation:-100}]}
    ]


###
Serepeticky kvuli fancyboxu -- kdyz jsem ho volal na submit udalost, nestihl
si nacist obrazky z CSSka a progress bar uvnitr taky chybel. Proto to delam
tak ze submit nejprve nahodi fancybox, a teprve po sekunde dojde ke skutecnemu
odeslani formulare.
###

upload_fancybox_opened = false

open_upload_fancybox = () ->
    upload_fancybox_opened = true
    $.fancybox({
        title: 'Uno momento'
        content: '<p><b>Vaše mapy se právě nahrávají na server a chvíli to potrvá</b></p><p><img src="' + MEDIA_URL + 'img/ajax-loader.gif"></p><p><em>Pro hrubou orientaci: Brno s cca 300 hernami trvá téměř 3 minuty.</em></p>'
        modal: true
    })

submit = () ->
    $('form').submit()


###
Inicializace fancyboxu (vrstvy pro zobrazovani vetsich obrazku a modalnich
oken).
###

init_fancybox = () ->
    $("a.fb").fancybox()
    if $('#upload_maps').length
        img = $('<img>').attr('src', MEDIA_URL + 'img/ajax-loader.gif')
        $('form').submit () ->
            if not upload_fancybox_opened
                open_upload_fancybox()
                t = setTimeout(submit, 1000)
                return false
            else
                return true


###
Inicializace mapy.
###

init_map = () ->
    # nastaveni vysky mapy pres cele okno prohlizece
    $('body').height($(window).height() + 'px')

    if not window.map?
        map_options =
            backgroundColor: '#ffffff'
            mapTypeControlOptions: {mapTypeIds:['CB', google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.ROADMAP]},
            mapTypeId: 'CB'
            noClear: true
            mapTypeControl: true
            # streetViewControl: false
            panControl: false
            zoomControl: true
            zoomControlOptions:
                position: google.maps.ControlPosition.RIGHT_TOP

        window.map = new google.maps.Map(document.getElementById("body"), map_options)
        styledMapType = new google.maps.StyledMapType(MAP_STYLE, {name:'Černobílá'})
        window.map.mapTypes.set('CB', styledMapType)

    # defaultne zamerime na CR
    center = new google.maps.LatLng(49.38512, 14.61765)
    window.map.setCenter(center)
    window.map.setZoom(7)

    # zavirani boxu
    open = true
    speed = 120
    $('#hide a').click () ->
        $('#inner_box').slideToggle(speed)
        if open
            height = '120px'
            opacity = .8
        else
            height = '80%'
            opacity = 1
        $('#info_box').animate {height: height, opacity:opacity}, speed
        open = !open
        false
