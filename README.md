Django app for import CSV data
===

Adds a button "Import" on model list page in Django admin site that allow to import new records to any model.

I get some code from [django-import-export](https://github.com/django-import-export/django-import-export) and adopted it to work with CVS file import.


How to use
---

Follow next steps:
 * Install with `pip install django-data-import`
 * Add `django_data_import` to `INSTALLED_APPS` in your `settings.py` file
 * Edit your `admin.py` file and add `from django_data_import import ImportDataMixin` and add mixin to ModelAdmin like this `class BlogAdmin(ImportDataMixin, admin.ModelAdmin)`
