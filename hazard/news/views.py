# -*- coding: utf-8 -*-

from django.views.generic import DetailView, ListView

from hazard.news.models import New


class NewDetailView(DetailView):
    """
    Detail konkretni zpravicky.
    """
    context_object_name = "new"
    template_name = 'news/detail.html'

    def get_queryset(self):
        return New.objects.filter(slug=self.kwargs['slug'], public=True)


class NewListView(ListView):
    """
    Chronologicky seznam vsech publikovanych zprav.
    """
    context_object_name = "news"
    template_name = 'news/list.html'

    def get_queryset(self):
        return New.objects.filter(public=True)
