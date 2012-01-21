# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from hazard.territories.views import RegionListView, DistrictListView, TownListView, TownDetailView, AutocompleteView, RedirectorView

urlpatterns = patterns('',
    url(r'^autocomplete/$', AutocompleteView.as_view(), name='autocomplete'),

    # TODO: nejspis to propojim takto natvrdo a hotovo
    # ale tak nejak citim, ze by to melo jit i lepe... (nejake proxy view)
    url(r'^(?P<region>[-0-9a-z]+)/kampan/(?P<campaign>mf)/', include('hazard.mf.urls_region')),
    url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/kampan/(?P<campaign>mf)/', include('hazard.mf.urls_district')),
    url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/(?P<town>[-0-9a-z]+)/kampan/(?P<campaign>mf)/', include('hazard.mf.urls_town')),

    url(r'^$', RegionListView.as_view(), name="region"),
    url(r'^(?P<region>[-0-9a-z]+)/$', DistrictListView.as_view(), name="region"),
    url(r'^(?P<region>[-0-9a-z]+)/_/$', RedirectorView.as_view(model='region', subobjects='district_set'), name="district-redirector"),
    url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/$', TownListView.as_view(), name="district"),
    url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/_/$', RedirectorView.as_view(model='district', subobjects='town_set'), name="town-redirector"),
    url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/(?P<town>[-0-9a-z]+)/$', TownDetailView.as_view(), name="town"),

    # tohle je trochu nestandardni, lepsi by bylo inkludovat s hlavniho urls,
    # ale tady to zase dava logiku v te navaznosti na skladbu URL
)
