django-flexquery
================

.. image:: https://travis-ci.org/efficiosoft/django-flexquery.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/efficiosoft/django-flexquery
.. image:: https://coveralls.io/repos/github/efficiosoft/django-flexquery/badge.svg?branch=master
   :alt: Test Coverage
   :target: https://coveralls.io/github/efficiosoft/django-flexquery?branch=master
.. image:: https://readthedocs.org/projects/django-flexquery/badge/?version=latest
   :alt: Documentation
   :target: https://django-flexquery.readthedocs.io/en/latest/

This library aims to provide a new way of declaring reusable QuerySet filtering
logic in your Django project, incorporating the DRY principle and maximizing user
experience and performance by allowing you to decide between sub-queries and JOINs.

Its strengths are, among others:

* Easy to learn in minutes
* Cleanly integrates with Django's ORM
* Small code footprint, less bugs - ~150 lines of code (LoC)
* 100% test coverage
* Fully documented code, formatted using the excellent `Black Code Formatter
  <https://github.com/python/black>`_.

See the `documentation at Read The Docs <https://django-flexquery.readthedocs.org>`_
to convince yourself.
