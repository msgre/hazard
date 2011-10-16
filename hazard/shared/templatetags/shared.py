# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re
import os

from django import template
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.conf import settings

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


KML_NAME_RE = re.compile(r'<name>Herny v obci ([^<]+)</name>')
CZECH_ALPHABET = list(u'aábcčdďeéěfghiíjklmnňoóprřsštťuúůvwxyýzž')

def dumb_czech_cmp(a, b):
    a = a[0].decode('utf-8')
    b = b[0].decode('utf-8')
    for i in range(min([len(a), len(b)])):
        a1 = a[i].lower()
        a1 = a1 in CZECH_ALPHABET and CZECH_ALPHABET.index(a1) + 1 or 1000
        b1 = b[i].lower()
        b1 = b1 in CZECH_ALPHABET and CZECH_ALPHABET.index(b1) + 1 or 1000
        ret = cmp(a1, b1)
        if ret != 0:
            return ret
    return -1 and len(a) < len(b) or 1

@register.inclusion_tag('shared/show_kml_list.html')
def show_kml_list():
    """
    Projede obsah adresare KML_OUTPUT_DIR, vyparsuje z kazdeho KML souboru
    nazev obce a zobrazi dlouhy seznam obci s odkazy na KML data.
    """
    out = []

    for filename in os.listdir(settings.KML_OUTPUT_DIR):
        path = os.path.join(settings.KML_OUTPUT_DIR, filename)
        if os.path.isdir(path):
            continue
        f = open(path)
        content = f.read(300)
        f.close()
        name = KML_NAME_RE.search(content)
        if not name:
            continue
        out.append((name.group(1), filename))

    return {'items': sorted(out, cmp=lambda a, b: dumb_czech_cmp(a, b))}
