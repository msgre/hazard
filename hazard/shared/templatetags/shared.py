# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re
import os

from django import template
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.base import Node
from django.utils.html import strip_spaces_between_tags

import ttag

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
    return mark_safe(LATLNG_RE.sub(do_shorten_latlon, text))


FLOAT_RE = re.compile(r'(\d+\.)(\d+)', re.M)

@register.filter
def shorten_float(text, precision=3):
    """
    Hleda v zadanem textu "XX.YY" a zkracuje YY na zadanou presnost.
    """
    def do_shorten_float(m):
        return m.group(1) + m.group(2)[:precision]

    return mark_safe(FLOAT_RE.sub(do_shorten_float, text))


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

    return {'items': sorted(out, cmp=lambda a, b: dumb_czech_cmp(a, b)), 'MEDIA_URL': settings.MEDIA_URL}


@register.filter
def key(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def space2nbsp(value):
    return mark_safe(value.replace(u' ', u'&nbsp;'))


class Variable(ttag.helpers.AsTag):
    """
    Vlozi vyraz do kontextu sablony pod zadanym nazvem.

    Priklad:
        {% variable product_variants|numkey:form.variant_id.value as product_variant %}

        V kontextu se objevi promenna {{ product_variant }} jejiz obsah bude
        roven {{ product_variants|numkey:form.variant_id.value }}
    """
    expression = ttag.Arg()

    def output(self, data):
        return data['expression']

register.tag(Variable)


@register.filter
def grammar(count, variants):
    """
    Sklonovadlo.
    """
    variants = [[y.strip() for y in i.strip().split('=')] for i in variants.split(',')]
    variants = dict([(i[0] == '?' and i[0] or int(i[0]), i[1]) for i in variants])
    for k in sorted(variants.keys()):
        if k == '?':
            return variants[k]
        elif count <= k:
            return variants[k]


RE_QUOTE = re.compile(r'"')
RE_WHITECHARS = re.compile(r'>\s+')
RE_NEWLINES = re.compile(r'\n+')

class JSONItemNode(Node):
    child_nodelists = ('nodecontent', )

    def __init__(self, name, nodecontent): # pylint: disable-msg=W0231
        self.nodecontent = nodecontent
        self.name = name

    def __repr__(self):
        return "<JSONItem node>"

    def __iter__(self):
        for node in self.nodecontent:
            yield node

    def render(self, context):
        try:
            name = self.name.resolve(context)
        except VariableDoesNotExist:
            name = None

        # pokud se v GETu objevi parametr stejneho jmena jako nazev bloku,
        # pak se cela polozka NEBUDE generovat
        if name in context['request'].GET:
            return ''

        # TODO: mozna staci escapnout jen " , ne? mrdat ' nebo <> YES! je to strasne velke ted!
        content = self.nodecontent.render(context)
        content = strip_spaces_between_tags(content).strip()
        content = RE_WHITECHARS.sub('> ', content)
        content = RE_NEWLINES.sub(' ', content)
        content = RE_QUOTE.sub('\\"', content)
        if content.startswith('[') and content.endswith(']'):
            return mark_safe(u'"%s":%s' % (name, content))
        else:
            return mark_safe(u'"%s":"%s"' % (name, content))

def do_jsonitem(parser, token):
    """
    Pomocny tag pro generovani JSON odpovedi na AJAXove dotazy ve Scuku.

    Generuje jednu polozku do JSON struktury. Pouziti:

        {% jsonblock %}
            {% jsonitem "NAME" %}{% block NAME %}{% endblock %}{% endjsonitem %}
        {% endjsonblock %}

    Pokud se tento tag objevi v materske sablone, bude {% block %} naplnen
    skutecnym obsahem. {% jsonitem %} obsah escapuje a vygeneruje:

        "NAME": "OBSAH"

    Deje se zde ale jeste jedna specialitka. Protoze ruzne AJAX dotazy potrebuji
    ruzne podmnoziny dat z sablon, je mozne do GETu uvest nazvy bloku, ktere
    se NEMAJI do vystupu generovat. Pokud by tedy v nasem priklade byl AJAXovy
    dotaz podan jako /?NAME, pak tento tag vrati prazdny retezec.
    """
    name = parser.compile_filter(token.split_contents()[1])
    nodecontent = parser.parse(('endjsonitem', ))
    parser.delete_first_token()
    return JSONItemNode(name, nodecontent)
do_jsonitem = register.tag("jsonitem", do_jsonitem)


class JSONBlockNode(Node):
    child_nodelists = ('nodecontent', )

    def __init__(self, nodecontent): # pylint: disable-msg=W0231
        self.nodecontent = nodecontent

    def __repr__(self):
        return "<JSONBlock node>"

    def __iter__(self):
        for node in self.nodecontent:
            yield node

    def render(self, context):
        content = self.nodecontent.render(context).split(u'\n')
        out = u",".join([i.strip() for i in content if i.strip()])
        return mark_safe(u"{%s}" % out)

def do_jsonblock(parser, token):
    """
    Pomocny tag pro generovani JSON odpovedi na AJAXove dotazy ve Scuku.

    Jednotlive JSON polozky slouci do bloku. Napr.:

        {% jsonblock %}
            {% jsonitem "NAME1" %}{% block NAME1 %}{% endblock %}{% endjsonitem %}
            {% jsonitem "NAME2" %}{% block NAME2 %}{% endblock %}{% endjsonitem %}
        {% endjsonblock %}

    Prevede do:

        {"NAME1":"OBSAH1","NAME2":"OBSAH2"}

    Konkretne se stara o to, ze vyradi prazdne {% jsonitem %} polozky, da pryc
    nepotrebne bile znaky, prida carky na konce polozek a vse to obali do {}.
    """
    nodecontent = parser.parse(('endjsonblock', ))
    parser.delete_first_token()
    return JSONBlockNode(nodecontent)
do_jsonblock = register.tag("jsonblock", do_jsonblock)
