# -*- coding: utf-8 -*-

import pickle

from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point, Polygon

from hazard.geo.utils import get_unique_slug


class Entry(models.Model):
    """
    Zaznam jedne obce/mesta.
    """
    title        = models.CharField(u"Název", max_length=200)
    slug         = models.SlugField(u"Webové jméno", max_length=100, unique=True)
    description  = models.TextField(u"Popis", blank=True)
    population   = models.IntegerField(u"Populace", blank=True, null=True)
    area         = models.IntegerField(u"Plocha katastrálního území", blank=True, null=True)
    wikipedia    = models.URLField(u"URL na Wikipedii", blank=True, null=True)
    hell_url     = models.URLField(u"URL na KML s popisem heren", blank=True, null=True)
    hell_kml     = models.TextField(editable=False)
    building_url = models.URLField(u"URL na KML s popisem veřejných budov", blank=True, null=True)
    building_kml = models.TextField(editable=False)
    public       = models.BooleanField(u"Veřejný záznam", default=False)
    created      = models.DateTimeField(u"Datum vytvoření", auto_now_add=True, editable=False)
    email        = models.EmailField(u"Kontaktní email", blank=True)
    ip           = models.CharField(u"IP adresa", max_length=40, blank=True)
    # denormalizovane hodnoty
    dperc           = models.FloatField(u"% protiprávních", editable=False, default=0)
    dhell_count     = models.FloatField(u"Počet heren", editable=False, default=0)
    dok_hell_count  = models.FloatField(editable=False, default=0)
    dper_population = models.FloatField(u"Obyvatel/hernu", editable=False, default=0)
    dper_area       = models.FloatField(u"Heren/km", editable=False, default=0)
    dpoint          = geomodels.PointField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = u'Záznam obce'
        verbose_name_plural = u'Záznamy obcí'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('entry-detail', kwargs={'slug': self.slug})

    def recalculate_denormalized_values(self, counts=False):
        """
        Prepocita denormalizovane statisticke udaje o hernach v obci.
        """
        if counts:
            self.dhell_count = self.hell_set.count()
            self.dok_hell_count = self.hell_set.filter(zones__isnull=True).count()
        if self.dhell_count > 0.0 and self.population > 0.0:
            self.dperc = float(self.dhell_count - self.dok_hell_count) / self.dhell_count * 100
            self.dper_population = float(self.population) / self.dhell_count
        if self.area > 0.0:
            self.dper_area = float(self.dhell_count) / self.area

        # stred zaznamu se udela z prumerne pozice heren
        coords = [i.point.coords for i in self.hell_set.all() if i.point]
        avg_lat = sum([i[1] for i in coords]) / len(coords)
        avg_lon = sum([i[0] for i in coords]) / len(coords)
        self.dpoint = Point(avg_lon, avg_lat, srid=4326)

    def dump(self, filename=None):
        """
        Ulozi kompletni strukturu dat popisujici jeden zaznam Entry. Vraci
        slovnik s daty a pokud je zadan parametr `filename`, pak vysledek
        "zpickluje" a ulozi do zadaneho souboru.
        """
        out = {'entry': {}, 'zones': {}, 'buildings': {}, 'hells': {}}
        zones = []

        # zaznam Entry
        out['entry'] = Entry.objects.filter(slug=self.slug).values()[0]
        out['entry']['dpoint'] = self.dpoint.coords

        # budovy
        for building in self.building_set.all():
            out['buildings'][building.id] = {
                'title':       building.title,
                'description': building.description,
                'slug':        building.slug,
                'poly':        building.poly.coords[0],
                'zone':        building.zone_id
            }
            zones.append(building.zone_id)

        # herny
        for hell in self.hell_set.all():
            out['hells'][hell.id] = {
                'title':            hell.title,
                'description':      hell.description,
                'slug':             hell.slug,
                'point':            hell.point.coords,
                'zones':            hell.zones.all().values_list('id', flat=True),
                'uzone':            hell.uzone_id,
                'zones_calculated': hell.zones_calculated
            }
            zones.append(hell.uzone_id)
            zones.extend(out['hells'][hell.id]['zones'])

        # zones
        for zone in Zone.objects.filter(id__in=set(zones)):
            out['zones'][zone.id] = {'poly': zone.poly.coords[0]}

        # ulozeni do souboru
        if filename:
            f = open(filename, 'wb')
            pickle.dump(out, f)
            f.close()

        return out

    @staticmethod
    def load(data_or_filename):
        """
        Vytvori komplet novy zaznam o jednom Entry podle dodanych dat.
        Data mohou byt zadana ve forme slovniku nebo cesty k pickle souboru
        (produkt Entry.dump). Nove naimportovana data budou mit jina ID, a
        zaznam Entry mozna i jiny slug.

        NOTE: Bacha! Pokud je parametr `data_or_filename` slovnik, bude jeho
        struktura mirne modifikovana (zaznamy zones dostanou novy klic 'new_id'
        s nove vytvorenym Zone.id).
        """
        # data jsou predana budto jako slovnik nebo cesta k pickle souboru
        if type(data_or_filename) in [type(''), type(u'')]:
            f = open(data_or_filename, 'rb')
            data = pickle.load(f)
            f.close()
        else:
            data = data_or_filename

        # zaznam Entry
        slug, exists = get_unique_slug(data['entry']['title'])
        entry = Entry.objects.create(
            title           = data['entry']['title'],
            slug            = slug,
            description     = data['entry']['description'],
            population      = data['entry']['population'],
            area            = data['entry']['area'],
            wikipedia       = data['entry']['wikipedia'],
            hell_url        = data['entry']['hell_url'],
            hell_kml        = data['entry']['hell_kml'],
            building_url    = data['entry']['building_url'],
            building_kml    = data['entry']['building_kml'],
            public          = data['entry']['public'],
            created         = data['entry']['created'],
            dperc           = data['entry']['dperc'],
            dhell_count     = data['entry']['dhell_count'],
            dok_hell_count  = data['entry']['dok_hell_count'],
            dper_population = data['entry']['dper_population'],
            dper_area       = data['entry']['dper_area'],
            dpoint          = Point(data['entry']['dpoint'][0], data['entry']['dpoint'][1], srid=4326)
        )

        # zones
        for zone_id, zone in data['zones'].iteritems():
            z = Zone.objects.create(poly=Polygon(zone['poly'], srid=4326))
            data['zones'][zone_id]['new_id'] = z.id

        # herny
        for hell_id, hell in data['hells'].iteritems():
            h = Hell.objects.create(
                title            = hell['title'],
                description      = hell['description'],
                slug             = hell['slug'],
                entry            = entry,
                point            = Point(hell['point'][0], hell['point'][1], srid=4326),
                uzone            = hell['uzone'] and Zone.objects.get(id=data['zones'][hell['uzone']]['new_id']) or None,
                zones_calculated = hell['zones_calculated']
            )
            zones = [data['zones'][i]['new_id'] for i in hell['zones']]
            h.zones.add(*Zone.objects.filter(id__in=zones))

        # budovy
        for building_id, building in data['buildings'].iteritems():
            b = Building.objects.create(
                title       = building['title'],
                description = building['description'],
                slug        = building['slug'],
                entry       = entry,
                zone        = Zone.objects.get(id=data['zones'][building['zone']]['new_id']),
                poly        = Polygon(building['poly'], srid=4326)
            )


class Zone(models.Model):
    """
    Obrys okoli verejne budovy.
    """
    poly = geomodels.PolygonField(u"Obrys okolí")

    class Meta:
        verbose_name = u'Okolí veřejné budovy'
        verbose_name_plural = u'Okolí veřejných budov'


class CommonInfo(models.Model):
    """
    Spolecne atributy verejnych budov a heren.
    """
    title       = models.CharField(u"Název", max_length=200)
    description = models.TextField(u"Popis", blank=True)
    slug        = models.SlugField(u"Webové jméno", max_length=100)
    entry       = models.ForeignKey(Entry, verbose_name=u"Záznam")

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Building(CommonInfo):
    """
    Verejna budova.
    """
    poly = geomodels.PolygonField(u"Obrys budovy")
    zone = models.ForeignKey(Zone, verbose_name=u"Zóna", blank=True, null=True)

    class Meta:
        verbose_name = u'Veřejná budova'
        verbose_name_plural = u'Veřejné budovy'

    def calculate_zone(self, distance):
        """
        Vypocita okoli budovy a ulozi jej do self.zone.
        """
        # pokud uz nejake okoli vypocitane mame, odstranime je...
        if self.zone:
            self.zone.delete()

        # prepocteme WGS84 souradnice obrysu budovy do krovaka
        ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
        m_poly = self.poly.transform(ct1, clone=True)

        # vypocitame okoli/sousedstvi budovy
        zone = m_poly.buffer(distance)

        # prevedeme okoli zpet na WGS84
        ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))
        zone.transform(ct2)

        # vytvorime v DB novy objekt
        self.zone = Zone.objects.create(poly=zone)
        self.save()


class Hell(CommonInfo):
    """
    Herna.
    """
    point = geomodels.PointField(u"Poloha")
    zones = models.ManyToManyField(Zone, related_name='hells', verbose_name=u'Zakázané zóny')
    uzone = models.ForeignKey(Zone, editable=False, blank=True, null=True)
    zones_calculated = models.BooleanField(editable=False, default=False)

    class Meta:
        verbose_name = u'Herna'
        verbose_name_plural = u'Herny'

    def calculate_conflicts(self):
        """
        Zjisti, do kterych oblasti herna zasahuje a ulozi je do atributu `zones`.
        """
        zones = []
        self.zones.clear()
        self.zones_calculated = False
        self.save()

        for building in self.entry.building_set.all():
            if building.zone.poly.contains(self.point):
                zones.append(building.zone)

        self.zones.add(*zones)
        self.zones_calculated = True
        self.save()

    def calculate_uzone(self):
        """
        Udela sjednoceni vsech zon, ktere se k herne vazou. Vysledkem je jediny
        velky polygon.
        """
        uzone = None
        for zone in self.zones.all():
            if uzone:
                uzone = zone.poly.union(uzone)
            else:
                uzone = zone.poly
        if uzone:
            self.uzone = Zone.objects.create(poly=uzone)
            self.save()

    def is_in_conflict(self):
        if not self.zones_calculated:
            return None
        return self.zones.count() > 0
    in_conflict = property(is_in_conflict)

#import signals
