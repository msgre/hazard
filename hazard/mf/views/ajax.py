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
    """
    template_name = 'mf/ajax.html'

    def get_context_data(self, **kwargs):
        out = super(MfAjax, self).get_context_data(**kwargs)
        if self.kwargs['type'] == 'kraje':
            out['json_details'] = dict([(i.id, i) for i in Region.objects.select_related().all()])
            out['statistics'] = MfPlaceConflict.statistics(None, group_by='region')
        elif self.kwargs['type'] == 'okresy':
            out['json_details'] = dict([(i.id, i) for i in District.objects.select_related().all()])
            out['statistics'] = MfPlaceConflict.statistics(None, group_by='district')
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
