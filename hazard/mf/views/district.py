# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from hazard.territories.views import TownListView
from hazard.territories.models import District, Region
from hazard.mf.models import MfPlaceConflict
from hazard.shared.ajax import JSONView


class MfDistrictView(JSONView, TownListView):
    """
    Prehled okresu.
    """
    base_template = 'mf/base.html'
    template_name = 'mf/district.html'

    def get_context_data(self, **kwargs):
        out = super(MfDistrictView, self).get_context_data(**kwargs)
        statistics = MfPlaceConflict.statistics(None, group_by='district')
        out.update({
            'base_template': self.base_template,
            'statistics': statistics,
            'regions': dict([(i.id, i) for i in Region.objects.select_related().all()]),
            'districts': dict([(i.id, i) for i in District.objects.select_related().all()]),
            'campaign': self.kwargs['campaign']
        })
        out['json_details'] = out['districts']
        return out
