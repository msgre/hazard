
PARAMETERS =
    counts: 'celkový počet'
    conflict_counts: 'počet nezákonně povolených'
    conflict_perc: 'poměr nezákonně/zákonně povolených'

TYPES =
    hells: 'heren'
    machines: 'automatů'


LEGENDS =
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

# TODO:
MAP_SEMAPHORE = []

# TODO: barvy
MAP_POLY_ZINDEX = 10
MAP_ACTIVE_POLY_COLOR = '#333333'
MAP_ACTIVE_POLY_ZINDEX = 20
MAP_HOVER_POLY_COLOR = '#333333'
