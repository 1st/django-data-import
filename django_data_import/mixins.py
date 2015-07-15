from __future__ import absolute_import
from __future__ import with_statement
import tempfile
import os.path
import csv
import django
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from .forms import ImportForm, ConfirmImportForm


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

        Here we show form to select file and process this file.
        """
        context = {}
        save_data = request.POST.get('save_data', False)
        try_again = request.POST.get('try_again', False)
        form = ImportForm(request.POST or None, request.FILES or None)

        if save_data:
            self._save_data(request)
            url = reverse(
                'admin:%s_%s_changelist' % self._get_model_info(),
                current_app=self.admin_site.name
            )
            return HttpResponseRedirect(url)

        elif try_again:
            confirm_form = ConfirmImportForm({
                'import_file_name': request.POST.get('import_file_name'),
                'delimiter': request.POST.get('delimiter'),
            })
            if confirm_form.is_valid():
                import_file_name = os.path.join(
                    tempfile.gettempdir(),
                    confirm_form.cleaned_data['import_file_name']
                )
                context['result'] = self._read_csv_file(
                    import_file_name,
                    delimiter=str(confirm_form.cleaned_data['delimiter'])
                )
            context['confirm_form'] = confirm_form

        elif request.method == 'POST' and form.is_valid():
            import_file = form.cleaned_data['import_file']
            delimiter = str(form.cleaned_data['delimiter'])

            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            context['result'] = self._read_csv_file(uploaded_file.name, delimiter=delimiter)

            context['confirm_form'] = ConfirmImportForm(initial={
                'import_file_name': os.path.basename(uploaded_file.name),
                'delimiter': form.cleaned_data['delimiter'],
            })

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = self._get_field_names()

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
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter, fieldnames=self._get_field_names())
            return list(reader)

    def _save_data(self, request):
        """
        Save data from CSV file to current model.
        """
        confirm_form = ConfirmImportForm(request.POST)

        if confirm_form.is_valid():
            import_file_name = os.path.join(
                tempfile.gettempdir(),
                confirm_form.cleaned_data['import_file_name']
            )
            delimiter = str(confirm_form.cleaned_data['delimiter'])

            rows = self._read_csv_file(import_file_name, delimiter=delimiter)
            fields = self._get_field_names()

            created_counter = 0

            # insert only records with names that we have in model
            for row in rows:
                data = {name: row[name] for name in fields}
                try:
                    self.model.objects.create(**data)
                    created_counter += 1
                except (IntegrityError, TypeError):
                    pass

            success_message = _('Imported {} rows'.format(created_counter))
            messages.success(request, success_message)
            return True
