# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf import settings

from hazard.dictionary.models import Term


class TermAdmin(admin.ModelAdmin):
    """
    Administrace pojmu ve slovniku.
    """
    list_display = ('title', )
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        js = [
            "%sjs/jquery-1.4.2.js" % settings.STATIC_URL,
            "%sjs/code-mirror/lib/codemirror.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/xml/xml.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/javascript/javascript.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/css/css.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/htmlmixed/htmlmixed.js" % settings.STATIC_URL,
            "%sjs/code-mirror/mode/htmlembedded/htmlembedded.js" % settings.STATIC_URL,
            "%sjs/lib/dictionary_admin.js" % settings.STATIC_URL,
        ]
        css = {
            "all": (
                "%sjs/code-mirror/lib/codemirror.css" % settings.STATIC_URL,
                "%scss/dictionary_admin.css" % settings.STATIC_URL,
            )
        }

admin.site.register(Term, TermAdmin)
