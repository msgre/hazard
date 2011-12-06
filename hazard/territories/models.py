# -*- coding: utf-8 -*-

import re

from django.db import models
from django.contrib.gis.db import models as geomodels


class Region(models.Model):
    """
    Kraj.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    description = models.TextField(u"Popis", blank=True)
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)

    class Meta:
        verbose_name = u'Kraj'
        verbose_name_plural = u'Kraje'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


class District(models.Model):
    """
    Okres.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True) # TODO: zjistit, jestli byly v CR okresy shodneho jmena
    description = models.TextField(u"Popis", blank=True)
    region      = models.ForeignKey(Region, verbose_name=u"Kraj")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)

    class Meta:
        verbose_name = u'Okres'
        verbose_name_plural = u'Okresy'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


class Town(models.Model):
    """
    Obec.
    """
    title       = models.CharField(u"Název", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    description = models.TextField(u"Popis", blank=True)
    district    = models.ForeignKey(District, verbose_name=u"Okres")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    point       = geomodels.PointField(u"Bod", null=True, blank=True)
    # denormalizace
    region      = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)

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

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o normovani PSC (vyrazeni bilych znaku) a ulozeni
        denormalizovanych hodnot pro kraj a okres.
        """
        self.title = WHITECHAR_RE.sub(self.title, '')
        self.region = self.town.region
        self.district = self.town.district
        return super(Zip, self).save(*args, **kwargs)
