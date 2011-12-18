# -*- coding: utf-8 -*-

from django.db import models

from hazard.gobjects.models import Hell
from hazard.campaigns.models import Campaign


class AbstractConflict(models.Model):
    """
    Abstraktni trida pro vyjadreni konfliktu mezi hernou a jinym objektem
    (definovanym v odvozenem potomkovi).
    """
    hell     = models.ForeignKey(Hell, verbose_name=u"Herna")
    created  = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated  = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('created', )

    def __unicode__(self):
        return unicode(self.id)

    @staticmethod
    def find_conflicts(town, campaigns, set_name, surround_attr='surround'):
        """
        Nalezne vsechny konflikty mezi hernami zarazenymi do kampani `campaigns`
        ve meste `town`, a objekty `set_name` ktere odkazuji na mesto `town`
        pres vazbu FK. Parametrem `surround_attr` je mozne zadat jmeno atributu,
        pod kterym je ulozen polygon, vuci kteremu je pocitan konflikt.

        Priklad -- nalezeni vsech kofliktu mezi hernami a budovami ve meste se
        muze udelat nasledovne:

            town = Town.objects.get(slug='valasske-mezirici')
            campaigns = Campaign.objects.filter(slug='mf')
            BuildingConflict.find_conflicts(town, campaigns, 'building_set')

        Vraci slovnik, kde klicem je herna a hodnotou slovnik objektu, se
        kterymi ma konflikt.
        """
        out = {}
        hells = [(i.address.point, i) for i in town.hell_set.filter(campaigns__in=campaigns)]

        for set_obj in getattr(town, set_name).all():
            for (point, hell) in hells:
                if getattr(set_obj, surround_attr).contains(point):
                    if hell not in out:
                        out[hell] = []
                    out[hell].append(set_obj)

        return out
