# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
TODO:
http://code.google.com/intl/cs-CZ/apis/kml/documentation/kmlreference.html

TODO:
- napsat manage.py command pro dump geoRSS (zadam csv, vyplivne georss)
- napsat manage.py command dump/load konkretniho entry v podobe Python struktury
  (bez DB ID), kterou bude mozne nahrat na server bez toho, aniz by se dely
  zbesilosti typu pocitani konfliktu pro kazdy vlozeny polygon
"""

import time
import csv
import pickle
from datetime import datetime

from hazard.geo.geocoders.google import geocode


def read_csv(filename, recipe, infinite_last=False):
    """
    Nacte zadany CSV soubor a kazdy radek v nem prevede na slovnik (nazvy
    klicu/sloupecku jsou definovany v `recipe`). Pokud se posledni sloupecek
    v tabulce opakuje do "nekonecna" (napr. v tabulce s budovami muze je 4 az
    n-ty sloupec gps souradnice), musi se nastavit parametr `infinite_last` na
    True, a do vystupniho slovniku se pak generuji klice slozene z posledniho
    klice z recipe+index (napr. 'gps1', 'gps2', atd).

    Oddelovacem bunek musi byt znak ",", bunky musi byt ohraniceny mezi
    dvojitymi uvozovkami.
    """
    out = []
    rows = csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
    for row in rows:
        row = [i.strip() for i in row]
        if len([i for i in row if i]) == 0:
            continue
        if not infinite_last:
            item = dict(zip(recipe, row[:len(recipe)]))
        else:
            _recipe1 = recipe[:-1]
            item = dict(zip(_recipe1, row[:len(_recipe1)]))
            _recipe2 = [recipe[-1]] * (len(row) - len(_recipe1))
            _recipe2 = ["%s%i" % (i, idx + 1) for idx, i in enumerate(_recipe2)]
            if _recipe2:
                item.update(dict(zip(_recipe2, row[len(_recipe1):])))

        # prevedeme retezce na utf-8
        for k in item.keys():
            item[k] = item[k].decode('utf-8')
        out.append(item)
    return out


def normalize_gps(data):
    """
    Prevede klice s gps souradnicemi (budto jediny item['gps']='49,12312, 16,2332',
    nebo sadu item['gps1'], item['gps2'], ...) na seznam slovniku:

    item['gps'] = [{'lat': 49.2232, 'lng': 16.223}, ...]
    """
    def parse_gps(row):
        out = row.copy()
        if 'gps1' in out:
            # zaznam s budovou, zadna, jedna nebo vice gps souradnic
            gps = []
            for i in range(len(row.keys())):
                key = 'gps%i' % i
                if key in out and out[key].strip():
                    delimiter = ',' if '.' in out[key] else ', '
                    gps.append(dict(zip(['lat', 'lng'], [i.strip() for i in out[key].split(delimiter)])))
                if key in out:
                    del out[key]
            out['gps'] = gps
        else:
            # zaznam s hernou, jedina gps pozice
            if out['gps'].strip():
                delimiter = ',' if '.' in out['gps'] else ', '
                out['gps'] = [dict(zip(['lat', 'lng'], [i.strip() for i in out['gps'].split(delimiter)]))]
            else:
                out['gps'] = []

        # prevedeme gps souradnice na floaty
        out['gps'] = [{'lat': float(i['lat'].replace(',', '.')), 'lng': float(i['lng'].replace(',', '.'))} for i in out['gps']]
        return out

    return [parse_gps(i) for i in data]


def get_missing_position(data, town):
    """
    Dohleda GPS pozici pro ta data, ktere maji v CSV tabulce uvedenu jen adresu.
    """
    out = []
    for item in data:
        if item['gps']:
            # GPS souradnice jsou zadany uz ve vstupnich CSV datech
            out.append(item)
            continue

        # GPS souradnice nebyly zadany, zkusime to je zjistit pres Google
        time.sleep(1)
        q = u'%s, %s' % (item['street'], town)
        print 'Looking for geo location for %s' % q
        json = geocode(q, '') # TODO: API key
        try:
            location = json['Placemark'][0]['Point']['coordinates'][:-1]
            location = dict(zip(['lng', 'lat'], location))
        except (KeyError, IndexError):
            location = None
        if not location:
            print "  Sorry, location wasn't found"
            continue

        # GPS pozice se nasla
        item['gps'] = [location]
        out.append(item)

    return out

def import_data(filename, recipe, town, infinite_last=False):
    """
    Nahraje CSV soubor, rozpasuje jej, prevede GPS pozice na lat/lng slovnik
    a u tech zaznamu, kterym GPS pozice chybi ji prostrednictvim Google Geocode
    zjisti.
    """
    out = read_csv(filename, recipe, infinite_last)
    out = normalize_gps(out)
    return get_missing_position(out, town)


GEORSS_CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
  xmlns:georss="http://www.georss.org/georss">
  <title>%(title)s</title>
  <updated>%(created)s</updated>
  %(entries)s
</feed>"""
GEORSS_ENTRY = """<entry>
    <title>%(title)s</title>
    <summary>%(description)s</summary>
    %(type)s
  </entry>"""
GEORSS_POINT = "<georss:point>%s</georss:point>"
GEORSS_POLY = "<georss:polygon>%s</georss:polygon>"

def build_georss(data, title):
    """
    Vytvori ze zadanych dat GeoRSS strukturu, kterou lze nasledne importovat
    do Google maps.
    """
    entries = []
    for item in data:
        # vytvoreni popisku
        description = []
        if 'name' in item:
            # budova
            description = [item['street'], item['type']]
            if item['street']:
                description.append(u'<em>%s</em>' % item['street'])
            if item['type']:
                description.append(item['type'])
        else:
            # herna
            if item['type']:
                description.append(u'Typ herny: %s' % item['type'])
            if item['count']:
                description.append(u'Počet hracích automatů: %s' % item['count'])
        description = u"<![CDATA[<p>%s</p>]]>" % '<br>'.join(description)

        mask = GEORSS_POLY if item['gps'] and len(item['gps']) > 1 else GEORSS_POINT
        entry = GEORSS_ENTRY % {
            'title': item['name'] if 'name' in item else item['street'],
            'description': description,
            'type': mask % " ".join(["%(lat)s %(lng)s" % i for i in item['gps']])
        }
        entries.append(entry)
    return GEORSS_CONTAINER % {
        'title': title,
        'created': datetime.now(),
        'entries': "\n".join(entries)
    }


# --------------

def _neco():
    herny = import_data('../brno_herny.csv', ['street', 'type', 'count', 'gps', 'note'], 'Brno')
    budovy = import_data('../brno_budovy.csv', ['type', 'name', 'street', 'gps'], 'Brno', True)

    output = open('budovy.pkl', 'wb')
    pickle.dump(budovy, output)
    output.close()

    output = open('herny.pkl', 'wb')
    pickle.dump(heryny, output)
    output.close()

def neco():
    def x(filename):
        f = open(filename, 'rb')
        out = pickle.load(f)
        f.close()
        return out

    data = x('budovy.pkl')
    print build_georss(data, u'Budovy v Brně')
    # print '******************************'
    # data = x('herny.pkl')
    # print build_georss(data, u'Herny v Brně')

neco()
