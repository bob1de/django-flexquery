"""
This module provides a convenient way to declare custom filtering logic with Django's
model managers in a reusable fashion using Q objects.
"""

import functools
import inspect

from django.db.models import Manager as _Manager, QuerySet as _QuerySet
from django.utils.decorators import classonlymethod


class FlexQuery:
    """
    Flexibly provides model-specific query constraints as an attribute of Manager
    or QuerySet objects.

    When a sub-type of FlexQuery is accessed as class attribute of a Manager or
    QuerySet object, its metaclass, which is implemented as a descriptor, will
    automatically initialize and return an instance of the FlexQuery type bound to
    the holding Manager or QuerySet.

    .. automethod:: __call__
    """

    # Will be set on sub-types
    func = None

    def __call__(self, *args, **kwargs):
        """Filters the base queryset using the provided function, relaying arguments.

        :returns QuerySet:
        """
        return self.base.filter(self.call_bound(*args, **kwargs))

    def __init__(self, base):
        """Binds a FlexQuery sub-type to the given base to perform its filtering on.

        :param base: instance to use as base for filtering
        :type  base: Manager | QuerySet
        :raises TypeError: if ``base`` is of unsupported type
        """
        if not isinstance(base, (_Manager, _QuerySet)):
            raise TypeError(
                "Can only bind %s to a Manager or QuerySet, but not to %r."
                % (self.__class__.__name__, base)
            )
        self.base = base

    def __repr__(self):
        return "<%s %r, bound to %r>" % (
            self.__class__.__name__,
            self.func.__name__,
            self.base,
        )

    def as_q(self, *args, **kwargs):
        """Returns the result of the configured function, relaying arguments.

        :returns Q:
        """
        return self.call_bound(*args, **kwargs)

    def call_bound(self, *args, **kwargs):
        """Calls the provided function with ``self.base.all()`` as first argument.

        This may be overwritten if arguments need to be preprocessed in some way
        before being passed to the custom function.

        :returns Q:
        """
        # pylint: disable=not-callable
        return self.func(self.base.all(), *args, **kwargs)

    @classonlymethod
    def from_func(cls, func=None, **attrs):
        """Creates a ``FlexQuery`` sub-type from a function.

        This classmethod can be used as decorator. As long as ``func`` is ``None``,
        a ``functools.partial`` with the given keyword arguments is returned.

        :param func: function taking a base ``QuerySet`` and returning a ``Q`` object
        :type  func: function
        :param attrs: additional attributes to set on the newly created type
        :returns FlexQueryType | functools.partial:
        :raises TypeError: if ``func`` is no function
        """
        if func is None:
            return functools.partial(cls.from_func, **attrs)

        if not inspect.isfunction(func):
            raise TypeError(
                "Can only create FlexQuery from function, but %s was given."
                % func.__class__.__name__
            )

        return InitializedFlexQueryType(
            cls.__name__, (cls,), {**attrs, "func": staticmethod(func)}
        )


class InitializedFlexQueryType(type):
    """
    Custom metaclass implementing the descriptor pattern for sub-types of ``FlexQuery``
    with function attached.
    """

    def __get__(cls, instance, owner):
        if isinstance(instance, (_Manager, _QuerySet)):
            # Return a new FlexQuery instance bound to the holding object
            return cls(instance)
        # Otherwise, preserve the FlexQuery type
        return cls

    def __repr__(cls):
        return "<type %s %r>" % (cls.__name__, cls.func.__name__)


class Manager(_Manager):
    """
    Use this class' ``from_queryset`` method if you want to derive a ``Manager``
    from a ``QuerySet`` with ``FlexQuery`` members. If Django's native
    ``Manager.from_queryset`` was used instead, those members would be lost.
    """

    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        methods = super()._get_queryset_methods(queryset_class)
        methods.update(
            inspect.getmembers(
                queryset_class,
                predicate=lambda member: isinstance(member, InitializedFlexQueryType)
                and not getattr(member, "queryset_only", None),
            )
        )
        return methods


class QuerySet(_QuerySet):
    """
    Adds support for deriving a ``Manager`` from a ``QuerySet`` class via
    ``as_manager``, preserving ``FlexQuery`` members.
    """

    @classmethod
    def as_manager(cls):
        manager = Manager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
