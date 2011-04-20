# -*- coding: utf-8 -*-

from django.db.models.signals import pre_delete, post_save
from hazard.geo.models import Hell


def update_denormalized_hell(sender, **kwargs):
    """
    Vypocet denormalizovanych statistickych hodnot v zaznamu Entry.
    """
    hell = kwargs.get('instance')
    entry = hell.entry
    recalculate_counts = False

    if kwargs.get('created', False):
        # byl vytvoren novy zaznam o herne
        entry.dhell_count += 1
        if hell.in_conflict == False:
            entry.dok_hell_count += 1
    elif kwargs.get('delete', False):
        # bude zrusen existujici zaznam o herne
        entry.dhell_count -= 1
        if hell.in_conflict == False:
            entry.dok_hell_count -= 1
    else:
        # objekt Hell byl zmenen a tezko rict jak; denormalizace se proto musi
        # provest "tezkou" cestou (aktualni pocty Hell zaznamu se vytahnou
        # dotazem na DB)
        recalculate_counts = True

    # aktualizace denormalizovanych hodnot
    entry.recalculate_denormalized_values(recalculate_counts)
    entry.save()


def update_denormalized_hell_by_delete(sender, **kwargs):
    kwargs['delete'] = True
    return update_denormalized_hell(sender, **kwargs)


post_save.connect(update_denormalized_hell, sender=Hell, dispatch_uid='update_denormalized_hell for *.post_save')
pre_delete.connect(update_denormalized_hell_by_delete, sender=Hell, dispatch_uid='update_denormalized_hell_by_delete for *.pre_delete')
