# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django.contrib.gis.db import models as geomodels


class HellQuerySet(geomodels.query.QuerySet):
    """
    Custom manager pro model Hell.
    """

    def visible(self):
        """
        Vrati queryset verejnych zaznamu.
        """
        return self.filter(visible=True)