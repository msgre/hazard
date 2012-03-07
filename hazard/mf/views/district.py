# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.utils.datastructures import SortedDict

from hazard.territories.views import TownListView
from hazard.territories.models import District, Region
from hazard.mf.models import MfPlaceConflict
from hazard.shared.ajax import JSONView
from hazard.campaigns.models import Campaign


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
            'regions': SortedDict([(i.id, i) for i in Region.objects.select_related().all()]),
            'districts': SortedDict([(i.id, i) for i in District.objects.select_related().all()]),
            'campaign_slug': self.kwargs['campaign'],
            'campaign': Campaign.objects.get(slug=self.kwargs['campaign'])
        })
        out['json_details'] = out['districts']
        return out
