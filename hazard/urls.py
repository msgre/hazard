from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView


from hazard.geo.views import EntryDetailView, EntryFormView, EntryListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name="shared/homepage.html")),
    url(r'^pridat/$', EntryFormView.as_view(), name="entry-form"),
    url(r'^hitparada/$', EntryListView.as_view(), name="entry-list"),
    url(r'^kontakt/$', TemplateView.as_view(template_name="shared/contact.html"), name="contact"),
    url(r'^navod/$', TemplateView.as_view(template_name="shared/instruction.html"), name="instruction"),
    url(r'^d/(?P<slug>[-_0-9a-z]+)/$', EntryDetailView.as_view(), name="entry-detail"),
)


# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
    )
