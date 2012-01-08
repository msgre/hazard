# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import ListView

from hazard.campaigns.models import Campaign


class CampaignHomepageView(ListView):
    """
    Uvodni stranka s prehledem vsech kampani.
    """
    context_object_name = 'campaigns'
    template_name = 'campaigns/homepage.html'

    def get_queryset(self):
        return Campaign.objects.select_related().all()
