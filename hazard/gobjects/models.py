# -*- coding: utf-8 -*-

import hashlib

from django.db import models
from django.contrib.gis.db import models as geomodels

from model_utils.managers import PassThroughManager

from hazard.campaigns.models import Campaign
from hazard.shared.fields import JSONField
from hazard.gobjects.managers import HellQuerySet


class AbstractPlace(geomodels.Model):
    """
    Nejake misto na konkretni adrese, abstraktni model.
    """
    title       = models.CharField(u"Název", blank=True, max_length=200)
    address     = models.ForeignKey('territories.Address', verbose_name=u"Adresa")
    description = models.TextField(u"Popis", blank=True)
    visible     = models.BooleanField(u"Viditelné?", default=True)
    # system
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # denormalizace
    region      = models.ForeignKey('territories.Region', verbose_name=u"Kraj")
    district    = models.ForeignKey('territories.District', verbose_name=u"Okres")
    town        = models.ForeignKey('territories.Town', verbose_name=u"Obec")

    class Meta:
        abstract = True
        ordering = ('created', )


class MachineType(models.Model):
    """
    Typ vyherniho automatu.

    TODO: initials
    u'EMR', u'Elektromechanická ruleta'
    u'VTZ', u'Vícemístné hrací zařízení'
    u'VHP', u'Výherní hrací přístroj'
    u'VLT', u'Videoloterijní terminál'
    u'IVT', u'Interaktivní videoloterijní terminál'
    """
    title = models.CharField(u"Kód", max_length=30)
    description = models.TextField(u"Popis", blank=True)

    class Meta:
        verbose_name = u'Typ výherního automatu'
        verbose_name_plural = u'Typy výherních automatů'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


class Hell(AbstractPlace):
    """
    Herna.
    """
    counts    = models.ManyToManyField(MachineType, related_name='hells', verbose_name=u"Počty automatů", through='MachineCount')
    note      = models.TextField(u"Poznámka", blank=True)
    json      = JSONField(u"Extra JSON data", null=True, blank=True)
    campaigns = models.ManyToManyField(Campaign, verbose_name=u"Kampaň")
    # denormalizace
    total     = models.IntegerField(default=0, editable=False)
    objects   = PassThroughManager(HellQuerySet)

    class Meta:
        verbose_name = u'Herna'
        verbose_name_plural = u'Herny'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj, okres, obec
        a secte celkovy pocet automatu v herne.
        """
        self.region = self.address.region
        self.district = self.address.district
        self.town = self.address.town

        return super(Hell, self).save(*args, **kwargs)


class MachineCount(models.Model):
    """
    Pocty automatu.
    """
    hell  = models.ForeignKey(Hell, verbose_name=u"Herna")
    type  = models.ForeignKey(MachineType, verbose_name=u"Typ automatu")
    count = models.IntegerField(u"Počet", default=0)
    json  = JSONField(u"Extra JSON data", null=True, blank=True)

    class Meta:
        verbose_name = u'Herna'
        verbose_name_plural = u'Herny'
        ordering = ('type__title', 'hell__created', )

    def __unicode__(self):
        return unicode(self.id)


# from django.contrib.gis.gdal import CoordTransform, SpatialReference
#
# class AbstractShape(geomodels.Model):
#     """
#     Model popisujici geograficky objekt (bod/cara/polygon).
#     """
#     MINIMUM_DISTANCE = 2 # v metrech; pokud se pocita okoli pro bod/caru a neni zadan distance, tak beru tuto hodnotu
#
#     # geometrie
#     point       = geomodels.PointField(u"Bod", null=True, blank=True)
#     line        = geomodels.LineStringField(u"Čára", null=True, blank=True)
#     poly        = geomodels.PolygonField(u"Polygon", null=True, blank=True)
#     # okoli
#     distance    = models.IntegerField(u"Vzdálenost", blank=True, null=True)
#     surround    = geomodels.PolygonField(u"Polygon okolí", null=True, blank=True)
#     hash        = models.CharField(u"Hash základního geo tvaru", max_length=80, editable=False)
#     # system
#     created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
#     updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
#     objects     = geomodels.GeoManager()
#
#     class Meta:
#         abstract = True
#         ordering = ('created', )
#
#     def get_geometry(self):
#         """
#         Vrati geometricky objekt (bod, caru nebo tvar).
#         """
#         return self.point or self.line or self.poly or None
#
#     def get_geometry_type(self):
#         """
#         Vrati retezec reprezentujici typ tvaru, ktery je v modelu ulozen
#         (point/line/poly).
#         """
#         return self.point and 'point' or \
#                self.line and 'line' or \
#                self.poly and 'poly' or None
#
#     def get_hash(self):
#         """
#         Vrati hash geometrickeho tvaru.
#         """
#         geometry = self.get_geometry()
#         geometry = geometry and geometry.ewkt or ''
#         return hashlib.sha224(geometry).hexdigest()
#
#     def calculate_surround(self, ct1=None, ct2=None):
#         """
#         Vypocita okoli tvaru a vrati jej.
#         """
#         geometry = self.get_geometry()
#         if not geometry:
#             return None
#
#         # prepocteme WGS84 souradnice tvaru do krovaka
#         if ct1 is None:
#             ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
#         krovak_geometry = geometry.transform(ct1, clone=True)
#
#         # vypocitame okoli tvaru
#         if self.get_geometry_type != 'poly' and (not self.distance or self.distance <= 0):
#             distance = self.MINIMUM_DISTANCE
#         else:
#             distance = self.distance or 0
#         surround = krovak_geometry.buffer(distance)
#
#         # prevedeme okoli zpet na WGS84
#         if ct2 is None:
#             ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))
#         surround.transform(ct2)
#
#         return surround


import signals
