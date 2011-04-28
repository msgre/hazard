# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re

from django import template
from django.utils import simplejson
from django.utils.safestring import mark_safe

register = template.Library()

FLOAT_AS_STRING_RE = re.compile(r'"(\d+(\.\d+))"')

@register.filter
def json(data, strip_str_floats=False):
    """
    Prevede vstupni data na JSON strukturu. Pokud je strip_str_floats pak
    se hledaji retezce ve tvaru "12.26576234" a prevadi se na 12.26576234
    """
    x = simplejson.dumps(data, separators=(',', ':'))
    if strip_str_floats:
        return mark_safe(FLOAT_AS_STRING_RE.sub(r"\1", x))
    else:
        return mark_safe(x)


LATLNG_RE = re.compile(r'(\[(\d+\.(\d+))|(\d+\.(\d+))\]|("(lat|lon)":\d+\.(\d+)))', re.M)
PRECISION = 6

def do_shorten_latlon(m):
    if m.group(2):
        return m.group(1).replace(m.group(3), m.group(3)[:PRECISION])
    elif m.group(4):
        return m.group(1).replace(m.group(5), m.group(5)[:PRECISION])
    elif m.group(6):
        return m.group(6).replace(m.group(8), m.group(8)[:PRECISION])

@register.filter
def shorten_latlon(text):
    """
    Filtr, ktery v zadanem textu (predpoklada se ze obsahem je JSON ve string
    podobe) pozkracuje lat/lng souradnice na max PRECISION desetinnych mist.

    Proc? Protoze lat/lon je ulozeno v podobe floatu, a ten ma tendenci byt
    prilis presny.
    """
    return LATLNG_RE.sub(do_shorten_latlon, text)
