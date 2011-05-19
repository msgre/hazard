# -*- coding: utf-8 -*-

import mox
import StringIO
import urllib2

from django.test import TestCase

from hazard.geo.utils import download_content


class UtilsTestCase(TestCase):
    RESPONSE = '<?xml version="1.0" encoding="utf-8"?><foo>bar</foo>'

    def setUp(self):
        # mock urllib2 knihovny
        self.m = mox.Mox()
        response = StringIO.StringIO(self.RESPONSE)
        self.m.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen(mox.IgnoreArg()).AndReturn(response)
        self.m.ReplayAll()

    def tearDown(self):
        self.m.UnsetStubs()
        self.m.VerifyAll()

    def test_downloand_content(self):
        content = download_content('http://fakeurl.com/')
        self.assertEqual(content, self.RESPONSE)
