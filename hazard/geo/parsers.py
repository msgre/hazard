# -*- coding: utf-8 -*-

"""
Jednoduchy parser KML dat z Googlich map.
"""

import re
import xml.sax
from StringIO import StringIO


class KMLHandler(xml.sax.handler.ContentHandler):
    """
    Parser geometrickych objektu (polygonu, bodu a car) z KML souboru. Priklad
    popisu XML:

    <Placemark>
        <name>herna</name>
        <description><![CDATA[]]></description>
        <styleUrl>#style1</styleUrl>
        <Polygon>
            <outerBoundaryIs>
                <LinearRing>
                    <tessellate>1</tessellate>
                    <coordinates>
                        17.973688,49.476315,0.000000
                        17.973921,49.476395,0.000000
                        17.974007,49.476292,0.000000
                        17.973772,49.476215,0.000000
                        17.973688,49.476315,0.000000
                    </coordinates>
                </LinearRing>
            </outerBoundaryIs>
        </Polygon>
    </Placemark>
    <Placemark>
        <name>Friedrichstraße 50</name>
        <description><![CDATA[10117 Berlin<br>]]></description>
        <styleUrl>#style11</styleUrl>
        <Point>
            <coordinates>13.390790,52.508930,0.000000</coordinates>
        </Point>
    </Placemark>
    """

    def __init__(self):
        self.starts = {}
        self.objects = []
        self.types = ['polygon', 'point', 'linestring']
        self.initPlacemark()

    def initPlacemark(self):
        self.placemark = {
            'name': [],
            'description': [],
            'coordinates': [],
            'type': ['unknown']
        }

    def startElement(self, name, attributes):
        name = name.lower()
        if name == 'placemark':
            self.starts[name] = 1
            self.initPlacemark()
        elif name in self.types:
            self.placemark['type'] = [name]
            self.starts[name] = 1
        elif name == 'name':
            self.starts[name] = 1
        elif name == 'description':
            self.starts[name] = 1
        elif name == 'coordinates':
            self.starts[name] = 1

    def endElement(self, name):
        name = name.lower()
        if name == 'placemark':
            self.starts.pop(name)
            self.objects.append(self.placemark)
        elif name in self.types:
            self.starts.pop(name)
        elif name == 'name':
            self.starts.pop(name)
        elif name == 'coordinates':
            self.starts.pop(name)

    def characters(self, data):
        if 'placemark' in self.starts:
            if 'name' in self.starts:
                self.placemark['name'].append(data)
            elif 'coordinates' in self.starts:
                self.placemark['coordinates'].append(data)
            elif 'description' in self.starts:
                self.placemark['description'].append(data)

    def normalizedOutput(self, filter=None):
        """
        Normalizuje naparsovany vystup, napr:

        TODO: priklady
        """
        out = []

        for obj in self.objects:
            # zakladni ocisteni
            item = {}
            for k, v in obj.iteritems():
                item[k] = [i.strip() for i in v if i.strip()]

            # vycistime konkretni prvky
            if 'name' in item and item['name']:
                item['name'] = item['name'][0].strip()
            if 'description' in item and item['description']:
                item['description'] = item['description'][0].strip()
            if 'type' in item and item['type']:
                item['type'] = item['type'][0].strip()
            if 'coordinates' in item and item['coordinates']:
                item['coordinates'] = [[float(y.strip()) for y in i.split(',')[:2]] \
                                       for i in item['coordinates']]
                item['coordinates'] = [dict(zip(['lon', 'lat'], i)) for i in item['coordinates']]

            if filter and item['type'] in filter:
                out.append(item)

        return out


class LinkHandler(xml.sax.handler.ContentHandler):
    """
    Parser "spatneho" KML, tj. takoveho, ktery obsahuje pouze odkaz na jiny
    KML, ve kterem uz je doopravdy popis geometrickych struktur.
    Priklad XML:

    <NetworkLink>
        <name>herna</name>
        <Link>
            <href>http://maps.google.com/maps/ms?ie=UTF8&amp;hl=cs&amp;vps=2&amp;jsv=321b&amp;oe=UTF8&amp;msa=0&amp;msid=217120881929273348625.00049e319b5e493cf79ef&amp;output=kml</href>
        </Link>
    </NetworkLink>
    """
    def __init__(self):
        self.starts = {}
        self.urls = []
        self.urls_idx = -1

    def startElement(self, name, attributes):
        name = name.lower()
        if name == 'networklink':
            self.starts[name] = 1
        elif name == 'link':
            self.starts[name] = 1
        elif name == 'href':
            self.starts[name] = 1

    def endElement(self, name):
        name = name.lower()
        if name == 'networklink':
            self.starts.pop(name)
        elif name == 'link':
            self.starts.pop(name)
        elif name == 'href':
            self.starts.pop(name)
            self.urls_idx += 1

    def characters(self, data):
        if 'networklink' in self.starts and 'link' in self.starts and \
           'href' in self.starts:
            if self.urls_idx < 0:
                self.urls.append([data])
                self.urls_idx = 0
            else:
                self.urls[self.urls_idx].append(data)

    def normalizedOutput(self, filter=None):
        """
        Normalizuje naparsovany vystup, napr:

        [u'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=321b&oe=UTF8\
           &msa=0&msid=217120881929273348625.00049e319b5e493cf79ef&output=kml']
        """
        out = []
        for url in self.urls:
            out.append(''.join([i.strip() for i in url if i.strip()]))
        return out


GEOBOX_RE = re.compile(r'\{\{Geobox([^}]+)\}\}')
POPULATION_RE = re.compile(r'\s*population\s*=\s*(\d+)')
AREA_RE = re.compile(r'\s*area\s*=\s*(\d+)')

class MediaWikiHandler(xml.sax.handler.ContentHandler):
    """
    Parser XML vystupu z Wikipedie.
    """
    def __init__(self):
        self.starts = {}
        self.content = []

    def startElement(self, name, attributes):
        name = name.lower()
        if name == 'text':
            self.starts[name] = 1

    def endElement(self, name):
        name = name.lower()
        if name == 'text':
            self.starts.pop(name)

    def characters(self, data):
        if 'text' in self.starts:
            self.content.append(data)

    def normalizedOutput(self, filter=None):
        """
        Vrati slovnik s nalezenou informaci o poctu obyvatel a plose
        katastralniho uzemi.
        """
        text = [i.strip() for i in self.content if i.strip()]
        text = ''.join(text)
        out = {'population': None, 'area': None}

        m = GEOBOX_RE.search(text)
        if m:
            # vyzobnuti poctu obyvatel
            n = POPULATION_RE.search(m.group(1))
            if n:
                out['population'] = n.group(1)

            # vyzobnuti katastralni vymery
            n = AREA_RE.search(m.group(1))
            if n:
                out['area'] = n.group(1)

        return out


def parse_xml(handler, content, filter=None):
    """
    Pomocna fce. Zadany obsah `content` v podobe retezce rozparsuje za pomoci
    `handler`u a vrati zpracovany vysledek (slovnik se zajimavymi daty).
    """
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO(content))
    parser.parse(inpsrc)
    return parser.getContentHandler().normalizedOutput(filter)


if __name__ == "__main__":

    link_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://earth.google.com/kml/2.2">
    <Document>
      <name>EuroDjangoCon</name>
      <description><![CDATA[]]></description>
      <NetworkLink>
        <name>EuroDjangoCon</name>
        <Link>
          <href>http://maps.google.com/maps/ms?ie=UTF8&amp;hl=cs&amp;vps=3&amp;jsv=332a&amp;oe=UTF8&amp;msa=0&amp;msid=209504919052977982241.00046815a0bc660d9cba2&amp;output=kml</href>
        </Link>
      </NetworkLink>
    </Document>
    </kml>"""

    mixed_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://earth.google.com/kml/2.2">
    <Document>
      <name>EuroDjangoCon</name>
      <description><![CDATA[]]></description>
      <Style id="style14">
        <IconStyle>
          <Icon>
            <href>http://maps.google.com/mapfiles/ms/micons/red-dot.png</href>
          </Icon>
        </IconStyle>
      </Style>
      <Style id="style1">
        <IconStyle>
          <Icon>
            <href>http://maps.google.com/mapfiles/ms/micons/red-dot.png</href>
          </Icon>
        </IconStyle>
      </Style>
      <Style id="style5">
        <LineStyle>
          <color>73FF0000</color>
          <width>5</width>
        </LineStyle>
      </Style>
      <Style id="style11">
        <IconStyle>
          <Icon>
            <href></href>
          </Icon>
        </IconStyle>
      </Style>
      <Placemark>
        <name>Iris Congress Hotel</name>
        <description><![CDATA[<div dir="ltr">The conference hotel.</div>]]></description>
        <styleUrl>#style14</styleUrl>
        <Point>
          <coordinates>14.471569,50.068283,0.000000</coordinates>
        </Point>
      </Placemark>
      <Placemark>
        <name>Trasa do cíle: 5321 palm valley road roanoke</name>
        <description><![CDATA[]]></description>
        <styleUrl>#style5</styleUrl>
        <ExtendedData>
          <Data name="_SnapToRoads">
            <value>true</value>
          </Data>
        </ExtendedData>
        <LineString>
          <tessellate>1</tessellate>
          <coordinates>
            -79.913857,37.407928,0.000000
            -79.913918,37.406860,0.000000
            -79.913834,37.405289,0.000000
            -79.913750,37.404839,0.000000
            -79.913620,37.404518,0.000000
            -79.911659,37.400871,0.000000
            -79.909790,37.398060,0.000000
            -79.909447,37.397678,0.000000
            -79.907181,37.395458,0.000000
            -79.906822,37.394989,0.000000
            -79.906563,37.394341,0.000000
            -79.905762,37.389980,0.000000
            -79.905663,37.389610,0.000000
          </coordinates>
        </LineString>
      </Placemark>
      <Placemark>
        <name>cara4</name>
        <description><![CDATA[]]></description>
        <styleUrl>#style1</styleUrl>
        <LineString>
          <tessellate>1</tessellate>
          <coordinates>
            17.973129162059738,49.475453782625515,0.000000
            17.97384753847081, 49.476304449159365,0.000000
          </coordinates>
        </LineString>
      </Placemark>
    </Document>
    </kml>"""

    wikipedia_xml = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.5/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.5/ http://www.mediawiki.org/xml/export-0.5.xsd" version="0.5" xml:lang="en">
  <siteinfo>
    <sitename>Wikipedia</sitename>
    <base>http://en.wikipedia.org/wiki/Main_Page</base>
    <generator>MediaWiki 1.17wmf1</generator>
    <case>first-letter</case>
    <namespaces>
      <namespace key="-2" case="first-letter">Media</namespace>
      <namespace key="-1" case="first-letter">Special</namespace>
      <namespace key="0" case="first-letter" />
      <namespace key="1" case="first-letter">Talk</namespace>
      <namespace key="2" case="first-letter">User</namespace>
      <namespace key="3" case="first-letter">User talk</namespace>
      <namespace key="4" case="first-letter">Wikipedia</namespace>
      <namespace key="5" case="first-letter">Wikipedia talk</namespace>
      <namespace key="6" case="first-letter">File</namespace>
      <namespace key="7" case="first-letter">File talk</namespace>
      <namespace key="8" case="first-letter">MediaWiki</namespace>
      <namespace key="9" case="first-letter">MediaWiki talk</namespace>
      <namespace key="10" case="first-letter">Template</namespace>
      <namespace key="11" case="first-letter">Template talk</namespace>
      <namespace key="12" case="first-letter">Help</namespace>
      <namespace key="13" case="first-letter">Help talk</namespace>
      <namespace key="14" case="first-letter">Category</namespace>
      <namespace key="15" case="first-letter">Category talk</namespace>
      <namespace key="100" case="first-letter">Portal</namespace>
      <namespace key="101" case="first-letter">Portal talk</namespace>
      <namespace key="108" case="first-letter">Book</namespace>
      <namespace key="109" case="first-letter">Book talk</namespace>
    </namespaces>
  </siteinfo>
  <page>
    <title>Valašské Meziříčí</title>
    <id>4445175</id>
    <revision>
      <id>422873263</id>
      <timestamp>2011-04-07T15:38:39Z</timestamp>
      <contributor>
        <username>Luckas-bot</username>
        <id>7320905</id>
      </contributor>
      <minor/>
      <comment>r2.7.1) (robot Adding: [[ru:Валашске-Мезиржичи]]</comment>
      <text xml:space="preserve" bytes="4033">{{Geobox | Settlement
&lt;!-- *** Heading *** --&gt;
| name               = Valašské Meziříčí
| other_name         =
| category           = Town
&lt;!-- *** Image *** --&gt;
| image              = Náměstí ve Valašském Meziříčí 2.jpg
| image_caption      = Town square
&lt;!-- *** Symbols *** --&gt;
| flag               = Valasske_Mezirici_prapor.png | flag_border = 1
| symbol             = Valasske_Mezirici_znak.png
&lt;!-- *** Name *** --&gt;
| etymology          =
| official_name      =
| motto              =
| nickname           =
&lt;!-- *** Country etc. *** --&gt;
| country            = Czech Republic
| country_flag       = 1
| state              =
| region             = [[Zlín Region|Zlín]]
| region_type        = [[Regions of the Czech Republic|Region]]
| district           = [[Vsetín District|Vsetín]]
| district_type      = [[Districts of the Czech Republic|District]]
| commune            = Valašské Meziříčí
| municipality       =
&lt;!-- *** Family *** --&gt;
| part               =
| river              = Bečva
&lt;!-- *** Locations *** --&gt;
| location           =
| elevation          = 294
| lat_d              = 49
| lat_m              = 28
| lat_s              = 36
| lat_NS             = N
| long_d             = 17
| long_m             = 58
| long_s             = 26
| long_EW            = E
| highest            =
| highest_elevation  =
| highest_lat_d      =
| highest_long_d     =
| lowest             =
| lowest_elevation   =
| lowest_lat_d       =
| lowest_long_d      =
&lt;!-- *** Dimensions *** --&gt;
| area               = 55
| area_round         = 0
&lt;!-- *** Population *** --&gt;
| population         = 27960
| population_date    =
| population_density = auto
&lt;!-- *** History &amp; management *** --&gt;
| established        = 1377
| established_type   = First mentioned
| mayor              = Jiří Částečka
&lt;!-- *** Codes *** --&gt;
| timezone           = [[Central European Time|CET]]
| utc_offset         = +1
| timezone_DST       = CEST
| utc_offset_DST     = +2
| postal_code        = 757 01
| area_code          =
| code               =
&lt;!-- *** Free frields *** --&gt;
| free               =
&lt;!-- *** Maps *** --&gt;
| map                = Czechia - outline map.svg
| map_background     = Czechia - background map.png
| map_caption        = Location in the Czech Republic
| map_locator        = Czechia
&lt;!-- *** Websites *** --&gt;
| commons            = Valašské Meziříčí
| statistics         = [http://www.statnisprava.cz/ebe/ciselniky.nsf/i/545058 statnisprava.cz]
| website            = [http://www.valasskemezirici.cz/ www.valasskemezirici.cz]
&lt;!-- *** Footnotes *** --&gt;
| footnotes          =
}}

'''Valašské Meziříčí''' ({{IPA-cs|ˈvalaʃskɛː ˈmɛzɪr̝iːtʃiː}}; {{lang-de|Wallachisch Meseritsch}}) is a town in the [[Zlín Region]], the [[Czech Republic]]. The town has 27,960 inhabitants.

[[Vsetínská Bečva]] and [[Rožnovská Bečva]] rivers join in the town to form the [[Bečva River]].

==Notable residents==
Famous tennis player [[Tomáš Berdych]], [[Academy Award]] winning songwriter and actress [[Markéta Irglová]] and footballer [[Milan Baroš]] were born here.

==Main sights==
* The [[House of Kinsky|Kinský]] Chateau
* The [[Moravská Gobelínová Manufaktura]]
* The [[House of Žerotín|Žerotín]] Chateau

==External links==
* [http://www.valasskemezirici.cz/ Official website] {{cs icon}}

{{Vsetín District}}

{{DEFAULTSORT:Valasske Mezirici}}
[[Category:Cities and towns in the Czech Republic]]
[[Category:Vsetín District]]

{{Zlín-geo-stub}}

[[ar:فالاشسكي ميزيريتشي]]
[[cs:Valašské Meziříčí]]
[[de:Valašské Meziříčí]]
[[eo:Valašské Meziříčí]]
[[fr:Valašské Meziříčí]]
[[hr:Valašské Meziříčí]]
[[it:Valašské Meziříčí]]
[[hu:Valašské Meziříčí]]
[[nl:Valašské Meziříčí]]
[[oc:Valašské Meziříčí]]
[[pl:Valašské Meziříčí]]
[[pt:Valašské Meziříčí]]
[[ru:Валашске-Мезиржичи]]
[[sk:Valašské Meziříčí]]
[[sr:Валашке Мезиричи]]</text>
    </revision>
  </page>
</mediawiki>"""

    assert len(parse_xml(KMLHandler(), mixed_xml)) == 3
    assert len(parse_xml(LinkHandler(), link_xml)) == 1
    assert len(parse_xml(MediaWikiHandler(), wikipedia_xml)) == 2
