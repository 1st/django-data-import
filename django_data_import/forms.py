import os.path
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _


def get_model_form(model, fields=None):
    """
    Create ModelForm based on model.
    """
    meta = type('Meta', (), {"model": model, "fields": fields})
    modelform_class = type('modelform', (forms.ModelForm,), {"Meta": meta})
    return modelform_class


def get_model_formset(form, *args, **kwargs):
    return formset_factory(form)(*args, **kwargs)


class ImportForm(forms.Form):
    import_file = forms.FileField(label=_('File to import'))
    delimiter = forms.ChoiceField(choices=((';', ';'), (',', ',')), initial=';')


class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    delimiter = forms.ChoiceField(choices=((';', ';'), (',', ',')), initial=';')

    def clean_import_file_name(self):
        data = self.cleaned_data['import_file_name']
        data = os.path.basename(data)
        return data
