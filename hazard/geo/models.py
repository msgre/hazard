# -*- coding: utf-8 -*-

import hashlib
import urllib2

from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.core.urlresolvers import reverse


class Entry(models.Model):
    """
    Zaznam jedne obce/mesta.
    """
    title        = models.CharField(u"Název", max_length=200)
    slug         = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    population   = models.IntegerField(u"Populace", blank=True, null=True)
    area         = models.IntegerField(u"Plocha katastrálního území", blank=True, null=True)
    wikipedia    = models.URLField(u"URL na Wikipedii", blank=True, null=True)
    hell_url     = models.URLField(u"URL na KML s popisem heren", blank=True, null=True)
    hell_kml     = models.TextField(editable=False)
    building_url = models.URLField(u"URL na KML s popisem veřejných budov", blank=True, null=True)
    building_kml = models.TextField(editable=False)
    public       = models.BooleanField(u"Veřejný záznam", default=False)
    created      = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    # denormalizovane hodnoty
    # TODO: popsat
    dperc           = models.FloatField(editable=False, default=0)
    dhell_count     = models.FloatField(editable=False, default=0)
    dok_hell_count  = models.FloatField(editable=False, default=0)
    dper_population = models.FloatField(editable=False, default=0)
    dper_area       = models.FloatField(editable=False, default=0)

    class Meta:
        verbose_name = u'Záznam obce'
        verbose_name_plural = u'Záznamy obcí'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('entry-detail', kwargs={'slug': self.slug})

    def recalculate_denormalized_values(self, counts=False):
        """
        Prepocita denormalizovane statisticke udaje o hernach v obci.
        """
        if counts:
            self.dhell_count = self.hell_set.count()
            self.dok_hell_count = self.hell_set.filter(zones__isnull=True).count()
        if self.dhell_count > 0.0:
            self.dperc = float(self.dhell_count - self.dok_hell_count) / self.dhell_count * 100
            self.dper_population = float(self.population) / self.dhell_count
        if self.area > 0.0:
            self.dper_area = float(self.dhell_count) / self.area


class Zone(models.Model):
    """
    Obrys okoli verejne budovy.
    """
    poly = geomodels.PolygonField(u"Obrys okolí")

    class Meta:
        verbose_name = u'Okolí veřejné budovy'
        verbose_name_plural = u'Okolí veřejných budov'


class CommonInfo(models.Model):
    """
    Spolecne atributy verejnych budov a heren.
    """
    title       = models.CharField(u"Název", max_length=200)
    description = models.TextField(u"Popis", blank=True)
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    entry       = models.ForeignKey(Entry, verbose_name=u"Záznam")

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Building(CommonInfo):
    """
    Verejna budova.
    """
    poly = geomodels.PolygonField(u"Obrys budovy")
    zone = models.ForeignKey(Zone, verbose_name=u"Zóna", blank=True, null=True)

    class Meta:
        verbose_name = u'Veřejná budova'
        verbose_name_plural = u'Veřejné budovy'

    def calculate_zone(self, distance):
        """
        Vypocita okoli budovy a ulozi jej do self.zone.
        """
        # pokud uz nejake okoli vypocitane mame, odstranime je...
        if self.zone:
            self.zone.delete()

        # prepocteme WGS84 souradnice obrysu budovy do krovaka
        ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
        m_poly = self.poly.transform(ct1, clone=True)

        # vypocitame okoli/sousedstvi budovy
        zone = m_poly.buffer(distance)

        # prevedeme okoli zpet na WGS84
        ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))
        zone.transform(ct2)

        # vytvorime v DB novy objekt
        self.zone = Zone.objects.create(poly=zone)
        self.save()


class Hell(CommonInfo):
    """
    Herna.
    """
    point = geomodels.PointField(u"Poloha")
    zones = models.ManyToManyField(Zone, related_name='hells', verbose_name=u'Zakázané zóny')
    uzone = models.ForeignKey(Zone, editable=False, blank=True, null=True)
    zones_calculated = models.BooleanField(editable=False, default=False)

    class Meta:
        verbose_name = u'Herna'
        verbose_name_plural = u'Herny'

    def calculate_conflicts(self):
        """
        Zjisti, do kterych oblasti herna zasahuje a ulozi je do atributu `zones`.
        """
        zones = []
        self.zones.clear()
        self.zones_calculated = False
        self.save()

        for building in self.entry.building_set.all():
            if building.zone.poly.contains(self.point):
                zones.append(building.zone)

        self.zones.add(*zones)
        self.zones_calculated = True
        self.save()

    def calculate_uzone(self):
        """
        Udela sjednoceni vsech zon, ktere se k herne vazou. Vysledkem je jediny
        velky polygon.
        """
        uzone = None
        for zone in self.zones.all():
            if uzone:
                uzone = zone.poly.union(uzone)
            else:
                uzone = zone.poly
        if uzone:
            self.uzone = Zone.objects.create(poly=uzone)
            self.save()

    def is_in_conflict(self):
        if not self.zones_calculated:
            return None
        return self.zones.count() > 0
    in_conflict = property(is_in_conflict)


import signals
