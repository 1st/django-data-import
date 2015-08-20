from __future__ import absolute_import
from __future__ import with_statement
import csv
import django
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from .forms import ImportForm, ConfirmImportForm, get_model_form, get_model_formset


class ImportDataMixin(object):
    """
    Data import mixin.
    """
    change_list_template = 'admin/django_data_import/change_list_import.html'
    import_template_name = 'admin/django_data_import/import.html'

    def get_urls(self):
        urls = super(ImportDataMixin, self).get_urls()
        my_urls = patterns(
            '',
            url(
                r'^import/$',
                self.admin_site.admin_view(self.import_action),
                name='%s_%s_import' % self._get_model_info()
            )
        )
        return my_urls + urls

    def import_action(self, request, *args, **kwargs):
        """
        Custom end-point to import CSV file.

        Here we show form to select file and save data to database.
        """
        context = {}
        save_data = request.POST.get('save_data', False)
        form = ImportForm(request.POST or None, request.FILES or None)
        model_fields = self._get_field_names()

        if save_data:
            import_form = get_model_form(self.model, fields=model_fields)
            import_formset = get_model_formset(import_form, request.POST)

            created_counter = 0
            for import_form in import_formset:
                try:
                    if import_form.is_valid():
                        import_form.save()
                        created_counter += 1
                except (IntegrityError, TypeError):
                    pass

            success_message = _('Imported {} rows'.format(created_counter))
            messages.success(request, success_message)

            url = reverse(
                'admin:%s_%s_changelist' % self._get_model_info(),
                current_app=self.admin_site.name
            )
            return HttpResponseRedirect(url)

        elif request.method == 'POST' and form.is_valid():
            import_file = form.cleaned_data['import_file']
            delimiter = str(form.cleaned_data['delimiter'])

            csv_data = self._read_csv_file(import_file, delimiter=delimiter)
            import_form = get_model_form(self.model, fields=model_fields)
            context['import_formset'] = get_model_formset(import_form, initial=csv_data)

            context['confirm_form'] = ConfirmImportForm(initial={
                'delimiter': form.cleaned_data['delimiter'],
            })

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = model_fields

        return TemplateResponse(
            request,
            self.import_template_name,
            context,
            current_app=self.admin_site.name
        )

    def _get_field_names(self):
        return [f.name for f in self.model._meta.fields if f.name != 'id']

    def _get_model_info(self):
        # module_name is renamed to model_name in Django 1.8
        app_label = self.model._meta.app_label
        try:
            return (app_label, self.model._meta.model_name)
        except AttributeError:
            return (app_label, self.model._meta.module_name)

    def _read_csv_file(self, filename, delimiter=','):
        """
        Return list of dicts from given CSV file.
        """
        reader = csv.DictReader(filename, delimiter=delimiter, fieldnames=self._get_field_names())
        return list(reader)
