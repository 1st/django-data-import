"""
Django data import
====================

Adds a button "Import" on model list page that allows to import new records to this model.

Read `Quick Start Guide <https://github.com/1st/django-data-import>`_ to get started.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = '1.0.1'


setup(
    name='Django-Data-Import',
    version=version,
    url='https://github.com/1st/django-data-import',
    license='MIT',
    author='Anton Danilchenko',
    author_email='anton@danilchenko.me',
    description='Data import from CVS file to Django Model',
    keywords='django csv data import',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['django_data_import'],
    install_requires=['django>=1.7'],
    include_package_data=True,
    zip_safe=False,
    platforms='any'
)
