# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import TemplateView
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django import http
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict

from hazard.territories.models import Address
from hazard.gobjects.models import Hell


class NearestHellsView(TemplateView):
    """
    Vrati JSON s hernami v okruhu RADIUS metru od zadane pozice (pres GET
    parametry ?lat=&lng).
    """
    allow_empty = True
    RADIUS = 500 # v metrech

    def get_hells(self):
        lat = self.request.GET.get('lat', None)
        lng = self.request.GET.get('lng', None)
        if not lat or not lng:
            return None
        point = Point(float(lng), float(lat), srid=4326)
        addresses = SortedDict((i[0], {'street': i[1], 'town': i[2], 'distance': int(i[3].m)}) for i in Address.objects.select_related().filter(point__distance_lte=(point, D(m=self.RADIUS))).distance(point, field_name='point').order_by('distance').values_list('id', 'title', 'town__title', 'distance'))
        return [dict(addresses[i.address_id].items() + [('title', i.title), ]) for i in Hell.objects.filter(address__id__in=addresses.keys())]

    def render_to_response(self, context, **response_kwargs):
        hells = self.get_hells()
        if hells is None:
            return http.HttpResponseBadRequest()
        return http.HttpResponse(json.dumps(hells), content_type='application/json')
