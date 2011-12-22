# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.campaigns.views import CampaignHomepageView, CampaignDetailView

urlpatterns = patterns('',
    url(r'^$', CampaignHomepageView.as_view(), name="campaign-homepage"),
    url(r'^(?P<campaign>[-0-9a-z]+)/$', CampaignDetailView.as_view(), name="campaign-detail"),
)
