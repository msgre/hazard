# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Import dat, zakoupenych Matejem v listopadu 2011.
"""

import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify

from hazard.gobjects.utils import ImporterBase
from hazard.territories.models import Region, District, Town, Zip, Address
from hazard.mf.models import MfPlace, MfPlaceType


class PlaceImporter1(ImporterBase):
    """
    Trida pro import dat, ktere Matej koupil koncem listopadu 2011.
    Ziskali jsme sadu XLS tabulek, kde byly zakladni informace, ale bez GPS
    pozic.

    Data jsem exportoval do CSV, rozrezal a behem cca 2 dnu pres Google Geocode
    zjistil potrebne pozice. Vysledky jsem ulozil do picklose, a s nim
    se tady dale pracuje.

    Pouziti:
    Je vhodne nejprve importovat vse s vyjimkou obci, a teprve pote pouze obce.
    Jde o to, ze data pro obce obsahuji nejmene dat (neni u nich uveden okres
    a kraj). Kdyz se naimportuje nejdrive vse ostatni, jsem pak schopen s
    pomoci PSC najit kde asi obec lezi, ikdyz zatim v DB ulozena neni.

        from hazard.mf.management.commands.import_places1 import PlaceImporter1
        a = PlaceImporter1('../data/budovy3.pickle', ignore_types=['obce'])
        a.run()
        b = PlaceImporter1('../data/budovy3.pickle', include_types=['obce'])
        b.run()

    TODO:
        pred nactenim obci by bylo dobre provest import z fusion tabulek
        teprem nakonec obce
        no a na uplny konec pak updatnout zaznamy z fusion (korekce gramatiky, populace, apod)

    Format:
    Pickle data jsou trojity slovnik:

    * prvni klic je typ mista ('skoly', 'ministerstvo', apod.)
    * druhy klic je INT, interni ID zaznamu (spolecne s prvnim klicem tvori
      jedinecny identifikator, napr. 'skoly-123')
    * hodnotou je slovnik, kde jednotlive klice odpovidaji sloupcum XLS tabulek;
      je zde drobna anomalie -- zaznamy pro 'obce' maji jinou strukturu
      dat nez vsechno ostatni (takto to bylo v XLS)

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

    Format dat pro obce:
        {'gps': [{'lat': 50.1737275, 'lng': 14.5562814}],
         'id': 10,
         'phone': u'283 932 290',
         'post': u'Mratin',
         'street': u'Hlavni 160, Velec',
         'town': u'Velec',
         'type': 'obce',
         'zip': u'250 63'}
    """

    def __init__(self, stdout, source, include_types=[], ignore_types=[]):
        self.stdout = stdout
        self.source = source
        self.include_types = include_types
        self.ignore_types = ignore_types
        self.missing_buildings = []

    def run(self):
        """
        Zpracuje zadany picklos a ulozi data z nej do DB.
        """
        if not self.check_source():
            return
        self.load_pickle_source()
        self.process()
        if self.missing_buildings:
            for i in self.missing_buildings:
                bid = u'-'.join([i['type'], str(i['id'])])
                self.log(bid)

    def process(self):
        """
        Zpracuje data z picklose.
        """
        if not self.data:
            return

        for tidx, type in enumerate(self.data):

            # nemame nahodou tento zaznam preskocit?
            if type in self.ignore_types or (self.include_types and type not in self.include_types):
                self.log('Skipping type %s' % (type,))
                continue

            type_size = len(self.data[type])
            for iidx, id in enumerate(self.data[type]):

                self.log('%s: %i / %i' % (type, iidx + 1, type_size))
                item = self.data[type][id]
                bid = u'-'.join([type, str(id)])

                # ulozeni do DB
                if type == 'obce':
                    town = self.get_town(item)
                    if town:
                        self.save_obec(item, town, bid)
                    else:
                        self.missing_buildings.append(item)
                else:
                    self.save_non_obec(item, bid)

    def get_town(self, item):
        """
        Zjisti mesto, do ktereho zaznam o miste patri.

        Tato metoda se pouziva pouze pri importu mist. Problem je v tom,
        ze mesto v DB nemusi existovat a zaznamy o obci nemaji informaci
        o okresu/kraji.
        """
        code = Zip.normalize(item['zip'])
        town = Town.objects.filter(title=item['town'].strip())
        if not town.exists():
            # mesto neexistuje
            zzip = Zip.objects.filter(title=code)
            if zzip.exists():
                # ...ale existuje PSC kod, podle ktereho najdeme i mesto
                town = zzip[0].town
            elif item['town'] and code:
                # ...ale ve zdrojovoych datech mame informaci o PSC a meste
                # zkusime najit orientacne okres
                district = self.guess_district(code)
                if district:
                    # okres jsme nasli, zalozime tedy nove mesto
                    town = Town.objects.create(
                        title    = item['town'].strip(),
                        slug     = slugify(item['town'].strip()),
                        district = district
                    )
                    zzip = Zip.objects.create(
                        title = code,
                        town  = town
                    )
                else:
                    town = None
            else:
                town = None
        else:
            if town.count() > 1:
                zzip = Zip.objects.filter(town__title=item['town'], title=code)
                if zzip.exists():
                    town = zzip[0].town
                else:
                    town = town[0]
            else:
                town = town[0]
        return town

    def guess_district(self, code):
        """
        Uhadne okres, do ktereho spada PSC `code`.
        """
        # ufikneme posledni cislici z PSC a zkusime najit v DB shodu
        zip = Zip.objects.filter(title__startswith=code[:-1])
        if zip.exists():
            return zip[0].town.district
        else:
            return False

    def save_obec(self, item, town, bid):
        """
        Ulozeni zaznamu o obci.
        """
        # adresa
        point = Point(item['gps'][0]['lng'], item['gps'][0]['lat'], srid=4326)
        address = Address.objects.create(
            title = item['street'].strip(),
            town  = town,
            slug  = slugify(item['street'].strip()),
            point = point
        )

        # zaznam o miste
        place_type, _ = MfPlaceType.objects.get_or_create(
            title = item['type'].strip()
        )
        title = u"Úřad obce %s" % (town.title,)
        place, created  = MfPlace.objects.get_or_create(
            title    = title,
            address  = address,
            type     = place_type,
            bid      = bid
        )
        if created:
            place.json = {'phone': item['phone'], 'post': item['post']}
            place.save()

    def save_non_obec(self, item, bid):
        """
        Ulozeni zaznamu pro ostatni zaznamy (skoly, ministerstva, apod.)
        """
        # uzemni celky
        region, _ = Region.objects.get_or_create(
            title = item['region'].strip(),
            slug  = slugify(item['region'].strip())
        )
        district, _ = District.objects.get_or_create(
            title  = item['district'].strip(),
            slug   = slugify(item['district'].strip()),
            region = region
        )
        town, _ = Town.objects.get_or_create(
            title    = item['post'].strip(),
            slug     = slugify(item['post'].strip()),
            district = district
        )
        zzip, _ = Zip.objects.get_or_create(
            title = Zip.normalize(item['zip']),
            town  = town
        )

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
            bid     = bid
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

        # kontrola ze nebylo zadano oboji
        if len(importer_kwargs) == 2:
            self.log('Nemuzes zadat oba parametry (--ignore a --include). Bud nezadavej nic, nebo jen jeden z nich.\n')
            sys.exit(1)

        # spusteni importu
        importer = PlaceImporter1(self.stdout, filename, **importer_kwargs)
        importer.run()
