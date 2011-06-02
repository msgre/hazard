# -*- coding: utf-8 -*-

import time
import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache

from hazard.geo.utils import connect_redis


logger = logging.getLogger(__name__)
IP_KEY = 'ip:'
POSTS_KEY = 'posts'
PERIOD = 120
POSTS_PER_PERIOD = 8
IP_PERIOD = 60
POSTS_PER_IP_AND_PERIOD = 2
PROCESSING_LIMIT = 2


class HttpResponseRequestTimeout(HttpResponse):
    status_code = 408


class ProcessingLimitMiddleware(object):
    """
    Jednoduchy middleware, ktery vrati HTTP status 408 tehdy, pokud prijde
    POST na adresu /pridat/ a podle udaju v cache prave probiha zpracovavani
    jinych postu.
    """
    def __init__(self, *args, **kwargs):
        self.redis = connect_redis()

    def process_request(self, request):
        if request.method == 'POST' and request.path == reverse('entry-form'):
            count = self.redis.get('processing')
            if count and int(count) >= PROCESSING_LIMIT:
                logger.info('POST request blocked due to processing limit: %s' % request)
                return HttpResponseRequestTimeout()


class PostLimitMiddleware(object):
    """
    Jednoduchy middleware, ktery hlida pocet POSTu na adresu /pridat/, a to
    dvojim zpusobem:

    * celkovy pocet POSTu provedenych za PERIOD vterin; pokud jich je vice
      nez POSTS_PER_PERIOD, pak aplikace vrati HTTP response kod 408 (Timeout)
    * celkovy pocet POSTu provedenych za IP_PERIOD vterin z dane IP adresy; pokud
      jich je vice nez POSTS_PER_IP_AND_PERIOD, pak aplikace vrati HTTP response
      kod 408 (Timeout)

    Smyslem celeho middleware je zabranit zahlceni serveru pozadavky o prekresleni
    mapy, ktere je casove narocne.
    """
    def __init__(self, *args, **kwargs):
        self.redis = connect_redis()
        self.bypass = hasattr(settings, 'BYPASS_AE_MIDDLEWARE') and getattr(settings, 'BYPASS_AE_MIDDLEWARE', False)

    def process_request(self, request):
        if request.method == 'POST' and request.path == reverse('entry-form'):

            # mame za zadkem redis? mame to tu zkratnout?
            if not self.redis or self.bypass:
                return

            self.now = time.time()

            # proverime celkovy pocet postu
            if not self._check(POSTS_KEY, POSTS_PER_PERIOD, PERIOD):
                return HttpResponseRequestTimeout()

            # proverime pocet postu z IP adresy
            ip_key = IP_KEY + request.META.get('REMOTE_ADDR', 'unkwnown_ip')
            if not self._check(ip_key, POSTS_PER_IP_AND_PERIOD, IP_PERIOD):
                return HttpResponseRequestTimeout()

    def _check(self, key, size, period):
        """
        Pomocna metoda -- overi stari posledniho prvku v seznamu `key` a pokud
        je mladsi nez `period`, vrati False. V opacnem pripade aktualizuje
        seznam aktualnim timestampem, orizne pole na velikost `size` a vrati
        True.
        """
        # proverime celkovy pocet postu
        oldest_entry = self.redis.lrange(key, 0, size - 1)
        if oldest_entry and len(oldest_entry) >= size and \
           self.now - float(oldest_entry[-1]) < period:
            logger.debug('Oldest entry from %s is too young => %.2f s. POST is forbidden.' % (key, self.now - float(oldest_entry[-1])))
            return False

        # uchovame zaznam o postnuti
        self.redis.lpush(key, self.now)
        self.redis.ltrim(key, 0, size - 1)
        return True
