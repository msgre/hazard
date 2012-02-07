# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from optparse import make_option

from django.core.management.base import BaseCommand

from hazard.campaigns.models import Campaign
from hazard.mf.models import MfPlace, MfAddressSurround
from hazard.territories.models import Address


class Command(BaseCommand):
    help = u'Vypocita 100 m okoli okolo chranenych budov.'

    option_list = BaseCommand.option_list + (
        make_option('--no-counter',
            dest='no_counter',
            action="store_true",
            help=u'Vypne vypisovani pocitadla zpracovanych zaznamu.'),
    )

    def handle(self, *args, **options):
        addresses = list(set(MfPlace.objects.all().values_list('address', flat=True)))
        total = len(addresses)
        for idx, addr in enumerate(Address.objects.filter(id__in=addresses)):
            if not options['no_counter']:
                if self.stdout:
                    msg = '%i / %i' % (idx + 1, total)
                    self.stdout.write(u'%s\n' % msg.strip())
            MfAddressSurround.create_surround(addr, 100, rebuild=True)
