MAP = undefined


$(document).ready () ->
    map_options =
        zoom: 7
        center: new google.maps.LatLng(49.38512, 14.61765) # defaultne zamerime na CR
        mapTypeId: google.maps.MapTypeId.ROADMAP
    MAP = new google.maps.Map(document.getElementById("map"), map_options)

    _.each window.shapes, (shape) ->
        if not shape
            return true
        polys = (new google.maps.LatLng(i[0], i[1]) for i in shape)
        sh = new google.maps.Polygon
            paths: polys
            strokeColor: "#FF0000"
            strokeOpacity: 0.8
            strokeWeight: 2
            fillColor: "#FF0000"
            fillOpacity: 0.35

        sh.setMap(MAP)
