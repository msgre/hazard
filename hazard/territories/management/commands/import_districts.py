# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re
import sys

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Polygon

from hazard.territories.models import Region, District
from hazard.gobjects.utils import ImporterBase


WHITECHAR_RE = re.compile(r'\s+')
OUTER_BOUNDARY_RE = re.compile(r'<outerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</outerBoundaryIs>', re.DOTALL)
INNER_BOUNDARY_RE = re.compile(r'<innerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</innerBoundaryIs>', re.DOTALL)


class DistrictImporter(ImporterBase):
    """
    Natazeni dat o okresech podle dat FreeGeodataCZ od Klokana Petra Pridala
    (http://www.google.com/fusiontables/DataSource?dsrcid=2121470).

    Zadany zdroj jsme prevedli do CSVcka, UTF-8 kodovani a vyzobavame z nej
    info o rozloze, poctech lidi. Mimo to doplnime jeste vysklonovanou
    verzi nazvu okresu.
    """

    def __init__(self, stdout, source):
        self.stdout = stdout
        self.source = source

    def run(self):
        if not self.check_source():
            return
        columns = ['cat', 'nk', 'kn', 'knok', 'kodnuts', 'knuts', 'kodok', 'nazkr', 'nazkr_a', 'nazok', 'nazok_a', 'vymera', 'ob91', 'ob01', 'obakt', 'nazcs', 'zmenazaz', 'zmenapol', 'geometry']
        self.load_csv_source(columns, ignore_first_lines=1)
        self.process()

    def process(self):
        total = len(self.data)

        for idx, item in enumerate(self.data):
            self.log('%i / %i' % (idx + 1, total))

            # priprava dat
            title = u"Okres %s" % item['nazok']
            slug = slugify(item['nazok_a'])

            # vyzobneme polygony
            polygons = OUTER_BOUNDARY_RE.findall(item['geometry'])
            polygons.extend(INNER_BOUNDARY_RE.findall(item['geometry']))
            final_coords = []
            for polygon in polygons:
                items = WHITECHAR_RE.split(polygon)
                coords = [[float(y) for y in i.strip().split(',')] for i in items if i.strip()]
                coords = [(i[1], i[0]) for i in coords]
                final_coords.append(coords)

            # ulozeni okresu
            district = District.objects.create(
                title       = title,
                slug        = slug,
                lokativ     = u"V okrese %s" % item['nazok'],
                shape       = Polygon(*final_coords),
                code        = item['kodok'],
                region      = Region.objects.get(code=item['nk']),
                surface     = float(item['vymera']),
                population  = int(item['obakt'])
            )


class Command(BaseCommand):
    """
    Custom command pro import udaju o okresech.

    Pouziti:
        ./manage.py import_districts ../data/okresy.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Import udaju o okresech Ceske republiky.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s okresy.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = DistrictImporter(self.stdout, filename)
        importer.run()
