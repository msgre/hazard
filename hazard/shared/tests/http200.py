# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class Http200TestCase(TestCase):
    """
    Kontrola dostupnosti jednotlivych sekci webu.

    Poznamka: detail obce netestuju, protoze k tomu je treba naplnit DB
    a to se mi tu nechce delat. Tohle se stejne proveruje v testu formiku.
    """

    def setUp(self):
        self.client = Client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_form(self):
        response = self.client.get('/pridat/')
        self.assertEqual(response.status_code, 200)

    def test_list(self):
        response = self.client.get('/hitparada/')
        self.assertEqual(response.status_code, 200)

    def test_full_list(self):
        response = self.client.get('/hitparada/kompletni/')
        self.assertEqual(response.status_code, 200)

    def test_contact(self):
        response = self.client.get('/kontakt/')
        self.assertEqual(response.status_code, 200)

    def test_help(self):
        response = self.client.get('/navod/')
        self.assertEqual(response.status_code, 200)

    def test_cooperation(self):
        response = self.client.get('/spoluprace/')
        self.assertEqual(response.status_code, 200)

    def test_news(self):
        response = self.client.get('/zpravy/')
        self.assertEqual(response.status_code, 200)
