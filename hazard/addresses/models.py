# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as geomodels

from hazard.territories.models import Region, District, Town


class Address(geomodels.Model):
    """
    Adresa.
    """
    title   = models.CharField(u"Ulice", max_length=200)
    town    = models.ForeignKey(Town, verbose_name=u"Obec")
    slug    = models.SlugField(u"Webové jméno", max_length=100)
    point   = geomodels.PointField(u"Bod", null=True, blank=True)
    # denormalizace
    region   = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)
    district = models.ForeignKey(District, verbose_name=u"Okres", editable=False)
    objects  = geomodels.GeoManager()

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
