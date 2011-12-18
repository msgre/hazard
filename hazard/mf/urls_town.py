# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.mf.views import MfTownDetailView, MfTownMapView, MfTownHellsListView, \
                            MfTownHellDetailView,MfTownBuildingsListView, \
                            MfTownBuildingDetailView

urlpatterns = patterns('',
    url(r'^$', MfTownDetailView.as_view(), name="mf-town"),
    url(r'^mapa/$', MfTownMapView.as_view(), name="mf-town-map"),
    url(r'^herny/$', MfTownHellsListView.as_view(), name="mf-town-hells-list"),
    url(r'^herny/(?P<id>\d+)/$', MfTownHellDetailView.as_view(), name="mf-town-hell-detail"),
    url(r'^budovy/$', MfTownBuildingsListView.as_view(), name="mf-town-buildings-list"),
    url(r'^budovy/(?P<id>\d+)/$', MfTownBuildingDetailView.as_view(), name="mf-town-building-detail"),
)
