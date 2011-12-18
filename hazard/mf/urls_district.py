# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.mf.views import MfTownListView #, MfDistrictHellsListView, \
                            # MfDistrictHellDetailView, MfDistrictBuildingsListView, \
                            # MfDistrictBuildingDetailView

urlpatterns = patterns('',
    url(r'^$', MfTownListView.as_view(), name="mf-district"),
    # url(r'^herny/$', MfDistrictHellsListView.as_view(), name="mf-district-hells-list"),
    # url(r'^herny/(?P<id>\d+)/$', MfDistrictHellDetailView.as_view(), name="mf-district-hell-detail"),
    # url(r'^budovy/$', MfDistrictBuildingsListView.as_view(), name="mf-district-buildings-list"),
    # url(r'^budovy/(?P<id>\d+)/$', MfDistrictBuildingDetailView.as_view(), name="mf-district-building-detail"),
)
