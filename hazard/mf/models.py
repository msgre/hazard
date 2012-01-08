# -*- coding: utf-8 -*-

import itertools

from django.db import models
from django.contrib.gis.db import models as geomodels
from django.db.models.loading import get_model
from django.contrib.gis.gdal import CoordTransform, SpatialReference

from hazard.territories.models import Region, District, Town, Address
from hazard.gobjects.models import Hell, AbstractPlace
from hazard.conflicts.models import AbstractConflict
from hazard.campaigns.models import Campaign
from hazard.shared.fields import JSONField


class MfPlaceType(models.Model):
    """
    Typy mist.

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
        verbose_name = u'Typ místa'
        verbose_name_plural = u'Typy míst'
        ordering = ('title', )

    def __unicode__(self):
        return self.title


class MfPlace(AbstractPlace):
    """
    Misto.
    """
    type    = models.ForeignKey(MfPlaceType, verbose_name=u"Typ místa")
    bid     = models.CharField(u"ID místa", max_length=30, null=True, blank=True, help_text=u"Interní ID místa, které se používalo během procesu získávání GPS pozice z XLS dat")
    note    = models.TextField(u"Poznámka", blank=True)
    json    = JSONField(u"Extra JSON data", null=True, blank=True)
    objects = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Místo'
        verbose_name_plural = u'Místa'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj, okres, obec.
        """
        self.region = self.address.region
        self.district = self.address.district
        self.town = self.address.town
        return super(MfPlace, self).save(*args, **kwargs)


class MfAddressSurround(geomodels.Model):
    """
    Okoli adresy.
    """
    MINIMUM_DISTANCE = 2 # v metrech; pokud se pocita okoli pro bod/caru a neni zadan distance, tak beru tuto hodnotu

    address  = models.ForeignKey(Address, verbose_name=u"Adresa", related_name='surrounds')
    distance = models.IntegerField(u"Vzdálenost", blank=True, null=True, help_text=u"V metrech.")
    poly     = geomodels.PolygonField(u"Polygon okolí", null=True, blank=True)
    hash     = models.CharField(u"Hash základního geo tvaru", max_length=80, editable=False)
    created  = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    # denormalizace
    region   = models.ForeignKey(Region, verbose_name=u"Kraj", editable=False)
    district = models.ForeignKey(District, verbose_name=u"Okres", editable=False)
    town     = models.ForeignKey(Town, verbose_name=u"Obec", editable=False)
    objects  = geomodels.GeoManager()

    class Meta:
        verbose_name = u'Okolí adresy'
        verbose_name_plural = u'Okolí adres'
        ordering = ('-created', )

    def save(self, *args, **kwargs):
        """
        Postara se o ulozeni denormalizovane hodnoty na kraj/okres/mesto.
        """
        self.region = self.address.region
        self.district = self.address.district
        self.town = self.address.town
        return super(MfAddressSurround, self).save(*args, **kwargs)

    @staticmethod
    def calculate_surround(address, distance, ct1=None, ct2=None):
        """
        Vypocita okoli adresy a vrati jej.
        """
        geometry = address.get_geometry()
        if not geometry:
            return None

        # prepocteme WGS84 souradnice tvaru do krovaka
        if ct1 is None:
            ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
        krovak_geometry = geometry.transform(ct1, clone=True)

        # vypocitame okoli tvaru
        if address.get_geometry_type() != 'poly' and (not distance or distance <= 0):
            distance = MfAddressSurround.MINIMUM_DISTANCE
        else:
            distance = distance or 0
        surround = krovak_geometry.buffer(distance)

        # prevedeme okoli zpet na WGS84
        if ct2 is None:
            ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))
        surround.transform(ct2)

        return surround

    @staticmethod
    def create_surround(address, distance, ct1=None, ct2=None, rebuild=False):
        """
        Vytvori "distance" metrove okoli adresy.
        Napr. MfAddressSurround.create_surround(100) vytvori 100 m okoli.
        """
        if rebuild:
            address.surrounds.delete()

        qs = address.surrounds.filter(distance=distance)
        if not qs.exists():
            poly = MfAddressSurround.calculate_surround(address, distance, ct1=ct1, ct2=ct2)
            return MfAddressSurround.objects.create(
                address = address,
                distance = distance,
                poly = poly,
                hash = address.get_hash()
            )

        return qs[0]


class MfPlaceConflict(AbstractConflict):
    """
    Konflikt mezi hernou a mistem.
    """
    place = models.ForeignKey(MfPlace, verbose_name=u"Místo", null=True, blank=True)

    class Meta:
        verbose_name = u'Konflikt mezi hernou a místem'
        verbose_name_plural = u'Konflikty mezi hernami a místy'

    @staticmethod
    def town_conflicts(town, rebuild=False):
        """
        Vypocita konflikty mezi misty a hernami ve meste `town`. Pokud se
        zavola nad stejnym mestem nekolikrat, tak jednou vytvorene konflikty
        se jiz neaktualizuji (tj. muze tam zustat i nejaky neaktualni bordel).
        Pokud se maji konflikty prepocitat uplne z gruntu, je treba nastavit
        parametr rebuild na True.
        """
        if rebuild:
            MfPlaceConflict.objects.filter(place__town=town).delete()

        campaigns = Campaign.objects.filter(app='mf') # zajimaji nas pouze herny ze setu MF

        # vytahneme si konfliktni adresy...
        conflicts = MfPlaceConflict.conflict_addresses(town, campaigns, 'mfaddresssurround_set')
        # ...a pretavime je do konkretnich heren a mist (klic je id adresy, hodnota seznam heren/mist)
        hells = dict([(i.id, i.hell_set.all()) for i in Address.objects.filter(id__in=conflicts.keys())])
        places = dict([(i.id, i.mfplace_set.all()) for i in Address.objects.filter(id__in=set(list(itertools.chain(*conflicts.values()))))])

        # a na zaver, tadaaaa -> konfliktni vazba
        for hell_id, places_id in conflicts.iteritems():
            for hell in hells[hell_id]:
                for place_id in places_id:
                    for place in places[place_id]:
                        MfPlaceConflict.objects.get_or_create(hell=hell, place=place)

    @staticmethod
    def statistics(obj, group_by='town'):
        """
        Vypocita statisticke udaje o hernach v zadanem meste/okrese/kraji.
        Vysledky seskupi do slovniku podle parametru group_by
        (opet mesto/okres/kraj).

        Priklad:
            # statistika pro jedine mesto
            MfPlaceConflict.statistics(Town.objects.get(slug='vsetin'), 'town')

            # statistika pro okres, vysledky seskupene podle mest
            MfPlaceConflict.statistics(District.objects.get(slug='okres-vsetin'), 'town')
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
        flat_conflicts_qs = MfPlaceConflict.objects.filter(hell__id__in=flat_hells_qs.values_list('id', flat=True))
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

        return out
