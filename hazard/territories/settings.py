# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.conf import settings

# urcuje, jestli necha uzivatele na "raw" URL geo oblasti (napr. /zlinsky/
# nebo /zlinsky/vsetin/), nebo jej presmeruje na defaultni kampan
REDIRECT_TO_DEFAULT_CAMPAIGN = getattr(settings, 'REDIRECT_TO_DEFAULT_CAMPAIGN', True)
