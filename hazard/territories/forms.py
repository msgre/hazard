# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

from django import forms
from hazard.shared.models import repair_referencies


class MergeTownAdminForm(forms.Form):
    """
    Formik pro custom admin view, ve kterem se voli obec, pod kterou se
    slouci vsechny ostatni vybrane.
    """
    towns = forms.ModelChoiceField(label=u'Obce', queryset=None, empty_label=None)

    def __init__(self, queryset, *args, **kwargs):
        super(MergeTownAdminForm, self).__init__(*args, **kwargs)
        self.fields['towns'].queryset = queryset
        choices = list(self.fields['towns'].choices)
        if choices:
            self.fields['towns'].initial = choices[0][0]
        self.fields['towns'].widget = forms.RadioSelect(choices=choices)

    def save(self):
        """
        Slouci vsechny obce z self.towns.queryset pod vybranou
        cleaned_data['towns'].
        """
        chief = self.cleaned_data['towns']
        others = self.fields['towns'].queryset.exclude(id=chief.id)
        out = {}
        for other in others:
            log = repair_referencies(other, chief)
            other.delete()
            for k in log['affected']:
                if k not in out:
                    out[k] = 0
                out[k] += len(log['affected'][k])
        return out
