# -*- coding: utf-8 -*-

from django.views.generic import ListView

from hazard.dictionary.models import Term


class TermListView(ListView):
    """
    Seznam terminu a pojmu.
    """
    context_object_name = "terms"
    template_name = 'dictionary/list.html'

    def get_queryset(self):
        return Term.objects.all()
