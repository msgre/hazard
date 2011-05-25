# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.cache import cache


class ClearCacheMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        cache.clear()
