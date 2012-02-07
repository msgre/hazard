# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.core.management.base import BaseCommand

from hazard.campaigns.models import Campaign


class Command(BaseCommand):
    help = u'Podiva se, jestli je v DB nastavena nektera z kampani jako default, a pokud ne, nastavi tak kampan "mf".'

    def handle(self, *args, **options):
        if not Campaign.objects.filter(default=True).exists():
            c = Campaign.objects.get(slug='mf')
            c.default = True
            c.save()
