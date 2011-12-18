# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.mf.views import MfDistrictListView

urlpatterns = patterns('',
    url(r'^$', MfDistrictListView.as_view(), name="mf-region"),
)
