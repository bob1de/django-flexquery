"""
This module provides a convenient way to declare custom filtering logic with Django's
model managers in a reusable fashion using Q objects.
"""

import inspect

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager as _Manager, QuerySet as _QuerySet
from django.utils.decorators import classonlymethod

from .q import Q


class FlexQueryType(type):
    """
    Custom metaclass for FlexQuery that implements the descriptor pattern.
    """

    def __get__(cls, instance, owner):
        if issubclass(cls, InitializedFlexQueryMixin) and isinstance(
            instance, (_Manager, _QuerySet)
        ):
            # Return a new FlexQuery instance bound to the holding object
            return cls(instance)
        # Otherwise, preserve the FlexQuery type
        return cls

    def __repr__(cls):
        if cls.q_func is not None or cls.qs_func is not None:
            return "<type %s %r>" % (
                cls.__name__,
                (cls.qs_func if cls.q_func is None else cls.q_func).__name__,
            )
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

    # pylint: disable=not-callable

    # Will be set when creating sub-types
    q_func = None
    qs_func = None

    def __call__(self, *args, **kwargs):
        """Filters the base QuerySet using the provided function.

        All arguments are passed through to the FlexQuery's custom function.

        :returns QuerySet:
        """
        if self.q_func is None:
            return self.qs_func(self.base.all(), *args, **kwargs)
        return self.base.filter(self.q_func(*args, **kwargs))

    def __init__(self, base):
        """Binds a FlexQuery instance to the given base to perform its filtering on.

        :param base: instance to use as base for filtering
        :type  base: Manager, QuerySet
        :raises ImproperlyConfigured:
            if this FlexQuery type wasn't created by one of the from_*() classmethods
        :raises TypeError: if base is of unsupported type
        """
        if self.q_func is None and self.qs_func is None:
            raise ImproperlyConfigured(
                "Use one of the from_*() classmethods to create a FlexQuery type."
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
            (self.qs_func if self.q_func is None else self.q_func).__name__,
            self.base,
        )

    def as_q(self, *args, **kwargs):
        """Returns a Q object representing the custom filters.

        The Q object is either retrieved from the configured Q function or, if a
        QuerySet filtering function was provided instead, will contain a sub-query
        ensuring the object is in the base QuerySet filtered by that function.

        All arguments are passed through to the FlexQuery's custom function.

        :returns Q:
        """
        if self.q_func is None:
            return Q(pk__in=self.qs_func(self.base.all(), *args, **kwargs))
        return self.q_func(*args, **kwargs)

    @classonlymethod
    def from_q(cls, func):
        """Creates a FlexQuery type from a Q function.

        :param func: callable returning a Q object
        :type  func: callable
        :returns FlexQueryType:
        """
        return type(cls)(
            "%sFromQFunction" % cls.__name__,
            (InitializedFlexQueryMixin, cls),
            {"q_func": staticmethod(func)},
        )

    @classonlymethod
    def from_queryset(cls, func):
        """Creates a FlexQuery type from a queryset filtering function.

        :param func:
            callable taking a QuerySet as first positional argument, applying some
            filtering on it and returning it back
        :type  func: callable
        :returns FlexQueryType:
        """
        return type(cls)(
            "%sFromQuerySetFunction" % cls.__name__,
            (InitializedFlexQueryMixin, cls),
            {"qs_func": staticmethod(func)},
        )


class InitializedFlexQueryMixin:
    """
    Mixin that prevents further usage of the from_*() classmethods on sub-types
    of FlexQuery.
    """

    # pylint: disable=missing-docstring,unused-argument

    @classonlymethod
    def _already_initialized(cls):
        raise NotImplementedError(
            "%r was already initialized with a function. Use FlexQuery.from_*() "
            "directly to derive new FlexQuery types." % cls
        )

    @classonlymethod
    def from_q(cls, func):
        cls._already_initialized()

    @classonlymethod
    def from_queryset(cls, func):
        cls._already_initialized()


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
