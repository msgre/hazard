# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as geomodels

from hazard.territories.models import Region, District, Town
from hazard.addresses.models import Address


class Hell(models.Model):
    """
    Herna.
    """
    title       = models.CharField(u"Název", blank=True, max_length=200)
    address     = models.ForeignKey(Address, verbose_name=u"Adresa")
    description = models.TextField(u"Popis", blank=True)
    visible     = models.BooleanField(u"Viditelné?", default=True)
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # pocty automatu
    emr_count   = models.IntegerField(u'EMR', default=0, help_text=u'Elektromechanická ruleta')
    vtz_count   = models.IntegerField(u'VTZ', default=0, help_text=u'Vícemístné hrací zařízení')
    vhp_count   = models.IntegerField(u'VHP', default=0, help_text=u'Výherní hrací přístroj')
    vlt_count   = models.IntegerField(u'VLT', default=0, help_text=u'Videoloterijní terminál')
    ivt_count   = models.IntegerField(u'IVT', default=0, help_text=u'Interaktivní videoloterijní terminál')
    # denormalizace
    region      = models.ForeignKey(Region, verbose_name=u"Kraj")
    district    = models.ForeignKey(District, verbose_name=u"Okres")
    town        = models.ForeignKey(Town, verbose_name=u"Obec")
    total       = models.IntegerField(default=0, editable=False)

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

        self.total = sum([self.emr_count, self.vtz_count, self.vhp_count,
                          self.vlt_count, self.ivt_count])

        return super(Hell, self).save(*args, **kwargs)


class BuildingType(models.Model):
    """
    Typy budov.

    TODO: dat do initials_data:

        # TODO: mam ty typy sloucit? socialni peci nemame?
        (u'nezname', u'Neznámé'),
        (u'zdravi', u'Zařízení zdravotní péče'),
        (u'cirkev', u'Budovy církví'),
        (u'skoly', u'Školy a školská zařízení'),
        (u'obce', u'?'),
        (u'lekarny', u'?'),
        (u'ministerstvo', u'Budovy státních orgánů'),
        (u'socialni', u'Zařízení sociální péče'),
    """
    title       = models.CharField(u"Název", max_length=200)
    description = models.TextField(u"Popis", blank=True)

    class Meta:
        verbose_name = u'Typ budovy'
        verbose_name_plural = u'Typy budov'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


class Building(models.Model):
    """
    Budova.
    """
    title       = models.CharField(u"Název", max_length=200)
    address     = models.ForeignKey(Address, verbose_name=u"Adresa")
    description = models.TextField(u"Popis", blank=True)
    visible     = models.BooleanField(u"Viditelné?", default=True)
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)
    # specificke atributy
    type        = models.ForeignKey(BuildingType, verbose_name=u"Typ budovy")
    shape       = geomodels.PolygonField(u"Tvar", null=True, blank=True)
    bid         = models.CharField(u"ID budovy", max_length=30, null=True, blank=True, help_text=u"Interní ID budovy, které se používalo během procesu získávání GPS pozice z XLS dat")
    # denormalizace
    point       = geomodels.PointField(u"Bod", null=True, blank=True)
    region      = models.ForeignKey(Region, verbose_name=u"Kraj")
    district    = models.ForeignKey(District, verbose_name=u"Okres")
    town        = models.ForeignKey(Town, verbose_name=u"Obec")

    class Meta:
        verbose_name = u'Budova'
        verbose_name_plural = u'Budovy'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj, okres, obec
        a geograficky bod.
        """
        self.point = self.address.point

        self.region = self.address.region
        self.district = self.address.district
        self.town = self.address.town

        return super(Building, self).save(*args, **kwargs)
