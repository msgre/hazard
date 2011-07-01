# -*- coding: utf-8 -*-

import logging
import hashlib
import random
import time

from django import forms
from django.contrib.gis.geos import Polygon, Point
from django.template.defaultfilters import iriencode
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.forms.util import ErrorList
from django.contrib.gis.measure import D
from django.core.cache import cache
from django.core.mail import send_mail

from hazard.shared.czech import slugify
from hazard.geo.parsers import parse_xml, KMLHandler, LinkHandler, MediaWikiHandler
from hazard.geo.utils import download_content, get_unique_slug
from hazard.geo.models import Building, Hell, Entry
from hazard.geo.geocoders.google import geocode


logger = logging.getLogger(__name__)

M100 = 100 # okoli budov v metrech
KM20 = 20  # pokud se zadava duplicitni zaznam pro obec kterou uz mame v DB, pak se kontroluje, jak daleko je novy zaznam od stareho. Pokud je moc blizko, pak se ulozi do DB jako neverejny


class PbrErrorList(ErrorList):
    """
    Custom trida pro formatovani error hlasek ve formularich (<p>error1<br>
    error2<br>...</p>).
    """

    def __unicode__(self):
        return self.as_pbr()

    def as_pbr(self):
        if not self: return u''
        return u'<p class="errorlist">%s</p>' % '<br>'.join(self)


class KMLForm(forms.Form):
    """
    Formular pro zadani KML souboru s popisem obrysu verejnych budov a bodu
    s hernami.
    """
    hells     = forms.URLField(label=u'Mapa heren')
    buildings = forms.URLField(label=u'Mapa budov')
    email     = forms.EmailField(label=u'Kontaktní email', help_text=u"Váš email nikde nezveřejníme, ani neposkytneme třetím stranám. Použijeme jej pouze, když budeme potřebovat pomoci s Vámi vytvořenou mapou.", required=False)
    slug      = forms.CharField(required=False, widget=forms.HiddenInput)

    err_wrong = u"Hm... Se zadaným odkazem si neporadím. Je to skutečně odkaz na KML soubor?"
    err_down = u"Nepovedlo se mi stáhnout odkazovaný KML soubor. Zkuste prosím odeslat formulář znovu."

    error_css_class = "error"
    required_css_class = "required"

    def __init__(self, *args, **kwargs):
        self.ip = kwargs.pop('ip', None)
        super(KMLForm, self).__init__(*args, **kwargs)
        self.update_no_change_slug = None

    def _clean_buildings(self):
        """
        Budovy mohou byt v KML zadany budto jako polygony, nebo jako jednoduche
        body (spendliky). Body se ale zde prevedenou na male kolecka (polygony),
        protoze veskery ostatni kod s tim pocita.
        """
        # normalne rozparsujeme KML
        url, err = self._common_clean('buildings', ['polygon', 'point'])
        if not err:

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

        return url, err

    def _clean_hells(self):
        return self._common_clean('hells', 'point')

    def _common_clean(self, att, filter=None):
        """
        Spolecna funkce pro clean_XXX metody. Zadany KML soubor rozparsuje a
        vytahne z nej nosne informace pod atribut `att`_data (napr. polygon_data).
        """
        data = self.cleaned_data.get(att)

        if data:
            # kontrola URL
            data = data.strip()
            if 'output=nl' not in data:
                data = data + '&output=nl'

            # stahneme KML soubor
            content = download_content(data)
            if content is None:
                # chyba behem downloadu
                logger.info('Problem with downloading URL %s' % data)
                return None, self.err_down
            setattr(self, '%s_kml' % att, content)

            # rozparsujeme zadany KML
            try:
                parsed_data = parse_xml(KMLHandler(), content, filter)
            except:
                logger.info('Parsing error during processing content of %s' % data)
                return None, self.err_wrong
            if not parsed_data:
                logger.info('Content of %s does not contain geo data' % data)
                # ha! mozna jsme dostali link na "spatny" KML, overime si to
                parsed_data2 = parse_xml(LinkHandler(), content)
                if len(parsed_data2) != 1:
                    logger.info('Content of %s does not contain link data' % data)
                    # uzivatel zadal asi nejake spatne URL
                    return None, self.err_wrong

                # mame nove URL, zkusime to s nim znovu
                new_url = parsed_data2[0]
                logger.info('Content of %s contain link to %s' % (data, new_url))
                # stahneme KML soubor
                content = download_content(new_url)
                if content is None:
                    # chyba behem downloadu
                    logger.info('Problem with downloading URL %s' % new_url)
                    return None, self.err_down
                setattr(self, '%s_kml' % att, content)

                # rozparsujeme novy KML
                parsed_data = parse_xml(KMLHandler(), content, filter)
                if not parsed_data:
                    # tak ani odkaz ze "spatneho" KML nas nikam nedovedl
                    logger.info('Content of %s does not contain geo data' % new_url)
                    return None, self.err_wrong

                data = new_url

            setattr(self, '%s_data' % att, parsed_data)

        return data, None

    def clean(self):
        cleaned_data = self.cleaned_data

        # vyzobneme udaje z formiku
        slug = cleaned_data.get('slug', None)
        hell_url = cleaned_data.get('hells', None)
        building_url = cleaned_data.get('buildings', None)
        email = cleaned_data.get('email', None)

        if not slug and not email:
            self._errors["email"] = [unicode(forms.CharField.default_error_messages['required'])]
            del cleaned_data["email"]
            email = None

        url_fields_ok = False
        msg_later = u"Mapy pro tuto obec budou za chvíli aktualizovány. Stavte se později."
        if hell_url and building_url:
            # overime (a vyzobneme) informace z odkazovanych URL
            hell_url, err1 = self._clean_hells()
            if err1:
                self._errors["hells"] = [err1]
                del cleaned_data["hells"]
            else:
                cleaned_data['hells'] = hell_url
            building_url, err2 = self._clean_buildings()
            if err2:
                self._errors["buildings"] = [err2]
                del cleaned_data["buildings"]
            else:
                cleaned_data['buildings'] = building_url
            url_fields_ok = not err1 and not err2

        # pokracujem ve validaci dat...
        if url_fields_ok:

            # vyzobneme podrobnejsi informace o zaznamu
            self.ei = self.find_entry_information()

            if not self.ei['pos'] or not self.ei['town']:
                # nepovedlo se zjistit zakladni informace, od kterych se odvozuje
                # vse ostatni -- tj. lat/lon pozici obce a nazev obce
                raise forms.ValidationError(u"Nepodařilo se nám zjistit obec ze které pochází Vaše mapy.")

            if slug:
                try:
                    entry = Entry.objects.get(slug=slug)
                except Entry.DoesNotExist:
                    entry = None
            else:
                try:
                    entry = Entry.objects.get(
                        hell_url = hell_url,
                        building_url = building_url
                    )
                except Entry.DoesNotExist:
                    entry = None
            self.old_entry = entry

            # kontrola obsahu KML map
            if entry and hasattr(self, 'buildings_kml') and hasattr(self, 'hells_kml'):
                if entry.building_kml == self.buildings_kml.decode('utf-8') and \
                   entry.hell_kml == self.hells_kml.decode('utf-8'):
                    if slug:
                        self.update_no_change_slug = slug
                    raise forms.ValidationError(u"Zdrojové mapy pro obec %s se nezměnily, záznam na našich stránkách je aktuální." % self.ei['town'])

        return cleaned_data

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
        json = geocode("%(lat)s, %(lon)s" % pos, '')
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
        out = {'wikipedia_url': None, 'public': False}
        out['pos'] = self.find_center()
        out['town'] = self.find_town(out['pos'])
        if out['town']:
            out['wikipedia_url'] = self.guess_wikipedia_url(out['town'])
            wikipedia_content = download_content(out['wikipedia_url'])
            if wikipedia_content:
                out.update(parse_xml(MediaWikiHandler(), wikipedia_content))
                if out['population'] and out['area']:
                    out['public'] = True
        return out

    def create_entry(self, ip=''):
        """
        Vytvori castecny zaznam o obci -- zatim neuplny, neverejny. Je to jen
        to nejnutnejsi pro Django, aby k zaznamu mohlo priradit ostatni FK/M2M
        vazby o hernach a budovach. Ke zpresneni zaznamu dojde pozdeji v
        refine_entry.
        """
        data = {
            'title':        self.ei['town'],
            'slug':         ''.join(random.sample(list('abcdefghjkmopqrstuvwxyz'), 10)),
            'hell_url':     self.cleaned_data['hells'],
            'hell_kml':     self.hells_kml,
            'building_url': self.cleaned_data['buildings'],
            'building_kml': self.buildings_kml,
            'public':       False,
            'ip':           ip
        }
        return Entry.objects.create(**data)

    def refine_entry(self, entry):
        """
        Vypilovani zaznamu o obci. Nyni aktualizujeme vsechny jeji udaje do
        finalni podoby.
        """

        ei = self.ei
        old_entry = self.old_entry

        if old_entry:
            exists = True
            # novy zaznam podedi nektere vlastnosti stareho zaznamu
            slug = old_entry.slug # stejny slug
            public = old_entry.public # viditelnost

            # stary zaznam obce odstavime na vedlejsi kolej
            old_entry.slug = "%s-%i" % (old_entry.slug, old_entry.id)
            old_entry.public = False
            old_entry.save()
        else:
            # pro novy zaznam vymyslime unikatni slug
            slug, exists = get_unique_slug(ei['town'][:90]) # TODO: neopakuje se mi to? ta :90
            if exists:
                point = Point(ei['pos']['lon'], ei['pos']['lat'], srid=4326)
                if Entry.objects.filter(slug__startswith=slugify(ei['town'][:90]), dpoint__distance_lte=(point, D(km=KM20))).exists():
                    # duplicitni zaznam s jinym zdrojem dat; tohle skryjem
                    public = False
                else:
                    # jde pouze o shodu jmena obce; normalne ji zverejnime
                    # (slug sice bude mit cislo, ale jinak to stejne nejde)
                    public = True
            else:
                public = True

        # data pro aktualizovani zaznamu Entry
        data = {
            'slug':         slug,
            'population':   ei['population'] and int(ei['population']) or None,
            'area':         ei['area'] and int(ei['area']) or None,
            'wikipedia':    ei['wikipedia_url'],
            'public':       public,
            'email':        self.cleaned_data['email'],
            'description':  ei['description']
        }
        if old_entry:
            # pokud nam v "ei" datech neco chybi, doplnime to ze stareho zaznamu
            data['population'] = data['population'] or old_entry.population
            data['area'] = data['area'] or old_entry.area
            data['wikipedia'] = data['wikipedia'] or old_entry.wikipedia
            data['description'] = data['description'] or old_entry.description

        # ulozeni objektu do DB
        for k, v in data.iteritems():
            setattr(entry, k, v)
        entry.recalculate_denormalized_values(True)
        entry.save()
        cache.clear()
        return entry, exists

    def save(self, ip):
        """
        Ulozi vyparsovane body s hernami, obrysy budov a jejich okoli pod zaznam
        `entry`.
        """
        # nejdriv ulozime "pahylek"
        entry = self.create_entry(ip)

        # pridruzime k obci budovy, herny a zony
        self.save_buildings(entry)
        self.save_hells(entry)

        # dobrousime zaznam obce
        entry, exists = self.refine_entry(entry)
        return entry, exists

    def save_buildings(self, entry):
        """
        Ulozi vyparsovane obrysy budov. Ke kazde budove vypocita jeji obrys.
        """
        ct1 = CoordTransform(SpatialReference('WGS84'), SpatialReference(102065))
        ct2 = CoordTransform(SpatialReference(102065), SpatialReference('WGS84'))

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
            b.calculate_zone(M100, ct1, ct2)

    def save_hells(self, entry):
        """
        Ulozi vyparsovane body s hernami. Pro kazdou z heren zjisti seznam zon,
        se kterymi je v konfliktu.
        """
        times = []
        buildings = list(entry.building_set.all())
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
            b.calculate_conflicts(buildings)
            b.calculate_uzone()


class EmailForm(forms.Form):
    """
    Administracni formular pro odeslani vzkazu autorovi map.
    """
    DEFAULT_EMAIL_MESSAGE = u"""Dobrý den,
děkujeme za Váš příspěvek do mapovaní hazardu v ČR.

Musíme Vás ale upozornit, že obec %(title)s je v naší aplikaci už evidována. Pokud chcete informace o hernách či budovách aktualizovat, prostudujte si podrobně tento návod: http://www.mapyhazardu.cz/spoluprace/

Děkujeme

--

Tým MapyHazardu.cz"""

    subject = forms.CharField(label=u"Předmět", max_length=80, widget=forms.TextInput(attrs={'style': 'width:320px'}))
    content = forms.CharField(label=u"Vzkaz", widget=forms.Textarea(attrs={'cols':'70', 'rows':'20'}))

    def send_email(self, to):
        send_mail(
            self.cleaned_data['subject'],
            self.cleaned_data['content'],
            'info@mapyhazardu.cz',
            [to],
            fail_silently=False
        )
