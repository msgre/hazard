# -*- coding: utf-8 -*-

import os

from django.db.models import get_apps, signals
from django.utils.importlib import import_module
from hazard.campaigns.models import Campaign


def update_campaings(app, created_models, **kwargs):
    """
    Projede adresare kazde instalovane aplikace a rozhlizi se po pritomnosti
    souboru campaign.py. Pokud jej nalezne, povazuje aplikaci za soucast
    kampani. Ucini zapis do modelu Campaign s udaji nalezenymi v souboru
    campaign.py, napr.:

        TITLE = u'VLT povolene Ministerstvem financi'
        SHORT_TITLE = u'VLT MF'
        SLUG = u'mf'
        DESCRIPTION = u'Data platna nekdy ke konci prazdnin 2011'
        ORDER = 100
    """
    # je aplikace soucasti nejake kampane?
    directory = os.path.dirname(app.__file__)
    if not os.path.exists(os.path.join(directory, 'campaign.py')):
        return

    # ano je, naimportujeme soubor campaign.py
    campaign_module_name = ".".join(app.__name__.split('.')[:-1])
    campaign_module_name = "%s.campaign" % (campaign_module_name, )
    campaign = import_module(campaign_module_name)

    # pokud zatim o kampani nemame v DB zadny zaznam, ulozime jej
    app_label = app.__name__.split('.')[-2]
    try:
        Campaign.objects.get(app=app_label)
    except Campaign.DoesNotExist:
        Campaign.objects.create(
            title       = campaign.TITLE,
            short_title = campaign.SHORT_TITLE,
            slug        = campaign.SLUG,
            description = campaign.DESCRIPTION,
            order       = campaign.ORDER,
            app         = app_label
        )


def update_all_campaigns(**kwargs):
    for app in get_apps():
        update_campaings(app, None, **kwargs)

signals.post_syncdb.connect(update_campaings)


if __name__ == "__main__":
    update_all_campaigns()
