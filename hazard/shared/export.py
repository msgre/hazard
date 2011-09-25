# -*- coding: utf-8 -*-
"""
Vygenerovani KML souboru ze zdrojove GDocs tabulky.

Tento skript navazuje na shared/spreadsheet.py
Na vstupu ocekava GDocs tabulku, ve ktere jsou pokud mozno co nejuplnejsi
informace o hernach (struktura tabulky viz shared/spreadsheet.py).
Ty prebira a do zadaneho vystupniho adresare generuje sadu KML souboru.

Co KML soubor, to jedno mesto, co zaznam to herna. Do poisku heren generuje
dodatecne informace o nazvu a poctu konkretnich typu automatu.


Pouziti
-------

./manage.py shell_plus

>>> from hazard.shared.export import make_kml_from_spreadsheet
>>> make_kml_from_spreadsheet('0AiH_kYn5i2nddDZ5dlZHSDdYRWFEUTRQaC1heTFaaEE')

GDocs dokument se zadava s pomoci jeho ID z URL, viz parametr key, napr.:

    https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDZ5RlZHSDdYRWFEUTRQaC1heTFaaEE&hl=en_US#gid=0

Zde key = 0AtH_kYn5iUnddDZ5RlZHSDdYRWFEUTRQaC1heTFaaEE


Konstanty v settings
--------------------

V settings.py je treba nastavit nasledujici konstanty:

* KML_OUTPUT_DIR -- absolutni cesta do adresare, do ktereho se maji ukladat
                    vygenerovane KMLka


TODO:
- option pro force zjistovani gps pozic i u radku, ktere ve sloupci nejakou
  hodnotu uz maji
"""

import os
import sys
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify, date
from django.contrib.auth.models import User

from hazard.shared.gdocs_common import *


# zkratky typu automatu
TYPE_LUT = {
    'emr': u'Elektromechanická ruleta',
    'vtz': u'Vícemístné hrací zařízení',
    'vhp': u'Výherní hrací přístroj',
    'vlt': u'Videoloterijní terminál',
    'ivt': u'Interaktivní videoloterijní terminál',
}


def update_places(row, places):
    """
    Do slovniku places generuje strukturu mesto -> ulice -> zaznam.
    """
    # mesto
    town = row[KEY_TOWN].strip()
    if type(town) == type(''):
        town = town.decode('utf-8')
    if town not in places:
        places[town] = {}

    # ulice
    street = row[KEY_STREET]
    street = street and street.strip() or ''
    if type(street) == type(''):
        street = street.decode('utf-8')

    # povedeme zaznam do places
    if street not in places[town]:
        # jmeno herny
        name = row[KEY_NAME]
        name = name and name.strip() or ''
        if type(name) == type(''):
            name = name.decode('utf-8')

        # poznamka k herne
        note = row[KEY_NOTE]
        note = note and note.strip() or ''
        if type(note) == type(''):
            note = note.decode('utf-8')

        # gps bod
        point = row[KEY_GPS].split(',') # TODO: casem asi budu muset obrnit vetsi toleranci na vstup, protoze do tabulek budou lidi vkladat data rucne
        point.append('0.000000')

        places[town][street] = {
            'counts': {},
            'title': street,
            'name': name,
            'note': note,
            'point': ','.join(point)
        }

    # typ automatu
    typ = row[KEY_TYPE]
    typ = typ and typ.strip() or u'Jiný'

    if typ not in places[town][street]['counts']:
        places[town][street]['counts'][typ] = 0

    # pocet automatu
    count = row[KEY_COUNT]
    count = count and count.strip().isdigit() and int(count.strip()) or 0
    places[town][street]['counts'][typ] += count


def update_description(places):
    """
    U kazdeho mesta/ulice doplni popis herny (ktery je slozen z nazvu herny
    a seznamu automatu, ktere se v herne provozuji).

    NOTE: nic nevraci, meni argument places.
    """
    for town in places:
        for street in places[town]:

            # pocty automatu
            total = sum(places[town][street]['counts'].values())
            if total == 1:
                machines = u'automat'
            elif total < 5:
                machines = u'automaty'
            else:
                machines = u'automatů'

            # uvodni veta
            name = places[town][street]['name']
            if name:
                intro = u'<p>Herna <b>"%s"</b>, celkem %i&nbsp;%s</p>' % (name, total, machines)
            else:
                intro = u'<p>Celkem %i&nbsp;%s</p>' % (total, machines)

            # seznam typu
            types = []
            for type in sorted(places[town][street]['counts'].keys()):
                if type.lower() in TYPE_LUT:
                    title = u'<abbr title="%s">%s</abbr>' % (TYPE_LUT[type.lower()], type)
                else:
                    title = type
                item = u"<li>%s: %i&nbsp;ks</li>" % (title, places[town][street]['counts'][type])
                types.append(item)

            # pripadna poznamka
            note = places[town][street]['note']
            note = note and u"\n<p>%s</p>" % note or u''

            # finalni popisek
            places[town][street]['description'] = u"%s\n<ul>\n%s</ul>%s" % (intro, "\n".join(types), note)


def process_spreadsheet(document_id):
    """
    Zpracuje zadanou GDocs tabulku -- vyzobne z ni vsechna data, rozdeli
    si zaznamy podle mest a ulic a vyslednou strukturu vrati ve slovniku.
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

        # zaznamy s neznamou pozici budeme ignorovat
        if not row[KEY_GPS] or row[KEY_GPS] == GPS_NOT_FOUND:
            sys.stderr.write('  No GPS position found, skipping...\n')
            continue

        # zaktualizujeme pocty automatu
        update_places(row, places)

    # zaktualizujeme description pro kazde pole
    update_description(places)

    return places


def export_kml(dirpath, places, description=None, overwrite=False):
    """
    Ze zadaneho slovniku places vygeneruje do adresare `dirpath` sadu KML
    souboru.

    Obsah `description` se prida k popisce dokumentu KML (popis celeho KML
    souboru). Pokud je argument `overwrite` True, pak pripadne existujici
    soubory ve vystupnim adresari prepise. V opacnem pripade konfliktnimu
    souboru prida nahodne vygenerovany suffix a data ulozi do nej.
    """

    for town in places:
        # cesta k vystupnimu souboru
        filename = "%s.kml" % slugify(town)
        filepath = os.path.join(dirpath, filename)

        # kontrola existence souboru
        if os.path.exists(filepath):
            if overwrite:
                sys.stderr.write('  File %s already exists, but we overwrite it.\n' % filepath)
            else:
                sys.stderr.write('  File %s already exists! Adding random suffix to filename...\n' % filepath)
                filepath = filepath.replace('.kml', '-%s.kml' % User.objects.make_random_password().lower())

        # spocitani celkoveho mnozstvi heren
        total = sum([sum(places[town][street]['counts'].values()) for street in places[town]])

        # popisek dokumentu
        description = description and u"%s\n" % description or u''
        main_description = u"""%s
* Celkový počet heren: %i
* Celkový počet automatů: %i

Mapa vytvořena dne: %s""" % (description, len(places[town]), total, date(datetime.now(), "j.n.Y v H:i:s"))

        # vytvoreni souboru
        f = open(filepath, 'w')
        context = {
            'main_title': u"Herny v obci %s" % town,
            'main_description': main_description,
            'entries': places[town]
        }
        out = render_to_string('shared/kml.html', context)
        f.write(out.encode('utf-8'))
        f.close()


def make_kml_from_spreadsheet(document_id, dirpath=None, overwrite=False):
    """
    Stahne data ze zadane GDocs tabulky, vygeneruje z ni sadu KML souboru
    a ulozi je do adresare dirpath (nebo settings.KML_OUTPUT_DIR).
    """
    places = process_spreadsheet(document_id)
    dirpath = dirpath or settings.KML_OUTPUT_DIR
    export_kml(dirpath, places, '', overwrite)
