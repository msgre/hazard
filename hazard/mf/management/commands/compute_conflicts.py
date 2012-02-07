# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from optparse import make_option

from django.core.management.base import BaseCommand

from hazard.mf.models import MfPlaceConflict
from hazard.territories.models import Town


class Command(BaseCommand):
    help = u'Vypocita konfliktni herny.'

    option_list = BaseCommand.option_list + (
        make_option('--no-counter',
            dest='no_counter',
            action="store_true",
            help=u'Vypne vypisovani pocitadla zpracovanych zaznamu.'),
    )

    def handle(self, *args, **options):
        towns = Town.objects.all()
        total = towns.count()
        for idx, town in enumerate(towns):
            if not options['no_counter']:
                if self.stdout:
                    msg = '%i / %i' % (idx + 1, total)
                    self.stdout.write(u'%s\n' % msg.strip())
            MfPlaceConflict.town_conflicts(town, True)
