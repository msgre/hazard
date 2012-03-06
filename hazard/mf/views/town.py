# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import itertools

from django.contrib.gis.geos import Polygon
from django.core.cache import cache

from hazard.gobjects.models import Hell
from hazard.territories.models import Region, District
from hazard.territories.views import TownDetailView
from hazard.mf.models import MfPlaceConflict, MfPlace, MfAddressSurround
from hazard.shared.ajax import JSONView
from hazard.campaigns.models import Campaign


CACHE_TIMEOUT = 10 * 60 # 10 minut


class MfTownDetailView(JSONView, TownDetailView):
    """
    Zakladni prehled o obci.
    """
    base_template = 'mf/base.html'
    template_name = 'mf/town.html'

    def get_context_data(self, **kwargs):
        out = super(MfTownDetailView, self).get_context_data(**kwargs)
        statistics = MfPlaceConflict.statistics(out['district'], group_by='town')
        out.update({
            'base_template': self.base_template,
            'regions': dict([(i.id, i) for i in Region.objects.select_related().all()]),
            'districts': dict([(i.id, i) for i in District.objects.select_related().all()]),
            'statistics': statistics,
            'campaign_slug': self.kwargs['campaign'],
            'campaign': Campaign.objects.get(slug=self.kwargs['campaign'])
        })
        return out


class MfTownMapView(MfTownDetailView):
    """
    Podrobna mapa se situaci herev v obci.
    """
    base_template = 'mf/base.html'
    template_name = 'mf/town_map.html'
    json_prefix = 'json_town_'

    def get_context_data(self, **kwargs):
        """
        V pripade AJAXoveho dotazu vratime JSON strukturu s podrobnymi daty
        o budovach a hernach v obci.
        """
        out = super(MfTownMapView, self).get_context_data(**kwargs)
        if self.ajax:
            key = 'MfTownMapView:ajax:get_context_data:%s' % self.request.path
            data = cache.get(key)
            if not data:
                # vsechny adresy v obci
                addresses = out['object'].address_set.all()
                addresses = dict([(i.id, {'title': i.title, \
                                           'geo_type': i.get_geometry_type(), \
                                           'geo': list(i.get_geometry().coords)}) \
                                   for i in addresses])

                # adresy mist
                places = MfPlace.objects.visible().filter(town=self.object)
                place_address_ids = list(set(places.values_list('address', flat=True)))

                # adresy heren
                hells = Hell.objects.visible().filter(town=self.object)
                hell_address_ids = list(set(hells.values_list('address', flat=True)))

                # okoli mist
                surrounds = MfAddressSurround.objects.filter(address__id__in=place_address_ids, distance=100)
                place_surrounds = dict([(i.address_id, list(i.poly.coords)) for i in surrounds])

                # konflikty
                # NOTE: takovato podminka by mela stacit, myslim ze neni treba ji
                # omezovat jeste z druhe strany, tj. z MfPlace
                conflicts = MfPlaceConflict.objects.filter(hell__id__in=hells.values_list('id', flat=True))
                conflicts = dict([(k, list(set([y[1] for y in g]))) \
                                   for k, g in itertools.groupby(conflicts.values_list('hell__address', 'place__address'), lambda a: a[0])])

                # sloucene okoli budov
                hell_surrounds = {}
                for address_id in conflicts:
                    if len(conflicts[address_id]) < 2:
                        continue
                    else:
                        merge = None
                        for surround_address_id in conflicts[address_id]:
                            if surround_address_id in place_surrounds:
                                coords = place_surrounds[surround_address_id]
                                poly = Polygon(*coords)
                                if not merge:
                                    merge = poly
                                else:
                                    merge = merge.union(poly)
                        hell_surrounds[address_id] = [list(list(y) for y in i) for i in merge.coords]

                # sup s daty do sablony
                data = {
                    # vsechny pouzite adresy v obci (at uz hernami, nebo budovami)
                    'addresses': addresses,
                    # IDcka mist/heren
                    'place_addresses': place_address_ids,
                    'hell_addresses': hell_address_ids,
                    # okoli budov
                    'place_surrounds': place_surrounds,
                    # sloucene okoli budov
                    'hell_surrounds': hell_surrounds,
                    # detaily k mistum/hernam
                    'places': dict([(k, [y[1] for y in g]) \
                                    for k, g in itertools.groupby(places.values_list('address_id', 'title'), lambda a: a[0])]),
                    'hells': dict([(k, [y[1] for y in g]) \
                                    for k, g in itertools.groupby(hells.values_list('address_id', 'title'), lambda a: a[0])]),
                    # konflikty mezi adresami
                    'conflicts': conflicts
                }
                cache.set(key, data)

            out.update(data)

        return out


class MfTownComments(MfTownDetailView):
    """
    Diskuze k dane obci.
    """
    template_name = 'mf/town_comments.html'
