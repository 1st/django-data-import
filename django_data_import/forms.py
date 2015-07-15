from __future__ import unicode_literals
import os.path
from django import forms
from django.utils.translation import ugettext_lazy as _


class ImportForm(forms.Form):
    import_file = forms.FileField(label=_('File to import'))
    delimiter = forms.ChoiceField(choices=((',', ','), (';', ';')), initial=',')


class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    delimiter = forms.ChoiceField(choices=((',', ','), (';', ';')), initial=',')

    def clean_import_file_name(self):
        data = self.cleaned_data['import_file_name']
        data = os.path.basename(data)
        return data
