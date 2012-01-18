# -*- coding: utf-8 -*-

from django.db import models


class Term(models.Model):
    """
    Vysvetleni nejakeho terminu, zkratky.
    """
    title       = models.CharField(u"Termín", max_length=200)
    slug        = models.SlugField(u"Webové jméno", max_length=100, unique=True, help_text=u"Webové jméno pojmu, automaticky generováno z políčka Termín. Příliš dlouhá jména je vhodné manuálně upravit na kratší variantu.")
    description = models.TextField(u"Popis")

    class Meta:
        ordering = ("title", )
        verbose_name = u"Pojem"
        verbose_name_plural = u"Pojmy"

    def __unicode__(self):
        return self.title
