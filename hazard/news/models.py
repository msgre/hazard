# -*- coding: utf-8 -*-
from django.db import models

class New(models.Model):
    """
    Aktualitky.
    """
    title      = models.CharField(u"Titulek", max_length=200)
    slug       = models.SlugField(u"Webové jméno", max_length=100, unique=True, help_text=u"Webové jméno zprávy, automaticky generováno z políčka Titulek. Příliš dlouhá jména je vhodné manuálně upravit na kratší variantu.")
    content    = models.TextField(u"Obsah")
    annotation = models.TextField(u"Anotace", blank=True, help_text=u"Krátká anotace obsahu zprávy.")
    created    = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    public     = models.BooleanField(u"Publikováno?", default=False, help_text=u"Dokud nebude zpráva publikována, neobjeví se na webu (tj. může se v klidu ladit její finální podoba, protože se zobrazí pouze správci webu).")

    class Meta:
        ordering = ("-created", )
        get_latest_by = 'created'
        verbose_name = u"Zpráva"
        verbose_name_plural = u"Zprávy"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('new-detail', (), {'slug': self.slug})
