# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.core.cache import cache
from hazard.geo.models import Entry


TIMEOUT = 60 * 5 # 5 minut

def common(request):
    """
    Vlozi do kontextu vsech sablon slovnik se zaznamy Entry, ktere se
    pak reprezentuji jako oranzove ikony v mape na pozadi. Pouziva se to
    na vsech strankach s vyjimkou detailu konkretni obce.
    """
    key = 'perc_entries'
    if key in cache:
        entries = cache.get(key)
    else:
        entries = {}
        for entry in Entry.objects.filter(public=True):
            entries[entry.id] = {
                'lat': entry.dpoint.coords[1],
                'lon': entry.dpoint.coords[0],
                'perc': '%i%%' % int(round(entry.dperc)),
                'title': entry.title,
                'url': entry.get_absolute_url()
            }
        cache.set(key, entries, TIMEOUT)
    return {'perc_entries': entries}
