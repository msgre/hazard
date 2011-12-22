# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from django.core.urlresolvers import reverse

import ttag

register = template.Library()


@register.inclusion_tag('mf/mf_primer_text.html', takes_context=True)
def mf_primer_text(context, obj, type):
    """
    TODO:
    """
    geo = obj.__class__.__name__.lower()
    if geo == 'town':
        prefix = 'obci'
        detail_title = ''
        subobjects = None
    elif geo == 'district':
        prefix = 'okrese'
        detail_title = 'obcích okresu'
        subobjects = obj.town_set.all()
    else:
        prefix = 'kraji'
        detail_title = 'okresech kraje'
        subobjects = obj.district_set.all()
    context.update({
        'prefix': prefix,
        'detail_title': detail_title,
        'hells': type == 'hells',
        'obj': obj,
        'subobjects': subobjects
    })
    return context


@register.inclusion_tag('mf/mf_table.html', takes_context=True)
def mf_table(context, area, type):
    """
    Generuje tabulku s pocty heren ci automatu v dane oblasti.
    """
    context.update({
        'area': area,
        'type': type,
        'actual_object': context[area]
    })

    if area == 'region':
        context['objects'] = context['regions']
        context['object_title'] = u'Kraj'
    elif area == 'district':
        context['objects'] = context['districts']
        context['object_title'] = u'Okres'
    else:
        context['objects'] = dict([(i.id, i) for i in context['district'].town_set.select_related().all()])
        context['object_title'] = u'Obec'

    if type == 'hells':
        context['counts'] = context['statistics']['hell_counts']
        context['conflict_counts'] = context['statistics']['conflict_hell_counts']
        context['conflict_perc'] = context['statistics']['conflict_hell_perc']
        context['type_title'] = u'heren'
        context['density'] = context['statistics']['hell_density']
        context['per_resident'] = context['statistics']['hell_per_resident']
    else:
        context['counts'] = context['statistics']['machine_counts']
        context['conflict_counts'] = context['statistics']['conflict_machine_counts']
        context['conflict_perc'] = context['statistics']['conflict_machine_perc']
        context['type_title'] = u'automatů'
        context['density'] = context['statistics']['machine_density']
        context['per_resident'] = context['statistics']['machine_per_resident']

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

register.tag(MfTableUrl)