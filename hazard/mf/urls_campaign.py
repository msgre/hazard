# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *

from hazard.mf.views import MfCampaignHomepage, MfCampaignToplist

urlpatterns = patterns('',
    url(r'^$', MfCampaignHomepage.as_view(), name='campaign-mf-homepage'),
    url(r'^zebricky/$', MfCampaignToplist.as_view(), name='campaign-mf-toplist'),
)
