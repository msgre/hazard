# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete

from hazard.gobjects.models import MachineCount, Hell


def update_machine_count(sender, **kwargs):
    """
    Udrzuje aktualni cislo o celkovem poctu automatu v herne.
    """
    hell = kwargs['instance'].hell
    if hell:
        total = sum(MachineCount.objects.filter(hell=hell).values_list('count', flat=True))
        Hell.objects.filter(id=hell.id).update(total=total)


post_save.connect(update_machine_count, sender=MachineCount, dispatch_uid="post_save for MachineCount")
pre_delete.connect(update_machine_count, sender=MachineCount, dispatch_uid="pre_delete for MachineCount")
