# hodnoty a labely pro ovladaci selektitka
PARAMETERS =
    counts: 'celkový počet'
    conflict_counts: 'počet nezákonně povolených'
    conflict_perc: 'poměr nezákonně/zákonně povolených'

TYPES =
    hells: 'heren'
    machines: 'automatů'

# legenda k mape
LEGENDS =
    # popisky ke krajum
    region:
        hells:
            counts:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím větší počet heren se v kraji vyskytuje."""
            conflict_counts:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím se v nich vyskytuje větší počet <a href="#">nezákonně
                povolených heren"""
            conflict_perc:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím je v kraji více <a href="#">nezákonně povolených heren</a>,
                než těch, jejichž umístění neodporuje žádnému zákonu."""
        machines:
            counts:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím větší počet automatů se v kraji vyskytuje."""
            conflict_counts:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím se v nich vyskytuje větší počet <a href="#">nezákonně
                povolených automatů</a>."""
            conflict_perc:
                """V mapě jsou vykresleny kraje České republiky. Čím tmavší
                barva je použita, tím je v kraji více <a href="#">nezákonně povolených automatů</a>,
                než těch, jejichž umístění neodporuje žádnému zákonu."""
    # popisky k okresum
    district:
        hells:
            counts:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím větší počet heren se v okrese vyskytuje."""
            conflict_counts:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím se v nich vyskytuje větší počet <a href="#">nezákonně
                povolených heren</a>."""
            conflict_perc:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím je v okrese více <a href="#">nezákonně povolených heren</a>,
                než těch, jejichž umístění neodporuje žádnému zákonu."""
        machines:
            counts:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím větší počet automatů se v okrese vyskytuje."""
            conflict_counts:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím se v nich vyskytuje větší počet <a href="#">nezákonně
                povolených automatů</a>."""
            conflict_perc:
                """V mapě jsou vykresleny bývalé okresy České republiky. Čím tmavší
                barva je použita, tím je v okrese více <a href="#">nezákonně povolených automatů</a>,
                než těch, jejichž umístění neodporuje žádnému zákonu."""


# barvy a z-indexy polygonu v mape
MAP_POLY_ZINDEX = 10
MAP_ACTIVE_POLY_COLOR = '#333333'
MAP_ACTIVE_POLY_ZINDEX = 20
MAP_HOVER_POLY_COLOR = '#333333'

# obarveni mapy
MAP_STYLE = [
  {featureType:"water", stylers:[{visibility:"off"}]}
  {featureType:"transit", stylers:[{ visibility:"off"}]}
  {featureType:"landscape.natural", stylers:[{visibility:"off"}]}
  {featureType:"road", stylers:[{visibility:"off"}]}
  {featureType:"landscape.man_made", stylers:[{visibility:"off"}]}
  {featureType:"poi", stylers:[{visibility:"off"}]}
  {featureType:"administrative.province", stylers:[{visibility:"off"}]}
  {featureType:"administrative.locality", stylers:[{visibility:"off"}]}
  {featureType:"administrative", elementType:"labels", stylers:[{visibility:"off"}]}
  {featureType:"administrative.country", elementType:"geometry", stylers:[{visibility:"on"}, {lightness:58}]}
]

# vylepseni Google Maps API -> getBounds nad polygonem
setPolygonBoundsFn: () ->
    if not google.maps.Polygon.prototype.getBounds
        google.maps.Polygon.prototype.getBounds = (latLng) ->
            bounds = new google.maps.LatLngBounds()
            paths = this.getPaths()
            for path in paths.getArray()
                for item in path.getArray()
                    bounds.extend(item)
            bounds

# globalni promenna s mapou
MAP = undefined

# detekce typu stranky
# TODO: tohle je kokotina -- typ stranky poznavat muzu, ale ty dalsi veci ne!
# (vlivem ajaxu se to meni pod rukama)
path = _.filter(window.location.pathname.split('/'), (i) -> i.length > 0)
if path.length == 3             # /zlinsky/kampan/mf/
    window.PAGE_TYPE = 'region'
    window.PAGE_REGION = path[0]
else if path.length == 4        # /zlinsky/vsetin/kampan/mf/
    window.PAGE_TYPE = 'district'
    window.PAGE_REGION = path[0]
    window.PAGE_DISTRICT = path[1]
else if path.length == 5        # /zlinsky/vsetin/valasske-mezirici/kampan/mf/
    window.PAGE_TYPE = 'town'
    window.PAGE_REGION = path[0]
    window.PAGE_DISTRICT = path[1]
    window.PAGE_TOWN = path[2]
