# -*- coding: utf-8 -*-

import itertools

from django.db import models, connections
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.db.models.loading import get_model

from hazard.territories.models import Region, District, Town
from hazard.addresses.models import Address
from hazard.gobjects.models import AbstractShape, Hell
from hazard.conflicts.models import AbstractConflict
from hazard.campaigns.models import Campaign


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


class Building(AbstractShape):
    """
    Budova.
    """
    address  = models.ForeignKey(Address, verbose_name=u"Adresa", related_name="buildings")
    type     = models.ForeignKey(BuildingType, verbose_name=u"Typ budovy")
    bid      = models.CharField(u"ID budovy", max_length=30, null=True, blank=True, help_text=u"Interní ID budovy, které se používalo během procesu získávání GPS pozice z XLS dat")
    note     = models.TextField(u"Poznámka", blank=True)
    # denormalizace
    region   = models.ForeignKey(Region, verbose_name=u"Kraj")
    district = models.ForeignKey(District, verbose_name=u"Okres")
    town     = models.ForeignKey(Town, verbose_name=u"Obec")
    objects  = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Budova'
        verbose_name_plural = u'Budovy'

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj, okres, obec
        a automaticky vypocita okoli budovy.
        """
        # pokud nemame zadan geo tvar, podedime jej z adresy
        if not self.point and not self.line and not self.poly:
            self.point = self.address.point

        # vypocitame okoli budovy
        hash = self.get_hash()
        if not self.surround or self.hash != hash:
            self.hash = hash
            self.surround = self.calculate_surround()

        # denormalizace uzemnich celku
        self.region = self.address.region
        self.district = self.address.district
        self.town = self.address.town

        return super(Building, self).save(*args, **kwargs)

    @staticmethod
    def recalculate_surround(town):
        """
        TODO:
        """
        for building in town.building_set.all():
            building.surround = None
            building.save()


class BuildingConflict(AbstractConflict):
    """
    Konflikt mezi hernou a budovou.
    """
    building = models.ForeignKey(Building, verbose_name=u"Budova", null=True, blank=True)

    class Meta:
        verbose_name = u'Konflikt s budovou'
        verbose_name_plural = u'Konflikty s budovami'


    @staticmethod
    def town_conflicts(town, rebuild=False):
        """
        Vypocita konflikty mezi budovami a hernami ve meste `town`. Pokud se
        zavola nad stejnym mestem nekolikrat, tak jednou vytvorene konflikty
        se jiz neaktualizuji.
        Pokud se maji konflikty prepocitat uplne z gruntu, je treba nastavit
        parametr rebuild na True.
        """
        if rebuild:
            BuildingConflict.objects.filter(building__town=town).delete()

        campaigns = Campaign.objects.filter(app='mf') # zajimaji nas pouze herny ze setu MF
        conflicts = BuildingConflict.find_conflicts(town, campaigns, 'building_set')
        for hell, buildings in conflicts.iteritems():
            for building in buildings:
                BuildingConflict.objects.get_or_create(
                    hell     = hell,
                    building = building
                )

    @staticmethod
    def old_statistics(town):
        """
        Vrati zakladni statisticke udaje o hernach v danem meste.
        """
        campaigns = Campaign.objects.filter(app='mf') # zajimaji nas pouze herny ze setu MF
        hells_qs = town.hell_set.filter(campaigns__in=campaigns)
        machines_total = sum(hells_qs.values_list('total', flat=True))
        conflicts_qs = BuildingConflict.objects.filter(hell__id__in=hells_qs.values_list('id', flat=True))
        conflicts_hells_qs = Hell.objects.filter(id__in=set(conflicts_qs.values_list('hell', flat=True)))

        out = {
            'hells_qs': hells_qs, # vsechny herny v meste (z MF setu)
            'hells_total': hells_qs.count(), # celkem heren
            'machines_total': machines_total, # celkem automatu
            'conflicts_qs': conflicts_qs, # konflikty (herny i budovy se zde mohou opakovat)
            'conflicts_hells_qs': conflicts_hells_qs, # herny v konfliktu
            'conflicts_hells_total': conflicts_hells_qs.count(), # celkem heren v konfliktu
            'conflicts_machines_total': sum(conflicts_hells_qs.values_list('total', flat=True)) # celkem automatu v konfliktu
        }

        # nekonfliktni herny
        out['nonconflicts_hells_total'] = out['hells_total'] - out['conflicts_hells_total']
        # nekonfliktni automaty
        out['nonconflicts_machines_total'] = out['machines_total'] - out['conflicts_machines_total']

        # procentualni hodnoty heren
        if out['hells_total']:
            out['conflicts_hells_perc'] = out['conflicts_hells_total'] / float(out['hells_total']) * 100
            out['nonconflicts_hells_perc'] = 100 - out['conflicts_hells_perc']
        # procentualni hodnoty automatu
        if out['machines_total']:
            out['conflicts_machines_perc'] = out['conflicts_machines_total'] / float(out['machines_total']) * 100
            out['nonconflicts_machines_perc'] = 100 - out['conflicts_machines_perc']

        # hustota heren/matu
        if town.surface:
            out['hells_per_km'] = out['hells_total'] / town.surface
            out['machines_per_km'] = out['machines_total'] / town.surface

        # lidi na hernu/mat
        if town.population:
            out['persons_per_hell'] = town.population / out['hells_total']
            out['persons_per_machines'] = town.population / out['machines_total']

        return out

    @staticmethod
    def statistics(obj, group_by='town'):
        """
        Vypocita statisticke udaje o hernach v zadanem meste/okrese/kraji.
        Vysledky seskupi do slovniku podle parametru group_by
        (opet mesto/okres/kraj).

        Priklad:
            # statistika pro jedine mesto
            BuildingConflict.statistics(Town.objects.get(slug='vsetin'), 'town')

            # statistika pro okres, vysledky seskupene podle mest
            BuildingConflict.statistics(District.objects.get(slug='okres-vsetin'), 'town')
        """
        # zajimaji nas pouze herny ze setu MF
        campaigns = Campaign.objects.filter(app='mf')

        # vytahneme si herny
        hells_kwargs = {
            'campaigns__in': campaigns
        }
        if obj:
            hells_kwargs[obj.__class__.__name__.lower()] = obj
        flat_hells_qs = Hell.objects.filter(**hells_kwargs)

        # celkove mnozstvi heren, seskupenych dle group_by
        # => hell_counts = {ID: pocet}
        hell_counts_qs = flat_hells_qs.values_list(group_by, 'id').order_by(group_by)
        hell_counts = dict([(k, len(list(g))) \
                            for k, g in itertools.groupby(hell_counts_qs, lambda a: a[0])])

        # celkove mnozstvi automatu v hernach, seskupenych dle group_by
        # => machine_counts = {ID: pocet}
        machine_counts_qs = flat_hells_qs.values_list(group_by, 'total').order_by(group_by)
        machine_counts = dict([(k, sum([i[1] for i in g])) \
                                for k, g in itertools.groupby(machine_counts_qs, lambda a: a[0])])

        # pocet konfliktnich heren, seskupenych dle group_by
        # => conflict_hell_counts = {ID: pocet}
        flat_conflicts_qs = BuildingConflict.objects.filter(hell__id__in=flat_hells_qs.values_list('id', flat=True))
        flat_conflict_hell_qs = flat_hells_qs.filter(id__in=set(flat_conflicts_qs.values_list('hell', flat=True)))
        conflict_hell_counts_qs = flat_conflict_hell_qs.values_list(group_by, 'id').order_by(group_by)
        conflict_hell_counts = dict([(k, len(list(g))) \
                                     for k, g in itertools.groupby(conflict_hell_counts_qs, lambda a: a[0])])

        # pocet konfliktnich automatu, seskupenych dle group_by
        # => conflict_machine_counts = {ID: pocet}
        conflict_machine_counts_qs = flat_conflict_hell_qs.values_list(group_by, 'total').order_by(group_by)
        conflict_machine_counts = dict([(k, sum([i[1] for i in g])) \
                                        for k, g in itertools.groupby(conflict_machine_counts_qs, lambda a: a[0])])

        # pocty nekonfliktnich heren/automatu
        nonconflict_hell_counts = dict([(k, hell_counts[k] - conflict_hell_counts[k]) for k in conflict_hell_counts])
        nonconflict_machine_counts = dict([(k, machine_counts[k] - conflict_machine_counts[k]) for k in conflict_machine_counts])

        # procentualni vyjadreni poctu heren/automatu
        conflict_hell_perc = dict([(k, 100 * conflict_hell_counts[k] / float(hell_counts[k])) for k in conflict_hell_counts])
        conflict_machine_perc = dict([(k, 100 * conflict_machine_counts[k] / float(machine_counts[k])) for k in conflict_machine_counts])
        nonconflict_hell_perc = dict([(k, 100 - conflict_hell_perc[k]) for k in conflict_hell_perc])
        nonconflict_machine_perc = dict([(k, 100 - conflict_machine_perc[k]) for k in conflict_machine_perc])

        out = {
            # absolutni celkove pocty
            'hell_counts': hell_counts,
            'machine_counts': machine_counts,
            # absolutni pocty konfliktu
            'conflict_hell_counts': conflict_hell_counts,
            'conflict_machine_counts': conflict_machine_counts,
            # absolutni pocty ne-konfliktu
            'nonconflict_hell_counts': nonconflict_hell_counts,
            'nonconflict_machine_counts': nonconflict_machine_counts,
            # procentualni pocty konfliktu
            'conflict_hell_perc': conflict_hell_perc,
            'conflict_machine_perc': conflict_machine_perc,
            # procentualni pocty ne-konfliktu
            'nonconflict_hell_perc': nonconflict_hell_perc,
            'nonconflict_machine_perc': nonconflict_machine_perc,
        }

        model = get_model('territories', group_by)
        data = dict([(i['id'], i) for i in model.objects.all().values('id', 'surface', 'population')])
        # hustota heren/matu
        out['hell_density'] = dict([(k, out['hell_counts'][k] / data[k]['surface']) for k in data if data[k]['surface']])
        out['machine_density'] = dict([(k, out['machine_counts'][k] / data[k]['surface']) for k in data if data[k]['surface']])

        # lidi na hernu/mat
        out['hell_per_resident'] = dict([(k, data[k]['population'] / out['hell_counts'][k]) for k in data if data[k]['population']])
        out['machine_per_resident'] = dict([(k, data[k]['population'] / out['machine_counts'][k]) for k in data if data[k]['population']])

        return out

    @staticmethod
    def javascript(town, statistics=None):
        """
        Vrati slovnik s daty, ktera pouziva Javascriptovy kod k vykresleni
        vsech potrebnych objektu do mapy.

        TODO: konkretne?
        """
        if not statistics:
            statistics = BuildingConflict.statistics(town)

        conflicts = {}
        buildings = []
        shape = None
        for i in statistics['conflicts_qs'].values('hell', 'building'):
            if i['hell'] not in conflicts:
                conflicts[i['hell']] = {'buildings': []}
            conflicts[i['hell']]['buildings'].append(i['building'])
            buildings.append(i['building'])

        surrounds = dict([(i.id, i.surround) for i in Building.objects.filter(id__in=set(buildings)).only('id', 'surround')])

        for k in conflicts:
            shapes = [surrounds[i] for i in conflicts[k]['buildings']]
            shape = reduce(lambda a, b: a.union(b), shapes[1:], shapes[0])
            conflicts[k]['shape'] = shape.coords

        out = {
            'js_hells': dict([(i['id'], i) for i in statistics['hells_qs'].values('address', 'description', 'title', 'total', 'id')]),
            'js_gobjects': dict([(i.id, {
                                  'id': i.id,
                                  'title': i.title,
                                  'description': i.description,
                                  'address': i.address_id,
                                  'type_id': i.type_id,
                                  'distance': i.distance,
                                  'geometry': i.get_geometry().coords,
                                  'geometry_type': i.get_geometry_type(),
                                  'surround': list(i.surround.coords)}) for i in Building.objects.filter(town=town)]),
            'js_conflicts': conflicts
        }
        address_ids = set([i['address'] for i in out['js_hells'].values()] + \
                          [i['address'] for i in out['js_gobjects'].values()])
        out['js_addresses'] = dict([(i['id'], i) for i in Address.objects.filter(id__in=address_ids).values('id', 'title', 'slug', 'point')])
        for k in out['js_addresses']:
            out['js_addresses'][k]['point'] = list(out['js_addresses'][k]['point'].coords)

        return out
