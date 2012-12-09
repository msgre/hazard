# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

admin.autodiscover()

# URL ze stareho webu
PREFIX = 'http://sousedstvi.mapyhazardu.cz/'
urlpatterns = patterns('',
    url(r'^(?P<url>pridat/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>hitparada/.*)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>podporuji-nas/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>navod/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>sousedstvi/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>d/.+)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>spoluprace/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>kml/)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
    url(r'^(?P<url>gdd-.+)$', RedirectView.as_view(url=PREFIX+'%(url)s')),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='pages/homepage.html')),
    url(r'^kampan/$', RedirectView.as_view(url='/kampane/')),
    url(r'^kampane/', include('hazard.campaigns.urls')),
    url(r'^mapy/', TemplateView.as_view(template_name='pages/maps.html'), name="maps"),
    url(r'^navody/', TemplateView.as_view(template_name='pages/manual.html'), name="manual"),
    url(r'^zpravy/', include('hazard.news.urls')),
    url(r'^kontakt/$', TemplateView.as_view(template_name='pages/contact.html'), name="contact"),
    url(r'^souvislosti/$', TemplateView.as_view(template_name='pages/context.html'), name="context"),
    url(r'^souvislosti/porusovani-zakona/$', TemplateView.as_view(template_name='pages/law.html'), name='law'),
    url(r'^souvislosti/casovy-vyvoj/$', TemplateView.as_view(template_name='pages/timeline.html'), name='timeline'),
    url(r'^souvislosti/dokumenty/$', TemplateView.as_view(template_name='pages/documents.html'), name='documents'),
    url(r'^souvislosti/infografiky/$', TemplateView.as_view(template_name='pages/infograph.html'), name='infograph'),
    url(r'^souvislosti/slovnik-pojmu/', include('hazard.dictionary.urls')),
    url(r'^souvislosti/kalkulacka/', TemplateView.as_view(template_name='pages/calculator.html'), name="calculator"),
)

# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
        #(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.STATIC_ROOT, '')}),
    )

urlpatterns += patterns('',
    url(r'^', include('hazard.territories.urls'))
)
