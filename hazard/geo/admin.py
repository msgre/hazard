# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.geo.models import Entry, Zone, Building, Hell
from hazard.shared.admin import ClearCacheMixin


class EntryAdmin(ClearCacheMixin):
    list_display = ('title', 'created', 'slug', 'public', 'dperc_display', 'dhell_count_display', 'dper_population_display', 'dper_area_display')
    list_filter = ('public', )
    list_editable = ('public', 'slug',)
    readonly_fields = ('wikipedia', 'hell_url', 'building_url', 'ip')
    search_fields = ('title', 'slug')
    date_hierarchy = 'created'
    ordering = ('-created',)

    class Media:
        js = ("js/lib/entry_admin.js",)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'email', 'public')
        }),
        (u'Informace vysosnuté z Wikipedie', {
            'classes': ('collapse',),
            'fields': ('population', 'area', 'wikipedia')
        }),
        (u'Doplňující informace', {
            'classes': ('collapse',),
            'fields': ('hell_url', 'building_url', 'ip')
        }),
    )
    actions = ['publish_new_one']

    def save_model(self, request, obj, form, change):
        """
        Pri ulozeni objektu prepocitame
        """
        obj.recalculate_denormalized_values(counts=True)
        super(EntryAdmin, self).save_model(request, obj, form, change)

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

    def publish_new_one(self, request, queryset):
        """
        Pomocna action metoda, ktera slouzi k rychlemu zverejneni cerstvejsiho
        zaznamu. Stava se, ze v systemu mame vice zaznamu pro teze mesto
        a potrebujem rychle stary zaznam skryt (a pridat ke slugu ID), a rychle
        zverejnit novy zaznam (a ufiknout mu skaredy suffix u slugu).

        No a presne k tomuto ucelu slouzi tato metoda.
        """
        if queryset.count() != 2:
            self.message_user(request, u"Označ 2 záznamy, starý publikovaný a nový nepublikovaný.")
        else:
            old = queryset.filter(public=True)
            new = queryset.filter(public=False)
            if not old:
                self.message_user(request, u"Neoznačil jsi starý publikovaný záznam.")
            elif not new:
                self.message_user(request, u"Neoznačil jsi nový, dosud nepublikovaný záznam.")
            else:
                old, new = old[0], new[0]
                # stary zaznam schovame a pridame ke slugu ID
                old.slug = "%s-%i" % (old.slug, old.id)
                old.public = False
                old.save()
                # novy zaznam zverejnime a slug zpeknime
                new.slug = "-".join(new.slug.split('-')[:-1])
                new.public = True
                new.save()
                self.message_user(request, u"Novější záznam byl zveřejněn, starý utlumen.")
    publish_new_one.short_description = u"Publikovat novější záznam"


class ZoneAdmin(ClearCacheMixin):
    pass

class BuildingAdmin(ClearCacheMixin):
    pass

class HellAdmin(ClearCacheMixin):
    pass


admin.site.register(Entry, EntryAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Hell, HellAdmin)
