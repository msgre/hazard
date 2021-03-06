from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views.decorators.cache import cache_page

from hazard.geo.views import EntryDetailView, EntryFormView, EntryListView, FullEntryListView
from hazard.news.views import NewDetailView, NewListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name="shared/homepage.html")),
    url(r'^pridat/$', EntryFormView.as_view(), name="entry-form"),
    url(r'^hitparada/$', EntryListView.as_view(), name="entry-list"),
    url(r'^hitparada/kompletni/$', FullEntryListView.as_view(), name="full-entry-list"),
    url(r'^kontakt/$', TemplateView.as_view(template_name="shared/contact.html"), name="contact"),
    url(r'^podporuji-nas/$', TemplateView.as_view(template_name="shared/support.html"), name="support"),
    url(r'^navod/$', TemplateView.as_view(template_name="shared/instruction.html"), name="instruction"),
    url(r'^sousedstvi/$', TemplateView.as_view(template_name="shared/neighborhood.html"), name="neighborhood"),
    url(r'^d/(?P<slug>[-_0-9a-z]+)/$', cache_page(EntryDetailView.as_view(), 60 * 20), name="entry-detail"),
    url(r'^zpravy/$', NewListView.as_view(), name="new-list"),
    url(r'^zpravy/(?P<slug>[-_0-9a-z]+)/$', NewDetailView.as_view(), name="new-detail"),
    url(r'^spoluprace/$', TemplateView.as_view(template_name="shared/cooperation.html"), name="cooperation"),
    url(r'^kml/$', cache_page(TemplateView.as_view(template_name="shared/kml_list.html"), 60 * 20), name="kml-list"),
    url(r'^gdd-?(2011|11)?/$', RedirectView.as_view(url="/kml/")), # google developer day
)


# debug static media server
from django.conf import settings
import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT, '')}),
    )
