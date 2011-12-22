# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import DetailView, ListView

from hazard.campaigns.models import Campaign


class CampaignHomepageView(ListView):
    """
    TODO:
    """
    context_object_name = 'campaigns'
    template_name = 'campaigns/homepage.html'

    def get_queryset(self):
        return Campaign.objects.select_related().all()


class CampaignDetailView(DetailView):
    """
    TODO:
    """
    context_object_name = 'campaign'

    def get_object(self, queryset=None):
        return Campaign.objects.select_related().get(slug=self.kwargs['campaign'])

    def get_template_names(self):
        return ['%s/homepage.html' % self.kwargs['campaign']]

    def get_context_data(self, **kwargs):
        out = super(CampaignDetailView, self).get_context_data(**kwargs)
        out.update({
            'campaigns': Campaign.objects.select_related().all()
        })
        return out
