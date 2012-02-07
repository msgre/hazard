# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Import ministerskych heren.
"""

import sys
import math
import re
import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.gis.measure import D

from hazard.gobjects.utils import ImporterBase
from hazard.territories.models import Region, District, Town, Zip, Address
from hazard.mf.models import MfPlace, MfPlaceType
from hazard.gobjects.models import Hell, MachineType, MachineCount
from hazard.campaigns.models import Campaign


class MfHellImporter(ImporterBase):
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

        from hazard.mf.management.commands.import_places1 import MfHellImporter
        a = MfHellImporter('../data/herny_ministerstvo_1.csv')
        a.run()
        a = MfHellImporter('../data/herny_ministerstvo_2.csv')
        a.run()
        a = MfHellImporter('../data/herny_ministerstvo_3.csv')
        a.run()
        a = MfHellImporter('../data/herny_ministerstvo_4.csv')
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

    def __init__(self, stdout, source, town_radius={'km': 1}, address_radius={'m': 250}, no_counter=False):
        self.town_radius = town_radius
        self.address_radius = address_radius
        self.stdout = stdout
        self.source = source
        self.suffix = os.path.splitext(os.path.basename(source))[0].split('_')[-1]
        self.no_counter = no_counter
        self.campaign = Campaign.objects.get(slug='mf')
        towns = [
            (ur'Brno-.+', u'Obec Brno'),
            (ur'Havířov-.+', u'Obec Havířov'),
            (ur'Liberec-Vratislavice nad Nisou', u'Obec Liberec'),
            (ur'Mariánské hory a Hulváky', u'Obec Ostrava'),
            (ur'Moravská Ostrava a Přívoz', u'Obec Ostrava'),
            (ur'Ostrava-.+', u'Obec Ostrava'),
            (ur'Pardubice .+', u'Obec Pardubice'),
            (ur'Plzeň .+', u'Obec Plzeň'),
            (ur'Praha .+', u'Obec Praha'),
            (ur'Praha-.+', u'Obec Praha'),
            (ur'Ústí n.L. .+', u'Obec Ústí nad Labem'),
            (ur'Ústí nad Labem .+', u'Obec Ústí nad Labem'),
            (ur'Ústí nad Labem-.+', u'Obec Ústí nad Labem'),
        ]
        self.town_lut = []
        for i in towns:
            self.town_lut.append({
                'regexp': re.compile(i[0]),
                'town': Town.objects.get(title=i[1])
            })

    def run(self):
        if not self.check_source():
            return
        self.load_csv_source(['town', 'street', 'type', 'number', 'count', 'name', 'note', 'gps'])
        self.process()

    def process(self):
        if not self.data:
            return

        total = len(self.data)
        radius = {}
        RADIUS_MULTIPLIER = 2

        for idx, item in enumerate(self.data):
            if not self.no_counter:
                self.log('%i / %i' % (idx + 1, total))
            bid = u'-'.join(['hell', self.suffix, str(idx)])

            # nejdrive pokus na prvni dobrou...
            town = Town.objects.filter(title=u'Obec %s' % item['town'])
            town_count = town.count()
            visible = True

            if town_count == 1:
                # yes! idealni pripad, je jen jedna obec takoveho jmena...
                town = town[0]

            elif town_count > 1:
                # komplikace
                # obci stejneho jmena je vic, musime nejak poznat, ktera je ta nase
                p1 = self.get_point(item)
                if not p1:
                    self.log('[BID:%s] There is more than one %s town but due to missing GPS position we are unable to find the right one; skipping this record' % (bid, item['town']))
                    continue
                closest_town = town.distance(p1, field_name='point').order_by('distance')[0]
                if closest_town.id not in radius:
                    radius[closest_town.id] = math.sqrt(closest_town.surface * 10000 / math.pi)
                if closest_town.distance.m > radius[closest_town.id] * RADIUS_MULTIPLIER:
                    # ha! nejblizsi nalezena obec je nejak daleko od stredu obce
                    # to je divne, radeji tento zaznam o uradu vyradime
                    visible = False
                    self.log('[BID:%s] There is more than one %s town; closest of them is %02f kilometres from center; we will hide this record' % (bid, item['town'], closest_town.distance.km))
                    town = closest_town
                else:
                    # nasli jsme
                    town = closest_town
            else:
                # obec se nenasla

                # zkusime mrknout do pomocneho regexp seznamu, jestli nejde
                # o nejake zmrsene jmeno obce
                for i in self.town_lut:
                    if i['regexp'].search(item['town']):
                        town = i['town']
                        break

                # pokud nejde, tak tady asi toho uz moc nenadelame
                if not town:
                    self.log('[BID:%s] Unknown town: %s' % (bid, item['town'], ))
                    continue

            # posledni kontrola, jestli nalezena obec neni nejak moc,
            # daleko od zjistene GPS pozice zaznamu
            if town:
                if town.id not in radius:
                    radius[town.id] = math.sqrt(town.surface * 10000 / math.pi)
                p1 = self.get_point(item)
                if not p1:
                    self.log('[BID:%s] Due to missing GPS position we are unable to check relevancy of this record; we take it, blindly... (sere pes rulez)' % (bid, ))
                else:
                    if visible is None:
                        visible = Town.objects.filter(point__distance_lte=(p1, D(m=radius[town.id] * RADIUS_MULTIPLIER)), id=town.id).exists()
                        if not visible:
                            self.log('[BID:%s] Municipal adress of %s is far away from center of the town (we will hide this record)' % (bid, item['town'], ))

            # ulozime zaznam do DB
            if town:
                self.save(item, bid, town, visible)

    def get_point(self, item):
        if 'gps' not in item or item['gps'] == 'nenalezeno':
            return None
        gps = [float(i.strip()) for i in item['gps'].split(',')] # lng/lat
        return Point(gps[0], gps[1], srid=4326)

    def save(self, item, bid, town, visible):
        # najdeme adresu
        if 'gps' not in item or item['gps'] == 'nenalezeno':
            return False
        gps = [float(i.strip()) for i in item['gps'].split(',')] # lng/lat
        address = self.get_address(
            gps[0], gps[1], item['street'], town
        )
        if not address:
            self.log('[BID:%s] Unable to create address for %s %s; record was not saved!' % (bid, item['street'], item['town']))
            return False

        # najdeme/vytvorime hernu
        hell, _ = Hell.objects.get_or_create(
            title   = item['street'].strip(),
            address = address,
            visible = visible
        )
        hell.campaigns.add(self.campaign)

        # zaneseme pocet automatu v herne
        mtype, _ = MachineType.objects.get_or_create(
            title = item['type'].strip().upper()
        )
        count, created = MachineCount.objects.get_or_create(
            hell  = hell,
            type  = mtype,
            count = int(item['count']),
        )
        if created:
            count.json = {'number': u'Číslo jednací: %s' % (item['number'],), 'bid': bid}
            count.save()


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

    option_list = BaseCommand.option_list + (
        make_option('--no-counter',
            dest='no_counter',
            action="store_true",
            help=u'Vypne vypisovani pocitadla zpracovanych zaznamu.'),
    )

    def handle(self, *args, **options):
        if not args:
            if self.stdout:
                msg = 'Zadej cestu k CSV souboru s hernami.'
                self.stdout.write(u'%s\n' % msg.strip())
            sys.exit(1)

        # parametry pro importer
        filename = args[0]
        importer_kwargs = {
            'no_counter': options['no_counter']
        }

        # spusteni importu
        importer = MfHellImporter(self.stdout, filename, **importer_kwargs)
        importer.run()
