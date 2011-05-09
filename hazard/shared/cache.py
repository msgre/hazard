# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

import os
from django.conf import settings

def clear_cache():
    path = os.path.abspath(os.path.join(settings.PROJECT_PATH, '../cache/'))
    os.system('rm -rf %s/*' % path)
