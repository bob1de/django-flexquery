"""
This module provides a convenient way to declare custom filtering logic with Django's
model managers in a reusable fashion using Q objects.
"""

import inspect

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager as _Manager, QuerySet as _QuerySet
from django.utils.decorators import classonlymethod


class FlexQueryType(type):
    """
    Custom metaclass for FlexQuery that implements the descriptor pattern.
    """

    def __get__(cls, instance, owner):
        if cls.func is not None and isinstance(instance, (_Manager, _QuerySet)):
            # Return a new FlexQuery instance bound to the holding object
            return cls(instance)
        # Otherwise, preserve the FlexQuery type
        return cls

    def __repr__(cls):
        if cls.func is not None:
            return "<type %s %r>" % (cls.__name__, cls.func.__name__)
        return super().__repr__()


class FlexQuery(metaclass=FlexQueryType):
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
        """Filters the base QuerySet using the provided function, relaying arguments.

        :returns QuerySet:
        """
        return self.base.filter(self.call_bound(*args, **kwargs))

    def __init__(self, base):
        """Binds a FlexQuery instance to the given base to perform its filtering on.

        :param base: instance to use as base for filtering
        :type  base: Manager | QuerySet
        :raises ImproperlyConfigured:
            if this FlexQuery type wasn't created by the from_q() classmethod
        :raises TypeError: if base is of unsupported type
        """
        if self.func is None:
            raise ImproperlyConfigured(
                "Use the from_q() classmethod to create a FlexQuery sub-type."
            )
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
        """Calls the provided Q function with self.base.all() as first argument.

        This may be overloaded if arguments need to be preprocessed in some way
        before being passed to the custom function.

        :returns Q:
        """
        # pylint: disable=not-callable
        return self.func(self.base.all(), *args, **kwargs)

    @classonlymethod
    def from_q(cls, func):
        """Creates a FlexQuery type from a Q function.

        :param func: callable taking a base QuerySet and returning a Q object
        :type  func: callable
        :returns FlexQueryType:
        """
        return type(cls)(cls.__name__, (cls,), {"func": staticmethod(func)})


class Manager(_Manager):
    """
    Use this Manager class' from_queryset() method if you want to derive a Manager from
    a QuerySet that has FlexQuery's defined. If Django's native Manager.from_queryset()
    was used instead, all FlexQuery's would be lost.
    """

    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        methods = super()._get_queryset_methods(queryset_class)
        methods.update(
            inspect.getmembers(
                queryset_class,
                predicate=lambda member: isinstance(member, FlexQueryType)
                and not getattr(member, "queryset_only", None),
            )
        )
        return methods


class QuerySet(_QuerySet):
    """
    Adds support for deriving a Manager from QuerySet via as_manager(), preserving
    the FlexQuery's.
    """

    @classmethod
    def as_manager(cls):
        manager = Manager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
