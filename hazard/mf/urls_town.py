# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.mf.views import MfTownDetailView, MfTownMapView, MfTownComments

urlpatterns = patterns('',
    url(r'^$', MfTownDetailView.as_view(), name="mf-town"),
    url(r'^mapa/$', MfTownMapView.as_view(), name="mf-town-map"),
    url(r'^komentare/$', MfTownComments.as_view(), name="mf-town-comments"),
)
