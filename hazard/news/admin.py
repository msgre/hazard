# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.news.models import New
from hazard.shared.admin import ClearCacheMixin


class NewAdmin(ClearCacheMixin):
    list_display = ('title', 'created', 'public', )
    list_filter = ('public', )
    search_fields = ('title', 'slug')
    date_hierarchy = 'created'
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ('public', )

    fieldsets = (
        (None, {
            'fields': ('title', 'annotation', 'content', )
        }),
        (u'Doplňující informace', {
            'fields': ('slug', 'public', )
        }),
    )

admin.site.register(New, NewAdmin)
