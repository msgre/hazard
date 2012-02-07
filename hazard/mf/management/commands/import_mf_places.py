# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Import dat, zakoupenych Matejem v listopadu 2011.
"""

import sys
import math
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.gis.measure import D

from hazard.gobjects.utils import ImporterBase
from hazard.territories.models import Region, District, Town, Zip, Address
from hazard.mf.models import MfPlace, MfPlaceType


class MfPlaceImporter(ImporterBase):
    """
    Trida pro import dat, ktere Matej koupil koncem listopadu 2011.
    Ziskali jsme sadu XLS tabulek, kde byly zakladni informace, ale bez GPS
    pozic.

    Data jsem exportoval do CSV, rozrezal a behem cca 2 dnu pres Google Geocode
    zjistil potrebne pozice. Vysledky jsem ulozil do picklose, a s nim
    se tady dale pracuje.

    Pouziti:

        from hazard.mf.management.commands.import_places1 import MfPlaceImporter
        a = MfPlaceImporter('../data/budovy3.pickle')
        a.run()

    Pripadne

        a = MfPlaceImporter('../data/budovy3.pickle', ignore_types=['obce'])
        a.run()
        b = MfPlaceImporter('../data/budovy3.pickle', include_types=['obce'])
        b.run()

    Poznamky:

    Puvodne jsme data importovali tak, ze behem natahovani dat se zaroven
    budovala hiearchie kraj->okres->obec. Nebylo to ale dobre, vznikla nam
    spousta nesmyslnych zaznamu (napr. obec radici se do konkretniho okresu,
    ale geo pozici mela na opacnem konci republiky). Cast problemu urcite
    souvisi s tim, ze geocoding provedeny pres Google neni 100% a vraci
    na dotazy nemale mnozstvi chybnych souradnic. Na jeho obranu je ale nutne
    poznamenat, ze nase vstupni data taky nejsou moc kvalitni. S vyjimkou
    obci totiz nevime, pro jake mesto je zaznam minen. V tabulkach je totiz
    informace o poste, ne o obci (takze google mohl byt z naseho dotazu
    zmaten a vracel nesmysly).

    Lepsi strategii se zda opacny pristup. Nejprve jsme z FreeGeodataCZ dat
    naimportovali kraje->okresy->mesta a do nich teprve koupena data o budovach.

    Format:

    Pickle data jsou trojity slovnik:

    * prvni klic je typ mista ('skoly', 'ministerstvo', apod.)
    * druhy klic je INT, interni ID zaznamu (spolecne s prvnim klicem tvori
      jedinecny identifikator, napr. 'skoly-123')
    * hodnotou je slovnik, kde jednotlive klice odpovidaji sloupcum XLS tabulek;
      je zde drobna anomalie -- zaznamy pro 'obce' maji jinou strukturu
      dat nez vsechno ostatni (takto to bylo v XLS)

    Format dat pro obce:
        {'gps': [{'lat': 50.1737275, 'lng': 14.5562814}],
         'id': 10,
         'phone': u'283 932 290',
         'post': u'Mratin',
         'street': u'Hlavni 160, Velec',
         'town': u'Velec',
         'type': 'obce',
         'zip': u'250 63'}

    Format dat:
        {'district': u'Obvod Praha 1',
         'gps': [{'lat': 50.0790212, 'lng': 14.4172211}],
         'id': 10,
         'post': u'Praha 1',
         'region': u'Hlavni mesto Praha',
         'street': u'Klemencova 179/12',
         'title1': u'Masarykova stredni skola chemicka,',
         'title2': u'Praha 1, Klemencova 12',
         'type': 'skoly',
         'zip': u'11000'}
    """

    def __init__(self, stdout, source, include_types=[], ignore_types=[], no_counter=False):
        self.stdout = stdout
        self.source = source
        self.include_types = include_types
        self.ignore_types = ignore_types
        self.no_counter = no_counter

    def run(self):
        """
        Zpracuje zadany picklos a ulozi data z nej do DB.
        """
        if not self.check_source():
            return
        self.load_pickle_source()
        self.process()

    def process(self):
        """
        Zpracuje data z picklose.
        """
        if not self.data:
            return

        radius = {}
        RADIUS_MULTIPLIER = 2
        RADIUS_MULTIPLIER2 = 0.9

        for tidx, type in enumerate(self.data):

            # nemame nahodou tento zaznam preskocit?
            if type in self.ignore_types or (self.include_types and type not in self.include_types):
                self.log('Skipping type %s' % (type,))
                continue

            type_size = len(self.data[type])
            for iidx, id in enumerate(self.data[type]):

                if not self.no_counter:
                    self.log('%s: %i / %i' % (type, iidx + 1, type_size))
                item = self.data[type][id]
                bid = u'-'.join([type, str(id)])
                visible = None

                if type == 'obce':
                    # nejdrive pokus na prvni dobrou...
                    town = Town.objects.filter(title=u'Obec %s' % item['town'])
                    town_count = town.count()

                    if town_count == 1:
                        # yes! idealni pripad, je jen jedna obec takoveho jmena...
                        town = town[0]

                    elif town_count > 1:
                        # komplikace
                        # obci stejneho jmena je vic, musime nejak poznat, ktera je ta nase
                        p1 = Point(item['gps'][0]['lng'], item['gps'][0]['lat'], srid=4326)
                        closest_town = town.distance(p1, field_name='point').order_by('distance')[0]
                        if closest_town.id not in radius:
                            radius[closest_town.id] = math.sqrt(closest_town.surface * 10000 / math.pi)
                        if closest_town.distance.m > radius[closest_town.id] * RADIUS_MULTIPLIER2:
                            # ha! nejblizsi nalezena obec je nejak daleko od stredu obce
                            # to je divne, radeji tento zaznam o uradu vyradime
                            visible = False
                            self.log('[BID:%s] There is more than one %s town; closest of them is %i metres from center; we will hide it' % (bid, item['town'], closest_town.distance.m))
                            town = closest_town
                        else:
                            # nasli jsme
                            town = closest_town
                    else:
                        # obec se nenasla
                        # NOTE: zkousel jsem realizovat nejaky pomocny algoritmus,
                        # ktery by obec nasel podle PSC ci posty, ale nema to cenu;
                        # jde o jednotky zaznamu, ve kterych je ale stejne problem,
                        # protoze se nevyskytuji v ofiko seznamu obci (asi je nase
                        # databaze obecnich uradu nejaka zastarala)
                        self.log('[BID:%s] Unknown town: %s, %s, post %s' % (bid, item['town'], item['zip'], item['post']))
                        continue

                    # posledni kontrola, jestli nalezena obec neni nejak moc,
                    # daleko od zjistene GPS pozice zaznamu
                    if town:
                        if town.id not in radius:
                            radius[town.id] = math.sqrt(town.surface * 10000 / math.pi)
                        p1 = Point(item['gps'][0]['lng'], item['gps'][0]['lat'], srid=4326)
                        if visible is None:
                            visible = Town.objects.filter(point__distance_lte=(p1, D(m=radius[town.id] * RADIUS_MULTIPLIER2)), id=town.id).exists()
                            if not visible:
                                self.log('[BID:%s] Municipal adress of %s (%s, %s) is far away from center of the town (we will hide this address)' % (bid, item['town'], item['zip'], item['post']))

                    # ulozeni
                    self.save_obec(item, bid, town, bool(visible))

                else:
                    # zkusime obec nalezt nejprve podle nazvu posty (bo to mame v datech)
                    zip = Zip.objects.filter(post=item['post']).order_by('-town__population')
                    if not zip.exists():
                        # pokud se to nepodari, zkusime najit presne PSC
                        zip = Zip.objects.filter(title=Zip.normalize(item['zip'])).order_by('-town__population')
                    if not zip.exists():
                        # pokud se ani to nepodari, zkusime najit obec podle jejiho jmena a fragmentu PSC
                        town = self.find_town(item)
                        if not town:
                            # pokud se ani to nepodari, zkusime nazev obce rozbit podle mezer a -
                            # a hledat trosku naslepo podle neuplneho jmena obce
                            parts = [i.strip() for i in item['post'].replace('-', ' ').split(' ') if i.strip()]
                            if parts[0].lower() in u'malá malý malé velká velký velké stará starý staré nová nový nové'.split(u' '):
                                parts[0] = u' '.join(parts[:2])
                            town = self.find_town(item, parts[0])
                    else:
                        town = zip[0].town

                    if not town:
                        self.log('[BID:%s] %s (PSC %s) not found' % (bid, item['post'], item['zip']))
                        continue

                    # kontrola vzdalenosti od stredu obce
                    # NOTE: u kazde obce mam informaci o vymere v hektarech;
                    # tu si idealizuji na kruh, a z nej vypocitam polomer v metrech
                    # pokud je bod dal nez RADIUS_MULTIPLIER nasobek teto vzdalenosti,
                    # tak ho udelame neviditelnym
                    if town.id not in radius:
                        radius[town.id] = math.sqrt(town.surface * 10000 / math.pi)
                    p1 = Point(item['gps'][0]['lng'], item['gps'][0]['lat'], srid=4326)
                    p1 = p1.transform(102065, True)
                    p2 = town.point.transform(102065, True)
                    d = p1.distance(p2)
                    visible = d <= radius[town.id] * RADIUS_MULTIPLIER

                    # ulozeni
                    self.save_non_obec(item, bid, town, visible)

    def find_town(self, item, partial=None):
        """
        Snazi se nalezt mesto, nejdrive podle nazvu a kdyz se to nepovede,
        tak podle PSC cisla.
        """
        if not partial:
            towns = Town.objects.filter(title=u"Obec %s" % item['post'])
        else:
            towns = Town.objects.filter(title__startswith=u"Obec %s" % partial)
        towns_count = towns.count()
        if towns_count > 1:
            # mame problem, mest se stejnym nazvem jsme nasli vic...
            # zkusime najit to prave tak, ze si pro kazde z mest vytahneme
            # vsechna PSC, a budeme s nimi porovnavat PSC v item['zip'].
            # ten kod, ktery se nejvice podoba item['zip'] (podoba == nejdelsi
            # shoda cislic od zacatku), je nas
            best_match = {}
            for town in towns:
                zips = town.zip_set.all()
                if zips.count() == 0:
                    # ha, zrada! nektera z obci nema vubec PSC cisla; tak balime
                    # kufry, tady to algoritmem nevyresime (nemuzeme srovnavat
                    # neco s nicim, a pak vratit bezelstne neco jako best match)
                    best_match = None
                    break
                else:
                    for zip in zips:
                        ratio = 0
                        for idx in range(len(item['zip'])):
                            if item['zip'][idx] != zip.title[idx]:
                                break
                            else:
                                ratio += 1
                        if not best_match or best_match['ratio'] < ratio:
                            best_match['ratio'] = ratio
                            best_match['zip'] = zip
            if best_match and best_match['ratio'] > 0:
                town = best_match['zip'].town
            else:
                town = None
        elif towns_count == 0:
            # zadana obec se vubec nenasla
            town = None
        else:
            # idealni pripad -- mesto zadaneho jmena je v DB jedinkrat, tak
            # to proste musi byt ono...
            town = towns[0]

        return town

    def save_obec(self, item, bid, town, visible):
        """
        Ulozeni zaznamu o obci.
        """
        # adresa
        address = self.get_address(
            item['gps'][0]['lng'],
            item['gps'][0]['lat'],
            item['street'],
            town
        )

        # zaznam o miste
        place_type, _ = MfPlaceType.objects.get_or_create(
            title = item['type'].strip()
        )
        title = u"Úřad obce %s" % (town.title,)
        place, created = MfPlace.objects.get_or_create(
            title   = title,
            address = address,
            type    = place_type,
            bid     = bid,
            visible = visible
        )
        if created:
            place.json = {'phone': item['phone'], 'post': item['post']}
            place.save()

    def save_non_obec(self, item, bid, town, visible):
        """
        Ulozeni zaznamu pro ostatni zaznamy (skoly, ministerstva, apod.)
        """
        # adresa
        address = self.get_address(
            item['gps'][0]['lng'], item['gps'][0]['lat'], item['street'], town
        )

        # zaznam o miste
        place_type, _ = MfPlaceType.objects.get_or_create(
            title = item['type'].strip()
        )
        title = u" ".join([item['title1'].strip(), item['title2'].strip()])
        place, _ = MfPlace.objects.get_or_create(
            title   = title.strip(),
            address = address,
            type    = place_type,
            bid     = bid,
            visible = visible
        )


class Command(BaseCommand):
    """
    Custom command pro import zakoupenych dat z listopadu 2011.

    Pouziti:
        # doporuceny postup -- obce az nakonec
        ./manage.py import_buildings1 ../data/budovy3.pickle --ignore=obce
        ./manage.py import_buildings1 ../data/budovy3.pickle --include=obce

        # nedoporucovany postup -- natazeni vseho najednou
        ./manage.py import_buildings1 ../data/budovy3.pickle
    """
    args = u'<cesta-k-pickle-souboru>'
    help = u'Import zakoupenych dat z listopadu 2011. Behem importu je mozne zadat, ktere typy mist se maji/nemaji natahnout. Seznam mist: zdravi, cirkev, skoly, obce, lekarny, ministerstvo.'

    option_list = BaseCommand.option_list + (
        make_option('--include',
            dest='include',
            help=u'Definuje konkretni jednotlive typy, ktere se maji importovat. Jednotlive typy se pisou za sebou jako retezec, oddelovacem je carka. Napr. "obce,leky".'),
        make_option('--ignore',
            dest='ignore',
            help=u'Definuje typy, ktere se nemaji importovat. Jednotlive typy se pisou za sebou jako retezec, oddelovacem je carka. Napr. "obce,leky".'),
        make_option('--no-counter',
            dest='no_counter',
            action="store_true",
            help=u'Vypne vypisovani pocitadla zpracovanych zaznamu.'),
    )

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k pickle souboru s budovami.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]
        importer_kwargs = {}
        if options['ignore']:
            importer_kwargs['ignore_types'] = [i.strip() for i in options['ignore'].split(',') if i.strip()]
        if options['include']:
            importer_kwargs['include_types'] = [i.strip() for i in options['include'].split(',') if i.strip()]
        importer_kwargs['no_counter'] = options['no_counter']

        # kontrola ze nebylo zadano oboji
        if 'ignore_types' in importer_kwargs and 'include_types' in importer_kwargs:
            if self.stdout:
                msg = 'Nemuzes zadat oba parametry (--ignore a --include). Bud nezadavej nic, nebo jen jeden z nich.\n'
                self.stdout.write(u'%s\n' % msg.strip())
            sys.exit(1)

        # spusteni importu
        importer = MfPlaceImporter(self.stdout, filename, **importer_kwargs)
        importer.run()
