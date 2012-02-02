# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import TemplateView

from hazard.mf.models import MfPlaceConflict
from hazard.territories.models import Region, District, Town


class MfCommonAjax(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({
            'mimetype': 'application/json'
        })
        return super(MfCommonAjax, self).render_to_response(context, **response_kwargs)


class MfAjax(MfCommonAjax):
    """
    Vraci JSON informace o krajich/okresech.

    TODO: saham do sablon, mozna to bude mit dusledky i zde...
    """
    template_name = 'mf/ajax.html'

    def get_context_data(self, **kwargs):
        out = super(MfAjax, self).get_context_data(**kwargs)
        if self.kwargs['type'] == 'kraje':
            out['json_details'] = dict([(i.id, i) for i in Region.objects.select_related().all()])
        elif self.kwargs['type'] == 'okresy':
            out['json_details'] = dict([(i.id, i) for i in District.objects.select_related().all()])
            out['detailed_output'] = 'detailni' in self.request.GET
            if out['detailed_output']:
                statistics = MfPlaceConflict.statistics(None, group_by='district')

                # regroup
                # puvodni tvar
                #   parameter1:
                #       id: value
                # novy tvar
                #   slug:
                #       type:
                #           parameter2: value
                district_lut = dict(District.objects.all().values_list('id', 'slug'))
                parameter_lut = {
                    'hell_counts': 'counts',
                    'machine_counts': 'counts',
                    'conflict_hell_counts': 'conflict_counts',
                    'conflict_machine_counts': 'conflict_counts',
                    'conflict_hell_perc': 'conflict_perc',
                    'conflict_machine_perc': 'conflict_perc',
                }
                regrouped = {}
                for parameter in statistics:
                    for id in statistics[parameter]:
                        slug = district_lut[id]
                        if slug not in regrouped:
                            regrouped[slug] = {}
                        type = 'hell_' in parameter and 'hells' or 'machines'
                        if type not in regrouped[slug]:
                            regrouped[slug][type] = {}
                        if parameter not in parameter_lut:
                            continue
                        _parameter = parameter_lut[parameter]
                        regrouped[slug][type][_parameter] = statistics[parameter][id]

                out['statistics'] = regrouped

        return out


class MfTownAjax(MfCommonAjax):
    """
    Ajaxova JSON odpoved pro mesta je obsahlejsi. Krome dat o mestech obsahuje
    udaje o okresech.
    """
    template_name = 'mf/ajax_town.html'

    def get_context_data(self, **kwargs):
        out = super(MfTownAjax, self).get_context_data(**kwargs)

        # udaje o mestech okresu
        json_details = dict([(i.id, i) for i in Town.objects.select_related().filter(district__slug=self.kwargs['district'])])
        statistics = MfPlaceConflict.statistics(District.objects.get(slug=self.kwargs['district']), group_by='town')

        # vytahneme zakladni udaje o okresech
        districts = dict([(i.id, {'slug': i.slug, 'title': i.title, 'url': i.get_absolute_url(), 'shape': i.shape.coords}) \
                          for i in District.objects.select_related().all()])

        # doplnime do slovniku okresu statisticke udaje
        district_statistics = MfPlaceConflict.statistics(None, group_by='district')
        for district_id in districts:
            data = {}
            for k in district_statistics:
                data[k] = district_statistics[k][district_id]
            districts[district_id].update({'statistics': data})

        # zjistime extremy ve statistikach okresu
        extrems = {}
        for k in district_statistics:
            values = district_statistics[k].values()
            extrems[k] = {
                'min': min(values),
                'max': max(values)
            }

        # sup do kontextu
        out.update({
            'json_details': json_details,
            'statistics': statistics,
            'districts': districts,
            'extrems': extrems
        })

        return out
