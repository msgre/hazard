# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from hazard.campaigns.models import Campaign

register = template.Library()

TOP_CAMPAIGNS = 5

@register.inclusion_tag('campaigns/display_campaigns.tag.html')
def display_campaigns(campaigns=None):
    """
    Zobrazi seznam poslednich kampani.
    """
    if not campaigns:
        campaigns = Campaign.objects.all()[:TOP_CAMPAIGNS]
    return {'campaigns': campaigns}
