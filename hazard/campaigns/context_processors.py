# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from hazard.campaigns.models import Campaign

def campaigns(request):
    return {
        'campaigns': Campaign.objects.all()
    }
