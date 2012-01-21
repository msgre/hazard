# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from hazard.mf.views import MfCampaignBase, MfAjax, MfTownAjax

AJAX_CACHE_TIMEOUT = 60 * 10

urlpatterns = patterns('',
    # staticke stranky
    url(r'^$', MfCampaignBase.as_view(template_name='mf/homepage.html'), name='campaign-mf-homepage'),
    url(r'^pomozte-nam/$', MfCampaignBase.as_view(template_name='mf/help.html'), name='campaign-mf-help'),
    url(r'^porusovani-zakona/$', MfCampaignBase.as_view(template_name='mf/law.html'), name='campaign-mf-law'),
    url(r'^casovy-vyvoj/$', MfCampaignBase.as_view(template_name='mf/timeline.html'), name='campaign-mf-timeline'),
    url(r'^o-mape/$', MfCampaignBase.as_view(template_name='mf/about.html'), name='campaign-mf-about'),
    # ajaxy
    url(r'^ajax/(?P<type>kraje|okresy)/$', cache_page(MfAjax.as_view(), AJAX_CACHE_TIMEOUT), name='campaign-mf-ajax'),
    url(r'^ajax/(?P<type>obce)/(?P<district>[\-a-z]+)/$', cache_page(MfTownAjax.as_view(), AJAX_CACHE_TIMEOUT), name='campaign-mf-town-ajax'),
)
