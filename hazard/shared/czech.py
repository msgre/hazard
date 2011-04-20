# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from re import sub

CZ_ASCII = {
    u'č': u'c', u'ě': u'e', u'á': u'a', u'í': u'i', u'é': u'e', u'ň': u'n',
    u'ť': u't', u'ř': u'r', u'ž': u'z', u'ý': u'y', u'ú': u'u', u'ů': u'u',
    u'š': u's', u'ó': u'o', u'ď': u'd', u'ü': u'u', u'ń': u'n', u'ŕ': u'r',
    u'Č': u'C', u'Ě': u'E', u'Á': u'A', u'Í': u'I', u'É': u'E', u'Ň': u'N',
    u'Ť': u'T', u'Ř': u'R', u'Ž': u'Z', u'Ý': u'Y', u'Ú': u'U', u'Ů': u'U',
    u'Š': u'S', u'Ó': u'O', u'Ď': u'D', u'Ü': u'U', u'Ń': u'N', u'Ŕ': u'R'
}
CZ_UPPER = {
    u'č': u'Č', u'ě': u'Ě', u'á': u'Á', u'í': u'Í', u'é': u'É', u'ň': u'Ň',
    u'ť': u'Ť', u'ř': u'Ř', u'ž': u'Ž', u'ý': u'Ý', u'ú': u'Ú', u'ů': u'Ů',
    u'š': u'Š', u'ó': u'Ó', u'ď': u'Ď', u'ü': u'Ü', u'ń': u'Ń', u'ŕ': u'Ŕ'
}
CZ_LOWER = {
    u'Č': u'č', u'Ě': u'ě', u'Á': u'á', u'Í': u'í', u'É': u'é', u'Ň': u'ň',
    u'Ť': u'ť', u'Ř': u'ř', u'Ž': u'ž', u'Ý': u'ý', u'Ú': u'ú', u'Ů': u'ů',
    u'Š': u'š', u'Ó': u'ó', u'Ď': u'ď', u'Ü': u'ü', u'Ń': u'ń', u'Ŕ': u'ŕ'
}



def translate(value, lookup):
    """
    Prelozi zadany retezec podle dodaneho slovniku.
    Pomocna fce.
    """
    out = value
    for char, repl in lookup.iteritems():
        if char in value:
            out = out.replace(char, repl)
    return out


def to_ascii(value):
    """
    Odstrani z textu cesky znaky s diakritikou (nahradi je
    za znaky bez znamenek).
    """
    return translate(value, CZ_ASCII)


def slugify(value):
    """
    Vyrobi ze zadane hodnoty slug (poradi si i s ceskymi znaky).
    """
    out = to_ascii(value)
    out = sub(r'[^a-zA-Z0-9 \t\n\r\f\v]', u' ', out).strip().lower()
    return sub(r'\s+', u'-', out)


def lower(value):
    """
    Lowerstring zadaneho parametr value.
    """
    return translate(value, CZ_LOWER).lower()


def upper(value):
    """
    Upperstring zadaneho parametr value.
    """
    return translate(value, CZ_UPPER).upper()


def capitalize(value):
    """
    Prevede prvni pismeno v retezci na velke.
    """
    if not len(value):
        return value
    return upper(value[0]) + value[1:]
