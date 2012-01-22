# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='pages/homepage.html')),
    url(r'^slovnik-pojmu/', include('hazard.dictionary.urls')),
    url(r'^kampane/$', RedirectView.as_view(url='/kampan/')),
    url(r'^kampan/', include('hazard.campaigns.urls')),
    url(r'^zpravy/', include('hazard.news.urls')),
    url(r'^kontakt/$', TemplateView.as_view(template_name='pages/contact.html'), name="contact"),
    url(r'^', include('hazard.territories.urls'))
)

# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
    )
