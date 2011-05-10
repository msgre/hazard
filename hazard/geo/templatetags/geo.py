# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def hell_numbers(entry):
    """
    Zobrazeni poctu protipravne provozovanych a celkoveho poctu evidovanych heren
    na uzemi obce.
    """
    bad = entry.dhell_count - entry.dok_hell_count
    return mark_safe(u'<span title="Počet heren v rozporu s §17">%.0f</span>/<span title="Počet evidovaných heren v obci">%.0f</span>' % (bad, entry.dhell_count))
