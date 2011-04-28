###
TODO:
###

window.map = undefined

# globalni promenne
MAP_STYLE = undefined   # definice stylu pro nasi custom mapu


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
TODO:
###

init_map = () ->
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
