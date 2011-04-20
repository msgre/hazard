from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from hazard.geo.views import EntryDetailView, EntryFormView, HomepageView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomepageView.as_view(), name="entry-form"),
    url(r'^novy/$', EntryFormView.as_view(), name="entry-form"),
    url(r'^d/(?P<slug>[-_0-9a-z]+)/$', EntryDetailView.as_view(), name="entry-detail"),
)


# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
    )
