``Q``
=====

The ``Q`` implementation provided by this library contains a simple addition to that
of Django.

Creating a ``Q`` object works as usual::

    >>> from django_flexquery import Q
    >>> q = Q(size__lt=10)
    >>> q
    <Q: (AND: ('size__lt', 10))>

But this implementation adds a ``prefix()`` method, which allows prefixing some
related field's name to the lookup keys of an existing ``Q`` object. Since ``Q``
objects can be nested, this is done recursively.

An example::

    >>> q.prefix("fruits")
    <Q: (AND: ('fruits__size__lt', 10))>

Nothing more to it. The real power comes when using these ``Q`` objects with
``FlexQuery``.


API
---

.. automodule:: django_flexquery.q
   :members:
