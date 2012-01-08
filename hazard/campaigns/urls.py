# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import os

from django.conf.urls.defaults import *
from django.db.models import get_apps

from hazard.campaigns.views import CampaignHomepageView


def get_campaing_urls():
    """
    Priradi dynamicky URL pravidla pro vysvetleni kampani.

    Facha to tak, ze se sniffuje obsah kazdeho adresare s aplikaci, a pokud
    se v ni naleznou soubory "campaign.py" a "urls_campaign.py", tak se priradi
    do URL pravidel.

    Timto zpusobem je mozne pro kazdou kampan definovat specificka view,
    a pouhym vytvorenim 2 vyse zminenych souboru je zaradit do celeho mapoveho
    "frameworku".
    """
    campaign_urls = [
        url(r'^$', CampaignHomepageView.as_view(), name="campaign-homepage"),
    ]

    for app in get_apps():
        directory = os.path.dirname(app.__file__)
        if not os.path.exists(os.path.join(directory, 'campaign.py')) or \
           not os.path.exists(os.path.join(directory, 'urls_campaign.py')):
            continue

        app_label = app.__name__.split('.')[-2]
        campaign_urls.append(url(
            r'^(?P<campaign>%s)/' % app_label,
            include('hazard.%s.urls_campaign' % app_label)
        ))

    return patterns('', *campaign_urls)


urlpatterns = get_campaing_urls()
