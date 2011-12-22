# -*- coding: utf-8 -*-

import re

from django.template.defaultfilters import slugify, striptags
from django.contrib.gis.geos import Polygon

from hazard.gobjects.utils import ImporterBase
from hazard.territories.models import District


WHITECHAR_RE = re.compile(r'\s+')
OUTER_BOUNDARY_RE = re.compile(r'<outerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</outerBoundaryIs>', re.DOTALL)
INNER_BOUNDARY_RE = re.compile(r'<innerBoundaryIs>\s*<LinearRing>\s*<coordinates>(.+)</coordinates>\s*</LinearRing>\s*</innerBoundaryIs>', re.DOTALL)


class DistrictImporter(ImporterBase):
    """
    Import dat z http://www.google.com/fusiontables/DataSource?dsrcid=2121559
    (aktualizace udaju o vymere, poctech obyvatel a polygonu kraje)
    """

    def __init__(self, source):
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
            print '%i / %i' % (idx + 1, total)

            # vytahneme kraj
            slug = slugify(item['nazok_a'])
            try:
                district = District.objects.get(slug='okres-%s' % (slug, ))
            except:
                if slug == 'jablonec-nad-nisou':
                    slug = 'jablonec-nnisou'
                    try:
                        district = District.objects.get(slug='okres-%s' % (slug, ))
                    except:
                        print '============== %s is missing' % (slug,)
                        continue
                else:
                    print '============== %s is missing' % (slug,)
                    continue
            # TODO: jeste nevim jak to vyresim s prahou...
            # (ve fusion tables je jediny okres hlavni-mesto-praha, ale ja
            # mam v DB mrte praha X zaznamu...)

            # vyzobneme polygony
            polygons = OUTER_BOUNDARY_RE.findall(item['geometry'])
            polygons.extend(INNER_BOUNDARY_RE.findall(item['geometry']))
            final_coords = []
            for polygon in polygons:
                items = WHITECHAR_RE.split(polygon)
                coords = [[float(y) for y in i.strip().split(',')] for i in items if i.strip()]
                coords = [(i[1], i[0]) for i in coords]
                final_coords.append(coords)

            # aktualizujeme zaznam o kraji
            district.surface = float(item['vymera'])
            district.population = int(item['obakt'])
            district.shape = Polygon(*final_coords)
            district.save()


class RegionImportet(ImporterBase):
    """
    TODO:
    """

    def __init__(self, source):
        self.source = source

    def run(self):
        if not self.check_source():
            return
        columns = ['cat', 'nk', 'kn', 'kodnuts', 'nazkr', 'nazkr_a', 'vymera', 'ob91', 'ob01', 'obakt', 'nazcs', 'zmenazaz', 'zmenapol', 'geometry']
        self.load_csv_source(columns, ignore_first_lines=1)
        self.process()

    def process(self):
        total = len(self.data)

        for idx, item in enumerate(self.data):
            print '%i / %i' % (idx + 1, total)

            # vytahneme kraj
            slug = slugify(item['nazok_a'])
            region = Region.objects.get(slug__contains=slug)

            # vyzobneme polygony
            polygons = OUTER_BOUNDARY_RE.findall(item['geometry'])
            polygons.extend(INNER_BOUNDARY_RE.findall(item['geometry']))
            final_coords = []
            for polygon in polygons:
                items = WHITECHAR_RE.split(polygon)
                coords = [[float(y) for y in i.strip().split(',')] for i in items if i.strip()]
                coords = [(i[1], i[0]) for i in coords]
                final_coords.append(coords)

            # aktualizujeme zaznam o kraji
            region.surface = float(item['vymera'])
            region.population = int(item['obakt'])
            region.shape = Polygon(*final_coords)
            region.save()
