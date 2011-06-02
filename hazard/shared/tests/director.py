# -*- coding: utf-8 -*-

from django.test import TestCase
from hazard.shared.director import director


class DirectorTestCase(TestCase):
    """
    Testy reditelicka -- pidikod, ktery se nam stara o spravu behem pridavani
    a aktualizace map.
    """

    def setUp(self):
        director.select_db(2)
        self.assertEqual(director.current, {})
        self.assertEqual(director.next(), False)
        self.assertEqual(director.done('xyz'), False)

    def tearDown(self):
        director.client.flushdb()

    def test_one_item_in_queue(self):
        # pridame ukol...
        self.assertEqual(director.add('pokus1'), True)
        # ...a protoze je prvni, hned se zaradi pod current
        self.assertEqual(director.current, {'pokus1': ''})

        # dalsi ukol nemuzeme pridat, protoze ve fronte zadny dalsi ukol neni
        self.assertEqual(director.next(), False)

        # dokoncime praci a fronta je zase prazdna
        self.assertEqual(director.done('pokus1'), True)
        self.assertEqual(director.current, {})

    def test_two_items_in_queue(self):
        # pridame do fronty 2 ukoly
        self.assertEqual(director.add('pokus1'), True)
        self.assertEqual(director.add('pokus2'), False)

        # aktualni je ten prvni pridany
        self.assertEqual(director.current, {'pokus1': ''})

        # dalsi ukol zaradit nemuzeme, protoze prvni ukol jeste neni hotov
        self.assertEqual(director.next(), False)
        self.assertEqual(director.done('pokus1'), True)

        # ted uz to mozne bude
        self.assertEqual(director.current, {})
        self.assertEqual(director.next(), 'pokus2')
        self.assertEqual(director.current, {'pokus2': ''})
        self.assertEqual(director.next(), False)
        self.assertEqual(director.done('pokus2'), True)
        self.assertEqual(director.current, {})

    def test_two_items_in_queue_simplified(self):
        # pridame do fronty 2 ukoly
        self.assertEqual(director.add('pokus1'), True)
        self.assertEqual(director.add('pokus2'), False)

        # aktualni je ten prvni pridany
        self.assertEqual(director.current, {'pokus1': ''})

        # ukoncime prvni, zaradime druhy
        self.assertEqual(director.done_and_next('pokus1'), 'pokus2')
        self.assertEqual(director.current, {'pokus2': ''})

        # ukoncime druhy a mame hotovo
        self.assertEqual(director.done_and_next('pokus2'), False)
        self.assertEqual(director.current, {})

    def test_multiple_same_items(self):
        # pridame do fronty vicekrat stejny ukol
        self.assertEqual(director.add('pokus1'), True)
        self.assertEqual(director.add('pokus1'), False)
        self.assertEqual(director.add('pokus1'), False)
        self.assertEqual(director.add('pokus1'), False)

        # ukol je zarazen a je aktualni
        self.assertEqual(director.current, {'pokus1': ''})

        # po jeho ukonceni uz v bufferu nic jineho neni
        self.assertEqual(director.done_and_next('pokus1'), False)
        self.assertEqual(director.current, {})

    def test_multiple_same_items2(self):
        # pridame do fronty vicekrat stejny ukol, prolozeny inacim ukolem
        self.assertEqual(director.add('pokus1'), True)
        self.assertEqual(director.add('pokus1'), False)
        self.assertEqual(director.add('upe_neco_jineho'), False)
        self.assertEqual(director.add('pokus1'), False)
        self.assertEqual(director.add('pokus1'), False)

        # prvni ukol je zarazen a je aktualni
        self.assertEqual(director.current, {'pokus1': ''})

        # po jeho ukonceni nas ceka druhy ukol
        self.assertEqual(director.done_and_next('pokus1'), 'upe_neco_jineho')
        self.assertEqual(director.current, {'upe_neco_jineho': ''})

        # no a pak uz fak nic
        self.assertEqual(director.done_and_next('upe_neco_jineho'), False)
        self.assertEqual(director.current, {})

    def test_is_waiting(self):
        # ve fronte nic neni
        self.assertEqual(director.is_waiting('pokus1'), False)

        # ve fronte nic neni, ale jeden ukol se prave zpracovava
        self.assertEqual(director.add('pokus1'), True)
        self.assertEqual(director.is_waiting('pokus1'), False)

        # ve fronte neco je a ceka to na zpracovani
        self.assertEqual(director.add('pokus2'), False)
        self.assertEqual(director.is_waiting('pokus2'), True)

        # dokoncime prvni ukol a uz se na nic neceka
        self.assertEqual(director.done_and_next('pokus1'), 'pokus2')
        self.assertEqual(director.is_waiting('pokus2'), False)

        # dokoncime druhy ukol a uz se vubec na nic neceka
        self.assertEqual(director.done_and_next('pokus2'), False)
        self.assertEqual(director.is_waiting('pokus2'), False)

    def test_value(self):
        # pridame ukol...
        self.assertEqual(director.add('pokus1', 'hodnota'), True)
        # ...a protoze je prvni, hned se zaradi pod current
        self.assertEqual(director.current, {'pokus1': 'hodnota'})

        # dalsi ukol nemuzeme pridat, protoze ve fronte zadny dalsi ukol neni
        self.assertEqual(director.next(), False)

        # dokoncime praci a fronta je zase prazdna
        self.assertEqual(director.done('pokus1'), True)
        self.assertEqual(director.current, {})
