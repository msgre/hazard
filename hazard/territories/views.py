# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import DetailView, ListView, TemplateView
from django.http import Http404, HttpResponseRedirect
from django.template.defaultfilters import slugify

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
            districts = [{'label': i.title.replace(u'Okres ', u''), 'url': i.get_absolute_url(), 'category': u'Okres'} \
                         for i in District.objects.select_related().filter(**qs_kwargs)]
            towns = [{'label': i.title.replace(u'Obec ', u''), 'url': i.get_absolute_url(), 'category': u'Obec'} \
                     for i in Town.objects.select_related().filter(**qs_kwargs)]
            out.update({'data': regions + districts + towns})
        else:
            out.update({'data': []})
        return out

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({'mimetype': 'application/json'})
        return super(AutocompleteView, self).render_to_response(context, **response_kwargs)
