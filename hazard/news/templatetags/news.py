# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import template
from hazard.news.models import New

register = template.Library()


TOP_NEWS = 3

@register.inclusion_tag('news/display_news.tag.html')
def display_news(news=None):
    """
    Zobrazi tabulku se zpravama. Budto se fci doda explicitne queryset,
    ktery se ma zobrazit, nebo fce sama vytahne z DB TOP_NEWS zprav z DB.
    """
    if not news:
        news = New.objects.all()[:TOP_NEWS]
    return {'news': news}

@register.inclusion_tag('news/display_last_new.tag.html')
def display_last_new():
    """
    Zobrazi posledni zpravu.
    """
    return {'news': New.objects.all()}
