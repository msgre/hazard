# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.utils.safestring import mark_safe

from hazard.territories.models import Region, District, Town, Zip, Address
from hazard.territories.forms import MergeTownAdminForm


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('title', 'region')
    search_fields = ('title', 'slug')
    list_filter = ('region', )


class TownAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'region', 'display_zip', 'population')
    search_fields = ('title', 'slug')
    list_filter = ('region', 'district', )
    actions = ['merge_action']

    def display_zip(self, obj):
        return u", ".join([i.display() for i in obj.zip_set.all()])
    display_zip.short_description = u"PSČ"

    def get_urls(self):
        urls = super(TownAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^merge/$', self.admin_site.admin_view(self.merge_view), name="territories-town-merge")
        )
        return my_urls + urls

    def merge_action(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        url = reverse('admin:territories-town-merge')
        return HttpResponseRedirect("%s?ids=%s" % (url, ",".join(selected)))
    merge_action.short_description = u"Sloučit vybrané obce"

    def merge_view(self, request):
        """
        Slouci vybrane obce pod jedinou (vcetne presunu automatu, budov a
        dalsich referenci).
        """
        # vyzobneme IDcka z URL
        ids = [int(i) for i in request.GET.get('ids', '').split(',') if i.isdigit()]
        if not ids:
            raise Http404
        queryset = Town.objects.filter(id__in=ids)

        # obsluha formiku
        if request.method == 'POST':
            form = MergeTownAdminForm(queryset, request.POST)
            if form.is_valid():
                log = form.save()
                msg = u", ".join([u"%s=%i" % (k, log[k]) for k in log])
                self.message_user(request, u"Sloučení obce úspěšně provedeno (%s)" % msg)
                return HttpResponseRedirect(reverse('admin:territories_town_changelist'))
        else:
            form = MergeTownAdminForm(queryset)

        # potrava pro sablonu
        adminForm = admin.helpers.AdminForm(form, [(None, {
            'fields': ('towns', ),
            'description': u'<p>Vyber obec, pod kterou se ostatní přesunou.</p>'
        })], {})
        media = self.media + adminForm.media

        # sup do sablony
        context = {
            'is_popup': False,
            'app_label': self.model._meta.app_label,
            'verbose_name': self.model._meta.verbose_name,
            'title': u'Sloučení obcí',
            'adminform': adminForm,
            'media': mark_safe(media),
            'original': None
        }
        self.change_form_template = 'admin/territories/town/merge.html'
        return self.render_change_form(request, context, change=True)


class ZipAdmin(admin.ModelAdmin):
    list_display = ('title', 'town')
    search_fields = ('title', 'slug')


admin.site.register(Region)
admin.site.register(District, DistrictAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(Zip, ZipAdmin)


from django.contrib.gis.admin.options import OSMGeoAdmin

class AddressAdmin(OSMGeoAdmin):
    pass

admin.site.register(Address, AddressAdmin)
