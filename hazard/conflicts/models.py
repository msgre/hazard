# -*- coding: utf-8 -*-

from django.db import models

from hazard.gobjects.models import Hell
from hazard.campaigns.models import Campaign


class AbstractConflict(models.Model):
    """
    Abstraktni trida pro vyjadreni konfliktu mezi hernou a jinym objektem
    (definovanym v odvozenem potomkovi).

    NOTE: Z ciste technickeho hlediska bychom meli spise evidovat konflikty
    mezi 2 adresami, protoze na jedne adrese muze sidlit nekolik subjektu
    (a pak je jasne, ze pokud je adresa v konfliktu, pak je v konfliktu i
    kazdy subjekt v ni).
    """
    hell    = models.ForeignKey(Hell, verbose_name=u"Herna")
    created = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('created', )

    def __unicode__(self):
        return unicode(self.id)

    @staticmethod
    def conflict_addresses(town, campaigns, set_name, address_attr='address', surround_attr='poly'):
        """
        Nalezne vsechny konfliktni adresy heren zarazenych do kampani `campaigns`
        ve meste `town`, a objekty `set_name` ktere odkazuji na mesto `town`
        pres vazbu FK. Parametrem `surround_attr` je mozne zadat jmeno atributu,
        pod kterym je ulozen polygon, vuci kteremu je pocitan konflikt a v
        parametru `address_attr` atribut vedouci na model Address.

        Priklad -- nalezeni vsech kofliktu mezi hernami a misty ve meste se
        muze udelat nasledovne:

            town = Town.objects.get(slug='valasske-mezirici')
            campaigns = Campaign.objects.filter(slug='mf')
            MfPlaceConflict.conflict_addresses(town, campaigns, 'mfaddresssurround_set')

        Vraci slovnik, kde klice jsou ID adres heren a hodnoty seznam ID adres
        mist.
        """
        out = {}
        hell_addresses = dict([(i.address_id, i.address.get_geometry()) \
                               for i in town.hell_set.filter(campaigns__in=campaigns)])

        for set_obj in getattr(town, set_name).all():
            for address, geo in hell_addresses.iteritems():
                if getattr(set_obj, surround_attr).intersects(geo):
                    if address not in out:
                        out[address] = []
                    out[address].append(getattr(set_obj, "%s_id" % (address_attr, )))

        return out
