# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.geo.models import Entry, Zone, Building, Hell

admin.site.register(Entry)
admin.site.register(Zone)
admin.site.register(Building)
admin.site.register(Hell)
