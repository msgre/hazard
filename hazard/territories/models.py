# -*- coding: utf-8 -*-

import re
import hashlib

from django.db import models
from django.contrib.gis.db import models as geomodels

WHITECHAR_RE = re.compile('\s+')



class Region(geomodels.Model):
    """
    Kraj.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    lokativ     = models.CharField(u"Lokativ", max_length=200, blank=True, null=True, help_text=u"6.pád, 'O kom, o čem', včetně vyskloňovaného slova 'kraj' a předložky. Např. 'Ve Zlínském kraji', nebo 'V Kraji Vysočina'.")
    description = models.TextField(u"Popis", blank=True)
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    # doplnujici informace o kraji
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V m<sup>2</sup>")
    population  = models.IntegerField(u"Počet obyvatel", null=True, blank=True)
    objects     = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Kraj'
        verbose_name_plural = u'Kraje'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('region', [], {'region': self.slug})

    def get_lokativ(self):
        return self.lokativ or self.title


class District(geomodels.Model):
    """
    Okres.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True) # TODO: zjistit, jestli byly v CR okresy shodneho jmena
    lokativ     = models.CharField(u"Lokativ", max_length=200, blank=True, null=True, help_text=u"6.pád, 'O kom, o čem', včetně vyskloňovaného slova 'okres' a předložky, např. 'Ve Vsetínském okrese', nebo 'V Benešovském okrese'.")
    description = models.TextField(u"Popis", blank=True)
    region      = models.ForeignKey(Region, verbose_name=u"Kraj")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    # doplnujici informace o kraji
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V m<sup>2</sup>")
    population  = models.IntegerField(u"Počet obyvatel", null=True, blank=True)
    objects     = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Okres'
        verbose_name_plural = u'Okresy'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        out = ('district', [], {'region': self.region.slug, 'district': self.slug})
        return out

    def get_lokativ(self):
        return self.lokativ or self.title


class Town(geomodels.Model):
    """
    Obec.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    lokativ     = models.CharField(u"Lokativ", max_length=200, blank=True, null=True, help_text=u"6.pád, 'O kom, o čem', včetně předložky, např. 'Ve Valašském Meziříčí', nebo 'V Krně'.")
    description = models.TextField(u"Popis", blank=True)
    district    = models.ForeignKey(District, verbose_name=u"Okres")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    code        = models.CharField(u"Kód obce", max_length=10, blank=True, null=True, help_text=u"Viz http://www.czso.cz/csu/rso.nsf/i/obec_rso, sekce Kód obce")
    point       = geomodels.PointField(u"Bod", null=True, blank=True)
    # doplnujici informace o obci
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V m<sup>2</sup>")
    population  = models.IntegerField(u"Počet obyvatel", null=True, blank=True)
    # denormalizace
    region      = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)
    objects     = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Obec'
        verbose_name_plural = u'Obce'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj.
        """
        self.region = self.district.region
        return super(Town, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        out = ('town', [], {'region': self.region.slug, 'district': self.district.slug, 'town': self.slug})
        return out

    def get_lokativ(self):
        return self.lokativ or self.title


class Zip(models.Model):
    """
    PSC.
    """
    title    = models.CharField(u"PSČ", max_length=10)
    town     = models.ForeignKey(Town, verbose_name=u"Město")
    # denormalizace
    region   = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)
    district = models.ForeignKey(District, verbose_name=u"Okres", editable=False)

    class Meta:
        verbose_name = u'PSČ'
        verbose_name_plural = u'PSČ'
        ordering = ('title', )
        unique_together = (('title', 'town'), )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o normovani PSC (vyrazeni bilych znaku) a ulozeni
        denormalizovanych hodnot pro kraj a okres.
        """
        self.title = Zip.normalize(self.title)
        self.region = self.town.region
        self.district = self.town.district
        return super(Zip, self).save(*args, **kwargs)

    @staticmethod
    def normalize(code):
        return unicode(WHITECHAR_RE.sub('', code))

    def display(self):
        return u"%s %s" % (self.title[:3], self.title[3:])


class Address(geomodels.Model):
    """
    Adresa. Muze se jednat o bod (Namesti 1), obrys (Polaskova 13, Krasno,
    Jizni mesto) ci caru (Polaskova).
    """
    title       = models.CharField(u"Adresa", max_length=200)
    town        = models.ForeignKey(Town, verbose_name=u"Obec")
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    # geometrie
    point       = geomodels.PointField(u"Bod", null=True, blank=True)
    line        = geomodels.LineStringField(u"Čára", null=True, blank=True)
    poly        = geomodels.PolygonField(u"Polygon", null=True, blank=True)
    # denormalizace
    region      = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)
    district    = models.ForeignKey(District, verbose_name=u"Okres", editable=False)
    objects     = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Adresa'
        verbose_name_plural = u'Adresy'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj a okres.
        """
        self.region = self.town.region
        self.district = self.town.district
        return super(Address, self).save(*args, **kwargs)

    def get_geometry(self):
        """
        Vrati geometricky objekt (bod, caru nebo tvar).
        """
        return self.point or self.line or self.poly or None

    def get_geometry_type(self):
        """
        Vrati retezec reprezentujici typ tvaru, ktery je v modelu ulozen
        (point/line/poly).
        """
        return self.point and 'point' or \
               self.line and 'line' or \
               self.poly and 'poly' or None

    def get_hash(self):
        """
        Vrati hash geometrickeho tvaru.
        """
        geometry = self.get_geometry()
        geometry = geometry and geometry.ewkt or ''
        return hashlib.sha224(geometry).hexdigest()



class AltAddress(models.Model):
    """
    Alternativni adresa.
    """
    title   = models.CharField(u"Ulice", max_length=200)
    address = models.ForeignKey(Address, verbose_name=u"Adresa")

    class Meta:
        verbose_name = u'Alternativní adresa'
        verbose_name_plural = u'Alternativní adresy'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


# class AddressSurround(geomodels.Model):
#     """
#     Okoli adresy.
#
#     TODO: co budu delat, kdyz se zmeni typ geo objektu adresy (treba z bodu
#     na polygon?); to bych pak mel vsechna okoli spojena s bodem znicit a
#     pak nejak automaticky generovat nova.
#     bacha ale na to, ze jedna adresa muze mit schvalne v DB i vice ruznych okoli
#     (treba 10m, 100m okoli, apod.); co ale nechci, je treba 10m okoli pro bod,
#     caru a polygon.... jak na to ale kua?
#
#     TODO: a je ted k necemu vubec ten hash?
#     """
#     address  = models.ForeignKey(Address, verbose_name=u"Adresa", related_name="buildings")
#     # okoli
#     distance = models.IntegerField(u"Vzdálenost", blank=True, null=True)
#     surround = geomodels.PolygonField(u"Polygon okolí", null=True, blank=True)
#     hash     = models.CharField(u"Hash základního geo tvaru", max_length=80, editable=False)
#     # denormalizace
#     region   = models.ForeignKey(Region, verbose_name=u"Kraj")
#     district = models.ForeignKey(District, verbose_name=u"Okres")
#     town     = models.ForeignKey(Town, verbose_name=u"Obec")
#     objects  = geomodels.GeoManager()
#
#     class Meta:
#         verbose_name = u'Okolí adresy'
#         verbose_name_plural = u'Okolí adres'
#
#     def get_hash(self):
#         """
#         Vrati hash geometrickeho tvaru.
#         """
#         geometry = self.address.get_geometry()
#         geometry = geometry and geometry.ewkt or ''
#         return hashlib.sha224(geometry).hexdigest()
#
#     def calculate_surround(self, ct1=None, ct2=None):
#         """
#         Vypocita okoli tvaru a vrati jej.
#         """
#         geometry = self.address.get_geometry()
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
