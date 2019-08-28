"""
FlexQuery variant that restricts the base QuerySet for a given user.
"""

from django.http import HttpRequest

from ..flexquery import FlexQuery
from ..q import Q


__all__ = ["UserBasedFlexQuery"]


class UserBasedFlexQuery(FlexQuery):
    """
    This is a slightly modified ``FlexQuery`` implementation, accepting either
    a ``django.http.HttpRequest`` or a user object as argument for the custom
    function and passing the user through.

    When no user (or ``None``) is given, the behavior is determined by the
    ``no_user_behavior`` attribute, which may be set to one of the following constants
    defined on the ``UserBasedFlexQuery`` class:

    * ``NUB_ALL``: don't restrict the queryset
    * ``NUB_NONE``: restrict to the empty queryset (default)
    * ``NUB_PASS``: let the custom function handle a ``user`` of ``None``

    If the ``pass_anonymous_user`` attribute is changed to ``False``,
    ``django.contrib.auth.models.AnonymousUser`` objects are treated as if they were
    ``None`` and the configured no-user behavior comes to play.

    Because it can handle an ``HttpRequest`` directly, instances of this ``FlexQuery``
    may also be used in conjunction with the django_filters library as the ``queryset``
    parameter of filters.
    """

    NUB_ALL = 0
    NUB_NONE = 1
    NUB_PASS = 2
    no_user_behavior = NUB_NONE

    pass_anonymous_user = True

    def call_bound(self, user, *args, **kwargs):  # pylint: disable=arguments-differ
        """Calls the custom function with a user, followed by the remaining arguments.

        :param user: User to filter the queryset for
        :type  user: django.contrib.auth.models.User | django.http.HttpRequest | None
        :returns Q:
        """
        from django.contrib.auth.models import AnonymousUser

        try:
            user = user.user if isinstance(user, HttpRequest) else user
        except AttributeError:
            user = None
        if not self.pass_anonymous_user and isinstance(user, AnonymousUser):
            user = None
        if user is None:
            if self.no_user_behavior == self.NUB_ALL:
                return Q()
            if self.no_user_behavior == self.NUB_NONE:
                return Q(pk__in=self.base.none())

        return super().call_bound(user, *args, **kwargs)
