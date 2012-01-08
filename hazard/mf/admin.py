# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.gis.admin.options import OSMGeoAdmin

from hazard.mf.models import MfPlaceType, MfPlace, MfAddressSurround, MfPlaceConflict


admin.site.register(MfPlaceType)
admin.site.register(MfPlaceConflict)
admin.site.register(MfPlace)


class MfAddressSurroundAdmin(OSMGeoAdmin):
    pass

admin.site.register(MfAddressSurround, MfAddressSurroundAdmin)
