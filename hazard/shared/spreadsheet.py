# -*- coding: utf-8 -*-
"""
Doplneni GPS pozice do GDocs tabulek.

Tento skript vznikl z potreby doplnit do dat z MF geo pozice (a nasledne je
pridat do MapHazardu). Normalne lidi mapy kresli interaktivne mysi, ale tady
jsme najednou meli 50.000 radkovou tabulku, kterou urcite nikdo prekreslovat
nebude. Tak proto...


Pouziti
-------

./manage.py shell_plus

>>> from hazard.shared.spreadsheet import update_gdocs_gps
>>> update_gdocs_gps('0AiH_kYn5i2nddDZ5dlZHSDdYRWFEUTRQaC1heTFaaEE')

GDocs dokument se zadava s pomoci jeho ID z URL, viz parametr key, napr.:

    https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDZ5RlZHSDdYRWFEUTRQaC1heTFaaEE&hl=en_US#gid=0

Zde key = 0AtH_kYn5iUnddDZ5RlZHSDdYRWFEUTRQaC1heTFaaEE


Vstup & specifikace
-------------------

Vstupem je GDocs tabulka, ktera ma nasledujici sloupce:

* Obec
* Ulice
* Typ činnosti
* Číslo jednací
* Počet
* Název herny
* Poznámka
* GPS

(pokud by se poradi nahodou zmenilo, je mozne upravit konstantu GDOCS_COLUMNS)

Dale je potreba dodrzet:

* v prvnim radku a sloupci uvest o jaka data jde (z kama pochazi, datum ke kteremu
  jsou platna, apod)
* druhy radek musi byt popisky sloupcu; MUSI byt vyplneny (viz predpokladana
  struktura vyse)
* na tretim radku zacinaji data; povinna pole jsou Obec a Ulice

S takovouto tabulkou umi skript pracovat a dokaze do sloupce GPS doplnit
lat/lon pozici odpovidajici adrese z prvnich dvou sloupcu. Pokud GPS pozici
nedokaze zjistit (napr. adresa je neuplna), pak do sloupce doplni retezec
"nenalezeno".


Konstanty v settings
--------------------

V settings.py je treba nastavit nasledujici konstanty:

* GDOCS_USERNAME -- uzivatelske jmeno do Google Docs
* GDOCS_PASSWORD -- heslo do Google Docs
* GDOCS_COLUMNS -- poradi sloupcu v GDocs tabulkach

Konstanta GDOCS_COLUMNS musi obsahovat retezce, ktere odpovidaji nazvum
KEY_* konstant v gdocs_common.py. Napr. konstante KEY_TOWN odpovida hodnota
"town" (KEY_ se zahazuje a zbytek se prevede na lowercase).


TODO:
- option pro force zjistovani gps pozic i u radku, ktere ve sloupci nejakou
  hodnotu uz maji
"""

import sys

from hazard.geo.geocoders.google import geocode
from hazard.shared.gdocs_common import *


def get_address(row, places):
    """
    Vytahne z radku mesto a ulici, a k ni zjisti GPS pozici (pokud ji nema
    v cache, tak ji vytahne online pres Google Geocode).
    """
    # vytahneme si mesto..
    town = row[KEY_TOWN].strip()
    if type(town) == type(''):
        town = town.decode('utf-8')
    if town not in places:
        places[town] = {}

    # ..vytahneme si ulici a pokusime se zjistit gps pozici
    street = row[KEY_STREET]
    if street and street.strip():
        if type(street) == type(''):
            street = street.decode('utf-8')
    else:
        street = u''
    q = u'%s, %s' % (street, town)
    if street not in places[town]:
        sys.stdout.write('  Geocode: Looking for "%s"\n' % q)
        json = geocode(q, '')
        try:
            gps = json['Placemark'][0]['Point']['coordinates'][:-1]
            gps = ",".join([str(i) for i in gps])
            sys.stdout.write('    Position found! (%s)\n' % gps)
        except (KeyError, IndexError):
            sys.stderr.write('    Position for address "%s" not found!\n' % q)
            gps = None
        places[town][street] = gps # lng/lat
    else:
        sys.stdout.write('  Geocode: Address "%s" already in cache\n' % q)
        gps = places[town][street]

    return town, street, gps


def update_gps(client, document_id, row_idx, gps):
    """
    Aktualizuje radek s GPS pozici v Google Docs tabulce.
    """
    # aktualizujeme zaznam v Google Docs tabulce
    upd_row_idx = row_idx + 2
    if not gps:
        gps = GPS_NOT_FOUND
    updated = client.UpdateCell(upd_row_idx, GPS_COLUMN_IDX, gps, document_id)
    return isinstance(updated, gdata.spreadsheet.SpreadsheetsCell)


def update_gdocs_gps(document_id, force_update=False):
    """
    Doplni do sloupce GPS v GDocs tabulce geografickou pozici herny
    (zjistenou ze sloupcu mesto a ulice).

    TODO: lepsi popis
    """
    places = {} # kes mest, ulic a GPS pozic
    gd_keys = None # nazvy s spravne poradi sloupcu v GDocs tabulce

    # otevreme dokument
    client, feed = open_spreadsheet(document_id)

    # projdeme radek po radku
    for row_idx, entry in enumerate(feed.entry):
        sys.stdout.write('Processing row #%i\n' % row_idx)

        if row_idx == 0:
            # vyzobnem si nazvy realnych klicu a jejich poradi v google docs tabulce
            sys.stdout.write('  Evaluating correct order of GDocs columns...\n')
            gd_keys = get_column_order(entry)
            continue

        # namapujeme GD radek na slovnik, at se nam s tim lepe dela
        row = map_to_dict(entry, gd_keys, REAL_COLUMNS)
        if row[KEY_GPS] and row[KEY_GPS].strip() and not force_update:
            sys.stdout.write('  GPS column in current row is already evaluated (%s)\n' % row[KEY_GPS])
            continue
        elif row[KEY_GPS] and row[KEY_GPS].strip():
            sys.stdout.write('  GPS column in current row is already evaluated (%s), but we will force update it.\n' % row[KEY_GPS])

        # zjistime pozici herny
        town, street, gps = get_address(row, places)

        # aktualizujeme zaznam v Google Docs tabulce
        sys.stdout.write('  Updating GDocs row...\n')
        if not update_gps(client, document_id, row_idx, gps):
            sys.stderr.write('  Problem with updating GDocs row #%i (town "%s", street "%s")\n' % (upd_row_idx, town, street))
