# -*- coding: utf-8 -*-

from django.db import transaction


# --- pomocne funkce pro slucovani objektu Town do jednoho --------------------
#     (psano obecne, aby to fachalo i v jinych pripadech)

@transaction.commit_manually
def repair_referencies(old_obj, new_obj):
    """
    Pro zadany objekt `old_obj` zjisti vsechny zpetne FK reference, a prenastavi
    je tak, aby ukazovaly na `new_obj`.

    Priklad:

        town1 = Town.objects.get(id=1)
        town2 = Town.objects.get(id=2)
        repair_referencies(town1, town2)

        Tento kod zajisti to, ze vsechny objekty, ktere ukazuji na town1 pres
        vazbu FK budou nove ukazovat na town2.

    TODO:
    Bacha! Facha jen pro FK vazby, pro M2M to teprv budu muset nekdy dodelat.
    (coz ale nebude jednoduche, protoze uz tak mam potize s FK ktere maji
    nastaven unique_together)
    """
    # vytahneme si vsechny zpetne reference
    model = old_obj.__class__
    fks = model._meta.get_all_related_objects()
    log = {
        'old_object': dict(model.objects.filter(id=old_obj.id).values()[0]),
        'new_object': dict(model.objects.filter(id=new_obj.id).values()[0]),
        'affected': {}
    }

    # oprava FK vazeb
    try:
        for fk in fks:
            # vytahneme z DB objekty s referenci na stary objekt
            old_kwargs = {fk.field.name: old_obj}
            qs = fk.model.objects.filter(**old_kwargs)

            # upravime reference
            new_kwargs = {fk.field.name: new_obj}
            uniques = _get_unique_field_lut(fk.model)
            ignore_ids = []
            if fk.field.name in uniques:
                # aaaaa... neprijemne slozitosti

                # objekty, kterym se chystame upravit referenci maji FK uveden
                # v unique_together, tj. musime zajistit, aby upravou nedoslo
                # k duplicitnimu vlozeni dat

                for unique in uniques[fk.field.name]:
                    # tyto atributy (a ID) chceme z modelu vytahnout
                    unique_kwargs = unique[:] + ['id']
                    # vytahneme unique parametry ze stare i nove vazby
                    old_uniques = _get_unique_id_lut(qs.values_list(*unique_kwargs))
                    new_uniques = _get_unique_id_lut(fk.model.objects.filter(**new_kwargs).values_list(*unique_kwargs))
                    # prunik old a new_uniques nam dava zaznamy, ktere nesmime v novem setu updatnout
                    ignore_uniques = set(old_uniques.keys()).intersection(new_uniques.keys())
                    for k in ignore_uniques:
                        ignore_ids.extend(old_uniques[k])

            if ignore_ids:
                qs = qs.exclude(id__in=ignore_ids)

            # ulozime zaznam o presunu
            app = ".".join([fk.model._meta.app_label, fk.model._meta.module_name])
            log['affected'][app] = list(qs.values_list('id', flat=True))

            qs.update(**new_kwargs)
    except:
        transaction.rollback()
        log['affected'] = None
    else:
        transaction.commit()

    return log


def _get_unique_field_lut(model):
    """
    Pomocna funkce, ktera vyzobne z modelu `model` informace v atributu
    unique_together (tj. policka spolecne tvori unikatni kombinaci, ktera
    mohou byt v DB pouze jednou) a pretavi ji do podoby slovniku. Priklad:

    Pro takovyto model:

        class Zip(models.Model):
            title = models.CharField(max_length=10)
            town  = models.ForeignKey()

            class Meta:
                unique_together = (('title', 'town'), )

    ...funkce vrati:

            {
                'title': [['town']],
                'town': [['title']]
            }

    Tj. klic slovniku tvori unique zaznam spolecne s kazdou polozkou v seznamu.
    """
    out = {}
    for item in model._meta.unique_together:
        for field in item:
            if field not in out:
                out[field] = []
            new_item = list(item)
            new_item.pop(new_item.index(field))
            out[field].append(new_item)
    return out


def _get_unique_id_lut(data):
    """
    Vrati slovnik, kde klicem jsou sledovane unique hodnoty objektu z DB, a
    klicem ID daneho objektu.

    Bacha! Posledni hodnota ve values_list musi byt 'id'!

    Priklad:

        qs = Zip.objects.filter(id__in=[1]).values_list('town', 'title', 'id')
        lut = _get_unique_id_lut(qs)

    Vrati:
        {
            (1,2): [1,2,3],
            (1,3): [4],
        }

    Tj. klicem jsou hodnoty ('town', 'title') a pod nim jsou skryta vsechna ID
    objektu Zip, ktera je maji nastaveny.
    """
    lut = {}
    for i in data:
        k = i[:-1]
        if k not in lut:
            lut[k] = []
        lut[k].append(i[-1])
    return lut
