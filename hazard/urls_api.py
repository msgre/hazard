# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *

from hazard.shared.views import NearestHellsView

urlpatterns = patterns('',
    url(r'^v0/hells/nearest/$', NearestHellsView.as_view()),
)
