# -*- coding: utf-8 -*-

import logging

from django import forms
from django.contrib.gis.geos import Polygon, Point
from django.template.defaultfilters import iriencode
from django.contrib.gis.gdal import CoordTransform, SpatialReference

from hazard.shared.czech import slugify
from hazard.geo.parsers import parse_xml, KMLHandler, LinkHandler, MediaWikiHandler
from hazard.geo.utils import download_content, get_unique_slug
from hazard.geo.models import Building, Hell
from hazard.geo.geocoders.google import geocode


logger = logging.getLogger(__name__)

M100 = 100 # okoli budov v metrech


class KMLForm(forms.Form):
    """
    Formular pro zadani KML souboru s popisem obrysu verejnych budov a bodu
    s hernami.
    """
    hells     = forms.URLField(label=u'Mapa heren')
    buildings = forms.URLField(label=u'Mapa budov')
    email     = forms.EmailField(label=u'Kontaktní email', required=False)

    err_wrong = u"Hm... Se zadaným odkazem si neporadím. Je to skutečně odkaz na KML soubor?"
    err_down = u"Nepovedlo se mi stáhnout odkazovaný KML soubor. Zkuste prosím odeslat formulář znovu."

    def clean_buildings(self):
        """
        Budovy mohou byt v KML zadany budto jako polygony, nebo jako jednoduche
        body (spendliky). Body se ale zde prevedenou na male kolecka (polygony),
        protoze veskery ostatni kod s tim pocita.
        """
        # normalne rozparsujeme KML
        url = self._common_clean('buildings', ['polygon', 'point'])

        # no ale ted rozdelime vysledek na 2 hromadky: polygony a body
        points = [i for i in self.buildings_data if i['type'] == 'point']
        polys = [i for i in self.buildings_data if i['type'] != 'point']

        # hromadku bodu prevedeme na malinke polygony (male kolca)
        out = []
        ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
        ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))
        for point in points:
            _point = Point(point['coordinates'][0]['lon'], point['coordinates'][0]['lat'], srid=4326)
            m_point = _point.transform(ct1, clone=True)
            m_point2 = m_point.buffer(3)
            m_point2.transform(ct2)
            point['coordinates'] = [dict(zip(['lon', 'lat'], i)) for i in m_point2.coords[0]]
            out.append(point)

        # no a vratime origos polygony a nase pretransformovane body na kolca
        self.buildings_data = polys + out
        return url

    def clean_hells(self):
        return self._common_clean('hells', 'point')

    def _common_clean(self, att, filter=None):
        """
        Spolecna funkce pro clean_XXX metody. Zadany KML soubor rozparsuje a
        vytahne z nej nosne informace pod atribut `att`_data (napr. polygon_data).
        """
        data = self.cleaned_data.get(att)

        if data:
            # stahneme KML soubor
            content = download_content(data)
            if content is None:
                # chyba behem downloadu
                logger.info('Problem with downloading URL %s' % data)
                raise forms.ValidationError(self.err_down)
            setattr(self, '%s_kml' % att, content)

            # rozparsujeme zadany KML
            parsed_data = parse_xml(KMLHandler(), content, filter)
            if not parsed_data:
                logger.info('Content of %s does not contain geo data' % data)
                # ha! mozna jsme dostali link na "spatny" KML, overime si to
                parsed_data2 = parse_xml(LinkHandler(), content)
                if len(parsed_data2) != 1:
                    logger.info('Content of %s does not contain link data' % data)
                    # uzivatel zadal asi nejake spatne URL
                    raise forms.ValidationError(self.err_wrong)

                # mame nove URL, zkusime to s nim znovu
                new_url = parsed_data2[0]
                logger.info('Content of %s contain link to %s' % (data, new_url))
                # stahneme KML soubor
                content = download_content(new_url)
                if content is None:
                    # chyba behem downloadu
                    logger.info('Problem with downloading URL %s' % new_url)
                    raise forms.ValidationError(self.err_down)
                setattr(self, '%s_kml' % att, content)

                # rozparsujeme novy KML
                parsed_data = parse_xml(KMLHandler(), content, filter)
                if not parsed_data:
                    # tak ani odkaz ze "spatneho" KML nas nikam nedovedl
                    logger.info('Content of %s does not contain geo data' % new_url)
                    raise forms.ValidationError(self.err_wrong)

                data = new_url

            setattr(self, '%s_data' % att, parsed_data)

        return data

    def find_center(self):
        """
        Vrati prumerny stred ze vsech heren. Ze ziskane pozice se pak snazim
        najit podrobnejsi geo informace (napr. o jake mesto vlastne jde).
        """
        coords = [(i['coordinates'][0]['lon'], i['coordinates'][0]['lat']) \
                  for i in self.hells_data]
        avg_lon = sum([i[0] for i in coords]) / float(len(coords))
        avg_lat = sum([i[1] for i in coords]) / float(len(coords))
        return {'lat': avg_lat, 'lon': avg_lon}

    def find_town(self, pos):
        """
        Pokusi se pres Google Geocode service zjistit kteremu mestu odpovida
        zadana pozice `pos`.
        """
        json = geocode("%(lat)s, %(lon)s" % pos, '') # TODO: API key
        try:
            town = json['Placemark'][0]['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea']['SubAdministrativeAreaName']
        except (KeyError, IndexError):
            town = None
        return town

    def guess_wikipedia_url(self, town):
        """
        Vrati URL do Wikipedie, na kterem je mozne ziskat XML data o obci.
        """
        mask = u'http://en.wikipedia.org/w/index.php?title=Special:Export&pages=%s&curonly=1&action=submit'
        return iriencode(mask % town.replace(' ', '_'))

    def find_entry_information(self):
        """
        Zjisti dodatecne informace ze zadanych KML souboru. Co presne?

        * vypocita geograficky stred vsech heren
        * podle lat/lon pozice pres google zjisti nazev mesta
        * z wikipedie vyzobne informaci o poctu obyvatel a rozloze

        Tyto informace slouzi pro naplneni zaznamu Entry.
        """
        out = {'town': u'Neznámé místo', 'wikipedia_url': None, 'public': False}
        pos = self.find_center()
        town = self.find_town(pos)
        if town:
            out['town'] = town
            out['wikipedia_url'] = self.guess_wikipedia_url(town)
            wikipedia_content = download_content(out['wikipedia_url'])
            if wikipedia_content:
                out.update(parse_xml(MediaWikiHandler(), wikipedia_content))
                if out['population'] and out['area']:
                    out['public'] = True
        return out

    def create_entry(self, ip=''):
        """
        Vytvori zaznam Entry. Pro vytvoreni objektu pouzije informace ziskane
        prostrednictvim zadanych KML souboru (viz find_entry_information).
        """
        from hazard.geo.models import Entry
        data = self.find_entry_information()

        # zajistime jedinecny slug
        slug = get_unique_slug(data['town'][:99])

        # vytvorime zaznam Entry
        entry, created = Entry.objects.get_or_create(
            title        = data['town'],
            slug         = slug,
            population   = int(data['population']),
            area         = int(data['area']),
            wikipedia    = data['wikipedia_url'],
            hell_url     = self.cleaned_data['hells'],
            hell_kml     = self.hells_kml,
            building_url = self.cleaned_data['buildings'],
            building_kml = self.buildings_kml,
            public       = data['public'],
            email        = self.cleaned_data['email'],
            ip           = ip
        )
        return entry, created

    def save(self, entry):
        """
        Ulozi vyparsovane body s hernami, obrysy budov a jejich okoli pod zaznam
        `entry`.
        """
        self.save_buildings(entry)
        self.save_hells(entry)

    def save_buildings(self, entry):
        """
        Ulozi vyparsovane obrysy budov. Ke kazde budove vypocita jeji obrys.
        """
        for building in self.buildings_data:
            # vytvorime polygon
            coords = [(i['lon'], i['lat']) for i in building['coordinates']]
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            if not coords:
                logger.info('No coordinates information in KML data for %s record' % building['name'])
                continue

            poly = Polygon(coords, srid=4326)

            # ulozime zaznam o budove do DB
            b = Building.objects.create(
                title       = building['name'],
                description = building['description'],
                slug        = slugify(building['name'][:99]),
                entry       = entry,
                poly        = poly
            )

            # vypocteme okoli budovy
            b.calculate_zone(M100)

    def save_hells(self, entry):
        """
        Ulozi vyparsovane body s hernami. Pro kazdou z heren zjisti seznam zon,
        se kterymi je v konfliktu.
        """
        for hell in self.hells_data:
            # vytvorime bod
            coords = [(i['lon'], i['lat']) for i in hell['coordinates']]
            point = Point(hell['coordinates'][0]['lon'], hell['coordinates'][0]['lat'], srid=4326)

            # ulozime zaznam o budove do DB
            b = Hell.objects.create(
                title       = hell['name'],
                description = hell['description'],
                slug        = slugify(hell['name'][:99]),
                entry       = entry,
                point       = point
            )

            # zjistime zony se kterymi ma podnik konflikt
            b.calculate_conflicts()
            b.calculate_uzone()

        # vypocet denormalizovanych hodnot
        entry.recalculate_denormalized_values(True)
        entry.save()
