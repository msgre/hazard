# -*- coding: utf-8 -*-

import os
import pickle
import csv

from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.gis.measure import D

from hazard.territories.models import Region, District, Town, Zip
from hazard.addresses.models import Address, AltAddress
from hazard.gobjects.models import Hell, MachineType, MachineCount
from hazard.mf.models import Building, BuildingType


class ImporterBase(object):

    ADDRESS_RADIUS = {'m': 2}

    def check_source(self):
        """
        Overi existenci zdrojoveho souboru.
        """
        return os.path.exists(self.source) and os.path.isfile(self.source)

    def load_pickle_source(self):
        """
        Nahraje picklos s daty.
        """
        try:
            self.data = pickle.load(open(self.source))
        except:
            self.data = None

    def load_csv_source(self, recipe, delimiter=',', quotechar='"', infinite_last=False, ignore_first_lines=0):
        """
        Nacte zadany CSV soubor a kazdy radek v nem prevede na slovnik (nazvy
        klicu/sloupecku jsou definovany v `recipe`). Pokud se posledni sloupecek
        v tabulce opakuje do "nekonecna" (napr. v tabulce s budovami muze je 4 az
        n-ty sloupec gps souradnice), musi se nastavit parametr `infinite_last` na
        True, a do vystupniho slovniku se pak generuji klice slozene z posledniho
        klice z recipe+index (napr. 'gps1', 'gps2', atd).
        """
        out = []
        rows = csv.reader(open(self.source, 'rb'), delimiter=delimiter, quotechar=quotechar)
        for line_no, row in enumerate(rows):
            if line_no < ignore_first_lines:
                continue
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
        self.data = out

    def get_address(self, lng, lat, street, town):
        """
        Pokusi se najit adresu pro zadany bod, ulici a mesto.
        """
        # nejdriv zjistime, jestli presne na tom samem bode uz neco nelezi
        point = Point(lng, lat, srid=4326)
        address = Address.objects.filter(point__same_as=point)
        if address.exists():
            # ano, lezi!
            address = address[0]
            if address.title != street.strip():
                # novy zaznam ma ale jinou ulici, uchovame si jeji tvar
                alt_address = AltAddress.objects.create(
                    title = street.strip(),
                    address = address
                )
        else:
            # presne na stejnem bode nic nelezi
            address = Address.objects.create(
                title = street.strip(),
                town  = town,
                slug  = slugify(street.strip()),
                point = point
            )
        return address


class BuildingImporter1(ImporterBase):
    """
    Trida pro import dat, ktere Matej koupil koncem listopadu 2011.
    Ziskali jsme sadu XLS tabulek, kde byly zakladni informace, ale bez GPS
    pozic.

    Data jsem exportoval do CSV, rozrezal a behem cca 2 dnu pres Google Geocode
    zjistil potrebne pozice. Vysledky jsem ulozil do picklose, a s nim
    se tady prave pracuje.

    Pouziti
    Je vhodne nejprve importovat vse s vyjimkou obci, a teprve pote pouze obce.
    Jde o to, ze data pro obce obsahuji mene dat (neni u nich uveden okres
    a kraj). Kdyz se naimportuje nejdrive vse ostatni, jsem pak schopen s
    pomoci PSC najit kde asi obec lezi, ikdyz zatim v DB ulozena neni.

        from hazard.gobjects.utils import BuildingImporter1
        a = BuildingImporter1('../data/budovy3.pickle', ignore_types=['obce'])
        a.run()
        b = BuildingImporter1('../data/budovy3.pickle', include_types=['obce'])
        b.run()

    Pickle data jsou trojity slovnik:
    * prvni klic je typ budovy ('skoly', 'ministerstvo', apod.)
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

    def __init__(self, source, include_types=[], ignore_types=[]):
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
                print bid

    def process(self):
        """
        Zpracuje data z picklose.
        """
        if not self.data:
            return

        for tidx, type in enumerate(self.data):

            # nemame nahodou tento zaznam preskocit?
            if type in self.ignore_types or (self.include_types and type not in self.include_types):
                print 'Skipping type %s' % (type,)
                continue

            type_size = len(self.data[type])
            for iidx, id in enumerate(self.data[type]):

                print '%s: %i / %i' % (type, iidx + 1, type_size)
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
        Zjisti mesto, do ktereho zaznam o budove patri.

        Tato metoda se pouziva pouze pri importu budov. Problem je v tom,
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

        # zaznam o budove
        building_type, _ = BuildingType.objects.get_or_create(
            title = item['type'].strip()
        )
        title = u"Úřad obce %s" % (town.title,)
        building, _  = Building.objects.get_or_create(
            title    = title,
            address  = address,
            type     = building_type,
            distance = 100,
            bid      = bid,
            note     = u"phone: %s\npost: %s" % (item['phone'], item['post'])
        )

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

        # zaznam o budove
        building_type, _ = BuildingType.objects.get_or_create(
            title = item['type'].strip()
        )
        title = u" ".join([item['title1'].strip(), item['title2'].strip()])
        building, _ = Building.objects.get_or_create(
            title   = title.strip(),
            address = address,
            type    = building_type,
            bid     = bid
        )


class MinistryHellImporter(ImporterBase):
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
    Je vhodne nejprve importovat vsechna data o budovach, viz BuildingImporter1
    (importem se do DB dostanou uzitecne informace o uzemnich celcich a adresach).
    Pak staci zavolat:

        from gobjects.utils import MinistryHellImporter
        a = MinistryHellImporter('../data/herny_ministerstvo_1.csv')
        a.run()
        a = MinistryHellImporter('../data/herny_ministerstvo_2.csv')
        a.run()
        a = MinistryHellImporter('../data/herny_ministerstvo_3.csv')
        a.run()
        a = MinistryHellImporter('../data/herny_ministerstvo_4.csv')
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
    TOWN_RADIUS = {'km': 1}
    ADDRESS_RADIUS = {'m': 250}

    def __init__(self, source):
        self.source = source
        self.missing = []

    def run(self):
        """
        TODO:
        """
        if not self.check_source():
            return
        self.load_csv_source(['town', 'street', 'type', 'number', 'count', 'name', 'note', 'gps'])
        self.process()
        if self.missing:
            for i in self.missing:
                print i

    def process(self):
        """
        TODO:
        """
        total = len(self.data)

        for idx, item in enumerate(self.data):
            print '%i / %i' % (idx + 1, total)
            qs = Town.objects.filter(title=item['town'])

            if not qs.exists():
                # pokud nemame GPS pozici, nemuzeme dal nic delat
                if 'gps' not in item or item['gps'] == 'nenalezeno':
                    print 'Skipping row %i due missing GPS' % (idx + 1,)
                    self.missing.append(idx)
                    continue

                # zkusime udelat geo lookup
                gps = [float(i.strip()) for i in item['gps'].split(',')] # lng/lat
                point = Point(gps[0], gps[1], srid=4326)
                qs = Town.objects.filter(point__isnull=False, point__distance_lte=(point, D(**self.TOWN_RADIUS))).distance(point).order_by('distance')
                if qs.exists():
                    print 'Geo lookup found near town (count=%i), first is %s, distance=%s' % (len(qs), qs[0], qs[0].distance)
                    town = qs[0]
                else:
                    qs = Address.objects.filter(point__isnull=False, point__distance_lte=(point, D(**self.ADDRESS_RADIUS))).distance(point).order_by('distance')
                    if qs.exists():
                        print 'Geo lookup found near addresses (count=%i), first is %s, distance=%s' % (len(qs), qs[0], qs[0].distance)
                        town = qs[0].town
                    else:
                        print 'Address was not found, row %i' % (idx, )
                        self.missing.append(idx)
                        continue
            else:
                town = qs[0]

            # ulozime zaznam do DB
            if town:
                self.save(item, town)

    def save(self, item, town):
        """
        TODO:
        """
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
