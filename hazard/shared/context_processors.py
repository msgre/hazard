# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from hazard.geo.models import Entry

def common(request):
    """
    Vlozi do kontextu vsech sablon slovnik se zaznamy Entry, ktere se
    pak reprezentuji jako oranzove ikony v mape na pozadi. Pouziva se to
    na vsech strankach s vyjimkou detailu konkretni obce.
    """
    entries = {}
    for entry in Entry.objects.filter(public=True):
        entries[entry.id] = {
            'lat': entry.dpoint.coords[1],
            'lon': entry.dpoint.coords[0],
            'perc': int(round(entry.dperc)),
            'url': entry.get_absolute_url()
        }
    return {'perc_entries': entries}
