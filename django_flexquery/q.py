"""
Extended Q implementation with support for prefixing lookup keys.
"""

from django.db.models import Q as _Q
from django.db.models.constants import LOOKUP_SEP


class Q(_Q):  # pylint: disable=invalid-name
    """
    A custom Q implementation that allows prefixing existing Q objects with some
    related field name dynamically.
    """

    def prefix(self, prefix):
        """Recursively copies the Q object, prefixing all lookup keys.

        The prefix and the existing filter key are delimited by the lookup separator __.
        Use this feature to delegate existing query constraints to a related field.

        :param prefix:
            Name of the related field to prepend to existing lookup keys. This isn't
            restricted to a single relation level, something like "tree__fruit"
            is perfectly valid as well.
        :type  prefix: str
        :returns Q:
        """
        return type(self)(
            *(
                child.prefix(prefix)
                if isinstance(child, Q)
                else (prefix + LOOKUP_SEP + child[0], child[1])
                for child in self.children
            ),
            _connector=self.connector,
            _negated=self.negated
        )
