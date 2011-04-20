# -*- coding: utf-8 -*-

import logging
import urllib2

logger = logging.getLogger(__name__)


def download_content(url):
    """
    Stahne obsah ze zadaneho URL.
    """
    try:
        opener = urllib2.Request(url, headers={'User-agent':'Mozilla/5.0'})
        f = urllib2.urlopen(opener)
        content = f.read()
        f.close()
        return content
    except e:
        logger.debug('Exception %s during downloading %s' % (e, url))
        return None
