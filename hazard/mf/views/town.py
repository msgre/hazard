# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.core.paginator import Paginator, InvalidPage

from hazard.gobjects.models import Hell, MachineCount
from hazard.territories.models import Region, District
from hazard.territories.views import TownDetailView
from hazard.mf.models import MfPlaceConflict, MfPlace
from hazard.shared.ajax import JSONView



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
            'campaign': self.kwargs['campaign']
        })
        return out


class MfTownMapView(MfTownDetailView):
    """
    Podrobna mapa se situaci herev v obci.
    """
    template_name = 'mf/town_map.html'


class MfTownComments(MfTownDetailView):
    """
    Diskuze k dane obci.
    """
    template_name = 'mf/town_comments.html'


# class MfCommon(object):
#     """
#     TODO:
#     """
#
#     PER_PAGE = 20
#
#     def paginator(self, qs):
#         """
#         Metoda, ktera se stara o strankovani zadaneho QS. Vraci data ve slovniku
#         vhodna pro pouziti primo v sablonach.
#
#         Kopie kodu Django generic ListView.
#         """
#         paginator = Paginator(qs, self.PER_PAGE, allow_empty_first_page=True)
#         page = self.kwargs.get('p') or self.request.GET.get('p') or 1
#
#         try:
#             page_number = int(page)
#         except ValueError:
#             raise Http404
#         try:
#             page = paginator.page(page_number)
#             return {
#                 'paginator': paginator,
#                 'page_obj': page,
#                 'is_paginated': page.has_other_pages(),
#                 'object_list': page.object_list
#             }
#         except InvalidPage:
#             raise Http404
#
#
# class MfTownHellsListView(TownDetailView, MfCommon):
#     """
#     Prehled heren ve meste.
#     """
#     template_name = 'mf/town_hells_list.html'
#
#     def get_context_data(self, **kwargs):
#         out = super(MfTownHellsListView, self).get_context_data(**kwargs)
#         statistics = MfPlaceConflict.statistics(self.object)
#         out.update(statistics)
#         out.update(self.paginator(statistics['hells_qs']))
#         out['campaign'] = self.kwargs['campaign']
#         return out
#
#
# class MfTownHellDetailView(TownDetailView):
#     """
#     Detail herny ve meste.
#     """
#     template_name = 'mf/town_hell_detail.html'
#
#     def get_context_data(self, **kwargs):
#         out = super(MfTownHellDetailView, self).get_context_data(**kwargs)
#         statistics = MfPlaceConflict.statistics(self.object)
#         out.update(statistics)
#
#         hell = Hell.objects.get(region=out['region'], district=out['district'], town=out['town'], id=self.kwargs['id'])
#         out.update({
#             'hell': hell,
#             'counts': MachineCount.objects.filter(hell=hell),
#             'campaign': self.kwargs['campaign']
#         })
#         return out
#
#
# class MfTownBuildingsListView(TownDetailView, MfCommon):
#     """
#     Prehled budov ve meste.
#     """
#     template_name = 'mf/town_buildings_list.html'
#
#     def get_context_data(self, **kwargs):
#         out = super(MfTownBuildingsListView, self).get_context_data(**kwargs)
#         statistics = MfPlaceConflict.statistics(self.object)
#         out.update(statistics)
#         out.update({
#             'buildings_qs': MfPlace.objects.filter(town=out['town']),
#             'campaign': self.kwargs['campaign']
#         })
#         out.update(self.paginator(out['buildings_qs']))
#         return out
#
#
# class MfTownBuildingDetailView(TownDetailView):
#     """
#     Detail budovy ve meste.
#     """
#     template_name = 'mf/town_building_detail.html'
#
#     def get_context_data(self, **kwargs):
#         out = super(MfTownBuildingDetailView, self).get_context_data(**kwargs)
#         statistics = MfPlaceConflict.statistics(self.object)
#         out.update(statistics)
#         out.update({
#             'building': MfPlace.objects.get(region=out['region'], district=out['district'], town=out['town'], id=self.kwargs['id']),
#             'campaign': self.kwargs['campaign']
#         })
#         return out
