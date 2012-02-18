# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re

from django.views.generic import View
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict
from django.core.cache import cache

from hazard.territories.models import Address
from hazard.gobjects.models import Hell, MachineCount

COORD_RE = re.compile(r'^-?\d+(\.\d+)?$')


class NearestHellsView(View):
    """
    Jednoduche view, ktere vraci seznam heren v nejblizsim okoli zadane
    geograficke pozice.
    """
    RADIUS = 500 # okoli kolem zadane pozice, ve kterem se herny hledaji (v metrech)
    LIMIT = 20   # zajima nas pouze N nejblizsich adres
    TIMEOUT = 5 * 60 # doba, po kterou budeme kesovat vysledek pro zadanou pozici (v minutach)

    def get_position(self):
        """
        Vyparsuje z GET URL parametru pozici lng/lat. Pokud ji nenajde, nebo
        je nejaka vadna, vrati None.
        """
        lat = self.request.GET.get('lat', None)
        lng = self.request.GET.get('lng', None)
        if not lat or not lng:
            return None
        if not COORD_RE.match(lat) or not COORD_RE.match(lng):
            return None
        return [float(lng), float(lat)]

    def get_addresses(self, position):
        """
        Vrati slovnik s adresami v nejblizsim okoli (okruh self.RADIUS) zadana
        pozice. Vraci pouze prvnich self.LIMIT vysledku.
        """
        point = Point(*position, srid=4326)
        address_qs = Address.objects.select_related()\
                                    .filter(point__distance_lte=(point, D(m=self.RADIUS)))\
                                    .distance(point, field_name='point')\
                                    .order_by('distance')[:self.LIMIT]
        addresses = [(i.id, {'street': i.title,
                             'town': i.town.title,
                             'distance': int(i.distance.m),
                             'position': i.point.coords}) for i in address_qs]
        return SortedDict(addresses)

    def get_hells(self, addresses):
        """
        Vrati slovnik s hernama, ktere lezi na zadanych adresach.
        """
        hell_qs = Hell.objects.filter(address__id__in=addresses.keys())
        hells = [(i.id, dict(addresses[i.address_id].items() + \
                             [('title', i.title), ('id', i.id), ('count', 0)])) \
                 for i in hell_qs]
        return SortedDict(hells)

    def update_machine_counts(self, hells):
        """
        Aktualizuje slovnik heren hells o pocty automatu v hernach.
        """
        machine_qs = MachineCount.objects.filter(hell__id__in=hells.keys()).values('hell', 'count')
        for i in machine_qs:
            hells[i['hell']]['count'] += i['count']

    def get(self, request, *args, **kwargs):
        """
        Pekarna.
        """
        position = self.get_position()
        if position is None:
            return HttpResponseBadRequest()

        key = 'api/hells/nearest/%s' % '-'.join([str(i) for i in position])
        print key
        if key in cache:
            return HttpResponse(cache.get(key), content_type='application/json')

        addresses = self.get_addresses(position)
        hells = self.get_hells(addresses)
        self.update_machine_counts(hells)
        data = json.dumps(hells.values())
        cache.set(key, data, self.TIMEOUT)

        return HttpResponse(data, content_type='application/json')
