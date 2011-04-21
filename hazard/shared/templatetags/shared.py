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
