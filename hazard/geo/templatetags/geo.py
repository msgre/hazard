# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re

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


URL_HL_RE = re.compile(r'hl=\w{2}')
URL_OUTPUT_RE = re.compile(r'output=[^&]+')

@register.filter
def kml_to_www(url):
    """
    Upravi odkaz na KML odkaz tak, aby vedl na konkretni www stranku do
    Moje mapy.
    """
    url = URL_HL_RE.sub('hl=cs', url)
    url = URL_OUTPUT_RE.sub('', url)
    return url

@register.filter
def prohibitted_hells(entry):
    """
    Vrati pocet heren, ktere lezi na zakazanych mistech.
    """
    return entry.dhell_count - entry.dok_hell_count
