# -*- coding: utf-8 -*-

import logging
import urllib2

from hazard.shared.czech import slugify

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

def get_unique_slug(title):
    """
    Vrati jedinecny slug pro zaznam Entry.
    """
    from hazard.geo.models import Entry

    slug = slugify(title)
    if Entry.objects.filter(slug=slug).exists():
        last_id = Entry.objects.all().order_by('-id').values_list('id', flat=True)[0]
        slug = "%s-%i" % (slug, last_id + 10)
    return slug
