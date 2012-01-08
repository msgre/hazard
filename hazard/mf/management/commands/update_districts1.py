# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Lesteni dat o okresech -- doplneni chybejicich a uprava stavajicich udaju.
"""

import re
import sys

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Polygon

from hazard.territories.models import Region, District
from hazard.gobjects.utils import ImporterBase
from hazard.shared.models import repair_referencies

WHITECHAR_RE = re.compile(r'\s+')
OUTER_BOUNDARY_RE = re.compile(r'<outerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</outerBoundaryIs>', re.DOTALL)
INNER_BOUNDARY_RE = re.compile(r'<innerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</innerBoundaryIs>', re.DOTALL)


class DistrictUpdater1(ImporterBase):
    """
    Aktualizace udaju o okresech podle dat FreeGeodataCZ od Klokana Petra Pridala
    (http://www.google.com/fusiontables/DataSource?dsrcid=2121559).

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

        # jeste nez zacnem, musime si zaridit existenci okresu "Hlavní město Praha"
        praha, _ = District.objects.get_or_create(
            title   = u'Hlavní město Praha',
            slug    = 'praha',
            lokativ = u'V okrese Hlavní město Praha',
            region  = Region.objects.get(slug='praha')
        )

        # ... a prenest pod nej omylem vytvorene obvody
        # NOTE: proc se to tu deje?
        # Historie -- prazske obvody na urovni okresu vznikly pri zpracovavani
        # surovych dat zakoupene Matejem. Teprve kdyz jsme zacali data zpresnovat
        # vyslo najevo, ze obvod je blbost (existuji pouze 3 okresy s prahou
        # v nazvu -- hlavni mesto, vychod a zapad)
        obvody = District.objects.filter(slug__contains='obvod-', region__slug='praha')
        if obvody.exists():
            for obvod in obvody:
                log = repair_referencies(obvod, praha)
                msg = u", ".join([u"%s=%i" % (k, len(log['affected'][k])) for k in log['affected']])
                self.log('Moved "%s" under "%s (%s)"' % (obvod.slug, praha.slug, msg))
                obvod.delete()

        for idx, item in enumerate(self.data):
            self.log('%i / %i' % (idx + 1, total))

            # vytahneme kraj
            slug = slugify(item['nazok_a'])
            if slug == 'jablonec-nad-nisou':
                slug = 'jablonec-nnisou'
            elif slug == 'hlavni-mesto-praha':
                slug = 'praha'
            try:
                district = District.objects.get(slug='okres-%s' % (slug, ))
            except District.DoesNotExist:
                try:
                    district = District.objects.get(slug=slug)
                except District.DoesNotExist:
                    self.log('============== %s is missing' % (slug,))
                    continue

            # vyzobneme polygony
            polygons = OUTER_BOUNDARY_RE.findall(item['geometry'])
            polygons.extend(INNER_BOUNDARY_RE.findall(item['geometry']))
            final_coords = []
            for polygon in polygons:
                items = WHITECHAR_RE.split(polygon)
                coords = [[float(y) for y in i.strip().split(',')] for i in items if i.strip()]
                coords = [(i[1], i[0]) for i in coords]
                final_coords.append(coords)

            # aktualizujeme zaznam o okrese
            district.title = u"Okres %s" % item['nazok']
            district.slug = slug
            district.lokativ = u"V okrese %s" % item['nazok']
            district.surface = float(item['vymera'])
            district.population = int(item['obakt'])
            district.shape = Polygon(*final_coords)
            district.save()


class Command(BaseCommand):
    """
    Custom command pro aktualizaci udaju o okresech.

    Prikaz je dobre volat az po ./manage.py import_places1, tj. az ve chvili,
    kdy uz v databazi mame informace o krajich, okresech a obcich. Jeho vysledkem
    jsou "vycistena" okresni data -- doplneni poctu obyvatel, rozlohy, tvaru
    okresu, vysklonovani nazvu.

    Pouziti:
        ./manage.py update_districts1 ../data/okresy.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Aktualizace udaju o okresech Ceske republiky.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s okresy.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = DistrictUpdater1(self.stdout, filename)
        importer.run()
