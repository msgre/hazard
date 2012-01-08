# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
TODO: tohle neni hotove
kod obce viz debata na mailing listu

Lesteni dat o obcich -- doplneni chybejicich a uprava stavajicich udaju.
"""

import re
import sys

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Polygon

from hazard.territories.models import Region, District, Zip, Town
from hazard.gobjects.utils import ImporterBase
from hazard.shared.models import repair_referencies

WHITECHAR_RE = re.compile(r'\s+')
OUTER_BOUNDARY_RE = re.compile(r'<outerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</outerBoundaryIs>', re.DOTALL)
INNER_BOUNDARY_RE = re.compile(r'<innerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</innerBoundaryIs>', re.DOTALL)


class TownUpdater1(ImporterBase):
    """
    Aktualizace udaju o obcich podle dat FreeGeodataCZ od Klokana Petra Pridala
    (http://www.google.com/fusiontables/DataSource?dsrcid=2121188).

    Zadany zdroj jsme prevedli do CSVcka, UTF-8 kodovani a vyzobavame z nej
    info o rozloze, poctech lidi. Mimo to doplnime jeste vysklonovanou
    verzi nazvu obce.
    """

    def __init__(self, stdout, source):
        self.stdout = stdout
        self.source = source

    def run(self):
        if not self.check_source():
            return
        columns = ['cat','nk','kn','knok','kodnuts','knuts','kodok','porob','kodob','ko','icob','iczuj','nazob','nazob_a','nazevur','nazevur_a','ico','om','ur','sm','psc','vymera','ob91','ob01','obakt','kodst','porcsu','kodfi','cfu','kodma','pcmat','probl','syob','sxob','mapa','nazcs','zmenazaz','zmenapol','cispou','okpo','kodpo','nazpo','nazpo_a','cisorp','okorp','kodorp','nazorp','nazorp_a','geometry']

        self.load_csv_source(columns, ignore_first_lines=1)
        self.process()

    def process(self):
        # nez se pustime do vaznejsich akci, musime si zamest cesticku a opravit
        # nektere anomalie v obcich...
        self.repair_anomalies()

        total = len(self.data)

        for idx, item in enumerate(self.data):
            self.log('%i / %i' % (idx + 1, total))

            # vytahneme obec
            code = item['psc']
            try:
                zip = Zip.objects.get(title=code)
            except Zip.MultipleObjectsReturned:
                try:
                    zip = Zip.objects.get(title=code, town__title=item['nazob'])
                except Zip.DoesNotExist:
                    self.log('Multiple towns for ZIP code %s. Skipping...' % item['psc'])
                    continue
            except Zip.DoesNotExist:
                self.log("Record for %s (%s) wasn't found in DB. Skipping..." % (item['nazob_a'], item['psc']))
                continue

            town = zip.town

            # aktualizujeme zaznam o obci
            town.title = u"Obec %s" % item['nazob']
            town.slug = slugify(item['nazob_a'])
            town.code = item['icob']
            town.lokativ = u"V obci %s" % item['nazob']
            town.surface = float(item['vymera'])
            town.population = int(item['obakt'])
            town.save()

    def repair_anomalies(self):
        """
        V hrube naimportovanych datech o obcich je treba jeste manualne upravit
        nektere zaznamy.
        """
        # oprava anomalii
        # obec Unhost patri do okresu kladno
        chief = Town.objects.get(slug='unhost', district__slug='kladno')
        slave = Town.objects.filter(slug='unhost', district__slug='praha-zapad')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Pohorelice
        chief = Town.objects.get(title=u'Pohořelice', district__title=u'Okres Brno-venkov')
        slave = Town.objects.filter(title=u'Pohořelice', district__title=u'Okres Břeclav')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Vranovice
        chief = Town.objects.get(title=u'Vranovice', district__title=u'Okres Brno-venkov')
        slave = Town.objects.filter(title=u'Vranovice', district__title=u'Okres Břeclav')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Jiřice u Miroslavi
        chief = Town.objects.get(title=u'Jiřice u Miroslavi', district__title=u'Okres Znojmo')
        slave = Town.objects.filter(title=u'Jiřice u Miroslavi', district__title=u'Okres Brno-venkov')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Brodek u Přerova
        chief = Town.objects.get(title=u'Brodek u Přerova', district__title=u'Okres Přerov')
        slave = Town.objects.filter(title=u'Brodek u Přerova', district__title=u'Okres Olomouc')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Břidličná
        chief = Town.objects.get(title=u'Břidličná', district__title=u'Okres Bruntál')
        slave = Town.objects.filter(title=u'Břidličná', district__title=u'Okres Olomouc')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Moravský Beroun
        chief = Town.objects.get(title=u'Moravský Beroun', district__title=u'Okres Olomouc')
        slave = Town.objects.filter(title=u'Moravský Beroun', district__title=u'Okres Bruntál')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Klimkovice
        chief = Town.objects.get(title=u'Klimkovice', district__title=u'Okres Ostrava-město')
        slave = Town.objects.filter(title=u'Klimkovice', district__title=u'Okres Nový Jičín')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Dolní Lhota
        chief = Town.objects.get(title=u'Dolní Lhota', district__title=u'Okres Ostrava-město')
        slave = Town.objects.filter(title=u'Dolní Lhota', district__title=u'Okres Opava')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # Velká Polom
        chief = Town.objects.get(title=u'Velká Polom', district__title=u'Okres Ostrava-město')
        slave = Town.objects.filter(title=u'Velká Polom', district__title=u'Okres Opava')
        if slave.exists():
            log = repair_referencies(slave[0], chief)
            msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
            self.log('Moving "%s" under "%s" (%s)' % (slave[0].slug, chief.slug, msg))
            slave.delete()

        # dvoji zaznamy pro stejne obce
        doubled = [u'Kostelec nad Černými Lesy', u'Starý Plzenec', u'Podbořany', u'České Meziříčí']
        for title in doubled:
            towns = Town.objects.filter(title=title)
            if towns.count() > 1:
                chief = towns[0]
                for slave in towns[1:]:
                    log = repair_referencies(slave, chief)
                    msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
                    self.log('Moving "%s" under "%s" (%s)' % (slave.slug, chief.slug, msg))
                    slave.delete()


class Command(BaseCommand):
    """
    Custom command pro aktualizaci udaju o obcich.

    Prikaz je dobre volat az po ./manage.py import_places1, tj. az ve chvili,
    kdy uz v databazi mame informace o krajich, okresech a obcich. Jeho vysledkem
    jsou "vycistena" okresni data -- doplneni poctu obyvatel, rozlohy, tvaru
    okresu, vysklonovani nazvu.

    Pouziti:
        ./manage.py update_towns1 ../data/obce.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Aktualizace udaju o obcich Ceske republiky.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s obcemi.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = TownUpdater1(self.stdout, filename)
        importer.run()
