# -*- coding: utf-8 -*-

from django.test import TestCase

from hazard.geo.parsers import parse_xml, KMLHandler, LinkHandler, MediaWikiHandler


class ParsersTestCase(TestCase):
    """
    Test parseru KML popisu map a XML popisu stranek o obcich ve Wikipedii.
    """

    def test_kmlhandler_wrong_filter(self):
        """
        Pokud do argumentu filter nic nezadame, anebo tam fouknem nesmysl,
        fce parse_xml nam vrati prazdny seznam.
        """
        out = parse_xml(KMLHandler(), self.PLACEMARK_KML)
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 0)
        out = parse_xml(KMLHandler(), self.PLACEMARK_KML, ['nonsence'])
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 0)

    def test_kmlhandler_placemark(self):
        """
        Rozparsovani KML s popisem heren (spendliky v mape).
        """
        out = parse_xml(KMLHandler(), self.PLACEMARK_KML, ['point'])
        # vrati se nam seznam zaznamu
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 33)
        # kazdy spendlik je popsan slovnikem
        self.assertEqual(type(out[0]), type({}))
        self.assertTrue('type' in out[0])
        self.assertTrue('name' in out[0])
        self.assertTrue('coordinates' in out[0])
        self.assertTrue('description' in out[0])
        self.assertEqual(out[0]['type'], 'point')
        self.assertEqual(out[0]['name'], u'Hranick\xe1 290')
        self.assertEqual(out[0]['coordinates'], [{'lat': 49.481411, 'lon': 17.962866}])
        self.assertEqual(out[0]['description'], '#style21')

    def test_kmlhandler_linestring(self):
        """
        Rozparsovani KML s popisem budov nakreslenych jako lomene cary.
        """
        out = parse_xml(KMLHandler(), self.LINESTRING_KML, ['polygon']) # jako filters zadavam polygon, protoze interne se ve tride KMLHandler prevadi linestring struktury na polygon
        # vrati se nam seznam zaznamu
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 11)
        # kazdy polygon je popsan slovnikem
        self.assertEqual(type(out[0]), type({}))
        self.assertTrue('type' in out[0])
        self.assertTrue('name' in out[0])
        self.assertTrue('coordinates' in out[0])
        self.assertTrue('description' in out[0])
        self.assertEqual(out[0]['type'], 'polygon')
        self.assertEqual(out[0]['name'], u'M\u011bstsk\xfd \xfa\u0159ad')
        self.assertEqual(out[0]['coordinates'], [{'lat': 49.712761, 'lon': 17.902891}, {'lat': 49.712696, 'lon': 17.90292}, {'lat': 49.71273, 'lon': 17.903151}, {'lat': 49.713009, 'lon': 17.903101}, {'lat': 49.712978, 'lon': 17.902836}, {'lat': 49.712769, 'lon': 17.902884}])
        self.assertEqual(out[0]['description'], '#style4')

    def test_kmlhandler_polygon(self):
        """
        Rozparsovani KML s popisem budov nakreslenych jako polygony.
        """
        out = parse_xml(KMLHandler(), self.POLYGON_KML, ['polygon'])
        # vrati se nam seznam zaznamu
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 82)
        # kazdy polygon je popsan slovnikem
        self.assertEqual(type(out[0]), type({}))
        self.assertTrue('type' in out[0])
        self.assertTrue('name' in out[0])
        self.assertTrue('coordinates' in out[0])
        self.assertTrue('description' in out[0])
        self.assertEqual(out[0]['type'], 'polygon')
        self.assertEqual(out[0]['name'], u'M\u0160 K\u0159i\u017en\xe1')
        self.assertEqual(out[0]['coordinates'], [{'lat': 49.471767, 'lon': 17.963467}, {'lat': 49.47179, 'lon': 17.963671}, {'lat': 49.471657, 'lon': 17.963705}, {'lat': 49.471645, 'lon': 17.963655}, {'lat': 49.471478, 'lon': 17.963697}, {'lat': 49.471458, 'lon': 17.96353}, {'lat': 49.471539, 'lon': 17.963518}, {'lat': 49.471535, 'lon': 17.963465}, {'lat': 49.471592, 'lon': 17.963448}, {'lat': 49.4716, 'lon': 17.963511}, {'lat': 49.471767, 'lon': 17.963467}])
        self.assertEqual(out[0]['description'], '#style42')

    def test_linkhandler(self):
        out = parse_xml(LinkHandler(), self.LINK_KML)
        # LinkHandler vraci seznam...
        self.assertEqual(type(out), type([]))
        self.assertEqual(len(out), 1)
        # ...jehoz hodnotou je vyzobnuta URL adresa
        self.assertEqual(out[0], 'http://maps.google.com/maps/ms?ie=UTF8&hl=cs&vps=2&jsv=332a&oe=UTF8&msa=0&msid=217120881929273348625.00049e61b09dabeb67157&output=kml')

    def test_mediawikihandler(self):
        out = parse_xml(MediaWikiHandler(), self.WIKIPEDIA_XML)
        # MediaWikiHandler vraci slovnik...
        self.assertEqual(type(out), type({}))
        self.assertEqual(len(out), 2)
        # ...se dvema klici
        self.assertTrue('area' in out)
        self.assertTrue('population' in out)
        # ...a temito hodnotami
        self.assertEqual(out['area'], '55')
        self.assertEqual(out['population'], '27960')

    # KML, ktere obsahuje jen odkaz na dalsi KML
    LINK_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>Veřejné budovy</name>
  <description><![CDATA[]]></description>
  <NetworkLink>
    <name>Veřejné budovy</name>
    <Link>
      <href>http://maps.google.com/maps/ms?ie=UTF8&amp;hl=cs&amp;vps=2&amp;jsv=332a&amp;oe=UTF8&amp;msa=0&amp;msid=217120881929273348625.00049e61b09dabeb67157&amp;output=kml</href>
    </Link>
  </NetworkLink>
</Document>
</kml>"""

    # budovy nakreslene carou
    LINESTRING_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>herny-budovy</name>
  <description><![CDATA[]]></description>
  <Style id="style4">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style5">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style10">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style6">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style1">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style11">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style7">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style2">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style8">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style9">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Style id="style3">
    <LineStyle>
      <color>73FF0000</color>
      <width>5</width>
    </LineStyle>
  </Style>
  <Placemark>
    <name>Městský úřad</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style4</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.902891,49.712761,0.000000
        17.902920,49.712696,0.000000
        17.903151,49.712730,0.000000
        17.903101,49.713009,0.000000
        17.902836,49.712978,0.000000
        17.902884,49.712769,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>ZUŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style5</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.904432,49.712112,0.000000
        17.904749,49.712208,0.000000
        17.904823,49.712090,0.000000
        17.904518,49.712006,0.000000
        17.904432,49.712112,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Památník J.A.Komenského</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style10</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.905455,49.712910,0.000000
        17.905146,49.712772,0.000000
        17.905233,49.712692,0.000000
        17.905548,49.712849,0.000000
        17.905455,49.712910,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Kostel Nejsvětější trojice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style6</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.903606,49.711872,0.000000
        17.904173,49.712032,0.000000
        17.904381,49.711998,0.000000
        17.904419,49.711845,0.000000
        17.904366,49.711639,0.000000
        17.903954,49.711506,0.000000
        17.903843,49.711674,0.000000
        17.903732,49.711651,0.000000
        17.903591,49.711872,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Dětský domov</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style1</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.902420,49.715588,0.000000
        17.902843,49.715752,0.000000
        17.903154,49.715408,0.000000
        17.903160,49.715343,0.000000
        17.902697,49.715199,0.000000
        17.902420,49.715588,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Kostel Sv. Josefa</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style11</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.903086,49.715740,0.000000
        17.903229,49.715782,0.000000
        17.903246,49.715862,0.000000
        17.903667,49.715969,0.000000
        17.903879,49.715694,0.000000
        17.903511,49.715553,0.000000
        17.903580,49.715485,0.000000
        17.903383,49.715401,0.000000
        17.903086,49.715740,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Žákladní škola J.A.Komenského</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style7</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.902273,49.715286,0.000000
        17.901646,49.715328,0.000000
        17.901602,49.715191,0.000000
        17.901272,49.715221,0.000000
        17.901291,49.715450,0.000000
        17.900888,49.715473,0.000000
        17.900848,49.715267,0.000000
        17.900696,49.715267,0.000000
        17.900724,49.715416,0.000000
        17.900072,49.715443,0.000000
        17.899023,49.715424,0.000000
        17.899023,49.715092,0.000000
        17.900702,49.715111,0.000000
        17.900709,49.715179,0.000000
        17.900791,49.715176,0.000000
        17.900757,49.714943,0.000000
        17.901064,49.714909,0.000000
        17.901600,49.714890,0.000000
        17.901613,49.715004,0.000000
        17.902206,49.715012,0.000000
        17.902273,49.715286,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Mateřská škola</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style2</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.904802,49.715740,0.000000
        17.904459,49.716686,0.000000
        17.905146,49.716728,0.000000
        17.905128,49.716946,0.000000
        17.906031,49.716969,0.000000
        17.905933,49.716366,0.000000
        17.906143,49.715790,0.000000
        17.904791,49.715763,0.000000
        17.904802,49.715740,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Městské kulturní centrum</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style8</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.906700,49.717060,0.000000
        17.906937,49.717083,0.000000
        17.907007,49.716702,0.000000
        17.906750,49.716675,0.000000
        17.906700,49.717060,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Základní škola T.G.Masaryka</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style9</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.908289,49.715286,0.000000
        17.908804,49.715225,0.000000
        17.908937,49.715244,0.000000
        17.909538,49.715160,0.000000
        17.909281,49.714542,0.000000
        17.908970,49.714474,0.000000
        17.908503,49.714493,0.000000
        17.908245,49.715317,0.000000
        17.908289,49.715286,0.000000
      </coordinates>
    </LineString>
  </Placemark>
  <Placemark>
    <name>Finanční úřad</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style3</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
        17.912157,49.713535,0.000000
        17.911959,49.713543,0.000000
        17.911959,49.713203,0.000000
        17.912048,49.713116,0.000000
        17.912167,49.713097,0.000000
        17.912300,49.713097,0.000000
        17.912334,49.713131,0.000000
        17.912119,49.713287,0.000000
        17.912157,49.713535,0.000000
      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>"""

    # budovy nakreslene polygonem
    POLYGON_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>Veřejné budovy</name>
  <description><![CDATA[]]></description>
  <Style id="style42">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style80">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style77">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style8">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style56">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style18">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style6">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style44">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style31">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style17">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style60">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style57">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style61">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style35">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style82">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style53">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style76">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style69">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style26">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style50">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style71">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style21">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style15">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style32">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style40">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style46">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style72">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style5">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style7">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style73">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style54">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style3">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style37">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style10">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style39">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style16">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style22">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style14">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style9">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style33">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style63">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style23">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style48">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style70">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style45">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style52">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style68">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style28">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style24">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style4">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style30">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style49">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style51">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style25">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style2">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style11">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style81">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style64">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style78">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style19">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style65">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style74">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style55">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style38">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style75">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style43">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style58">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style1">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style34">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style13">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style27">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style62">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style47">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style12">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style20">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style66">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style36">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style29">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style67">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style41">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style59">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Style id="style79">
    <LineStyle>
      <color>40000000</color>
      <width>3</width>
    </LineStyle>
    <PolyStyle>
      <color>73FF0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  <Placemark>
    <name>MŠ Křižná</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style42</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.963467,49.471767,0.000000
            17.963671,49.471790,0.000000
            17.963705,49.471657,0.000000
            17.963655,49.471645,0.000000
            17.963697,49.471478,0.000000
            17.963530,49.471458,0.000000
            17.963518,49.471539,0.000000
            17.963465,49.471535,0.000000
            17.963448,49.471592,0.000000
            17.963511,49.471600,0.000000
            17.963467,49.471767,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Křižná</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style80</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.964230,49.472260,0.000000
            17.964270,49.472198,0.000000
            17.964211,49.472179,0.000000
            17.964319,49.471989,0.000000
            17.964390,49.472012,0.000000
            17.964581,49.471729,0.000000
            17.964781,49.471802,0.000000
            17.964640,49.472038,0.000000
            17.964899,49.472111,0.000000
            17.965090,49.471802,0.000000
            17.964581,49.471661,0.000000
            17.964630,49.471539,0.000000
            17.964899,49.471611,0.000000
            17.964870,49.471642,0.000000
            17.965506,49.471806,0.000000
            17.965454,49.471889,0.000000
            17.965210,49.471828,0.000000
            17.965160,49.471909,0.000000
            17.965490,49.472012,0.000000
            17.965300,49.472301,0.000000
            17.965170,49.472271,0.000000
            17.965050,49.472462,0.000000
            17.965481,49.472569,0.000000
            17.965540,49.472488,0.000000
            17.966000,49.472610,0.000000
            17.966000,49.472519,0.000000
            17.965540,49.472408,0.000000
            17.965599,49.472301,0.000000
            17.966009,49.472408,0.000000
            17.966009,49.472290,0.000000
            17.965570,49.472160,0.000000
            17.965630,49.472061,0.000000
            17.966009,49.472149,0.000000
            17.966009,49.472061,0.000000
            17.965580,49.471931,0.000000
            17.965639,49.471821,0.000000
            17.967030,49.472210,0.000000
            17.966970,49.472301,0.000000
            17.966150,49.472099,0.000000
            17.966141,49.472721,0.000000
            17.966330,49.472771,0.000000
            17.966370,49.472721,0.000000
            17.966801,49.472820,0.000000
            17.966869,49.472710,0.000000
            17.967440,49.472870,0.000000
            17.967310,49.473061,0.000000
            17.966890,49.472961,0.000000
            17.966850,49.473000,0.000000
            17.965031,49.472530,0.000000
            17.965000,49.472569,0.000000
            17.964670,49.472488,0.000000
            17.964741,49.472401,0.000000
            17.964230,49.472260,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>MŠ Seifertova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style77</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.966976,49.474957,0.000000
            17.966970,49.474903,0.000000
            17.966831,49.474861,0.000000
            17.966909,49.474762,0.000000
            17.967119,49.474831,0.000000
            17.967253,49.474670,0.000000
            17.967083,49.474617,0.000000
            17.967150,49.474522,0.000000
            17.967682,49.474705,0.000000
            17.967619,49.474789,0.000000
            17.967461,49.474743,0.000000
            17.967340,49.474903,0.000000
            17.967617,49.475006,0.000000
            17.967539,49.475101,0.000000
            17.967346,49.475037,0.000000
            17.967300,49.475075,0.000000
            17.966976,49.474957,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>VOŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style8</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972477,49.476505,0.000000
            17.972651,49.476231,0.000000
            17.971844,49.476006,0.000000
            17.971869,49.475960,0.000000
            17.971540,49.475868,0.000000
            17.971428,49.476040,0.000000
            17.972176,49.476250,0.000000
            17.972221,49.476192,0.000000
            17.972372,49.476238,0.000000
            17.972338,49.476295,0.000000
            17.972277,49.476276,0.000000
            17.972179,49.476421,0.000000
            17.972477,49.476505,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Masarykova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style56</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971176,49.476364,0.000000
            17.971390,49.476082,0.000000
            17.971581,49.476139,0.000000
            17.971443,49.476326,0.000000
            17.971577,49.476364,0.000000
            17.971500,49.476463,0.000000
            17.971176,49.476364,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Masarykova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style18</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970682,49.476547,0.000000
            17.970755,49.476471,0.000000
            17.971136,49.476570,0.000000
            17.971228,49.476440,0.000000
            17.971315,49.476467,0.000000
            17.971281,49.476509,0.000000
            17.971525,49.476582,0.000000
            17.971561,49.476540,0.000000
            17.971685,49.476555,0.000000
            17.971750,49.476578,0.000000
            17.971626,49.476753,0.000000
            17.971676,49.476784,0.000000
            17.971561,49.476936,0.000000
            17.971678,49.476982,0.000000
            17.971540,49.477184,0.000000
            17.971409,49.477154,0.000000
            17.971373,49.477200,0.000000
            17.971209,49.477158,0.000000
            17.971275,49.477058,0.000000
            17.970482,49.476822,0.000000
            17.970539,49.476734,0.000000
            17.970919,49.476833,0.000000
            17.971031,49.476662,0.000000
            17.970682,49.476547,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>VOŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style6</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972383,49.477146,0.000000
            17.972391,49.477055,0.000000
            17.972782,49.477070,0.000000
            17.972893,49.476883,0.000000
            17.972734,49.476837,0.000000
            17.972799,49.476742,0.000000
            17.973269,49.476887,0.000000
            17.973206,49.476967,0.000000
            17.973072,49.476929,0.000000
            17.972960,49.477097,0.000000
            17.973137,49.477154,0.000000
            17.973076,49.477245,0.000000
            17.972828,49.477173,0.000000
            17.972383,49.477146,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ISŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style44</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975222,49.477139,0.000000
            17.975237,49.476856,0.000000
            17.975447,49.476864,0.000000
            17.975443,49.476997,0.000000
            17.975805,49.477013,0.000000
            17.975798,49.477158,0.000000
            17.975222,49.477139,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ISŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style31</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975492,49.476921,0.000000
            17.975506,49.476776,0.000000
            17.975948,49.476810,0.000000
            17.975925,49.476952,0.000000
            17.975492,49.476921,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Žerotínova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style17</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975866,49.472122,0.000000
            17.976040,49.472122,0.000000
            17.976044,49.471893,0.000000
            17.975990,49.471889,0.000000
            17.976023,49.471378,0.000000
            17.975857,49.471378,0.000000
            17.975836,49.471573,0.000000
            17.975470,49.471554,0.000000
            17.975477,49.471256,0.000000
            17.975212,49.471256,0.000000
            17.975233,49.472027,0.000000
            17.975855,49.472027,0.000000
            17.975866,49.472122,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Šafaříkova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style60</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.976892,49.467686,0.000000
            17.976910,49.467579,0.000000
            17.976704,49.467564,0.000000
            17.976707,49.467510,0.000000
            17.975882,49.467461,0.000000
            17.975870,49.467525,0.000000
            17.975653,49.467518,0.000000
            17.975632,49.467632,0.000000
            17.975748,49.467644,0.000000
            17.975714,49.467926,0.000000
            17.975977,49.467945,0.000000
            17.975964,49.468018,0.000000
            17.975540,49.467991,0.000000
            17.975594,49.467667,0.000000
            17.975525,49.467663,0.000000
            17.975536,49.467602,0.000000
            17.975340,49.467590,0.000000
            17.975281,49.467991,0.000000
            17.975159,49.467983,0.000000
            17.975107,49.468235,0.000000
            17.975348,49.468254,0.000000
            17.975357,49.468147,0.000000
            17.976395,49.468212,0.000000
            17.976377,49.468380,0.000000
            17.976517,49.468391,0.000000
            17.976589,49.467876,0.000000
            17.976448,49.467865,0.000000
            17.976406,49.468121,0.000000
            17.976082,49.468098,0.000000
            17.976114,49.467911,0.000000
            17.976154,49.467911,0.000000
            17.976170,49.467834,0.000000
            17.976135,49.467831,0.000000
            17.976168,49.467648,0.000000
            17.975985,49.467632,0.000000
            17.975990,49.467590,0.000000
            17.976629,49.467628,0.000000
            17.976624,49.467670,0.000000
            17.976892,49.467686,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Salvátor</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style57</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970034,49.468422,0.000000
            17.970186,49.468430,0.000000
            17.970205,49.468025,0.000000
            17.969936,49.468010,0.000000
            17.969913,49.468334,0.000000
            17.970039,49.468338,0.000000
            17.970034,49.468422,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZŠ Vyhlídka</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style61</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970173,49.468731,0.000000
            17.969513,49.468719,0.000000
            17.969273,49.469177,0.000000
            17.969095,49.469135,0.000000
            17.969349,49.468643,0.000000
            17.969339,49.468002,0.000000
            17.969500,49.467999,0.000000
            17.969519,49.468552,0.000000
            17.970179,49.468555,0.000000
            17.970173,49.468731,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>MŠ Tylova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style35</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971294,49.465904,0.000000
            17.971317,49.465782,0.000000
            17.971573,49.465797,0.000000
            17.971632,49.465405,0.000000
            17.971737,49.465405,0.000000
            17.971626,49.465221,0.000000
            17.971458,49.465202,0.000000
            17.971468,49.465099,0.000000
            17.971962,49.465130,0.000000
            17.971939,49.465244,0.000000
            17.971710,49.465237,0.000000
            17.971792,49.465405,0.000000
            17.971863,49.465416,0.000000
            17.971828,49.465652,0.000000
            17.971647,49.465641,0.000000
            17.971628,49.465813,0.000000
            17.971802,49.465824,0.000000
            17.971792,49.465946,0.000000
            17.971294,49.465904,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>MŠ Kraiczova</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style82</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.969597,49.467239,0.000000
            17.969604,49.467178,0.000000
            17.969414,49.467171,0.000000
            17.969435,49.467037,0.000000
            17.969915,49.467064,0.000000
            17.969896,49.467197,0.000000
            17.969744,49.467194,0.000000
            17.969736,49.467251,0.000000
            17.969597,49.467239,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>MŠ Štěpánov</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style53</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.980600,49.465717,0.000000
            17.980175,49.465523,0.000000
            17.980309,49.465405,0.000000
            17.980461,49.465473,0.000000
            17.980730,49.465225,0.000000
            17.981146,49.465424,0.000000
            17.981033,49.465527,0.000000
            17.980717,49.465385,0.000000
            17.980762,49.465340,0.000000
            17.980734,49.465328,0.000000
            17.980545,49.465500,0.000000
            17.980742,49.465591,0.000000
            17.980600,49.465717,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SOU Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style76</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970009,49.471565,0.000000
            17.970106,49.471378,0.000000
            17.970596,49.471474,0.000000
            17.970591,49.471542,0.000000
            17.970627,49.471550,0.000000
            17.970577,49.471684,0.000000
            17.970009,49.471565,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Gymnázium</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style69</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.968483,49.470219,0.000000
            17.968609,49.469963,0.000000
            17.969316,49.470108,0.000000
            17.969191,49.470371,0.000000
            17.968483,49.470219,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SPŠ Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style26</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975288,49.469227,0.000000
            17.975330,49.468964,0.000000
            17.975481,49.468975,0.000000
            17.975456,49.469112,0.000000
            17.975672,49.469131,0.000000
            17.975643,49.469257,0.000000
            17.975288,49.469227,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SPŠ Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style50</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975691,49.469284,0.000000
            17.975698,49.469151,0.000000
            17.975740,49.469147,0.000000
            17.975758,49.468967,0.000000
            17.975344,49.468929,0.000000
            17.975370,49.468670,0.000000
            17.975574,49.468681,0.000000
            17.975542,49.468819,0.000000
            17.976255,49.468864,0.000000
            17.976240,49.468998,0.000000
            17.975918,49.468971,0.000000
            17.975883,49.469181,0.000000
            17.976418,49.469215,0.000000
            17.976431,49.469143,0.000000
            17.976595,49.469151,0.000000
            17.976583,49.469330,0.000000
            17.975691,49.469284,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SPŠ Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style71</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975428,49.468643,0.000000
            17.975437,49.468555,0.000000
            17.976353,49.468620,0.000000
            17.976332,49.468708,0.000000
            17.975428,49.468643,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SPŠ Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style21</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.976391,49.469078,0.000000
            17.976400,49.468983,0.000000
            17.976358,49.468975,0.000000
            17.976421,49.468479,0.000000
            17.976702,49.468502,0.000000
            17.976648,49.468891,0.000000
            17.976578,49.468887,0.000000
            17.976545,49.469093,0.000000
            17.976391,49.469078,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Škola pro sluchově postižené</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style15</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.974512,49.466587,0.000000
            17.975283,49.466656,0.000000
            17.975342,49.466354,0.000000
            17.975418,49.466358,0.000000
            17.975443,49.466244,0.000000
            17.974506,49.466167,0.000000
            17.974485,49.466278,0.000000
            17.974571,49.466286,0.000000
            17.974512,49.466587,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Škola pro sluchově postižené</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style32</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975283,49.465755,0.000000
            17.975033,49.465729,0.000000
            17.974962,49.465992,0.000000
            17.975212,49.466019,0.000000
            17.975283,49.465755,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Škola pro sluchově postižené</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style40</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975124,49.465633,0.000000
            17.975397,49.465668,0.000000
            17.975332,49.465950,0.000000
            17.975540,49.465973,0.000000
            17.975626,49.465599,0.000000
            17.975140,49.465553,0.000000
            17.975124,49.465633,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ISŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style46</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.968048,49.462559,0.000000
            17.968554,49.462669,0.000000
            17.968245,49.463306,0.000000
            17.967924,49.463238,0.000000
            17.967796,49.463490,0.000000
            17.968100,49.463554,0.000000
            17.968048,49.463665,0.000000
            17.967745,49.463600,0.000000
            17.967592,49.463905,0.000000
            17.967884,49.463966,0.000000
            17.967756,49.464230,0.000000
            17.967649,49.464207,0.000000
            17.967335,49.464840,0.000000
            17.967148,49.464802,0.000000
            17.967453,49.464172,0.000000
            17.967087,49.464100,0.000000
            17.967215,49.463825,0.000000
            17.967390,49.463860,0.000000
            17.967552,49.463539,0.000000
            17.966797,49.463379,0.000000
            17.966858,49.463276,0.000000
            17.967691,49.463451,0.000000
            17.967817,49.463203,0.000000
            17.967735,49.463184,0.000000
            17.968048,49.462559,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>SOU Stavební</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style72</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975414,49.474209,0.000000
            17.975643,49.474213,0.000000
            17.975628,49.473980,0.000000
            17.975859,49.473980,0.000000
            17.975859,49.473839,0.000000
            17.975349,49.473831,0.000000
            17.975414,49.474209,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Střední uměleckoprůmyslová škola sklářská</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style5</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.979139,49.476227,0.000000
            17.979107,49.476082,0.000000
            17.979729,49.476032,0.000000
            17.979755,49.476181,0.000000
            17.979139,49.476227,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Střední uměleckoprůmyslová škola sklářská</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style7</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.979950,49.476295,0.000000
            17.979927,49.476112,0.000000
            17.980085,49.476097,0.000000
            17.980103,49.476292,0.000000
            17.979950,49.476295,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Střední uměleckoprůmyslová škola sklářská</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style73</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.979561,49.476833,0.000000
            17.979721,49.476826,0.000000
            17.979694,49.476608,0.000000
            17.979822,49.476601,0.000000
            17.979813,49.476490,0.000000
            17.979244,49.476521,0.000000
            17.979258,49.476627,0.000000
            17.979536,49.476616,0.000000
            17.979561,49.476833,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZUŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style54</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970049,49.471817,0.000000
            17.970158,49.471840,0.000000
            17.970179,49.471794,0.000000
            17.970287,49.471809,0.000000
            17.970312,49.471741,0.000000
            17.970186,49.471725,0.000000
            17.970201,49.471699,0.000000
            17.970098,49.471676,0.000000
            17.970087,49.471706,0.000000
            17.969975,49.471691,0.000000
            17.969948,49.471771,0.000000
            17.970057,49.471790,0.000000
            17.970049,49.471817,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZUŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style3</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.967360,49.476341,0.000000
            17.967400,49.476269,0.000000
            17.967558,49.476311,0.000000
            17.967587,49.476261,0.000000
            17.967861,49.476330,0.000000
            17.967796,49.476440,0.000000
            17.967360,49.476341,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Středisko volného času Domeček</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style37</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.967907,49.465588,0.000000
            17.968052,49.465294,0.000000
            17.968243,49.465340,0.000000
            17.968225,49.465374,0.000000
            17.968477,49.465424,0.000000
            17.968597,49.465176,0.000000
            17.968657,49.465187,0.000000
            17.968714,49.465061,0.000000
            17.968681,49.465054,0.000000
            17.968714,49.464993,0.000000
            17.968609,49.464966,0.000000
            17.968760,49.464668,0.000000
            17.968475,49.464615,0.000000
            17.968325,49.464909,0.000000
            17.968416,49.464924,0.000000
            17.968231,49.465302,0.000000
            17.967920,49.465237,0.000000
            17.967907,49.465267,0.000000
            17.967758,49.465237,0.000000
            17.967619,49.465534,0.000000
            17.967907,49.465588,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Dětský domov</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style10</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.976137,49.471172,0.000000
            17.976431,49.471191,0.000000
            17.976463,49.470970,0.000000
            17.976170,49.470951,0.000000
            17.976137,49.471172,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Krizové centrum</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style39</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970484,49.467552,0.000000
            17.970505,49.467442,0.000000
            17.970783,49.467464,0.000000
            17.970762,49.467579,0.000000
            17.970484,49.467552,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Domov důchodců</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style16</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971367,49.463570,0.000000
            17.971458,49.463486,0.000000
            17.971657,49.463539,0.000000
            17.971725,49.463459,0.000000
            17.972141,49.463387,0.000000
            17.972139,49.463421,0.000000
            17.972240,49.463428,0.000000
            17.972321,49.462971,0.000000
            17.972187,49.462963,0.000000
            17.972191,49.462933,0.000000
            17.972122,49.462929,0.000000
            17.972050,49.463303,0.000000
            17.971518,49.463379,0.000000
            17.971577,49.463310,0.000000
            17.971390,49.463245,0.000000
            17.971161,49.463509,0.000000
            17.971367,49.463570,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Domov důchodců</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style22</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971958,49.462830,0.000000
            17.971949,49.462734,0.000000
            17.972166,49.462700,0.000000
            17.972219,49.462379,0.000000
            17.972277,49.462387,0.000000
            17.972298,49.462318,0.000000
            17.972473,49.462341,0.000000
            17.972366,49.462788,0.000000
            17.971958,49.462830,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Dům na půl cesty</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style14</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.966753,49.465763,0.000000
            17.966825,49.465649,0.000000
            17.966953,49.465683,0.000000
            17.966892,49.465794,0.000000
            17.966753,49.465763,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Dům na půl cesty</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style9</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.965088,49.481606,0.000000
            17.965052,49.481506,0.000000
            17.965252,49.481476,0.000000
            17.965288,49.481583,0.000000
            17.965088,49.481606,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Dům na půl cesty</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style33</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975510,49.461220,0.000000
            17.975512,49.461189,0.000000
            17.975763,49.461155,0.000000
            17.975815,49.461159,0.000000
            17.975796,49.461246,0.000000
            17.975510,49.461220,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Dům na půl cesty</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style63</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972176,49.478260,0.000000
            17.972357,49.478352,0.000000
            17.972488,49.478245,0.000000
            17.972298,49.478149,0.000000
            17.972176,49.478260,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Hospic</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style23</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.979551,49.471886,0.000000
            17.979410,49.471794,0.000000
            17.979523,49.471718,0.000000
            17.979548,49.471611,0.000000
            17.979521,49.471500,0.000000
            17.979404,49.471416,0.000000
            17.979488,49.471310,0.000000
            17.979595,49.471355,0.000000
            17.979670,49.471420,0.000000
            17.979715,49.471504,0.000000
            17.979866,49.471500,0.000000
            17.979860,49.471447,0.000000
            17.980255,49.471436,0.000000
            17.980259,49.471687,0.000000
            17.979879,49.471695,0.000000
            17.979877,49.471661,0.000000
            17.979734,49.471676,0.000000
            17.979654,49.471817,0.000000
            17.979551,49.471886,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kojenecký ústav</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style48</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.964830,49.469013,0.000000
            17.964878,49.468922,0.000000
            17.965101,49.468975,0.000000
            17.965052,49.469067,0.000000
            17.964830,49.469013,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kojenecký ústav</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style70</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.965322,49.469124,0.000000
            17.965425,49.468967,0.000000
            17.965302,49.468937,0.000000
            17.965342,49.468876,0.000000
            17.965609,49.468945,0.000000
            17.965485,49.469166,0.000000
            17.965322,49.469124,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Azylový dům</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style45</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.984776,49.468632,0.000000
            17.984941,49.468643,0.000000
            17.985001,49.468193,0.000000
            17.984823,49.468182,0.000000
            17.984776,49.468632,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Charita</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style52</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.965652,49.480656,0.000000
            17.965715,49.480545,0.000000
            17.966309,49.480694,0.000000
            17.966246,49.480797,0.000000
            17.965652,49.480656,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Nízkoprahové zařízení</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style68</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971037,49.472889,0.000000
            17.971077,49.472736,0.000000
            17.971441,49.472775,0.000000
            17.971399,49.472935,0.000000
            17.971037,49.472889,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Area Medica</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style28</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.968216,49.469791,0.000000
            17.968279,49.469589,0.000000
            17.968580,49.469635,0.000000
            17.968512,49.469833,0.000000
            17.968216,49.469791,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Ordinace</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style24</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970087,49.470192,0.000000
            17.970106,49.470100,0.000000
            17.970346,49.470135,0.000000
            17.970304,49.470234,0.000000
            17.970087,49.470192,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Ordinace</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style4</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.976648,49.464584,0.000000
            17.976656,49.464489,0.000000
            17.976856,49.464504,0.000000
            17.976843,49.464600,0.000000
            17.976648,49.464584,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Nemocnice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style30</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.976217,49.463177,0.000000
            17.976229,49.462933,0.000000
            17.975952,49.462921,0.000000
            17.975956,49.462791,0.000000
            17.976133,49.462673,0.000000
            17.976313,49.462494,0.000000
            17.977165,49.462528,0.000000
            17.977741,49.462418,0.000000
            17.977552,49.462132,0.000000
            17.977777,49.462067,0.000000
            17.977898,49.462261,0.000000
            17.978058,49.462215,0.000000
            17.978249,49.462608,0.000000
            17.977879,49.462688,0.000000
            17.977812,49.462551,0.000000
            17.977165,49.462677,0.000000
            17.977125,49.463039,0.000000
            17.977444,49.463058,0.000000
            17.977430,49.463184,0.000000
            17.976610,49.463142,0.000000
            17.976589,49.463188,0.000000
            17.976217,49.463177,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Nemocnice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style49</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.977274,49.463291,0.000000
            17.977282,49.463196,0.000000
            17.977800,49.463219,0.000000
            17.977844,49.462830,0.000000
            17.977962,49.462833,0.000000
            17.977900,49.463322,0.000000
            17.977274,49.463291,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Nemocnice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style51</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.978056,49.463234,0.000000
            17.978102,49.462868,0.000000
            17.978216,49.462875,0.000000
            17.978167,49.463242,0.000000
            17.978056,49.463234,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Nemocnice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style25</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.977171,49.463867,0.000000
            17.977196,49.463547,0.000000
            17.977390,49.463554,0.000000
            17.977390,49.463608,0.000000
            17.977686,49.463619,0.000000
            17.977686,49.463573,0.000000
            17.977867,49.463581,0.000000
            17.977831,49.463924,0.000000
            17.977636,49.463913,0.000000
            17.977659,49.463688,0.000000
            17.977592,49.463688,0.000000
            17.977592,49.463730,0.000000
            17.977451,49.463722,0.000000
            17.977451,49.463673,0.000000
            17.977377,49.463669,0.000000
            17.977364,49.463879,0.000000
            17.977171,49.463867,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Zubař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style2</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.966005,49.467232,0.000000
            17.966047,49.467144,0.000000
            17.966198,49.467178,0.000000
            17.966145,49.467262,0.000000
            17.966005,49.467232,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Zubař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style11</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.968899,49.473560,0.000000
            17.968958,49.473438,0.000000
            17.969137,49.473476,0.000000
            17.969072,49.473602,0.000000
            17.968899,49.473560,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Odborný lékař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style81</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970398,49.473522,0.000000
            17.970491,49.473541,0.000000
            17.970594,49.473358,0.000000
            17.970491,49.473335,0.000000
            17.970398,49.473522,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Odborný lékař, Lékárna</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style64</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972113,49.472782,0.000000
            17.972332,49.472675,0.000000
            17.972061,49.472645,0.000000
            17.972021,49.472778,0.000000
            17.972113,49.472782,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Odborný lékař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style78</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.973366,49.473461,0.000000
            17.973358,49.473370,0.000000
            17.973440,49.473366,0.000000
            17.973440,49.473335,0.000000
            17.973520,49.473331,0.000000
            17.973528,49.473457,0.000000
            17.973366,49.473461,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Odborný lékař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style19</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.964731,49.469593,0.000000
            17.964542,49.469547,0.000000
            17.964474,49.469669,0.000000
            17.964653,49.469715,0.000000
            17.964731,49.469593,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Lékárna</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style65</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970436,49.470230,0.000000
            17.970470,49.470161,0.000000
            17.970680,49.470211,0.000000
            17.970634,49.470287,0.000000
            17.970436,49.470230,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Lékárna</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style74</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971336,49.473129,0.000000
            17.971367,49.473038,0.000000
            17.971558,49.473061,0.000000
            17.971533,49.473156,0.000000
            17.971336,49.473129,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Lékárna</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style55</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972630,49.475056,0.000000
            17.972654,49.474983,0.000000
            17.972750,49.474998,0.000000
            17.972721,49.475071,0.000000
            17.972630,49.475056,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Lékárna</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style38</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.968472,49.474754,0.000000
            17.968515,49.474663,0.000000
            17.968664,49.474693,0.000000
            17.968620,49.474789,0.000000
            17.968472,49.474754,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Finanční úřad</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style75</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975403,49.474354,0.000000
            17.975603,49.474346,0.000000
            17.975626,49.474705,0.000000
            17.975441,49.474705,0.000000
            17.975403,49.474354,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Diakonie</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style43</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.975958,49.474777,0.000000
            17.975956,49.474712,0.000000
            17.975691,49.474689,0.000000
            17.975687,49.474762,0.000000
            17.975958,49.474777,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Hasiči</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style58</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.983496,49.468712,0.000000
            17.983557,49.468258,0.000000
            17.984598,49.468319,0.000000
            17.984568,49.468552,0.000000
            17.984364,49.468540,0.000000
            17.984331,49.468765,0.000000
            17.983496,49.468712,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Úřad práce</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style1</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.983351,49.470112,0.000000
            17.983541,49.470123,0.000000
            17.983576,49.469845,0.000000
            17.983383,49.469837,0.000000
            17.983351,49.470112,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Katastrální úřad</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style34</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.980856,49.470715,0.000000
            17.981068,49.470722,0.000000
            17.981115,49.470306,0.000000
            17.980907,49.470295,0.000000
            17.980856,49.470715,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Městský úřad</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style13</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970425,49.471344,0.000000
            17.970594,49.471378,0.000000
            17.970747,49.471024,0.000000
            17.970463,49.470970,0.000000
            17.970411,49.471069,0.000000
            17.970484,49.471081,0.000000
            17.970438,49.471165,0.000000
            17.970491,49.471188,0.000000
            17.970425,49.471344,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Radnice</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style27</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970724,49.471340,0.000000
            17.970757,49.471233,0.000000
            17.971239,49.471298,0.000000
            17.971197,49.471416,0.000000
            17.970724,49.471340,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Úřad práce</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style62</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.984119,49.476772,0.000000
            17.984270,49.476803,0.000000
            17.984308,49.476723,0.000000
            17.984818,49.476814,0.000000
            17.984858,49.476730,0.000000
            17.984295,49.476624,0.000000
            17.984348,49.476486,0.000000
            17.984110,49.476437,0.000000
            17.984064,49.476582,0.000000
            17.983706,49.476517,0.000000
            17.983669,49.476608,0.000000
            17.984150,49.476685,0.000000
            17.984119,49.476772,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Policie ČR</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style47</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972351,49.472500,0.000000
            17.972561,49.472538,0.000000
            17.972643,49.472343,0.000000
            17.972431,49.472305,0.000000
            17.972351,49.472500,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Městská policie</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style12</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970865,49.472336,0.000000
            17.970917,49.472206,0.000000
            17.971054,49.472233,0.000000
            17.970997,49.472366,0.000000
            17.970865,49.472336,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Soud</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style20</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.982264,49.469479,0.000000
            17.982307,49.469090,0.000000
            17.983063,49.469124,0.000000
            17.983004,49.469528,0.000000
            17.982264,49.469479,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kostel</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style66</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.965889,49.470062,0.000000
            17.965990,49.469856,0.000000
            17.966078,49.469879,0.000000
            17.966131,49.469776,0.000000
            17.966383,49.469830,0.000000
            17.966297,49.469997,0.000000
            17.966125,49.469959,0.000000
            17.966047,49.470100,0.000000
            17.965889,49.470062,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kostel</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style36</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970570,49.472561,0.000000
            17.970629,49.472431,0.000000
            17.971004,49.472507,0.000000
            17.971031,49.472549,0.000000
            17.971006,49.472599,0.000000
            17.970924,49.472630,0.000000
            17.970570,49.472561,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kostel</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style29</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.970987,49.472702,0.000000
            17.971004,49.472614,0.000000
            17.971138,49.472630,0.000000
            17.971121,49.472713,0.000000
            17.970987,49.472702,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Kostel</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style67</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.971125,49.472588,0.000000
            17.971144,49.472477,0.000000
            17.971472,49.472500,0.000000
            17.971455,49.472618,0.000000
            17.971125,49.472588,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Zubař</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style41</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.972033,49.469986,0.000000
            17.972054,49.469887,0.000000
            17.972168,49.469894,0.000000
            17.972153,49.469997,0.000000
            17.972033,49.469986,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>Domov důchodců</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style59</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.973351,49.472763,0.000000
            17.973396,49.472691,0.000000
            17.973309,49.472691,0.000000
            17.973301,49.472488,0.000000
            17.973366,49.472488,0.000000
            17.973351,49.472229,0.000000
            17.973625,49.472225,0.000000
            17.973639,49.472450,0.000000
            17.973543,49.472454,0.000000
            17.973551,49.472591,0.000000
            17.973703,49.472584,0.000000
            17.973644,49.472759,0.000000
            17.973351,49.472763,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
  <Placemark>
    <name>ZUŠ</name>
    <description><![CDATA[]]></description>
    <styleUrl>#style79</styleUrl>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <tessellate>1</tessellate>
          <coordinates>
            17.969324,49.470936,0.000000
            17.969507,49.470970,0.000000
            17.969690,49.470631,0.000000
            17.969528,49.470589,0.000000
            17.969324,49.470936,0.000000
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
</Document>
</kml>"""

    # herny zadane formou bodu
    PLACEMARK_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>Herny ve Valašském Meziříčí</name>
  <description><![CDATA[]]></description>
  <Style id="style21">
  </Style>
  <Style id="style27">
  </Style>
  <Style id="style9">
  </Style>
  <Style id="style32">
  </Style>
  <Style id="style13">
  </Style>
  <Style id="style22">
  </Style>
  <Style id="style18">
  </Style>
  <Style id="style33">
  </Style>
  <Style id="style7">
  </Style>
  <Style id="style24">
  </Style>
  <Style id="style20">
  </Style>
  <Style id="style8">
  </Style>
  <Style id="style4">
  </Style>
  <Style id="style25">
  </Style>
  <Style id="style19">
  </Style>
  <Style id="style29">
  </Style>
  <Style id="style5">
  </Style>
  <Style id="style16">
  </Style>
  <Style id="style31">
  </Style>
  <Style id="style6">
  </Style>
  <Style id="style3">
  </Style>
  <Style id="style1">
  </Style>
  <Style id="style11">
  </Style>
  <Style id="style28">
  </Style>
  <Style id="style10">
  </Style>
  <Style id="style30">
  </Style>
  <Style id="style12">
  </Style>
  <Style id="style17">
  </Style>
  <Style id="style15">
  </Style>
  <Style id="style14">
  </Style>
  <Style id="style26">
  </Style>
  <Style id="style23">
  </Style>
  <Style id="style2">
  </Style>
  <Placemark>
    <name>Hranická 290</name>
    <styleUrl>#style21</styleUrl>
    <Point>
      <coordinates>17.962866,49.481411,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zdeňka Fibicha 56</name>
    <styleUrl>#style27</styleUrl>
    <Point>
      <coordinates>17.969444,49.463028,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Poláškova 81/3</name>
    <styleUrl>#style9</styleUrl>
    <Point>
      <coordinates>17.972525,49.471096,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Poláškova 79/7</name>
    <styleUrl>#style32</styleUrl>
    <Point>
      <coordinates>17.972580,49.470905,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Nádražní 92</name>
    <styleUrl>#style13</styleUrl>
    <Point>
      <coordinates>17.968353,49.476578,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Nádražní 545</name>
    <styleUrl>#style22</styleUrl>
    <Point>
      <coordinates>17.961241,49.474422,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Pospíšilova 16</name>
    <styleUrl>#style18</styleUrl>
    <Point>
      <coordinates>17.971260,49.470551,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Křižná 32</name>
    <styleUrl>#style33</styleUrl>
    <Point>
      <coordinates>17.966234,49.473511,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Mostní 102</name>
    <styleUrl>#style7</styleUrl>
    <Point>
      <coordinates>17.971935,49.472740,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Vsetínská 1430</name>
    <styleUrl>#style24</styleUrl>
    <Point>
      <coordinates>17.973948,49.469498,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Havlíčkova 1264</name>
    <description><![CDATA[<i>Havlíčkova 1264</i><div><br>&nbsp;</div><div><img src="http://upload.wikimedia.org/wikipedia/commons/6/65/N%C3%A1m%C4%9Bst%C3%AD_ve_Vala%C5%A1sk%C3%A9m_Mezi%C5%99%C3%AD%C4%8D%C3%AD_2.jpg" style="width:244px"></div><div><ul><li>Typ výherních automatů: VHP</li></li><li>Počet automatů: 13</li></li><li>Povolení uděleno: 28.2.2008</li></li></ul></div>]]></description>
    <styleUrl>#style20</styleUrl>
    <Point>
      <coordinates>17.968456,49.468040,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Hřbitovní 484</name>
    <styleUrl>#style8</styleUrl>
    <Point>
      <coordinates>17.967030,49.481628,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Křižná 184</name>
    <styleUrl>#style4</styleUrl>
    <Point>
      <coordinates>17.965204,49.473248,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zdeňka Fibicha 1210</name>
    <styleUrl>#style25</styleUrl>
    <Point>
      <coordinates>17.968931,49.462799,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zašovská 461</name>
    <styleUrl>#style19</styleUrl>
    <Point>
      <coordinates>17.980494,49.476345,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Štěpánov 261</name>
    <styleUrl>#style29</styleUrl>
    <Point>
      <coordinates>17.986797,49.460407,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Mostní 461</name>
    <styleUrl>#style5</styleUrl>
    <Point>
      <coordinates>17.971598,49.473038,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Podlesí 71</name>
    <styleUrl>#style16</styleUrl>
    <Point>
      <coordinates>17.977732,49.455418,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Luční 28</name>
    <styleUrl>#style31</styleUrl>
    <Point>
      <coordinates>17.981487,49.463928,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zašovská 251</name>
    <styleUrl>#style6</styleUrl>
    <Point>
      <coordinates>17.973467,49.474529,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Pod Oborou 168</name>
    <styleUrl>#style3</styleUrl>
    <Point>
      <coordinates>17.971939,49.478481,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Mostní 267</name>
    <styleUrl>#style1</styleUrl>
    <Point>
      <coordinates>17.971516,49.472885,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Mírova 657</name>
    <styleUrl>#style11</styleUrl>
    <Point>
      <coordinates>17.974846,49.469559,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zašovská 261</name>
    <styleUrl>#style28</styleUrl>
    <Point>
      <coordinates>17.980267,49.475746,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Sokolská 1272</name>
    <styleUrl>#style10</styleUrl>
    <Point>
      <coordinates>17.972492,49.470009,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Štěpánov 541</name>
    <styleUrl>#style30</styleUrl>
    <Point>
      <coordinates>17.981459,49.464214,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Jičínská 1308/1</name>
    <styleUrl>#style12</styleUrl>
    <Point>
      <coordinates>17.974266,49.476463,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Na Mlynářce 128/6</name>
    <styleUrl>#style17</styleUrl>
    <Point>
      <coordinates>17.972948,49.477966,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Poláškova 17</name>
    <styleUrl>#style15</styleUrl>
    <Point>
      <coordinates>17.970823,49.470493,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Nádražní 207</name>
    <styleUrl>#style14</styleUrl>
    <Point>
      <coordinates>17.967112,49.476147,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Zašovská 758</name>
    <styleUrl>#style26</styleUrl>
    <Point>
      <coordinates>17.980267,49.475746,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Vrbenská 805</name>
    <styleUrl>#style23</styleUrl>
    <Point>
      <coordinates>17.973951,49.473682,0.000000</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Podlesí 102</name>
    <styleUrl>#style2</styleUrl>
    <Point>
      <coordinates>17.977968,49.454044,0.000000</coordinates>
    </Point>
  </Placemark>
</Document>
</kml>"""

    # obsah stranky z Wikipedie (popis obce)
    WIKIPEDIA_XML = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.5/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.5/ http://www.mediawiki.org/xml/export-0.5.xsd" version="0.5" xml:lang="en">
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

