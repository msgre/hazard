# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import re
import sys

from django.core.management.base import BaseCommand

from hazard.territories.models import Town, Zip
from hazard.gobjects.utils import ImporterBase


class ZipImporter(ImporterBase):
    """
    Natazeni dat o PSC z dat Ceske posty
    (http://www.ceskaposta.cz/cz/nastroje/dokumenty-ke-stazeni-id355/,
    kapitola Zákaznické výstupy, Seznam PSČ částí obcí a obcí bez částí (XLS)).

    Vyznam jednotlivych sloupcu tabulky:

    * NAZCOBCE -- Název části obce nebo obce bez části
    * PSC -- Využitelné PSČ v části obce
    * NAZPOST -- Název adresní pošty
    * KODOKRESU -- Kód okresu
    * NAZOKRESU -- Název okresu
    * NAZOBCE -- Název obce
    """

    def __init__(self, stdout, source):
        self.stdout = stdout
        self.source = source

    def run(self):
        if not self.check_source():
            return
        columns = ["NAZCOBCE","PSC","NAZPOST","KODOKRESU","NAZOKRESU","NAZOBCE"]
        self.load_csv_source(columns, ignore_first_lines=1)
        self.process()

    def process(self):
        total = len(self.data)

        for idx, item in enumerate(self.data):
            #self.log('%i / %i' % (idx + 1, total))

            try:
                town = Town.objects.get(title=u"Obec %s" % item['NAZOBCE'], district__code=item['KODOKRESU'])
            except Town.DoesNotExist:
                try:
                    town = Town.objects.get(title=u"Obec %s" % item['NAZCOBCE'], district__code=item['KODOKRESU'])
                except Town.DoesNotExist:
                    self.log('Unknown town %s (psc=%s, %s)' % (item['NAZOBCE'], item['PSC'], item['NAZCOBCE']))
                    continue

            Zip.objects.get_or_create(
                title = item['PSC'],
                post  = item['NAZPOST'],
                town  = town
            )


class Command(BaseCommand):
    """
    Custom command pro import udaju o PSC.

    Pouziti:
        ./manage.py import_zips ../data/psc.csv
    """
    args = u'<cesta-k-csv-souboru>'
    help = u'Import udaju o PSC Ceske republiky.'

    def handle(self, *args, **options):
        if not args:
            self.log('Zadej cestu k CSV souboru s PSC.\n')
            sys.exit(1)

        # parametry pro importer
        filename = args[0]

        # spusteni importu
        importer = ZipImporter(self.stdout, filename)
        importer.run()
