# -*- coding: utf-8 -*-

from django.contrib import messages
from django.views.generic import DetailView, FormView, ListView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from hazard.geo.models import Entry, Zone
from hazard.geo.forms import KMLForm, PbrErrorList


class EntryFormView(FormView):
    """
    Formular pro vlozeni KML souboru s popisem heren a verejnych budov.
    """
    form_class = KMLForm
    template_name = 'geo/form.html'
    # # brno podruhe
    # initial = {
    #     'buildings': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=334b&msa=0&output=nl&msid=217120881929273348625.0004a1ecb651553072cca',
    #     'hells': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=334b&msa=0&output=nl&msid=217120881929273348625.0004a1eca126d4f32052c'
    # }
    # # valmez
    # initial = {
    #     'buildings': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=332a&msa=0&output=nl&msid=217120881929273348625.00049e61b09dabeb67157',
    #     'hells': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=4&jsv=332a&msa=0&output=nl&msid=217120881929273348625.0004a13fa50f7e1dc6c22'
    # }
    # # brno jednodussi
    # initial = {
    #     'buildings': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=1&jsv=332a&msa=0&output=nl&msid=217120881929273348625.0004a1739eed3bb1f0f24',
    #     'hells': 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=1&jsv=332a&msa=0&output=nl&msid=217120881929273348625.0004a172ca42f5022bab1'
    # }


    def get_form_kwargs(self):
        out = super(EntryFormView, self).get_form_kwargs()
        out.update(error_class=PbrErrorList)
        return out

    def form_valid(self, form):
        """
        V pripade ze zadane KML soubory jsou v poradku, ulozime vyparsovana data
        do databaze.
        """
        ip = self.request.META.get('REMOTE_ADDR', self.request.META.get('HTTP_X_FORWARDED_FOR', ''))
        entry, exists = form.create_entry(ip)
        if not exists:
            form.save(entry)
            if entry.public:
                messages.success(self.request, 'Hotovo. Díky!')
            else:
                messages.success(self.request, 'Hotovo. Vaše mapa byla uložena, \
                ale musíme v ní ještě doplnit některé údaje. Až dáme věci do \
                pořádku, zveřejníme ji. Díky!')
        else:
            messages.warning(self.request, u'Hotovo. Záznam pro %s ale \
            v databázi již máme a Váš příspěvek musíme manuálně zkontrolovat. \
            Pokud bude vše v pořádku, dosavadní informace dáme pryč a Vaše nová \
            data zveřejníme. Díky!' % entry.title)
        return HttpResponseRedirect(reverse('entry-detail',
                                    kwargs={'slug': entry.slug}))


class EntryDetailView(DetailView):
    """
    Detail konkretniho zaznamu (obce).
    """
    context_object_name = "entry"
    template_name = 'geo/detail.html'

    def get_queryset(self):
        """
        Poznamka: puvodne jsem tahal jen zverejnene zaznamy, ale v pripade
        detailu budu zobrazovat i ty neverejne, protoze potrebuji uzivateli
        zobrazit to co prave nahral.

        Na ostatnich mistech (v mape na pozadi, hitparade) ale budeme zobrazovat
        jen ty opravdu zverejnene.
        """
        #return Entry.objects.filter(public=True, slug=self.kwargs['slug'])
        return Entry.objects.filter(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """
        Statisticke udaje o hernach.
        """
        out = super(EntryDetailView, self).get_context_data(**kwargs)

        # pomocne promenne
        hells = dict([(i.id, {'title':i.title, 'pos':i.point.coords, \
                     'description': i.description, 'conflict':i.in_conflict, \
                     'buildings':list(i.zones.all().values_list('building', flat=True)),
                     'uzone': i.uzone and i.uzone.poly.coords[0] or []}) \
                     for i in self.object.hell_set.all()])
        buildings = dict([(i.id, {'title':i.title, 'polygon':i.poly.coords[0],
                         'zone':i.zone_id}) \
                         for i in self.object.building_set.all()])
        zone_ids = [i['zone'] for i in buildings.values()]

        # aktualizovani kontextu
        out.update({
            # slovnik heren
            'hells': hells,
            # slovnik verejnych budov
            'buildings': buildings,
            # slovnik okolnich zon
            'zones': dict([(i.id, {'polygon': i.poly.coords[0]}) \
                           for i in Zone.objects.filter(id__in=zone_ids)]),
        })
        return out


TOP_ENTRIES_COUNT = 10

class EntryListView(ListView):
    context_object_name = "entries"
    template_name = 'geo/list.html'
    paginate_by = 5

    def get_queryset(self):
        return Entry.objects.filter(public=True).order_by('-dperc')[:TOP_ENTRIES_COUNT]
