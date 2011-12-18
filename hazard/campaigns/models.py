# -*- coding: utf-8 -*-

import re

from django.db import models


class Campaign(models.Model):
    """
    Kampan.

    Eviduje aplikace v celem projektu, ktere prezentuji nejakou kampan nad
    ulozenymi daty.
    """
    title       = models.CharField(u"Název", max_length=200)
    short_title = models.CharField(u"Zkrácený název", max_length=100, blank=True, null=True)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    description = models.TextField(u"Popis", blank=True)
    order       = models.IntegerField(u"Pořadí", default=100)
    visible     = models.BooleanField(u"Viditelná kampaň?", default=True)
    app         = models.CharField(u"Jméno aplikace", max_length=50)
    default     = models.BooleanField(u"Výchozí kampaň?", default=False)
    created     = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    updated     = models.DateTimeField(u"Datum poslední aktualizace", auto_now=True, editable=False)

    class Meta:
        verbose_name = u'Kampaň'
        verbose_name_plural = u'Kampaně'
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def get_title(self):
        return self.short_title or self.title
