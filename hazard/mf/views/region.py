# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
TODO: tohle jsou prilepky za territories url strukturu
"""

from django.core.paginator import Paginator, InvalidPage

from hazard.gobjects.models import Hell, MachineCount
from hazard.territories.views import DistrictListView
from hazard.mf.models import BuildingConflict, Building


class MfDistrictListView(DistrictListView):
    """
    TODO:
    """
    template_name = 'mf/district_list.html'

    def get_context_data(self, **kwargs):
        out = super(MfDistrictListView, self).get_context_data(**kwargs)

        total = {
            'hells_total': 0,
            'machines_total': 0,
            'nonconflicts_hells_total': 0,
            'nonconflicts_machines_total': 0,
            'conflicts_hells_total': 0,
            'conflicts_machines_total': 0,
        }
        statistics = {}

        for district in self.object_list:
            for town in district.town_set.all():
                statistics[town.id] = BuildingConflict.statistics(town)
                for k in total.keys():
                    if k in statistics[town.id]:
                        total[k] += statistics[town.id][k]

        # procentualni hodnoty heren
        if total['hells_total']:
            total['conflicts_hells_perc'] = total['conflicts_hells_total'] / float(total['hells_total']) * 100
            total['nonconflicts_hells_perc'] = 100 - total['conflicts_hells_perc']
        # procentualni hodnoty automatu
        if total['machines_total']:
            total['conflicts_machines_perc'] = total['conflicts_machines_total'] / float(total['machines_total']) * 100
            total['nonconflicts_machines_perc'] = 100 - total['conflicts_machines_perc']

        out.update({
            'town_statistics': statistics,
            'total_statistics': total
        })
        return out
