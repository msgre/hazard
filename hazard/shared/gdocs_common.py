# -*- coding: utf-8 -*-
"""
Spolecne konstanty a funkce pro praci s GDocs tabulkami.

Podrobnejsi info viz shared/spreadsheet.py a shared/export.py
"""

import gdata.spreadsheet.service

from django.conf import settings


# sloupce v tabulce, se kterymi pocitame
KEY_TOWN = 'mesto'
KEY_STREET = 'ulice'
KEY_TYPE = 'typ cinnosti'
KEY_NUMBER = 'cislo jednaci'
KEY_COUNT = 'pocet'
KEY_NAME = 'nazev herny'
KEY_NOTE = 'poznamka'
KEY_GPS = 'gps'

# poradi sloupci v tabulce
REAL_COLUMNS = [globals()["KEY_%s" % k.upper()] for k in settings.GDOCS_COLUMNS]

# retezec, ktery se vklada do sloupce GPS pokud se pozice nepodari nalezt
GPS_NOT_FOUND = 'nenalezeno'


def open_spreadsheet(document_id):
    """
    Otevre Google Docs tabulku a vrati tuple:

    * objekt client pro dalsi praci nad dokumentem
    * feed jednotlivych radku
    """
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.ClientLogin(settings.GDOCS_USERNAME, settings.GDOCS_PASSWORD)
    return client, client.GetListFeed(document_id)


def get_column_order(entry):
    """
    Feed ma neprijemnou vlastnost a to tu, ze jednotlive sloupce vraci v
    predem neznamem poradi (je to slovnik). Nastesti je ale mozne z pole
    entry.content.text poradi rozpoznat.

    Tato funkce vrati seznam klicu, ktere odpovidaji jednotlivym sloupcum,
    v tom poradi, v jakem se v dokumentu nachazi.
    """
    positions = []
    for key in entry.custom.keys():
        pos = entry.content.text.decode('utf-8').find(u"%s:" % key)
        positions.append((key, pos))
    return [i[0] for i in sorted(positions, cmp=lambda a, b: cmp(a[1], b[1]))]


def map_to_dict(entry, key_order, real_columns):
    """
    Namapuje radek z Google Docs tabulky do slovniku, jehoz klice odpovidaji
    realite (v Google Docs tabulce nemusi byt radek s vyznamem jednotlivych
    sloupcu, proto je zadavan explicitne z vnejsku).

    Vraci slovnik s hodnotami.
    """
    out = {}

    # nejprve ponastavujeme co skutecne v radku je (muze to byt podmnozina
    # real_columns)
    for idx, key in enumerate(key_order):
        value = entry.custom.get(key, None)
        value = value and value.text or None
        real_key = real_columns[idx]
        out[real_key] = value

    # doplneni chybejicich klicu
    for key in set(real_columns).difference(out.keys()):
        out[key] = None

    return out
