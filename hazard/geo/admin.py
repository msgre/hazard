# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from hazard.geo.models import Entry, Zone, Building, Hell
from hazard.geo.forms import EmailForm
from hazard.shared.admin import ClearCacheMixin


class EntryAdmin(ClearCacheMixin):
    list_display = ('title', 'created', 'slug', 'public', 'dperc_display', 'dhell_count_display', 'dper_population_display', 'dper_area_display', 'email_author')
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
    dhell_count_display.short_description = u"Heren"

    def dper_population_display(self, obj):
        return u"%i" % round(obj.dper_population)
    dper_population_display.short_description = u"Obyv./hernu"

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
                if old.title != new.title:
                    self.message_user(request, u"Asi jsi označil 2 záznamy z různých měst, protože názvy obcí v označených řádcích se neshodují.")
                else:
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

    def email_author(self, obj):
        """
        Link do changelist tabulky pro odeslani emailu autorovi mapovych
        podkladu.
        """
        if obj.email:
            return u'<a href="./%i/email/">Poslat vzkaz</a>' % obj.id
        else:
            return ''
    email_author.short_description = u""
    email_author.allow_tags = True

    def get_urls(self):
        urls = super(EntryAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(?P<id>\d+)/email/$', self.admin_site.admin_view(self.email_view))
        )
        return my_urls + urls

    def email_view(self, request, id):
        """
        View pro odeslani vzkazu autorovi mapovych podkladu.
        """
        obj = get_object_or_404(Entry, pk=id)
        if request.method == 'POST':
            form = EmailForm(request.POST)
            if form.is_valid():
                form.send_email(obj.email)
                return HttpResponseRedirect(request.path + '../../')
        else:
            form = EmailForm(initial={
                'subject': u'Mapy k obci %s' % obj.title,
                'content': EmailForm.DEFAULT_EMAIL_MESSAGE % {'title': obj.title}
            })

        adminform = admin.helpers.AdminForm(form, [(None, {
            'fields': ('subject', 'content',),
        })], {})

        return render_to_response('admin/geo/email.html', {
            'adminform': adminform,
            'obj': obj
        }, context_instance=RequestContext(request))

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
