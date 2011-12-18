# -*- coding: utf-8 -*-

from django.contrib import admin

from hazard.territories.models import Region, District, Town, Zip


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('title', 'region')
    search_fields = ('title', 'slug')
    list_filter = ('region', )


class TownAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'region', 'display_zip')
    search_fields = ('title', 'slug')
    list_filter = ('region', 'district', )

    def display_zip(self, obj):
        return u", ".join([i.display() for i in obj.zip_set.all()])
    display_zip.short_description = u"PSČ"


class ZipAdmin(admin.ModelAdmin):
    list_display = ('title', 'town')
    search_fields = ('title', 'slug')


admin.site.register(Region)
admin.site.register(District, DistrictAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(Zip, ZipAdmin)
