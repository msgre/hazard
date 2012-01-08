# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
TODO: neodzkouseno!

Import ministerskych heren.
"""

import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.gis.measure import D

from hazard.gobjects.utils import ImporterBase
from hazard.territories.models import Region, District, Town, Zip, Address
from hazard.mf.models import MfPlace, MfPlaceType
from hazard.gobjects.models import Hell, MachineType, MachineCount


class HellImporter1(ImporterBase):
    """
    Trida pro import dat o hernach povolenych Ministerstvem financi.

    Zdrojova data pochazi z XLS, resp. GDocs tabulky, kterou jsme rozdelili
    na 4 mensi casti a pres Google Geocode doplnili lokace jednotlivych heren,
    viz:

        https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDZ5RlZHSDdYRWFEUTRQaC1heTFaaEE&hl=en_US#gid=0
        https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDRhV1JrUGxmdWlSYjEtTi1mLXRORUE&hl=en_US#gid=0
        https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDZiUkFiM0hTOFFUUWladW91djFRbmc&hl=en_US#gid=0
        https://docs.google.com/spreadsheet/ccc?key=0AtH_kYn5iUnddDZJekktVjhhXzJuU0RfblN4V193d3c&hl=en_US#gid=0

    Pouziti
    Je vhodne nejprve importovat vsechna data o mistech, viz PlaceImporter1
    (importem se do DB dostanou uzitecne informace o uzemnich celcich a adresach).
    Pak staci zavolat:

        from hazard.mf.management.commands.import_places1 import HellImporter1
        a = HellImporter1('../data/herny_ministerstvo_1.csv')
        a.run()
        a = HellImporter1('../data/herny_ministerstvo_2.csv')
        a.run()
        a = HellImporter1('../data/herny_ministerstvo_3.csv')
        a.run()
        a = HellImporter1('../data/herny_ministerstvo_4.csv')
        a.run()

    CSV data maji nasledujici sloupce:

    * Obec
    * Ulice
    * Typ činnosti (EMR, IVT, VTZ, ostatní §50/3)
    * Číslo jednací (napr. 34/79228/2008)
    * Počet
    * Název herny (vzdy prazdne)
    * Poznámka (vzdy prazdne)
    * GPS (lng,lat)

    Jedna herna muze byt zaznamenana i na vice radku, protoze kazdy radek
    reprezentuje konkretni povoleni na provoz automatu.

    Poznamka:
    Muze se stat, ze pro konkretni obec nemame v DB zaznam. Data nejsou zatim
    normovana, a v nazvu obce muze byt pouzita nejaka zkratka ci ciselny pridavek,
    a razem nevime kde hernu zaradit.
    V techto pripadech se provadi geolookup, kdy hledame co nejblizsi mesto/ulici
    vuci pozici herny.
    """

    def __init__(self, stdout, source, town_radius={'km': 1}, address_radius={'m': 250}):
        self.town_radius = town_radius
        self.address_radius = address_radius
        self.stdout = stdout
        self.source = source
        self.missing = []

    def run(self):
        if not self.check_source():
            return
        self.load_csv_source(['town', 'street', 'type', 'number', 'count', 'name', 'note', 'gps'])
        self.process()
        if self.missing:
            self.log('Skipping %i row(s) due missing GPS or unknown address' % (len(self.missing),))

    def process(self):
        total = len(self.data)

        for idx, item in enumerate(self.data):
            self.log('%i / %i' % (idx + 1, total))
            qs = Town.objects.filter(title=item['town'])

            if not qs.exists():
                # pokud nemame GPS pozici, nemuzeme dal nic delat
                if 'gps' not in item or item['gps'] == 'nenalezeno':
                    self.log('Skipping row %i due missing GPS' % (idx + 1,))
                    self.missing.append(idx)
                    continue

                # zkusime udelat geo lookup
                gps = [float(i.strip()) for i in item['gps'].split(',')] # lng/lat
                point = Point(gps[0], gps[1], srid=4326)
                qs = Town.objects.filter(point__isnull=False, point__distance_lte=(point, D(**self.town_radius))).distance(point).order_by('distance')
                if qs.exists():
                    self.log(u'Geo lookup found near town (count=%i), first is %s, distance=%s' % (len(qs), qs[0], qs[0].distance))
                    town = qs[0]
                else:
                    qs = Address.objects.filter(point__isnull=False, point__distance_lte=(point, D(**self.address_radius))).distance(point).order_by('distance')
                    if qs.exists():
                        self.log(u'Geo lookup found near addresses (count=%i), first is %s, distance=%s' % (len(qs), qs[0], qs[0].distance))
                        town = qs[0].town
                    else:
                        self.log('Address was not found, row %i' % (idx, ))
                        self.missing.append(idx)
                        continue
            else:
                town = qs[0]

            # ulozime zaznam do DB
            if town:
                self.save(item, town)

    def save(self, item, town):
        # najdeme adresu
        if 'gps' not in item or item['gps'] == 'nenalezeno':
            return False
        gps = [float(i.strip()) for i in item['gps'].split(',')] # lng/lat
        address = self.get_address(
            gps[0], gps[1], item['street'], town
        )
        if not address:
            return False

        # najdeme/vytvorime hernu
        hell, _ = Hell.objects.get_or_create(
            title   = item['street'].strip(),
            address = address
        )

        # zaneseme pocet automatu v herne
        mtype, _ = MachineType.objects.get_or_create(
            title = item['type'].strip().upper()
        )
        count, _ = MachineCount.objects.get_or_create(
            hell  = hell,
            type  = mtype,
            count = int(item['count']),
            note  = u'Číslo jednací: %s' % (item['number'],)
        )


class Command(BaseCommand):
    """
    Custom command pro import ministerskych heren.

    Pouziti:
        ./manage.py import_hells1 ../data/herny_ministerstvo_1.csv
        ./manage.py import_hells1 ../data/herny_ministerstvo_2.csv
        ./manage.py import_hells1 ../data/herny_ministerstvo_3.csv
        ./manage.py import_hells1 ../data/herny_ministerstvo_4.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Import heren povolenych Ministerstvem Financi.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s hernami.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = HellImporter1(self.stdout, filename)
        importer.run()
