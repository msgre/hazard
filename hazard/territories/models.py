# -*- coding: utf-8 -*-

"""
TODO:
- nejaky slucovac mest podle stejneho zip kodu
"""

import re

from django.db import models
from django.contrib.gis.db import models as geomodels


class Region(geomodels.Model):
    """
    Kraj.

    TODO: pridat rozlohu a pocet lidi
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    lokativ     = models.CharField(u"Lokativ", max_length=200, blank=True, null=True, help_text=u"6.pád, 'O kom, o čem', včetně vyskloňovaného slova 'kraj'.")
    description = models.TextField(u"Popis", blank=True)
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    # doplnujici informace o kraji
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V km<sup>2</sup>")
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

    TODO: pridat rozlohu a pocet lidi
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True) # TODO: zjistit, jestli byly v CR okresy shodneho jmena
    description = models.TextField(u"Popis", blank=True)
    region      = models.ForeignKey(Region, verbose_name=u"Kraj")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    # doplnujici informace o kraji
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V km<sup>2</sup>")
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


class Town(geomodels.Model):
    """
    Obec.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    description = models.TextField(u"Popis", blank=True)
    district    = models.ForeignKey(District, verbose_name=u"Okres")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    point       = geomodels.PointField(u"Bod", null=True, blank=True)
    # doplnujici informace o obci
    surface     = models.FloatField(u"Katastrální výměra", null=True, blank=True, help_text="V km<sup>2</sup>")
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


WHITECHAR_RE = re.compile('\s+')

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
