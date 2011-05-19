# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

"""
Testy pridavani a aktualizovani podniku pres formik /pridat/ a kliknuti
na tlacitko "Aktualizovat" v detailu obce.

Poznamka:
Pro praci s formulari pouzivam knihovnu mox, s pomoci ktere fejkuju
reakce na urllib a urllib2. Diky tomu nejsem odkazan na online komunikaci
se servery, a knihovny reaguji tak jak potrebuju.
"""

import mox
import StringIO
import urllib
import urllib2

from django.test import TestCase
from django.test.client import Client

from hazard.geo.models import Entry



class FormTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.mox.UnsetStubs()
        self.mox.VerifyAll()

    # -----------------------------------------------------------

    def test_add(self):
        """
        Prida na stranky novy zaznam o obci.
        """
        self._common()

    def test_add_same_kml(self):
        """
        Pridame pres klasicky formik stejny zaznam o obci vedouci na *totozne*
        KML mapy jako originalni zaznam, pricemz data v KML jsou nezmenena.

        Co se ma stat:
        - v DB se nic nezmeni, zustava v ni pouze originalni zaznam
        - ve formiku se objevi error hlaska, ze data se nezmenila
        """
        # vlozime do stranek zaznam o obci
        self._common()
        # vlozime do stranek totozny zaznam podruhe
        response = self._common(check_response=False)
        self.assertEqual(len(response.redirect_chain), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(u'se nezměnily, záznam na našich stránkách je aktuální.' in response.content.decode('utf-8'))

    def test_add_different_kml_content(self):
        """
        Pridame pres klasicky formik stejny zaznam o obci vedouci na *totozne*
        KML mapy jako originalni zaznam, ale uvnitr map doslo k nejake zmene.

        Co se ma stat:
        - stary zaznam zustava v db ale meni se mu public a slug
        - v db se objevuje novy zaznam, s jednoduchym slugem a verejny
        - dochazi k presmerovani na detail (a mozna s hlaskou ze se zaznam
          *aktualizoval*)
        """
        # vlozime do stranek zaznam o obci
        self._common()

        # podruhe vlozime do stranek stejna URL, ale obsah jedne z map upravime
        modified_kml = self._modify_kml()
        mox_args = [modified_kml, self.POLYGON_KML, self.WIKIPEDIA_XML]
        self._common(mox_args=mox_args, check_db=False)

        # kontrola DB
        entries = Entry.objects.all().order_by('-created')
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0].public)
        self.assertEqual(entries[0].slug, 'valasske-mezirici')
        self.assertFalse(entries[1].public)
        self.assertEqual(entries[1].slug, 'valasske-mezirici-%i' % entries[1].id)
        self.assertEqual(entries[0].hell_set.count(), entries[1].hell_set.count()-1)
        self.assertEqual(entries[0].building_set.count(), entries[1].building_set.count())

    def test_add_different_kml_url(self):
        """
        Pridame pres klasicky formik stejny zaznam o obci vedouci na *jine*
        URL KML map, nez ma originalni zaznam v DB. Jejich obsah ale zustava
        stejny.

        Co se ma stat:
        - nova data se ulozi do db, slug bude mit skaredy suffix, zaznam nebude zverejnen
        - uzivatel bude presmerovan na detail se zpravou, ze to neni zverejene,
          a ze to musime manualne zkontrolovat
        """
        # vlozime do stranek zaznam o obci
        self._common()

        # vlozime zaznam podruhe, stejna obec ale jina zdrojova data
        response = self._common(hell_url='http://fake-hell.com/?p=2', \
                                building_url='http://fake-building.com/?p=3', \
                                check_db=False, check_response=False)

        entries = Entry.objects.all().order_by('-created')

        # kontrola odpovedi
        self._check_response(response, '/d/%s/' % entries[0].slug)
        self.assertTrue(u'v databázi již máme a Váš příspěvek musíme manuálně zkontrolovat' in response.content.decode('utf-8'))

        # kontrola DB
        self.assertEqual(Entry.objects.count(), 2)
        self.assertFalse(entries[0].public)
        self.assertNotEqual(entries[0].slug, 'valasske-mezirici')
        self.assertTrue(entries[1].public)
        self.assertEqual(entries[1].slug, 'valasske-mezirici')
        self.assertEqual(entries[0].hell_set.count(), entries[1].hell_set.count())
        self.assertEqual(entries[0].building_set.count(), entries[1].building_set.count())

    def test_update_same_kml(self):
        """
        V detailu zaznamu klikneme na tlacitko "Aktualizovat mapu". Zdrojova
        data ani URL se v nicem nezmenila.

        Co se ma stat:
        - chovani stejne jako odeslani totoznych URL pro existujici podnik
          z formulare pro pridani nove obce
        - v DB se nic nezmeni, zustava v ni pouze originalni zaznam
        - maly rozdil -- po odeslani formiku zustavame v detailu obce
          a zobrazi se nam informacni hlaska ze se data nezmenila
        """
        # vlozime do stranek zaznam o obci
        self._common()

        # tupnem na tlacitko "Aktualizovat mapu" v detailu obce
        response = self._common(form_data={'slug': 'valasske-mezirici'})

        # overime response
        self.assertTrue(u'se nezměnily, záznam na našich stránkách je aktuální.' in response.content.decode('utf-8'))

    def test_update_different_kml_content(self):
        """
        V detailu zaznamu klikneme na tlacitko "Aktualizovat mapu". Zdrojova
        URL se nezmenila, ale v obsahu jedne z map doslo ke zmene.

        Co se ma stat:
        - zustaneme na strance
        - do DB se ulozi novy zaznam a zverejni se
        - na strance se objevi hlaska o aktuaizaci
        """
        # vlozime do stranek zaznam o obci
        self._common()

        # podruhe vlozime do stranek stejna URL, ale obsah jedne z map upravime
        modified_kml = self._modify_kml()
        mox_args = [modified_kml, self.POLYGON_KML, self.WIKIPEDIA_XML]
        response = self._common(mox_args=mox_args, check_db=False,
                     form_data={'slug': 'valasske-mezirici'})
        self.assertTrue(u'v databázi již máme a Váš příspěvek musíme manuálně zkontrolovat' in response.content.decode('utf-8'))

        # kontrola DB
        entries = Entry.objects.all().order_by('-created')
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0].public)
        self.assertEqual(entries[0].slug, 'valasske-mezirici')
        self.assertFalse(entries[1].public)
        self.assertEqual(entries[1].slug, 'valasske-mezirici-%i' % entries[1].id)
        self.assertEqual(entries[0].hell_set.count(), entries[1].hell_set.count()-1)
        self.assertEqual(entries[0].building_set.count(), entries[1].building_set.count())

    def test_add_unpublished_entry(self):
        """
        Vlozime pres formik dalsi zaznam o podniku, ktery uz sice v DB je,
        ale neni verejny. Novy zaznam ma stejna URL jako stary, ale obsah jedne
        z KML map se zmenil.

        Co se ma stat:
        - nova data se ulozi do DB, slug bude pekny, public bude False
        - stara data zustavaji v DB, slug se zeskaredi a public zustava False
        - uzivatel bude presmerovan na detail se zpravou, ze to neni zverejene,
          a ze to musime manualne zkontrolovat
        """
        # vlozime do stranek zaznam o obci a zneverejnime ho
        self._common()
        Entry.objects.all().update(public=False)

        # upravime obsah KML mapy
        modified_kml = self._modify_kml()
        mox_args = [modified_kml, self.POLYGON_KML, self.WIKIPEDIA_XML]

        # vlozime zaznam do DB podruhe
        response = self._common(mox_args=mox_args, check_db=False)
        self.assertTrue(u'v databázi již máme a Váš příspěvek musíme manuálně zkontrolovat' in response.content.decode('utf-8'))

        # kontrola DB
        entries = Entry.objects.all().order_by('-created')
        self.assertEqual(len(entries), 2)
        self.assertFalse(entries[0].public)
        self.assertEqual(entries[0].slug, 'valasske-mezirici')
        self.assertFalse(entries[1].public)
        self.assertEqual(entries[1].slug, 'valasske-mezirici-%i' % entries[1].id)


    # ---[ pomocne metody ]----------------------------------------------------

    def _common(self, mox_args=None, hell_url='http://fake-hell.com/?p=1', \
                building_url='http://fake-building.com/?p=1', \
                slug='valasske-mezirici', check_response=True, check_db=True,
                form_data={}):
        """
        Pomocna metoda, ktera prida novy zaznam o obci pres formik /pridat/.
        """
        # ofejkujem urllib2 (dotazy na KML mapy)
        if mox_args is None:
            mox_args = [self.PLACEMARK_KML, self.POLYGON_KML, self.WIKIPEDIA_XML]
        self.setup_mox(*mox_args)

        # odesleme formik s pridanim nove obce
        form_data.update({
            'hells': hell_url, # viz setup_mox
            'buildings': building_url # viz setup_mox
        })
        response = self.client.post('/pridat/', form_data, follow=True)

        # po uspesnem odeslani jsme presmerovani na detail zaznamu
        if check_response:
            self._check_response(response, '/d/valasske-mezirici/')

        # kontrola stavu v DB
        if check_db:
            entry = Entry.objects.filter(slug=slug)
            self.assertEqual(len(entry), 1)
            entry = entry[0]
            self.assertEqual(entry.hell_set.count(), 11)
            self.assertEqual(entry.building_set.count(), 19)

        return response

    def _modify_kml(self):
        modified_kml = self.PLACEMARK_KML
        modified_kml = modified_kml[:modified_kml.rfind('<Placemark>')]
        modified_kml += '</Document></kml>'
        return modified_kml

    def _check_response(self, response, url):
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(url in response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)

    def setup_mox(self, *args):
        """
        Ofejkovani knihoven urllib2 a urllib tak, aby vracely moje data.
        """
        self.mox = mox.Mox()

        # fejk na download KML map a XML wikipedie
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        for arg in args:
            urllib2.urlopen(mox.IgnoreArg()).AndReturn(StringIO.StringIO(arg))

        # fejk na download Google Geocoders
        self.mox.StubOutWithMock(urllib, 'urlopen')
        urllib.urlopen(mox.IgnoreArg()).AndReturn(StringIO.StringIO(self.GEO_JSON))

        self.mox.ReplayAll()


    # ---[ data simulujici komunikaci s externimi servery ] -------------------

    # odpoved z Google Geocoders pro Valmez
    GEO_JSON = u"""{
  "name": "49.47198, 17.9689856364",
  "Status": {
    "code": 200,
    "request": "geocode"
  },
  "Placemark": [ {
    "id": "p1",
    "address": "Komenského 1/3, 757 01 Valašské Meziříčí, Česká republika",
    "AddressDetails": {
   "Accuracy" : 8,
   "Country" : {
      "AdministrativeArea" : {
         "AdministrativeAreaName" : "Zlínský",
         "SubAdministrativeArea" : {
            "PostalCode" : {
               "PostalCodeNumber" : "757 01"
            },
            "SubAdministrativeAreaName" : "Valašské Meziříčí",
            "Thoroughfare" : {
               "ThoroughfareName" : "Komenského 1/3"
            }
         }
      },
      "CountryName" : "Česká republika",
      "CountryNameCode" : "CZ"
   }
},
    "ExtendedData": {
      "LatLonBox": {
        "north": 49.4749820,
        "south": 49.4686868,
        "east": 17.9725334,
        "west": 17.9662382
      }
    },
    "Point": {
      "coordinates": [ 17.9693858, 49.4718344, 0 ]
    }
  } ]
}"""

    # herny ve Valmezu
    PLACEMARK_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>Herny ve Valašském Meziříčí</name>
  <description><![CDATA[]]></description>
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
</Document>
</kml>"""

    # budovy ve valmezu
    POLYGON_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>Veřejné budovy</name>
  <description><![CDATA[]]></description>
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
