# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from django.core.urlresolvers import reverse

import ttag

register = template.Library()


class TerritoryBaseUrl(ttag.helpers.AsTag):
    """
    Generuje "bazove" URL pro danou geo oblast dle kontextovych promennych.
    Napr. v pripade mest najde v kontextu informaci o kraji, okresu i meste,
    a vytvori napr. /zlinsky/vsetin/valasske-mezirici/.
    V pripade, ze jsme na strance kraju pak v kontextu nachazi pouze kraj
    a generuje /zlinsky/.
    """

    def as_value(self, data, context):
        if 'town' in context:
            url = reverse('town', kwargs={
                'region': context['region'].slug,
                'district': context['district'].slug,
                'town': context['town'].slug,
            })
        elif 'district' in context:
            url = reverse('district', kwargs={
                'region': context['region'].slug,
                'district': context['district'].slug,
            })
        elif 'region' in context:
            url = reverse('region', kwargs={
                'region': context['region'].slug,
            })
        else:
            url = '/'

        return url

register.tag(TerritoryBaseUrl)
