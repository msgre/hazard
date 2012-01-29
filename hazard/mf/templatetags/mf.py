# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from django.core.urlresolvers import reverse

import ttag

register = template.Library()


@register.inclusion_tag('mf/mf_primer_text.html', takes_context=True)
def mf_primer_text(context, obj):
    """
    Generuje uvodni text se zakladnimi informacemi o poctech a procentech
    heren/automatu v dane oblasti.
    """
    geo = obj.__class__.__name__.lower()
    prefix = 'neco dlouheho a nesmyslneho'
    if geo == 'town':
        detail_title = ''
        subobjects = None
    elif geo == 'district':
        detail_title = 'obcích okresu'
        subobjects = obj.town_set.all()
        prefix = 'Obec'
    else:
        detail_title = 'okresech kraje'
        subobjects = obj.district_set.all()
        prefix = 'Okres'
    context.update({
        'detail_title': detail_title,
        'obj': obj,
        'prefix': prefix,
        'subobjects': subobjects,
        'geo': geo
    })
    return context

@register.inclusion_tag('mf/mf_primer_text.html', takes_context=True)
def old_mf_primer_text(context, obj):
    """
    Generuje uvodni text se zakladnimi informacemi o poctech a procentech
    heren/automatu v dane oblasti.
    """
    geo = obj.__class__.__name__.lower()
    prefix = 'neco dlouheho a nesmyslneho'
    if geo == 'town':
        detail_title = ''
        subobjects = None
    elif geo == 'district':
        detail_title = 'obcích okresu'
        subobjects = obj.town_set.all()
        prefix = 'Obec'
    else:
        detail_title = 'okresech kraje'
        subobjects = obj.district_set.all()
        prefix = 'Okres'
    context.update({
        'detail_title': detail_title,
        'obj': obj,
        'prefix': prefix,
        'subobjects': subobjects,
        'geo': geo
    })
    return context

@register.inclusion_tag('mf/mf_table.html', takes_context=True)
def mf_table(context, area):
    """
    Generuje tabulku s pocty heren ci automatu v dane oblasti.
    """
    context.update({
        'actual_object': context[area],
        'parent_class': {}
    })

    if area == 'region':
        context['objects'] = context['regions']
        context['object_title'] = u'Kraj'
    elif area == 'district':
        context['objects'] = context['districts']
        context['object_title'] = u'Okres'
        context['parent_class'] = dict([(i.id, 'region_%s' % i.region.slug) for i in context['districts'].values()])
    else:
        context['objects'] = dict([(i.id, i) for i in context['district'].town_set.select_related().all()])
        context['object_title'] = u'Obec'

    # premapovani statistickych informaci pod jine klice
    # TODO: kua, tohle by se mohlo dit uz ve view, ale neni ted cas to resit
    context['statistics']['hells'] = {
        'counts': context['statistics']['hell_counts'],
        'conflict_counts': context['statistics']['conflict_hell_counts'],
        'conflict_perc': context['statistics']['conflict_hell_perc']
    }
    context['statistics']['machines'] = {
        'counts': context['statistics']['machine_counts'],
        'conflict_counts': context['statistics']['conflict_machine_counts'],
        'conflict_perc': context['statistics']['conflict_machine_perc']
    }

    return context


class MfTableUrl(ttag.helpers.AsTag):
    """
    Pomocny tag pro generovani URL z tabulky {% mf_table %}.

    Jde o to, ze {% mf_table %} je obecny kus kodu, ktery se pouziva pro
    vykreslovani statistickych tabulek pro kraje, okresy i mesta. Abych se
    vyhnul slozitym podminkam v sablone, napsal jsem tento tag, ktery usnadnuje
    generovani URL na tu spravnou geografickou oblast.
    """
    obj = ttag.Arg()

    def as_value(self, data, context):

        data = self.resolve(context)
        obj = data['obj']
        type = obj.__class__.__name__.lower()

        if type == 'region':
            url = reverse('mf-region', kwargs={
                'region': obj.slug,
                'campaign': 'mf'
            })
        elif type == 'district':
            url = reverse('mf-district', kwargs={
                'region': context['regions'][obj.region_id].slug,
                'district': obj.slug,
                'campaign': 'mf'
            })
        else:
            url = reverse('mf-town', kwargs={
                'region': context['regions'][obj.region_id].slug,
                'district': context['districts'][obj.district_id].slug,
                'town': obj.slug,
                'campaign': 'mf'
            })

        return url


@register.inclusion_tag('mf/mf_toplist.html', takes_context=True)
def mf_toplist(context, statistics, geo, key, title):
    """
    TODO:
    """
    context.update({
        'statistics': statistics,
        'geo': geo,
        'key': key,
        'title': title
    })
    return context


@register.filter
def remove_str(value, substr):
    """
    Odstrani z retezce value substr (nahradi jej za '').
    """
    return unicode(value).replace(substr, '').strip()

register.tag(MfTableUrl)
