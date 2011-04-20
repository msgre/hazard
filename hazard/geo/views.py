# -*- coding: utf-8 -*-

from django.contrib import messages
from django.views.generic import DetailView, FormView, ListView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from hazard.geo.models import Entry
from hazard.geo.forms import KMLForm


class EntryFormView(FormView):
    """
    Formular pro vlozeni KML souboru s popisem heren a verejnych budov.
    """
    form_class = KMLForm
    template_name = 'geo/form.html'
    initial = {
        'buildings': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=332a&msa=0&output=nl&msid=217120881929273348625.00049e61b09dabeb67157',
        'hells': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=1&jsv=332a&msa=0&output=nl&msid=217120881929273348625.0004a13fa50f7e1dc6c22'
    }

    def form_valid(self, form):
        """
        V pripade ze zadane KML soubory jsou v poradku, ulozime vyparsovana data
        do databaze.
        """
        entry, created = form.create_entry()
        if created:
            form.save(entry)
            messages.success(self.request, 'Hotovo. Díky!')
        else:
            messages.warning(self.request, u'Záznam pro %s již existuje. Pokud \
            chcete zde zobrazené informace změnit, postupujte \
            <a href="#">následujícím způsobem</a>.' % entry.title)
        return HttpResponseRedirect(reverse('entry-detail',
                                    kwargs={'slug': entry.slug}))


class EntryDetailView(DetailView):
    """
    Detail konkretniho zaznamu (obce).
    """
    context_object_name = "entry"
    template_name = 'geo/detail.html'

    def get_queryset(self):
        return Entry.objects.filter(public=True, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """
        Statisticke udaje o hernach.
        """
        out = super(EntryDetailView, self).get_context_data(**kwargs)
        total_hell = float(self.object.hell_set.count())
        noproblem_hell = self.object.hell_set.filter(zones__isnull=True).count()
        out.update({
            'percent': (total_hell - noproblem_hell) / total_hell * 100,
            'per_population': self.object.population / total_hell,
            'per_area': total_hell / self.object.area
        })
        return out


TOP_ENTRIES_COUNT = 10

class HomepageView(ListView):
    context_object_name = "entries"
    template_name = 'geo/homepage.html'

    def get_queryset(self):
        return Entry.objects.filter(public=True).order_by('-dperc')[:TOP_ENTRIES_COUNT]
