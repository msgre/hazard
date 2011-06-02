# -*- coding: utf-8 -*-

import socket

from django.contrib import messages
from django.views.generic import DetailView, FormView, ListView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.validators import ipv4_re

from hazard.geo.models import Entry, Zone
from hazard.geo.forms import KMLForm, PbrErrorList
from hazard.shared.director import director

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

    def post(self, request, *args, **kwargs):
        """
        Hack -- formularova policka URL nedelaji strip() a pokud nekdo do formiku
        zada URL s nejakymi bilymi znaky, aplikace spadne. Proto zde, na urovni
        view tesne pred tim nez predam rizeni generickym view stripnu zadana URL.
        """
        if hasattr(request, 'POST'):
            request.POST = request.POST.copy()
            if 'hells' in request.POST:
                request.POST['hells'] = request.POST['hells'].strip()
            if 'buildings' in request.POST:
                request.POST['buildings'] = request.POST['buildings'].strip()
        return super(EntryFormView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        out = super(EntryFormView, self).get_form_kwargs()
        out.update(error_class=PbrErrorList, ip=self.get_ip())
        return out

    def form_invalid(self, form):
        if hasattr(form, 'qkey'):
            director.done(form.qkey)
        cache.clear() # musime maznout cache, protoze jinak by se nezobrazila message
        if form.update_no_change_slug:
            # v pripade, ze se mapy nezmenily a formik byl odeslan pres
            # tlacitko v detailu stranky, zustaneme na strance s detailem
            # a error hlasku z formulare pretransformuje na message
            messages.warning(self.request, form.non_field_errors()[0], extra_tags='notice')
            return HttpResponseRedirect(reverse('entry-detail',
                                        kwargs={'slug': form.update_no_change_slug}))
        else:
            return super(EntryFormView, self).form_invalid(form)

    def get_ip(self):
        return self.request.META.get('REMOTE_ADDR', self.request.META.get('HTTP_X_FORWARDED_FOR', ''))

    def form_valid(self, form):
        """
        V pripade ze zadane KML soubory jsou v poradku, ulozime vyparsovana data
        do databaze.
        """
        # ip adresu vytahneme primarne z HTTP hlavicek
        ip = self.get_ip()

        # pokud ale ip adresa odpovida serveru, na kterem bezi nase aplikace,
        # mrkneme se do GETu, jestli tam neni IP adresa explicitne uvedena
        # (timto zpusobem se totiz prenasi IP v pripade, ze pozadavek o zpracovani
        # map prichazi z cronjobu)
        server_name = self.request.META.get('SERVER_NAME', '')
        if ip and server_name:
            try:
                server_ip = socket.gethostbyaddr(server_name)[2]
                if ip in server_ip and 'ip' in self.request.GET and ipv4_re.match(self.request.GET['ip']):
                    ip = request.GET['ip']
            except:
                pass

        # ulozeni
        entry, exists = form.save(ip)
        if not exists:
            if entry.public:
                messages.success(self.request, u'Hotovo. Díky!')
            else:
                messages.success(self.request, u'Hotovo. Vaše mapa byla uložena, ale musíme v ní ještě doplnit některé údaje. Až dáme věci do pořádku, zveřejníme ji. Díky!', extra_tags='notice')
        else:
            if not entry.public:
                messages.warning(self.request, u'Hotovo. Záznam pro %s ale v databázi již máme a Váš příspěvek musíme manuálně zkontrolovat. Pokud bude vše v pořádku, dosavadní informace dáme pryč a Vaše nová data zveřejníme. Díky!' % entry.title, extra_tags='notice')
            else:
                messages.warning(self.request, u'Hotovo. Záznam pro %s byl uspěšně aktualizován. Díky!' % entry.title, extra_tags='notice')
        director.done(form.qkey)
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
            # povoleni/zakazani aktualizace mapy
            'should_be_updated': KMLForm.should_be_updated(self.object.hell_url, self.object.building_url)
        })
        return out


TOP_ENTRIES_COUNT = 4

class EntryListView(ListView):
    context_object_name = "entries"
    template_name = 'geo/list.html'

    def get_queryset(self):
        return Entry.objects.filter(public=True)[:TOP_ENTRIES_COUNT]

    def get_context_data(self, **kwargs):
        out = super(EntryListView, self).get_context_data(**kwargs)
        out.update({
            'show_next': Entry.objects.filter(public=True).count() > TOP_ENTRIES_COUNT
        })
        return out

class FullEntryListView(ListView):
    context_object_name = "entries"
    template_name = 'geo/fulllist.html'

    def get_queryset(self):
        return Entry.objects.filter(public=True)
