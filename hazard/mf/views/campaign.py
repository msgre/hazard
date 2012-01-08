# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import DetailView, TemplateView

from hazard.campaigns.models import Campaign
from hazard.mf.models import MfPlaceConflict
from hazard.territories.models import Region, District, Town


class MfCampaignHomepage(DetailView):
    """
    Uvodni stranka kampane o VLT automatech povolenych MF.
    """
    context_object_name = 'campaign'
    template_name = 'mf/homepage.html'

    def get_object(self, queryset=None):
        return Campaign.objects.select_related().get(slug=self.kwargs['campaign'])

    def get_context_data(self, **kwargs):
        out = super(MfCampaignHomepage, self).get_context_data(**kwargs)
        out.update({
            'campaigns': Campaign.objects.select_related().all()
        })
        return out


class MfCampaignToplist(MfCampaignHomepage):
    """
    Zebricky nejhorsich.

    TODO: pokud bych neco podobneho realizoval, pak bych asi mel upravit
    metodu statistics tak, aby pocitala jen neco a ne vsechno (default).
    Napr. tady budu zobrazovat vzdy jen jeden pohled (herny total v krajich/okresech/mestech),
    ale statistika se pocita i pro vse ostatni (total automatu, procenta, apod)
    """
    template_name = 'mf/toplist.html'

    def sort(self, statistics):
        out = {}
        for k in statistics:
            out[k] = sorted([(i, statistics[k][i]) for i in statistics[k]], cmp=lambda a, b: cmp(a[1], b[1]), reverse=True)[:20]
        return out

    def get_region_statistics(self):
        statistics = MfPlaceConflict.statistics(None, group_by='region')
        return self.sort(statistics)

    def get_district_statistics(self):
        statistics = MfPlaceConflict.statistics(None, group_by='district')
        return self.sort(statistics)

    def get_town_statistics(self):
        statistics = MfPlaceConflict.statistics(None, group_by='town')
        return self.sort(statistics)

    def get_context_data(self, **kwargs):
        out = super(MfCampaignToplist, self).get_context_data(**kwargs)
        out.update({
            # statistiky pro geo oblasti
            'region_statistics': self.get_region_statistics(),
            'district_statistics': self.get_district_statistics(),
            'town_statistics': self.get_town_statistics(),
            # seznam vsech geo oblasti
            'regions': dict([(i.id, i) for i in Region.objects.select_related().all()]),
            'districts': dict([(i.id, i) for i in District.objects.select_related().all()]),
            'towns': dict([(i.id, i) for i in Town.objects.select_related().all()]),
        })
        return out
