# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.geo.models import Entry, Zone, Building, Hell

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'slug', 'public', 'dperc', 'dhell_count', 'dper_population', 'dper_area' )
    list_filter = ('public', )
    list_editable = ('public', 'slug', )
    readonly_fields = ('wikipedia', 'hell_url', 'building_url', 'ip')
    date_hierarchy = 'created'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'email', 'public')
        }),
        (u'Informace vysosnuté z Wikipedie', {
            'fields': ('population', 'area', 'wikipedia')
        }),
        (u'Doplňující informace', {
            'classes': ('collapse',),
            'fields': ('hell_url', 'building_url', 'ip')
        }),
    )


    def save_model(self, request, obj, form, change):
        """
        Pri ulozeni objektu prepocitame
        """
        obj.recalculate_denormalized_values(counts=True)
        obj.save()

admin.site.register(Entry, EntryAdmin)
admin.site.register(Zone)
admin.site.register(Building)
admin.site.register(Hell)
