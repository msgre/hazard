# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.views.generic import TemplateView

from hazard.mf.models import MfPlaceConflict
from hazard.territories.models import Region, District, Town


class MfAjax(TemplateView):
    """
    Vraci JSON informace o krajich/okresech.
    """
    template_name = 'mf/ajax.html'

    def get_context_data(self, **kwargs):
        out = super(MfAjax, self).get_context_data(**kwargs)
        out['statistics'] = MfPlaceConflict.statistics(None, group_by='region')
        if self.kwargs['type'] == 'kraje':
            out['json_details'] = dict([(i.id, i) for i in Region.objects.select_related().all()])
        elif self.kwargs['type'] == 'okresy':
            out['json_details'] = dict([(i.id, i) for i in District.objects.select_related().all()])
        else:
            out['json_details'] = dict([(i.id, i) for i in Town.objects.select_related().all()])
        return out

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({
            'mimetype': 'application/json'
        })
        return super(MfAjax, self).render_to_response(context, **response_kwargs)
