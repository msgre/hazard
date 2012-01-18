# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import DetailView

from hazard.campaigns.models import Campaign


class MfCampaignBase(DetailView):
    context_object_name = 'campaign'

    def get_object(self, queryset=None):
        return Campaign.objects.select_related().get(slug=self.kwargs['campaign'])

    def get_context_data(self, **kwargs):
        out = super(MfCampaignBase, self).get_context_data(**kwargs)
        out.update({
            'campaigns': Campaign.objects.select_related().all()
        })
        return out
