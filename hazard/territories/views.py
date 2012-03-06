# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import DetailView, ListView, TemplateView, RedirectView
from django.http import Http404, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.db import models
from django.shortcuts import get_object_or_404

from hazard.territories.models import Region, District, Town
from hazard.campaigns.models import Campaign
from hazard.territories.settings import REDIRECT_TO_DEFAULT_CAMPAIGN


class TerritoriesBaseView(object):
    """
    Spolecna trida pro territories view, zajistuje presmerovani na kampane.
    """

    def get(self, request, *args, **kwargs):
        if not 'campaign' in kwargs and REDIRECT_TO_DEFAULT_CAMPAIGN:
            campaign = Campaign.objects.get(default=True)
            return HttpResponseRedirect("%skampan/%s/" % (request.path, campaign.slug))
        else:
            return super(TerritoriesBaseView, self).get(request, *args, **kwargs)


class RegionListView(TerritoriesBaseView, ListView):
    """
    Vypis kraju.
    """
    context_object_name = "regions"
    template_name = 'territories/region_list.html'
    allow_empty = True

    def get_queryset(self):
        return Region.objects.select_related().all()


class DistrictListView(TerritoriesBaseView, ListView):
    """
    Vypis okresu.
    """
    context_object_name = "districts"
    template_name = 'territories/district_list.html'
    allow_empty = True

    def get_queryset(self):
        return District.objects.select_related().filter(region__slug=self.kwargs['region'])

    def get_context_data(self, **kwargs):
        kwargs.update({
            'region': Region.objects.select_related().get(slug=self.kwargs['region'])
        })
        return super(DistrictListView, self).get_context_data(**kwargs)


class TownListView(TerritoriesBaseView, ListView):
    """
    Vypis mest.
    """
    context_object_name = "towns"
    template_name = 'territories/town_list.html'
    allow_empty = True

    def get_queryset(self):
        return Town.objects.select_related().filter(region__slug=self.kwargs['region'], district__slug=self.kwargs['district'])

    def get_context_data(self, **kwargs):
        kwargs.update({
            'region': Region.objects.select_related().get(slug=self.kwargs['region']),
            'district': District.objects.select_related().get(slug=self.kwargs['district']),
        })
        return super(TownListView, self).get_context_data(**kwargs)


class TownDetailView(TerritoriesBaseView, DetailView):
    """
    Detail konkretniho mesta.
    """
    context_object_name = "town"
    template_name = 'shop/town_detail.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'region': Region.objects.select_related().get(slug=self.kwargs['region']),
            'district': District.objects.select_related().get(slug=self.kwargs['district'])
            # town je generovan s pomoci DetailView
        })
        return super(TownDetailView, self).get_context_data(**kwargs)

    def get_object(self, queryset=None):
        try:
            return Town.objects.select_related().get(
                region__slug = self.kwargs['region'],
                district__slug = self.kwargs['district'],
                slug = self.kwargs['town']
            )
        except Town.DoesNotExist:
            raise Http404


class AutocompleteView(TemplateView):
    """
    Backend pro naseptavac kraju/okresu/obci.
    """
    template_name = 'territories/autocomplete.html'

    def get_context_data(self, **kwargs):
        out = super(AutocompleteView, self).get_context_data(**kwargs)
        term = self.request.GET.get('term', '')
        if len(term) >= 2:
            # budem reagovat od 2 pismen vys
            qs_kwargs = {'slug__contains': slugify(term)}
            regions = [{'label': i.title, 'url': i.get_absolute_url(), 'category': u'Kraj'} \
                       for i in Region.objects.select_related().filter(**qs_kwargs)]
            districts = [{'label': u"%s (%s)" % (i.title.replace(u'Okres ', u''), i.region.title), 'url': i.get_absolute_url(), 'category': u'Okres'} \
                         for i in District.objects.select_related().filter(**qs_kwargs)]
            towns = [{'label': u"%s (%s)" % (i.title.replace(u'Obec ', u''), i.district.title), 'url': i.get_absolute_url(), 'category': u'Obec'} \
                     for i in Town.objects.select_related().filter(**qs_kwargs)]
            out.update({'data': regions + districts + towns})
        else:
            out.update({'data': []})
        return out

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({'mimetype': 'application/json'})
        return super(AutocompleteView, self).render_to_response(context, **response_kwargs)


class RedirectorView(RedirectView):
    """
    Pomocna trida pro "slepe" presmerovani na podrazeny uzemni celek.

    Priklad:

    Jsem ve zlinskem kraji (/zlinsky/) a chci se rychle dostat na nejaky
    okres v nem (aniz bych predem znal jmeno nektereho ze zlinskych okresu).
    Vlozim do prohlizece URL /zlinsky/_/, cimz se zavola tato trida a ta
    vrati URL /zlinsky/kromeriz/.

    Pouziti (nastaveni v urls.py):

        url(r'^(?P<region>[-0-9a-z]+)/_/$',
            RedirectorView.as_view(model='region', subobjects='district_set'),
            name="district-redirector")
        url(r'^(?P<region>[-0-9a-z]+)/(?P<district>[-0-9a-z]+)/_/$',
            RedirectorView.as_view(model='district', subobjects='town_set'),
            name="town-redirector")
    """
    model = None
    subobjects = None

    def get_redirect_url(self, **kwargs):
        if not self.model or not self.subobjects:
            raise Http404
        model = models.get_model('territories', self.model)
        obj = get_object_or_404(model, slug=self.kwargs[self.model])
        obj_set = getattr(obj, self.subobjects)
        return obj_set.all()[0].get_absolute_url()
