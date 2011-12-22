# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.mf.views import MfRegionView

urlpatterns = patterns('',
    url(r'^$', MfRegionView.as_view(), name="mf-region"),
)
