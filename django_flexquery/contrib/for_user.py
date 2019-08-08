"""
FlexQuery variant that filters the base QuerySet for a given user.
"""

from django.http import HttpRequest

from ..flexquery import FlexQuery
from ..q import Q


__all__ = ["ForUserFlexQuery"]


class ForUserFlexQuery(FlexQuery):
    """
    This is a slightly modified ``FlexQuery`` implementation, accepting either
    a ``django.http.HttpRequest`` or a user object as argument for the custom
    function and passing the user through. When no user (or ``None``) is given,
    the default behavior is to hide all objects. This can be changed by setting the
    ``all_if_no_user`` attribute to ``True``.

    Because it can handle an ``HttpRequest`` directly, instances of this ``FlexQuery``
    may also be used in conjunction with the django_filters library as the ``queryset``
    parameter of filters.
    """

    all_if_no_user = False

    def call_bound(self, user, *args, **kwargs):  # pylint: disable=arguments-differ
        """Calls the custom function with a user, followed by the remaining arguments.

        :param user: User to filter the queryset for
        :type  user: django.contrib.auth.models.User | django.http.HttpRequest | None
        :returns Q:
        """
        try:
            user = user.user if isinstance(user, HttpRequest) else user
        except AttributeError:
            user = None
        if user is None:
            if self.all_if_no_user:
                return Q()
            return Q(pk__in=self.base.none())

        return super().call_bound(user, *args, **kwargs)
