from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views.decorators.cache import cache_page

#from hazard.geo.views import EntryDetailView, EntryFormView, EntryListView, FullEntryListView
#from hazard.news.views import NewDetailView, NewListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('hazard.territories.urls')),
)

# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
    )
