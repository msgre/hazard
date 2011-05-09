# -*- coding: utf-8 -*-

import logging
import urllib2

from hazard.shared.czech import slugify

logger = logging.getLogger(__name__)


def download_content(url):
    """
    Stahne obsah ze zadaneho URL.
    """
    opener = urllib2.Request(url, headers={'User-agent':'Mozilla/5.0'})
    f = urllib2.urlopen(opener)
    content = f.read()
    f.close()
    return content

def get_unique_slug(title):
    """
    Vrati jedinecny slug pro zaznam Entry a priznak, jestli se musela "vypocitavat"
    alternativni forma s cislem (protoze v DB uz stejny slug existuje).
    """
    from hazard.geo.models import Entry

    slug = slugify(title)
    exists = False
    if Entry.objects.filter(slug=slug).exists():
        last_id = Entry.objects.all().order_by('-id').values_list('id', flat=True)[0]
        slug = "%s-%i" % (slug, last_id + 10)
        exists = True
    return slug, exists
