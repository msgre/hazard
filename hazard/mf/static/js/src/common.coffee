DEBUG = false

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
    # popisky k obcim
    town:
        hells:
            counts:
                """V mapě jsou vykresleny obce vybraného okresu České
                republiky.  Čím větší počet heren se v obci vyskytuje, tím
                větší kolečko je vykresleno."""
            conflict_counts:
                """V mapě jsou vykresleny obce vybraného okresu České republiky.
                Čím více je v obci <a href="#">nezákonně povolených heren</a>, tím větší kolečko
                je vykresleno."""
            conflict_perc:
                """V mapě jsou vykresleny obce vybraného okresu České republiky.
                Čím více je v obci nezákonně povolených heren, vůči těm, jejichž
                umístění neodporuje žádnému zákonu, tím je kolečko větší."""
        machines:
            counts:
                """V mapě jsou vykresleny obce vybraného okresu České
                republiky.  Čím větší počet automatů se v obci vyskytuje, tím
                větší kolečko je vykresleno."""
            conflict_counts:
                """V mapě jsou vykresleny obce vybraného okresu České republiky.
                Čím více je v obci <a href="#">nezákonně povolených automatů</a>, tím větší kolečko
                je vykresleno."""
            conflict_perc:
                """V mapě jsou vykresleny obce vybraného okresu České republiky.
                Čím více je v obci nezákonně povolených automatů, vůči těm, jejichž
                umístění neodporuje žádnému zákonu, tím je kolečko větší."""

# navod, jak mapu ovladat
CONTROL_LEGEND = """
    Ovládání mapy: najeďte myší nad region či obec která vás zajímá a kliknutím
    aktualizujete informace na stránce. Pokud v případě krajů a okresů nad oblastí
    provedete dvojklik, aplikace vám zobrazí územně nižší celky (např. pokud si
    prohlížíte nějaký kraj, dvojklikem se dostanete na zobrazení okresů)."""


# barvy a z-indexy polygonu v mape
MAP_POLY_ZINDEX = 10
MAP_ACTIVE_POLY_COLOR = '#f4f3f0'
MAP_ACTIVE_POLY_ZINDEX = 30
MAP_HOVER_POLY_COLOR = '#333333'
MAP_HOVER_POLY_ZINDEX = 25
MAP_BORDERS_ZINDEX = 20
MAP_BORDERS_COLOR = '#FA9700'

MAP_CIRCLE_ZINDEX = 40
MAP_ACTIVE_CIRCLE_ZINDEX = 45
MAP_HOVER_CIRCLE_ZINDEX = 50
MAP_CIRCLE_COLOR = '#bbbbbb'
MAP_ACTIVE_CIRCLE_COLOR = '#fac90d'
MAP_ACTIVE_CIRCLE_BORDER_COLOR = '#333333'
MAP_HOVER_CIRCLE_COLOR = '#333333'

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
setPolygonBoundsFn = () ->
    if not google.maps.Polygon.prototype.getBounds
        google.maps.Polygon.prototype.getBounds = (latLng) ->
            bounds = new google.maps.LatLngBounds()
            paths = this.getPaths()
            for path in paths.getArray()
                for item in path.getArray()
                    bounds.extend(item)
            bounds

# min/max rozmer kolecka, ktere reprezentuje obci
# (hodnota je v metrech)
POINT_MIN_RADIUS = 1200
POINT_MAX_RADIUS = 3600

# globalni promenna s mapou
MAP = undefined

# detekce typu stranky
path = _.filter(window.location.pathname.split('/'), (i) -> i.length > 0)
if path.length == 3             # /zlinsky/kampane/mf/
    PAGE_TYPE = 'region'
else if path.length == 4        # /zlinsky/vsetin/kampane/mf/
    PAGE_TYPE = 'district'
else if path.length == 5        # /zlinsky/vsetin/valasske-mezirici/kampane/mf/
    PAGE_TYPE = 'town'

# vyzobne z aktualniho URL slug kraje/okresu/mesta
parseUrl = () ->
    out = {district: undefined, town: undefined}
    path = _.filter(window.location.pathname.split('/'), (i) -> i.length > 0)
    if PAGE_TYPE == 'region'
        out.region = path[0]
    else if PAGE_TYPE == 'district'
        out.region = path[0]
        out.district = path[1]
    else if PAGE_TYPE == 'town'
        out.region = path[0]
        out.district = path[1]
        out.town = path[2]
    out

# pomocna logovaci fce (pokud je DEBUG == false, nic se neloguje)
log = (message) ->
    if DEBUG
        console.log message
