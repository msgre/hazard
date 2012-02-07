# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re
import sys

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point

from hazard.territories.models import Region, District, Town
from hazard.gobjects.utils import ImporterBase


POINT_RE = re.compile(r'<Point>\s*<coordinates>(.+)</coordinates>\s*</Point>', re.DOTALL)


class TownImporter(ImporterBase):
    """
    Natazeni dat o obcich podle dat FreeGeodataCZ od Klokana Petra Pridala
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
        total = len(self.data)

        for idx, item in enumerate(self.data):
            self.log('%i / %i' % (idx + 1, total))

            # priprava dat
            title = u"Obec %s" % item['nazob']
            slug = slugify(item['nazob_a'])

            # vyzobneme bod
            point = POINT_RE.findall(item['geometry'])
            point = point and [float(i) for i in point[0].strip().split(',')] or None

            # ulozeni okresu
            Town.objects.create(
                title      = title,
                slug       = slug,
                lokativ    = u"V obci %s" % item['nazob'],
                point      = Point(*point),
                code       = item['kodob'],
                lau        = item['icob'],
                region     = Region.objects.get(code=item['nk']),
                district   = District.objects.get(code=item['kodok']),
                surface    = float(item['vymera']),
                population = int(item['obakt'])
            )


class Command(BaseCommand):
    """
    Custom command pro import udaju o obcich.

    Pouziti:
        ./manage.py import_towns ../data/obce.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Import udaju o obcich Ceske republiky.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s obcemi.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = TownImporter(self.stdout, filename)
        importer.run()
