# -*- coding: utf-8 -*-

import logging

from django import forms
from django.contrib.gis.geos import Polygon, Point
from django.template.defaultfilters import iriencode

from hazard.shared.czech import slugify
from hazard.geo.parsers import parse_xml, KMLHandler, LinkHandler, MediaWikiHandler
from hazard.geo.utils import download_content
from hazard.geo.models import Building, Hell
from hazard.geo.geocoders.google import geocode


logger = logging.getLogger(__name__)

class KMLForm(forms.Form):
    """
    Formular pro zadani KML souboru s popisem obrysu verejnych budov a bodu
    s hernami.
    """
    buildings = forms.URLField(label=u'Mapa veřejných budov')
    hells     = forms.URLField(label=u'Mapa heren')

    err_wrong = u"Hm... Se zadaným odkazem si neporadím. Je to skutečně odkaz na KML soubor?"
    err_down = u"Nepovedlo se mi stáhnout odkazovaný KML soubor. Zkuste prosím odeslat formulář znovu."

    def clean_buildings(self):
        return self._common_clean('buildings', 'polygon')

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
        print json
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

    def create_entry(self):
        """
        Vytvori zaznam Entry. Pro vytvoreni objektu pouzije informace ziskane
        prostrednictvim zadanych KML souboru (viz find_entry_information).
        """
        from hazard.geo.models import Entry
        data = self.find_entry_information()

        # zajistime jedinecny slug
        slug = slugify(data['town'])
        if Entry.objects.filter(slug=slug).exists():
            slug = "%s-%i" % (slug, Entry.objects.all().order_by('-id').values_list('id', flat=True)[0] + 1)

        # vytvorime zaznam Entry
        # TODO: mel bych nejak dynamicky menit m100, ale porad nevim podle jakeho algoritmu
        entry, created = Entry.objects.get_or_create(
            title        = data['town'],
            slug         = slug,
            population   = int(data['population']),
            area         = int(data['area']),
            wikipedia    = data['wikipedia_url'],
            hell_url     = self.cleaned_data['hells'],
            building_url = self.cleaned_data['buildings'],
            public       = data['public']
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
                slug        = slugify(building['name']),
                entry       = entry,
                poly        = poly
            )

            # vypocteme okoli budovy
            b.calculate_zone(entry.m100)

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
                slug        = slugify(hell['name']),
                entry       = entry,
                point       = point
            )

            # zjistime zony se kterymi ma podnik konflikt
            b.calculate_conflicts()
            b.calculate_uzone()
