# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from hazard.territories.views import DistrictListView
from hazard.mf.models import MfPlaceConflict
from hazard.territories.models import Region


class MfRegionView(DistrictListView):
    """
    Prehled kraju.
    """
    template_name = 'mf/region.html'

    def get_context_data(self, **kwargs):
        out = super(MfRegionView, self).get_context_data(**kwargs)
        statistics = MfPlaceConflict.statistics(None, group_by='region')
        out.update({
            'statistics': statistics,
            'regions': dict([(i.id, i) for i in Region.objects.select_related().all()]),
            'campaign': self.kwargs['campaign']
        })
        return out
