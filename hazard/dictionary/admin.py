# -*- coding: utf-8 -*-

from django.contrib import admin
from hazard.dictionary.models import Term


class TermAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Term, TermAdmin)
