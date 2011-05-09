# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.geo.models import Entry, Zone, Building, Hell
from hazard.shared.cache import clear_cache

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'slug', 'public', 'dperc_display', 'dhell_count_display', 'dper_population_display', 'dper_area_display')
    list_filter = ('public', )
    list_editable = ('public', 'slug', )
    readonly_fields = ('wikipedia', 'hell_url', 'building_url', 'ip')
    search_fields = ('title', 'slug')
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
        clear_cache()

    def dperc_display(self, obj):
        return u"%i%%" % round(obj.dperc)
    dperc_display.short_description = u"Protiprávních"

    def dhell_count_display(self, obj):
        return u"%i" % obj.dhell_count
    dhell_count_display.short_description = u"Počet heren"

    def dper_population_display(self, obj):
        return u"%i" % round(obj.dper_population)
    dper_population_display.short_description = u"Obyvatel/hernu"

    def dper_area_display(self, obj):
        return u"%.3f" % obj.dper_area
    dper_area_display.short_description = u"Heren/km"


admin.site.register(Entry, EntryAdmin)
admin.site.register(Zone)
admin.site.register(Building)
admin.site.register(Hell)
