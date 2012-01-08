# -*- coding: utf-8 -*-

import os
import pickle
import csv

from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.contrib.gis.measure import D

from hazard.territories.models import Town, Address, AltAddress
from hazard.gobjects.models import Hell, MachineType, MachineCount


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

    def log(self, msg):
        if self.stdout:
            self.stdout.write(u'%s\n' % msg.strip())
