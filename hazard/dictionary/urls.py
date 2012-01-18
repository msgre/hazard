# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.dictionary.views import TermListView

urlpatterns = patterns('',
    url(r'^$', TermListView.as_view(), name="dictionary"),
)
