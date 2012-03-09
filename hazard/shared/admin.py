# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.cache import cache
from django.conf import settings

from chunks.models import Chunk
from chunks.templatetags.chunks import CACHE_PREFIX


class ClearCacheMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        cache.clear()


class ChunkAdmin(admin.ModelAdmin):
    """
    Vlastni admin pro chunky (kvuli editoru nad textarea polickem).
    """
    list_display = ('key','description',)
    search_fields = ('key', 'content')

    class Media:
        js = [
            "%sjs/jquery-1.4.2.js" % settings.STATIC_URL,
            "%sjs/code-mirror/lib/codemirror.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/xml/xml.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/javascript/javascript.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/css/css.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/htmlmixed/htmlmixed.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/htmlembedded/htmlembedded.js" % settings.STATIC_URL,
            "%sjs/lib/chunk_admin.js" % settings.STATIC_URL,
        ]
        css = {
            "all": (
                "%sjs/code-mirror/lib/codemirror.css" % settings.STATIC_URL,
                "%scss/chunk_admin.css" % settings.STATIC_URL,
            )
        }

    def save_model(self, request, obj, form, change):
        """
        Smazani cache chunku.
        """
        obj.save()
        cache_key = CACHE_PREFIX + obj.key
        cache.delete(cache_key)

admin.site.unregister(Chunk)
admin.site.register(Chunk, ChunkAdmin)
