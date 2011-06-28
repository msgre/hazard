# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.core.cache import cache
from hazard.geo.models import Entry


TIMEOUT = 60 * 5 # 5 minut

def common(request):
    # obce, jejich souradnice a pocet heren v nich
    # (slouzi pro zobrazeni oranzovych kolecek na mape)
    key = 'perc_entries'
    if key in cache:
        entries = cache.get(key)
    else:
        entries = {}
        for entry in Entry.objects.filter(public=True):
            entries[entry.id] = {
                'lat': entry.dpoint.coords[1],
                'lon': entry.dpoint.coords[0],
                #'perc': '%i%%' % int(round(entry.dperc)),
                'perc': entry.dhell_count,
                'title': entry.title,
                'url': entry.get_absolute_url()
            }
        cache.set(key, entries, TIMEOUT)

    # celkovy pocet heren
    key = 'total_hell_count'
    if key in cache:
        total_hell_count = cache.get(key)
    else:
        total_hell_count = sum(Entry.objects.filter(public=True).values_list('dhell_count', flat=True))
        cache.set(key, total_hell_count, TIMEOUT)

    return {
        'perc_entries': entries,
        'total_hell_count': total_hell_count
    }
