# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.news.views import NewDetailView, NewListView

urlpatterns = patterns('',
    url(r'^$', NewListView.as_view(), name="new-list"),
    url(r'^(?P<slug>[-0-9a-z]+)/$', NewDetailView.as_view(), name="new-detail"),
)
